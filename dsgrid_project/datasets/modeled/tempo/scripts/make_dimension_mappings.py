import itertools
import pandas as pd
import os
from pathlib import Path

from dsgrid.common import LOCAL_REGISTRY
from dsgrid.dimension.base_models import DimensionType
from dsgrid.registry.registry_manager import RegistryManager
from dsgrid.config.project_config import ProjectConfig
from dsgrid.config.dimension_mappings_config import DimensionMappingsConfig

from dsgrid.utils.files import dump_data

project_path = Path(__file__).parents[4]
tempo_path = Path(__file__).parents[1]

# join county to county
project_county = pd.read_csv(project_path / "dimensions" / "counties.csv", dtype={"id": str})
project_county["to_id"] = project_county["id"]
tempo_county =  pd.read_csv(tempo_path / "dimensions" / "counties.csv", dtype={"id": str})
tempo_county["from_id"] = tempo_county["id"]
county = pd.merge(tempo_county[["id", "from_id"]], project_county[["id", "to_id"]], on="id", how="left", indicator="_merge")
county[["from_id", "to_id"]].to_csv(tempo_path / "dimension_mappings" /"county_to_county.csv", index=False)

# join model year to model year
project_model_year = pd.read_csv(project_path / "dimensions" / "model_years.csv", dtype={"id": str})
project_model_year["to_id"] = project_model_year["id"]
tempo_model_year = pd.read_csv(tempo_path / "dimensions" / "year.csv", dtype={"id": str})
tempo_model_year["from_id"] = tempo_model_year["id"]
join = pd.merge(tempo_model_year[["id", "from_id"]], project_model_year[["id", "to_id"]], on="id", how="left", indicator="_merge")
join[["from_id", "to_id"]].to_csv(tempo_path / "dimension_mappings" /"model_year_to_model_year.csv", index=False)

# join subsector to subsector
project_subsector = pd.read_csv(project_path / "dimensions" / "subsectors.csv", dtype={"id": str})
project_subsector["to_id"] = project_subsector["id"]
tempo_subsector =  pd.read_csv(tempo_path / "dimensions" / "bin.csv", dtype={"id": str})
tempo_subsector["from_id"] = tempo_subsector["id"]
tempo_subsector.loc[(tempo_subsector.id.str.contains("Compact")) & (tempo_subsector.id.str.contains("BEV")), "id"] = "bev_compact"
tempo_subsector.loc[(tempo_subsector.id.str.contains("Midsize")) & (tempo_subsector.id.str.contains("BEV")), "id"] = "bev_midsize"
tempo_subsector.loc[(tempo_subsector.id.str.contains("SUV")) & (tempo_subsector.id.str.contains("BEV")), "id"] = "bev_suv"
tempo_subsector.loc[(tempo_subsector.id.str.contains("Pickup")) & (tempo_subsector.id.str.contains("BEV")), "id"] = "bev_pickup"
# TODO: issue -- I can't find PHEV in the bin.csv ***************
tempo_subsector.loc[(tempo_subsector.id.str.contains("Compact")) & (tempo_subsector.id.str.contains("PHEV")), "id"] = "phev_compact"
tempo_subsector.loc[(tempo_subsector.id.str.contains("Midsize")) & (tempo_subsector.id.str.contains("PHEV")), "id"] = "phev_midsize"
tempo_subsector.loc[(tempo_subsector.id.str.contains("SUV")) & (tempo_subsector.id.str.contains("PHEV")), "id"] = "phev_suv"
tempo_subsector.loc[(tempo_subsector.id.str.contains("Pickup")) & (tempo_subsector.id.str.contains("PHEV")), "id"] = "phev_pickup"
join = pd.merge(tempo_subsector[["id", "from_id"]], project_subsector[["id", "to_id"]], on="id", how="left", indicator="_merge")
join[["from_id", "to_id"]].to_csv(tempo_path / "dimension_mappings" /"subsector_to_subsector.csv", index=False)
