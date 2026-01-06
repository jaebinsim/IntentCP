# routers/control.py
from fastapi import APIRouter, HTTPException, Query
from typing import Any

import asyncio
from dataclasses import dataclass
from urllib.parse import parse_qs
import anyio

from ..domain.devices import DEVICE_REGISTRY, DeviceInfo, DeviceKind
from ..services.tuya_client import tuya_client

router = APIRouter()

# --- New URL scheme (IntentCP v1):
# Single action:
#   /{device}/{action}[?delay=seconds]
# Sequence:
#   /sequence?actions=step1,step2,...
#   step format: {device}:{action}[?delay=seconds]
#
# Note: We keep the legacy `/devices/{device}/...` routes for compatibility.

@dataclass(frozen=True)
class _SeqStep:
    device: str
    action: str
    delay: int = 0

def _parse_delay_qs(qs: str) -> int:
    """Parse delay from a query-string fragment like 'delay=10'."""
    if not qs:
        return 0
    parsed = parse_qs(qs, keep_blank_values=True)
    raw = (parsed.get("delay") or ["0"])[0]
    try:
        d = int(raw)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid delay: {raw}")
    if d < 0:
        raise HTTPException(status_code=400, detail="delay must be >= 0")
    return d

def _parse_sequence_actions(actions: str) -> list[_SeqStep]:
    if not actions or not actions.strip():
        raise HTTPException(status_code=400, detail="actions is required")

    steps: list[_SeqStep] = []
    for raw_step in actions.split(","):
        raw_step = raw_step.strip()
        if not raw_step:
            continue

        # {device}:{action}[?delay=...]
        if ":" not in raw_step:
            raise HTTPException(status_code=400, detail=f"Invalid step: {raw_step}")

        base, *qs_parts = raw_step.split("?", 1)
        qs = qs_parts[0] if qs_parts else ""
        delay = _parse_delay_qs(qs)

        device, action = base.split(":", 1)
        device = device.strip()
        action = action.strip()
        if not device or not action:
            raise HTTPException(status_code=400, detail=f"Invalid step: {raw_step}")

        steps.append(_SeqStep(device=device, action=action, delay=delay))

    if not steps:
        raise HTTPException(status_code=400, detail="No valid steps in actions")
    return steps

async def _run_after_delay(delay: int, fn, *args, **kwargs) -> None:
    """Run a blocking function after delay seconds without blocking the event loop.
    Any exception is caught and logged to avoid crashing background tasks.
    """
    try:
        if delay > 0:
            await anyio.sleep(delay)
        await anyio.to_thread.run_sync(fn, *args, **kwargs)
    except HTTPException as e:
        # Unknown device or bad action should not crash background tasks
        # Consider this a skipped/failed step
        return
    except Exception:
        return

def _execute_single_action_now(device_name: str, action: str) -> dict[str, Any]:
    """Execute a single action immediately and return a standard response payload."""
    action = action.strip().lower()
    device_name = device_name.strip()

    try:
        info = _get_device_info(device_name)
    except HTTPException as e:
        if e.status_code == 404:
            return {
                "ok": False,
                "skipped": True,
                "reason": "unknown_device",
                "device": device_name,
                "action": action,
            }
        raise

    if action in ("on", "off"):
        if action == "on":
            device_id = _resolve_on_device_id(info)
            code = _command_code_on(info)
            resp = tuya_client.send_command(device_id, code, True)
        else:
            device_id = _resolve_off_device_id(info)
            code = _command_code_off(info)
            resp = tuya_client.send_command(device_id, code, False)

        return {
            "ok": True,
            "device": device_name,
            "action": action,
            "tuya_response": resp,
        }

    if action == "status":
        device_id = _resolve_status_device_id(info)
        status = tuya_client.get_status(device_id)
        return {"ok": True, "device": device_name, "action": "status", "status": status}

    raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


# --- IntentCP v1 routes ---

@router.post("/{device_name}/{action}")
@router.get("/{device_name}/{action}")
async def v1_device_action(
    device_name: str,
    action: str,
    delay: int = Query(0, ge=0, le=86400 * 30),
) -> dict[str, Any]:
    """Single action endpoint.

    Examples:
      /living_light/on
      /subdesk_light/off?delay=10
      /living_light/status
    """
    try:
        if delay == 0:
            return _execute_single_action_now(device_name, action)

        # Schedule and return immediately
        asyncio.create_task(_run_after_delay(delay, _execute_single_action_now, device_name, action))
        return {
            "ok": True,
            "scheduled": True,
            "device": device_name,
            "action": action,
            "delay": delay,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sequence")
@router.get("/sequence")
async def v1_sequence(actions: str = Query(...)) -> dict[str, Any]:
    """Execute multiple actions in order.

    Query:
      actions=step1,step2,...

    Step format:
      {device}:{action}[?delay=seconds]

    Example:
      /sequence?actions=door:open,living_light:on,living_light:off?delay=7200

    Notes:
      - Steps are executed in the order they appear.
      - Each step can have its own delay (relative to *now*).
    """
    try:
        steps = _parse_sequence_actions(actions)

        scheduled: list[dict[str, Any]] = []
        for idx, step in enumerate(steps):
            # For now, we schedule each step independently relative to now.
            asyncio.create_task(_run_after_delay(step.delay, _execute_single_action_now, step.device, step.action))
            scheduled.append(
                {
                    "index": idx,
                    "device": step.device,
                    "action": step.action,
                    "delay": step.delay,
                }
            )

        return {"ok": True, "scheduled": True, "count": len(scheduled), "steps": scheduled}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions to resolve Tuya command codes for ON/OFF based on device metadata
def _command_code_on(info: DeviceInfo) -> str:
    """
    Decide which Tuya command code to use for turning a device ON.

    Heuristic for now:
    - Dimmable lights (supports_brightness): use 'switch_led'
    - Everything else (Fingerbot, smart plug, etc.): use 'switch_1'
    Later this can be driven fully from config.
    """
    if info.kind == DeviceKind.LIGHT and info.supports_brightness:
        return "switch_led"
    return "switch_1"


def _command_code_off(info: DeviceInfo) -> str:
    """
    Decide which Tuya command code to use for turning a device OFF.

    Same heuristic as _command_code_on; many Tuya devices use the same
    boolean 'switch_1' (or 'switch_led') field for both on/off.
    """
    if info.kind == DeviceKind.LIGHT and info.supports_brightness:
        return "switch_led"
    return "switch_1"


def _get_device_info(device_name: str) -> DeviceInfo:
    info = DEVICE_REGISTRY.get(device_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Unknown device: {device_name}")
    return info


def _resolve_on_device_id(info: DeviceInfo) -> str:
    if getattr(info, "tuya_on_device_id", None):
        return info.tuya_on_device_id  # type: ignore[return-value]
    if info.tuya_device_id:
        return info.tuya_device_id
    raise HTTPException(status_code=500, detail="No Tuya device configured for ON")


def _resolve_off_device_id(info: DeviceInfo) -> str:
    if getattr(info, "tuya_off_device_id", None):
        return info.tuya_off_device_id  # type: ignore[return-value]
    if info.tuya_device_id:
        return info.tuya_device_id
    raise HTTPException(status_code=500, detail="No Tuya device configured for OFF")


def _resolve_status_device_id(info: DeviceInfo) -> str:
    # Prefer main device_id, then ON, then OFF as a fallback for status checks
    if info.tuya_device_id:
        return info.tuya_device_id
    if getattr(info, "tuya_on_device_id", None):
        return info.tuya_on_device_id  # type: ignore[return-value]
    if getattr(info, "tuya_off_device_id", None):
        return info.tuya_off_device_id  # type: ignore[return-value]
    raise HTTPException(status_code=500, detail="No Tuya device configured for status")



@router.post("/devices/{device_name}/on")
@router.get("/devices/{device_name}/on")
async def device_on(device_name: str) -> dict[str, Any]:
    info = _get_device_info(device_name)
    try:
        device_id = _resolve_on_device_id(info)
        code = _command_code_on(info)
        resp = tuya_client.send_command(device_id, code, True)
        return {
            "ok": True,
            "device": device_name,
            "action": "on",
            "tuya_response": resp,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/devices/{device_name}/off")
@router.get("/devices/{device_name}/off")
async def device_off(device_name: str) -> dict[str, Any]:
    info = _get_device_info(device_name)
    try:
        device_id = _resolve_off_device_id(info)
        code = _command_code_off(info)
        resp = tuya_client.send_command(device_id, code, False)
        return {
            "ok": True,
            "device": device_name,
            "action": "off",
            "tuya_response": resp,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/devices/{device_name}/brightness/{value}")
async def device_brightness(device_name: str, value: int) -> dict[str, Any]:
    info = _get_device_info(device_name)

    if not info.supports_brightness:
      raise HTTPException(status_code=400, detail="Device does not support brightness")

    if value < 1 or value > 100:
        raise HTTPException(status_code=400, detail="Brightness must be between 1 and 100")

    try:
        if not info.tuya_device_id:
            raise HTTPException(status_code=500, detail="No Tuya device configured for brightness control")
        tuya_client.send_command(info.tuya_device_id, "bright_value_v2", value)
        return {"ok": True, "device": device_name, "action": "brightness", "value": value}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_name}/status")
async def device_status(device_name: str) -> dict[str, Any]:
    info = _get_device_info(device_name)
    try:
        device_id = _resolve_status_device_id(info)
        status = tuya_client.get_status(device_id)
        return {"ok": True, "device": device_name, "status": status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sequence/{name}")
async def run_sequence(name: str) -> dict[str, Any]:
    """
    Basic preset sequences.
    movie: turn off main lights (bed, subdesk)
    sleep: turn off all lights
    mood: turn on bed light with ~40% brightness
    """
    try:
        if name == "movie":
            for name in ["bed_light", "subdesk_light"]:
                info = DEVICE_REGISTRY.get(name)
                if info:
                    device_id = _resolve_off_device_id(info)
                    tuya_client.send_command(device_id, "switch_led", False)

            return {"ok": True, "sequence": "movie"}

        elif name == "sleep":
            for name, info in DEVICE_REGISTRY.items():
                try:
                    device_id = _resolve_off_device_id(info)
                except HTTPException:
                    continue
                tuya_client.send_command(device_id, "switch_led", False)

            return {"ok": True, "sequence": "sleep"}

        elif name == "mood":
            info = DEVICE_REGISTRY.get("bed_light")
            if not info:
                raise HTTPException(status_code=404, detail="bed_light not defined")

            device_id = _resolve_on_device_id(info)
            tuya_client.send_command(device_id, "switch_led", True)
            try:
                if info.supports_brightness and info.tuya_device_id:
                    tuya_client.send_command(info.tuya_device_id, "bright_value_v2", 40)
            except Exception:
                # brightness failure is non-fatal for mood sequence
                pass

            return {"ok": True, "sequence": "mood"}

        else:
            raise HTTPException(status_code=400, detail="Unknown sequence")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))