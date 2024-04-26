# TEMPO County-level Light-duty Electric Vehicle Charging Profiles v2022

This dsgrid project has been used to publish the data documented in:

Yip, Arthur, Christopher Hoehne, Paige Jadun, Catherine Ledna, Elaine Hale, and Matteo Muratori. 2023. “Highly Resolved Projections of Passenger Electric Vehicle Charging Loads for the Contiguous United States.” Technical Report. Golden, CO (United States): National Renewable Energy Laboratory. https://www.nrel.gov/docs/fy23osti/83916.pdf.

in an accessible way through the [Open Energy Data Initiative (OEDI)](https://data.openei.org/home).

## dsgrid Project Definition and Files

## Output Data Directory Structure

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

## Working with the Output Data Files

## Running dsgrid Queries

*How do people get different output files if they want them?* *What should they think about all the supplementary dimensions?*