# HPC Runs

These scripts are templates for running larger ESM-2 models on a SLURM-style cluster such as LBNL/NERSC-like environments.

They intentionally avoid hard-coding account names, partitions, or module names. Edit the `#SBATCH` lines and environment setup to match the cluster you are using.

## Recommended Run Order

1. `esm2_35m.slurm`
2. `esm2_150m.slurm`
3. `esm2_650m.slurm`

Each job runs the same ProteinGym TEM-1 benchmark and writes outputs under `results/`.

## What To Edit

- `--account`
- `--partition`
- `--gres` or GPU resource request syntax
- module/conda setup
- repo path

## After Jobs Finish

Run:

```bash
python scripts/compare_metrics.py \
  results/proteingym_blat_esm2_t6_8M/metrics.json \
  results/proteingym_blat_esm2_t12_35M/metrics.json \
  results/proteingym_blat_esm2_t30_150M/metrics.json \
  results/proteingym_blat_esm2_t33_650M/metrics.json \
  --output results/proteingym_blat_esm2_scaling_comparison.json
```

Then update `docs/public_writeup.md` with the scaling table.
