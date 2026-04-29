#!/bin/bash
#BSUB -u charlie.c.kjaerager@gmail.com
#BSUB -B
#BSUB -N
#BSUB -J simulations
#BSUB -q hpc
#BSUB -W 300
#BSUB -R "rusage[mem=100GB]"
#BSUB -R "select[model==XeonGold6126R]"
#BSUB -o simulations.out
#BSUB -e simulations.err
#BSUB -n 1
#BSUB -R "span[hosts=1]"

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

kernprof -l simulate.py 15
python -m line_profiler -rmt simulate.py.lprof