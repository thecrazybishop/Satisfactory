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
HISTORY_MAXLEN = 3600  # 1 hour of history at a 1s poll interval


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


class ItemStats:
    __slots__ = ("item", "produced", "consumed")

    def __init__(self, item):
        self.item = item
        self.produced = 0.0
        self.consumed = 0.0


def aggregate_items(buildings):
    """Aggregate produced/consumed rates per item name across ALL buildings,
    regardless of which recipe/machine they come from. This is what actually
    answers "is production of this item keeping up with what's consuming
    it" — recipe-scoped totals conflate a recipe's own ingredients with its
    output and can't answer that.
    """
    by_item = {}
    for building in buildings:
        for entry in building.get("production") or []:
            name = entry.get("Name", "?")
            stats = by_item.setdefault(name, ItemStats(name))
            stats.produced += entry.get("CurrentProd") or 0.0

        for entry in building.get("ingredients") or []:
            name = entry.get("Name", "?")
            stats = by_item.setdefault(name, ItemStats(name))
            stats.consumed += entry.get("CurrentConsumed") or 0.0

    return by_item


def total_power(power_circuits):
    """Sum production/consumption/capacity across all circuits."""
    production = sum((c.get("PowerProduction") or 0.0) for c in power_circuits)
    consumption = sum((c.get("PowerConsumed") or 0.0) for c in power_circuits)
    capacity = sum((c.get("PowerCapacity") or 0.0) for c in power_circuits)
    return production, consumption, capacity


class SharedState:
    """Snapshot of the latest poll, guarded by `lock`. Read it under the lock
    and copy out whatever you need before releasing it.
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.session_info = None
        self.recipes: dict[str, RecipeStats] = {}
        self.items: dict[str, ItemStats] = {}
        self.power_circuits: list[dict] = []
        self.power_history: deque = deque(maxlen=HISTORY_MAXLEN)
        self.history: dict[str, deque] = defaultdict(lambda: deque(maxlen=HISTORY_MAXLEN))
        self.item_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=HISTORY_MAXLEN))
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

        buildings = buildings or []
        by_recipe = aggregate_factory_by_recipe(buildings)
        by_item = aggregate_items(buildings)
        timestamp = datetime.now()

        with self.state.lock:
            self.state.connected = True
            self.state.last_error = None
            self.state.recipes = by_recipe
            self.state.items = by_item
            self.state.power_circuits = power_circuits or []
            for recipe, stats in by_recipe.items():
                self.state.history[recipe].append((timestamp, stats.total_produced, stats.total_consumed))
            for item, stats in by_item.items():
                self.state.item_history[item].append((timestamp, stats.produced, stats.consumed))

            production, consumption, capacity = total_power(self.state.power_circuits)
            self.state.power_history.append((timestamp, production, consumption, capacity))
