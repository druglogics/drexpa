"""
Tests for preflight validation in the pipeline.
"""
from pathlib import Path

import pandas as pd
import pytest

from drexpa.config import get_default_config, Config
from drexpa.main import DrexpaPipeline


def _write_text(path: Path, content: str = ""):
    path.write_text(content, encoding="utf-8")


def test_preflight_fails_when_required_file_missing(tmp_path):
    config = get_default_config()
    config["global"]["base_data_dir"] = str(tmp_path)
    config["paths"]["drug_names_file"] = "missing_drug_names.txt"

    pipeline = DrexpaPipeline(Config(config), synergy_data_file=None)

    with pytest.raises(FileNotFoundError, match="drug_names_file"):
        pipeline.run_pipeline(["chembl_ids"])


def test_preflight_fails_when_required_columns_missing(tmp_path):
    synergy_file = tmp_path / "synergy_data.csv"
    pd.DataFrame(
        {
            "drug_name_A": ["DrugA"],
            "drug_name_B": ["DrugB"],
            "cell_line": ["A549"],
        }
    ).to_csv(synergy_file, index=False)

    _write_text(tmp_path / "drug_names.txt", "DrugA\nDrugB\n")
    _write_text(tmp_path / "node_dict.csv", "gene,node\nEGFR,EGFR\n")
    _write_text(tmp_path / "drug_targets.db", "")

    config = get_default_config()
    config["global"]["base_data_dir"] = str(tmp_path)
    config["paths"]["drug_names_file"] = "drug_names.txt"
    config["paths"]["node_dict_file"] = "node_dict.csv"
    config["paths"]["db_file"] = "drug_targets.db"
    config["paths"]["synergy_data_file"] = "synergy_data.csv"

    pipeline = DrexpaPipeline(Config(config), synergy_data_file=str(synergy_file))

    with pytest.raises(ValueError, match="Missing required columns"):
        pipeline.run_pipeline(["combinations"])


def test_preflight_validates_internal_db_when_targets_step_requested(tmp_path):
    """Test that preflight checks internal DB exists when targets step is in pipeline."""
    from drexpa.resources.database import get_internal_database_path

    synergy_file = tmp_path / "synergy_data.csv"
    pd.DataFrame(
        {
            "drug_name_A": ["DrugA"],
            "drug_name_B": ["DrugB"],
            "conc_A": [1.0],
            "conc_B": [2.0],
            "cell_line": ["A549"],
            "synergy": [0.2],
        }
    ).to_csv(synergy_file, index=False)

    _write_text(tmp_path / "drug_names.txt", "DrugA\nDrugB\n")
    _write_text(tmp_path / "node_dict.csv", "gene,node\nEGFR,EGFR\n")

    config = get_default_config()
    config["global"]["base_data_dir"] = str(tmp_path)
    config["paths"]["drug_names_file"] = "drug_names.txt"
    config["paths"]["node_dict_file"] = "node_dict.csv"
    config["paths"]["synergy_data_file"] = "synergy_data.csv"
    config["paths"]["db_file"] = None  # Use internal DB

    pipeline = DrexpaPipeline(Config(config), synergy_data_file=str(synergy_file))

    # Preflight should succeed because internal DB exists
    pipeline._validate_required_files(["targets"])


def test_internal_db_path_used_when_config_db_is_none():
    """Test that targets config uses internal DB path when config.paths.db_file is None."""
    from drexpa.resources.database import get_internal_database_path
    from drexpa.config import Config, get_default_config

    config = Config(get_default_config())
    targets_config = config.get_targets_config()

    internal_db_path = get_internal_database_path()
    assert targets_config["db_file"] == internal_db_path
