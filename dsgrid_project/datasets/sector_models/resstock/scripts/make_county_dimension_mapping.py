import os
import pandas as pd
from pathlib import Path

path = str(Path(__file__).parents[1])
os.chdir(path)

resstock = pd.read_csv("dimensions/conus_2022-resstock_geography_county_fips.csv", dtype={"id": str})
project = pd.read_csv("../../../dimensions/counties.csv", dtype={"id": str})

resstock["match_id"] = resstock["id"].str[1:3] + resstock["id"].str[4:-1]
resstock.columns = ["from_id", "name", "state", "id"]

joindf = pd.merge(project[["id"]], resstock, on=["id"], how="left")
joindf = joindf[["from_id", "id"]].copy()
joindf.columns = ["from_id", "to_id"]

joindf.to_csv("dimension_mappings/county_to_county.csv", index=False)