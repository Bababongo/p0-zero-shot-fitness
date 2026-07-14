#!/bin/bash
#SBATCH --job-name=p0-pmpnn-prof
#SBATCH --partition=savio3_gpu
#SBATCH --account=fc_pkss
#SBATCH --qos=a40_gpu3_normal
#SBATCH --output=logs/p0-pmpnn-prof-%j.out
#SBATCH --error=logs/p0-pmpnn-prof-%j.err
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:A40:1

set -euo pipefail

ROOT="/global/scratch/users/ezechinyereukabiala/p0-zero-shot-fitness"
P0_ENV="/global/scratch/users/ezechinyereukabiala/conda_envs/p0-zero-shot-fitness"
PROTEINMPNN_ENV="${PROTEINMPNN_ENV:-/global/scratch/users/ezechinyereukabiala/conda_envs/proteinmpnn}"
PROTEINMPNN_ROOT="${PROTEINMPNN_ROOT:-/global/scratch/users/ezechinyereukabiala/ProteinMPNN}"

mkdir -p "$ROOT/logs"

module load anaconda3

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-4}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-4}"
export PYTHONUNBUFFERED=1

cd "$ROOT"
echo "PWD=$(pwd)"
echo "ProteinMPNN root: $PROTEINMPNN_ROOT"

if [ ! -f "$PROTEINMPNN_ROOT/protein_mpnn_run.py" ]; then
  echo "[ERROR] ProteinMPNN not found at $PROTEINMPNN_ROOT/protein_mpnn_run.py"
  echo "Clone ProteinMPNN on Savio or set PROTEINMPNN_ROOT before submitting."
  exit 1
fi

run_profile() {
  local protein_id="$1"
  local structure_path="$2"
  local fasta_path="$3"
  local output_dir="$4"
  local seed="$5"

  local raw_dir="$output_dir/mpnn_raw"
  mkdir -p "$raw_dir"

  echo "[RUN] ProteinMPNN probabilities for $protein_id"
  source activate "$PROTEINMPNN_ENV" || conda activate "$PROTEINMPNN_ENV"
  python "$PROTEINMPNN_ROOT/protein_mpnn_run.py" \
    --pdb_path "$structure_path" \
    --out_folder "$raw_dir" \
    --unconditional_probs_only 1 \
    --num_seq_per_target 1 \
    --batch_size 1 \
    --seed "$seed"

  local npz_path
  npz_path=$(find "$raw_dir" -name "*.npz" -type f | sort | tail -1)
  if [ -z "$npz_path" ]; then
    echo "[ERROR] No ProteinMPNN NPZ found under $raw_dir"
    exit 1
  fi
  echo "[CONVERT] $npz_path -> $output_dir/profile.json"

  source activate "$P0_ENV" || conda activate "$P0_ENV"
  python -m pip install -e ".[proteinmpnn]"
  python scripts/convert_proteinmpnn_npz_to_profile.py \
    --proteinmpnn-npz "$npz_path" \
    --wild-type-fasta "$fasta_path" \
    --protein "$protein_id" \
    --structure "$(basename "$structure_path")" \
    --chain A \
    --source-mode unconditional_probs_only \
    --output-json "$output_dir/profile.json"
}

run_profile \
  "A4GRB6_PSEAI" \
  "data/proteingym/structures/A4GRB6_PSEAI.pdb" \
  "data/proteingym/A4GRB6_PSEAI.fasta" \
  "results/proteingym_vim2_proteinmpnn" \
  1301

run_profile \
  "AMIE_PSEAE" \
  "data/proteingym/structures/AMIE_PSEAE.pdb" \
  "data/proteingym/AMIE_PSEAE.fasta" \
  "results/proteingym_amie_proteinmpnn" \
  1302

run_profile \
  "Q59976_STRSQ" \
  "data/proteingym/structures/Q59976_STRSQ.pdb" \
  "data/proteingym/Q59976_STRSQ.fasta" \
  "results/proteingym_bgly_proteinmpnn" \
  1303

echo "[DONE] ProteinMPNN profile generation and conversion finished."
