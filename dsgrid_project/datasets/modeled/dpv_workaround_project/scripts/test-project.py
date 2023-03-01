"""
Script to test the DPV workaround project

--------------
CLI COMMANDS:
--------------
# register the project
dsgrid registry --offline projects register "dsgrid_project/datasets/modeled/dpv_workaround_project/project.json5" -l "test"

# register the datasets
dsgrid registry --offline datasets register "dsgrid-project-StandardScenarios/dsgrid_project/datasets/historical/dsgrid_efs_2012_dpv/dataset.json5" "/projects/dsgrid/data-StandardScenarios/dsgrid_efs_2012_dpv" -l "test"
dsgrid registry --offline datasets register "dsgrid-project-StandardScenarios/dsgrid_project/datasets/historical/dsgrid_efs_2012_dpv_capacity/dataset.json5" "/dpv/output/capacities_2012" -l "test"
dsgrid registry --offline datasets register "dsgrid-project-StandardScenarios/dsgrid_project/datasets/modeled/dgen/dataset.json5" "/dpv/output/capacities_SS22" -l "test"

# submit the datasets to project
dsgrid registry --offline projects submit-dataset -d "dsgrid_efs_2012_dpv" -p "dsgrid_conus_2022_dpv_calcs" -m "dsgrid-project-StandardScenarios/dsgrid_project/datasets/historical/dsgrid_efs_2012_dpv/dimension_mappings.json5" -l "test"
dsgrid registry --offline projects submit-dataset -d "dsgrid_efs_2012_dpv_capacity" -p "dsgrid_conus_2022_dpv_calcs" -m "dsgrid-project-StandardScenarios/dsgrid_project/datasets/historical/dsgrid_efs_2012_dpv_capacity/dimension_mappings.json5" -l "test"
dsgrid registry --offline projects submit-dataset -d "dgen_stdscen_2022_dpv_capacity" -p "dsgrid_conus_2022_dpv_calcs" -m "dsgrid-project-StandardScenarios/dsgrid_project/datasets/modeled/dgen/dimension_mappings.json5" -l "test"

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

# locate project information
project_dir = Path(__file__).parent.parent.parent.parent.parent
assert project_dir.name == "dsgrid_project", project_dir
project_json5 = project_dir / "datasets" / "modeled" / "dpv_workaround_project" / "project.json5"
assert project_json5.exists(), project_json5
data_dir = Path("/projects/dsgrid/data-StandardScenarios/")
dpv_dir = (project_dir / ".." / ".." / "dpv").absolute()
assert dpv_dir.exists(), f"dpv repo not found at {dpv_dir}"

# locate dataset information
dataset_paths = [
    ("dsgrid_efs_2012_dpv",
     project_dir / "datasets" / "historical" / "dsgrid_efs_2012_dpv",
     data_dir / "dsgrid_efs_2012_dpv"),
    ("dsgrid_efs_2012_dpv_capacity", 
     project_dir / "datasets" / "historical" / "dsgrid_efs_2012_dpv_capacity",
     dpv_dir / "output" / "capacities_2012"),
    ("dgen_stdscen_2022_dpv_capacity", 
     project_dir / "datasets" / "modeled" / "dgen",
     dpv_dir / "output" / "capacities_SS22"),
]


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

# register datasets and and submit them to project
for dataset_id, dataset_dir, dataset_data_path in dataset_paths:
    print(f"Registering {dataset_id} ------------------------------------------")
    manager.dataset_manager.register(
        config_file=dataset_dir / "dataset.json5",
        dataset_path=dataset_data_path,
        submitter=submitter,
        log_message="test",
        force=True
    )
    print(f"Submitting {dataset_id} -------------------------------------------")
    dimension_mappings_path = dataset_dir / "dimension_mappings.json5"
    manager.submit_dataset(
        project_id="dsgrid_conus_2022_dpv_calcs",
        dataset_id=dataset_id,
        submitter=submitter,
        log_message="test",
        dimension_mapping_file=dimension_mappings_path if dimension_mappings_path.exists() else None,
        dimension_mapping_references_file=None
    )
