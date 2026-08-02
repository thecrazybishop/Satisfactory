"""Client for the FICSIT Remote Monitoring (FRM) HTTP API.

Docs: https://docs.ficsit.app/ficsitremotemonitoring/latest/json/json.html
"""

from typing import Any, Optional

import requests

from .exceptions import (
    FRMAuthenticationError,
    FRMConnectionError,
    FRMRequestError,
)

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8080
DEFAULT_TIMEOUT = 10

AUTH_HEADER = "X-FRM-Authorization"

# Documented GET (read) endpoints. Each is exposed as a like-named method on
# FRMClient, e.g. FRMClient.getFactory() -> FRMClient.get("getFactory").
# `getAll` is intentionally excluded: it's retired per the FRM docs.
READ_ENDPOINTS = [
    "getChatMessages",
    "getAssembler",
    "getBlender",
    "getConstructor",
    "getConverter",
    "getElevators",
    "getEncoder",
    "getFactory",
    "getSmelter",
    "getRefinery",
    "getManufacturer",
    "getPackager",
    "getParticle",
    "getFoundry",
    "getBelts",
    "getCables",
    "getHypertube",
    "getPipeJunctions",
    "getPipes",
    "getPump",
    "getTrainRails",
    "getExtractor",
    "getFrackingActivator",
    "getPortal",
    "getRadarTower",
    "getResourceSinkBuilding",
    "getSpaceElevator",
    "getHUBTerminal",
    "getSwitches",
    "getGenerators",
    "getBiomassGenerator",
    "getCoalGenerator",
    "getNuclearGenerator",
    "getFuelGenerator",
    "getGeothermalGenerator",
    "getCloudInv",
    "getWorldInv",
    "getStorageInv",
    "getResourceNode",
    "getResourceGeyser",
    "getResourceWell",
    "getSessionInfo",
    "getResearchTrees",
    "getPlayer",
    "getModList",
    "getSinkList",
    "getResourceSink",
    "getExplorationSink",
    "getDroneStation",
    "getTrainStation",
    "getTruckStation",
    "getDrone",
    "getExplorer",
    "getFactoryCart",
    "getTractor",
    "getTrains",
    "getTruck",
    "getVehiclePaths",
    "getVehicles",
    "getCreatures",
    "getDoggo",
    "getDropPod",
    "getMapMarkers",
    "getPowerSlug",
    "getProdStats",
    "getRecipes",
    "getSchematics",
    "getTapes",
    "getUnlockItems",
    "getUObjectCount",
    "getPower",
    "getPowerUsage",
]


class FRMClient:
    """Talks to a running FICSIT Remote Monitoring web server.

    Read endpoints (GET) work without a token. Write endpoints (POST) require
    a token, found in-game under Configs/FicsitRemoteMonitoring/WebServer.cfg
    (Authentication_Token key).
    """

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        token: Optional[str] = None,
        scheme: str = "http",
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ):
        self.base_url = f"{scheme}://{host}:{port}"
        self.token = token
        self.timeout = timeout
        self.session = session or requests.Session()

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[dict] = None,
        json_body: Any = None,
        auth_required: bool = False,
    ) -> Any:
        headers = {}
        if auth_required:
            if not self.token:
                raise FRMAuthenticationError(
                    f"'{endpoint}' requires an FRM authentication token; none was configured."
                )
            headers[AUTH_HEADER] = self.token

        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.request(
                method, url, params=params, json=json_body, headers=headers, timeout=self.timeout
            )
        except requests.exceptions.RequestException as exc:
            raise FRMConnectionError(f"Could not reach FRM server at {url}: {exc}") from exc

        if response.status_code in (401, 403):
            raise FRMAuthenticationError(
                f"FRM server rejected the request to '{endpoint}' ({response.status_code})."
            )
        if not response.ok:
            raise FRMRequestError(
                f"FRM request to '{endpoint}' failed ({response.status_code}): {response.text}"
            )

        return response.json() if response.content else None

    def get(self, endpoint: str, **params) -> Any:
        """Call any GET (read) endpoint by name, e.g. client.get("getFactory")."""
        return self._request("GET", endpoint, params=params or None)

    def post(self, endpoint: str, body: Any) -> Any:
        """Call any POST (write) endpoint by name. Requires a configured token."""
        return self._request("POST", endpoint, json_body=body, auth_required=True)

    # -- Write endpoints (typed convenience wrappers) ------------------------

    def sendChatMessage(self, message: str, sender: Optional[str] = None, color: Optional[dict] = None):
        body = {"message": message}
        if sender is not None:
            body["sender"] = sender
        if color is not None:
            body["color"] = color
        return self.post("sendChatMessage", body)

    def setEnabled(self, id: str, status: Optional[bool] = None):
        body = {"ID": id}
        if status is not None:
            body["status"] = status
        return self.post("setEnabled", body)

    def setSwitches(
        self,
        id: str,
        name: Optional[str] = None,
        priority: Optional[int] = None,
        status: Optional[bool] = None,
    ):
        body = {"ID": id}
        if name is not None:
            body["name"] = name
        if priority is not None:
            body["priority"] = priority
        if status is not None:
            body["status"] = status
        return self.post("setSwitches", body)

    def createPing(self, x: float, y: float, z: float):
        return self.post("createPing", {"x": x, "y": y, "z": z})

    def setModSetting(self, **settings):
        if not settings:
            raise ValueError("setModSetting requires at least one setting to update.")
        return self.post("setModSetting", settings)


def _make_read_method(endpoint_name: str):
    def method(self, **params):
        return self.get(endpoint_name, **params)

    method.__name__ = endpoint_name
    method.__doc__ = f"Calls the '{endpoint_name}' read endpoint. See FRM docs for the response shape."
    return method


for _endpoint in READ_ENDPOINTS:
    setattr(FRMClient, _endpoint, _make_read_method(_endpoint))
del _endpoint
