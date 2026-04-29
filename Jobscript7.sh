
#!/bin/bash
#BSUB -J task7
#BSUB -q hpc
#BSUB -W 15
#BSUB -R "rusage[mem=40GB]"
#BSUB -o taks7_%J.out
#BSUB -e task7_%J.err
#BSUB -R "span[hosts=1]"
#BSUB -n 7
#BSUB -R "select[model==XeonGold6126]"

# Initialize Python environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

# Run Python script
python task7.py 15 7