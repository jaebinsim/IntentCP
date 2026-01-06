from __future__ import annotations

from typing import Any, Optional
from tuya_iot import TuyaOpenAPI
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)


class TuyaClient:
    def __init__(self) -> None:
        self._api: Optional[TuyaOpenAPI] = None

    def _ensure_connected(self) -> TuyaOpenAPI:
        if self._api is not None:
            return self._api

        api = TuyaOpenAPI(
            settings.tuya.endpoint,
            settings.tuya.access_id,
            settings.tuya.access_key,
        )

        logger.info(
            "Connecting to Tuya OpenAPI (endpoint=%s, username=%s)...",
            settings.tuya.endpoint,
            settings.tuya.username,
        )
        try:
            ok = api.connect(
                settings.tuya.username,
                settings.tuya.password,
                settings.tuya.country_code,
                settings.tuya.app_schema,
            )
        except Exception as e:
            logger.exception("Tuya OpenAPI connect() raised an exception.")
            raise RuntimeError(f"Tuya OpenAPI connect() failed: {e}") from e

        if not ok:
            logger.error("Tuya OpenAPI login failed. Check access_id/access_key/endpoint/username/password.")
            raise RuntimeError("Tuya OpenAPI login failed (connect() returned False).")

        self._api = api
        logger.info("Tuya OpenAPI connected successfully.")
        return self._api

    def send_command(self, device_id: str, code: str, value: Any) -> Any:
        api = self._ensure_connected()
        payload = {"commands": [{"code": code, "value": value}]}

        resp = api.post(
            f"/v1.0/iot-03/devices/{device_id}/commands",
            payload,
        )

        # If token is invalid/expired, clear client and retry once.
        if isinstance(resp, dict) and resp.get("code") == 1010:
            logger.warning("Tuya token invalid (code=1010), reconnecting and retrying command once...")
            self._api = None
            api = self._ensure_connected()
            resp = api.post(
                f"/v1.0/iot-03/devices/{device_id}/commands",
                payload,
            )

        return resp

    def get_status(self, device_id: str) -> Any:
        api = self._ensure_connected()
        resp = api.get(f"/v1.0/iot-03/devices/{device_id}/status")

        if isinstance(resp, dict) and resp.get("code") == 1010:
            logger.warning("Tuya token invalid (code=1010) on status call, reconnecting and retrying once...")
            self._api = None
            api = self._ensure_connected()
            resp = api.get(f"/v1.0/iot-03/devices/{device_id}/status")

        return resp


tuya_client = TuyaClient()