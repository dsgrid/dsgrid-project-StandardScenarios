# TEMPO County-level Light-duty Passenger Electric Vehicle Charging Profiles v2022

This dsgrid project has been used to publish the hourly data documented in:

> Yip, Arthur, Christopher Hoehne, Paige Jadun, Catherine Ledna, Elaine Hale, and Matteo Muratori. 2023. “Highly Resolved Projections of Passenger Electric Vehicle Charging Loads for the Contiguous United States.” Technical Report. Golden, CO (United States): National Renewable Energy Laboratory. https://www.nrel.gov/docs/fy23osti/83916.pdf.

via the [Open Energy Data Initiative (OEDI)](https://data.openei.org/home).

The data are hourly annual for 2024-2050 based on 2012 actual meteorological year (AMY) weather; are available for three scenarios of light-duty passenger electric vehicle adoption, 3,108 counties in the contiguous United States (CONUS), 720 household and vehicle types, and two charging types (L1&L2 and DCFC); and were produced by running the [TEMPO](https://www.nrel.gov/transportation/tempo-model.html) model at the county-level. The three adoption scenarios are:

- *AEO Reference Case*, which is aligned with the [U.S. EIA Annual Energy Outlook 2018](https://www.eia.gov/outlooks/archive/aeo18/)
- *EFS High Electrification*, which is aligned with the High Electrification scenario of the [Electrification Futures Study](https://www.nrel.gov/docs/fy18osti/71500.pdf)
- *All EV Sales by 2035*, which assumes that average passenger light-duty EV sales reach 50\% in 2030 and 100\% in 2035

The charging shapes are derived from two key assumptions of which data users should be aware:

1. *Ubiquitous charger access:* Drivers of vehicles are assumed to have access to a charger whenever a trip is not in progress.
2. *Immediate charging:* Immediately after trip completion, vehicles are plugged in and charge until they are either fully recharged or taken on another trip.

These assumptions result in a bounding case in which vehicle state of charge is maximized at all times. This bounding case would minimize range anxiety, but is based on unrealistically high electric vehicle service equipment (EVSE) (i.e., charger) access, and unrealistic plug-in behavior. (Regarding the latter point, battery electric vehicles [BEVs] are often only plugged in a few times per week, but ubiquitous-immediate charging can result in dozens of charging sessions per week.)

## Contents

- [dsgrid Project Definition and Files](#dsgrid-project-definition-and-files) - Describes the metadata, dimension, and mapping information available in [dsgrid-project-StandardScenarios/tempo_project](https://github.com/dsgrid/dsgrid-project-StandardScenarios/tree/main/tempo_project)
- [Output Data Files Available on OEDI](#output-data-files-available-on-oedi) - Describes what [files are available on OEDI](https://data.openei.org/submissions/5958) and documents how to work with them using DuckDB, pandas, or PySpark.
    - [Directory Structure and Contents](#directory-structure-and-contents)
    - [Working with Datasets](#working-with-datasets)
        - [DuckDB](#examples-duckdbipynb)
        - [pandas](#examples-pandasipynb)
        - [PySpark](#examples-sparkipynb)
- [Options for Accessing Different Slices of the Data](#options-for-accessing-different-slices-of-the-data) - Outlines options for creating or requesting the publication of different slices of the data than the ones that are already available.

## dsgrid Project Definition and Files

The [dsgrid](https://github.com/dsgrid/dsgrid) software provides the construct of a [*dsgrid Project*](https://dsgrid.github.io/dsgrid/explanations/components/projects.html) for aligning [*Datasets*](https://dsgrid.github.io/dsgrid/explanations/components/datasets.html) via *Base Dimensions*. dsgrid does this by requiring [*dataset contributors*](https://dsgrid.github.io/dsgrid/#dataset-contributors) and [*project coordinators*](https://dsgrid.github.io/dsgrid/#project-coordinators) to very explicitly define resolution across eight [*Dimension Types*](https://dsgrid.github.io/dsgrid/explanations/components/dimensions.html#dimension-types):
- `scenario`
- `model_year`
- `weather_year`
- `geography`
- `time`
- `sector`
- `subsector`
- `metric`

In this project, whose purpose is to publish the TEMPO data documented in https://www.nrel.gov/docs/fy23osti/83916.pdf, the starting point is the [dataset](https://github.com/dsgrid/dsgrid-project-StandardScenarios/tree/main/tempo_project/dataset), whose *Dimensions* are defined in the `dimensions` portion of the [`dataset.json5`](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dataset/dataset.json5) config file, and in the `.csv` files referenced therein, which are available in the [dataset's dimensions folder](https://github.com/dsgrid/dsgrid-project-StandardScenarios/tree/main/tempo_project/dataset/dimensions). In brief, the dataset dimensions are:
- `scenario`: Projections are provided for three scenarios: 'Reference' ('reference'), 'EFS High LDVs' ('efs_high_ldv'), 'LDV Sales All-EV by 2035' ('ldv_sales_evs_2035'); `display name: 'scenario'`
- `model_year`: Projection years from 2018 to 2050 in two year intervals
- `weather_year`: Trivial dimension (only one element) indicating that these data follow the 2012 Actual Meteorological Year; `display name: 'weather_2012'`
- `geography`: Contiguous U.S. counties, American Community Survey (U.S. Census Bureau 2018)
- `time`: Representative week charging profiles, hourly for each month
- `sector`: Trivial dimension (only one element) equal to id: 'trans', name: 'Transportation'; `display name: 'transportation'`
- `subsector`: TEMPO household bins and vehicle types (60 household bins x 12 vehicle types=720 combinations); `display name: 'household_and_vehicle_type'`
- `metric`: Energy use split into L1&L2, DCFC, recorded in kWh

The project's *Base Dimensions*, which are outlined in the `base_dimensions` portion of the `project.json5` that lives in [the project folder](https://github.com/dsgrid/dsgrid-project-StandardScenarios/tree/main/tempo_project), mostly reuses the dataset's dimensions, with the following exceptions:
- `model_year`: Projection years from 2024 to 2050 in two year intervals; `display name: 'tempo_project_model_year'`
- `geography`: Contiguous U.S. counties (U.S. Census Bureau 2020); `display name: 'county'`
- `time`: Hourly, period beginning timestamps for 2012 (to match this project's weather year) as experienced in Eastern Standard Time (EST). Leap day is retained, and data are available for all 8784 EST hours.; `display name: 'time_est'`
- `metric`: Energy use split into L1&L2, DCFC, recorded in MWh; `display name: 'end_use'`

Analogous to the dataset, the files referenced by the dimension definitions generally live in the [project's dimensions folder](https://github.com/dsgrid/dsgrid-project-StandardScenarios/tree/main/tempo_project/dimensions).

When dataset and project dimensions don't match for a given dimension type, the *dataset contributor* must provide a [*Dimension Mapping*](https://dsgrid.github.io/dsgrid/explanations/components/dimension_mappings.html) file *unless the dimension type in question is a Time type*, in which case dsgrid handles the transformations programmatically. In this project, the dataset provides mapping files ([dimension_mappings.json5](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dataset/dimension_mappings.json5), [dimension_mappings folder](https://github.com/dsgrid/dsgrid-project-StandardScenarios/tree/main/tempo_project/dataset/dimension_mappings)) for:
- `model_year`: Drop data for historical years
- `geography`: Map vintage 2018 counties into vintage 2020 counties
- `metric`: Map the different labels used to indicate L1&L2 and DCFC together. (For example, the dataset uses the id `L1andL2` while the project uses the id `electricity_ev_l1l2`.)

dsgrid translates TEMPO's representative week data into 8784 profiles that account for day of week, each geography's time zone, and daylight savings time. dsgrid also converts the energy use (metric) data from kWh to MWh automatically. **All energy use reported in the OEDI data is in MWh.**

dsgrid projects also enable [*Queries*](https://dsgrid.github.io/dsgrid/tutorials/query_project.html), which start by mapping datasets to the project's base dimensions and then perform user-specified mapping, filtering, aggregation, and sorting operations. Outputs can of course use the project's base dimensions, but they can also make use of *Supplemental Dimensions*. The available supplemental dimensions are outlined in the `subset_dimensions` and `supplemental_dimensions` portions of the [`project.json5`](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/project.json5) file, which refer to .csv files in the [dimensions/subset](https://github.com/dsgrid/dsgrid-project-StandardScenarios/tree/main/tempo_project/dimensions/subset) and [dimensions/supplemental](https://github.com/dsgrid/dsgrid-project-StandardScenarios/tree/main/tempo_project/dimensions/supplemental) folders. Regular *Supplemental Dimensions* and their [associated mapings](https://github.com/dsgrid/dsgrid-project-StandardScenarios/tree/main/tempo_project/dimension_mappings/base_to_supplemental) work analogously to dataset dimensions and their mappings. *Subset Dimensions* are simple alternative groupings of the project's base dimensions. Each subset dimension is defined in one file that maps each base dimension record of the given dimension type to a specific *Subset Dimension Selector* which functions as an element of the overall supplemental dimension created by the subset dimension and can also be used on its own to select or refer to specific slices of data.

The data published on OEDI make use of the following supplemental dimensions:
- `metric`:
    - Subset dimension `end_uses_by_fuel_type`, which [maps](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimensions/subset/enduses_by_fuel_type.csv) all energy use into `electricity_end_uses`
- `subsector`:
    - Subset dimension `subsector` which [maps](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimensions/subset/dsgrid_subsectors.csv) TEMPO's 720 household bins and vehicle types into 8 simplified vehicle types (i.e., battery electric vehicle (BEV) or plug-in hybrid electric vehicle (PHEV), and compact, midsize, SUV, or pickup).
- `geography`:
    - Supplemental dimension `state`; [definition](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimensions/supplemental/states.csv), [mapping](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimension_mappings/base_to_supplemental/lookup_county_to_state.csv)
    - Supplemental dimension `census_division`; [definition](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimensions/supplemental/census_divisions.csv), [mapping](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimension_mappings/base_to_supplemental/lookup_county_to_censusdivision.csv)
    - Supplemental dimension `conus`, which aggregates all geographies together to represent the entire contiguous United States (CONUS); [definition](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimensions/supplemental/conus.csv), [mapping](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimension_mappings/base_to_supplemental/lookup_county_to_conus.csv)
- `model_year`:
    - Supplemental dimension `five_year_intervals`; [definition](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimensions/supplemental/five_year_intervals.csv), [mapping](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimension_mappings/base_to_supplemental/interpolate_to_five_year_intervals.csv)

Additional supplemental dimensions are defined in this dsgrid project, but have not been used in the published outputs:
- `subsector`:
    - Subset dimension `household_size`; [mapping](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimensions/subset/household_size.csv)
    - Subset dimension `household_income`; [mapping](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimensions/subset/household_income.csv)
    - Subset dimension `urbanity`; [mapping](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimensions/subset/urbanity.csv)
    - Subset dimension `vehicle_technology`; [mapping](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimensions/subset/vehicle_technology.csv)
    - Subset dimension `vehicle_class`; [mapping](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimensions/subset/vehicle_class.csv)
- `geography`:
    - Supplemental dimension `census_region`; [definition](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimensions/supplemental/census_regions.csv), [mapping](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimension_mappings/base_to_supplemental/lookup_county_to_censusregion.csv)
    - Supplemental dimension `reeds_pca`; [definition](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimensions/supplemental/reeds_pca.csv), [mapping](https://github.com/dsgrid/dsgrid-project-StandardScenarios/blob/main/tempo_project/dimension_mappings/base_to_supplemental/lookup_county_to_reeds_pca.csv)

## Output Data Files Available on OEDI

### Directory Structure and Contents

Output data are available through OEDI. All numerical data are energy use projections as would be measured at electrical meters in units of MWh. The top-level folders available in the Data Lake are:

| Folder Name              | Folder Contents                                                    | Folder Size | Partitioned By              |
| ------------------------ | ------------------------------------------------------------------ | ----------- | --------------------------- |
| `query_files`            | dsgrid query definitions in .json5 format                          |        32 K | N/A (not a dataset)         |
| `full_dataset`           | Full dataset in project base dimensions                            |       742 G | scenario, model_year, state |
| `full_state_level`       | Aggregation to `state`                                             |        63 G | state, scenario, model_year | 
| `state_level_simplified` | Aggregation to `state`, `subsector`, and one (electric) end use    |       964 M | scenario                    |
| `simple_profiles`        | Aggregation to `census_division`, one subsector, and one end use   |       112 M | N/A                         |
| `annual_summary_conus`   | Aggregation to `conus`, `subsector`, one end use, and annual time  |        52 K | N/A                         |
| `annual_summary_state`   | Aggregation to `state`, `subsector`, one end use, and annual time  |       1.1 M | N/A                         |
| `annual_summary_county`  | Aggregation to `county`, `subsector`, one end use, and annual time |       3.2 M | N/A                         |

Each dataset folder contains:
- `query.json`: dsgrid query definition as output by the CLI in the course of running the query.
- `metadata.json`: File that describes the structure of the output table.
- `table.parquet`: Folder containing the output table in .parquet format. Some datasets (i.e., `full_dataset`, `full_state_level`, and `state_level_simplified`) are partitioned on meaningful columns, which makes it so that subfolders of `table.parquet` can be loaded as parquet files on their own to get access to certain slices of the data without loading the entire dataset.
- `table.csv`: ONLY PRESENT FOR SMALL DATASETS. The same data as table.parquet but in comma separated value (CSV, .csv) format.

### Working with Datasets

In this repository, under `tempo_project/notebooks`, we provide example notebooks you can run using [duckdb](https://github.com/dsgrid/dsgrid-project-StandardScenarios/tree/main/tempo_project/notebooks/examples-duckdb.ipynb), [pandas](https://github.com/dsgrid/dsgrid-project-StandardScenarios/tree/main/tempo_project/notebooks/examples-pandas.ipynb), or [spark](https://github.com/dsgrid/dsgrid-project-StandardScenarios/tree/main/tempo_project/notebooks/examples-spark.ipynb) after you adjust `data_dir` to point to the location where you have downloaded one or more of the folders listed above and `dataset_name` to be the name of the folder containing the dataset you want to access.

All three notebooks:
- Load the `metadata.json` files to programmatically access the dataset column names, and use that information to discern, e.g., geographic resolution, whether the data are hourly or annual.
- Display the initial timestamps (hourly data only).
    - The timestamps stored in the dsgrid .parquet files are in UTC and cover the EST year 2012. Depending on exactly how the data are loaded, the starting timestamp might show up as `2012-01-01 00:00:00` (i.e., the starting timestamp in EST) or as `2012-01-01 05:00:00` (i.e., the starting timestamp in UTC).
    - If the first timestamp is `2012-01-01 05:00:00` the notebook also demonstrates how to adjust the timestamps to start with `2012-01-01 00:00:00` as expected.
- Validate the data by:
    - Re-creating the lefthand side of Figure ES-1 in https://www.nrel.gov/docs/fy23osti/83916.pdf
    - For hourly data only, plotting daily load profiles for two different days, one during standard time and one during daylight savings time, and for four different geographies, one for each time zone in the contiguous United States

#### Loading the metadata

Although the dsgrid query interface provides other options, all of the published datasets have at most one column per dimension type and have been written in unpivoted format. Thus, the column names can be loaded as in this example:

```python
import json
from pathlib import Path

def get_metadata(dataset_path):
    with open(dataset_path / "metadata.json") as f:
        result = json.load(f)
    return result

# load metadata and get column names by type
metadata = get_metadata(data_dir / dataset_name)
assert metadata["table_format"]["format_type"] == "unpivoted", metadata["table_format"]
value_column = metadata["table_format"]["value_column"]
columns_by_type = {dim_type: metadata["dimensions"][dim_type][0]["column_names"][0] 
                   for dim_type in metadata["dimensions"] if metadata["dimensions"][dim_type]}
```

Note that trivial dimensions, i.e., those with only one possible value, like `weather_year`, have column names listed in the metadata but are not included in the data files. Thus, not all column names listed in the metadata and loaded into `columns_by_type` will actually be present in loaded data frames.

#### Data size capabilities of the tools

This table summarizes the data size capabilities of DuckDB, pandas, and Spark *on NREL HPC (Kestrel) compute nodes,* which have 104 cores, 256 GB of memory, and 1.92 TB of local storage.

| Dataset                  | Tool    | Number of Nodes | Able to Load and Count Data? | Able to Recreate Lefthand Side of Figure ES-1? | Example Partition that Can Be Loaded |
| ------------------------ | ------- | --------------- | ---------------------------- | ---------------------------------------------- | ------------------------------------ | 
| `full_dataset`           | DuckDB  | 1               | No (> 1 hour)                | No                                             | scenario=efs_high_ldv, tempo_project_model_years=2050, state=CA |
| `full_state_level`       | DuckDB  | 1               | No (> 1 hour)                | No                                             | state=CA                             | 
| `state_level_simplified` | DuckDB  | 1               | Yes                          | Yes                                            | Not Necessary                        |
| `simple_profiles`        | DuckDB  | 1               | Yes                          | Yes                                            | N/A                                  |
| `annual_summary_conus`   | DuckDB  | 1               | Yes                          | Yes                                            | N/A                                  |
| `annual_summary_state`   | DuckDB  | 1               | Yes                          | Yes                                            | N/A                                  |
| `annual_summary_county`  | DuckDB  | 1               | Yes                          | Yes                                            | N/A                                  |
| `full_dataset`           | pandas  | 1               | No                           | No                                             | scenario=efs_high_ldv, tempo_project_model_years=2050, state=CA |
| `full_state_level`       | pandas  | 1               | No                           | No                                             | state=CA                             | 
| `state_level_simplified` | pandas  | 1               | Yes                          | Yes                                            | Not Necessary                        |
| `simple_profiles`        | pandas  | 1               | Yes                          | Yes                                            | N/A                                  |
| `annual_summary_conus`   | pandas  | 1               | Yes                          | Yes                                            | N/A                                  |
| `annual_summary_state`   | pandas  | 1               | Yes                          | Yes                                            | N/A                                  |
| `annual_summary_county`  | pandas  | 1               | Yes                          | Yes                                            | N/A                                  |
| `full_dataset`           | PySpark | 1               | Yes                          | Yes                                            | Not Necessary                        |
| `full_state_level`       | PySpark | 1               | Yes                          | Yes                                            | Not Necessary                        |
| `state_level_simplified` | PySpark | 1               | Yes                          | Yes                                            | Not Necessary                        |
| `simple_profiles`        | PySpark | 1               | Yes                          | Yes                                            | N/A                                  |
| `annual_summary_conus`   | PySpark | 1               | Yes                          | Yes                                            | N/A                                  |
| `annual_summary_state`   | PySpark | 1               | Yes                          | Yes                                            | N/A                                  |
| `annual_summary_county`  | PySpark | 1               | Yes                          | Yes                                            | N/A                                  |

#### examples-duckdb.ipynb

Dependencies:
- python>=3.10
- jupyter
- duckdb>=0.9.2
- pandas
- plotly

Advantages: DuckDB makes the most efficient use of available resources and is easy to set up.

Limitations: DuckDB is limited to one node and can run out of resources. What datasets you can analyze and what queries you can perform thus depends on the hardware you use.

##### Getting Started

DuckDB easily loads parquet files, including partitioned files assuming the duckdb version is sufficiently recent. For example, a dataset can be loaded and then previewed with the code:
```python
import duckdb

def load_table(filepath, tablename):
    duckdb.sql(f"""CREATE TABLE {tablename} AS SELECT * 
                     FROM read_parquet('{filepath}/**/*.parquet', hive_partitioning=true, hive_types_autocast=false)""")
    description = duckdb.sql(f"DESCRIBE {tablename}")
    logger.info(f"Loaded {filepath} as {tablename}:\n{description}")

# load data table
filepath = data_dir / dataset_name / "table.parquet"
tablename = "tbl"
load_table(filepath, tablename)
duckdb.sql(f"SELECT * FROM {tablename} LIMIT 5").df()
```
For example, with `dataset_name = "state_level_simplified"` running this code in the notebook returns:
![screenshot](docs/duckdb-load-data.png "Notebook output after loading 'state_level_simplified' into DuckDB")

##### Writing Queries

[DuckDB](https://duckdb.org/docs/) provides a variety of interfaces. The example notebook uses the Python package to read .parquet files using the SQL interface. In this case, and assuming the data have been loaded as described above, one example query is:
```
df = duckdb.sql(f"""SELECT scenario, {columns_by_type["model_year"]} as year, 
                           SUM({value_column})/1.0E6 as annual_twh
                      FROM {tablename} 
                  GROUP BY scenario, {columns_by_type["model_year"]}
                  ORDER BY scenario, year""").df()
```
which returns a `pandas.DataFrame` containing three columns: `scenario`, `year`, and `annual_twh`.

A couple of timestamp-related queries that are demonstrated in the notebook include:
1. Shifting the timestamps to match the `time_est` label rather than being in `UTC` (example shown is for `dataset_name = "state_level_simplified"`):

      ```SQL
        SELECT scenario, 
               state, 
               tempo_project_model_years, 
               subsector, time_est - INTERVAL 5 HOUR as time_est, 
               weather_2012, 
               value 
          FROM tbl 
         WHERE (scenario = 'reference') AND 
               (tempo_project_model_years = 2050) AND 
               (subsector = 'bev_compact')
      ORDER BY time_est 
         LIMIT 5
    ```

2. Selecting timstamps within a range:

    ```Python
    import datetime as dt
    
    # Select UTC timestamps that correspond to EST 2/14/2012
    start_timestamp = dt.datetime(2012, 2, 14, 5)
    stop_timestamp = dt.datetime(2012, 2, 15, 4)

    duckdb.sql(f"""SELECT time_est, 
                          SUM({value_column}) as {value_column}
                     FROM {tablename} 
                    WHERE {where_clause} AND 
                          (time_est >= TIMESTAMP '{start_timestamp}') AND 
                          (time_est <= TIMESTAMP '{end_timestamp}')
                 GROUP BY time_est 
                 ORDER BY time_est""")
    ```

##### Additional Reading

The following DuckDB documentation links might be helpful:
- [Parquet import and export](https://duckdb.org/docs/data/parquet/overview) - Our examples use `CREATE TABLE` to enable multiple queries on the same dataset without reloading the files.
- [Client APIs](https://duckdb.org/docs/api/overview) - Read up more on the Python API or try out a different API if you prefer to work in a different language.
- [SQL Syntax Documentation](https://duckdb.org/docs/sql/introduction) - This documentation starts from the basics and is well organized. Because timestamps are always hard for everyone, this page might be of particular interest: [Timestamp Functions](https://duckdb.org/docs/sql/functions/timestamp).


#### examples-pandas.ipynb

Dependencies:
- python>=3.10
- jupyter
- pandas
- pyarrow
- plotly

Advantages: Very familiar to many Python users and easy to use.

Limitations: Of the three documented options, pandas is least able to work with large datasets. For any of the large (e.g., 1 GB or greater on disk) datasets, most users will quickly run into issues trying to open the whole dataset as a pandas.DataFrame. For that reason, we have partitioned the large datasets into smaller chunks that should be openable (one-by-one) in this standard tool.

##### Getting Started

pandas easily loads parquet files even when those files are actually directories containing a partitioned dataset. For example, running this code:
```Python
import pandas as pd

dataset_name = "state_level_simplified"

# Load data table
filepath = data_dir / dataset_name / "table.parquet"
df = pd.read_parquet(filepath)
logger.info(f"df.dtypes = \n{df.dtypes}")
df.head(5)
```
in the notebook returns:
![screenshot](docs/pandas-load-data.png "Notebook output after loading 'state_level_simplified' into pandas")

When loading .csv files, pandas does not have explicit information on data types and therefore does its best to guess the type of data in each column (e.g., str, int, float). Therefore, the example notebook contains the following extended data loading code to ensure that columns come in with the same data type no matter if they are loaded from .csv or .parquet:

```
# Load data table
filepath = data_dir / dataset_name / "table.csv"
if not filepath.exists():
    filepath = data_dir / dataset_name / "table.parquet"

if filepath.suffix == ".csv":
    kwargs = { 
        "dtype": { columns_by_type['model_year']: str }
    }
    if columns_by_type['time'] == "time_est": 
        kwargs["parse_dates"] = ["time_est"]
        
    df = pd.read_csv(filepath, **kwargs) 
else:  
    df = pd.read_parquet(filepath)
    
logger.info(df.dtypes)
df.head(5)
```

##### Writing Queries

The pandas.DataFrame interface enables SQL-like functionality, but with a different syntax. For example, to get a summary data frame with three columns: `scenario`, `year`, and `annual_twh`; we can write:

```
df2 = (df.groupby(["scenario", columns_by_type["model_year"]])[value_column].sum() / 1.0E6).reset_index()
df2.rename({columns_by_type["model_year"]: "year", value_column: "annual_twh"}, axis=1, inplace=True)
```

And duplicating the timestamp-related queries documented for DuckDB above looks like:
1. Shifting the timestamps to match the `time_est` label rather than being in `UTC`:

    ```Python
    df3 = df2.copy()
    df3["time_est"] = df3["time_est"] - dt.timedelta(hours=5)
    df3.head(5)
    ```

2. Selecting timestamps within a range:

    ```Python
    inds &= ((df['time_est'] >= start_timestamp) & (df['time_est'] <= end_timestamp))
    df2 = df[inds].groupby("time_est")[value_column].sum().reset_index().sort_values("time_est")
    ```

#### examples-spark.ipynb

Dependencies:
- python>=3.12
- jupyter
- pyspark==3.5.0 (exact version required for NREL HPC)
- pandas
- plotly

Advantages: The data were originally created with Spark, and Spark nominally works with all of the datasets (assuming sufficient computational hardware is available).

Limitations: Although set-up is easy for local mode, Spark only offers advantages over DuckDB and pandas when run in cluster mode, which can be challenging to set up and expensive to run.

##### Getting Started

Large datasets require running Spark in cluster mode rather than local mode. To run the example notebook in cluster mode on NREL HPC resources, follow these two sets of instructions:
- https://dsgrid.github.io/dsgrid/how_tos/spark_cluster_on_kestrel.html
- https://dsgrid.github.io/dsgrid/spark_overview.html#jupyter

Running the code that follows without performing these steps (or the equivalent) first will run PySpark in local mode, which syntatically works the same, but computationally is less performant than DuckDB.

PySpark easily loads parquet tables no matter over how many files and directories the table is stored. For example, running this code:
```Python
from pyspark.sql import SparkSession

spark = (
            SparkSession.builder
            .appName("dsgrid")
            .config("spark.sql.sources.partitionColumnTypeInference.enabled", "false")
            .config("spark.sql.session.timeZone", "EST")
            .getOrCreate()
        )

dataset_name = "state_level_simplified"

# Load data table
filepath = data_dir / dataset_name / "table.parquet"
df = spark.read.parquet(str(filepath))
tablename = "tbl"
df.createOrReplaceTempView(tablename)
logger.info(f"Loaded {filepath} as {tablename}:\n{df.printSchema()}")
df.show(n=5)
```
in the notebook returns:
![screenshot](docs/pyspark-load-data.png "Notebook output after loading 'state_level_simplified' into PySpark")

##### Writing Queries

[PySpark](https://spark.apache.org/docs/latest/api/python/index.html) data frames can be queried using functions like [filter](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.filter.html#pyspark.sql.DataFrame.filter) or by writing straight SQL. In the notebook we use SQL. For example, this query (when the data are small enough to process):
```Python
df = spark.sql(f"""SELECT scenario, 
                          {columns_by_type["model_year"]} as year, 
                          SUM({value_column})/1.0E6 as annual_twh
                     FROM {tablename} 
                 GROUP BY scenario, {columns_by_type["model_year"]}
                 ORDER BY scenario, year""").toPandas()
```
returns a `pandas.DataFrame` containing three columns: `scenario`, `year`, and `annual_twh`.

And this is an example of how to select timestamps within a range:
```Python
import datetime as dt
    
# Select EST timestamps for 2/14/2012
start_timestamp = dt.datetime(2012, 2, 14, 0)
stop_timestamp = dt.datetime(2012, 2, 14, 23)

df = spark.sql(f"""SELECT time_est, 
                          SUM({value_column}) as {value_column}
                     FROM {tablename} 
                    WHERE {where_clause} AND 
                          (time_est >= TIMESTAMP '{start_timestamp}') AND 
                          (time_est <= TIMESTAMP '{end_timestamp}')
                GROUP BY time_est 
                ORDER BY time_est""").toPandas()
```

##### Additional Reading

- [dsgrid Spark documentation](https://dsgrid.github.io/dsgrid/spark_overview.html) - Currently focuses on using Spark, especially dsgrid use cases, on NREL HPC. If you have NREL HPC access and would like more information, please reach out to the dsgrid team. Also see [NREL HPC Spark documentation](https://github.com/NREL/HPC/tree/master/applications/spark).
- [Spark on AWS](https://aws.amazon.com/emr/features/spark/) - Other cloud providers will have similar documentation.

## Options for Accessing Different Slices of the Data

The datasets published on OEDI are meant to enable broad access for common use cases while balancing different users' ability to work with large datasets. However, we might not have covered your use case, and there are many other aggregations that are possible with the current set of supplemental dimensions. Even more types of aggregations could be created if additional supplemental dimensions were added to the dsgrid project.

There are essentially two reasons (alone or in combination) why working directly with the published data using your data analysis package of choice might not meet your needs:
1. Data size - The full dataset expands to over 1 TB in memory. Although some tools (like DuckDB) can nominally process very large datasets on a typical laptop by actively managing memory and CPU resources, in practice that can either take a very long time or fail if the query is very complex and/or not well aligned with how the data are laid out across files. Other tools present different challenges. For example, pandas can only work with datasets that fit in memory, and Spark can work with very large datasets but only if it can spread the work out over multiple compute nodes (in cluster, rather than local, mode).
2. Output dimensions - One or more dimension types might not be described at the level of resolution you want. Depending on the type of mapping desired, it may or may not be straightforward to perform your own join operations outside of dsgrid.

If you hit one of these issues, you have at least two options, see below. Super-power users might also be interested in directly using dsgrid software, which is nominally possible, but not recommended due to complex software dependencies (i.e., ArangoDB and Apache Spark), computational requirements (i.e., HPC or Cloud), and large data sizes. That said, if you really think you want to go down this route, please reach out to the dsgrid team to learn more.

### Option 1: Write your own processing code to work through the data sequentially

Although you would not want to download the full dataset to most machines, you could process it sequentially using a combination of [`awscli`](https://aws.amazon.com/cli/) and your data analysis package of choice. **Warning:** Not for the faint of heart, and you will want to double- and triple-check the result.

### Option 2: Reach out to the dsgrid team

If you're looking for a query that is easy to run and/or expected to be of broad interest, please reach out to us and we will let you know if we are able to fulfill 
the request.
