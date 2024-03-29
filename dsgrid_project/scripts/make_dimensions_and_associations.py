"""Make project dimensions and association for project"""

import pandas as pd
import os
from pathlib import Path
import numpy as np
from itertools import chain
from typing import Dict, List, Union

project_path = str(Path(__file__).parents[1])
os.chdir(project_path)


def make_project_dimension_associations():
    """For Standard Scenarios

    relationships are defined by data_source
        dimension_type : dependencies
        -----------------------------
        data_source : main discriminator
        sector : data_source
        subsector : data_source
        geography : common (to be created externally by sth else)
        metric : data_source
        model_year : common
        weather_year : common
        scenario : common
        time : not relevant

    """

    ### [0] Specify key dimensions and associations

    data_sources = ["comstock", "resstock", "tempo"]
    sectors_by_data_source = {
        "comstock": "com",
        "resstock": "res",
        "tempo": "trans",
    }
    subsectors_by_data_source = {
        "comstock": [
            "full_service_restaurant",
            "hospital",
            "large_office",
            "primary_school",
            "retail_standalone",
            "retail_stripmall",
            "small_office",
            "secondary_school",
            "warehouse",
            "large_hotel",
            "small_hotel",
            "outpatient",
            "quick_service_restaurant",
            "medium_office",
        ],
        "resstock": [
            "multifamily_2_to_4_units",
            "single_family_attached",
            "mobile_home",
            "single_family_detached",
            "multifamily_5_plus_units",
        ],
        "tempo": [
            "bev_compact",
            "bev_midsize",
            "bev_pickup",
            "bev_suv",
            "phev_compact",
            "phev_midsize",
            "phev_pickup",
            "phev_suv",
        ],
    }
    metrics_by_data_source = {
        "comstock": {
            "district_cooling_cooling": "electricity",
            "district_heating_heating": "natural_gas",
            "district_heating_water_systems": "natural_gas",
            "electricity_cooling": "electricity",
            "electricity_exterior_lighting": "electricity",
            "electricity_fans": "electricity",
            "electricity_heat_recovery": "electricity",
            "electricity_heat_rejection": "electricity",
            "electricity_heating": "electricity",
            "electricity_interior_equipment": "electricity",
            "electricity_interior_lighting": "electricity",
            "electricity_pumps": "electricity",
            "electricity_refrigeration": "electricity",
            "electricity_water_systems": "electricity",
            "natural_gas_heating": "natural_gas",
            "natural_gas_interior_equipment": "natural_gas",
            "natural_gas_water_systems": "natural_gas",
            "fuel_oil_heating": "fuel_oil",
            "fuel_oil_water_systems": "fuel_oil",
            "propane_heating": "propane",
            "propane_water_systems": "propane",
        },
        "resstock": {
            "electricity_bath_fan": "electricity",
            "electricity_ceiling_fan": "electricity",
            "electricity_clothes_dryer": "electricity",
            "electricity_clothes_washer": "electricity",
            "electricity_cooking_range": "electricity",
            "electricity_cooling": "electricity",
            "electricity_dishwasher": "electricity",
            "electricity_exterior_holiday_lighting": "electricity", # mapping req'd
            "electricity_exterior_lighting": "electricity",
            "electricity_extra_refrigerator": "electricity",
            "electricity_fans_cooling": "electricity",
            "electricity_fans_heating": "electricity",
            "electricity_freezer": "electricity",
            "electricity_garage_lighting": "electricity",
            "electricity_heating": "electricity",
            "electricity_heating_supplemental": "electricity", # mapping req'd
            "electricity_hot_tub_heater": "electricity",
            "electricity_hot_tub_pump": "electricity",
            "electricity_house_fan": "electricity",
            "electricity_interior_lighting": "electricity",
            "electricity_plug_loads": "electricity",
            "electricity_pool_heater": "electricity",
            "electricity_pool_pump": "electricity",
            "electricity_pumps_cooling": "electricity",
            "electricity_pumps_heating": "electricity",
            "electricity_range_fan": "electricity",
            "electricity_recirc_pump": "electricity",
            "electricity_refrigerator": "electricity",
            "electricity_water_systems": "electricity",
            "electricity_well_pump": "electricity",
            "fuel_oil_heating": "fuel_oil",
            "fuel_oil_water_systems": "fuel_oil",
            "natural_gas_clothes_dryer": "natural_gas",
            "natural_gas_cooking_range": "natural_gas",
            "natural_gas_fireplace": "natural_gas",
            "natural_gas_grill": "natural_gas",
            "natural_gas_heating": "natural_gas",
            "natural_gas_hot_tub_heater": "natural_gas",
            "natural_gas_lighting": "natural_gas",
            "natural_gas_pool_heater": "natural_gas",
            "natural_gas_water_systems": "natural_gas",
            "propane_clothes_dryer": "propane",
            "propane_cooking_range": "propane",
            "propane_heating": "propane",
            "propane_water_systems": "propane",
            "wood_heating": "wood",
        },
        "tempo": {
            "electricity_ev_l1l2": "electricity",
            "electricity_ev_dcfc": "electricity",
        },
    }

    model_years = list(np.arange(2010, 2051))
    weather_years = [2012]
    scenarios = ["reference", "efs_high_ldv", "ldv_sales_evs_2035"]

    ### [1] DIMENSION ASSOCIATIONS - convert to df and save
    create_df_and_save_association(sectors_by_data_source, ["data_source", "sector"])
    create_df_and_save_association(
        subsectors_by_data_source, ["data_source", "subsector"]
    )
    create_df_and_save_association(metrics_by_data_source, ["data_source", "metric"])

    ### [2] DIMENSIONS - convert to df and save
    create_df_and_save_dimension_list(data_sources, "sources", sort=True)
    create_df_and_save_dimension_dict(sectors_by_data_source, "sectors", sort=True)
    create_df_and_save_dimension_dict(subsectors_by_data_source, "subsectors", sort=True)
    create_df_and_save_enduse(metrics_by_data_source, "kWh", "enduses_kwh", sort=True)
    create_df_and_save_dimension_list(model_years, "model_years", sort=True)
    create_df_and_save_dimension_list(weather_years, "weather_years", sort=True)
    create_df_and_save_dimension_list(scenarios, "scenarios", sort=True)


def create_df_and_save_association(association_dict: dict, column_names: list):
    file = f"dimension_associations/{'__'.join(column_names)}.csv"
    dct = []
    for key, val in association_dict.items():
        if isinstance(val, list) or isinstance(val, dict):
            for v in val:
                dct.append((key, v))
        else:
            dct.append((key, val))
    pd.DataFrame(dct, columns=column_names).sort_values(by=column_names).to_csv(
        file, index=False
    )


def create_df_and_save_dimension_list(data: List, file_name: str, sort=False):
    """create and save df for a dimension.
    Input data is a dimension record list

    Args:
    -----
        data : [list, dict]
            list of dimension records
        file_name : str
            name of file to save
        sort : bool
            sort by "id"
    """

    file = f"dimensions/{file_name}.csv"
    df = pd.DataFrame(
        {
            "id": data,
            "name": [str(x).title().replace("_", " ") for x in data],
        }
    )
    if sort:
        df.sort_values(by=["id"]).to_csv(file, index=False)
    else:
        df.to_csv(file, index=False)


def create_df_and_save_dimension_dict(data: Dict, file_name: str, sort=False):
    """create and save df for a dimension.
    Input data is a dimension association where the values are the
    dimension records to be processed.

    Args:
    -----
        data : Dict
            dict of dimension associations, where dimension records are the dict values
        file_name : str
            name of file to save
        sort : bool
            sort by "id"
    """

    file = f"dimensions/{file_name}.csv"

    vals = set()
    for val in data.values():
        if isinstance(val, list):
            vals.update(set(val))
        elif isinstance(val, str) or isinstance(val, int):
            vals.add(val)
        else:
            raise TypeError(
                f"values of data dict have unsupported type={type(val)}. Valid types: [list, str, int]"
            )
    df = pd.Series(list(vals)).rename("id").to_frame()
    df["name"] = df["id"].astype(str).str.title().str.replace("_", " ")

    if sort:
        df.sort_values(by=["id"]).to_csv(file, index=False)
    else:
        df.to_csv(file, index=False)


def create_df_and_save_enduse(
    data: Dict, units: Union[Dict, str], file_name: str = "metrics", sort=False
):
    """create and save df for end uses.
    Input data is a dimension association where the values are the dimension
    records to be processed.

    Args:
    -----
        data : dict
            dict of dimension associations, where metrics are the dict values
        units : str or dict
            single unit in str or dict that maps units by fuel_id
        file_name : str
            name of file to save
        sort : bool
            sort by "id"
    """

    file = f"dimensions/{file_name}.csv"
    fuel_by_enduse = dict(
        chain(*map(dict.items, data.values()))
    )  # combine list of dicts

    df = pd.DataFrame(fuel_by_enduse.items(), columns=["id", "fuel_id"])
    df["name"] = df["id"].astype(str).str.title().str.replace("_", " ")

    if isinstance(units, str):
        df["unit"] = units
    elif isinstance(units, dict):
        df["unit"] = df["fuel_id"].map(units)
    else:
        raise TypeError(
            f"units has unsupported type={type(units)}. Valid types: [str, dict]"
        )
    if sort:
        df.sort_values(by=["id"]).to_csv(file, index=False)
    else:
        df.to_csv(file, index=False)


if __name__ == "__main__":

    make_project_dimension_associations()
    print(
        "* project dimensions and dimension_associations created for Standard Scenarios, "
        "excluding dimensions/counties.csv. *"
    )
