#!/bin/bash
#BSUB -J gpujob
#BSUB -q c02613
#BSUB -W 15
#BSUB -R "rusage[mem=40GB]"
#BSUB -o cuda_%J.out
#BSUB -e cuda_%J.err
#BSUB -R "span[hosts=1]"
#BSUB -n 2
#BSUB -W 00:30


# Initialize Python environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

# Run Python script
python task8.py 15 2