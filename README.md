# dsgrid-project-StandardScenarios
Project instructions and configuration data for the dsgrid Standard Scenarios project

⚠️ ***NOTE FOR DSGRID CONTRIBUTORS: Dsgrid project repositories are currently in active development. Details listed here are subject to change. Please work with the dsgrid Coordination team to ensure you have the latest information.*** ⚠️

## Repo Organization
```
.
├── dsgrid_project      # Every dsgrid project must be in a dsgrid_project dir
    ├── datasets        # This is where we define input datasets (by type) for the dsgrid project
    ├── dimension.toml  # Project dimension configs for new dimensions that need to be registered
    ├── dimensions      # This is where we store Project-level dimension records (csv, json) to be registered to the S3 dimension registry
    ├── env.toml        # User environment config
    └── project.toml    # Project config
```
## 🗂 Project 
Everything starts with a project...

### Project Config (project.toml)
The project config is the the nucleus of any dsgrid project; it defines the input dataset requirements and project-level dimensions (+ path to dimension records) of the dsgrid project.

*TBC (later): Will also define metadata, output requirements, benchmark checks, project-level scalars, visualization, allowable transformations, etc.*

The project config provides the following details:
- `project_id`: Unique Project ID that is Project-specific (e.g. "standard-scenarios-2021")
- `name`: A project name to accompany the ID. Optional.
- `description`: A detailed project description.
- [`input_datasets`]: List of input datasets. Each list contains the following details:
  - `dataset_id`: a unique and project-specific dataset id
  - `dataset_type`: dataset type setting; Options(`sector_model`, `historical`, `benchmark`)
  - `data_source`: Data source or model name (e.g., "ComStock")
  - `version`: Optional. Defautl
- `[dimensions]`: List of project-define dimensions. Includes `Project Dimensions` and `Supplemental Dimensions`. Each list contains either:
  1. `[project_dimensions]`: list of base-level Project Dimensions. All input datasets must match the Project Dimensions exactly or provide a mapping from the dataset's dimension to Project Dimension. All 9 project dimensions must be defined here. No duplicate dimension types are allowed.
  2. `[supplemental_dimensions]`: list of additional Supplemental Dimensions to support for querying. Duplicate dimension types are allowed.
   
  Each dimension in the lists must have the following details:
   - `type`: dimension type. Options(`sector`, `subsector`, `geography`, `end_use`, `time`, `data_source`, `model_year`, `weather_year`, `scenario`)
   - `dimension_id`: the dimension-registry UUID
   - `version`: the dimension record version association with the dimension_id to use. Optional. If no version is defined, then the latest version is used.

## 💾 Dataset
There are three dataset types:
1. Benchmark
2. Historical
3. Sector Model

Datasets can be registered outside of a project, however, to be used by a project, they must be submitted to the project and pass all project validations/meet all project expectations. 

**Dataset Repo Organization:**
```
dsgrid_project/
├── datasets                                # datasets organized by type (level1)
│   ├── benchmark
│       └── ...
│   ├── historical
│       └── ...
│   └── sector_models
│       ├── comstock                        # datasets organized further for each dataset source (level2)
│       │   ├── dataset.toml                # dataset-level configuration
│       │   ├── dimensions.toml             # dataset-specific dimension configs for dimension registry
│       │   └── dimensions                  # dir that stores dataset-specific dimension records to be registered
│       │       ├── comstock_enduses.csv    # example of dataset record file
│       │       └── ...
│       └── ...
└── ...
```

### Dataset Config (dataset.toml)
A dataset config is required for each input dataset. The config must contain the following fields:
- `dataset_id`: Unique dataset ID (project specific is prefered). For posterity's sake, the dataset_id cannot be the same as the model_name.
- `dataset_type`: Data set type. Options=(`"benchmark"`, `"historical"`, `"sector_model"`)
- `data_source`: Model or dataset source name, e.g., "ComStock"
- `path`: Dsgrid dataset S3 reigistry path of the dataset
- `description`: Detailed description of dataset 
- `[[dimensions]]`: List of dataset dimensions. Must define all 9 dimensions. For each dimension list, the following fields are required: 
  - `type` = Dimension type. Options=(`geography`, `sector`, `subsector`, `end_use`, `model_year`, `scenario`, `data_source`, `time`)
  - `dimension_id`: Dimension registry UUID, e.g. "county__58f264b4-b83d-4554-96d0-1349852ff03d"
  - `version`: Dimension registry UUID version
- `metadata`: TBD. metadata information such as origin_date, creator, contacts, organization, tags, etc. *

## 🧬 Dimension
dsgrid data (and projects) are multi-dimensional. 

There are **9 dimension types** for dsgrid data:
1. `geography`
2. `sector`
3. `subsector`
4. `end_use`
5. `time`
6. `data_source`
7. `model_year`
8. `scenario`
9. `weather_year`

All 9 dimension types must be defined for all projects and datasets. To define a dimension for a project or dataset, it must registered to the dsgrid dimension registry and the registery UUID must be provided in the project.toml or dataset.toml configuration file.

**Dimension (instance)**
Dimensions are instances of one of the 9 Dimension Types (e.g., Counties would be an instance of the Geography Dimension Type). At a minimum, dimensions specify their type, have an id, a name, and a set of dimension records. Everything but the dimension records is defined in the dimension config.

**Dimension Store**
There are three dimension stores within dsgrid. 
Dimension stores provide in-memory access to Dimensions needed to understand Projects or Datasets, or to support queries at additional resolution levels of interest. That is, there are three categories of dimension stores

1. **Dataset Dimension Store**
Defines the dimensions associated with a dataset.

2. **Project Dimension Store**
Defines the dimensions associated with a project.

3. **Project Supplemental Dimension Store**
Supplemental dimensions define additional dimensions that the project will support queries for. For example, project may want to support queries to aggregate to the State geography or to aggregate All Electricity end uses.

### Dimension Records
All dimensions must have a dimension record file (csv or json) that enumerates all of the dimension ids associated with a particular dimension. 
-	Required Fields: (`id`, `name`)
-	Required Fields for End Use Records: (`id`, `name`, `units`, `fuel_type`)
-	Optional Fields: standard module support will be provided for (`label`,`abbreviation`, `color`, `order`, `units`, `fuel_type`) but users can also provide any other user-defined field
#### Dimension Record Config (dimensions.toml)
This is dimension configuration file used to register *new* dsgrid dimension records. If a dimension has already been registered previously (e.g., for another project), there is no need to define them in the dimension configuration here.

Technically, one or many dimension configuration files can be created for projects and datasets, however, the dsgrid team recommends that project dimension configs be defined at the project-level in `dsgrid-project/dimensions.toml` while dataset-specific dimension configurations be defined at the dataset level, e.g. `./datasets/comstock/dimensions.toml`. Once a dimension has been registered, a unique UUID is generated; this UUID is then specified in the `project.toml`. The CLI `dsgrid register dimensions` command outputs a file called `dimension_with_assigned_id.toml` which also lists all of the dimension-UUIDs registered.

The dimension config defines the following for each dimension:

*If dimension type != time:*
- `type`: Non-Time Dimension Type. Options=(`geography`, `sector`, `subsector`, `end_use`, `model_year`, `scenario`, `data_source`)
- `name`: Detailed (reusable/memorable) dimension record name to be used in the dimension registry as well as the prefix to the dimensin registry UUID.
- `file`: local file path in the project repository with the dimension records (csv or json). e.g., "dimensions/scenarios.csv"
- `module`: Python module with the dimension pydantic model. Optional. If none, the default is "dsgrid.dimension.standard". Users have the ability to supply their own module if the dimension record fields differ from what is supported by dsgrid.dimension.standard.
- `class`: Dimension model class name. Optional; default class name uses the name of the dimension.
- `description`: Description of dimension record, this gets stored in both dimension config file and dimension registry
- `trivial`: Boolean flag for if the dimension is trivial (i.e., if it is a 1-element dimension)

*If dimension type == time:*
- `type`: TimeDimension type "time"
- `name`: Detailed (reusable) dimension record name to be used in dimension registry
- `start`: Start Time, e.g. "2012-01-01 01:00:00"
- `end`: End Time, e.g. "2012-12-31 23:59:59"
- `frequency`: Time frequency, e.g. "1 hour".
- `includes_dst`: Boolean flag for whether the data includes DST adjustments
- `leap_day_adjustment`: Leap day adjustments (if any) made to data. Default is None. Options include (`drop_dec31`, `drop_feb29`, `drop_jan1`)
- `period`: Time period representation. Options=(`period_ending`, `period_beginning`, `instantaneous`)
- `str_format`: String format to parse ts data, e.g. "%Y-%m-%d %H:%M:%S"
- `timezone`: Time zone of data, e.g. "PST" or "UTC"
- `value_representation`: Time value measurement. Options=(`mean`, `min`, `max`, `measured`)
- `description`: Detailed dimension description to be used in dimension registry

### Dimension Mappings 
Dimension mappings help map dimensions across/within dimension stores and dimension types. dsgrid supports three different types of mappings:
1. **Dataset-to-Project**:  Dimension mappings to translate input Dataset Dimensions to the Project Dimensions. This mapping type is for only dimensions WITHIN the same dimension type (e.g., from county to state). These are required when submitting a dataset to a project if the dataset's dimensions are different than the project's.
2. **Project-to-Supplemental**: Dimension mappings to translate Project Dimensions to Supplemental Dimensions. This mapping type is for only dimensions WITHIN the same dimension type (e.g., from county to state). This allows us to support transformation queries for supplemental dimensions at the project level. Usually, this includes query support for aggregations or disaggregations. If disaggregation, then scaling factor may be required (TBD).
1. **Project-to-Project**: Dimension mappings to categorize how different Project Dimensions map to other Project Dimensions. For example, not all end uses map to all sectors.

🚧🚧🚧 *NOTE: Dimension mappings are under active development. As of 4/13/21, we still need to build support for dimension mappings in the dsgrid-registry. More on this soon!* 🚧🚧🚧 

#### Dimension Mapping Config (dimension-mapping.toml)
🚧🚧🚧 *There will likely need to be a serperate set of configuration files for these mappings.* 🚧🚧🚧

---
## Other Configs
### Environment Config (env.toml)
🚧🚧🚧 *Coming soon. Likely to include AWS profile settings and spark configuration details.* 🚧🚧🚧