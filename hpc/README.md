# HPC Runs

These scripts are templates for running larger ESM-2 models on a SLURM-style cluster such as LBNL/NERSC-like environments.

They intentionally avoid hard-coding account names, partitions, or module names. Edit the `#SBATCH` lines and environment setup to match the cluster you are using.

## Recommended Run Order

On Savio, start with:

1. `savio_esm2_35m.slurm`
2. `savio_esm2_35m_vim2.slurm`
3. `savio_esm2_35m_amie.slurm`

Generic templates for other SLURM-style clusters:

1. `esm2_35m.slurm`
2. `esm2_150m.slurm`
3. `esm2_650m.slurm`

The concrete Savio jobs run:

| Script | Dataset | Output |
| --- | --- | --- |
| `savio_esm2_35m.slurm` | TEM-1 / `proteingym-blat` | `results/proteingym_blat_esm2_t12_35M` |
| `savio_esm2_35m_vim2.slurm` | VIM-2 / `proteingym-vim2` | `results/proteingym_vim2_esm2_t12_35M` |
| `savio_esm2_35m_amie.slurm` | AMIE / `proteingym-amie` | `results/proteingym_amie_esm2_t12_35M` |

Each job writes metrics, scored variants, and a scatter plot under `results/`.

## What To Edit

- `--account`
- `--partition`
- `--gres` or GPU resource request syntax
- module/conda setup
- repo path

For the concrete Savio workflow, see `SAVIO.md`.

## After Jobs Finish

Run:

```bash
python scripts/compare_metrics.py \
  results/proteingym_blat_esm2_t12_35M/metrics.json \
  results/proteingym_vim2_esm2_t12_35M/metrics.json \
  results/proteingym_amie_esm2_t12_35M/metrics.json \
  --output results/proteingym_three_enzyme_esm2_t12_35M_comparison.json
```

Then update `docs/public_writeup.md` and `docs/protein_gym_three_enzyme_comparison.md` with the 35M three-enzyme table.
