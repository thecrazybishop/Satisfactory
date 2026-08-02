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


class MainWindow(tk.Tk):
    def __init__(self, state: SharedState, poller: Poller):
        super().__init__()
        self.title("Satisfactory FRM Dashboard")
        self.geometry("1050x680")

        self.state_ = state
        self.poller = poller
        self._known_recipes: list[str] = []

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
        ttk.Label(controls, text="Recipe:").pack(side="left")

        self.recipe_var = tk.StringVar()
        self.recipe_combo = ttk.Combobox(controls, textvariable=self.recipe_var, state="readonly", width=40)
        self.recipe_combo.pack(side="left", padx=6)
        self.recipe_combo.bind("<<ComboboxSelected>>", lambda _evt: self._redraw_history())

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Seconds ago")
        self.ax.set_ylabel("Rate / min")

        self.canvas = FigureCanvasTkAgg(self.figure, master=frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    def _build_power_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Power")

        summary = ttk.Frame(frame)
        summary.pack(fill="x", padx=10, pady=10)

        self.power_summary_vars = {
            "production": tk.StringVar(value="Production: -- MW"),
            "capacity": tk.StringVar(value="Capacity: -- MW"),
            "consumption": tk.StringVar(value="Consumption: -- MW"),
        }
        for key in ("production", "capacity", "consumption"):
            ttk.Label(
                summary, textvariable=self.power_summary_vars[key], font=("TkDefaultFont", 14, "bold")
            ).pack(side="left", padx=20)

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

        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=120, anchor="w")
        tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.power_tree = tree

    # -- refresh loop -----------------------------------------------------

    def _refresh(self):
        with self.state_.lock:
            connected = self.state_.connected
            last_error = self.state_.last_error
            session_info = self.state_.session_info
            recipes = dict(self.state_.recipes)
            power_circuits = list(self.state_.power_circuits)
            history_snapshot = {recipe: list(points) for recipe, points in self.state_.history.items()}

        self._update_status(connected, last_error, session_info)
        self._update_production_tab(recipes)
        self._update_history_controls(recipes)
        self._redraw_history(history_snapshot)
        self._update_power_tab(power_circuits)

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

    def _update_history_controls(self, recipes):
        recipe_names = sorted(recipes)
        if recipe_names != self._known_recipes:
            self._known_recipes = recipe_names
            self.recipe_combo["values"] = recipe_names
            if not self.recipe_var.get() and recipe_names:
                self.recipe_var.set(recipe_names[0])

    def _redraw_history(self, history_snapshot=None):
        recipe = self.recipe_var.get()
        if history_snapshot is None:
            with self.state_.lock:
                history_snapshot = {recipe: list(self.state_.history.get(recipe, []))}

        points = history_snapshot.get(recipe, [])

        self.ax.clear()
        self.ax.set_xlabel("Seconds ago")
        self.ax.set_ylabel("Rate / min")
        self.ax.set_title(recipe or "No recipe selected")

        if points:
            now = datetime.now()
            xs = [-(now - ts).total_seconds() for ts, _p, _c in points]
            produced = [p for _ts, p, _c in points]
            consumed = [c for _ts, _p, c in points]
            self.ax.plot(xs, produced, label="Produced/min")
            self.ax.plot(xs, consumed, label="Consumed/min")
            self.ax.legend(loc="upper left")

        self.canvas.draw_idle()

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

        self.power_summary_vars["production"].set(f"Production: {total_production:.1f} MW")
        self.power_summary_vars["capacity"].set(f"Capacity: {total_capacity:.1f} MW")
        self.power_summary_vars["consumption"].set(f"Consumption: {total_consumption:.1f} MW")

    def _on_close(self):
        self.poller.stop()
        self.destroy()
