"""Make time zone mapping for county.csv using resstock's options_lookup
created on 06/19/2024

County files used:
- dsgrid-project-StandardScenarios/dsgrid_project/dimensions/counties.csv
- dsgrid-project-StandardScenarios/tempo_project/dimensions/counties.csv
- dsgrid-project-StandardScenarios/dsgrid_project/datasets/modeled/resstock/dimensions/conus_2022-resstock_geography_county_fips.csv
- dsgrid-project-StandardScenarios/dsgrid_project/datasets/modeled/comstock/dimensions/conus_2022-comstock_geography_county_fips.csv
- dsgrid-project-DECARB/project/dimensions/counties.csv
"""

import pandas as pd
from pathlib import Path
import argparse


def main(county_file: str, lookup_file: str, pre2015_counties=False):
    # Process lookup file
    lookup_file = Path(lookup_file)
    assert (
        lookup_file.name == "options_lookup.tsv"
    ), "lookup_file needs to have name: 'options_lookup.tsv'"
    lkup = pd.read_csv(lookup_file, sep="\t")
    lkup = (
        lkup.loc[lkup["Parameter Name"] == "County"]
        .dropna(how="all", axis=1)
        .reset_index(drop=True)
    )
    lkup = lkup[["Option Name", "Unnamed: 6"]]
    lkup["Option Name"] = (
        lkup["Option Name"]
        .str.lower()
        .str.removesuffix("county")
        .str.strip()
        .str.removesuffix("city and borough")
        .str.strip()
        .str.removesuffix("city")
        .str.strip()
        .str.removesuffix("parish")
        .str.strip()
        .str.removesuffix("borough")
        .str.strip()
        .str.removesuffix("census area")
        .str.strip()
        .str.removesuffix("municipality")
        .str.strip()
        .str.replace("'", "")
        .str.replace(".", "")
    )
    lkup["time_zone"] = (
        lkup["Unnamed: 6"]
        .str.removeprefix("site_time_zone_utc_offset=")
        .map(
            {
                "-5": "EasternPrevailing",
                "-6": "CentralPrevailing",
                "-7": "MountainPrevailing",
                "-8": "PacificPrevailing",
                "-9": "AlaskaPrevailing",
                "-10": "HawaiiAleutianStandard",
            }
        )
    )

    # Add AZ exceptions
    cond = lkup["Option Name"].str.contains("az,")
    cond2 = cond & (~lkup["Option Name"].str.contains("navajo"))
    lkup.loc[cond2, "time_zone"] = "USArizona"
    print("Adjusted time zones for AZ in lookup:")
    print(lkup.loc[cond])

    # Check map for duplicated rows (Option Name formatting can cause duplicates)
    dup_by_name = lkup.loc[
        lkup["Option Name"].isin(
            lkup.loc[lkup["Option Name"].duplicated(), "Option Name"]
        )
    ]
    dup_by_row = lkup.loc[
        lkup["Option Name"].isin(lkup.loc[lkup.duplicated(), "Option Name"])
    ]
    assert (
        len(dup_by_name.compare(dup_by_row)) == 0
    ), "Duplicated Option Name found that do not share the same time zone, cannot drop rows."
    lkup = lkup.drop_duplicates()

    # Map to county file
    county_file = Path(county_file)
    df = pd.read_csv(county_file)
    n_df = len(df)

    has_old_time_zone = False
    if "time_zone" in df.columns:
        df = df.rename(columns={"time_zone": "old_time_zone"})
        has_old_time_zone = True
    df["map_key"] = (
        (df["state"] + ", " + df["name"])
        .str.lower()
        .str.removesuffix("county")
        .str.strip()
        .str.removesuffix("city and borough")
        .str.strip()
        .str.removesuffix("city")
        .str.strip()
        .str.removesuffix("parish")
        .str.strip()
        .str.removesuffix("borough")
        .str.strip()
        .str.removesuffix("census area")
        .str.strip()
        .str.removesuffix("municipality")
        .str.strip()
        .str.replace("'", "")
        .str.replace(".", "")
    )

    ## Fix discrepancies and old county names
    county_map = {
        "la, lasalle": "la, la salle",
        "ak, wade hampton": "ak, kusilvak",
        "sd, shannon": "sd, oglala lakota",
    }
    for key, val in county_map.items():
        cond = df["map_key"] == key
        if len(df.loc[cond]) == 1:
            df.loc[cond, "map_key"] = val

    df = df.join(lkup.set_index("Option Name")["time_zone"], on="map_key", how="left")

    # Check mapping
    not_mapped = df.loc[df["time_zone"].isna()]
    # assert len(not_mapped) == 0, f"counties not mapped:\n{not_mapped}"
    avail_mapping = lkup.loc[~lkup["Option Name"].isin(df["map_key"])]
    if len(not_mapped) > 0:
        print(f"Counties not mapped:\n{not_mapped}")
        print(f"Available mapping:\n{avail_mapping}")
        breakpoint()
    if len(avail_mapping) > 0:
        print("\nWarning: the following counties from options_lookup are unmapped:")
        print(avail_mapping)

    # Check old and new time_zone
    if has_old_time_zone:
        cond = df["time_zone"] != df["old_time_zone"]
        cols = [x for x in df.columns if x != "map_key"]
        print("\nDifference between old and new time_zone:")
        print(df.loc[cond, cols])

    # Clean up and save
    if df["id"].dtype == float or df["id"].dtype == int:
        df["id"] = df["id"].astype(int).astype(str).str.zfill(5)
    df = df.drop(columns=["old_time_zone", "map_key"])
    # assert len(df) == n_df, "county df does not have the same number of rows as before."
    if len(df) != n_df:
        print("county df does not have the same number of rows as before.")
        breakpoint()

    df.to_csv(county_file, index=False)
    print(f"\nUpdated time_zone column in county file: {county_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "county_file",
        action="store",
        default=None,
        nargs="?",
        help="Path to dsgrid geography record: county.csv",
    )
    parser.add_argument(
        "lookup_file",
        action="store",
        default=None,
        nargs="?",
        help="Path to ResStock options_lookup tsv file. i.e., "
        "https://github.com/NREL/resstock/blob/develop/resources/options_lookup.tsv",
    )

    args = parser.parse_args()
    main(args.county_file, args.lookup_file)
