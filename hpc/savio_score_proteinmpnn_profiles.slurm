#!/bin/bash
#SBATCH --job-name=p0-pmpnn-score
#SBATCH --partition=savio3_gpu
#SBATCH --account=fc_pkss
#SBATCH --qos=a40_gpu3_normal
#SBATCH --output=logs/p0-pmpnn-score-%j.out
#SBATCH --error=logs/p0-pmpnn-score-%j.err
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --gres=gpu:A40:1

set -euo pipefail

ROOT="/global/scratch/users/ezechinyereukabiala/p0-zero-shot-fitness"
CONDA_ENV="/global/scratch/users/ezechinyereukabiala/conda_envs/p0-zero-shot-fitness"

mkdir -p "$ROOT/logs"

module load anaconda3
source activate "$CONDA_ENV" || conda activate "$CONDA_ENV"

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-4}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-4}"
export PYTHONUNBUFFERED=1

cd "$ROOT"
echo "PWD=$(pwd)"
echo "Python: $(python -V)"

python -m pip install -e ".[dev,proteinmpnn]"

python scripts/audit_proteinmpnn_targets.py \
  --output-json results/proteinmpnn_target_audit.json

python scripts/score_structure_profile_baseline.py \
  --scored-variants-csv results/proteingym_vim2_esm2_t12_35M/scored_variants.csv \
  --structure-profile-json results/proteingym_vim2_proteinmpnn/profile.json \
  --position-covariates-json results/proteingym_vim2_esm2_t12_35M/position_covariates.json \
  --dataset-name "ProteinGym A4GRB6_PSEAI_Chen_2020" \
  --output-dir results/proteingym_vim2_proteinmpnn \
  --bootstrap-iterations 1000 \
  --null-iterations 1000 \
  --covariate-null-iterations 1000

python scripts/score_structure_profile_baseline.py \
  --scored-variants-csv results/proteingym_amie_esm2_t12_35M/scored_variants.csv \
  --structure-profile-json results/proteingym_amie_proteinmpnn/profile.json \
  --position-covariates-json results/proteingym_amie_esm2_t12_35M/position_covariates.json \
  --dataset-name "ProteinGym AMIE_PSEAE_Wrenbeck_2017" \
  --output-dir results/proteingym_amie_proteinmpnn \
  --bootstrap-iterations 1000 \
  --null-iterations 1000 \
  --covariate-null-iterations 1000

python scripts/score_structure_profile_baseline.py \
  --scored-variants-csv results/proteingym_bgly_esm2_t12_35M/scored_variants.csv \
  --structure-profile-json results/proteingym_bgly_proteinmpnn/profile.json \
  --position-covariates-json results/proteingym_bgly_esm2_t12_35M/position_covariates.json \
  --dataset-name "ProteinGym Q59976_STRSQ_Romero_2015" \
  --output-dir results/proteingym_bgly_proteinmpnn \
  --bootstrap-iterations 1000 \
  --null-iterations 1000 \
  --covariate-null-iterations 1000

echo "[DONE] P0 ProteinMPNN profile scoring finished."
