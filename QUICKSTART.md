# QUICKSTART: DREXPA in 5 Minutes

Two minimal, self-contained examples showing DREXPA pipelines end-to-end.

**For in-depth documentation**, see [README.md](README.md).  
**For architecture & code layout**, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md).

---

## Example 1: With Concentration Data (Full Pipeline)

Complete dual-drug screening data flow with dose information, target extraction, and synergy analysis.

### Input Files

**`data/drug_names.txt`:**
```
Aspirin
Ibuprofen
Paracetamol
```

**`data/node_dict.csv`:**
```csv
gene,node
HGNC:5236,COX1
HGNC:5237,COX2
TP53,p53
EGFR,EGFR
```

**`data/synergy_data.csv`:**
```csv
drug_name_A,drug_name_B,conc_A,conc_B,tissue,cell_line,synergy
Aspirin,Ibuprofen,1.5,2.0,Breast,MCF7,0.18
Aspirin,Ibuprofen,2.0,3.0,Breast,T47D,0.22
Ibuprofen,Paracetamol,1.0,1.5,Colorectal,HCT116,0.05
```

### Config

**`my_config_with_doses.json`:**
```json
{
  "global": {
    "output_dir": "results_with_doses",
    "base_data_dir": "data",
    "verbose": true,
    "save": true
  },
  "paths": {
    "drug_names_file": "drug_names.txt",
    "synergy_data_file": "synergy_data.csv",
    "node_dict_file": "node_dict.csv",
    "tissue_cline_file": null
  },
  "options": {
    "double_drug_screen": true,
    "synergy_threshold": 0.0
  }
}
```

### Run

```bash
# Full pipeline (all 10 steps)
drexpa --config my_config_with_doses.json

# Or programmatically
python << 'EOF'
from drexpa import run_pipeline

config = {
    "global": {"output_dir": "results_with_doses", "base_data_dir": "data"},
    "paths": {
        "drug_names_file": "drug_names.txt",
        "synergy_data_file": "synergy_data.csv",
        "node_dict_file": "node_dict.csv"
    },
    "options": {"double_drug_screen": true}
}
run_pipeline(config_dict=config)
EOF
```

### Expected Output

```
================================================================================
RUNNING DREXPA PIPELINE
Runtime mode: with_concentrations
Steps to run: load_data, chembl_ids, doses, targets, node_targets, profiles, combinations, panel, perturbations, synergies
================================================================================

[LOAD_DATA] Load synergy data...
Loaded synergy data: (3, 9)

[CHEMBL_IDS] Get ChEMBL IDs...
Got ChEMBL IDs for 3 drugs

[DOSES] Process drug doses...
Processed doses for 6 unique drug entries

[TARGETS] Get drug targets...
Got targets for drugs

[NODE_TARGETS] Map targets to nodes...
Mapped targets to nodes

[PROFILES] Build drug profiles...
Built drug profiles: (6, 4)

[COMBINATIONS] Prepare combinations...
Prepared combinations: (3, 11)

[PANEL] Create drug panel...
Created drug panel: (6, 4)

[PERTURBATIONS] Create perturbation panels...
Created perturbation panels for all cell lines

[SYNERGIES] Process observed synergies...
Processed synergies for 3 cell lines

================================================================================
PIPELINE COMPLETED SUCCESSFULLY!
================================================================================

Output files saved to: results_with_doses
```

---

## Example 2: Without Concentration Data (Profile-Based)

Single-dose screening with synergy combinations but no concentration information.

### Input Files

**`data2/drug_names.txt`:**
```
Drug_A
Drug_B
Drug_C
```

**`data2/node_dict.csv`:**
```csv
gene,node
PTEN,PTEN
AKT1,AKT
BRAF,BRAF
```

**`data2/synergy_data_no_conc.csv`:**
```csv
drug_name_A,drug_name_B,tissue,cell_line,synergy
Drug_A,Drug_B,Lung,A549,0.12
Drug_B,Drug_C,Lung,H1975,0.08
Drug_A,Drug_C,Pancreatic,MiaPaCa2,0.25
```

### Config

**`my_config_no_doses.json`:**
```json
{
  "global": {
    "output_dir": "results_no_doses",
    "base_data_dir": "data2",
    "verbose": false
  },
  "paths": {
    "drug_names_file": "drug_names.txt",
    "synergy_data_file": "synergy_data_no_conc.csv",
    "node_dict_file": "node_dict.csv"
  },
  "options": {
    "double_drug_screen": true
  }
}
```

### Run

```bash
# Profile generation only (skips dose-dependent steps)
drexpa --config my_config_no_doses.json --until profiles

# Or full pipeline (doses skipped automatically)
drexpa --config my_config_no_doses.json

# Or via Python
python << 'EOF'
from drexpa import run_pipeline

config = {
    "global": {"output_dir": "results_no_doses", "base_data_dir": "data2"},
    "paths": {
        "drug_names_file": "drug_names.txt",
        "synergy_data_file": "synergy_data_no_conc.csv",
        "node_dict_file": "node_dict.csv"
    },
    "options": {"double_drug_screen": true}
}
run_pipeline(config_dict=config, steps_to_run=["profiles", "panel"])
EOF
```

### Expected Output

```
================================================================================
RUNNING DREXPA PIPELINE
Runtime mode: without_concentrations
Steps to run: load_data, chembl_ids, targets, node_targets, profiles, combinations, panel, perturbations, synergies
================================================================================

[LOAD_DATA] Load synergy data...
Loaded synergy data: (3, 7)

[CHEMBL_IDS] Get ChEMBL IDs...
Got ChEMBL IDs for 3 drugs

[TARGETS] Get drug targets...
Got targets for drugs

[NODE_TARGETS] Map targets to nodes...
Mapped targets to nodes

[PROFILES] Build drug profiles...
Built drug profiles: (3, 4)
Creating combinations data from synergy data (no concentrations)...
Created combinations data: (3, 12)

[COMBINATIONS] Prepare combinations...
Prepared combinations: (3, 12)

[PANEL] Create drug panel...
Created drug panel: (3, 4)

[PERTURBATIONS] Create perturbation panels...
Created perturbation panels for all cell lines

[SYNERGIES] Process observed synergies...
Processed synergies for 3 cell lines

================================================================================
PIPELINE COMPLETED SUCCESSFULLY!
================================================================================

Output files saved to: results_no_doses
```

---

## Example 3: Profile Generation Only (No Synergy Data)

Single-step minimal run: drug names → profiles. No synergy data required.

### Config

**`my_config_profiles_only.json`:**
```json
{
  "global": {
    "output_dir": "results_profiles_only",
    "base_data_dir": "data"
  },
  "paths": {
    "drug_names_file": "drug_names.txt",
    "node_dict_file": "node_dict.csv"
  }
}
```

### Run

```bash
drexpa --config my_config_profiles_only.json --until profiles
```

---

## Validation Checklist

After running a pipeline:

- [ ] `output_dir` contains `.csv` files
- [ ] `drug_profiles.csv` has `drug_name`, `node`, `Pipeline_ID` columns
- [ ] `drug_panel_df.csv` matches DrugLogics format
- [ ] No `FileNotFoundError` or column-mismatch errors
- [ ] Verbose logs show timing for each step

### Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `FileNotFoundError: drug_names.txt` | Path mismatch | Check `base_data_dir` + `drug_names_file` resolve correctly |
| `Missing required columns: conc_A, conc_B` | Conc columns absent, mode assumed `with_concentrations` | Remove `conc_A`/`conc_B` from synergy file or add them |
| `ValueError: Unknown step: invalid_step` | Typo in step name | Use `--until profiles` (not `--until profile`) |
| `ChEMBL network timeout` | External API down | Provide `manual_chembl.csv` to skip network calls |

---

## Next Steps

- **Understand runtime modes:** Read [README.md § Pipeline Modes](README.md#pipeline-modes)
- **Customize configuration:** See [README.md § Configuration Reference](README.md#configuration-reference)
- **Build scripts for production:** Use Python API + config files for reproducible workflows
- **Review module architecture:** See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
