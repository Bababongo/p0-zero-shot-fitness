# P0 - Zero-Shot Fitness

**Question:** Do protein language models fail differently on catalytic residues than on the rest of the protein?

This repo is a fixture-first benchmark scaffold for comparing zero-shot protein language model scores against enzyme deep mutational scanning data. The first version uses a tiny synthetic enzyme DMS fixture and a deterministic placeholder scorer so the full analysis pipeline works before downloading or running ESM.

Read the public-facing result writeup: [Do Protein Language Models Fail Differently On Catalytic Residues?](docs/public_writeup.md)

## Why This Matters

Protein language models can capture evolutionary and stability constraints, but enzyme function often depends on chemistry: catalytic residues, active-site geometry, cofactors, and transition-state stabilization. A model can rank generic damaging mutations well while still failing on the residues a protein engineer cares about most.

## What This Version Demonstrates

- mutation parsing and validation against a wild-type sequence,
- catalytic versus non-catalytic residue labeling,
- a swappable model-scoring interface,
- Spearman correlation overall and by residue group,
- top-k enrichment for experimentally high-fitness variants,
- mutation-class breakdown,
- reproducible CLI output and a simple SVG plot.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Run Tests

```bash
python -m pytest
```

## Run The Fixture Benchmark

```bash
p0-fitness --output-dir results
```

Or without installing the console script:

```bash
PYTHONPATH=src python -m p0_zero_shot_fitness.cli --output-dir results
```

Outputs:

- `results/metrics.json`
- `results/scored_variants.csv`
- `results/fitness_scatter.svg`

## Run The Real TEM-1 ProteinGym Benchmark

This repo includes the ProteinGym `BLAT_ECOLX_Firnberg_2014` processed assay file and metadata for TEM-1 beta-lactamase.

ProteinGym source: <https://github.com/OATML-Markslab/ProteinGym>

Placeholder scorer:

```bash
p0-fitness --preset proteingym-blat --output-dir results/proteingym_blat_placeholder
```

ESM-2 8M masked-marginal scorer:

```bash
python -m pip install -e ".[esm]"
p0-fitness --preset proteingym-blat --scorer esm2 --esm-model esm2_t6_8M_UR50D --output-dir results/proteingym_blat_esm2_t6_8M
```

Compare runs:

```bash
python scripts/compare_metrics.py \
  results/proteingym_blat_placeholder/metrics.json \
  results/proteingym_blat_esm2_t6_8M/metrics.json \
  --output results/proteingym_blat_comparison.json
```

First real result:

| Scorer | Overall Spearman | Catalytic Spearman | Non-catalytic Spearman | Top-5 Enrichment |
| --- | ---: | ---: | ---: | ---: |
| Placeholder | 0.0430 | 0.3922 | 0.0362 | 0.5247 |
| ESM-2 8M | 0.4113 | 0.6230 | 0.3889 | 2.6237 |

Active-site-neighborhood slice:

| Scorer | Active-site-neighborhood Spearman | Outside-neighborhood Spearman | Neighborhood Variants |
| --- | ---: | ---: | ---: |
| Placeholder | 0.3076 | 0.0249 | 480 |
| ESM-2 8M | 0.5949 | 0.3785 | 480 |

ESM-2 8M 95% bootstrap intervals from 1,000 resamples:

| Group | Spearman | 95% Bootstrap CI |
| --- | ---: | ---: |
| Overall | 0.4113 | 0.3846 to 0.4342 |
| Catalytic positions | 0.6230 | 0.4219 to 0.7643 |
| Non-catalytic positions | 0.3889 | 0.3643 to 0.4133 |
| Active-site neighborhood | 0.5949 | 0.5302 to 0.6564 |
| Outside active-site neighborhood | 0.3785 | 0.3510 to 0.4054 |

## Current Scope

The fixture version is intentionally offline and deterministic. The real TEM-1 ProteinGym run uses a processed public DMS assay and can run either with the placeholder scorer or with ESM-2.

## Next Scientific Steps

1. Validate catalytic residue labels from UniProt and structure annotations.
2. Replace the first-pass active-site-neighborhood labels with structure-derived ligand-contact labels.
3. Compare larger ESM-2 models, ESM-1v, and an MSA-based baseline.
4. Run the SLURM templates in `hpc/` on LBNL compute.
5. Expand from TEM-1 to a small enzyme panel.

## Portfolio Signal

This project is designed to show protein ML judgment: not just running a model, but asking whether model errors differ in chemically important regions of an enzyme.
