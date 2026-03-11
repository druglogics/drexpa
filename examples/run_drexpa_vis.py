"""
Example: DREXPA Pipeline with Vis Dataset (WITHOUT Concentration Data)

This example demonstrates the DREXPA pipeline with drug screening data
that does NOT include concentration information (single-dose screening).

Runtime Mode: "without_concentrations"
- Loads synergy data without conc_A, conc_B columns
- Skips dose processing (uses default IC50 threshold)
- Extracts targets for all drugs at a single default concentration
- Creates combinations and perturbation panels
- Analyzes synergy metrics
"""
from drexpa import run_pipeline

# Configuration for Vis dataset (without dose/concentration data)
config = {
    "global": {
        "output_dir": "output_vis",
        "base_data_dir": "data/input/vis",
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
        "cell_line": "cell_line",
        "synergy": "synergy"
        # Note: No conc_A, conc_B defined - triggers "without_concentrations" mode
    },
    "options": {
        "synergy_threshold": 0.0,
        "double_drug_screen": True
    }
}

if __name__ == "__main__":
    print("=" * 80)
    print("DREXPA Example: Vis Dataset (WITHOUT Concentration Data)")
    print("=" * 80)
    print("\nRunning pipeline (without dose step):")
    print("  chembl_ids → targets (default IC50) → node_targets → profiles")
    print("  → panel → combinations → perturbations → synergies")
    print()

    # Run full pipeline (steps automatically adapted for no-concentration mode)
    run_pipeline(
        config_dict=config,
        synergy_data_file="data/input/vis/synergy_data.csv"
    )

    print("\n" + "=" * 80)
    print("✓ Pipeline completed successfully!")
    print("=" * 80)
    print(f"\nOutput files saved to: output_vis/")
    print("  - drug_ChEMBL_IDs.csv")
    print("  - drug_ChEMBL_targets.csv (single-dose at default IC50)")
    print("  - drug_node_targets.csv")
    print("  - drug_profiles.csv")
    print("  - drug_panel_df.csv")
    print("  - drugpanel (formatted)")
    print("  - perturbation files per tissue/cell line")
    print("  - synergy analysis outputs")
