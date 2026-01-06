from __future__ import annotations

import typer
from rich import print

from intentcp_core.cli.wizard import run_setup_wizard
from intentcp_core.cli.validate import run_doctor
from intentcp_core.cli.devices import app as devices_app

app = typer.Typer(
    name="intentcp",
    help="IntentCP CLI — setup, validate, and run your Home Control Plane",
    add_completion=False,
)

app.add_typer(devices_app, name="devices")


@app.command()
def init():
    """
    Interactive setup wizard.

    - Prompts for Tuya Cloud credentials
    - Lets you select region
    - Generates settings.toml
    - Validates connection immediately
    """
    print("[bold cyan]🚀 IntentCP Setup Wizard[/bold cyan]")
    run_setup_wizard()


@app.command()
def doctor():
    """
    Validate current IntentCP configuration.

    - Checks settings.toml existence and format
    - Tests Tuya Cloud connectivity
    - Prints actionable error messages
    """
    print("[bold yellow]🩺 IntentCP Doctor[/bold yellow]")
    run_doctor()


if __name__ == "__main__":
    app()
