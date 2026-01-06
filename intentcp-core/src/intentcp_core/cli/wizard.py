from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from intentcp_core.cli.io import (
    default_devices_path,
    default_settings_path,
    ensure_parent_dir,
    load_toml_if_exists,
    write_toml,
)
from intentcp_core.cli.validate import validate_tuya_credentials


console = Console()


@dataclass(frozen=True)
class RegionOption:
    label: str
    endpoint: str
    region: str


REGIONS: list[RegionOption] = [
    RegionOption("US (Americas)", "https://openapi.tuyaus.com", "us"),
    RegionOption("EU (Europe)", "https://openapi.tuyaeu.com", "eu"),
    RegionOption("CN (China)", "https://openapi.tuyacn.com", "cn"),
    RegionOption("IN (India)", "https://openapi.tuyain.com", "in"),
]


def _render_region_table() -> Table:
    table = Table(title="Select your Tuya Cloud region", show_lines=True)
    table.add_column("No.", justify="right", style="bold")
    table.add_column("Region")
    table.add_column("Endpoint")

    for i, opt in enumerate(REGIONS, start=1):
        table.add_row(str(i), opt.label, opt.endpoint)

    return table


def _pick_region() -> RegionOption:
    console.print(_render_region_table())
    while True:
        raw = Prompt.ask("Enter a number", default="1")
        try:
            idx = int(raw)
            if 1 <= idx <= len(REGIONS):
                return REGIONS[idx - 1]
        except ValueError:
            pass
        console.print("[red]Invalid selection. Please enter a valid number.[/red]")


def run_setup_wizard(
    settings_path: Optional[Path] = None,
    devices_path: Optional[Path] = None,
) -> None:
    """Interactive wizard that generates settings.toml (and prepares devices.toml path).

    This wizard focuses on:
    - Prompting for Tuya credentials/region
    - Writing `settings.toml` safely
    - Validating the config immediately via Tuya token request

    `devices.toml` is not generated yet (future command: `intentcp devices sync`).
    """

    settings_path = settings_path or default_settings_path()
    devices_path = devices_path or default_devices_path()

    console.print(
        Panel.fit(
            "This wizard will create/update your IntentCP config.\n"
            "We will validate your Tuya credentials right after saving.",
            title="IntentCP Setup",
        )
    )

    # Preload existing settings to keep upgrades non-destructive
    existing = load_toml_if_exists(settings_path)

    console.print(f"[dim]settings.toml:[/dim] {settings_path}")
    console.print(f"[dim]devices.toml:[/dim]  {devices_path}")

    # Safety check: ensure config paths are under intentcp-core/
    if ("intentcp-core" not in str(settings_path)) and ("intentcp-core" not in str(settings_path)):
        console.print(
            Panel.fit(
                f"[yellow]Warning:[/yellow] settings.toml path looks unusual:\n{settings_path}\n"
                "This usually means the package was installed from a different directory.\n"
                "Consider reinstalling with: pip install -e ./intentcp-core",
                title="Path Warning",
            )
        )

    # Credentials
    tuya_existing = existing.get("tuya", {}) if isinstance(existing, dict) else {}
    default_access_id = str(tuya_existing.get("access_id") or "")
    default_access_key = str(tuya_existing.get("access_key") or "")
    default_username = str(tuya_existing.get("username") or "")
    default_country_code = str(tuya_existing.get("country_code") or "82")
    default_schema = str(tuya_existing.get("app_schema") or "tuyaSmart")
    # NOTE: This is your Tuya mobile app account password. It will be stored in settings.toml.
    # Make sure config/settings.toml is NOT committed and is kept private.
    default_password = str(tuya_existing.get("password") or "")

    access_id = Prompt.ask(
        "Tuya Access ID",
        default=default_access_id,
    ).strip()
    if not access_id:
        raise typer.Exit(code=1)

    access_key = Prompt.ask(
        "Tuya Access Secret",
        default=default_access_key,
        password=True,
    ).strip()
    if not access_key:
        raise typer.Exit(code=1)

    # Region
    console.print("\n[bold]Region[/bold]")
    picked = _pick_region()

    console.print("\n[bold]Tuya App Account[/bold]")
    username = Prompt.ask(
        "Tuya App Account Email (username)",
        default=default_username,
    ).strip()
    if not username:
        raise typer.Exit(code=1)

    # NOTE: This is your Tuya mobile app account password. It will be stored in settings.toml.
    # Make sure config/settings.toml is NOT committed and is kept private.
    password = Prompt.ask(
        "Tuya App Account Password",
        default=default_password,
        password=True,
    ).strip()
    if not password:
        raise typer.Exit(code=1)

    country_code = Prompt.ask(
        "Country Code (e.g., 82 for KR)",
        default=default_country_code,
    ).strip()
    if not country_code:
        raise typer.Exit(code=1)

    schema = Prompt.ask(
        "Tuya App Schema (default: tuyaSmart)",
        default=default_schema,
    ).strip()
    if not schema:
        raise typer.Exit(code=1)

    # Build settings dict (preserve any unrelated keys)
    new_settings = dict(existing) if isinstance(existing, dict) else {}
    tuya_block = dict(new_settings.get("tuya", {}))
    # Remove legacy/duplicate keys to keep settings.toml clean
    tuya_block.pop("client_id", None)
    tuya_block.pop("client_secret", None)
    tuya_block.pop("schema", None)
    tuya_block.pop("country_code", None)
    tuya_block.pop("app_schema", None)
    tuya_block.update(
        {
            "access_id": access_id,
            "access_key": access_key,
            "region": picked.region,
            "endpoint": picked.endpoint,
            "username": username,
            "password": password,
            "country_code": country_code,
            "app_schema": schema,
        }
    )
    new_settings["tuya"] = tuya_block

    ensure_parent_dir(settings_path)
    write_toml(settings_path, new_settings)

    console.print("\n[green]✅ Saved settings.toml[/green]")

    # Validate immediately
    console.print("\n[bold]Validating Tuya credentials…[/bold]")
    ok, message = validate_tuya_credentials(
        access_id=access_id,
        access_key=access_key,
        endpoint=picked.endpoint,
        region=picked.region,
        username=username,
        password=password,
        country_code=country_code,
        app_schema=schema,
    )

    if not ok:
        console.print(Panel.fit(f"[red]{message}[/red]", title="Validation Failed"))
        console.print(
            "\n[yellow]Tip:[/yellow] Region mismatch is the most common cause. Try a different region."
        )
        raise typer.Exit(code=2)

    console.print(Panel.fit(f"[green]{message}[/green]", title="Validation OK"))

    console.print(
        "\n[bold green]Next steps[/bold green]\n"
        "1) Run the server for LAN access (recommended):\n"
        "   [cyan]uvicorn intentcp_core.app:app --reload --host 0.0.0.0 --port 8000[/cyan]\n"
        "2) Open the Web Panel:\n"
        "   - Local: [cyan]http://127.0.0.1:8000/panel/[/cyan]\n"
        "   - LAN:   [cyan]http://<your-local-ip>:8000/panel/[/cyan]\n"
        "3) Install the Siri Shortcut and set your server URL\n"
        "4) Try: [cyan]/tuya/<device>/status[/cyan] or [cyan]/tuya/<device>/on[/cyan]\n"
    )
