# Social Post Draft

I built a small protein ML benchmark around a question I care about:

> Do protein language models fail differently on catalytic residues than on the rest of the protein?

First pass:

- Dataset: ProteinGym `BLAT_ECOLX_Firnberg_2014`
- Protein: TEM-1 beta-lactamase
- Variants: 4,783 single amino-acid substitutions
- Model: ESM-2 8M masked-marginal scoring
- Split: catalytic positions, active-site motif neighborhood, and the rest of the protein

Result:

```text
ESM-2 8M
Overall Spearman:        0.4113
Catalytic Spearman:      0.6230
Non-catalytic Spearman:  0.3889
Active-site-neighborhood Spearman: 0.5949
Outside-neighborhood Spearman:     0.3785
Top-5 enrichment:        2.6237
```

With 1,000 bootstrap resamples:

```text
Overall 95% CI:        0.3846 to 0.4342
Catalytic 95% CI:      0.4219 to 0.7643
Non-catalytic 95% CI:  0.3643 to 0.4133
Active-neighborhood 95% CI: 0.5302 to 0.6564
```

This is not a final biological claim yet. The catalytic and active-site-neighborhood labels need structure/UniProt validation, and this is only one enzyme with the smallest ESM-2 model.

But the evaluation shape is the point: aggregate protein language model performance can hide behavior on mechanism-critical residue subsets.

Repo: https://github.com/Bababongo/p0-zero-shot-fitness

Next:

- validate catalytic labels,
- replace the motif-neighborhood group with structure-derived ligand-contact labels,
- run larger ESM-2 models on LBNL compute,
- expand to more enzyme DMS assays.
