# Social Post Draft

I built a small protein ML benchmark around a question I care about:

> Do protein language models fail differently on catalytic residues than on the rest of the protein?

First pass:

- Dataset: ProteinGym `BLAT_ECOLX_Firnberg_2014`
- Protein: TEM-1 beta-lactamase
- Variants: 4,783 single amino-acid substitutions
- Model: ESM-2 8M masked-marginal scoring
- Split: UniProt active-site positions, PDB 1M40 ligand contacts, active-site neighborhood, and the rest of the protein

Result:

```text
ESM-2 8M
Overall Spearman:        0.4113
UniProt active-site Spearman:      0.3023
Non-active-site Spearman:          0.4042
PDB ligand-contact Spearman:       0.6076
Outside ligand-contact Spearman:   0.3997
Active-site-neighborhood Spearman: 0.6453
Outside-neighborhood Spearman:     0.3752
Top-5 enrichment:        2.6237
```

With 1,000 bootstrap resamples:

```text
Overall 95% CI:        0.3846 to 0.4342
UniProt active-site 95% CI: 0.0478 to 0.5341
PDB ligand-contact 95% CI:  0.5274 to 0.6779
Active-neighborhood 95% CI: 0.5825 to 0.6994
```

This is not a final biological claim yet. The active-site-only subset is tiny, the ligand-contact group comes from one inhibitor-bound structure, and this is only one enzyme with the smallest ESM-2 model.

But the evaluation shape is the point: aggregate protein language model performance can hide behavior on mechanism-critical residue subsets.

Repo: https://github.com/Bababongo/p0-zero-shot-fitness

Next:

- run larger ESM-2 models on LBNL compute,
- add a ProteinMPNN structure-conditioned baseline,
- expand to more enzyme DMS assays.
