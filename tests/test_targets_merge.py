import pandas as pd

from drexpa.features.targets import TargetProcessor


def test_merge_manual_targets_dual_drug_does_not_cross_contaminate_targets():
    processor = TargetProcessor(
        column_drugname="drug_name",
        column_concentration="concentration",
        manual_targets_column=["targets_A", "targets_B"],
        merge_strategy="combine",
    )

    chembl_targets_df = pd.DataFrame(
        {
            "drug_name": ["AZD-8055", "SN-38", "Oxaliplatin"],
            "concentration": [1250, 625, 20000],
            "targets": ["RPTOR", "TOP1", None],
            "ChEMBL_conc": [
                "CHEMBL_AZD_1250_nM",
                "CHEMBL_SN38_625_nM",
                "CHEMBL_OXA_20000_nM",
            ],
        }
    )

    manual_df = pd.DataFrame(
        {
            "drug_name_A": ["AZD-8055", "AZD-8055"],
            "drug_name_B": ["SN-38", "Oxaliplatin"],
            "conc_A": [1250, 1250],
            "conc_B": [625, 20000],
            "targets_A": ["RPTOR, PRR5", "RPTOR, PRR5"],
            "targets_B": ["chemo", "chemo"],
        }
    )

    merged = processor._merge_manual_targets(chembl_targets_df, manual_df)

    sn38_targets = merged.loc[
        (merged["drug_name"] == "SN-38") & (merged["concentration"] == 625), "targets"
    ].iloc[0]
    oxa_targets = merged.loc[
        (merged["drug_name"] == "Oxaliplatin") & (merged["concentration"] == 20000), "targets"
    ].iloc[0]

    assert "chemo" in sn38_targets
    assert "RPTOR" not in sn38_targets
    assert "PRR5" not in sn38_targets

    assert "chemo" in oxa_targets
    assert "RPTOR" not in oxa_targets
    assert "PRR5" not in oxa_targets
