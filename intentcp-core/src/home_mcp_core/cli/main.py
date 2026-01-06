from __future__ import annotations

import typer
from rich import print

from home_mcp_core.cli.wizard import run_setup_wizard
from home_mcp_core.cli.validate import run_doctor
from home_mcp_core.cli.devices import app as devices_app

app = typer.Typer(
    name="homemcp",
    help="HomeMCP CLI — setup, validate, and run your Home Control Plane",
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
    print("[bold cyan]🚀 HomeMCP Setup Wizard[/bold cyan]")
    run_setup_wizard()


@app.command()
def doctor():
    """
    Validate current HomeMCP configuration.

    - Checks settings.toml existence and format
    - Tests Tuya Cloud connectivity
    - Prints actionable error messages
    """
    print("[bold yellow]🩺 HomeMCP Doctor[/bold yellow]")
    run_doctor()


if __name__ == "__main__":
    app()
