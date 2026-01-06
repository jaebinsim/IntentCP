# src/intentcp_core/app.py
from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from rich import print as rich_print

from .routers import control, panel, status, health


def create_app() -> FastAPI:
    app = FastAPI(
        title="IntentCP Core",
        version="0.1.0",
    )

    # Static (Admin Panel assets)
    base_dir = Path(__file__).resolve().parents[2]  # .../intentcp-core
    static_dir = base_dir / "web" / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Routers
    # status / health / panel routers define their own prefixes internally.
    app.include_router(status.router)
    app.include_router(health.router)
    app.include_router(panel.router)

    # control router is mounted under /tuya
    app.include_router(control.router, prefix="/tuya", tags=["tuya"])

    @app.on_event("startup")
    async def _startup_message():
        host = os.getenv("HOST", "127.0.0.1")
        # Uvicorn commonly uses PORT; fall back to 8000 if not set
        port = os.getenv("PORT") or os.getenv("UVICORN_PORT") or "8000"
        rich_print(
            "\n[bold green]🚀 IntentCP server is running[/bold green]\n"
            "Web Panel:\n"
            f"[bold cyan]👉 http://{host}:{port}/panel/[/bold cyan]\n"
            "[dim]If you are running on a different host or port, adjust the URL accordingly.[/dim]\n"
        )

    return app


app = create_app()