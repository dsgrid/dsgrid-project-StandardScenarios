# TEMPO County-level Light-duty Electric Vehicle Charging Profiles v2022

This dsgrid project has been used to publish the hourly data documented in:

Yip, Arthur, Christopher Hoehne, Paige Jadun, Catherine Ledna, Elaine Hale, and Matteo Muratori. 2023. “Highly Resolved Projections of Passenger Electric Vehicle Charging Loads for the Contiguous United States.” Technical Report. Golden, CO (United States): National Renewable Energy Laboratory. https://www.nrel.gov/docs/fy23osti/83916.pdf.

via the [Open Energy Data Initiative (OEDI)](https://data.openei.org/home).

## Contents

- [dsgrid Project Definition and Files](#dsgrid-project-definition-and-files) - Describes the metadata, dimension, and mapping information available in [dsgrid-project-StandardScenarios/tempo_project](https://github.com/dsgrid/dsgrid-project-StandardScenarios/tree/main/tempo_project)
- [Output Data Files Available on OEDI](#output-data-files-available-on-oedi) - Describes what [files are available on OEDI](https://data.openei.org/submissions/180) and documents best practices for using them.
- [Options for Accessing Different Slices of the Data](#options-for-accessing-different-slices-of-the-data) - Outlines options for creating or requesting the publication of different slices of the data than the ones that are already available.

## dsgrid Project Definition and Files

[dsgrid](HERE) provides a *dsgrid Project* container for aligning *Datasets* via *Base Dimensions*. dsgrid does this by requiring *dataset contributors* and *project coordinators* to very explicitly define resolution across X *Dimension Types*:


In this project, whose purpose is to publish TEMPO data, the starting point is the [dataset](HERE), whose *Dimensions* are defined in the X portion of the `dataset.json5` config file, and in the `.csv` files referenced therein, which are available in the [dataset's dimensions folder](HERE). In brief, the dataset dimensions are:


The project mostly reuses the dataset's dimensions, with the following exceptions:


In any case, the project's *Base Dimensions* are outlined in the X portion of the `project.json5` that lives beside this README file, as well as the files referenced therein, some of which are available in the top level of the [project's dimensions folder](HERE).

When dataset and project dimensions don't match, the *dataset contributor* must provide a mapping file, *unless the dimension type in question is a Time type*, in which case dsgrid handles the transformations programmatically. In this project, the dataset provides mapping files for:


The project also enables queries ...

## Output Data Files Available on OEDI

### Directory Structure and Contents

Output data are available through OEDI. The top-level folders availalbe in the Data Lake are:

| Folder Name            | Folder Contents                                          | Folder Size | Partitioned By |
| ---------------------- | -------------------------------------------------------- | ----------- | -------------- |
| query_files            | dsgrid query definitions in .json5 format                      |  32 K |                |
| full_dataset           | Full dataset in project base dimensions                        | 663 G |                |
| state_level_simplified | Aggregation to state, subsector, and one (electric) end use    | 1.3 G |                |
| very_simple            | Aggregation to census division, one subsector, and one end use | 225 M |                |
| annual_summary_state   | Aggregation to state, subsector, one end use, and annual time  | 404 K |                |

Each dataset folder contains:
- `query.json`: dsgrid query definition as output by the CLI in the course of running the query.
- `metadata.json`: File that describes the structure of the output table.
- `table.parquet`: Folder containing the output table in .parquet format. Some datasets are partitioned on meaningful columns, which makes it so that subfolders of `table.parquet` can be loaded as parquet files on their own to get access to certain slices of the data without loading the entire dataset.

### Working with Datasets

In this repository, under `tempo_project/notebooks`, we provide example notebooks you can run using [pyspark](HERE), [duckdb](HERE), or [pandas](HERE) after you adjust `data_dir` to point to the location where you have downloaded one or more of the folders listed above and `dataset_name` to be the name of the folder containing the dataset you want to access.

All three notebooks:
- Load the `metadata.json` files to programmatically access the dataset column names, and use that information to discern, e.g., geographic resolution, whether the data are hourly or annual.
- **Display the initial timestamps** (hourly data only) -- The timestamps stored in the dsgrid .parquet files are in UTC and cover the EST year 2012. Depending on exactly how the data are loaded, the starting timestamp might show up as `2012-01-01 00:00:00` (i.e., the starting timestamp in EST) or as `2012-01-01 05:00:00` (i.e., the starting timestamp in UTC).
- Validate the data by:
    - Re-creating the lefthand side of Figure ES-1 in https://www.nrel.gov/docs/fy23osti/83916.pdf
    - For hourly data only, plotting daily load profiles for two different days, one during standard time and one during daylight savings time, and for four different geographies, one for each time zone in the contiguous United States


#### examples-spark

Dependencies:
- jupyter
- pyspark
- pandas
- plotly

Limitations: Spark can work with all of the datasets, but for the largest datasets generally require setting up a multi-node cluster for complex queries.

##### Getting Started

##### Writing Queries

##### Additional Reading


#### examples-duckdb

Dependencies:
- jupyter
- duckdb
- pandas
- plotly

Limitations: DuckDB makes the most efficient use of available resources and is trivial to set up, but is limited to one node and can run out of resources. What datasets you can analyze and what queries you can perform thus depends on the hardware available.

##### Getting Started

##### Writing Queries

##### Additional Reading


#### examples-pandas

Dependencies:
- jupyter
- pandas
- plotly

Limitations: pandas is very familiar to many Python users, but is the most limited of these three options. For any of the large (e.g., 1 GB or greater on disk) datasets, most users will quickly run into issues trying to open the whole dataset as a pandas.DataFrame. For that reason, we have partitioned the large datasets into smaller chunks that should be openable in this standard tool.

##### Getting Started




## Options for Accessing Different Slices of the Data

The datasets published on OEDI are meant to enable broad access for common use cases while balancing different users' ability to work with large datasets. That said, we might not have covered your use case, and there are certainly many other aggregations that are possible with the current set of supplemental dimensions and even more that could be created if additional mappings were added to the dsgrid project.

There are essentially two reasons (alone or in combination) why working directly with the published data using your data analysis package of choice might not meet your needs:
1. Data size - The full dataset expands to over 1 TB in memory. Although some tools (like DuckDB) can nominally process very large datasets on a typical laptop by working through all the pieces in series, in practice that can either take a very long time or fail (if the query is very complex and/or not well aligned with how the data are laid out across files). Other tools present different challenges. For example, pandas can only work with datasets that fit in memory, and Spark can work with very large datasets but only if it can spread the work out over multiple compute nodes.
2. Output dimensions - One or more dimension types might not be described at the level of resolution you want either at all or in a (sub-)dataset that's small enough for you to work with. Depending on the type of mapping desired, it may or may not be straightforward to perform your own join operations outside of dsgrid.

If you hit one of these issues, you have at least three options.

### Option 1: Write your own processing code to work through the data sequentially

Although you would not want to download the full dataset to most machines, you could process it sequentially using a combination of `awscli` and your data analysis package of choice. **Warning:** Not for the faint of heart, and you will want to double- and triple-check the result.

### Option 2: Reach out to the dsgrid team

If you're looking for 