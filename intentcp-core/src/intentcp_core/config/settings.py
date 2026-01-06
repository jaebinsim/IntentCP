from __future__ import annotations

from pathlib import Path
from typing import Any
import tomllib
from pydantic import BaseModel, AnyHttpUrl, Field, ConfigDict


# Resolve paths robustly (independent of CWD)
# .../intentcp-core/src/intentcp_core/config/settings.py
# parents[0]=config, [1]=intentcp_core, [2]=src, [3]=intentcp-core
BASE_DIR = Path(__file__).resolve().parents[3]
CONFIG_DIR = BASE_DIR / "config"


class TuyaSettings(BaseModel):
    access_id: str = Field(alias="access_id")
    access_key: str = Field(alias="access_key")
    username: str
    password: str
    endpoint: str = "https://openapi.tuya.com"
    country_code: str = Field(default="82")
    app_schema: str = Field(default="tuyaSmart")


class WindowsAgentSettings(BaseModel):
    base_url: AnyHttpUrl | None = None


class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tuya: TuyaSettings
    windows_agent: WindowsAgentSettings | None = None


def load_settings(path: Path | str | None = None) -> Settings:
    if path is None:
        path = CONFIG_DIR / "settings.toml"

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"settings.toml not found at {path}. Run `intentcp init` to create it."
        )
    data: dict[str, Any] = tomllib.loads(path.read_text(encoding="utf-8"))
    return Settings.model_validate(data)


settings = load_settings()