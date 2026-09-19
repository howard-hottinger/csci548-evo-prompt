#!/bin/bash -l

#SBATCH --job-name=csci548-pilot
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:h200:1
#SBATCH --time=01:00:00

#SBATCH --output=/scratch/%u/csci548/logs/%x-%j.out
#SBATCH --error=/scratch/%u/csci548/logs/%x-%j.err

source ~/medora_env.sh

cd ~/csci548-evo-prompt

echo "============================================================"
echo "CSCI 548 Pilot Evaluation"
echo "============================================================"
echo "Job ID: $SLURM_JOB_ID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Git revision: $(git rev-parse HEAD)"

nvidia-smi \
    --query-gpu=name,memory.total,driver_version \
    --format=csv,noheader

python src/evaluate_pilot.py
