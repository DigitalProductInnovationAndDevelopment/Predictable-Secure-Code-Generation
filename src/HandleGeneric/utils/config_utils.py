"""
Configuration utility functions for HandleGeneric.

This module contains utility functions for configuration management.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_json_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to the JSON configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_json_config(config: Dict[str, Any], config_path: Path) -> None:
    """
    Save configuration to JSON file.

    Args:
        config: Configuration dictionary
        config_path: Path where to save the configuration
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def save_yaml_config(config: Dict[str, Any], config_path: Path) -> None:
    """
    Save configuration to YAML file.

    Args:
        config: Configuration dictionary
        config_path: Path where to save the configuration
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from file (auto-detect format).

    Args:
        config_path: Path to the configuration file

    Returns:
        Configuration dictionary
    """
    if config_path.suffix.lower() in [".yaml", ".yml"]:
        return load_yaml_config(config_path)
    else:
        return load_json_config(config_path)


def merge_configs(
    base_config: Dict[str, Any], override_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries.

    Args:
        base_config: Base configuration
        override_config: Configuration to override with

    Returns:
        Merged configuration
    """
    result = base_config.copy()

    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get a configuration value using dot notation.

    Args:
        config: Configuration dictionary
        key_path: Dot-separated path to the key (e.g., "database.host")
        default: Default value if key doesn't exist

    Returns:
        Configuration value or default
    """
    keys = key_path.split(".")
    current = config

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current
