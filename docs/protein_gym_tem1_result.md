# First Real P0 Result: TEM-1 Beta-Lactamase

## Question

Do protein language models fail differently on catalytic residues than on the rest of the protein?

## Dataset

- Dataset: ProteinGym `BLAT_ECOLX_Firnberg_2014`
- Protein: TEM-1 beta-lactamase (`BLAT_ECOLX`)
- Assay: growth under ampicillin selection
- Variants analyzed: 4,783 single amino-acid substitutions
- Fitness column: ProteinGym `DMS_score`, where higher is better
- ProteinGym repository: <https://github.com/OATML-Markslab/ProteinGym>
- ProteinGym benchmark paper: <https://proceedings.neurips.cc/paper_files/paper/2023/file/cac723e5ff29f65e3fcbb0739ae91bee-Paper-Datasets_and_Benchmarks.pdf>
- ProteinGym data archive used: <https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/DMS_ProteinGym_substitutions.zip>

## Residue Labels

The catalytic labels are now validated against UniProt P62593 (`BLAT_ECOLX`) natural sequence numbering:

- Active site: positions 68, 71, 128, and 164
- Substrate binding site: positions 232-234

UniProt notes that class-A beta-lactamase papers often use Ambler numbering. In that convention, the same catalytic motifs are commonly discussed as Ser70, Lys73, Ser130, Glu166, and Lys234. The ProteinGym/UniProt target sequence uses natural 286-aa sequence numbering, so the labels above are the ones used in metrics.

I also added two larger mechanism-relevant groups:

- `active_site_neighborhood`: a +/-2 residue window around UniProt-supported active-site and substrate-binding positions.
- `structure_ligand_contact_5a`: residues with any heavy atom within 5.0 Angstrom of the `CB4` inhibitor in PDB 1M40 chain A, mapped to ProteinGym numbering with a -2 residue offset.

Source records are included in `data/proteingym/source_records/`, and the downloaded PDB is stored in `data/proteingym/structures/1M40.pdb`.

## Models Compared

- Placeholder conservation scorer: deterministic pipeline sanity check
- ESM-2 8M masked-marginal scorer: real protein language model zero-shot baseline
- ESM implementation: <https://github.com/facebookresearch/esm>

## Result

| Scorer | Overall Spearman | UniProt active-site Spearman | Non-active-site Spearman | Top-5 Enrichment |
| --- | ---: | ---: | ---: | ---: |
| Placeholder | 0.0430 | 0.1231 | 0.0342 | 0.5247 |
| ESM-2 8M | 0.4113 | 0.3023 | 0.4042 | 2.6237 |

Mechanism-relevant residue slices:

| Scorer | Group | Spearman | Outside-group Spearman | Variants |
| --- | --- | ---: | ---: | ---: |
| Placeholder | UniProt active site | 0.1231 | 0.0342 | 57 |
| Placeholder | UniProt substrate-binding site | -0.0350 | 0.0368 | 55 |
| Placeholder | PDB 1M40 ligand contact, 5 A | 0.1777 | 0.0361 | 277 |
| Placeholder | Active-site neighborhood | 0.2916 | 0.0278 | 461 |
| ESM-2 8M | UniProt active site | 0.3023 | 0.4042 | 57 |
| ESM-2 8M | UniProt substrate-binding site | 0.4383 | 0.3992 | 55 |
| ESM-2 8M | PDB 1M40 ligand contact, 5 A | 0.6076 | 0.3997 | 277 |
| ESM-2 8M | Active-site neighborhood | 0.6453 | 0.3752 | 461 |

ESM-2 8M bootstrap intervals from 1,000 resamples:

| Group | Spearman | 95% Bootstrap CI |
| --- | ---: | ---: |
| Overall | 0.4113 | 0.3846 to 0.4342 |
| UniProt active-site positions | 0.3023 | 0.0478 to 0.5341 |
| Non-active-site positions | 0.4042 | 0.3783 to 0.4278 |
| UniProt substrate-binding site | 0.4383 | 0.1569 to 0.6699 |
| PDB 1M40 ligand-contact positions | 0.6076 | 0.5274 to 0.6779 |
| Outside ligand-contact positions | 0.3997 | 0.3755 to 0.4224 |
| Active-site neighborhood | 0.6453 | 0.5825 to 0.6994 |
| Outside active-site neighborhood | 0.3752 | 0.3497 to 0.4006 |

## Interpretation

ESM-2 8M is substantially better than the placeholder scorer overall on the real TEM-1 DMS assay.

The corrected UniProt active-site-only subset is very small: 57 variants across four positions. ESM-2 is positive there, but lower than its non-active-site correlation, and the confidence interval is wide. That is an important correction to the earlier motif-only readout.

The stronger signal appears in chemistry-adjacent regions with more variants. ESM-2 performs much better in the PDB 1M40 ligand-contact group and in the active-site neighborhood than outside those groups. That suggests the model captures constraints around the active-site environment better than a tiny catalytic-residue-only slice would imply.

The useful portfolio signal is the evaluation shape: the benchmark separates global performance from UniProt features, substrate-binding features, and structure-derived ligand-contact residue groups.

## Next Upgrade

Run larger ESM-2 or ESM-1v models on LBNL compute and repeat this same validated residue-slice analysis. SLURM templates for larger ESM-2 runs are in `hpc/`.
