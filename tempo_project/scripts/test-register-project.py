"""
Script to test registering the project

--------------
CLI COMMANDS:
--------------

# configure dsgrid (feel free to use a different registry and/or database name)
dsgrid config create -u http://localhost:8529 -N test-tempo

# register the project
dsgrid registry projects register "dsgrid-project-StandardScenarios/tempo_project/project.json5" --log-message "test"
"""

import os
from pathlib import Path

from dsgrid.common import REMOTE_REGISTRY
from dsgrid.dsgrid_rc import DsgridRuntimeConfig
from dsgrid.registry.registry_database import DatabaseConnection
from dsgrid.registry.registry_manager import RegistryManager

submitter = os.getlogin()

project_dir = Path(__file__).absolute().parent.parent
project_json5 = project_dir / "project.json5"

config = DsgridRuntimeConfig.load()
conn = DatabaseConnection.from_url(
    config.database_url,
    database=config.database_name,
    username=config.database_user,
    password=config.database_password,
)

registry_manager = RegistryManager.load(
    conn, 
    REMOTE_REGISTRY, 
    offline_mode=config.offline)
manager = registry_manager.project_manager

# register project
manager.register(config_file=project_json5, 
                 submitter=submitter, 
                 log_message="test")
