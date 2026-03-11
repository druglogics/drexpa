# TODO: DREXPA Roadmap & Maintenance Backlog

Planned improvements, known issues, and maintenance items for DREXPA.

- **P0 (Complete):** Shared step registry, preflight validation, version cleanup, structured logging.
- **P1 (Complete):** Deep config merge, explicit runtime modes, integration tests.
- **P2 (Planned):** Caching, dataset adapters, broader extensibility.
- **Maintenance:** Ongoing doc/code alignment, test coverage, and tech debt.

**Navigation:** [README](README.md) · [QUICKSTART](QUICKSTART.md) · [PROJECT_STRUCTURE](PROJECT_STRUCTURE.md)

---

## P0: Quick Wins ✅ Done

- ✅ Single step registry (`drexpa/step_registry.py`) for unified CLI/orchestration
- ✅ Preflight file & column validation (step-aware, catches errors early)
- ✅ Single-source versioning (metadata-based, not hardcoded duplicates)
- ✅ Structured logging + per-step timing summary
- ✅ Internal DB management (package-shipped, not user-provided)

**Tests:** `tests/test_step_registry.py`, `tests/test_preflight.py`, `tests/test_resources.py`

---

## P1: Reliability ✅ Done

- ✅ Config deep-merge with schema-aware behavior (replaces shallow `.update()`)
- ✅ Explicit runtime modes (`no_synergy`, `with_concentrations`, `without_concentrations`)
- ✅ Removed duplicate `get_synergies_config` definition
- ✅ Step-aware column validation (different requirements per run mode)

**Tests:** `tests/test_config.py::test_merge_config_*`, `tests/test_pipeline_modes.py`

Benefit: Nested config defaults preserved on custom overrides; branching logic transparent.

---

## P2: Scale & Extensibility (Next Phase)

### 2.1: Deterministic Lookup Caching

Fast-path repeated runs with same genes/targets/nodes.

**Scope:**
- Cache `TargetProcessor` DB queries (keyed by drug name × concentration).
- Cache `NodeTargetMapper` gene-to-node lookups (keyed by gene symbol).
- Optional cache backend (`sqlite`, `pickle`, in-memory).

**Impact:** High (typical re-runs 2–10× faster).  
**Feasibility:** Medium (requires cache invalidation strategy).  
**Acceptance:** Speed benchmark + cache hit rate logging.

---

### 2.2: Dataset Adapter Interface

Clean extension point for new screening formats without touching orchestrator.

**Scope:**
- Standardized dataset class: `def load(config) → synergy_df, tissue_map`.
- Registry pattern: `register_dataset_adapter("bashi", BashiAdapter)`.
- Built-in adapters for current formats (BASHI, VIS, JAaks, O'Neill).
- Metadata versioning (data version, update timestamp, schema version).

**Impact:** High (unlock new datasets, reduce maintenance burden).  
**Feasibility:** Low-Medium (design-sensitive; requires backward-compat).  
**Acceptance:** New dataset loads without modifying `main.py`.

---

### 2.3: Broader Test Coverage

Integration tests for step combinations, datasets, and edge cases.

**Scope:**
- Step combination matrix: all valid `--until` + `--steps` permutations on synthetic data.
- Branch behavior: `with_conc` vs `without_conc` vs `no_synergy` correctness.
- Edge case: empty results, single drug, missing optional columns.
- Regression suite: known bug fixes (e.g., duplicate config methods, old step lists).

**Impact:** High (catches broken pipelines early).  
**Feasibility:** High (mostly test code, no core changes).  
**Acceptance:** 90%+ coverage; CI runs on all PRs.

---

## Maintenance Backlog

### Documentation Alignment

- [ ] Keep CLI `--until` options in sync with `step_registry.py`.
- [ ] Update examples whenever config keys change.
- [ ] Add DB schema/version docs (for maintainers).
- [ ] Link internal module docs to README architecture diagram.

**Owner:** Any maintainer. **Trigger:** Version bump, new dataset support.

---

### Version Management

- [ ] Single source: `pyproject.toml` → auto-picked by `__version__` (done).
- [ ] Release checklist: update DB file → bump version → test → changelog → publish.
- [ ] DB metadata table: embed schema version, data release date for traceability.

**Owner:** Release manager. **Cadence:** Per-release.

---

### Legacy Code Assessment

**Status:** Refactored in P0/P1; marked as internal-only.

- [ ] Legacy pipeline class in `drexpa/features/drug.py` (953 lines, not wired in runtime).
  - **Action:** Deprecate or remove by v1.0. Update `CHANGELOG.md`.
- [ ] Root-level integration scripts (`test_bashi_pipeline.py`, `test_vis_pipeline.py`).
  - **Action:** Move to `examples/legacy/` or remove if covered by tests.

**Owner:** Architecture lead. **Timeline:** v0.2–v1.0.

---

### Known Issues & Workarounds

#### Issue #1: ChEMBL Network Dependency

ChEMBL resolution can timeout or is unavailable in offline environments.

**Workaround (current):** Provide `manual_chembl.csv`.  
**Future:** Cached ChEMBL snapshot (small DB, updated quarterly).  
**Priority:** Low (not mission-critical; workaround exists).

---

#### Issue #2: Column Name Rigidity

Config columns are customizable but preflight doesn't warn about typos until runtime.

**Fix idea:** Pre-check column config against actual data in preflight.  
**Impact:** Prevent silent column mismatches.  
**Priority:** Medium (rare but confusing).

---

#### Issue #3: Per-Step Reproducibility Logs

Current timing logs lack full parameter dump (e.g., IC50 threshold used, merge strategy).

**Fix idea:** Log full step config at execution (not just timing).  
**Impact:** Better debugging & reproducibility.  
**Priority:** Low (verbose mode mitigates).

---

## Release Checklist

Before publishing a new version:

- [ ] Run full test suite: `pytest tests/ --cov` (>90% coverage).
- [ ] Update `pyproject.toml` version.
- [ ] Update internal DB if applicable; test DB loading.
- [ ] Add `CHANGELOG.md` entry.
- [ ] Test install: `pip install -e .` then `drexpa --version`.
- [ ] Tag release: `git tag -a v0.2.0 -m "Release notes"`.
- [ ] Publish: `python -m build && twine upload dist/*`.
- [ ] Verify PyPI page updated.

**Owner:** Release manager. **Approvals:** Code review, architecture lead.

---

## Metrics & Observability

### Monitoring (Future)

- Pipeline success rate (by dataset & version).
- Average runtime per step (identify bottlenecks).
- ChEMBL resolution success rate (warn if API has issues).
- DB schema/data version tracking (audit trail).

**Implementation:** Optional telemetry module (opt-in, no PII).

---

## Timeline

| Phase | Target | Goals |
|-------|--------|-------|
| **v0.1.x** (Current) | Feb–Mar 2026 | P0 + P1 stabilization, internal DB shipped |
| **v0.2** | Apr–May 2026 | P2.1 caching, broader test matrix, legacy cleanup |
| **v0.3** | Jun–Jul 2026 | P2.2 dataset adapters, metadata versioning |
| **v1.0** | Sep 2026 | Stable API, production-ready, no deprecation warnings |

---

## Contributing

For contributors interested in P2 items or backlog tasks:

1. **Fork:** Clone the repo and create a feature branch.
2. **Discuss:** Open an issue for large changes; get architecture lead feedback.
3. **Implement:** Follow existing patterns (config structure, step definitions, testing).
4. **Test:** Add tests for new code; validate with `pytest --cov`.
5. **PR:** Reference issue, describe changes, ensure CI passes.

### Code Style

- **Format:** Black + isort (run: `black drexpa tests` + `isort drexpa tests`)
- **Lint:** Flake8 (run: `flake8 drexpa tests`)
- **Type hints:** Optional for now; encouraged for new code.
- **Tests:** Pytest; unit > integration > end-to-end.

---

## References

- [README.md](README.md) – Full user guide
- [QUICKSTART.md](QUICKSTART.md) – Minimal runnable examples
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) – Architecture & module layout
- [P0 Implementation Plan](README.md#quick-wins-) – Detailed P0 decisions
- [P1 Implementation Plan](README.md#reliability-) – Config & modes specifics
