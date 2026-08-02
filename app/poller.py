"""Background polling of the FRM server: session info once, then production
and power stats every second, kept in a lock-protected SharedState that the
GUI reads from on its own refresh cycle.
"""

import threading
import time
from collections import defaultdict, deque
from datetime import datetime

from frm import FRMClient, FRMError

POLL_INTERVAL_SECONDS = 1.0
HISTORY_MAXLEN = 1800  # ~30 minutes of history at a 1s poll interval


class RecipeStats:
    __slots__ = ("recipe", "machine_count", "produced", "consumed", "efficiency_sum")

    def __init__(self, recipe):
        self.recipe = recipe
        self.machine_count = 0
        self.produced = {}
        self.consumed = {}
        self.efficiency_sum = 0.0

    @property
    def avg_efficiency(self):
        return self.efficiency_sum / self.machine_count if self.machine_count else 0.0

    @property
    def total_produced(self):
        return sum(self.produced.values())

    @property
    def total_consumed(self):
        return sum(self.consumed.values())


def aggregate_factory_by_recipe(buildings):
    """Group getFactory() buildings by recipe, summing production/consumption."""
    by_recipe = {}
    for building in buildings:
        recipe = building.get("Recipe") or "(unconfigured)"
        stats = by_recipe.setdefault(recipe, RecipeStats(recipe))
        stats.machine_count += 1

        production = building.get("production") or []
        for item in production:
            name = item.get("Name", "?")
            stats.produced[name] = stats.produced.get(name, 0.0) + (item.get("CurrentProd") or 0.0)
        if production:
            stats.efficiency_sum += sum((p.get("ProdPercent") or 0.0) for p in production) / len(production)

        for item in building.get("ingredients") or []:
            name = item.get("Name", "?")
            stats.consumed[name] = stats.consumed.get(name, 0.0) + (item.get("CurrentConsumed") or 0.0)

    return by_recipe


class SharedState:
    """Snapshot of the latest poll, guarded by `lock`. Read it under the lock
    and copy out whatever you need before releasing it.
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.session_info = None
        self.recipes: dict[str, RecipeStats] = {}
        self.power_circuits: list[dict] = []
        self.history: dict[str, deque] = defaultdict(lambda: deque(maxlen=HISTORY_MAXLEN))
        self.connected = False
        self.last_error = None


class Poller(threading.Thread):
    def __init__(self, client: FRMClient, state: SharedState):
        super().__init__(daemon=True, name="frm-poller")
        self.client = client
        self.state = state
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            started_at = time.monotonic()

            if self.state.session_info is None:
                self._fetch_session_info()

            self._poll_production_and_power()

            elapsed = time.monotonic() - started_at
            self._stop_event.wait(max(0.0, POLL_INTERVAL_SECONDS - elapsed))

    def _fetch_session_info(self):
        try:
            info = self.client.getSessionInfo()
        except FRMError as exc:
            with self.state.lock:
                self.state.connected = False
                self.state.last_error = str(exc)
            return

        with self.state.lock:
            self.state.session_info = info
            self.state.connected = True
            self.state.last_error = None

    def _poll_production_and_power(self):
        try:
            buildings = self.client.getFactory()
            power_circuits = self.client.getPower()
        except FRMError as exc:
            with self.state.lock:
                self.state.connected = False
                self.state.last_error = str(exc)
            return

        by_recipe = aggregate_factory_by_recipe(buildings or [])
        timestamp = datetime.now()

        with self.state.lock:
            self.state.connected = True
            self.state.last_error = None
            self.state.recipes = by_recipe
            self.state.power_circuits = power_circuits or []
            for recipe, stats in by_recipe.items():
                self.state.history[recipe].append((timestamp, stats.total_produced, stats.total_consumed))
