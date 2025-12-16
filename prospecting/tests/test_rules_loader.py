"""
Tests for rules_loader.py

Tests:
- Loading base configuration
- Tier A vs B differences
- Invalid YAML handling
- Configuration caching
- Helper functions
"""

import pytest
import yaml
from pathlib import Path
import tempfile
import os
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rules_loader import (
    load_rules,
    clear_cache,
    get_persona_patterns,
    get_constraints,
    get_signal_rules,
    _load_yaml_file,
    _deep_merge,
    _apply_tier_rules,
    RULES_DIR
)


class TestLoadRules:
    """Test main load_rules function"""

    def setup_method(self):
        """Clear cache before each test"""
        clear_cache()

    def test_load_base_config_tier_a(self):
        """Test loading base config for tier A"""
        config = load_rules(tier="A")

        # Check main sections exist
        assert "personas" in config
        assert "angles" in config
        assert "offers" in config
        assert "subjects" in config
        assert "constraints" in config
        assert "signal_rules" in config
        assert "tiering" in config

        # Check tier A settings
        assert config["active_tier"]["tier"] == "A"
        assert config["active_tier"]["min_signals"] == 3

    def test_load_base_config_tier_b(self):
        """Test loading base config for tier B"""
        config = load_rules(tier="B")

        # Check tier B settings
        assert config["active_tier"]["tier"] == "B"
        assert config["active_tier"]["min_signals"] == 2

    def test_tier_case_insensitive(self):
        """Test that tier parameter is case-insensitive"""
        config_a = load_rules(tier="a")
        config_b = load_rules(tier="B")

        assert config_a["active_tier"]["tier"] == "A"
        assert config_b["active_tier"]["tier"] == "B"

    def test_invalid_tier_defaults_to_a(self):
        """Test that invalid tier defaults to A"""
        config = load_rules(tier="X")

        assert config["active_tier"]["tier"] == "A"
        assert config["active_tier"]["min_signals"] == 3

    def test_config_caching(self):
        """Test that configs are cached properly"""
        # Load twice with same params
        config1 = load_rules(tier="A")
        config2 = load_rules(tier="A")

        # Should be same object (cached)
        assert config1 is config2

        # Different params should give different objects
        config3 = load_rules(tier="B")
        assert config1 is not config3

    def test_cache_clearing(self):
        """Test cache clearing"""
        config1 = load_rules(tier="A")
        clear_cache()
        config2 = load_rules(tier="A")

        # Should be different objects after cache clear
        assert config1 is not config2

    def test_personas_structure(self):
        """Test personas section structure"""
        config = load_rules(tier="A")

        personas = config["personas"]
        assert "quality" in personas
        assert "operations" in personas
        assert "it" in personas
        assert "regulatory" in personas

        # Check patterns exist for each persona
        for persona_data in personas.values():
            assert "patterns" in persona_data
            assert isinstance(persona_data["patterns"], list)
            assert len(persona_data["patterns"]) > 0

    def test_angles_structure(self):
        """Test angles section structure"""
        config = load_rules(tier="A")

        angles = config["angles"]
        assert "regulatory_pressure" in angles
        assert "operational_cost" in angles
        assert "audit_readiness" in angles

        # Check angle structure
        for angle_key, angle_data in angles.items():
            assert "name" in angle_data
            assert "description" in angle_data
            assert "personas" in angle_data
            assert "industries" in angle_data
            assert "pain_areas" in angle_data

    def test_offers_structure(self):
        """Test offers section structure"""
        config = load_rules(tier="A")

        offers = config["offers"]
        assert "checklist_capa" in offers
        assert "benchmark_batch_release" in offers
        assert "architecture_system_sprawl" in offers

        # Check offer structure
        for offer_key, offer_data in offers.items():
            assert "deliverable" in offer_data
            assert "pain_areas" in offer_data
            assert "personas" in offer_data
            assert "text" in offer_data

    def test_subjects_structure(self):
        """Test subjects section structure"""
        config = load_rules(tier="A")

        subjects = config["subjects"]
        assert "capa" in subjects
        assert "audit_readiness" in subjects
        assert "batch_release" in subjects

        # Check each pain area has subject options
        for pain_area, subject_list in subjects.items():
            assert isinstance(subject_list, list)
            assert len(subject_list) > 0

    def test_constraints_structure(self):
        """Test constraints section structure"""
        config = load_rules(tier="A")

        constraints = config["constraints"]
        assert "default_profile" in constraints

        profile = constraints["default_profile"]
        assert "word_count_min" in profile
        assert "word_count_max" in profile
        assert "sentence_count_min" in profile
        assert "sentence_count_max" in profile
        assert "subject_word_max" in profile
        assert "no_meeting_ask" in profile
        assert "no_product_pitch" in profile
        assert "banned_phrases" in profile

        # Check constraint values
        assert profile["word_count_min"] == 50
        assert profile["word_count_max"] == 100
        assert profile["sentence_count_min"] == 3
        assert profile["sentence_count_max"] == 4
        assert profile["subject_word_max"] == 4
        assert profile["no_meeting_ask"] is True
        assert profile["no_product_pitch"] is True
        assert isinstance(profile["banned_phrases"], list)

    def test_signal_rules_structure(self):
        """Test signal_rules section structure"""
        config = load_rules(tier="A")

        signal_rules = config["signal_rules"]
        assert "scope_types" in signal_rules
        assert "recency_thresholds" in signal_rules

        # Check scope types
        scope_types = signal_rules["scope_types"]
        assert "funding_round" in scope_types
        assert "leadership_change" in scope_types
        assert "regulatory_event" in scope_types

        # Check recency thresholds
        thresholds = signal_rules["recency_thresholds"]
        assert "funding_round" in thresholds
        assert "leadership_change" in thresholds
        assert isinstance(thresholds["funding_round"], int)


class TestHelperFunctions:
    """Test helper functions"""

    def setup_method(self):
        """Clear cache before each test"""
        clear_cache()

    def test_get_persona_patterns(self):
        """Test extracting persona patterns"""
        config = load_rules(tier="A")
        patterns = get_persona_patterns(config)

        assert "quality" in patterns
        assert "operations" in patterns
        assert isinstance(patterns["quality"], list)
        assert len(patterns["quality"]) > 0

    def test_get_constraints_default(self):
        """Test extracting default constraints"""
        config = load_rules(tier="A")
        constraints = get_constraints(config)

        assert "word_count_min" in constraints
        assert "word_count_max" in constraints
        assert constraints["word_count_min"] == 50

    def test_get_constraints_invalid_profile(self):
        """Test extracting constraints with invalid profile"""
        config = load_rules(tier="A")
        constraints = get_constraints(config, profile="nonexistent")

        assert constraints == {}

    def test_get_signal_rules(self):
        """Test extracting signal rules"""
        config = load_rules(tier="A")
        signal_rules = get_signal_rules(config)

        assert "scope_types" in signal_rules
        assert "recency_thresholds" in signal_rules


class TestInvalidYAML:
    """Test handling of invalid YAML files"""

    def test_missing_base_config(self, monkeypatch):
        """Test error when base_config.yaml is missing"""
        # Temporarily point to non-existent directory
        import rules_loader
        fake_dir = Path("/tmp/nonexistent_rules_dir")
        monkeypatch.setattr(rules_loader, "RULES_DIR", fake_dir)
        clear_cache()

        with pytest.raises(FileNotFoundError):
            load_rules(tier="A")

    def test_invalid_yaml_syntax(self, tmp_path):
        """Test error when YAML has syntax errors"""
        # Create invalid YAML file
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: syntax: error:")

        with pytest.raises(yaml.YAMLError):
            _load_yaml_file(invalid_yaml)

    def test_empty_yaml_file(self, tmp_path):
        """Test loading empty YAML file"""
        empty_yaml = tmp_path / "empty.yaml"
        empty_yaml.write_text("")

        result = _load_yaml_file(empty_yaml)
        assert result == {}


class TestDeepMerge:
    """Test _deep_merge function"""

    def test_merge_simple_dicts(self):
        """Test merging simple dicts"""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}

        result = _deep_merge(base, override)

        assert result == {"a": 1, "b": 3, "c": 4}
        # Base should not be modified
        assert base == {"a": 1, "b": 2}

    def test_merge_nested_dicts(self):
        """Test merging nested dicts"""
        base = {
            "level1": {
                "level2": {
                    "a": 1,
                    "b": 2
                },
                "other": 3
            }
        }
        override = {
            "level1": {
                "level2": {
                    "b": 99,
                    "c": 100
                }
            }
        }

        result = _deep_merge(base, override)

        assert result["level1"]["level2"]["a"] == 1
        assert result["level1"]["level2"]["b"] == 99
        assert result["level1"]["level2"]["c"] == 100
        assert result["level1"]["other"] == 3

    def test_merge_with_lists(self):
        """Test that lists are replaced, not merged"""
        base = {"items": [1, 2, 3]}
        override = {"items": [4, 5]}

        result = _deep_merge(base, override)

        # Lists should be replaced, not merged
        assert result["items"] == [4, 5]


class TestApplyTierRules:
    """Test _apply_tier_rules function"""

    def test_apply_tier_a_rules(self):
        """Test applying tier A rules"""
        config = {
            "tiering": {
                "tier_a": {
                    "min_signals": 3,
                    "description": "High priority"
                }
            }
        }

        result = _apply_tier_rules(config, "A")

        assert "active_tier" in result
        assert result["active_tier"]["tier"] == "A"
        assert result["active_tier"]["min_signals"] == 3
        assert result["active_tier"]["description"] == "High priority"

    def test_apply_tier_b_rules(self):
        """Test applying tier B rules"""
        config = {
            "tiering": {
                "tier_b": {
                    "min_signals": 2,
                    "description": "Standard"
                }
            }
        }

        result = _apply_tier_rules(config, "B")

        assert result["active_tier"]["tier"] == "B"
        assert result["active_tier"]["min_signals"] == 2

    def test_tier_case_conversion(self):
        """Test that tier is case-insensitive"""
        config = {
            "tiering": {
                "tier_a": {"min_signals": 3}
            }
        }

        result = _apply_tier_rules(config, "a")
        assert result["active_tier"]["tier"] == "A"

    def test_invalid_tier_defaults(self):
        """Test that invalid tier gets default values"""
        config = {"tiering": {}}

        result = _apply_tier_rules(config, "X")

        assert result["active_tier"]["tier"] == "A"
        assert result["active_tier"]["min_signals"] == 3


class TestExperimentLoading:
    """Test experiment config loading (future feature)"""

    def test_missing_experiment_file(self):
        """Test error when experiment file doesn't exist"""
        clear_cache()

        with pytest.raises(FileNotFoundError):
            load_rules(experiment="nonexistent_experiment", tier="A")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
