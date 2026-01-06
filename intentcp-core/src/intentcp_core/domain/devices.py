# src/intentcp_core/domain/devices.py
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional, Dict

import tomllib
from pydantic import BaseModel, Field


class DeviceKind(str, Enum):
    LIGHT = "light"
    SWITCH = "switch"
    AIRCON = "aircon"
    PROJECTOR = "projector"
    WINDOWS_PC = "windows_pc"


class DeviceInfo(BaseModel):
    kind: DeviceKind
    tuya_device_id: Optional[str] = None

    tuya_on_device_id: Optional[str] = None
    tuya_off_device_id: Optional[str] = None

    location: Optional[str] = None
    supports_brightness: bool = False
    supports_temperature: bool = False


# ─────────────────────────────────────────────
# TOML 로딩
# ─────────────────────────────────────────────

# Resolve paths robustly (independent of CWD)
# .../intentcp-core/src/intentcp_core/domain/devices.py
# parents[0]=domain, [1]=intentcp_core, [2]=src, [3]=intentcp-core
_BASE_DIR = Path(__file__).resolve().parents[3]
_CONFIG_DIR = _BASE_DIR / "config"
_DEVICES_FILE = _CONFIG_DIR / "devices.toml"

# In-process cache to avoid requiring server restarts on config edits.
_DEVICE_REGISTRY_CACHE: Dict[str, DeviceInfo] | None = None
_DEVICE_REGISTRY_MTIME_NS: int | None = None

# Keys in DEVICE_REGISTRY are logical device names (e.g. "bed_light", "living_light")
# defined in config/devices.toml under the [devices.*] tables.
def _load_device_registry() -> Dict[str, DeviceInfo]:
    if not _DEVICES_FILE.exists():
        # Fresh setup: allow server to boot without devices configured yet.
        return {}

    data = tomllib.loads(_DEVICES_FILE.read_text(encoding="utf-8"))

    devices_raw = data.get("devices", {})
    if not isinstance(devices_raw, dict):
        return {}

    registry: Dict[str, DeviceInfo] = {}

    for logical_name, cfg in devices_raw.items():
        registry[logical_name] = DeviceInfo.model_validate(cfg)

    return registry



def get_device_registry() -> Dict[str, DeviceInfo]:
    """Return the latest device registry, reloading if config/devices.toml changed."""
    global _DEVICE_REGISTRY_CACHE, _DEVICE_REGISTRY_MTIME_NS

    if not _DEVICES_FILE.exists():
        _DEVICE_REGISTRY_CACHE = {}
        _DEVICE_REGISTRY_MTIME_NS = None
        return _DEVICE_REGISTRY_CACHE

    mtime_ns = _DEVICES_FILE.stat().st_mtime_ns
    if _DEVICE_REGISTRY_CACHE is None or _DEVICE_REGISTRY_MTIME_NS != mtime_ns:
        _DEVICE_REGISTRY_CACHE = _load_device_registry()
        _DEVICE_REGISTRY_MTIME_NS = mtime_ns

    return _DEVICE_REGISTRY_CACHE


def get_device_info(device_name: str) -> Optional[DeviceInfo]:
    return get_device_registry().get(device_name)


# Backwards-compatible snapshot (may be stale). Prefer `get_device_registry()`.
DEVICE_REGISTRY: Dict[str, DeviceInfo] = get_device_registry()