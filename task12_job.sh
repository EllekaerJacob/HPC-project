#!/bin/sh
#BSUB -J task12
#BSUB -q gpua100
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=64GB]"
#BSUB -W 01:00
#BSUB -o task12_%J.out
#BSUB -e task12_%J.err

set -e

# This job script lives in mini project/HPC_Project, while task12.py is two
# directories above it in the HPC folder.
cd "$(dirname "$0")/../.."

export MPLCONFIGDIR="$PWD/.mplconfig"
mkdir -p "$MPLCONFIGDIR"

python3 task12.py
