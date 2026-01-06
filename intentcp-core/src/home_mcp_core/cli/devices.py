

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import tomllib
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

from .io import default_devices_path

app = typer.Typer(help="Manage HomeMCP devices.toml (alias-based device registry).")

console = Console()


def _read_toml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    raw = path.read_bytes()
    if not raw:
        return {}
    return tomllib.loads(raw.decode("utf-8"))


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _toml_quote(s: str) -> str:
    # Minimal TOML string quoting (good enough for ids/aliases/notes)
    escaped = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _toml_value(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        # Avoid scientific notation for common values
        return format(v, "f").rstrip("0").rstrip(".") or "0"
    if v is None:
        return '""'
    return _toml_quote(str(v))


def _write_devices_file(path: Path, devices: Dict[str, Dict[str, Any]]) -> None:
    """Write devices.toml.

    Note: This writer intentionally keeps the format simple and deterministic.
    It does NOT preserve comments or ordering from an existing file.
    """

    lines: List[str] = []

    # Deterministic ordering
    for alias in sorted(devices.keys()):
        block = devices[alias] or {}
        lines.append(f"[devices.{alias}]")

        # Keep a pleasant key order for the common fields, then add remaining keys.
        preferred = [
            "kind",
            "location",
            "tuya_device_id",
            "tuya_on_device_id",
            "tuya_off_device_id",
            "base_url",
            "supports_brightness",
            "supports_temperature",
            "note",
        ]
        emitted = set()
        for k in preferred:
            if k in block:
                lines.append(f"{k} = {_toml_value(block[k])}")
                emitted.add(k)

        for k in sorted(block.keys()):
            if k in emitted:
                continue
            lines.append(f"{k} = {_toml_value(block[k])}")

        lines.append("")

    _ensure_parent(path)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _load_devices(path: Optional[Path] = None) -> Tuple[Path, Dict[str, Dict[str, Any]]]:
    devices_path = path or default_devices_path()
    data = _read_toml(devices_path)
    devices_raw = data.get("devices", {}) if isinstance(data, dict) else {}
    if not isinstance(devices_raw, dict):
        devices_raw = {}

    # Normalize: alias -> dict
    devices: Dict[str, Dict[str, Any]] = {}
    for alias, raw in devices_raw.items():
        if isinstance(raw, dict):
            devices[str(alias)] = dict(raw)

    return devices_path, devices


def _save_devices(path: Path, devices: Dict[str, Dict[str, Any]]) -> None:
    _write_devices_file(path, devices)


def _bool_prompt(label: str, default: bool) -> bool:
    return Confirm.ask(label, default=default)


def _print_path_hint(path: Path) -> None:
    console.print(f"[dim]devices.toml (spec):[/dim] {path}")


@app.command("list")
def list_devices(path: Optional[Path] = typer.Option(None, "--path", help="Override devices.toml path"), verbose: bool = typer.Option(False, "--verbose", help="Show more columns")) -> None:
    """List registered devices."""

    devices_path, devices = _load_devices(path)
    _print_path_hint(devices_path)

    if not devices:
        console.print(Panel.fit("No devices configured yet. Use `homemcp devices add`.", title="Devices"))
        raise typer.Exit(code=0)

    table = Table(title="HomeMCP Devices")
    table.add_column("alias", style="bold")
    table.add_column("kind")
    table.add_column("location")
    if verbose:
        table.add_column("tuya_device_id")
        table.add_column("tuya_on_device_id")
        table.add_column("tuya_off_device_id")
        table.add_column("base_url")
    table.add_column("note")

    for alias in sorted(devices.keys()):
        d = devices[alias]
        kind = str(d.get("kind", ""))
        location = str(d.get("location", ""))
        note = str(d.get("note", ""))

        row = [alias, kind, location]
        if verbose:
            row += [
                str(d.get("tuya_device_id", "")),
                str(d.get("tuya_on_device_id", "")),
                str(d.get("tuya_off_device_id", "")),
                str(d.get("base_url", "")),
            ]
        row += [note]
        table.add_row(*row)

    console.print(table)


@app.command("show")
def show_device(alias: str, path: Optional[Path] = typer.Option(None, "--path", help="Override devices.toml path")) -> None:
    """Show a single device block."""

    devices_path, devices = _load_devices(path)
    _print_path_hint(devices_path)

    if alias not in devices:
        console.print(Panel.fit(f"Unknown alias: {alias}", title="Not Found", border_style="red"))
        raise typer.Exit(code=1)

    d = devices[alias]
    # Pretty-ish TOML-like output
    lines = [f"[devices.{alias}]"]
    for k in sorted(d.keys()):
        lines.append(f"{k} = {_toml_value(d[k])}")

    console.print(Panel("\n".join(lines), title=f"devices.{alias}"))


@app.command("remove")
def remove_device(alias: str, yes: bool = typer.Option(False, "-y", "--yes", help="Do not ask for confirmation"), path: Optional[Path] = typer.Option(None, "--path", help="Override devices.toml path")) -> None:
    """Remove a device by alias."""

    devices_path, devices = _load_devices(path)
    _print_path_hint(devices_path)

    if alias not in devices:
        console.print(Panel.fit(f"Unknown alias: {alias}", title="Not Found", border_style="red"))
        raise typer.Exit(code=1)

    if not yes:
        ok = Confirm.ask(f"Remove device '{alias}'?", default=False)
        if not ok:
            raise typer.Exit(code=0)

    devices.pop(alias, None)
    _save_devices(devices_path, devices)
    console.print(Panel.fit(f"Removed: {alias}", title="OK", border_style="green"))


@dataclass
class _AddCommon:
    alias: str
    kind: str
    location: str
    supports_brightness: bool
    supports_temperature: bool
    note: str


def _prompt_common(existing_aliases: Iterable[str]) -> _AddCommon:
    alias = Prompt.ask("Alias (unique key, e.g. living_light)").strip()
    if not alias:
        raise typer.Exit(code=1)
    if alias in set(existing_aliases):
        console.print(Panel.fit(f"Alias already exists: {alias}", title="Duplicate", border_style="red"))
        raise typer.Exit(code=1)

    kind = Prompt.ask("Kind (category, e.g., light, windows_pc, sensor, plug)", default="light").strip()
    location = Prompt.ask("Location (e.g., living, bedroom, office)", default="living").strip()

    supports_brightness = _bool_prompt("Supports brightness?", default=False)
    supports_temperature = _bool_prompt("Supports temperature?", default=False)
    note = Prompt.ask("Note (optional)", default="").strip()

    return _AddCommon(
        alias=alias,
        kind=kind,
        location=location,
        supports_brightness=supports_brightness,
        supports_temperature=supports_temperature,
        note=note,
    )


# --- Light schema validator ---
def _normalize_and_validate_block(alias: str, block: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize + validate a device block before writing.

    Rules (current schema):
    - The table key `[devices.<alias>]` is the alias.
    - `kind` is a category string (e.g. "light").
    - For lights, you may specify either:
        * `tuya_device_id` (single)
      OR
        * `tuya_on_device_id` + `tuya_off_device_id` (dual fingerbot)
      but not both.
    """
    kind = str(block.get("kind", "")).lower().strip()

    # Ensure required-ish fields are present
    if not kind:
        raise typer.BadParameter(f"'{alias}': missing required field 'kind'")

    if not str(block.get("location", "")).strip():
        raise typer.BadParameter(f"'{alias}': missing required field 'location'")

    if kind in {"light", "lamp", "switch"}:
        has_single = bool(str(block.get("tuya_device_id", "")).strip())
        on_id = str(block.get("tuya_on_device_id", "")).strip()
        off_id = str(block.get("tuya_off_device_id", "")).strip()
        has_dual = bool(on_id or off_id)

        if has_single and has_dual:
            raise typer.BadParameter(
                f"'{alias}': do not mix 'tuya_device_id' with 'tuya_on_device_id/tuya_off_device_id'. Choose single or dual."
            )

        if has_dual:
            if not on_id or not off_id:
                raise typer.BadParameter(
                    f"'{alias}': dual fingerbot mode requires BOTH 'tuya_on_device_id' and 'tuya_off_device_id'."
                )

    return block


def _prompt_light_ids() -> Dict[str, str]:
    """Handle the 'dual fingerbot' case (on/off separated) vs single device id."""

    console.print(Panel.fit(
        "Some lights (e.g., Zigbee Fingerbot Plus FBZ501) are more reliable when you use two devices:\n"
        "- one Fingerbot dedicated to ON\n"
        "- another Fingerbot dedicated to OFF\n\n"
        "Choose the control mode below.",
        title="Light Control Mode",
    ))

    mode = Prompt.ask(
        "Control mode",
        choices=["single", "dual_fingerbot"],
        default="single",
        show_choices=True,
    ).strip()

    if mode == "dual_fingerbot":
        on_id = Prompt.ask("Tuya ON device_id (fingerbot for ON)").strip()
        off_id = Prompt.ask("Tuya OFF device_id (fingerbot for OFF)").strip()
        if not on_id or not off_id:
            raise typer.Exit(code=1)
        return {"tuya_on_device_id": on_id, "tuya_off_device_id": off_id}

    device_id = Prompt.ask("Tuya device_id").strip()
    if not device_id:
        raise typer.Exit(code=1)
    return {"tuya_device_id": device_id}


def _prompt_windows() -> Dict[str, str]:
    base_url = Prompt.ask("Windows Agent base_url", default="http://192.168.1.220:8765").strip()
    if not base_url:
        raise typer.Exit(code=1)
    return {"base_url": base_url}


@app.command("add")
def add_device(
    path: Optional[Path] = typer.Option(None, "--path", help="Override devices.toml path"),
) -> None:
    """Interactively add a device.

    This command is intentionally flexible: devices.toml may include non-Tuya devices
    and future fields. We capture common fields + a small set of kind-specific fields.
    """

    devices_path, devices = _load_devices(path)
    _print_path_hint(devices_path)

    common = _prompt_common(existing_aliases=devices.keys())

    extra: Dict[str, Any] = {}

    # Kind-specific prompts (best-effort, non-strict)
    kind_lower = common.kind.lower()
    if "windows" in kind_lower:
        extra.update(_prompt_windows())
    elif kind_lower in {"light", "lamp", "switch"}:
        extra.update(_prompt_light_ids())
    else:
        # Default: ask for an optional Tuya device_id if relevant
        if Confirm.ask("Is this a Tuya-backed device?", default=True):
            device_id = Prompt.ask("Tuya device_id (leave blank to skip)", default="").strip()
            if device_id:
                extra["tuya_device_id"] = device_id

    block: Dict[str, Any] = {
        "kind": common.kind,
        "location": common.location,
        "supports_brightness": common.supports_brightness,
        "supports_temperature": common.supports_temperature,
    }
    if common.note:
        block["note"] = common.note

    block.update(extra)

    block = _normalize_and_validate_block(common.alias, block)
    devices[common.alias] = block
    _save_devices(devices_path, devices)

    console.print(Panel.fit(
        f"Added: {common.alias}\n\nRun:\n  homemcp devices show {common.alias}",
        title="OK",
        border_style="green",
    ))