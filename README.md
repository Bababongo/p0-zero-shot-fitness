# P0 - Zero-Shot Fitness

**Question:** Do protein language models fail differently on catalytic residues than on the rest of the protein?

This repo is a fixture-first benchmark scaffold for comparing zero-shot protein language model scores against enzyme deep mutational scanning data. The first version uses a tiny synthetic enzyme DMS fixture and a deterministic placeholder scorer so the full analysis pipeline works before downloading or running ESM.

Read the public-facing result writeup: [Do Protein Language Models Fail Differently On Catalytic Residues?](docs/public_writeup.md)

Read the full project report: [P0 Extensive Project Report](docs/p0_extensive_project_report.md)

Read the v2 novelty upgrade: [Matched Residue-Position Null Controls](docs/p0_v2_novelty_upgrade.md)

Read the v3 enzyme-panel plan: [P0 Enzyme Panel Plan](docs/enzyme_panel_plan.md)

New to Python? Start with the [beginner code walkthrough](docs/code_walkthrough_for_beginners.md), then run `examples/beginner_walkthrough.py`.

## Why This Matters

Protein language models can capture evolutionary and stability constraints, but enzyme function often depends on chemistry: catalytic residues, active-site geometry, cofactors, and transition-state stabilization. A model can rank generic damaging mutations well while still failing on the residues a protein engineer cares about most.

## What This Version Demonstrates

- mutation parsing and validation against a wild-type sequence,
- UniProt-backed catalytic versus non-catalytic residue labeling,
- structure-derived ligand-contact residue grouping from PDB 1M40,
- a swappable model-scoring interface,
- Spearman correlation overall and by residue group,
- top-k enrichment for experimentally high-fitness variants,
- mutation-class breakdown,
- matched residue-position null controls for mechanism-relevant residue slices,
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

Add matched residue-position null controls:

```bash
p0-fitness --preset proteingym-blat --null-iterations 1000 --output-dir results/proteingym_blat_placeholder_null
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
| Placeholder | 0.0430 | 0.1231 | 0.0342 | 0.5247 |
| ESM-2 8M | 0.4113 | 0.3023 | 0.4042 | 2.6237 |

Mechanism-relevant residue slices:

| Scorer | Group | Spearman | Outside-group Spearman | Variants |
| --- | --- | ---: | ---: | ---: |
| Placeholder | UniProt active site | 0.1231 | 0.0342 | 57 |
| Placeholder | PDB 1M40 ligand contact, 5 A | 0.1777 | 0.0361 | 277 |
| Placeholder | Active-site neighborhood | 0.2916 | 0.0278 | 461 |
| ESM-2 8M | UniProt active site | 0.3023 | 0.4042 | 57 |
| ESM-2 8M | PDB 1M40 ligand contact, 5 A | 0.6076 | 0.3997 | 277 |
| ESM-2 8M | Active-site neighborhood | 0.6453 | 0.3752 | 461 |

ESM-2 8M 95% bootstrap intervals from 1,000 resamples:

| Group | Spearman | 95% Bootstrap CI |
| --- | ---: | ---: |
| Overall | 0.4113 | 0.3846 to 0.4342 |
| UniProt active-site positions | 0.3023 | 0.0478 to 0.5341 |
| Non-active-site positions | 0.4042 | 0.3783 to 0.4278 |
| PDB 1M40 ligand-contact positions | 0.6076 | 0.5274 to 0.6779 |
| Outside ligand-contact positions | 0.3997 | 0.3755 to 0.4224 |
| Active-site neighborhood | 0.6453 | 0.5825 to 0.6994 |
| Outside active-site neighborhood | 0.3752 | 0.3497 to 0.4006 |

## Current Scope

The fixture version is intentionally offline and deterministic. The real TEM-1 ProteinGym run uses a processed public DMS assay and can run either with the placeholder scorer or with ESM-2.

## Next Scientific Steps

1. Validate the enzyme-panel registry in `data/panels/p0_enzyme_panel_candidates.csv`.
2. Add VIM-2 beta-lactamase, SARS-CoV-2 Mpro, and aliphatic amidase as the first panel expansion.
3. Add conservation-matched and solvent-accessibility-matched null controls.
4. Compare larger ESM-2 models, ESM-1v, MSA Transformer, and a conservation baseline.
5. Add more structures or ligands to test contact-label robustness.

## Portfolio Signal

This project is designed to show protein ML judgment: not just running a model, but asking whether model errors differ in chemically important regions of an enzyme.
