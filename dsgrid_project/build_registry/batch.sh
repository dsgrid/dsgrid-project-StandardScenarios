#!/bin/bash
#SBATCH --account=dsgrid
#SBATCH --job-name=dsgrid_registry
#SBATCH --time=16:00:00
#SBATCH --output=output_%j.o
#SBATCH --error=output_%j.e
#SBATCH --nodes=6
#SBATCH --mem=730G

DSGRID_REPO=${HOME}/repos/dsgrid
DSGRID_SS_REPO=${HOME}/repos/dsgrid-project-StandardScenarios
HPC_REPO=${HOME}/repos/HPC
bash ${DGRID_SS_REPO}/dsgrid_project/scripts/build_registry/build_registry.sh ${DGRID_REPO} ${DSGRID_SS_REPO} ${HPC_REPO}
