"""
Script to test dataset submission to project and to use for debugging

--------------
CLI COMMANDS:
--------------
# register the project
dsgrid registry --offline projects register "/Users/mmooney/Documents/github/github.com/dsgrid/dsgrid-project-StandardScenarios/dsgrid_project/project.json5" -l "test"

# register the dataset
dsgrid registry --offline datasets register "dsgrid-project-StandardScenarios/dsgrid_project/datasets/historical/eia_861_annual_energy_use_state_sector/dataset.json5" "/projects/dsgrid/data-StandardScenarios/eia_861_annual_energy_use_state_sector" -l "test"

# submit dataset to project
dsgrid registry --offline projects submit-dataset -d "eia_861_annual_energy_use_state_sector" -p "dsgrid_conus_2022" -m "dsgrid-project-StandardScenarios/dsgrid_project/datasets/historical/eia_861_annual_energy_use_state_sector/dimension_mappings.json5" -l "test"
"""

import shutil
from pathlib import Path
from dsgrid.common import REMOTE_REGISTRY, LOCAL_REGISTRY
from dsgrid.registry.registry_manager import RegistryManager


# start with fresh offline mode registry
local_test_registry = Path.home() / ".dsgrid-registry-test"
if local_test_registry.exists():
    shutil.rmtree(local_test_registry)


submitter = "mmooney"

project_dir = Path().absolute() / "dsgrid_project"
dataset_dir = project_dir / "datasets" / "historical" / "eia_861_annual_energy_use_state_sector"
project_json5 = project_dir / "project.json5"
dataset_json5 = dataset_dir / "dataset.json5"
dimension_mapping_file = dataset_dir / "dimension_mappings.json5"
dataset_path = Path("/Users/mmooney/OneDrive - NREL/Documents - dsgrid-load/dsgrid-v2.0/Data Coordination/eia861/processed/eia_861_annual_energy_use_state_sector") # located on dsgrid-load teams files

# remove tmp supplemental dir
tmp_supplemental_dir = project_dir / "__tmp_supplemental__"
if tmp_supplemental_dir.exists():
    shutil.rmtree(tmp_supplemental_dir)


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

# register dataset
manager.dataset_manager.register(config_file=dataset_json5, 
                                 dataset_path=dataset_path, 
                                 submitter=submitter, 
                                 log_message="test", 
                                 force=True)

# submit dataset to project
manager.submit_dataset(
    project_id="dsgrid_conus_2022",
    dataset_id="eia_861_annual_energy_use_state_sector",
    submitter=submitter,
    log_message="test",
    dimension_mapping_file=dimension_mapping_file,
    dimension_mapping_references_file=None,
)