"""
Rules Loader - Central configuration loader for email generation system

Loads and merges configuration from:
1. Base config (base_config.yaml) - always loaded
2. Experiment overrides (experiments/{name}.yaml) - optional
3. Tier adjustments (A vs B) - applied at load time

Provides caching to avoid repeated YAML parsing.

Usage:
    from rules_loader import load_rules

    # Load base config for tier A
    rules = load_rules(tier="A")

    # Load base + experiment for tier B
    rules = load_rules(experiment="short_subject", tier="B")
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Cache for loaded configurations
_CONFIG_CACHE: Dict[str, Dict[str, Any]] = {}

# Determine rules directory
RULES_DIR = Path(__file__).parent / "rules"


def load_rules(experiment: Optional[str] = None, tier: str = "A") -> Dict[str, Any]:
    """
    Load and merge rules configuration.

    Args:
        experiment: Optional experiment name (loads from experiments/{experiment}.yaml)
        tier: Prospect tier ("A" or "B") - affects signal thresholds

    Returns:
        Merged configuration dict with all rules

    Raises:
        FileNotFoundError: If base_config.yaml or experiment file not found
        yaml.YAMLError: If YAML parsing fails
    """
    # Create cache key
    cache_key = f"{experiment or 'base'}_{tier}"

    # Return cached config if available
    if cache_key in _CONFIG_CACHE:
        logger.debug(f"Returning cached config for {cache_key}")
        return _CONFIG_CACHE[cache_key]

    logger.info(f"Loading rules: experiment={experiment}, tier={tier}")

    # Load base config
    base_config = _load_yaml_file(RULES_DIR / "base_config.yaml")
    logger.debug("Loaded base_config.yaml")

    # Start with base config
    merged_config = base_config.copy()

    # Load and merge experiment config if specified
    if experiment:
        experiment_path = RULES_DIR / "experiments" / f"{experiment}.yaml"
        if not experiment_path.exists():
            raise FileNotFoundError(
                f"Experiment config not found: {experiment_path}"
            )

        experiment_config = _load_yaml_file(experiment_path)
        logger.debug(f"Loaded experiment config: {experiment}")

        # Deep merge experiment config into base
        merged_config = _deep_merge(merged_config, experiment_config)

    # Apply tier-specific rules
    merged_config = _apply_tier_rules(merged_config, tier)

    # Cache the result
    _CONFIG_CACHE[cache_key] = merged_config
    logger.info(f"Cached config for {cache_key}")

    return merged_config


def _load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """
    Load YAML file and return as dict.

    Args:
        file_path: Path to YAML file

    Returns:
        Parsed YAML content as dict

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")

    try:
        with open(file_path, 'r') as f:
            content = yaml.safe_load(f)

        if content is None:
            logger.warning(f"Empty YAML file: {file_path}")
            return {}

        return content

    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML file {file_path}: {e}")
        raise


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge override dict into base dict.

    Args:
        base: Base configuration dict
        override: Override configuration dict

    Returns:
        Merged dict (base is not modified)
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            result[key] = _deep_merge(result[key], value)
        else:
            # Override value
            result[key] = value

    return result


def _apply_tier_rules(config: Dict[str, Any], tier: str) -> Dict[str, Any]:
    """
    Apply tier-specific rules to configuration.

    Tier A: High-priority prospects (3+ signals)
    Tier B: Standard prospects (2+ signals)

    Args:
        config: Configuration dict
        tier: Tier level ("A" or "B")

    Returns:
        Config with tier-specific rules applied
    """
    tier = tier.upper()

    if tier not in ["A", "B"]:
        logger.warning(f"Invalid tier '{tier}', defaulting to 'A'")
        tier = "A"

    # Extract tier-specific settings from config
    tiering_config = config.get("tiering", {})
    tier_key = f"tier_{tier.lower()}"

    if tier_key in tiering_config:
        tier_settings = tiering_config[tier_key]

        # Add active tier info to config root
        config["active_tier"] = {
            "tier": tier,
            "min_signals": tier_settings.get("min_signals", 3 if tier == "A" else 2),
            "description": tier_settings.get("description", "")
        }

        logger.debug(f"Applied tier {tier} rules: min_signals={config['active_tier']['min_signals']}")
    else:
        logger.warning(f"No tier config found for {tier}, using defaults")
        config["active_tier"] = {
            "tier": tier,
            "min_signals": 3 if tier == "A" else 2,
            "description": f"Tier {tier} (default)"
        }

    return config


def clear_cache():
    """
    Clear the configuration cache.

    Useful for testing or when configs change at runtime.
    """
    global _CONFIG_CACHE
    _CONFIG_CACHE.clear()
    logger.info("Cleared rules cache")


def get_persona_patterns(config: Dict[str, Any]) -> Dict[str, list]:
    """
    Extract persona patterns from config.

    Args:
        config: Rules configuration dict

    Returns:
        Dict mapping persona -> list of title patterns
    """
    personas = config.get("personas", {})
    return {
        persona: data.get("patterns", [])
        for persona, data in personas.items()
    }


def get_constraints(config: Dict[str, Any], profile: str = "default_profile") -> Dict[str, Any]:
    """
    Extract constraints for a specific profile.

    Args:
        config: Rules configuration dict
        profile: Constraint profile name (default: "default_profile")

    Returns:
        Constraint settings dict
    """
    constraints = config.get("constraints", {})
    return constraints.get(profile, {})


def get_signal_rules(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract signal detection rules from config.

    Args:
        config: Rules configuration dict

    Returns:
        Signal rules dict with scope_types and recency_thresholds
    """
    return config.get("signal_rules", {})
