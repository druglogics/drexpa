"""
DREXPA: DRug EXperimental PAnel

A pipeline for processing experimental drug screening datasets into drug panels
and perturbation files compatible with the DrugLogics pipeline (drabme/Bless modules)
and GITSBE for in silico validation.

The pipeline transforms drug names into ChEMBL IDs, retrieves drug targets,
maps them to logical model nodes, and generates drug panels and perturbation
files for downstream analysis.

Key Features:
- Automated ChEMBL ID resolution from drug names
- Drug target retrieval and processing
- Biological network node mapping
- Drug profile generation for logical models
- Drug panel creation for DrugLogics pipeline
- Perturbation file generation for specific conditions
- Flexible configuration and pipeline execution

Main Output:
- Drug panels with Pipeline Drug IDs (PD_IDs)
- Perturbation files for experimental conditions
- Node target profiles for logical modeling
"""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("drexpa")
except PackageNotFoundError:
    __version__ = "0.1.0"
__author__ = "Viviam Solangeli Bermúdez Paiva"

# Lazy imports to avoid importing pandas at package import time
def __getattr__(name):
    if name == 'run_pipeline':
        from .main import run_pipeline
        return run_pipeline
    elif name == 'DrexpaPipeline':
        from .main import DrexpaPipeline
        return DrexpaPipeline
    elif name == 'Config':
        from .config import Config
        return Config
    elif name == 'get_default_config':
        from .config import get_default_config
        return get_default_config
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "__version__",
    "run_pipeline",
    "DrexpaPipeline",
    "Config",
    "get_default_config",
]