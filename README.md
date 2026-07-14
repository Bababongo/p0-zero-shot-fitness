# P0 - Zero-Shot Fitness

**Question:** Do protein language models fail differently on catalytic residues than on the rest of the protein?

This repo is a fixture-first benchmark scaffold for comparing zero-shot protein language model scores against enzyme deep mutational scanning data. It now includes real TEM-1, VIM-2, AMIE, and beta-glucosidase ProteinGym benchmarks, ESM-2 masked-marginal scoring, matched residue-position null controls, structure-derived mechanism slices, ligand-bound VIM-2 inhibitor-contact labels, and a validated enzyme-panel registry for expanding the question beyond one enzyme.

Read the public-facing result writeup: [Do Protein Language Models Fail Differently On Catalytic Residues?](docs/public_writeup.md)

Read the final report: [P0 Final Report - Mechanism-Sliced Zero-Shot Fitness](docs/p0_final_report.md)

Read the full project report: [P0 Extensive Project Report](docs/p0_extensive_project_report.md)

Read the portfolio card: [Mechanism-Sliced Zero-Shot Fitness](docs/p0_portfolio_card.md)

Read the v2 novelty upgrade: [Matched Residue-Position Null Controls](docs/p0_v2_novelty_upgrade.md)

Read the v3 enzyme-panel plan: [P0 Enzyme Panel Plan](docs/enzyme_panel_plan.md)

Read the first VIM-2 expansion note: [ProteinGym VIM-2 Result](docs/protein_gym_vim2_result.md)

Read the first AMIE expansion note: [ProteinGym AMIE Result](docs/protein_gym_amie_result.md)

Read the beta-glucosidase expansion note: [ProteinGym Beta-Glucosidase Result](docs/protein_gym_beta_glucosidase_result.md)

Read the three-enzyme comparison: [ProteinGym Three-Enzyme Comparison](docs/protein_gym_three_enzyme_comparison.md)

Read the four-enzyme 8M comparison: [ProteinGym Four-Enzyme ESM-2 8M Comparison](docs/protein_gym_four_enzyme_8m_comparison.md)

Read the four-enzyme 35M comparison: [ProteinGym Four-Enzyme ESM-2 35M Comparison](docs/protein_gym_four_enzyme_35m_comparison.md)

Read the pre-report control upgrade: [P0 Pre-Report Control Upgrade](docs/p0_pre_report_control_upgrade.md)

New to Python? Start with the [beginner code walkthrough](docs/code_walkthrough_for_beginners.md), then run `examples/beginner_walkthrough.py`.

## Why This Matters

Protein language models can capture evolutionary and stability constraints, but enzyme function often depends on chemistry: catalytic residues, active-site geometry, cofactors, and transition-state stabilization. A model can rank generic damaging mutations well while still failing on the residues a protein engineer cares about most.

## What This Version Demonstrates

- mutation parsing and validation against a wild-type sequence,
- UniProt-backed catalytic versus non-catalytic residue labeling,
- structure-derived ligand-contact residue grouping from PDB 1M40,
- ProteinGym AF2-derived VIM-2 metal-site shell grouping,
- RCSB 5ACX-derived VIM-2 WL3 inhibitor-contact grouping,
- ProteinGym AF2-derived AMIE catalytic-shell grouping,
- ProteinGym AF2-derived beta-glucosidase catalytic-shell grouping,
- a validated enzyme-panel registry for multi-enzyme follow-up,
- a swappable model-scoring interface,
- ESM-2 8M masked-marginal scoring across four enzymes,
- ESM-2 35M masked-marginal scoring across four enzymes,
- Spearman correlation overall and by residue group,
- top-k enrichment for experimentally high-fitness variants,
- mutation-class breakdown,
- matched residue-position null controls for mechanism-relevant residue slices,
- covariate-matched null controls for mutation coverage, fitness variance, model-score sensitivity, relative position, and structure contact density,
- approximate solvent-accessibility/SASA controls for structure-aware matched null tests,
- a true MSA conservation baseline across the four-enzyme panel,
- conservation-plus-SASA matched controls for mechanism-slice interpretation,
- a placeholder-vs-ESM-2 baseline comparison across the four-enzyme panel,
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

## Run The VIM-2 ProteinGym Benchmark

This repo now includes the ProteinGym `A4GRB6_PSEAI_Chen_2020` processed assay file and metadata for VIM-2 metallo-beta-lactamase.

Materialize a ProteinGym dataset from the public substitutions archive:

```bash
python scripts/materialize_proteingym_dataset.py \
  --dms-id A4GRB6_PSEAI_Chen_2020 \
  --archive-path /tmp/DMS_ProteinGym_substitutions.zip
```

Run the VIM-2 placeholder baseline:

```bash
p0-fitness \
  --preset proteingym-vim2 \
  --output-dir results/proteingym_vim2_placeholder \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

VIM-2 placeholder result:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.0194 | - | 5,004 |
| Curated metal-binding site | 0.1214 | 0.0045 | 113 |
| 5ACX WL3 inhibitor contact, 5 A | 0.3257 | 0.0022 | 247 |
| Active-site neighborhood | 0.2003 | -0.0006 | 448 |

The placeholder scorer is not the scientific model result. Its job is to prove the second-enzyme data path, labels, metrics, bootstrap intervals, and matched-position null controls before spending ESM compute.

Run the VIM-2 ESM-2 8M baseline:

```bash
p0-fitness \
  --preset proteingym-vim2 \
  --scorer esm2 \
  --esm-model esm2_t6_8M_UR50D \
  --output-dir results/proteingym_vim2_esm2_t6_8M \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

VIM-2 ESM-2 8M result:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.4305 | - | 5,004 |
| Curated metal-binding site | 0.3702 | 0.4123 | 113 |
| 5ACX WL3 inhibitor contact, 5 A | 0.4841 | 0.4316 | 247 |
| AF2 structure metal-site shell, 5 A | 0.5734 | 0.3843 | 802 |
| Active-site neighborhood | 0.6128 | 0.3936 | 448 |

The AF2 structure metal-site shell is higher than same-size random residue-position controls for ESM-2 8M: observed Spearman `0.5734`, null 95% interval `0.2323 to 0.5188`, empirical p = `0.000`.

The active-site-neighborhood slice is higher than same-size random residue-position controls for ESM-2 8M: observed Spearman `0.6128`, null 95% interval `0.1787 to 0.5736`, empirical p = `0.012`.

VIM-2 ESM-2 35M result:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.5280 | - | 5,004 |
| Curated metal-binding site | 0.3449 | 0.5085 | 113 |
| 5ACX WL3 inhibitor contact, 5 A | 0.6613 | 0.5207 | 247 |
| AF2 structure metal-site shell, 5 A | 0.5846 | 0.4778 | 802 |
| Active-site neighborhood | 0.6133 | 0.4897 | 448 |

The 35M model improves VIM-2 overall performance. The ligand-bound 5ACX/WL3 contact group is the strongest raw VIM-2 mechanism slice, but it still falls inside the conservation-plus-SASA matched null. That makes the project more careful: raw mechanism-slice lifts need matched controls before they become biological claims.

## Run The AMIE ProteinGym Benchmark

This repo now includes the ProteinGym `AMIE_PSEAE_Wrenbeck_2017` processed assay file and metadata for AMIE aliphatic amidase.

- `data/proteingym/AMIE_PSEAE_Wrenbeck_2017.csv`
- `data/proteingym/AMIE_PSEAE.fasta`
- `data/proteingym/AMIE_PSEAE_Wrenbeck_2017_metadata.json`
- `data/proteingym/AMIE_PSEAE_catalytic_residues.json`
- `data/proteingym/AMIE_PSEAE_residue_groups.json`
- `data/proteingym/structures/AMIE_PSEAE.pdb`

AMIE uses a UniProt-backed Cys-Glu-Lys catalytic triad annotation, with local AF2 structure-shell support:

```text
[59, 134, 166]
```

UniProtKB/Swiss-Prot P11436 directly annotates Glu59, Lys134, and Cys166 as active-site residues. The source record is `data/proteingym/source_records/uniprot_P11436_AMIE_PSEAE_active_site.json`.

Run the AMIE placeholder baseline:

```bash
p0-fitness \
  --preset proteingym-amie \
  --output-dir results/proteingym_amie_placeholder \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

Run the AMIE ESM-2 8M baseline:

```bash
p0-fitness \
  --preset proteingym-amie \
  --scorer esm2 \
  --esm-model esm2_t6_8M_UR50D \
  --output-dir results/proteingym_amie_esm2_t6_8M \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

AMIE ESM-2 8M result:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.3264 | - | 6,227 |
| Curated catalytic site | 0.2057 | 0.3157 | 57 |
| AF2 catalytic shell, 5 A | 0.2630 | 0.3152 | 621 |
| Active-site neighborhood | 0.4092 | 0.3017 | 259 |

The AMIE active-site neighborhood is stronger than the outside background, but remains inside the same-size matched-position null interval for ESM-2 8M. This makes AMIE an important counterexample: the mechanism-neighborhood signal is not automatically significant in every enzyme.

AMIE ESM-2 35M result:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.4082 | - | 6,227 |
| Curated catalytic site | 0.0911 | 0.3991 | 57 |
| AF2 catalytic shell, 5 A | 0.3071 | 0.4069 | 621 |
| Active-site neighborhood | 0.4335 | 0.3902 | 259 |

The 35M model improves AMIE overall performance, but the exact catalytic site remains weak and all AMIE mechanism slices remain inside matched-position null intervals.

## Run The Beta-Glucosidase ProteinGym Benchmark

This repo now includes the ProteinGym `Q59976_STRSQ_Romero_2015` processed assay file and metadata for beta-glucosidase.

- `data/proteingym/Q59976_STRSQ_Romero_2015.csv`
- `data/proteingym/Q59976_STRSQ.fasta`
- `data/proteingym/Q59976_STRSQ_Romero_2015_metadata.json`
- `data/proteingym/Q59976_STRSQ_catalytic_residues.json`
- `data/proteingym/Q59976_STRSQ_residue_groups.json`
- `data/proteingym/structures/Q59976_STRSQ.pdb`

Beta-glucosidase uses a conservative GH1 motif annotation:

```text
[178, 383]
```

These positions correspond to a general acid/base glutamate in the `NEP` motif and a catalytic nucleophile glutamate in the `ITENG` motif, mapped onto the exact ProteinGym target sequence.

Run the beta-glucosidase placeholder baseline:

```bash
p0-fitness \
  --preset proteingym-bgly \
  --output-dir results/proteingym_bgly_placeholder \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

Run the beta-glucosidase ESM-2 8M baseline:

```bash
p0-fitness \
  --preset proteingym-bgly \
  --scorer esm2 \
  --esm-model esm2_t6_8M_UR50D \
  --output-dir results/proteingym_bgly_esm2_t6_8M \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

Beta-glucosidase ESM-2 8M result:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.1442 | - | 2,999 |
| Curated catalytic site | 0.4196 | 0.1363 | 12 |
| AF2 catalytic shell, 5 A | 0.3712 | 0.1101 | 149 |
| Active-site neighborhood | 0.3595 | 0.1222 | 60 |

The beta-glucosidase AF2 catalytic shell is higher than same-size random residue-position controls for ESM-2 8M: observed Spearman `0.3712`, null 95% interval `-0.0969 to 0.3450`, empirical p = `0.018`.

Beta-glucosidase ESM-2 35M result:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.4481 | - | 2,999 |
| Curated catalytic site | 0.5105 | 0.4434 | 12 |
| AF2 catalytic shell, 5 A | 0.3808 | 0.4286 | 149 |
| Active-site neighborhood | 0.4327 | 0.4341 | 60 |

The beta-glucosidase 35M result is scientifically useful because it changes the 8M story. Scaling strongly improves global performance from `0.1442` to `0.4481`, but the AF2 catalytic shell no longer clears matched random residue-position controls: observed Spearman `0.3808`, null 95% interval `0.2042 to 0.6283`, empirical p = `0.654`.

The exact two-residue catalytic site has only 12 measured variants, so it is useful as a biological label but too small to overclaim alone.

## Validate The Enzyme Panel Registry

The v3 upgrade expands P0 from one TEM-1 case study into a mechanism-stratified enzyme benchmark plan. The registry validator checks that candidate enzyme datasets match local ProteinGym metadata, estimates masked-marginal scoring cost, and recommends the first three datasets to add.

```bash
python scripts/validate_panel_registry.py
```

Output:

- `results/panel_registry_validation.json`

Current validation summary:

| Check | Result |
| --- | ---: |
| Candidate enzyme datasets | 17 |
| ProteinGym metadata matches | 17 |
| Ready for current P0 pipeline | 4 |
| Need local data and annotations | 13 |

Recommended next panel path:

1. `A4GRB6_PSEAI_Chen_2020` - VIM-2 beta-lactamase, active as the first second-enzyme case.
2. `AMIE_PSEAE_Wrenbeck_2017` - aliphatic amidase, active as the first non-beta-lactamase hydrolase case.
3. `Q59976_STRSQ_Romero_2015` - beta-glucosidase, now active as the second non-beta-lactamase enzyme-function case.

Four-enzyme ESM-2 8M comparison:

| Dataset | Enzyme | Overall | Exact Site | Background | Best Mechanism Slice |
| --- | --- | ---: | ---: | ---: | --- |
| `BLAT_ECOLX_Firnberg_2014` | TEM-1 beta-lactamase | 0.4113 | 0.3023 | 0.4042 | Active-site neighborhood, 0.6453 |
| `A4GRB6_PSEAI_Chen_2020` | VIM-2 metallo-beta-lactamase | 0.4305 | 0.3702 | 0.4123 | Active-site neighborhood, 0.6128 |
| `AMIE_PSEAE_Wrenbeck_2017` | AMIE aliphatic amidase | 0.3264 | 0.2057 | 0.3157 | Active-site neighborhood, 0.4092 |
| `Q59976_STRSQ_Romero_2015` | Beta-glucosidase | 0.1442 | 0.4196 | 0.1363 | AF2 catalytic shell, 0.3712 |

Four-enzyme ESM-2 35M comparison:

| Dataset | Enzyme | Overall | Exact Site | Background | Best Mechanism Slice |
| --- | --- | ---: | ---: | ---: | --- |
| `BLAT_ECOLX_Firnberg_2014` | TEM-1 beta-lactamase | 0.5548 | 0.4596 | 0.5428 | PDB ligand contact, 0.7127; active-site neighborhood, 0.7027 |
| `A4GRB6_PSEAI_Chen_2020` | VIM-2 metallo-beta-lactamase | 0.5280 | 0.3449 | 0.5085 | WL3 inhibitor contact, 0.6613; active-site neighborhood, 0.6133; metal shell, 0.5846 |
| `AMIE_PSEAE_Wrenbeck_2017` | AMIE aliphatic amidase | 0.4082 | 0.0911 | 0.3991 | Active-site neighborhood, 0.4335 |
| `Q59976_STRSQ_Romero_2015` | Beta-glucosidase | 0.4481 | 0.5105 | 0.4434 | Active-site neighborhood, 0.4327; AF2 catalytic shell, 0.3808 |

35M scaling improves global zero-shot performance across the panel. The careful residue-zone interpretation is narrower: TEM-1 active-site neighborhood remains higher than matched-position null controls; VIM-2, AMIE, and beta-glucosidase mechanism slices are useful raw signals but inside matched null intervals at 35M.

Four-enzyme MSA conservation baseline:

| Dataset | Enzyme | MSA Overall | MSA Exact Site | MSA Background | ESM-2 35M Overall |
| --- | --- | ---: | ---: | ---: | ---: |
| `BLAT_ECOLX_Firnberg_2014` | TEM-1 beta-lactamase | 0.4247 | 0.4824 | 0.4114 | 0.5548 |
| `A4GRB6_PSEAI_Chen_2020` | VIM-2 metallo-beta-lactamase | 0.4931 | 0.3079 | 0.4724 | 0.5280 |
| `AMIE_PSEAE_Wrenbeck_2017` | AMIE aliphatic amidase | 0.4306 | 0.2944 | 0.4217 | 0.4082 |
| `Q59976_STRSQ_Romero_2015` | Beta-glucosidase | 0.5615 | 0.4406 | 0.5585 | 0.4481 |

The MSA baseline makes the result more intellectually honest: ESM-2 35M is stronger overall for TEM-1 and slightly stronger for VIM-2, but family-specific conservation is stronger overall for AMIE and beta-glucosidase.

Four-enzyme conservation-plus-SASA matched control:

| Dataset | Slice | Observed Spearman | Conservation+SASA Null 95% Interval | Empirical p | Read |
| --- | --- | ---: | ---: | ---: | --- |
| TEM-1 | Active-site neighborhood | 0.7027 | 0.4481 to 0.7133 | 0.094 | High, but inside strict conservation+SASA control |
| VIM-2 | Metal-site shell, 5 A | 0.5846 | 0.3734 to 0.6016 | 0.110 | Suggestive, but inside strict conservation+SASA control |
| VIM-2 | 5ACX WL3 inhibitor contact, 5 A | 0.6613 | 0.3873 to 0.7863 | 0.876 | Strong raw pocket signal, but inside strict conservation+SASA control |
| AMIE | Catalytic shell, 5 A | 0.3071 | 0.3496 to 0.5602 | 0.004 | Lower than matched conservation+SASA control |
| Beta-glucosidase | Catalytic shell, 5 A | 0.3808 | 0.3407 to 0.6218 | 0.166 | Inside strict conservation+SASA control |

This is the strongest control so far. It says the raw mechanism-slice lifts are not enough by themselves: after matching on family conservation and structural exposure, no 35M mechanism slice cleanly clears the null interval. That narrows the final claim from "ESM-2 understands catalytic regions" to "ESM-2 global signal is real, while mechanism-local signal is enzyme-specific and often explainable by conservation/exposure."

## Current Scope

The fixture version is intentionally offline and deterministic. The real ProteinGym runs now cover TEM-1 beta-lactamase, VIM-2 metallo-beta-lactamase, AMIE aliphatic amidase, and beta-glucosidase. All four enzymes have ESM-2 8M, ESM-2 35M, MSA conservation baselines, and conservation-plus-SASA matched controls. TEM-1 and AMIE have UniProt-backed catalytic labels. VIM-2 has reference-record and PDB-backed metal-site provenance plus an experimental 5ACX/WL3 ligand-contact group, with a transparent caveat that the original A4GRB6 UniProt accession is inactive/deleted.

## Next Scientific Steps

1. Add an explicit ESM-2-vs-MSA interpretation figure.
2. Run the ProteinMPNN structure-conditioned baseline using `docs/protein_mpnn_structure_baseline_plan.md`.
3. Add MSA Transformer only if the ProteinMPNN result leaves a model-family ambiguity worth resolving.
4. Add prospective validation on a new enzyme-design target.
5. Turn the four-enzyme result into a clean methods card.

## Portfolio Signal

This project is designed to show protein ML judgment: not just running a model, but asking whether model errors differ in chemically important regions of an enzyme.
