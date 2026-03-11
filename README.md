# DREXPA: DRug EXperimental PAnel

[![PyPI version](https://badge.fury.io/py/drexpa.svg)](https://pypi.org/project/drexpa/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**DREXPA** (DRug EXperimental PAnel) transforms experimental drug screening datasets into in silico drug panel and perturbations that can be test in Boolean models using the DrugLogics & Trafikk pipelines (drabme/Bless modules). It automates drug name resolution, target retrieval, node mapping, and creates drug panels and perturbation files compatible with in silico validation workflows.

**For first-time users:** Start with [QUICKSTART.md](QUICKSTART.md) for minimal runnable examples.  
**For project structure & internals:** See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md).  
**For maintenance & future work:** See [TODO.md](TODO.md).

---

## Overview

DREXPA orchestrates a multi-step drug screening pipeline:

```
Drug Names (TXT)
  ↓ [chembl_ids]
ChEMBL IDs
  ↓ [targets]
Drug Targets (from internal DB)
  ↓ [node_targets] + Node Dict (CSV)
Logical Model Nodes
  ↓ [profiles]
Drug Profiles (with Pipeline IDs)
  ├→ [panel] → Drug Panel (DrugLogics format)
  └→ [combinations] + Synergy Data (CSV, optional)
      ↓ [perturbations]
      Perturbation Files (per tissue/cell line)
      ↓ [synergies]
      Synergy Summaries
```

### Pipeline Modes

DREXPA automatically adapts to three execution modes:

1. **No Synergy Data**: Generates drug profiles and panel; skips doses/combinations/synergies.
2. **With Concentration Data**: Full pipeline including dose-based target extraction and combinations.
3. **Without Concentration Data**: Profiles and panel from single-dose targets; combinations from profile mapping.

---

## Installation

### From PyPI (Recommended)
```bash
pip install drexpa
```

### Development Installation
```bash
git clone https://github.com/yourusername/drexpa.git
cd drexpa
pip install -e ".[dev]"
pytest  # Validate installation
```

---

## Quick Start (CLI)

**1. Prepare input files:**
```
data/
├── drug_names.txt           # One drug per line
├── node_dict.csv            # Gene → Node mapping
└── synergy_data.csv         # Optional: drug combinations + effects
```

**2. Create config file** (`my_config.json`):
```json
{
  "global": {"output_dir": "results", "base_data_dir": "data"},
  "paths": {
    "drug_names_file": "drug_names.txt",
    "node_dict_file": "node_dict.csv",
    "synergy_data_file": "synergy_data.csv"
  },
  "options": {"double_drug_screen": true}
}
```

**3. Run pipeline:**
```bash
# Full pipeline
drexpa --config my_config.json

# Generate profiles only
drexpa --config my_config.json --until profiles

# Profiles + panel only
drexpa --config my_config.json --steps profiles,panel

# Verbose mode (structured logging + timing)
drexpa --config my_config.json --verbose
```

For detailed walkthrough, see [QUICKSTART.md](QUICKSTART.md).

---

## CLI Options

```bash
drexpa --help
```

| Option | Description | Example |
|--------|-------------|----------|
| `--config PATH` | Custom config JSON file | `--config my_config.json` |
| `--synergy-data PATH` | Override synergy data file | `--synergy-data screen.csv` |
| `--output-dir DIR` | Override output directory | `--output-dir ./results` |
| `--until STEP` | Run until step (inclusive) | `--until panel` |
| `--steps STEPS` | Specific steps (comma-separated) | `--steps profiles,panel` |
| `--verbose` | Enable structured logging + timing | `--verbose` |
| `--version` | Show version | |
| `--help` | Show full help | |

### Available Steps (Complete List)

1. `load_data` – Load synergy data
2. `chembl_ids` – Resolve ChEMBL IDs (requires ChEMBL network access)
3. `doses` – Extract & process drug doses (requires concentration columns)
4. `targets` – Query internal drug-target database
5. `node_targets` – Map targets to logical model nodes
6. `profiles` – Generate unique drug profiles with Pipeline IDs
7. `combinations` – Prepare drug combinations (requires synergy data)
8. `panel` – Create drug panel (DrugLogics format)
9. `perturbations` – Generate perturbation files per condition
10. `synergies` – Process observed synergies

**Dependencies** are resolved automatically: `--until panel` runs steps 1–8 with all prerequisites.

**For step execution flow & dependency resolution:** See [PROJECT_STRUCTURE.md § Step Definitions](PROJECT_STRUCTURE.md#step-definitions-step_registrypy).

---

## Python API

Use DREXPA programmatically:

```python
from drexpa import run_pipeline

config = {
    "global": {"output_dir": "results"},
    "paths": {
        "drug_names_file": "data/drugs.txt",
        "node_dict_file": "data/nodes.csv",
    }
}

# Full pipeline
run_pipeline(config_dict=config)

# Specific steps
run_pipeline(
    config_dict=config,
    synergy_data_file="data/synergy.csv",
    steps_to_run=["profiles", "panel"]
)
```

**For orchestration details & entry points:** See [PROJECT_STRUCTURE.md § Entry Points](PROJECT_STRUCTURE.md#entry-points).

---

## Configuration Reference

**Default config structure** (see `drexpa.config.get_default_config()`):

```json
{
  "global": {
    "output_dir": "output",
    "verbose": false,
    "save": true,
    "base_data_dir": "data"
  },
  "paths": {
    "drug_names_file": "drug_names.txt",
    "synergy_data_file": "synergy_data.csv",
    "node_dict_file": "node_dict.csv",
    "tissue_cline_file": "tissue_cline.csv",
    "db_file": null,
    "manual_chembl_csv": "manual_chembl.csv"
  },
  "columns": {
    "drug_name": "drug_name",
    "drug_name_A": "drug_name_A",
    "drug_name_B": "drug_name_B",
    "conc_A": "conc_A",
    "conc_B": "conc_B",
    "cell_line": "cell_line",
    "synergy": "synergy"
  },
  "options": {
    "synergy_threshold": 0.0,
    "double_drug_screen": true,
    "original_target_merge": "fill_missing"
  }
}
```

**Key points:**
- `db_file: null` → Uses internal package database (managed by project, not user).
- `base_data_dir` – Base path; all relative paths are resolved against it.
- `columns` – Customize column names if your data uses different headers.
- Deep-merge override: Custom config merges recursively with defaults; only specified sections override.

**For configuration flow & per-step config builders:** See [PROJECT_STRUCTURE.md § Configuration Flow](PROJECT_STRUCTURE.md#configuration-flow).

---

## Output Files

By default, outputs are written to `output_dir`:

| File | Step | Content |
|------|------|----------|
| `drug_ChEMBL_IDs.csv` | `chembl_ids` | Drug name → ChEMBL ID mapping |
| `drug_ChEMBL_doses.csv` | `doses` | Drugs with IC50 concentrations |
| `drug_ChEMBL_targets.csv` | `targets` | Drug → Targets from database |
| `drug_node_targets.csv` | `node_targets` | Drug → Logical model nodes |
| `drug_profiles.csv` | `profiles` | Drug profiles with Pipeline IDs |
| `drug_panel_df.csv` | `panel` | Drug panel (DrugLogics format) |
| `drugpanel` | `panel` | Formatted drug panel file |
| `<TISSUE>/` | `perturbations` | Per-tissue perturbation files |

---

## Troubleshooting

### Missing Required Files

**Error:** `FileNotFoundError: Preflight validation failed. Missing required files`

**Fix:** Check file paths in config. Ensure `base_data_dir` is correct.

### Missing Required Columns

**Error:** `ValueError: Missing required columns in synergy data`

**Fix:** Verify `columns` section in config matches your data headers. Use `--verbose` to see exact missing columns.

### ChEMBL Resolution Fails

**Error:** Network timeout or no results for drug name

**Fix:** 
- Check drug name spelling (must match ChEMBL exactly or be unambiguous).
- Provide manual ChEMBL mapping in `manual_chembl.csv` to skip network queries.
- Run with `--verbose` to see which drugs failed.

### Internal Database Missing

**Error:** `FileNotFoundError: Internal drug-target interaction database not found`

**Fix:** Indicates broken DREXPA installation. Reinstall: `pip install --upgrade drexpa`

---

## Advanced Features

### Manual ChEMBL Mapping

Provide a CSV to override ChEMBL resolution (skip network queries):

```csv
drug_name,ChEMBL_ID
Aspirin,CHEMBL25
Ibuprofen,CHEMBL521
```

Configure in `paths.manual_chembl_csv`.

### Custom Config Merge

Configs deep-merge with defaults, so you only specify changes:

```json
{
  "global": {"output_dir": "custom_results"},
  "paths": {"drug_names_file": "my_drugs.txt"}
}
```

Unspecified keys inherit defaults; all section keys must remain intact.

### Verbose Logging & Timing

Enable structured logs + per-step timing:

```bash
drexpa --config my_config.json --verbose
```

Output includes:
- Step start/end timestamps
- Per-step duration (seconds)
- Preflight warnings & validation details
- Pipeline summary

---

## Data Format Specifications

### Drug Names File
Plain text, one drug per line:
```
Aspirin
Ibuprofen
Paracetamol
```

### Node Dictionary (CSV)  
Gene/protein symbols mapped to logical model node names:
```csv
gene,node
EGFR,EGFR_node
TP53,p53
BRAF,BRAF_node
```

### Synergy Data (CSV)

**With concentration data** (dual-drug screening):
```csv
drug_name_A,drug_name_B,conc_A,conc_B,tissue,cell_line,synergy
Aspirin,Ibuprofen,1.0,2.0,Breast,MCF7,0.15
```

**Without concentration data** (single-dose combinations):
```csv
drug_name_A,drug_name_B,tissue,cell_line,synergy
Aspirin,Ibuprofen,Breast,MCF7,0.15
```

### Tissue-Cell Line Mapping (CSV)
```csv
tissue,cell_line
Breast,MCF7
Breast,T47D
Colorectal,HCT116
```

---

## For Maintainers

### Updating Internal Database  

The drug-target interaction database is shipped with the package. To update:

1. Replace `drexpa/resources/DrugTargetInteractionDB.db` with new database file.
2. Update version in `pyproject.toml`.
3. Add changelog entry.
4. Rebuild and release: `pip install build; python -m build; twine upload dist/*`

### Running Tests

```bash
pytest tests/ -q  # Quick run
pytest tests/ --cov  # Coverage report
```

### Development Workflow

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for module architecture and [TODO.md](TODO.md) for planned improvements.

---

## License

MIT License. See LICENSE file for details.

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run `pytest` to validate
5. Submit pull request

---

## Support & Citation

If DREXPA is helpful in your research, please cite:

```bibtex
@software{drexpa2024,
  title = {DREXPA: Drug Experimental Panel Generator},
  author = {Bermudez Paiva, Viviam},
  year = {2024},
  url = {https://github.com/yourusername/drexpa}
}
```

For issues, feature requests, or questions: [GitHub Issues](https://github.com/yourusername/drexpa/issues)

---

## Quick Links

- **[QUICKSTART.md](QUICKSTART.md)** – Two minimal runnable examples (with & without concentrations)
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** – Module architecture, entry points, legacy code
- **[TODO.md](TODO.md)** – Roadmap (P2 architecture improvements, caching, extensibility)