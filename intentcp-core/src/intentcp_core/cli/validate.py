from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import typer
from rich.console import Console
from rich.panel import Panel

from intentcp_core.cli.io import default_devices_path, default_settings_path, load_toml_if_exists


console = Console()


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    message: str


def _human_hint_for_failure(msg: str) -> str:
    lower = msg.lower()
    if "timeout" in lower or "timed out" in lower:
        return "Network timeout. Check your internet connection or try again."
    if "unauthorized" in lower or "401" in lower:
        return "Unauthorized. Your Access ID/Secret may be incorrect."
    if "forbidden" in lower or "403" in lower:
        return "Forbidden. Your Tuya Cloud project may not have the required API permissions."
    if "not found" in lower or "404" in lower:
        return "Endpoint not found. Region/endpoint mismatch is a common cause."
    if "region" in lower or "endpoint" in lower:
        return "Region/endpoint mismatch. Try selecting a different region in `intentcp init`."
    return "Double-check your credentials and region. Region mismatch is the most common cause."


def _pick_any_tuya_device_id(devices_data: object) -> Optional[str]:
    """Best-effort: extract a Tuya device_id from devices.toml.

    We support multiple shapes because devices.toml may evolve:
    - [devices.<name>] tuya_device_id / device_id
    - [devices.<name>] tuya_on_device_id / tuya_off_device_id (dual fingerbot)
    """
    if not isinstance(devices_data, dict):
        return None

    devices = devices_data.get("devices")
    if not isinstance(devices, dict):
        return None

    candidate_keys = [
        "tuya_device_id",
        "device_id",
        "tuya_on_device_id",
        "tuya_off_device_id",
    ]

    for _, block in devices.items():
        if not isinstance(block, dict):
            continue
        for k in candidate_keys:
            v = block.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()

    return None


def validate_tuya_credentials(
    access_id: str,
    access_key: str,
    endpoint: str,
    region: str,
    username: str,
    password: str,
    country_code: str,
    app_schema: str,
    probe_device_id: Optional[str] = None,
) -> Tuple[bool, str]:
    """Validate Tuya credentials by performing a real OpenAPI connect.

    This matches the runtime behavior of `intentcp_core.services.tuya_client`:
    - Create TuyaOpenAPI(endpoint, access_id, access_key)
    - api.connect(username, password, country_code, app_schema)

    If the SDK is not installed or connect fails, this returns (False, message).
    """

    # Basic sanity checks to produce friendly errors before SDK/network calls.
    missing = [
        name
        for name, val in [
            ("tuya.access_id", access_id),
            ("tuya.access_key", access_key),
            ("tuya.endpoint", endpoint),
            ("tuya.region", region),
            ("tuya.username", username),
            ("tuya.password", password),
            ("tuya.country_code", country_code),
            ("tuya.app_schema", app_schema),
        ]
        if not str(val).strip()
    ]
    if missing:
        return False, "Missing required config keys:\n- " + "\n- ".join(missing)

    try:
        # Prefer the official Tuya OpenAPI SDK used by the server.
        from tuya_iot import TuyaOpenAPI  # type: ignore
    except Exception as e:
        return (
            False,
            "Tuya SDK (tuya-iot-py-sdk) is not available in this environment. "
            "Install dependencies from intentcp-core (pip install -e ./intentcp-core).\n\n"
            f"Import error: {e}",
        )

    try:
        api = TuyaOpenAPI(endpoint, access_id, access_key)
        ok = api.connect(username, password, country_code, app_schema)
        if not ok:
            return False, "Tuya connect() returned False. Check username/password/country_code/app_schema and your project region."

        # Optional: perform an authenticated call to confirm requests work.
        # Prefer probing the same endpoint the server uses.
        if probe_device_id:
            resp = api.get(f"/v1.0/iot-03/devices/{probe_device_id}/status")
            if isinstance(resp, dict) and resp.get("success") is True:
                return True, f"Successfully connected to Tuya OpenAPI and fetched status for device {probe_device_id}."

            if isinstance(resp, dict):
                code = resp.get("code")
                msg = resp.get("msg") or resp.get("message") or "Unknown error"
                return False, f"Connected, but status probe failed for device {probe_device_id}: {code} {msg}"

            return True, "Successfully connected to Tuya OpenAPI."

        # If no device is configured yet, connection alone is the best we can do.
        return True, "Successfully connected to Tuya OpenAPI."

    except Exception as e:
        msg = str(e) or repr(e)
        hint = _human_hint_for_failure(msg)
        return False, f"{msg}\n\nHint: {hint}"


def run_doctor(settings_path: Optional[Path] = None) -> None:
    """Run configuration diagnostics for IntentCP."""

    settings_path = settings_path or default_settings_path()
    data = load_toml_if_exists(settings_path)

    if not settings_path.exists():
        console.print(
            Panel.fit(
                f"[red]settings.toml not found[/red]\n{settings_path}\n\n"
                "Run [bold]intentcp init[/bold] to generate it.",
                title="IntentCP Doctor",
            )
        )
        raise typer.Exit(code=1)

    tuya = data.get("tuya", {}) if isinstance(data, dict) else {}

    access_id = str(tuya.get("access_id", "")).strip()
    access_key = str(tuya.get("access_key", "")).strip()
    endpoint = str(tuya.get("endpoint", "")).strip()
    region = str(tuya.get("region", "")).strip()
    username = str(tuya.get("username", "")).strip()
    password = str(tuya.get("password", "")).strip()
    country_code = str(tuya.get("country_code", "")).strip()
    app_schema = str(tuya.get("app_schema", "")).strip()

    missing = [
        name
        for name, val in [
            ("tuya.access_id", access_id),
            ("tuya.access_key", access_key),
            ("tuya.endpoint", endpoint),
            ("tuya.region", region),
            ("tuya.username", username),
            ("tuya.password", password),
            ("tuya.country_code", country_code),
            ("tuya.app_schema", app_schema),
        ]
        if not val
    ]

    if missing:
        console.print(
            Panel.fit(
                "[red]Missing required config keys:[/red]\n- "
                + "\n- ".join(missing)
                + "\n\nRun [bold]intentcp init[/bold] to fix.",
                title="IntentCP Doctor",
            )
        )
        raise typer.Exit(code=2)

    devices_path = default_devices_path()
    devices_data = load_toml_if_exists(devices_path) if devices_path.exists() else {}
    probe_device_id = _pick_any_tuya_device_id(devices_data)

    if probe_device_id:
        console.print(f"[bold]Testing Tuya connectivity (probe device: {probe_device_id})…[/bold]")
    else:
        console.print("[bold]Testing Tuya connectivity…[/bold]")
    ok, message = validate_tuya_credentials(
        access_id=access_id,
        access_key=access_key,
        endpoint=endpoint,
        region=region,
        username=username,
        password=password,
        country_code=country_code,
        app_schema=app_schema,
        probe_device_id=probe_device_id,
    )

    if not ok:
        console.print(Panel.fit(f"[red]{message}[/red]", title="Tuya Validation Failed"))
        raise typer.Exit(code=3)

    console.print(Panel.fit(f"[green]{message}[/green]", title="Tuya Validation OK"))
    console.print("[green]✅ Your IntentCP configuration looks good.[/green]")
