"""
# Prepare data for EIA 861 Annual Energy Use by State by Sector

...

**Description:**
EIA 861 Utility Customer Sales by State by Sector by Year for 2012-2020


**Relevent infromation about the EIA861 data**

- `Operational_Data_<year>`: “Disposition” columns (i.e. where the electricity is going)
    - “Total Disposition” : total electricity at bus bar, should more or less equal to “Total Sources” column
    - “Retail Sales” : total sales to consumers, should more or less equal to “TOTAL Sales” column in Sales_Ult_Cust_<year>
    - “Sales for Resale” : sale of electricity to other utilities (this is accounted for in “Retail Sales” of the utilities in the receiving end, so I think you can ignore this column)
    - “Furnished without Charge” : electricity consumed in things like municipal lighting and services
    - “Consumed by respondent without Charge” : electricity consumed by the utilities
    - “Total Energy Losses” : transmission losses (I don’t believe 861 accounts for generation losses at all)
    *I am not sure how Elaine wants to categorize the electricity consumed without charge.
    
- `Sales_Ult_Cust_<year>`: Sectoral “Sales” columns (sales to ultimate customers in each sector).
  - Make sure to follow the footnote (i.e. ignore Part C-Delivery) to get the correct aggregation of electric demands. Some utilities use other utilities’ lines to deliver energy to their customers and get charged for the delivery service.
  - What about texas part D?
- `Sales_Ult_Cust_<year>`: sales made to Customer Sited, this lists sales to identified customers, which are already accounted for as adjustments in Sales_Ult_Cust_<year>, so this can be ignored.

**Processing Notes:**
- [PUDL](https://catalystcoop-pudl.readthedocs.io/en/latest/index.html) was used to download the raw EIA861 data. Note that cleaned PUDL outputs for EIA861 data tables were not published by PUDL at the time this dataset was created, so the PUDL tool could only be used to download the raw EIA data. This notebook processes the raw EIA861 data excel tables.
- EIA861 data tables are then stored (here)[https://nrel.sharepoint.com/:u:/r/sites/dsgrid-load/Shared%20Documents/dsgrid-v2.0/Data%20Coordination/eia861/eia861_2010_2018.zip?csf=1&web=1&e=8Ru8do] in `dsgrid-load` Teams channel in the `dsgrid-v2.0` channel.

"""

import pandas as pd
from pathlib import Path

from pyspark.sql import Row, SparkSession
from pyspark.sql.dataframe import DataFrame


root_dir = Path('/Users/mmooney/OneDrive - NREL/Documents - dsgrid-load/dsgrid-v2.0/Data Coordination/eia861')
raw_data_dir = root_dir / "raw" / "eia861_2010_2018"
processed_data_dir = root_dir / "processed" / "eia_861_annual_energy_use_state_sector"

def sales_utl_cust_read_xlsx(year):
    """
    Function to read EIA861 Sales_Utl_Cust_{year}.xlsx and put into Dataframe we can work with
    """
    
    try:
        xlsx = raw_data_dir / f"f861{year}" / f"Sales_Ult_Cust_{year}.xlsx"
        df = pd.read_excel(xlsx, sheet_name="States", header=[0,1, 2], skiprows=[-1])
    except:
        # some files are .xls not .xlsx
        xlsx = raw_data_dir / f"f861{year}" / f"Sales_Ult_Cust_{year}.xls"
        df = pd.read_excel(xlsx, sheet_name="States", header=[0,1, 2], skiprows=[-1])
        
    # deal with multi-index columns
    df.columns = df.columns.get_level_values(0) + '_' +  df.columns.get_level_values(1) + '_' +  df.columns.get_level_values(2)
    fix_cols = {}
    for c in df.columns:
        keep_col = True
        if "Utility Char" in c:
            if "Observed" in c:
                col = "data_type_observed_or_imputed"
            else:
                col = c.split("_")[-1].lower().replace(" ", "_")
        elif "TOTAL" in c:
            keep_col = False
        elif "Sales" in c:
            col = c.lower().replace("_sales_megawatthours", "")
            import numpy as np
            df.loc[df[c] == ".", c] = 0 # TODO: should this be Nan?
            df[c] = df[c].astype(float)
        else:
            keep_col = False
        if keep_col:
            fix_cols[c] = col
    df  = df.rename(columns=fix_cols)
    
    # subset for cols we care about
    df = df[[*fix_cols.values()]].copy()
    
    # remove footnote
    df = df[:-1]
    
    # melt df into long format
    df = df.melt(id_vars=["data_year", "state", "part"], value_vars=["residential", "commercial", "industrial", "transportation"], var_name="sector_fullname", value_name="sales")
    
    # replace sector with sector abbreviation
    df_sector_abbr = pd.DataFrame({"sector_fullname": ["residential", "commercial", "transportation", "industrial"],
                                "sector": ["res", "com", "ind", "trans"]})
    df = pd.merge(df, df_sector_abbr, on="sector_fullname", how="left")
    df = df.drop(columns="sector_fullname")
    
    return df


def process_eia_861_ult_cust_sales():
    dfs = []
    years = range(2010,2021)
    for year in years:

        df = sales_utl_cust_read_xlsx(year)
        
        # filter for Sales and Customers only (not Revenue from Retail Power Market)
        df = df.loc[df.part!="C"]
        df = df.loc[(df.state!="TX")&(df.part!="D")] # Texas is weird, need to filter further
        
        dfs.append(df)
        
    # concat all historic years
    df = pd.concat(dfs)   

    # get state-year-sector sums
    df = df[["data_year", "state", "sector", "sales"]].groupby(["data_year", "state", "sector"]).sum().reset_index()


    # more column cleanup 
    final_col_names = {
        "data_year": "timestamp", # TODO is this year or timestamp?
    }
    df = df.rename(columns=final_col_names)

    return df


eia861_sales = process_eia_861_ult_cust_sales()

# TODO: do something with EIA 861 Furnished without charge

# move data to spark
spark = SparkSession.builder.appName("convert_dsg").getOrCreate()
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
spark_df = spark.createDataFrame(eia861_sales)

# write to dsgrid parquet format
parquet_filename = processed_data_dir / "load_data.parquet"
spark_df.write.parquet(str(parquet_filename), mode="overwrite")