"""
Reliability tests for explicit runtime mode classification.
"""
import pandas as pd

from drexpa.config import Config, get_default_config
from drexpa.main import (
    DrexpaPipeline,
    RUNTIME_MODE_NO_SYNERGY,
    RUNTIME_MODE_WITH_CONCENTRATIONS,
    RUNTIME_MODE_WITHOUT_CONCENTRATIONS,
)


def _base_config(tmp_path):
    config = get_default_config()
    config["global"]["base_data_dir"] = str(tmp_path)
    config["global"]["output_dir"] = str(tmp_path / "out")
    return config


def test_runtime_mode_no_synergy_data(tmp_path):
    config = _base_config(tmp_path)
    pipeline = DrexpaPipeline(Config(config), synergy_data_file=None)

    steps = ["chembl_ids", "targets"]
    pipeline._set_runtime_mode(steps)

    assert pipeline.runtime_mode == RUNTIME_MODE_NO_SYNERGY


def test_runtime_mode_with_concentrations_from_synergy_header(tmp_path):
    synergy_file = tmp_path / "synergy_with_conc.csv"
    pd.DataFrame(
        {
            "drug_name_A": ["A"],
            "drug_name_B": ["B"],
            "conc_A": [1.0],
            "conc_B": [2.0],
            "cell_line": ["CL1"],
            "synergy": [0.2],
        }
    ).to_csv(synergy_file, index=False)

    config = _base_config(tmp_path)
    pipeline = DrexpaPipeline(Config(config), synergy_data_file=str(synergy_file))

    pipeline._validate_required_columns(["load_data", "doses"])
    pipeline._set_runtime_mode(["load_data", "doses"])

    assert pipeline.runtime_mode == RUNTIME_MODE_WITH_CONCENTRATIONS


def test_runtime_mode_without_concentrations_from_synergy_header(tmp_path):
    synergy_file = tmp_path / "synergy_no_conc.csv"
    pd.DataFrame(
        {
            "drug_name_A": ["A"],
            "drug_name_B": ["B"],
            "cell_line": ["CL1"],
            "synergy": [0.2],
        }
    ).to_csv(synergy_file, index=False)

    config = _base_config(tmp_path)
    pipeline = DrexpaPipeline(Config(config), synergy_data_file=str(synergy_file))

    pipeline._validate_required_columns(["load_data", "doses"])
    pipeline._set_runtime_mode(["load_data", "doses"])

    assert pipeline.runtime_mode == RUNTIME_MODE_WITHOUT_CONCENTRATIONS
