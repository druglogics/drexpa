# DREXPA Configuration Reference

Complete reference for all configuration keys supported by DREXPA.

If you are new to the package, start with [QUICKSTART.md](QUICKSTART.md). This file is the full schema and behavior guide.

## 1. How Configuration Is Loaded

Configuration is assembled in this order:

1. Built-in defaults from `drexpa.config.get_default_config()`.
2. CLI applies `--output-dir` and `--verbose` to that default dictionary.
3. If `--config` is passed, JSON is deep-merged into the dictionary (nested merge, override wins).

Important current behavior:
- Deep merge preserves unspecified defaults.
- In the current CLI implementation, a value from `--config` can overwrite `--output-dir` and `--verbose` if both are provided.

Programmatic API:
- `run_pipeline(config_dict=...)` uses exactly the dictionary you pass.
- `run_pipeline(synergy_data_file=...)` overrides only the synergy data path used at runtime.

## 2. Full Default Configuration

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
    "chembl_id": "ChEMBL_ID",
    "concentration": "concentration",
    "cell_line": "cell_line",
    "synergy": "synergy",
    "drug_name_A": "drug_name_A",
    "drug_name_B": "drug_name_B",
    "conc_A": "conc_A",
    "conc_B": "conc_B",
    "targets_A": "targets_A",
    "targets_B": "targets_B",
    "targets": "targets"
  },
  "options": {
    "synergy_threshold": 0.0,
    "ic50_value": null,
    "double_drug_screen": true,
    "original_target_merge": "fill_missing",
    "profile_values": "drug_name"
  }
}
```

## 3. Section-by-Section Reference

## 3.1 `global`

| Key | Type | Default | Meaning |
|---|---|---|---|
| `output_dir` | string | `"output"` | Directory for generated pipeline outputs. |
| `verbose` | bool | `false` | Enables verbose logging/prints in processors. |
| `save` | bool | `true` | If `true`, steps write files; if `false`, results stay in memory. |
| `base_data_dir` | string | `"data"` | Base directory prepended to most relative input paths in `paths`. |

Notes:
- Most file paths are resolved as `base_data_dir + relative_path`.
- `output_dir` is used as provided (not joined with `base_data_dir`).

## 3.2 `paths`

| Key | Type | Default | Required | Meaning |
|---|---|---|---|---|
| `drug_names_file` | string | `"drug_names.txt"` | Yes for most pipelines | One drug name per line. |
| `synergy_data_file` | string | `"synergy_data.csv"` | Required when running `load_data` or synergy-dependent steps | Combination screen CSV. |
| `node_dict_file` | string | `"node_dict.csv"` | Required for node mapping and downstream profile/panel steps | Gene-to-node mapping CSV. |
| `tissue_cline_file` | string or null | `"tissue_cline.csv"` | Required for `perturbations` and `synergies` preflight | Cell line to tissue mapping CSV. |
| `db_file` | string or null | `null` | Optional | Drug-target DB path override. `null` means packaged internal DB. |
| `manual_chembl_csv` | string | `"manual_chembl.csv"` | Optional | Optional manual mapping file used by ChEMBL resolver. |

Database behavior details:
- `db_file: null` uses internal packaged DB via `get_internal_database_path()`.
- If `db_file` is set, target processing joins it with `base_data_dir`.
- Current preflight behavior for `targets`/`combinations` still validates internal DB availability.

## 3.3 `columns`

Use this section when your CSV headers differ from defaults.

| Key | Default | Used For |
|---|---|---|
| `drug_name` | `drug_name` | Canonical drug-name column in intermediate tables. |
| `chembl_id` | `ChEMBL_ID` | ChEMBL ID column name. |
| `concentration` | `concentration` | Canonical concentration column in intermediate tables. |
| `cell_line` | `cell_line` | Cell line column in synergy/combinations/synergies. |
| `synergy` | `synergy` | Synergy score column. |
| `drug_name_A` | `drug_name_A` | Combination anchor drug column in input synergy data. |
| `drug_name_B` | `drug_name_B` | Combination library drug column in input synergy data. |
| `conc_A` | `conc_A` | Anchor concentration column in input synergy data. |
| `conc_B` | `conc_B` | Library concentration column in input synergy data. |
| `targets_A` | `targets_A` | Optional manual targets for anchor drug. |
| `targets_B` | `targets_B` | Optional manual targets for library drug. |
| `targets` | `targets` | Optional single-drug manual targets column. |

Practical note:
- Some feature modules still use fixed internal column names for intermediate outputs. Keeping defaults is safest unless you are actively remapping input CSV headers.

## 3.4 `options`

| Key | Type | Default | Allowed/Expected Values | Meaning |
|---|---|---|---|---|
| `synergy_threshold` | float | `0.0` | any numeric value | In `synergies`, keeps rows where `synergy > threshold`. |
| `ic50_value` | float or null | `null` | numeric or `null` | IC50 filter used in target retrieval when concentration-aware processing is active. |
| `double_drug_screen` | bool | `true` | `true` or `false` | Treat synergy input as A/B drug combinations. |
| `original_target_merge` | string | `"fill_missing"` | `fill_missing`, `combine`, `override` | How manual targets are merged with DB targets. |
| `profile_values` | string | `"drug_name"` | usually `drug_name` or `ChEMBL_conc` | Identifier used when creating profile dictionaries. |

Manual target merge strategies:
- `fill_missing`: keep DB targets, fill only missing with manual targets.
- `combine`: union DB and manual targets.
- `override`: use manual targets when present, otherwise DB targets.

## 4. Runtime Modes

DREXPA selects runtime mode from available synergy input and concentration columns:

1. `no_synergy_data`
: no synergy file provided or `load_data` not selected.
2. `with_concentrations`
: synergy data includes both concentration columns (`conc_A`, `conc_B` after remap).
3. `without_concentrations`
: synergy data loaded but concentration columns are missing.

Impact:
- With concentrations: dose-based branch and concentration-specific profile mapping.
- Without concentrations: targets/profiles still run, combinations may be built from profile mapping without dose columns.

## 5. Step Requirements (Files and Columns)

Step-level requirements enforced by preflight/runtime:

| Step | Required Files | Required Columns in synergy data |
|---|---|---|
| `load_data` | `synergy_data_file` | none |
| `chembl_ids` | `drug_names_file` | none |
| `doses` | `synergy_data_file`, `drug_names_file` | `drug_name_A` and, if `double_drug_screen=true`, `drug_name_B`; concentration columns are checked and can trigger skip/warning behavior |
| `targets` | internal DB checked in preflight | none |
| `node_targets` | `node_dict_file`, `drug_names_file` | none |
| `profiles` | `node_dict_file`, `drug_names_file` | none |
| `combinations` | synergy data present in practice | `drug_name_A`, `drug_name_B`, `cell_line`, `synergy`; concentration columns are needed by current `CombinationProcessor` path |
| `panel` | `drug_names_file`, `node_dict_file` | none |
| `perturbations` | `tissue_cline_file` | uses prepared combinations output |
| `synergies` | `tissue_cline_file` | `cell_line` (plus synergy data from upstream output) |

## 6. Minimal Config Patterns

## 6.1 Profiles + Panel Only (no synergy file)

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

Run:

```bash
drexpa --config my_config.json --until panel
```

## 6.2 Full Dual-Drug Pipeline (with concentrations)

```json
{
  "global": {
    "output_dir": "results_full",
    "base_data_dir": "data",
    "verbose": true,
    "save": true
  },
  "paths": {
    "drug_names_file": "drug_names.txt",
    "synergy_data_file": "synergy_data.csv",
    "node_dict_file": "node_dict.csv",
    "tissue_cline_file": "tissue_cline.csv"
  },
  "options": {
    "double_drug_screen": true,
    "synergy_threshold": 0.1,
    "original_target_merge": "combine"
  }
}
```

## 6.3 Column Remapping Example

```json
{
  "global": {
    "output_dir": "results_remap",
    "base_data_dir": "my_data"
  },
  "paths": {
    "drug_names_file": "drugs.txt",
    "synergy_data_file": "screen.csv",
    "node_dict_file": "model_nodes.csv"
  },
  "columns": {
    "drug_name_A": "DrugA",
    "drug_name_B": "DrugB",
    "conc_A": "DoseA_nM",
    "conc_B": "DoseB_nM",
    "cell_line": "Cell",
    "synergy": "BlissScore"
  }
}
```

## 7. CLI and Config Interactions

Common commands:

```bash
# Use defaults from package
drexpa

# Use custom config JSON
drexpa --config my_config.json

# Override synergy path only (runtime)
drexpa --config my_config.json --synergy-data alt_synergy.csv

# Restrict execution
drexpa --config my_config.json --until profiles
drexpa --config my_config.json --steps profiles,panel
```

Validation tips:
- Use `--verbose` during setup to inspect step progression and warnings.
- If preflight fails, verify `base_data_dir` + each file in `paths` resolves to an existing file.
- If column errors occur, remap `columns` to exact CSV header text.

## 8. Common Misconfigurations

1. Missing `base_data_dir` alignment.
- Symptom: `FileNotFoundError` for files that exist elsewhere.
- Fix: ensure all relative path entries in `paths` are relative to `base_data_dir`.

2. Running `combinations` without concentrations.
- Symptom: errors about missing `conc_A`/`conc_B` in some workflows.
- Fix: either include concentration columns or run subset steps that avoid concentration-dependent combination path.

3. Assuming `db_file` override bypasses internal DB preflight check.
- Symptom: internal DB error even with custom DB path set.
- Fix: ensure packaged DB is present, or adjust code if custom-only DB behavior is required.

4. Header mismatch in synergy input.
- Symptom: missing required column validation errors.
- Fix: set `columns` remapping to your exact header names.

## 9. Source of Truth in Code

These modules define config behavior:
- `drexpa/config.py`
- `drexpa/main.py`
- `drexpa/cli.py`
- `drexpa/step_registry.py`

If behavior and docs differ, trust code and update docs accordingly.
