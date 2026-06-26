#!/bin/bash
#SBATCH --job-name=p0-esm2-150m
#SBATCH --output=logs/p0-esm2-150m-%j.out
#SBATCH --error=logs/p0-esm2-150m-%j.err
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --gres=gpu:1

set -euo pipefail

mkdir -p logs

# Edit this section for your LBNL/NERSC environment.
# module load python
# module load cuda
# conda activate p0-zero-shot-fitness

python -m pip install -e ".[esm]"

p0-fitness \
  --preset proteingym-blat \
  --scorer esm2 \
  --esm-model esm2_t30_150M_UR50D \
  --device cuda \
  --bootstrap-iterations 1000 \
  --output-dir results/proteingym_blat_esm2_t30_150M
