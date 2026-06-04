# PROJECT_STRUCTURE: DREXPA Architecture & Repository Layout

Overview of DREXPA's module organization, runtime entry points, testing infrastructure, and data flow.

---

## Repository Layout

```
drexpa/                         # Main Python package
├── __init__.py                 # Lazy imports; exports __version__, run_pipeline(), etc.
├── __main__.py                 # Entry point for python -m drexpa (calls cli.main)
├── cli.py                       # Command-line interface; argparse + logging setup
├── main.py                      # Pipeline orchestrator; step registry wiring, preflight, execution
├── config.py                    # Config defaults, Config class, deep-merge utilities
├── step_registry.py             # Shared step catalog; dependency resolution
│
├── resources/                   # Package-shipped assets
│   ├── __init__.py
│   ├── database.py              # DB path resolver; get_internal_database_path()
│   └── DrugTargetInteractionDB.db  # Internal drug-target interaction database (project-managed)
│
├── features/                    # Feature modules (core processing steps)
│   ├── __init__.py
│   ├── chembl_ids.py            # ChEMBLIDResolver; drug name → ChEMBL ID queries
│   ├── doses.py                 # DoseProcessor; extract concentrations from synergy data
│   ├── targets.py               # TargetProcessor; query internal DB for drug targets
│   ├── node_targets.py          # NodeTargetMapper; map targets to logical model nodes
│   ├── profiles.py              # ProfileBuilder; generate unique drug profiles + Pipeline IDs
│   ├── combinations.py          # CombinationProcessor; prepare drug combinations
│   ├── panel.py                 # PanelMaker; create DrugLogics-compatible drug panel
│   ├── perturbations.py         # PerturbationPanelBuilder; generate per-condition perturbation files
│   ├── synergies.py             # SynergyProcessor; analyze synergy scores
│   ├── target_checker.py        # SQLite query helper (low-level DB interface)
│   ├── utils.py                 # Utilities (currently empty; reserved for shared helpers)
│   └── drug.py                  # LEGACY: Monolithic old pipeline class (not wired; internal use only)
│
└── __pycache__/                 # Cached bytecode (ignored in git)

tests/                           # Test suite
├── test_basic.py                # Package import, version, config loading
├── test_config.py               # Config validation, defaults, deep-merge behavior
├── test_cli.py                  # CLI argument parsing, version flag, help text
├── test_step_registry.py        # Step ordering, dependency resolution, until/steps logic
├── test_preflight.py            # File/column validation, error messages
├── test_pipeline_modes.py       # Runtime mode classification (with/without concentrations)
├── test_resources.py            # Internal DB path resolution, resource availability
└── __pycache__/                 # Cached bytecode

data/                            # Data directory (user-provided inputs & outputs)
├── input/                       # User input files
│   ├── CFP_nodes.csv            # Example node dictionary
│   └── bashi/, jaaks/, oneil/, vis/  # Example synergy datasets
│
└── output/                       # Pipeline outputs (created by run)
    ├── bashi/, bashi2/, bashi3/  # Per-dataset output folders
    └── *.csv / drugpanel files

examples/                        # User examples & templates
├── config_template.json         # Full config template with all options
├── example_cli_usage.py         # CLI invocation patterns
├── example_bashi_with_doses.py  # Full pipeline with concentration data
├── example_vis_without_doses.py # Pipeline without concentration data
├── sample_drug_names.txt        # Example drug names
└── README.md                    # Examples documentation

pre-processing notebooks/        # Jupyter notebooks for exploratory data prep
├── dataprocessing_bashi.ipynb
├── dataprocessing_jaaks.ipynb
└── dataprocessing_vis.ipynb

.git/                            # Version control (ignored here)
.gitignore                       # Excludes *.pyc, venv/, __pycache__, etc.

pyproject.toml                   # Package metadata, version, dependencies, entry points
MANIFEST.in                      # Specifies which non-code files to include in source dist
pytest.ini                       # Pytest configuration (test discovery, testpaths)
README.md                        # Main user & contributor documentation
QUICKSTART.md                    # Minimal runnable examples
PROJECT_STRUCTURE.md             # This file
TODO.md                          # Roadmap & maintenance backlog
LICENSE                          # MIT License
```

---

## Entry Points

### CLI (Command Line Interface)

```bash
drexpa [--config CONFIG] [--until STEP] [--steps STEPS] [--verbose] ...
```

**Flow:**
1. User runs `drexpa --config my_config.json`
2. OS launches entry point defined in `pyproject.toml`: `drexpa.cli:main`
3. `cli.main()` parses arguments, loads config (default + JSON override via deep-merge)
4. Calls `run_pipeline(config_dict, synergy_data_file, steps_to_run)`
5. `main.run_pipeline()` → `DrexpaPipeline(config, synergy_file).run_pipeline(steps)`

**Key files:**
- `drexpa/cli.py` – Argument parsing, config loading, logging setup
- `pyproject.toml` – Entrypoint definition: `drexpa = "drexpa.cli:main"`

### Python API

```python
from drexpa import run_pipeline

config = {...}
run_pipeline(config_dict=config, synergy_data_file="...", steps_to_run=["profiles"])
```

**Flow:**
1. Import triggers lazy-load in `__init__.py`
2. `__init__.py.__getattr__("run_pipeline")` returns `main.run_pipeline`
3. User calls `run_pipeline(config_dict, synergy_data_file, steps_to_run)`
4. Same orchestration as CLI

**Key files:**
- `drexpa/__init__.py` – Lazy exports; `__version__`, `run_pipeline()`, `Config`, etc.
- `drexpa/main.py` – Core orchestration logic

### Module Entry Point

```bash
python -m drexpa --help
```

**Flow:**
1. Python loader finds `drexpa/__main__.py`
2. `__main__.py` imports and calls `cli.main()`
3. Same as CLI flow

**Key file:**
- `drexpa/__main__.py` – One-liner: `from .cli import main; if __name__ == '__main__': main()`

---

## Step Execution Flow (Runtime)

```
Config Load (CLI / Python API)
    ↓
Config Merge (defaults + custom JSON)
    ↓
DrexpaPipeline.__init__(config, synergy_data_file)
    ├→ Resolve synergy_data_file path (if provided)
    ├→ Initialize step_durations, runtime_mode, etc.
    └→ Store config as instance variables
    ↓
run_pipeline(steps_to_run=None)
    ├→ _resolve_steps(steps_to_run) → resolve via step_registry
    ├→ Skip load_data + dependents if no synergy file
    ├→ _preflight_validate(steps)
    │   ├→ _validate_required_files(steps)
    │   │   └→ Check drug_names, node_dict, internal DB, synergy file (if needed)
    │   ├→ _validate_required_columns(steps)
    │   │   └→ Check synergy data columns match config (conc_A, drug_name_A, etc.)
    │   └→ _set_runtime_mode(steps)
    │       └→ Classify: no_synergy | with_concentrations | without_concentrations
    ├→ For each step in steps:
    │   ├→ Log step start (structured logging)
    │   ├→ Call step method (e.g., _get_chembl_ids(), _build_profiles())
    │   ├→ Record duration
    │   └→ Log step end
    └→ _log_timing_summary()
        └→ Print total time + per-step breakdown
```

---

## Configuration Flow

```
get_default_config() (in config.py)
    ↓ Returns dict with all default paths, columns, options
    ↓
merge_config(defaults, custom_json) (in config.py)
    ├→ Deep-merge: nested dicts recursively merged
    ├→ Scalar values override defaults
    └→ Inputs not mutated (deepcopy used)
    ↓
Config(config_dict) (class in config.py)
    ├→ Stores merged config internally
    ├→ Provides typed accessors: get_chembl_config(), get_targets_config(), etc.
    └→ Each accessor resolves paths relative to base_data_dir
        └→ Special case: db_file → get_internal_database_path() if config.db_file is None
    ↓
DrexpaPipeline(config)
    └→ Stores config; calls config.get_*_config() per step
```

---

## Step Definitions (step_registry.py)

```python
STEP_REGISTRY = OrderedDict([
    ("load_data", {"method": "_load_synergy_data", "description": "Load synergy data"}),
    ("chembl_ids", {"method": "_get_chembl_ids", "description": "Get ChEMBL IDs"}),
    ("doses", {"method": "_process_doses", "description": "Process drug doses"}),
    # ... (10 steps total)
])

STEP_DEPENDENCIES = {
    "load_data": [],
    "chembl_ids": ["load_data"],
    "doses": ["load_data", "chembl_ids"],
    # ... (auto-resolved by resolve_steps())
}
```

**Functions:**
- `ordered_step_names()` – Return list of all steps in order
- `until_choices()` – Same as above (alias for CLI)
- `resolve_steps(steps_to_run)` – Parse user input → expand dependencies → return ordered subset

---

## Feature Modules (drexpa/features/)

Each module implements a pipeline step. Typical pattern:

```python
class SomeProcessor:
    def __init__(self, **config):
        self.output_dir = config.get('directory_output', 'output')
        self.verbose = config.get('verbose', False)
        # ...
    
    def process_data(self, input_data):
        # Core logic
        return output_data
    
    # Wrapper method called by orchestrator
    def get_output(self):
        # Setup, call, save
        return result
```

**Modules:**
- `chembl_ids.py` – ChEMBLIDResolver (queries ChEMBL API or manual CSV)
- `doses.py` – DoseProcessor (extracts IC50 from synergy data)
- `targets.py` – TargetProcessor (queries internal DB)
- `node_targets.py` – NodeTargetMapper (maps genes to model nodes)
- `profiles.py` – ProfileBuilder (generates Pipeline IDs)
- `combinations.py` – CombinationProcessor (pairs selected drugs)
- `panel.py` – PanelMaker (DrugLogics format output)
- `perturbations.py` – PerturbationPanelBuilder (per-condition files)
- `synergies.py` – SynergyProcessor (synergy summary stats)
- `target_checker.py` – SQLite helper (low-level DB queries; used by targets.py)

---

## Internal Database Management

**Location:** `drexpa/resources/DrugTargetInteractionDB.db`

**Access:**
```python
from drexpa.resources.database import get_internal_database_path

db_path = get_internal_database_path()  # Returns absolute path
```

**Why internal?**
- Users don't provide it; maintainer updates it.
- Shipped with package → reproducible results.
- Preflight validates presence; clear error if missing.

**Update Workflow (Maintainer):**
1. Replace `drexpa/resources/DrugTargetInteractionDB.db`
2. Update `pyproject.toml` version
3. Add changelog entry
4. Test: `drexpa --config test.json` should find & use new DB
5. Publish via PyPI

---

## Testing Architecture

### Test Organization

| File | Purpose | Scope |
|------|---------|-------|
| `test_basic.py` | Package health checks | Import, version, lazy loading |
| `test_config.py` | Config system | Defaults, validation, deep-merge |
| `test_cli.py` | CLI parsing & help | Arguments, version output, invalid options |
| `test_step_registry.py` | Step dependency logic | Resolve until/steps, ordering |
| `test_preflight.py` | Input validation | File/column checks, error messages |
| `test_pipeline_modes.py` | Runtime mode classification | Branching behavior by data |
| `test_resources.py` | Resource availability | DB path resolution |

### Test Strategy

- **Unit tests** (most): Mock external data, test individual functions.
- **Integration tests** (few): Temp directories with real CSV data, full pipeline paths.
- **End-to-end** (external): Manual steps on real datasets (not in CI due to ChEMBL API dependency).

### Running Tests

```bash
# Run all tests
pytest tests/ -q

# With coverage
pytest tests/ --cov=drexpa --cov-report=html

# Specific test file
pytest tests/test_preflight.py -v

# Match test name pattern
pytest -k "test_merge" -v
```

**Config:** `pytest.ini` sets `testpaths = tests` so `pytest` searches only `tests/` directory.

---

## Dependency Graph

```
User Input (config.json + drug_names.txt + synergy_data.csv + node_dict.csv)
    ↓
cli.py (argument parsing)
    ↓
main.py (orchestrator)
    │
    ├→ step_registry.py (step definitions + dependencies)
    ├→ config.py (config loading + merging)
    │   └→ resources/database.py (internal DB path)
    │
    └→ For each step:
        └→ features/<step>.py
            ├→ Uses config.<get_*_config>() for parameters
            ├→ Reads/writes data (df, CSV, files)
            ├→ May call target_checker.py (DB queries)
            └→ Outputs to output_dir

Output Files (drug_panel.csv, perturbation files, etc.)
```

---

## Legacy & Non-Primary Code

### `drexpa/features/drug.py` (953 lines)

**Status:** Internal / not wired in active pipeline.

- Monolithic old pipeline class with step methods.
- Kept for historical reference & potential future compatibility.
- **Action (v1.0):** Remove or move to `examples/legacy/`.
- **Why kept now:** Low maintenance cost; may have user scripts depending on it.

### Root-level integration scripts

- `test_bashi_pipeline.py`, `test_vis_pipeline.py` – Historical smoke tests.
- **Action (v1.0):** Move to `examples/legacy/` or consolidate into `tests/`.

### Old pipeline examples

- `examples/example_bashi_with_doses.py`, `examples/example_vis_without_doses.py`
- **Status:** Still valid; updated for current config/API in P0/P1.
- **Action:** Keep; add deprecation notices if major API changes.

---

## Version Management

**Single source of truth:** `pyproject.toml`

**Reading version at runtime:**
```python
# drexpa/__init__.py
from importlib.metadata import version
__version__ = version("drexpa")  # Reads from pyproject.toml
```

**Why this approach?**
- Single file to update per release.
- Avoids hardcoded duplicate version strings.
- `pip install` automatically sets metadata.

---

## Development Workflow

1. **Branch:** `git checkout -b feature/new-thing`
2. **Code:** Add files in `drexpa/` or `tests/`
3. **Format:** `black drexpa tests` + `isort drexpa tests`
4. **Lint:** `flake8 drexpa tests`
5. **Test:** `pytest tests/ --cov` (ensure >90% coverage)
6. **PR:** Push, create PR, await CI + review
7. **Merge:** Squash or rebase merge to `main`
8. **Release:** Tag, bump version, publish to PyPI

**CI (GitHub Actions / similar):**
- On PR/push: Run `pytest`, `flake8`, coverage checks
- Fail if tests don't pass or coverage drops

---

## Quick Reference: How To...

### Add a New Step

1. Create `drexpa/features/my_step.py` with `MyStepProcessor` class.
2. Add to `step_registry.py`: `("my_step", {"method": "_my_step", "description": "..."})`
3. Add dependencies if needed.
4. Implement `_my_step()` method in `DrexpaPipeline` calling the processor.
5. Add config getter in `Config.get_my_step_config()`.
6. Add tests in `tests/test_my_step.py`.

### Update Internal Database

1. Replace `drexpa/resources/DrugTargetInteractionDB.db`
2. Bump version in `pyproject.toml`
3. Add changelog entry
4. Test locally: `drexpa --config test_config.json`
5. Commit & tag: `git tag -a v0.2.0`
6. Publish: `python -m build && twine upload dist/*`

### Change Config Structure

1. Update defaults in `config.py:get_default_config()`
2. Update `Config` class accessors as needed
3. Update `tests/test_config.py` to cover new structure
4. Update `README.md` § Configuration Reference
5. Add migration notes to `TODO.md` or `CHANGELOG.md`

---

## Related Documentation

- [README.md](README.md) – User guide, CLI, API, troubleshooting
- [QUICKSTART.md](QUICKSTART.md) – Two runnable examples
- [TODO.md](TODO.md) – Roadmap, P2 improvements, maintenance items
