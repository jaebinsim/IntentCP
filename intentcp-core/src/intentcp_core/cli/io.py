from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import tomllib


def _core_root() -> Path:
    """Resolve the `intentcp-core` package root directory.

    This file lives at:
      intentcp-core/src/intentcp_core/cli/io.py
    So parents (Path.parents):
      0=cli, 1=intentcp_core, 2=src, 3=intentcp-core

    We store runtime config files in (spec):
      intentcp-core/config/
    """

    return Path(__file__).resolve().parents[3]


def default_settings_path() -> Path:
    return _core_root() / "config" / "settings.toml"


def default_devices_path() -> Path:
    return _core_root() / "config" / "devices.toml"


def config_dir() -> Path:
    """Return the IntentCP core config directory (spec)."""
    return _core_root() / "config"


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_toml_if_exists(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    data = path.read_bytes()
    if not data:
        return {}

    try:
        return dict(tomllib.loads(data.decode("utf-8")))
    except Exception:
        # Keep it safe: if parsing fails, don't crash the wizard.
        # The doctor command should provide stricter validation.
        return {}


def _toml_escape_basic(value: str) -> str:
    # Minimal escaping for TOML basic strings.
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _toml_dump(obj: Any, indent: int = 0) -> str:
    """Very small TOML writer.

    This avoids adding a heavy dependency (tomlkit). It supports:
    - dict[str, Any]
    - str/int/float/bool
    - nested dicts as tables

    It is intentionally minimal for IntentCP config needs.
    """

    lines: list[str] = []

    # First write scalar keys
    if isinstance(obj, dict):
        scalar_items: list[tuple[str, Any]] = []
        table_items: list[tuple[str, dict]] = []

        for k, v in obj.items():
            if isinstance(v, dict):
                table_items.append((k, v))
            else:
                scalar_items.append((k, v))

        for k, v in scalar_items:
            if isinstance(v, bool):
                vv = "true" if v else "false"
            elif isinstance(v, (int, float)):
                vv = str(v)
            elif v is None:
                vv = '""'
            else:
                vv = f'"{_toml_escape_basic(str(v))}"'
            lines.append(f"{k} = {vv}")

        # Then write nested tables
        for k, v in table_items:
            if lines:
                lines.append("")
            lines.append(f"[{k}]")
            lines.append(_toml_dump(v, indent=indent))

        return "\n".join(lines).strip() + "\n"

    raise TypeError(f"Unsupported type for TOML dump: {type(obj)}")


def write_toml(path: Path, data: Dict[str, Any]) -> None:
    ensure_parent_dir(path)
    text = _toml_dump(data)
    path.write_text(text, encoding="utf-8")
