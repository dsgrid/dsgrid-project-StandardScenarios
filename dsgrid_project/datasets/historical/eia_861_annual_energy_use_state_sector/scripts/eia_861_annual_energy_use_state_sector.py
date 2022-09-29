"""
# Prepare data for EIA 861 Annual Energy Use by State by Sector

...

**Description:**
EIA 861 Utility Customer Sales (MWh) by State by Sector by Year for 2010-2020


**Relevent infromation about the EIA861 data**

- `Operational_Data_<year>`: “Disposition” columns (i.e. where the electricity is going)
    - “Total Disposition” : total electricity at bus bar, should more or less equal to “Total Sources” column
    - “Retail Sales” : total sales to consumers, should more or less equal to “TOTAL Sales” column in Sales_Ult_Cust_<year>
    - “Sales for Resale” : sale of electricity to other utilities (this is accounted for in “Retail Sales” of the utilities in the receiving end, so I think you can ignore this column)
    - “Furnished without Charge” : electricity consumed in things like municipal lighting and services
    - “Consumed by respondent without Charge” : electricity consumed by the utilities
    - “Total Energy Losses” : transmission losses (I don’t believe 861 accounts for generation losses at all)
    
- `Sales_Ult_Cust_<year>`: Sectoral “Sales” columns (sales to ultimate customers in each sector).
  - Make sure to follow the footnote (i.e. ignore Part C-Delivery) to get the correct aggregation of electric demands. Some utilities use other utilities’ lines to deliver energy to their customers and get charged for the delivery service.

- `Sales_Ult_Cust_CS_<year>`: sales made to Customer Sited, this lists sales to identified customers, which are already accounted for as adjustments in Sales_Ult_Cust_<year>, so this can be ignored.

**Processing Notes:**
- [PUDL](https://catalystcoop-pudl.readthedocs.io/en/latest/index.html) was used to download the raw EIA861 data. Note that cleaned PUDL outputs for EIA861 data tables were not published by PUDL at the time this dataset was created, so the PUDL tool could only be used to download the raw EIA data. This notebook processes the raw EIA861 data excel tables.
    - EIA861 data tables are then stored (here)[https://nrel.sharepoint.com/:u:/r/sites/dsgrid-load/Shared%20Documents/dsgrid-v2.0/Data%20Coordination/eia861/eia861_2010_2018.zip?csf=1&web=1&e=8Ru8do] in `dsgrid-load` Teams channel in the `dsgrid-v2.0` channel.
- For each year, use the `Sales_Ult_Cust_<year>` dataset to get the total sales (MWh) to customers by sector (com, res, ind, trans)
- The data is by utility & state, however, for this first pass, we will sum total sector by state (for each year). In the second pass, we will separate out by utility-state using Ventyx Geometries
- Then pull in the Furnished Without Charge sales data since this is reported differently. Since this is mostly big commercial sales, we will treat this as additional commercial sales. You can find this in the `Operational_Data_{year}` table. Add this to the other dataset (described in bullet above), treated as commercial.


"""

from logging import raiseExceptions
import pandas as pd
from pathlib import Path

from pyspark.sql import Row, SparkSession
from pyspark.sql.dataframe import DataFrame


root_dir = Path('/Users/mmooney/OneDrive - NREL/Documents - dsgrid-load/dsgrid-v2.0/Data Coordination/eia861')
raw_data_dir = root_dir / "raw" / "eia861_2010_2018"
processed_data_dir = root_dir / "processed" / "eia_861_annual_energy_use_state_sector"

def sales_utl_cust_read_xlsx(year):
    """
    Function to read EIA861 Sales_Utl_Cust_{year}.xlsx and put into Dataframe we can work with.
    """
    
    possible_files = (
        raw_data_dir / f"f861{year}" / f"Sales_Ult_Cust_{year}.xlsx",
        raw_data_dir / f"f861{year}" / f"Sales_Ult_Cust_{year}.xls"
        )
    for file in possible_files:
        if file.exists():
            df = pd.read_excel(file, sheet_name="States", header=[0,1, 2])
            
    # remove footnote
    df = df[:-1]
        
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
            df.loc[df[c] == ".", c] = 0 # TODO: should this be Nan?
            df[c] = df[c].astype(float)
        else:
            keep_col = False
        if keep_col:
            fix_cols[c] = col
    df  = df.rename(columns=fix_cols)
    
    # subset for cols we care about
    df = df[[*fix_cols.values()]].copy()
    
    # melt df into long format
    df = df.melt(id_vars=["data_year", "state", "part"], value_vars=["residential", "commercial", "industrial", "transportation"], var_name="sector_fullname", value_name="sales")
    
    # replace sector with sector abbreviation
    df_sector_abbr = pd.DataFrame({"sector_fullname": ["residential", "commercial", "transportation", "industrial"],
                                "sector": ["res", "com", "trans", "ind"]})
    df = pd.merge(df, df_sector_abbr, on="sector_fullname", how="left")
    df = df.drop(columns="sector_fullname")
    
    return df


def operational_data_read_xlsx(year):
    """
    Function to read EIA861 Operational_Data_{year}.xlsx and put into Dataframe we can work with.
    """
    
    possible_files = (raw_data_dir / f"f861{year}" / f"Operational_Data_{year}.xlsx",
                      raw_data_dir / f"f861{year}" / f"Operational_Data_{year}.xls",
                      raw_data_dir / f"f861{year}" / f"operational_data_{year}.xlsx")
    for file in possible_files:
        if file.exists():
            df = pd.read_excel(file, sheet_name="States", header=[0,1, 2])
    
    # deal with multi-index columns
    df.columns = df.columns.get_level_values(0) + '_' +  df.columns.get_level_values(1) + '_' +  df.columns.get_level_values(2)
    fix_cols = {}
    for c in df.columns:
        keep_col = True
        if "Utility Char" in c:
            if "Data Year" in c:
                col = c.split("_")[-1].lower().replace(" ", "_")
            elif "State" in c:
                col = c.split("_")[-1].lower().replace(" ", "_")
            else:
                keep_col = False
        elif "Furnished" in c:
            col = "sales"
            df.loc[df[c] == ".", c] = 0 # TODO: should this be Nan?
            df[c] = df[c].astype(float)
        else:
            keep_col = False
        if keep_col:
            fix_cols[c] = col
    df  = df.rename(columns=fix_cols)    
    
    # subset for cols we care about
    df = df[[*fix_cols.values()]].copy()
    
    # treat furnished without charge as commercial sector
    df["sector"] = "com"
    
    # Note: 2010 operational dataset has a CN state with 0 values for furnished without charge
    df = df.loc[df.state!="CN"].copy()
    
    return df


def process_eia_861():
    dfs = []
    years = range(2010,2021)
    for year in years:

        ult_cust = sales_utl_cust_read_xlsx(year)
        furnished_without_charge = operational_data_read_xlsx(year)
        
        # concat sales from ultimate customer and furnished without charge (as commercial)
        df = pd.concat([ult_cust, furnished_without_charge])
        
        # filter for Sales and Customers only (not Revenue from Retail Power Market)
        df = df.loc[df.part!="C"]
        
        # rename existing columns to fit dsgrid dimension names
        df["time_year"] = year
        df["geography"] = df["state"]
        df["electricity_sales"] = df["sales"]
        
        # add weather_year, model_year (required by dsgrid for non-trivial dimensions)
        df["weather_year"] = str(year) # Note: dsgrid requires id from dimension records to be str
        df["model_year"] = str(year)
        
        dfs.append(df)
        
    # concat all historic years
    df = pd.concat(dfs)   

    # get state-year-sector sums
    groupby_cols = ["weather_year", "model_year", "time_year", "geography", "sector"]
    df = df[groupby_cols + ["electricity_sales"]].groupby(groupby_cols).sum().reset_index()

    return df


if __name__ == "__main__":
    
    # process eia 861 data in pandas
    eia861 = process_eia_861()

    # move data to spark
    spark = SparkSession.builder.appName("convert_dsg").getOrCreate()
    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
    spark_df = spark.createDataFrame(eia861)

    # write to dsgrid parquet format
    parquet_filename = processed_data_dir / "load_data.parquet"
    spark_df.write.parquet(str(parquet_filename), mode="overwrite")