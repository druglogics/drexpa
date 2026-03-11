# DREXPA Examples

Minimal, runnable examples demonstrating two real-world use cases with DREXPA.

**Note:** See [../QUICKSTART.md](../QUICKSTART.md) for detailed walkthrough and expected output.

---

## Example 1: With Concentration Data

**File:** [`run_drexpa_bashi.py`](run_drexpa_bashi.py)

Full DREXPA pipeline processing experimental drug screening data with concentration information.

**Runtime Mode:** `with_concentrations`

**Datasets:** Bashi dataset (dual-drug screening with IC50 measurements)

**Steps executed:**
1. Resolve drug names → ChEMBL IDs
2. Extract & process drug doses from synergy data
3. Retrieve drug targets at specific concentrations
4. Map targets to logical model nodes
5. Build concentration-specific drug profiles
6. Create drug panel (DrugLogics format)
7. Prepare drug combinations
8. Generate perturbation files per tissue/cell line
9. Analyze synergy metrics

**Run:**
```bash
python examples/run_drexpa_bashi.py
```

**Output directory:** `output_bashi/`

---

## Example 2: Without Concentration Data

**File:** [`run_drexpa_vis.py`](run_drexpa_vis.py)

Simplified DREXPA pipeline for drug screening without concentration information (single-dose screening).

**Runtime Mode:** `without_concentrations`

**Datasets:** Vis dataset (single-dose drug combinations)

**Steps executed:**
1. Resolve drug names → ChEMBL IDs
2. Retrieve drug targets at default IC50 threshold (10 µM)
3. Map targets to logical model nodes
4. Build drug profiles
5. Create drug panel (DrugLogics format)
6. Prepare drug combinations
7. Generate perturbation files per tissue/cell line
8. Analyze synergy metrics

**Run:**
```bash
python examples/run_drexpa_vis.py
```

**Output directory:** `output_vis/`

---

## Configuration Files & Templates

- `config_template.json` – Full configuration template with all available options
- `sample_drug_names.txt` – Example drug names (one per line)
- `sample_node_dict.csv` – Example node dictionary

---

## Key Differences

| Feature | Bashi Example | Vis Example |
|---------|---------------|-------------|
| **Data** | Experimental concentrations | Single-dose (no concentrations) |
| **Pipeline mode** | `with_concentrations` | `without_concentrations` |
| **Dose processing** | ✅ Yes | ❌ No |
| **Concentration-specific targets** | ✅ Yes | ❌ Uses default IC50 |
| **Processing time** | Slower | Faster |
| **Use case** | Full experimental analysis | Initial drug panel screening |

---

## Quick Start

1. **Prepare input files:** Place drug names, node dictionary, and synergy data in expected locations
2. **Run example:**
   ```bash
   python examples/run_drexpa_bashi.py
   # or
   python examples/run_drexpa_vis.py
   ```
3. **Check outputs:** Results saved to `output_bashi/` or `output_vis/`

---

## Using Config Files

Both scripts use Python dicts, but you can also call via CLI with JSON config:

```bash
drexpa --config examples/config_template.json --verbose
```

Edit `config_template.json` to customize paths, columns, and options.

---

## Output Files

Both examples produce:

- `drug_ChEMBL_IDs.csv` – Drug name → ChEMBL ID mapping
- `drug_ChEMBL_targets.csv` – Drug → Targets from database
- `drug_node_targets.csv` – Targets → Logical model nodes
- `drug_profiles.csv` – Drug profiles with Pipeline IDs
- `drug_panel_df.csv` – Drug panel (DrugLogics format)
- `drugpanel` – Binary formatted drug panel
- Perturbation files (per tissue/cell line in subdirectories)
- Synergy outputs (tissue-specific analysis summaries)

**See:** [../README.md § Output Files](../README.md#output-files)