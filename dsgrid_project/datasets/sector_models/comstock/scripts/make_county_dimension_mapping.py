import os
import pandas as pd
from pathlib import Path

path = str(Path(__file__).parents[1])
os.chdir(path)

comstock = pd.read_csv("dimensions/conus_2022-comstock_geography_county_fips.csv", dtype={"id": str})
project = pd.read_csv("../../../dimensions/counties.csv", dtype={"id": str})

comstock["match_id"] = comstock["id"].str[1:3] + comstock["id"].str[4:-1]
comstock.columns = ["from_id", "name", "state", "id"]

joindf = pd.merge(project[["id"]], comstock, on=["id"], how="left")
joindf = joindf[["from_id", "id"]].copy()
joindf.columns = ["from_id", "to_id"]

joindf.to_csv("dimension_mappings/county_to_county.csv", index=False)