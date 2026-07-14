# HPC Runs

These scripts are templates for running larger ESM-2 models on a SLURM-style cluster such as LBNL/NERSC-like environments.

They intentionally avoid hard-coding account names, partitions, or module names. Edit the `#SBATCH` lines and environment setup to match the cluster you are using.

## Recommended Run Order

On Savio, start with:

1. `savio_esm2_35m.slurm`
2. `savio_esm2_35m_vim2.slurm`
3. `savio_esm2_35m_amie.slurm`
4. `savio_esm2_35m_bgly.slurm`

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
| `savio_esm2_35m_bgly.slurm` | Beta-glucosidase / `proteingym-bgly` | `results/proteingym_bgly_esm2_t12_35M` |

Each job writes metrics, scored variants, and a scatter plot under `results/`.

## What To Edit

- `--account`
- `--partition`
- `--gres` or GPU resource request syntax
- module/conda setup
- repo path

For the concrete Savio workflow, see `SAVIO.md`.

For the ProteinMPNN structure-conditioned baseline, see `SAVIO_PROTEINMPNN.md`.

After ProteinMPNN profile JSON files are generated, score the three ready enzymes with:

```bash
sbatch hpc/savio_score_proteinmpnn_profiles.slurm
```

The profile-generation job is:

```bash
sbatch hpc/savio_generate_proteinmpnn_profiles.slurm
```

## After Jobs Finish

Run:

```bash
python scripts/compare_metrics.py \
  results/proteingym_blat_esm2_t12_35M/metrics.json \
  results/proteingym_vim2_esm2_t12_35M/metrics.json \
  results/proteingym_amie_esm2_t12_35M/metrics.json \
  --output results/proteingym_three_enzyme_esm2_t12_35M_comparison.json
```

The current completed panel includes beta-glucosidase, so the main comparison artifact is the four-enzyme 35M comparison:

```bash
python scripts/compare_metrics.py \
  results/proteingym_blat_esm2_t12_35M/metrics.json \
  results/proteingym_vim2_esm2_t12_35M/metrics.json \
  results/proteingym_amie_esm2_t12_35M/metrics.json \
  results/proteingym_bgly_esm2_t12_35M/metrics.json \
  --output results/proteingym_four_enzyme_esm2_t12_35M_comparison.json
```

Then update `docs/public_writeup.md`, `docs/protein_gym_four_enzyme_35m_comparison.md`, and the Obsidian P0 result notes.
