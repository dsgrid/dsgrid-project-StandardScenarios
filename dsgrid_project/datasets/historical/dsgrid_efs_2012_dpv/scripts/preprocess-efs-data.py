"""
This script does some data preprocessing cleanup on the efs dpv data to reconcile missing 
geographies (i.e., counties with no dpv data) and missing geography + sector combinations.

The dsgrid parquet files were generated using the convert_dsg.py script in dsgrid-legacy-efs-api.
This converted the efs distributedpv_sectoral.dsg into new dsgrid parquet format

    Command used:
    spark-submit --driver-memory 16G "/Users/mmooney/Documents/github/github.com/dsgrid/dsgrid-legacy-efs-api/bin/convert_dsg.py" "/Users/mmooney/Library/CloudStorage/OneDrive-NREL/Documents - dsgrid-load/File Archive/fy17 - OSP - Electrification Load Modeling/data/dsgrid_v0.2.0/data/distributedpv_sectoral.dsg" "/Users/mmooney/Library/CloudStorage/OneDrive-NREL/Documents - dsgrid-load/dsgrid-v2.0/Data Coordination/efs_datasets/dpv/distributedpv_sectoral" -s sector -n 2

"""
import numpy as np
import pandas as pd
from pathlib import Path

datasetdir = Path(__file__).absolute().parent.parent
projecdir = Path(__file__).absolute().parent.parent.parent.parent.parent
datapath = Path("/Users/mmooney/Library/CloudStorage/OneDrive-NREL/Documents - dsgrid-load/dsgrid-v2.0/Data Coordination/efs_datasets/dpv")
# datapath = Path("/projects/dsgrid/data-StandardScenarios2/dsgrid_efs_2012_dpv")

df_lkup = pd.read_parquet(datapath / "load_data_lookup.parquet copy")

# -----------------
# Geography
# -----------------
counties = pd.read_csv(datasetdir / "dimensions" / "geography.csv", dtype={"id": str})

# check the counties in the load_data_lookup that are not in the dimension records
if len({x for x in df_lkup.geography.unique() if x not in counties.id.unique()}) > 0:
    print("We have counties in lookup that are not in the dimension records")

# check counties in the dimension records missing from lookup
missing_county_data = {x for x in counties.id.unique() if x not in df_lkup.geography.unique()}
print(f"There are {missing_county_data} missing counties with no DPV data in lookup")

# dsgrid recommendation is to set these values to 0 in the load_data_lookup or to remove them from the dimension records. IF you remove them from the dimension records, then you need to set the dimension associations in the project.json saying what geographeis you expect. Because this is geography, that will be a long 

# -------------------------------
# Geography + Sector Combos
# -------------------------------
dfs = []
for county in counties.id.unique():
    for sector in df_lkup.sector.unique():
        if len(df_lkup.loc[(df_lkup.geography==county) & (df_lkup.sector==sector)]) == 0:
            dfs.append(pd.DataFrame({"geography": [county], "id": [np.nan], "sector": [sector]}))
dfs = pd.concat(dfs)
df_lkup = pd.concat([df_lkup, dfs])

# dpv data is also missing county 46102 (Oglala Lakota,SD), go ahead and add that in and update dimension records to match
dfs = []
for county in ["46102"]:
    for sector in df_lkup.sector.unique():
        if len(df_lkup.loc[(df_lkup.geography==county) & (df_lkup.sector==sector)]) == 0:
            print("yes")
            dfs.append(pd.DataFrame({"geography": [county], "id": [np.nan], "sector": [sector]}))
dfs = pd.concat(dfs)
df_lkup = pd.concat([df_lkup, dfs])

df_lkup.to_parquet(datapath / "load_data_lookup.parquet", index=False)