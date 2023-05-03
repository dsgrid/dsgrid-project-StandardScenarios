# Build StandardScenarios registry
The `build_registry.sh` script in this directory builds a dsgrid registry containing all
StandardScenarios datasets and derived datasets. dsgrid developers need to keep the scripts updated
as new derived datasets are added.

## Dependencies
You need to have access to a dsgrid registry database. This README will be updated when the dsgrid
team has a central database. For now, refer to the dsgrid documentation or contact the developers
if you need help setting up a database.

The scripts rely on Apache Spark cluster creation scripts in
https://github.com/NREL/HPC/tree/master/applications/spark. You must clone it locally.
```
$ git clone https://github.com/NREL/HPC
```

## Preparation
The script will generate a large amount of data (currently 8-9 TiB). Run the script from
`/scratch/$USER`. Ensure that the data is correct before you copy it to `/projects/dsgrid` or AWS.

The rest of these instructions assume that you are working from an empty directory in
`/scratch/$USER`.

If `${HOME}/.dsgrid.json5` exists, edit it to point to the correct database and ensure that
``offline`` is true. If you don't have the file, run this command with correct values:
```
$ dsgrid config create --database-name TEXT --database-url TEXT --offline
```

### Required modifications
You must make several changes to `./project_registration.json5` before running the workflow.
```
$ cp $DSGRID_SS_REPO_BASE_PATH/dsgrid_project/build_registry/project_registration.json5 .
```
Open `project_registration.json5` with a text editor and make these changes:
- Modify the `conn` section to match your database.
- Replace every instance of `DSGRID_SS_REPO_BASE_PATH` with the path to your local
dsgrid-project-StandardScenarios repository. The path you give must contain the subdirectory
`dsgrid_project`.

Copy and customize the `sbatch` script `batch.sh`. You need to specify correct paths to your local
repositories as well as the name of your conda environment.
```
$ cp $DSGRID_SS_REPO_BASE_PATH/dsgrid_project/scripts/build_registry/batch.sh .
```
We have observed that building the derived datasets requires at least 6 compute nodes and that each
node needs fast local storage. Use either `bigmem` or `gpu` nodes. Using a compute node
with a spinning disk is guaranteed to fail (this is the case for the vast majority of Eagle nodes).

Run `shownodes` to check how busy the HPC is. In some cases, especially on the weekends, lots of
nodes are free. Spark scales well with nodes. Acquire as many as are available.

For reference, building `comstock_conus_2022_projected` took 36 minutes on a 6-node cluster. It
took 17 minutes on a 20-node cluster.

### Optional modifications
By default the script creates a new registry database called `standard-scenarios`. If you want to
add the project and datasets to a different database, adjust those settings accordingly.

## Run the script
```
$ sbatch batch.sh
```
