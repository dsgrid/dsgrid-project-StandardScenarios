"""
Script to test the DPV workaround project

--------------
CLI COMMANDS:
--------------
# register the project
dsgrid registry --offline projects register "dsgrid_project/datasets/modeled/dpv_workaround_project/project.json5" -l "test"

# register the datasets

# submit the datasets to project

# create the generation shape (capacity factors) derived dataset

# apply the generation shapes to the dGen projected capacities to create 
# the projected dataset

"""

import os
import shutil
from pathlib import Path
from dsgrid.common import REMOTE_REGISTRY, LOCAL_REGISTRY
from dsgrid.registry.registry_manager import RegistryManager

submitter = "ehale"

local_test_registry = os.environ.get("DSGRID_REGISTRY_PATH", None)
if local_test_registry.endswith("test"):
    local_test_registry = Path(local_test_registry)
else:
    local_test_registry = Path.home() / ".dsgrid-registry-test"

print(f"Using registry location: {local_test_registry}")
if local_test_registry.exists():
    shutil.rmtree(local_test_registry)

project_dir = Path(__file__).parent.parent.parent.parent.parent
assert project_dir.name == "dsgrid_project", project_dir
project_json5 = project_dir / "datasets" / "modeled" / "dpv_workaround_project" / "project.json5"

registry_manager = RegistryManager.load(
        local_test_registry, REMOTE_REGISTRY, offline_mode=True, no_prompts=True
    )

manager = registry_manager.project_manager

# register project
manager.register(config_file=project_json5, 
                 submitter=submitter, 
                 log_message="test", 
                 force=True
                 )