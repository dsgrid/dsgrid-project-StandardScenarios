"""Make project dimension mappings for project to supplement"""

import pandas as pd
import os
from pathlib import Path

from dsgrid.utils.files import dump_data
from dsgrid.common import LOCAL_REGISTRY

project_path = str(Path(__file__).parents[1])
os.chdir(project_path)
project_config_file = "/project.json5"
local_registry = LOCAL_REGISTRY


def make_maps_for_state_county_divisions_and_regions():
    """One-off function to make the initial mappings between county, state, division, region. Not intended for reuse."""
    counties = pd.read_csv("dimensions/counties.csv", dtype={"id": str})
    states = pd.read_csv("dimensions/supplemental/states.csv", dtype={"id": str})
    divisions = pd.read_csv("dimensions/supplemental/census_divisions.csv", dtype={"id": str})
    regions = pd.read_csv("dimensions/supplemental/census_regions.csv", dtype={"id": str})

    DF = counties.set_index("state").join(states.set_index("id")[["census_division", "census_region"]], how="left").reset_index().sort_values("id").rename(columns={"index": "state"})
    
    supplemental_dimensions = [
        "CensusRegion", "CensusDivision", "State"
    ]
    mappings = []
    for x in supplemental_dimensions:

        if x == "CensusRegion":
            df = DF[["id", "census_region"]].copy().rename(columns={"id": "from_id", "census_region": "to_id"})
        if x == "CensusDivision":
            df = DF[["id", "census_division"]].copy().rename(columns={"id": "from_id", "census_division": "to_id"})
        elif x == "State":
            df = DF[["id", "state"]].copy().rename(columns={"id": "from_id", "state": "to_id"})

        filename = f"dimension_mappings/base_to_supplemental/lookup_county_to_{x.lower()}.csv"
        df.to_csv(filename, index=False)

        mappings.append(
            {'description': f"Maps Comstock US Counties 2020 to {x}",
            'file': filename,
            'from_dimension': {
                'dimension_id': "",
                'type': "geography", 
                'version': "1.0.0"
                },
            'to_dimension': {
                'dimension_id': "",
                'type': "geography",
                'version': "1.0.0"
                }
            })

    return mappings

if __name__ == '__main__': 

    maps = []

    maps.extend(make_maps_for_state_county_divisions_and_regions())

    # create a dimension_mappings.json5
    config = {"mappings": maps}
    dump_data(config, "dimension_mappings.json5")


    