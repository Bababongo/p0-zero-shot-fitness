# Savio Runbook For P0

Scientific goal:

> Test whether ESM-2 performance changes across residue groups in TEM-1 beta-lactamase, especially catalytic residues and active-site neighborhoods.

Why Savio is needed:

- The local 8M ESM-2 run proves the pipeline works.
- The 35M Savio run tests whether the result survives a stronger model.
- Bigger ESM-2 models need GPU memory and stable runtime, so the work belongs on a compute node rather than a laptop.

Analogy:

- laptop: practice bench
- Savio login node: front desk
- GPU node: instrument room
- SLURM script: job request form
- ESM-2: microscope for sequence plausibility
- DMS data: experimental ground truth

## Step 1 - Connect To Savio

Run this from your laptop terminal:

```bash
ssh ezechinyereukabiala@hpc.brc.berkeley.edu
```

Type your Savio password/PIN/Duo response only into the terminal prompt.

Do not run model scoring on the login node. The login node is only for setup, file movement, and submitting jobs.

## Step 2 - Go To Scratch

```bash
cd /global/scratch/users/ezechinyereukabiala
```

## Step 3 - Clone Or Update The Repo

If the repo is not already there:

```bash
git clone https://github.com/Bababongo/p0-zero-shot-fitness.git
```

If it is already there:

```bash
cd /global/scratch/users/ezechinyereukabiala/p0-zero-shot-fitness
git pull
```

## Step 4 - Create The Conda Environment Once

```bash
module load anaconda3
mkdir -p /global/scratch/users/ezechinyereukabiala/conda_envs
conda create -y --prefix /global/scratch/users/ezechinyereukabiala/conda_envs/p0-zero-shot-fitness python=3.10
source activate /global/scratch/users/ezechinyereukabiala/conda_envs/p0-zero-shot-fitness
cd /global/scratch/users/ezechinyereukabiala/p0-zero-shot-fitness
python -m pip install --upgrade pip
python -m pip install -e ".[dev,esm]"
python -m pytest
```

## Step 5 - Submit The First Scientific Scaling Job

```bash
cd /global/scratch/users/ezechinyereukabiala/p0-zero-shot-fitness
sbatch hpc/savio_esm2_35m.slurm
```

This submits the 35M ESM-2 run. It is the first real scaling step beyond the local 8M result.

## Step 6 - Watch The Job

```bash
squeue -u ezechinyereukabiala
```

When it finishes, check logs:

```bash
ls -lh logs
tail -80 logs/p0-esm2-35m-*.out
tail -80 logs/p0-esm2-35m-*.err
```

## Step 7 - Check Outputs

```bash
ls -lh results/proteingym_blat_esm2_t12_35M
cat results/proteingym_blat_esm2_t12_35M/metrics.json
```

Expected files:

- `metrics.json`
- `scored_variants.csv`
- `fitness_scatter.svg`

## Step 8 - Compare Against Existing Runs

```bash
python scripts/compare_metrics.py \
  results/proteingym_blat_placeholder/metrics.json \
  results/proteingym_blat_esm2_t6_8M/metrics.json \
  results/proteingym_blat_esm2_t12_35M/metrics.json \
  --output results/proteingym_blat_esm2_scaling_comparison.json
```

Scientific interpretation:

- If 35M improves everywhere, the small model was underpowered.
- If 35M improves non-catalytic residues more than catalytic residues, that supports the idea that catalytic chemistry is a harder regime.
- If 35M improves catalytic and active-site-neighborhood residues, the model may be capturing useful evolutionary constraints around mechanism-relevant regions.
- One enzyme is not enough for a universal claim, but it is enough for a credible portfolio project and a clear next experiment.

