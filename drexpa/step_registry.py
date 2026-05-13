"""
Shared pipeline step registry for DREXPA.

This module centralizes step ordering and dependency resolution so CLI and
pipeline orchestration stay in sync.
"""

from collections import OrderedDict


STEP_REGISTRY = OrderedDict([
    ("load_data", {"method": "_load_synergy_data", "description": "Load synergy data"}),
    ("chembl_ids", {"method": "_get_chembl_ids", "description": "Get ChEMBL IDs"}),
    ("doses", {"method": "_process_doses", "description": "Process drug doses"}),
    ("targets", {"method": "_get_targets", "description": "Get drug targets"}),
    ("node_targets", {"method": "_map_node_targets", "description": "Map targets to nodes"}),
    ("profiles", {"method": "_build_profiles", "description": "Build drug profiles"}),
    ("combinations", {"method": "_prepare_combinations", "description": "Prepare combinations"}),
    ("panel", {"method": "_create_panel", "description": "Create drug panel"}),
    ("perturbations", {"method": "_create_perturbations", "description": "Create perturbation panels"}),
    ("synergies", {"method": "_process_synergies", "description": "Process observed synergies"}),
])


STEP_DEPENDENCIES = {
    "load_data": [],
    "chembl_ids": ["load_data"],
    "doses": ["load_data", "chembl_ids"],
    "targets": ["doses"],
    "node_targets": ["targets"],
    "profiles": ["node_targets"],
    "combinations": ["profiles", "targets"],
    "panel": ["profiles"],
    "perturbations": ["profiles"],
    "synergies": ["profiles"],
}


def ordered_step_names():
    """Return step names in execution order."""
    return list(STEP_REGISTRY.keys())


def until_choices():
    """Return valid --until step names."""
    return ordered_step_names()


def resolve_steps(steps_to_run):
    """
    Resolve which steps to run.

    Args:
        steps_to_run (str | list | None):
            - None: run all steps
            - "until_<step>": run until target step (inclusive)
            - list[str]: explicit steps, expanded with dependencies
    """
    all_steps = ordered_step_names()

    if steps_to_run is None:
        return all_steps

    if isinstance(steps_to_run, str):
        if not steps_to_run.startswith("until_"):
            raise ValueError(f"Invalid steps specification: {steps_to_run}")
        target_step = steps_to_run[6:]
        if target_step not in STEP_REGISTRY:
            raise ValueError(f"Unknown step: {target_step}")
        target_index = all_steps.index(target_step)
        return all_steps[: target_index + 1]

    if isinstance(steps_to_run, list):
        requested_steps = []
        for step in steps_to_run:
            if step not in STEP_REGISTRY:
                raise ValueError(f"Unknown step: {step}")
            requested_steps.append(step)

        resolved = set()

        def add_dependencies(step_name):
            if step_name in resolved:
                return
            resolved.add(step_name)
            for dep in STEP_DEPENDENCIES.get(step_name, []):
                add_dependencies(dep)

        for step_name in requested_steps:
            add_dependencies(step_name)

        return [step for step in all_steps if step in resolved]

    raise ValueError(f"Invalid steps specification: {steps_to_run}")
