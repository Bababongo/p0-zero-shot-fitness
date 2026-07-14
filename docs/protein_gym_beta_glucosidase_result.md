# ProteinGym Beta-Glucosidase Result

## Purpose

Beta-glucosidase is the fourth P0 enzyme and the second non-beta-lactamase enzyme-function case. It tests whether the mechanism-slice story still holds in a glycoside hydrolase, not only in beta-lactamases or amidases.

## Dataset

- ProteinGym dataset: `Q59976_STRSQ_Romero_2015`
- Protein: beta-glucosidase
- Family: GH1 glycoside hydrolase
- Assay: microfluidic enzyme-function enrichment
- Variants: 2,999 single amino-acid substitutions
- Fitness target: ProteinGym `DMS_score`
- Sequence length: 501 aa

Local files:

- `data/proteingym/Q59976_STRSQ_Romero_2015.csv`
- `data/proteingym/Q59976_STRSQ.fasta`
- `data/proteingym/Q59976_STRSQ_Romero_2015_metadata.json`
- `data/proteingym/Q59976_STRSQ_catalytic_residues.json`
- `data/proteingym/Q59976_STRSQ_residue_groups.json`
- `data/proteingym/structures/Q59976_STRSQ.pdb`

## Residue Labels

GH1 beta-glycosidases are retaining enzymes with known catalytic glutamates. CAZypedia describes a general acid/base glutamate in a typical `NEP` sequence and a nucleophile glutamate in a `YITENG`-like motif.

Mapped onto the ProteinGym Q59976_STRSQ target sequence:

| Role | Motif | Position |
| --- | --- | ---: |
| General acid/base candidate | `LNEP` | Glu178 |
| Catalytic nucleophile candidate | `VITENG` | Glu383 |

Residue groups:

| Group | Definition | Variants |
| --- | --- | ---: |
| `curated_catalytic_site` | Exact Glu178/Glu383 mutations | 12 |
| `active_site_neighborhood` | +/-2 residue windows around Glu178/Glu383 | 60 |
| `structure_catalytic_shell_5a` | AF2 residues within 5 A of either catalytic Glu | 149 |

## Placeholder Result

The placeholder scorer is a plumbing baseline, not a scientific model.

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.0443 | - | 2,999 |
| Curated catalytic site | 0.0000 | 0.0422 | 12 |
| Active-site neighborhood | 0.3362 | 0.0395 | 60 |
| AF2 catalytic shell, 5 A | 0.2008 | 0.0382 | 149 |

## ESM-2 8M Result

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.1442 | - | 2,999 |
| Curated catalytic site | 0.4196 | 0.1363 | 12 |
| Active-site neighborhood | 0.3595 | 0.1222 | 60 |
| AF2 catalytic shell, 5 A | 0.3712 | 0.1101 | 149 |

Matched-position null read:

| Slice | Observed Spearman | Null 95% Interval | Empirical p | Read |
| --- | ---: | ---: | ---: | --- |
| Curated catalytic site | 0.4196 | -0.6025 to 0.8187 | 0.548 | Inside null |
| Active-site neighborhood | 0.3595 | -0.2463 to 0.4796 | 0.210 | Inside null |
| AF2 catalytic shell, 5 A | 0.3712 | -0.0969 to 0.3450 | 0.018 | Higher than matched null |

## ESM-2 35M Result

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.4481 | - | 2,999 |
| Curated catalytic site | 0.5105 | 0.4434 | 12 |
| Active-site neighborhood | 0.4327 | 0.4341 | 60 |
| AF2 catalytic shell, 5 A | 0.3808 | 0.4286 | 149 |

Matched-position null read:

| Slice | Observed Spearman | Null 95% Interval | Empirical p | Read |
| --- | ---: | ---: | ---: | --- |
| Curated catalytic site | 0.5105 | -0.4056 to 0.8419 | 0.772 | Inside null |
| Active-site neighborhood | 0.4327 | 0.0794 to 0.7030 | 0.984 | Inside null |
| AF2 catalytic shell, 5 A | 0.3808 | 0.2042 to 0.6283 | 0.654 | Inside null |

## Interpretation

The beta-glucosidase scaling result is a useful correction to the first 8M read.

At 8M, the overall score is modest, but the structure-derived catalytic shell is much stronger than the outside background and higher than matched random residue-position controls.

At 35M, the overall score improves sharply from `0.1442` to `0.4481`. However, the mechanism-slice result becomes more conservative: the AF2 catalytic shell, active-site neighborhood, and exact catalytic site all fall inside matched random residue-position controls.

The exact two-glutamate catalytic slice has only 12 measured variants, so it should not be overclaimed. The more defensible signal is the 5 A catalytic shell: a broader mechanism-adjacent region with enough variants to compare against matched controls.

This result makes P0 more interesting because beta-glucosidase behaves differently across scale. It shows that a mechanism-slice signal can appear at 8M but fail to persist at 35M once global model quality improves. The mature interpretation is not "beta-glucosidase catalytic shell is special." It is:

> Scale improves global zero-shot fitness prediction, but mechanism-slice effects are enzyme- and model-size-dependent.

## Artifacts

- `results/proteingym_bgly_placeholder/metrics.json`
- `results/proteingym_bgly_esm2_t6_8M/metrics.json`
- `results/proteingym_bgly_esm2_t12_35M/metrics.json`
- `results/proteingym_bgly_placeholder_vs_esm2_t6_8M.json`
- `results/proteingym_four_enzyme_esm2_t6_8M_comparison.json`
- `results/proteingym_four_enzyme_esm2_t12_35M_comparison.json`
- `hpc/savio_esm2_35m_bgly.slurm`

## Next Step

Use this as the fourth-enzyme counterexample in the P0 panel, then add conservation-matched and solvent-accessibility-matched controls before making broader claims about mechanism-adjacent regions.
