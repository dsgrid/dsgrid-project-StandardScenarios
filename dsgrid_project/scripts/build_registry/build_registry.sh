#!/bin/bash

# Builds a dsgrid StandardScenarios registry with standalone and derived datasets.

CONDA_ENV=$1
DSGRID_REPO=$2
DSGRID_SS_REPO=$3
HPC_REPO=$4

usage="Usage: bash $0 CONDA_ENV DSGRID_REPO_PATH DSGRID_STANDARD_SCENARIOS_REPO_PATH HPC_REPO_PATH"
if [ -z ${CONDA_ENV} ]; then
    echo "${usage}"
    exit 1
fi
if [ -z ${DSGRID_REPO} ]; then
    echo "${usage}"
    exit 1
fi
if [ -z ${DSGRID_SS_REPO} ]; then
    echo "${usage}"
    exit 1
fi
if [ -z ${HPC_REPO} ]; then
    echo "${usage}"
    exit 1
fi

HPC_REPO_SCRIPTS=${HPC_REPO}/applications/spark/spark_scripts
DD_QUERY_SRC_DIR=${DSGRID_SS_REPO}/dsgrid_project/derived_datasets
DSGRID_SS_BUILD_DIR=${DSGRID_SS_REPO}/dsgrid_project/scripts/build_registry
QUERY_OUTPUT=query-output
SPARK_CLUSTER="spark://$(hostname):7077"
# This may need to be adjusted for each dataset.
NUM_PARTITIONS=2400

# Run a command and exit if it fails.
function runx()
{
    $@
    if [ $? -ne 0 ]; then
      echo "Error: failed to run command: $@"
      exit 1
    fi
}

module load apptainer
runx ${HPC_REPO_SCRIPTS}/configure_and_start_spark.sh -D -M 30 -c /projects/dsgrid/containers/spark341_py311.sif
export SPARK_CONF_DIR=$(pwd)/conf
module unload apptainer

module load mamba
conda activate ${CONDA_ENV}
DSGRID_CLI=$(which dsgrid-cli.py)

# Create the registry with standalone datasets.
runx spark-submit \
    --master ${SPARK_CLUSTER} \
    --conf spark.sql.shuffle.partitions=${NUM_PARTITIONS} \
    ${DSGRID_REPO}/dsgrid/tests/register.py project_registration.json5

# Create the derived datasets from query files stored in this repository.
runx spark-submit \
    --master ${SPARK_CLUSTER} \
    --conf spark.sql.shuffle.partitions=${NUM_PARTITIONS} \
    ${DSGRID_CLI} \
    query \
    project \
    run \
    ${DD_QUERY_SRC_DIR}/comstock_conus_2022_projected.json5 \
    --no-persist-intermediate-table \
    -o ${QUERY_OUTPUT}

runx spark-submit \
    --master ${SPARK_CLUSTER} \
    --conf spark.sql.shuffle.partitions=${NUM_PARTITIONS} \
    ${DSGRID_CLI} \
    query \
    project \
    run \
    ${DD_QUERY_SRC_DIR}/resstock_conus_2022_projected.json5 \
    --no-persist-intermediate-table \
    -o ${QUERY_OUTPUT}

runx spark-submit \
    --master ${SPARK_CLUSTER} \
    --conf spark.sql.shuffle.partitions=${NUM_PARTITIONS} \
    ${DSGRID_CLI} \
    query \
    project \
    run \
    ${DD_QUERY_SRC_DIR}/tempo_conus_2022_mapped.json5 \
    --no-persist-intermediate-table \
    -o ${QUERY_OUTPUT}

# Create derived-dataset config files.
runx spark-submit \
    --master ${SPARK_CLUSTER} \
    --conf spark.sql.shuffle.partitions=${NUM_PARTITIONS} \
    ${DSGRID_CLI} \
    query \
    project \
    create-derived-dataset-config \
    ${QUERY_OUTPUT}/comstock_conus_2022_projected \
    comstock-dd

runx spark-submit \
    --master ${SPARK_CLUSTER} \
    --conf spark.sql.shuffle.partitions=${NUM_PARTITIONS} \
    ${DSGRID_CLI} \
    query \
    project \
    create-derived-dataset-config \
    ${QUERY_OUTPUT}/resstock_conus_2022_projected \
    resstock-dd

runx spark-submit \
    --master ${SPARK_CLUSTER} \
    --conf spark.sql.shuffle.partitions=${NUM_PARTITIONS} \
    ${DSGRID_CLI} \
    query \
    project \
    create-derived-dataset-config \
    ${QUERY_OUTPUT}/tempo_conus_2022_mapped \
    tempo-dd

# Register the derived datasets.
runx spark-submit \
    --master ${SPARK_CLUSTER} \
    --conf spark.sql.shuffle.partitions=${NUM_PARTITIONS} \
    ${DSGRID_CLI} \
    registry \
    datasets \
    register \
    comstock-dd/dataset.json5 \
    ${QUERY_OUTPUT}/comstock_conus_2022_projected \
    -l Register_comstock_conus_2022_projected

runx spark-submit \
    --master ${SPARK_CLUSTER} \
    --conf spark.sql.shuffle.partitions=${NUM_PARTITIONS} \
    ${DSGRID_CLI} \
    registry \
    datasets \
    register \
    resstock-dd/dataset.json5 \
    ${QUERY_OUTPUT}/resstock_conus_2022_projected \
    -l Register_resstock_conus_2022_projected

runx spark-submit \
    --master ${SPARK_CLUSTER} \
    --conf spark.sql.shuffle.partitions=${NUM_PARTITIONS} \
    ${DSGRID_CLI} \
    registry \
    datasets \
    register \
    tempo-dd/dataset.json5 \
    ${QUERY_OUTPUT}/tempo_conus_2022_mapped \
    -l Register_tempo_conus_2022_mapped

# Submit the derived datasets to the project.
# Note that this does not use the Spark cluster - it runs in local mode instead on a single node.
# Results have been mixed. In the ideal case, each of the next three commands should take no more
# than five minutes. If it looks like it will take hours, something is configured incorrectly.
dsgrid \
    registry \
    projects \
    submit-dataset \
    -p dsgrid_conus_2022 \
    -d comstock_conus_2022_projected \
    -l Submit_comstock_conus_2022_projected

dsgrid \
    registry \
    projects \
    submit-dataset \
    -p dsgrid_conus_2022 \
    -d resstock_conus_2022_projected \
    -l Submit_resstock_conus_2022_projected

dsgrid \
    registry \
    projects \
    submit-dataset \
    -p dsgrid_conus_2022 \
    -d tempo_conus_2022_mapped \
    -l Submit_tempo_conus_2022_mapped
