"""
Script to test dataset submission to project and to use for debugging
--------------
CLI COMMANDS:
--------------
# register the project
dsgrid registry --offline projects register "/Users/mmooney/Documents/github/github.com/dsgrid/dsgrid-project-StandardScenarios/dsgrid_project/project.toml" -l "test"
# register the dataset
dsgrid registry --offline datasets register "/Users/mmooney/Documents/github/github.com/dsgrid/dsgrid-project-StandardScenarios/dsgrid_project/datasets/historical/dsgrid_efs_2012_distributed_generation/dataset.toml" "/Users/mmooney/OneDrive - NREL/Documents - dsgrid-load/dsgrid-v2.0/Data Coordination/efs_datasets/loss_model" -l "test"
# submit dataset to project
dsgrid registry --offline projects submit-dataset -d "dsgrid_efs_2012_distributed_generation" -p "dsgrid_conus_2022" -m "/Users/mmooney/Documents/github/github.com/dsgrid/dsgrid-project-StandardScenarios/dsgrid_project/datasets/historical/dsgrid_efs_2012_distributed_generation/dimension_mappings.toml" -l "test"
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
dataset_dir = project_dir / "datasets" / "historical" / "dsgrid_efs_2012_distributed_generation"
project_toml = project_dir / "project.toml"
dataset_toml = dataset_dir / "dataset.toml"
dimension_mapping_file = dataset_dir / "dimension_mappings.toml"
dataset_path = Path("/Users/mmooney/OneDrive - NREL/Documents - dsgrid-load/dsgrid-v2.0/Data Coordination/efs_datasets/chp_dg") # located on dsgrid-load teams files

# remove tmp supplemental dir
tmp_supplemental_dir = project_dir / "__tmp_supplemental__"
if tmp_supplemental_dir.exists():
    shutil.rmtree(tmp_supplemental_dir)


registry_manager = RegistryManager.load(
            local_test_registry, REMOTE_REGISTRY, offline_mode=True, no_prompts=True
        )

manager = registry_manager.project_manager

# register project
manager.register(config_file=project_toml, 
                 submitter=submitter, 
                 log_message="test", 
                 force=True
                 )

# register dataset
manager.dataset_manager.register(config_file=dataset_toml, 
                                 dataset_path=dataset_path, 
                                 submitter=submitter, 
                                 log_message="test", 
                                 force=True)

# submit dataset to project
manager.submit_dataset(
    project_id="dsgrid_conus_2022",
    dataset_id="dsgrid_efs_2012_distributed_generation",
    submitter=submitter,
    log_message="test",
    dimension_mapping_file=dimension_mapping_file,
    dimension_mapping_references_file=None,
)