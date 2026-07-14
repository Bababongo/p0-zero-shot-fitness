#!/bin/bash
#SBATCH --job-name=p0-amie-35m
#SBATCH --partition=savio3_gpu
#SBATCH --account=fc_pkss
#SBATCH --qos=a40_gpu3_normal
#SBATCH --output=logs/p0-amie-35m-%j.out
#SBATCH --error=logs/p0-amie-35m-%j.err
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --gres=gpu:A40:1

set -euo pipefail

ROOT="/global/scratch/users/ezechinyereukabiala/p0-zero-shot-fitness"
CONDA_ENV="/global/scratch/users/ezechinyereukabiala/conda_envs/p0-zero-shot-fitness"

mkdir -p "$ROOT/logs"

module load anaconda3
source activate "$CONDA_ENV" || conda activate "$CONDA_ENV"

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export PYTHONUNBUFFERED=1

cd "$ROOT"
echo "PWD=$(pwd)"
echo "Python: $(python -V)"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi || true
fi

python -m pip install -e ".[esm]"

python -m p0_zero_shot_fitness.cli \
  --preset proteingym-amie \
  --scorer esm2 \
  --esm-model esm2_t12_35M_UR50D \
  --device cuda \
  --bootstrap-iterations 1000 \
  --null-iterations 1000 \
  --output-dir results/proteingym_amie_esm2_t12_35M

echo "[DONE] P0 AMIE ESM-2 35M benchmark finished."
