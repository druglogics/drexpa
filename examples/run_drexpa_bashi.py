"""
Example: DREXPA Pipeline with Bashi Dataset (WITH Concentration Data)

This example demonstrates the full DREXPA pipeline with drug screening data
that includes concentration information for dual-drug screening.

Runtime Mode: "with_concentrations"
- Loads synergy data with drug_name_A, drug_name_B, conc_A, conc_B, etc.
- Processes doses for both drugs
- Extracts targets at specific concentrations
- Creates combinations and perturbation panels
- Analyzes synergy metrics
"""
from drexpa import run_pipeline

# Configuration for Bashi dataset (with dose/concentration data)
config = {
    "global": {
        "output_dir": "output_bashi",
        "base_data_dir": "data/input/bashi",
        "verbose": True,
        "save": True
    },
    "paths": {
        "drug_names_file": "drug_names.txt",
        "synergy_data_file": "synergy_data.csv",
        "node_dict_file": "../CFP_nodes.csv",
        "tissue_cline_file": "tissue_cline.csv"
    },
    "columns": {
        "drug_name_A": "drug_name_A",
        "drug_name_B": "drug_name_B",
        "conc_A": "conc_A",
        "conc_B": "conc_B",
        "cell_line": "cell_line",
        "synergy": "synergy"
    },
    "options": {
        "synergy_threshold": 0.0,
        "double_drug_screen": True
    }
}

if __name__ == "__main__":
    print("=" * 80)
    print("DREXPA Example: Bashi Dataset (WITH Concentration Data)")
    print("=" * 80)
    print("\nRunning full pipeline:")
    print("  chembl_ids → doses → targets → node_targets → profiles")
    print("  → panel → combinations → perturbations → synergies")
    print()

    # Run full pipeline (all steps with automatic dependency resolution)
    run_pipeline(
        config_dict=config,
        synergy_data_file="data/input/bashi/synergy_data.csv"
    )

    print("\n" + "=" * 80)
    print("✓ Pipeline completed successfully!")
    print("=" * 80)
    print(f"\nOutput files saved to: output_bashi/")
    print("  - drug_ChEMBL_IDs.csv")
    print("  - drug_ChEMBL_doses.csv")
    print("  - drug_ChEMBL_targets.csv")
    print("  - drug_node_targets.csv")
    print("  - drug_profiles.csv")
    print("  - drug_panel_df.csv")
    print("  - drugpanel (formatted)")
    print("  - perturbation files per tissue/cell line")
    print("  - synergy analysis outputs")
