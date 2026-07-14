# Savio Runbook For P0

Scientific goal:

> Test whether ESM-2 performance changes across residue groups in TEM-1, VIM-2, AMIE, and beta-glucosidase, especially exact catalytic sites, structure-derived mechanism shells, and active-site neighborhoods.

Why Savio is needed:

- The local 8M ESM-2 run proves the pipeline works.
- The 35M Savio runs test whether the residue-zone pattern survives a stronger model across the enzyme panel.
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

## Step 5 - Submit The Scientific Scaling Jobs

```bash
cd /global/scratch/users/ezechinyereukabiala/p0-zero-shot-fitness
sbatch hpc/savio_esm2_35m.slurm
```

This submits the TEM-1 35M ESM-2 run.

The next jobs scale the newer enzyme-panel cases:

```bash
sbatch hpc/savio_esm2_35m_vim2.slurm
sbatch hpc/savio_esm2_35m_amie.slurm
sbatch hpc/savio_esm2_35m_bgly.slurm
```

These are the next real scaling steps beyond the local 8M VIM-2, AMIE, and beta-glucosidase results.

## Step 6 - Watch The Job

```bash
squeue -u ezechinyereukabiala
```

When it finishes, check logs:

```bash
ls -lh logs
tail -80 logs/p0-esm2-35m-*.out
tail -80 logs/p0-esm2-35m-*.err
tail -80 logs/p0-vim2-35m-*.out
tail -80 logs/p0-vim2-35m-*.err
tail -80 logs/p0-amie-35m-*.out
tail -80 logs/p0-amie-35m-*.err
tail -80 logs/p0-bgly-35m-*.out
tail -80 logs/p0-bgly-35m-*.err
```

## Step 7 - Check Outputs

```bash
ls -lh results/proteingym_blat_esm2_t12_35M
ls -lh results/proteingym_vim2_esm2_t12_35M
ls -lh results/proteingym_amie_esm2_t12_35M
ls -lh results/proteingym_bgly_esm2_t12_35M
```

Expected files:

- `metrics.json`
- `scored_variants.csv`
- `fitness_scatter.svg`

To inspect a result:

```bash
cat results/proteingym_vim2_esm2_t12_35M/metrics.json
cat results/proteingym_amie_esm2_t12_35M/metrics.json
cat results/proteingym_bgly_esm2_t12_35M/metrics.json
```

## Step 8 - Compare Across Enzymes

```bash
python scripts/compare_metrics.py \
  results/proteingym_blat_esm2_t12_35M/metrics.json \
  results/proteingym_vim2_esm2_t12_35M/metrics.json \
  results/proteingym_amie_esm2_t12_35M/metrics.json \
  --output results/proteingym_three_enzyme_esm2_t12_35M_comparison.json
```

After beta-glucosidase finishes:

```bash
python scripts/compare_metrics.py \
  results/proteingym_blat_esm2_t12_35M/metrics.json \
  results/proteingym_vim2_esm2_t12_35M/metrics.json \
  results/proteingym_amie_esm2_t12_35M/metrics.json \
  results/proteingym_bgly_esm2_t12_35M/metrics.json \
  --output results/proteingym_four_enzyme_esm2_t12_35M_comparison.json
```

Scientific interpretation:

- If 35M improves all three enzymes, the 8M model was underpowered.
- If VIM-2 stays strong in the active-site neighborhood, the TEM-1/VIM-2 pattern becomes more convincing.
- If AMIE still stays inside matched-position null controls, it remains the useful counterexample.
- If AMIE becomes significant at 35M, model scale may recover a mechanism-neighborhood signal that 8M missed.
