"""Tkinter dashboard: Production, History, and Power tabs driven by a
SharedState that a background Poller keeps refreshed once per second.
"""

import tkinter as tk
from datetime import datetime
from tkinter import ttk

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from .poller import Poller, SharedState  # noqa: E402

UI_REFRESH_MS = 1000

HORIZON_OPTIONS = [
    ("1 second", 1),
    ("5 seconds", 5),
    ("30 seconds", 30),
    ("1 minute", 60),
    ("5 minutes", 300),
    ("15 minutes", 900),
    ("30 minutes", 1800),
    ("1 hour", 3600),
]
HORIZON_SECONDS_BY_LABEL = dict(HORIZON_OPTIONS)
DEFAULT_HORIZON_LABEL = "5 minutes"


class MainWindow(tk.Tk):
    def __init__(self, state: SharedState, poller: Poller):
        super().__init__()
        self.title("Satisfactory FRM Dashboard")
        self.geometry("1050x680")

        self.state_ = state
        self.poller = poller
        self._known_items: list[str] = []

        self._build_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(UI_REFRESH_MS, self._refresh)

    # -- layout ---------------------------------------------------------

    def _build_widgets(self):
        self.status_var = tk.StringVar(value="Connecting…")
        ttk.Label(self, textvariable=self.status_var, anchor="w", relief="sunken").pack(
            side="bottom", fill="x"
        )

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self._build_production_tab(notebook)
        self._build_history_tab(notebook)
        self._build_power_tab(notebook)

    def _build_production_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Production")

        columns = ("recipe", "machines", "produced", "consumed", "efficiency")
        headings = {
            "recipe": "Recipe",
            "machines": "Machines",
            "produced": "Producing / min",
            "consumed": "Consuming / min",
            "efficiency": "Avg Efficiency",
        }
        widths = {"recipe": 200, "machines": 80, "produced": 340, "consumed": 340, "efficiency": 110}

        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")
        tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.production_tree = tree

    def _build_history_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="History")

        controls = ttk.Frame(frame)
        controls.pack(fill="x", padx=8, pady=8)
        ttk.Label(controls, text="Item:").pack(side="left")

        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(controls, textvariable=self.item_var, state="readonly", width=40)
        self.item_combo.pack(side="left", padx=6)
        self.item_combo.bind("<<ComboboxSelected>>", lambda _evt: self._redraw_history())

        ttk.Label(controls, text="Time range:").pack(side="left", padx=(12, 0))
        self.history_horizon_var = tk.StringVar(value=DEFAULT_HORIZON_LABEL)
        history_horizon_combo = ttk.Combobox(
            controls,
            textvariable=self.history_horizon_var,
            state="readonly",
            width=12,
            values=[label for label, _seconds in HORIZON_OPTIONS],
        )
        history_horizon_combo.pack(side="left", padx=6)
        history_horizon_combo.bind("<<ComboboxSelected>>", lambda _evt: self._redraw_history())

        charts_frame = ttk.Frame(frame)
        charts_frame.pack(fill="both", expand=True, padx=8, pady=8)

        produced_frame = ttk.Frame(charts_frame)
        produced_frame.pack(side="left", fill="both", expand=True, padx=(0, 4))
        consumed_frame = ttk.Frame(charts_frame)
        consumed_frame.pack(side="left", fill="both", expand=True, padx=(4, 0))

        self.produced_figure = Figure(figsize=(5, 4), dpi=100)
        self.produced_ax = self.produced_figure.add_subplot(111)
        self.produced_ax.set_xlabel("Seconds ago")
        self.produced_ax.set_ylabel("Rate / min")

        self.produced_canvas = FigureCanvasTkAgg(self.produced_figure, master=produced_frame)
        self.produced_canvas.get_tk_widget().pack(fill="both", expand=True)

        self.consumed_figure = Figure(figsize=(5, 4), dpi=100)
        self.consumed_ax = self.consumed_figure.add_subplot(111)
        self.consumed_ax.set_xlabel("Seconds ago")
        self.consumed_ax.set_ylabel("Rate / min")

        self.consumed_canvas = FigureCanvasTkAgg(self.consumed_figure, master=consumed_frame)
        self.consumed_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _build_power_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Power")

        summary = ttk.Frame(frame)
        summary.pack(fill="x", padx=10, pady=(10, 0))

        self.power_summary_vars = {
            "production": tk.StringVar(value="Production: -- MW"),
            "capacity": tk.StringVar(value="Capacity: -- MW"),
            "consumption": tk.StringVar(value="Consumption: -- MW"),
            "usage_pct": tk.StringVar(value="Usage: -- % of capacity"),
        }
        for key in ("production", "capacity", "consumption", "usage_pct"):
            ttk.Label(
                summary, textvariable=self.power_summary_vars[key], font=("TkDefaultFont", 14, "bold")
            ).pack(side="left", padx=20)

        self.power_usage_bar = ttk.Progressbar(frame, orient="horizontal", mode="determinate", maximum=100)
        self.power_usage_bar.pack(fill="x", padx=10, pady=10)

        columns = (
            "circuit",
            "production",
            "consumption",
            "capacity",
            "battery_pct",
            "time_empty",
            "time_full",
            "fuse",
        )
        headings = {
            "circuit": "Circuit",
            "production": "Production (MW)",
            "consumption": "Consumption (MW)",
            "capacity": "Capacity (MW)",
            "battery_pct": "Battery Charge",
            "time_empty": "Time to Empty",
            "time_full": "Time to Full",
            "fuse": "Fuse Tripped",
        }

        table_frame = ttk.Frame(frame)
        table_frame.pack(fill="x", padx=10, pady=(0, 10))

        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=120, anchor="w")
        tree.pack(fill="x", side="left", expand=True)

        table_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=table_scrollbar.set)
        table_scrollbar.pack(side="right", fill="y")

        self.power_tree = tree

        power_controls = ttk.Frame(frame)
        power_controls.pack(fill="x", padx=10, pady=(0, 4))
        ttk.Label(power_controls, text="Time range:").pack(side="left")
        self.power_horizon_var = tk.StringVar(value=DEFAULT_HORIZON_LABEL)
        power_horizon_combo = ttk.Combobox(
            power_controls,
            textvariable=self.power_horizon_var,
            state="readonly",
            width=12,
            values=[label for label, _seconds in HORIZON_OPTIONS],
        )
        power_horizon_combo.pack(side="left", padx=6)
        power_horizon_combo.bind("<<ComboboxSelected>>", lambda _evt: self._redraw_power_history())

        self.power_figure = Figure(figsize=(6, 3), dpi=100)
        self.power_ax = self.power_figure.add_subplot(111)
        self.power_ax.set_xlabel("Seconds ago")
        self.power_ax.set_ylabel("MW")

        self.power_canvas = FigureCanvasTkAgg(self.power_figure, master=frame)
        self.power_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # -- refresh loop -----------------------------------------------------

    def _refresh(self):
        with self.state_.lock:
            connected = self.state_.connected
            last_error = self.state_.last_error
            session_info = self.state_.session_info
            recipes = dict(self.state_.recipes)
            items = dict(self.state_.items)
            power_circuits = list(self.state_.power_circuits)
            power_history = list(self.state_.power_history)
            history_snapshot = {item: list(points) for item, points in self.state_.item_history.items()}

        self._update_status(connected, last_error, session_info)
        self._update_production_tab(recipes)
        self._update_history_controls(items)
        self._redraw_history(history_snapshot)
        self._update_power_tab(power_circuits)
        self._redraw_power_history(power_history)

        self.after(UI_REFRESH_MS, self._refresh)

    def _update_status(self, connected, last_error, session_info):
        if connected and session_info:
            self.status_var.set(
                f"Connected — Session: {session_info.get('SessionName', '?')}  "
                f"Play time: {session_info.get('TotalPlayDurationText', '?')}"
            )
        elif connected:
            self.status_var.set("Connected — waiting for session info…")
        else:
            self.status_var.set(f"Disconnected: {last_error or 'not connected yet'}")

    def _update_production_tab(self, recipes):
        tree = self.production_tree
        tree.delete(*tree.get_children())
        for recipe in sorted(recipes):
            stats = recipes[recipe]
            produced = ", ".join(f"{name}: {rate:.1f}" for name, rate in stats.produced.items()) or "--"
            consumed = ", ".join(f"{name}: {rate:.1f}" for name, rate in stats.consumed.items()) or "--"
            tree.insert(
                "",
                "end",
                values=(recipe, stats.machine_count, produced, consumed, f"{stats.avg_efficiency:.1f}%"),
            )

    def _update_history_controls(self, items):
        item_names = sorted(items)
        if item_names != self._known_items:
            self._known_items = item_names
            self.item_combo["values"] = item_names
            if not self.item_var.get() and item_names:
                self.item_var.set(item_names[0])

    def _redraw_history(self, history_snapshot=None):
        item = self.item_var.get()
        if history_snapshot is None:
            with self.state_.lock:
                history_snapshot = {item: list(self.state_.item_history.get(item, []))}

        points = history_snapshot.get(item, [])
        horizon_seconds = HORIZON_SECONDS_BY_LABEL.get(
            self.history_horizon_var.get(), HORIZON_SECONDS_BY_LABEL[DEFAULT_HORIZON_LABEL]
        )

        title = item or "No item selected"

        self.produced_ax.clear()
        self.produced_ax.set_xlabel("Seconds ago")
        self.produced_ax.set_ylabel("Rate / min")
        self.produced_ax.set_title(f"{title} — Produced/min")
        self.produced_ax.set_xlim(-horizon_seconds, 0)

        self.consumed_ax.clear()
        self.consumed_ax.set_xlabel("Seconds ago")
        self.consumed_ax.set_ylabel("Rate / min")
        self.consumed_ax.set_title(f"{title} — Consumed/min")
        self.consumed_ax.set_xlim(-horizon_seconds, 0)

        if points:
            now = datetime.now()
            visible = [(ts, p, c) for ts, p, c in points if (now - ts).total_seconds() <= horizon_seconds]
            if visible:
                xs = [-(now - ts).total_seconds() for ts, _p, _c in visible]
                produced = [p for _ts, p, _c in visible]
                consumed = [c for _ts, _p, c in visible]
                self.produced_ax.plot(xs, produced, color="tab:green", label="Produced/min")
                self.produced_ax.legend(loc="upper left")
                self.consumed_ax.plot(xs, consumed, color="tab:red", label="Consumed/min")
                self.consumed_ax.legend(loc="upper left")

        self.produced_canvas.draw_idle()
        self.consumed_canvas.draw_idle()

    def _update_power_tab(self, circuits):
        tree = self.power_tree
        tree.delete(*tree.get_children())

        total_production = 0.0
        total_capacity = 0.0
        total_consumption = 0.0

        for circuit in circuits:
            production = circuit.get("PowerProduction") or 0.0
            consumption = circuit.get("PowerConsumed") or 0.0
            capacity = circuit.get("PowerCapacity") or 0.0
            total_production += production
            total_capacity += capacity
            total_consumption += consumption

            tree.insert(
                "",
                "end",
                values=(
                    circuit.get("CircuitGroupID", "?"),
                    f"{production:.1f}",
                    f"{consumption:.1f}",
                    f"{capacity:.1f}",
                    f"{(circuit.get('BatteryPercent') or 0.0):.1f}%",
                    circuit.get("BatteryTimeEmpty", "--"),
                    circuit.get("BatteryTimeFull", "--"),
                    "Yes" if circuit.get("FuseTriggered") else "No",
                ),
            )

        usage_pct = (total_consumption / total_capacity * 100.0) if total_capacity else 0.0

        self.power_summary_vars["production"].set(f"Production: {total_production:.1f} MW")
        self.power_summary_vars["capacity"].set(f"Capacity: {total_capacity:.1f} MW")
        self.power_summary_vars["consumption"].set(f"Consumption: {total_consumption:.1f} MW")
        self.power_summary_vars["usage_pct"].set(f"Usage: {usage_pct:.1f}% of capacity")
        self.power_usage_bar["value"] = min(usage_pct, 100.0)

    def _redraw_power_history(self, power_history=None):
        if power_history is None:
            with self.state_.lock:
                power_history = list(self.state_.power_history)

        horizon_seconds = HORIZON_SECONDS_BY_LABEL.get(
            self.power_horizon_var.get(), HORIZON_SECONDS_BY_LABEL[DEFAULT_HORIZON_LABEL]
        )

        self.power_ax.clear()
        self.power_ax.set_xlabel("Seconds ago")
        self.power_ax.set_ylabel("MW")
        self.power_ax.set_title("Power over time")
        self.power_ax.set_xlim(-horizon_seconds, 0)

        if power_history:
            now = datetime.now()
            visible = [
                (ts, p, c, cap) for ts, p, c, cap in power_history if (now - ts).total_seconds() <= horizon_seconds
            ]
            if visible:
                xs = [-(now - ts).total_seconds() for ts, _p, _c, _cap in visible]
                production = [p for _ts, p, _c, _cap in visible]
                consumption = [c for _ts, _p, c, _cap in visible]
                capacity = [cap for _ts, _p, _c, cap in visible]
                self.power_ax.plot(xs, production, label="Production")
                self.power_ax.plot(xs, consumption, label="Consumption")
                self.power_ax.plot(xs, capacity, label="Capacity", linestyle="--")
                self.power_ax.legend(loc="upper left")

        self.power_canvas.draw_idle()

    def _on_close(self):
        self.poller.stop()
        self.destroy()
