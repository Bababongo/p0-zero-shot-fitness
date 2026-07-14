# Savio Runbook For P0 ProteinMPNN Baseline

Scientific goal:

> Compare ESM-2 sequence-context signal, MSA conservation signal, and ProteinMPNN fixed-backbone structure signal on the same enzyme DMS assays and the same mechanism-local residue labels.

## Current Readiness

The repo now includes:

- `data/proteingym/proteinmpnn_targets.json`
- `scripts/audit_proteinmpnn_targets.py`
- `scripts/score_structure_profile_baseline.py`
- `docs/protein_mpnn_structure_baseline_plan.md`

Run this audit first:

```bash
python scripts/audit_proteinmpnn_targets.py \
  --output-json results/proteinmpnn_target_audit.json
```

Expected current result:

- VIM-2: ready
- AMIE: ready
- beta-glucosidase: ready
- TEM-1: not ready until a target-aligned BLAT_ECOLX structure or profile remap is added

## Step 1 - Update P0 On Savio

```bash
cd /global/scratch/users/ezechinyereukabiala/p0-zero-shot-fitness
git pull
module load anaconda3
source activate /global/scratch/users/ezechinyereukabiala/conda_envs/p0-zero-shot-fitness
python -m pip install -e ".[dev]"
python -m pytest
python scripts/audit_proteinmpnn_targets.py \
  --output-json results/proteinmpnn_target_audit.json
```

## Step 2 - Install Or Point To ProteinMPNN

If ProteinMPNN is not already on Savio:

```bash
cd /global/scratch/users/ezechinyereukabiala
git clone https://github.com/dauparas/ProteinMPNN.git
conda create -y --prefix /global/scratch/users/ezechinyereukabiala/conda_envs/proteinmpnn python=3.10
source activate /global/scratch/users/ezechinyereukabiala/conda_envs/proteinmpnn
python -m pip install --upgrade pip
python -m pip install torch numpy scipy biopython
```

If ProteinMPNN is already installed somewhere else, set this before submitting:

```bash
export PROTEINMPNN_ROOT=/path/to/ProteinMPNN
export PROTEINMPNN_ENV=/path/to/proteinmpnn/conda/env
```

## Step 3 - Generate ProteinMPNN Profiles

Generate one fixed-backbone amino-acid log-probability profile per ready enzyme:

- `results/proteingym_vim2_proteinmpnn/profile.json`
- `results/proteingym_amie_proteinmpnn/profile.json`
- `results/proteingym_bgly_proteinmpnn/profile.json`

Each profile must use P0's target-numbered profile schema:

```json
{
  "format": "p0_structure_log_probability_profile.v1",
  "scorer": "ProteinMPNNProfileScorer",
  "positions": {
    "1": {
      "wild_type": "M",
      "log_probabilities": {
        "A": -3.2,
        "C": -6.4,
        "D": -4.0
      }
    }
  }
}
```

The important part is that JSON position `"1"` means DMS target position 1, not arbitrary PDB residue number 1 unless the structure audit says the structure is target-aligned.

Operationally, this is two files per enzyme:

1. ProteinMPNN writes an NPZ probability file.
2. P0 converts the NPZ into `profile.json`.

The conversion command is:

```bash
python scripts/convert_proteinmpnn_npz_to_profile.py \
  --proteinmpnn-npz PATH_FROM_PROTEINMPNN.npz \
  --wild-type-fasta data/proteingym/A4GRB6_PSEAI.fasta \
  --protein A4GRB6_PSEAI \
  --structure A4GRB6_PSEAI.pdb \
  --chain A \
  --output-json results/proteingym_vim2_proteinmpnn/profile.json
```

Repeat with the AMIE and beta-glucosidase FASTA/profile paths.

If using the public ProteinMPNN repo, the probability-generation step should be run in a separate ProteinMPNN environment. The key setting is to generate per-position amino-acid probabilities from the fixed backbone, then pass the resulting NPZ through `scripts/convert_proteinmpnn_npz_to_profile.py`.

Submit the profile-generation job:

```bash
sbatch hpc/savio_generate_proteinmpnn_profiles.slurm
```

Watch it:

```bash
squeue -u ezechinyereukabiala
tail -80 logs/p0-pmpnn-prof-*.out
tail -80 logs/p0-pmpnn-prof-*.err
```

Check expected profiles:

```bash
ls -lh results/proteingym_vim2_proteinmpnn/profile.json
ls -lh results/proteingym_amie_proteinmpnn/profile.json
ls -lh results/proteingym_bgly_proteinmpnn/profile.json
```

## Step 4 - Score The Profiles Through P0

VIM-2:

```bash
python scripts/score_structure_profile_baseline.py \
  --scored-variants-csv results/proteingym_vim2_esm2_t12_35M/scored_variants.csv \
  --structure-profile-json results/proteingym_vim2_proteinmpnn/profile.json \
  --position-covariates-json results/proteingym_vim2_esm2_t12_35M/position_covariates.json \
  --dataset-name "ProteinGym A4GRB6_PSEAI_Chen_2020" \
  --output-dir results/proteingym_vim2_proteinmpnn \
  --bootstrap-iterations 1000 \
  --null-iterations 1000 \
  --covariate-null-iterations 1000
```

AMIE:

```bash
python scripts/score_structure_profile_baseline.py \
  --scored-variants-csv results/proteingym_amie_esm2_t12_35M/scored_variants.csv \
  --structure-profile-json results/proteingym_amie_proteinmpnn/profile.json \
  --position-covariates-json results/proteingym_amie_esm2_t12_35M/position_covariates.json \
  --dataset-name "ProteinGym AMIE_PSEAE_Wrenbeck_2017" \
  --output-dir results/proteingym_amie_proteinmpnn \
  --bootstrap-iterations 1000 \
  --null-iterations 1000 \
  --covariate-null-iterations 1000
```

Beta-glucosidase:

```bash
python scripts/score_structure_profile_baseline.py \
  --scored-variants-csv results/proteingym_bgly_esm2_t12_35M/scored_variants.csv \
  --structure-profile-json results/proteingym_bgly_proteinmpnn/profile.json \
  --position-covariates-json results/proteingym_bgly_esm2_t12_35M/position_covariates.json \
  --dataset-name "ProteinGym Q59976_STRSQ_Romero_2015" \
  --output-dir results/proteingym_bgly_proteinmpnn \
  --bootstrap-iterations 1000 \
  --null-iterations 1000 \
  --covariate-null-iterations 1000
```

Or score all three ready profiles with:

```bash
sbatch hpc/savio_score_proteinmpnn_profiles.slurm
```

Watch it:

```bash
squeue -u ezechinyereukabiala
tail -80 logs/p0-pmpnn-score-*.out
tail -80 logs/p0-pmpnn-score-*.err
```

## Step 5 - Compare Model Families

After scoring finishes:

```bash
python scripts/compare_model_family_metrics.py \
  results/proteingym_vim2_esm2_t12_35M/metrics.json \
  results/proteingym_vim2_msa_conservation/metrics.json \
  results/proteingym_vim2_proteinmpnn/metrics.json \
  results/proteingym_amie_esm2_t12_35M/metrics.json \
  results/proteingym_amie_msa_conservation/metrics.json \
  results/proteingym_amie_proteinmpnn/metrics.json \
  results/proteingym_bgly_esm2_t12_35M/metrics.json \
  results/proteingym_bgly_msa_conservation/metrics.json \
  results/proteingym_bgly_proteinmpnn/metrics.json \
  --output results/proteingym_ready_enzyme_model_family_comparison.json
```

This is the step that answers:

> Does structure-conditioned ProteinMPNN agree with ESM-2 and MSA conservation on mechanism-local residues?

## Step 6 - Interpretation

Do not frame ProteinMPNN as an activity predictor.

Frame it as:

> a structure-conditioned fixed-backbone compatibility baseline.

The comparison asks whether ESM-2's mechanism-local signal is also visible to a structure-conditioned inverse-folding model.
