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

## Interpretation

The overall beta-glucosidase ESM-2 8M score is modest, but the structure-derived catalytic shell is much stronger than the outside background and higher than matched random residue-position controls.

The exact two-glutamate catalytic slice has only 12 measured variants, so it should not be overclaimed. The more defensible signal is the 5 A catalytic shell: a broader mechanism-adjacent region with enough variants to compare against matched controls.

This result makes P0 more interesting because beta-glucosidase behaves differently from AMIE. AMIE showed a useful raw active-site-neighborhood lift but stayed inside matched null controls. Beta-glucosidase shows a controlled 8M signal in the AF2 catalytic shell.

## Artifacts

- `results/proteingym_bgly_placeholder/metrics.json`
- `results/proteingym_bgly_esm2_t6_8M/metrics.json`
- `results/proteingym_bgly_placeholder_vs_esm2_t6_8M.json`
- `results/proteingym_four_enzyme_esm2_t6_8M_comparison.json`
- `hpc/savio_esm2_35m_bgly.slurm`

## Next Step

Run the Savio 35M beta-glucosidase job:

```bash
sbatch hpc/savio_esm2_35m_bgly.slurm
```

Then compare against the existing three-enzyme 35M panel.
