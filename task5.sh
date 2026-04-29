#!/bin/bash
#BSUB -u charlie.c.kjaerager@gmail.com
#BSUB -B
#BSUB -N
#BSUB -J task5
#BSUB -q hpc
#BSUB -W 300
#BSUB -R "rusage[mem=100GB]"
#BSUB -R "select[model==XeonGold6126R]"
#BSUB -o task5.out
#BSUB -e task5.err
#BSUB -n 8
#BSUB -R "span[hosts=1]"

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

python task5.py 15
