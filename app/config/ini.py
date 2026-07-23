import configparser
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings

_INI_DIR = Path(__file__).parent


def load_ini(path: Path) -> configparser.ConfigParser:
    """Load and return a ConfigParser from the given path.

    Args:
        path: Absolute or relative path to the .ini file.

    Returns:
        A ConfigParser instance with the file contents parsed.
    """
    ini = configparser.ConfigParser()
    ini.read(path)
    return ini


def apply_ini_defaults(
    settings: BaseSettings,
    mapping: dict[str, tuple[str, str]],
) -> None:
    """Populate settings fields not set from the environment using .ini defaults.

    Fields already present in model_fields_set were explicitly provided via env
    var or .env file and are left untouched. The .ini file is read at most once
    per unique filename.

    Args:
        settings: The Settings instance to populate.
        mapping: Dict mapping field_name to (filename, "section.option").
    """
    cache: dict[str, Any] = {}
    for field, (filename, key) in mapping.items():
        if field not in settings.model_fields_set:
            if filename not in cache:
                cache[filename] = load_ini(_INI_DIR / filename)
            section, option = key.split(".")
            object.__setattr__(settings, field, cache[filename][section][option])
