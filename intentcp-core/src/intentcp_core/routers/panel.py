# src/intentcp_core/routers/panel.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple

import tomllib
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/panel", tags=["panel"])

# Resolve paths robustly (independent of CWD)
# .../intentcp-core/src/intentcp_core/routers/panel.py
# parents[0]=routers, [1]=intentcp_core, [2]=src, [3]=intentcp-core
BASE_DIR = Path(__file__).resolve().parents[3]
WEB_DIR = BASE_DIR / "web"
TEMPLATES_DIR = WEB_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Config lives at repo root: intentcp-core/config/*.toml
SETTINGS_FILE = BASE_DIR / "config" / "settings.toml"
DEVICES_FILE = BASE_DIR / "config" / "devices.toml"

# ─────────────────────────────────────────────────────────────
# Simple in-process cache (reloads automatically when files change)
# ─────────────────────────────────────────────────────────────
_SETTINGS_CACHE: Dict[str, Any] = {"mtime": None, "raw": "", "obj": {}}
_DEVICES_CACHE: Dict[str, Any] = {"mtime": None, "raw": "", "obj": {}}


def _parse_toml(text: str) -> Dict[str, Any]:
    if not text.strip():
        return {}
    return tomllib.loads(text)


def _load_toml_file(path: Path, cache: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Load TOML text + parsed object with mtime-based caching."""
    if not path.exists():
        cache["mtime"] = None
        cache["raw"] = ""
        cache["obj"] = {}
        return "", {}

    mtime = path.stat().st_mtime
    if cache.get("mtime") == mtime:
        return cache.get("raw", ""), cache.get("obj", {})

    raw = path.read_text(encoding="utf-8")
    obj = _parse_toml(raw)

    cache["mtime"] = mtime
    cache["raw"] = raw
    cache["obj"] = obj
    return raw, obj


def _invalidate_config_cache() -> None:
    _SETTINGS_CACHE["mtime"] = None
    _DEVICES_CACHE["mtime"] = None


def _format_toml_error(e: Exception) -> str:
    # tomllib errors are not super friendly; keep it readable.
    return f"{type(e).__name__}: {e}"


def _mask_settings(d: Dict[str, Any]) -> Dict[str, Any]:
    """Mask secrets in settings for display purposes."""
    masked = dict(d)
    tuya = dict(masked.get("tuya", {}) or {})
    # mask common secrets
    for k in ("access_key", "secret_key", "password"):
        if k in tuya and tuya[k]:
            tuya[k] = "********"
    masked["tuya"] = tuya
    return masked


def _render_or_error(request: Request, template_name: str, context: Dict[str, Any]) -> HTMLResponse:
    """Render a template; if it fails, return a readable HTML error page."""
    try:
        return templates.TemplateResponse(template_name, context)
    except Exception as e:
        details = (
            f"Template render failed: {template_name}\n"
            f"Error: {type(e).__name__}: {e}\n\n"
            f"BASE_DIR: {BASE_DIR}\n"
            f"TEMPLATES_DIR: {TEMPLATES_DIR}\n"
            f"SETTINGS_FILE: {SETTINGS_FILE}\n"
            f"DEVICES_FILE: {DEVICES_FILE}\n"
            f"SETTINGS_FILE exists: {SETTINGS_FILE.exists()}\n"
            f"DEVICES_FILE exists: {DEVICES_FILE.exists()}\n"
        )
        return HTMLResponse(
            "<!doctype html><html><body style='font-family: ui-monospace, monospace; white-space: pre-wrap; padding: 20px;'>"
            + details
            + "</body></html>",
            status_code=500,
        )


@router.get("/ping")
async def panel_ping():
    return {"ok": True, "panel": True}


@router.get("")
async def panel_index_noslash(request: Request):
    # Handle /panel (no trailing slash) explicitly.
    return await panel_index(request)


@router.get("/debug", response_class=HTMLResponse)
async def panel_debug(request: Request):
    # A template-free page to verify routing + paths.
    details = (
        f"/panel routing OK\n\n"
        f"BASE_DIR: {BASE_DIR}\n"
        f"TEMPLATES_DIR: {TEMPLATES_DIR}\n"
        f"SETTINGS_FILE exists: {SETTINGS_FILE.exists()} ({SETTINGS_FILE})\n"
        f"DEVICES_FILE exists: {DEVICES_FILE.exists()} ({DEVICES_FILE})\n"
    )
    return HTMLResponse(
        "<!doctype html><html><body style='font-family: ui-monospace, monospace; white-space: pre-wrap; padding: 20px;'>"
        + details
        + "</body></html>",
        status_code=200,
    )


@router.get("/", response_class=HTMLResponse)
async def panel_index(request: Request):
    settings_raw, settings_obj = _load_toml_file(SETTINGS_FILE, _SETTINGS_CACHE)
    devices_raw, devices_obj = _load_toml_file(DEVICES_FILE, _DEVICES_CACHE)

    device_count = len((devices_obj.get("devices", {}) or {}).keys())
    masked_settings = _mask_settings(settings_obj)

    return _render_or_error(
        request,
        "panel/index.html",
        {
            "request": request,
            "settings_path": str(SETTINGS_FILE),
            "devices_path": str(DEVICES_FILE),
            "device_count": device_count,
            "settings_preview": masked_settings,
        },
    )


@router.get("/settings", response_class=HTMLResponse)
async def panel_settings(request: Request, saved: int = 0):
    raw, parsed = _load_toml_file(SETTINGS_FILE, _SETTINGS_CACHE)
    preview = _mask_settings(parsed)

    return _render_or_error(
        request,
        "panel/settings.html",
        {
            "request": request,
            "path": str(SETTINGS_FILE),
            "raw_toml": raw,
            "preview": preview,
            "saved": bool(saved),
            "error": None,
        },
    )


@router.post("/settings", response_class=HTMLResponse)
async def panel_settings_save(request: Request, toml_text: str = Form(...)):
    try:
        _parse_toml(toml_text)  # validate
    except Exception as e:
        # Render inline error (no redirect)
        return _render_or_error(
            request,
            "panel/settings.html",
            {
                "request": request,
                "path": str(SETTINGS_FILE),
                "raw_toml": toml_text,
                "preview": {},
                "saved": False,
                "error": _format_toml_error(e),
            },
        )

    SETTINGS_FILE.write_text(toml_text, encoding="utf-8")
    _invalidate_config_cache()
    return RedirectResponse(url="/panel/settings?saved=1", status_code=303)


@router.get("/devices", response_class=HTMLResponse)
async def panel_devices(request: Request, saved: int = 0):
    raw, parsed = _load_toml_file(DEVICES_FILE, _DEVICES_CACHE)
    devices = parsed.get("devices", {}) or {}

    return _render_or_error(
        request,
        "panel/devices.html",
        {
            "request": request,
            "path": str(DEVICES_FILE),
            "raw_toml": raw,
            "device_names": sorted(list(devices.keys())),
            "devices": devices,
            "saved": bool(saved),
            "error": None,
        },
    )


@router.post("/devices", response_class=HTMLResponse)
async def panel_devices_save(request: Request, toml_text: str = Form(...)):
    try:
        parsed = _parse_toml(toml_text)  # validate
    except Exception as e:
        # Render inline error (no redirect)
        return _render_or_error(
            request,
            "panel/devices.html",
            {
                "request": request,
                "path": str(DEVICES_FILE),
                "raw_toml": toml_text,
                "device_names": [],
                "devices": {},
                "saved": False,
                "error": _format_toml_error(e),
            },
        )

    DEVICES_FILE.write_text(toml_text, encoding="utf-8")
    _invalidate_config_cache()
    return RedirectResponse(url="/panel/devices?saved=1", status_code=303)
