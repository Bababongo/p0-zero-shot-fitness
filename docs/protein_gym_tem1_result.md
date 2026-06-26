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

## Catalytic Residue Labels

Catalytic/active-site labels were mapped onto the 286-aa ProteinGym target sequence using TEM-family motifs:

- `SXXK`: target positions 68 and 71
- `SDN`: target positions 128 and 130, with position 128 included in the first-pass catalytic set
- `E166`: target position 166
- `KSG`: target position 232

The current catalytic set is `[68, 71, 128, 166, 232]`. This is a credible first-pass mapping, but it should be validated against UniProt features and a structure before publication.

## Models Compared

- Placeholder conservation scorer: deterministic pipeline sanity check
- ESM-2 8M masked-marginal scorer: real protein language model zero-shot baseline
- ESM implementation: <https://github.com/facebookresearch/esm>

## Result

| Scorer | Overall Spearman | Catalytic Spearman | Non-catalytic Spearman | Top-5 Enrichment |
| --- | ---: | ---: | ---: | ---: |
| Placeholder | 0.0430 | 0.3922 | 0.0362 | 0.5247 |
| ESM-2 8M | 0.4113 | 0.6230 | 0.3889 | 2.6237 |

ESM-2 8M bootstrap intervals from 1,000 resamples:

| Group | Spearman | 95% Bootstrap CI |
| --- | ---: | ---: |
| Overall | 0.4113 | 0.3846 to 0.4342 |
| Catalytic positions | 0.6230 | 0.4219 to 0.7643 |
| Non-catalytic positions | 0.3889 | 0.3643 to 0.4133 |

## Interpretation

ESM-2 8M is substantially better than the placeholder scorer on the real TEM-1 DMS assay. In this first pass, ESM-2 performs better on catalytic-position variants than on non-catalytic variants by Spearman correlation. That does not yet prove catalytic residues are easier in general; the catalytic subset is small and the labels need structural validation.

The useful portfolio signal is the evaluation shape: the benchmark can separate global performance from mechanism-relevant residue subsets and can expose whether a model's aggregate score hides a different failure mode near catalytic chemistry.

## Next Upgrade

Run the same benchmark with a larger ESM-2 model, validate catalytic residue numbering from external annotations, and add a binding-pocket residue group from structure-derived ligand contacts. SLURM templates for larger ESM-2 runs are in `hpc/`.
