#!/bin/bash
#SBATCH --job-name=p0-esm2-650m
#SBATCH --output=logs/p0-esm2-650m-%j.out
#SBATCH --error=logs/p0-esm2-650m-%j.err
#SBATCH --time=08:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=80G
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
  --esm-model esm2_t33_650M_UR50D \
  --device cuda \
  --bootstrap-iterations 1000 \
  --output-dir results/proteingym_blat_esm2_t33_650M
