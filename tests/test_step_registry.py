"""
Tests for shared pipeline step registry and dependency resolution.
"""
import pytest

from drexpa.step_registry import ordered_step_names, resolve_steps, until_choices


def test_ordered_step_names_matches_until_choices():
    assert ordered_step_names() == until_choices()


def test_resolve_steps_none_runs_all_in_order():
    assert resolve_steps(None) == ordered_step_names()


def test_resolve_steps_until_profiles_includes_prefix():
    steps = resolve_steps("until_profiles")
    assert steps[-1] == "profiles"
    assert "load_data" in steps
    assert "node_targets" in steps


def test_resolve_steps_explicit_adds_dependencies():
    steps = resolve_steps(["panel"])
    expected_dependencies = ["load_data", "chembl_ids", "doses", "targets", "node_targets", "profiles", "panel"]
    assert steps == expected_dependencies


def test_resolve_steps_invalid_raises():
    with pytest.raises(ValueError):
        resolve_steps(["does_not_exist"])


@pytest.mark.parametrize(
    "requested,last_expected",
    [
        (["profiles"], "profiles"),
        (["panel"], "panel"),
        (["perturbations"], "perturbations"),
        (["synergies"], "synergies"),
        (["profiles", "panel"], "panel"),
    ],
)
def test_step_matrix_dependency_resolution(requested, last_expected):
    steps = resolve_steps(requested)
    assert steps[-1] == last_expected
    assert "chembl_ids" in steps
    assert "targets" in steps
