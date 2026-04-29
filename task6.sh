#!/bin/bash
#BSUB -u charlie.c.kjaerager@gmail.com
#BSUB -B
#BSUB -N
#BSUB -J task6
#BSUB -q hpc
#BSUB -W 300
#BSUB -R "rusage[mem=100GB]"
#BSUB -R "select[model==XeonGold6126R]"
#BSUB -o task6.out
#BSUB -e task6.err
#BSUB -n 8
#BSUB -R "span[hosts=1]"

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

python task6.py 15
