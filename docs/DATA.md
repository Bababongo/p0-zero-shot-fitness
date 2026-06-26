# Data Notes

## ProteinGym TEM-1 Assay

This repository includes a processed ProteinGym substitution assay:

- `data/proteingym/BLAT_ECOLX_Firnberg_2014.csv`
- Dataset ID: `BLAT_ECOLX_Firnberg_2014`
- Protein: TEM-1 beta-lactamase (`BLAT_ECOLX`)
- Source: ProteinGym DMS substitutions benchmark
- Source repository: <https://github.com/OATML-Markslab/ProteinGym>
- Data archive: <https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/DMS_ProteinGym_substitutions.zip>

The assay file is used here as a portfolio benchmark for zero-shot variant-effect prediction. The repository also includes a local metadata file and catalytic-residue annotation file so the analysis can run reproducibly.

## Catalytic Residue Labels

The first-pass catalytic set is:

```text
[68, 71, 128, 166, 232]
```

These positions are mapped onto the 286-aa ProteinGym target sequence using TEM-family active-site motifs. They should be validated against external UniProt and structural annotations before treating the result as publication-grade.

## Model Outputs

The `results/` directory contains reproducible benchmark outputs from:

- placeholder conservation scorer,
- ESM-2 8M masked-marginal scorer.

ESM model weights are not stored in this repository.
