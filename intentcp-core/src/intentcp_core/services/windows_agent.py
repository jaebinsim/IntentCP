# src/intentcp_core/services/windows_agent.py
import httpx
from ..config.settings import settings


class WindowsAgentClient:
    def __init__(self) -> None:
        self.base_url = settings.windows_agent.base_url.rstrip("/")

    def _post(self, path: str, json: dict | None = None):
        url = f"{self.base_url}{path}"
        resp = httpx.post(url, json=json or {})
        resp.raise_for_status()
        if resp.content:
            return resp.json()
        return None

    def screen_off(self):
        return self._post("/screen/off")

    def open_youtube(self, url: str):
        return self._post("/browser/youtube", {"url": url})


windows_agent = WindowsAgentClient()