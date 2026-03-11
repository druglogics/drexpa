"""
Tests for DREXPA configuration system
"""
import pytest
import json
import tempfile
from pathlib import Path
from drexpa.config import get_default_config, validate_config, merge_config


class TestConfig:
    """Test configuration functionality"""

    def test_default_config_structure(self):
        """Test default config has required structure"""
        config = get_default_config()

        assert isinstance(config, dict)
        assert "global" in config
        assert "paths" in config

        # Check global section
        assert "output_dir" in config["global"]
        assert "verbose" in config["global"]
        assert "save" in config["global"]

        # Check paths section
        assert "drug_names_file" in config["paths"]
        assert "node_dict_file" in config["paths"]

    def test_default_config_values(self):
        """Test default config has reasonable default values"""
        config = get_default_config()

        assert isinstance(config["global"]["output_dir"], str)
        assert isinstance(config["global"]["verbose"], bool)
        assert isinstance(config["global"]["save"], bool)

    def test_config_validation_passes_valid_config(self):
        """Test config validation accepts valid config"""
        config = get_default_config()
        # Should not raise exception
        validate_config(config)

    def test_config_validation_fails_missing_global(self):
        """Test config validation fails with missing global section"""
        config = {"paths": {}}
        with pytest.raises(ValueError):
            validate_config(config)

    def test_config_validation_fails_missing_paths(self):
        """Test config validation fails with missing paths section"""
        config = {"global": {}}
        with pytest.raises(ValueError):
            validate_config(config)

    def test_config_file_loading(self):
        """Test loading config from JSON file"""
        config_data = {
            "global": {
                "output_dir": "test_output",
                "verbose": True
            },
            "paths": {
                "drug_names_file": "test_drugs.txt"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            # Test that we can load the file (basic file I/O test)
            with open(temp_file, 'r') as f:
                loaded_config = json.load(f)

            assert loaded_config["global"]["output_dir"] == "test_output"
            assert loaded_config["global"]["verbose"] is True
        finally:
            Path(temp_file).unlink()

    def test_merge_config_deep_merges_nested_dicts(self):
        """Test deep merge preserves unspecified nested defaults."""
        base = get_default_config()
        override = {
            "global": {"output_dir": "custom_out"},
            "paths": {"drug_names_file": "custom_drugs.txt"}
        }

        merged = merge_config(base, override)

        assert merged["global"]["output_dir"] == "custom_out"
        assert merged["global"]["base_data_dir"] == base["global"]["base_data_dir"]
        assert merged["paths"]["drug_names_file"] == "custom_drugs.txt"
        assert merged["paths"]["node_dict_file"] == base["paths"]["node_dict_file"]

    def test_merge_config_does_not_mutate_inputs(self):
        """Test merge function does not mutate base config."""
        base = get_default_config()
        original_output_dir = base["global"]["output_dir"]
        override = {"global": {"output_dir": "new_output"}}

        merged = merge_config(base, override)

        assert base["global"]["output_dir"] == original_output_dir
        assert merged["global"]["output_dir"] == "new_output"