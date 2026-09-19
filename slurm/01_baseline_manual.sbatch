#!/bin/bash -l

#SBATCH --job-name=csci548-baselines
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:h200:1
#SBATCH --time=00:20:00

#SBATCH --output=/scratch/%u/csci548/logs/%x-%j.out
#SBATCH --error=/scratch/%u/csci548/logs/%x-%j.err

source ~/medora_env.sh

cd ~/csci548-evo-prompt

echo "========================================"
echo "CSCI 548 Baseline Evaluation"
echo "========================================"
echo "Job ID: $SLURM_JOB_ID"
echo "Host: $(hostname)"
echo "Date: $(date)"

nvidia-smi --query-gpu=name,memory.total,driver_version \
    --format=csv,noheader

python src/evaluate.py
