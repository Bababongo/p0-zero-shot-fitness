# Do Protein Language Models Fail Differently On Catalytic Residues?

## Short Answer

In this first TEM-1 beta-lactamase benchmark, ESM-2 performs better than a simple placeholder baseline overall. After validating residue labels against UniProt and PDB 1M40, the active-site-only subset is small and noisy, while broader ligand-contact and active-site-neighborhood slices show a stronger ESM-2 signal.

The first local run used ESM-2 8M. I then ran ESM-2 35M on Savio as the first scaling check. The 35M model improved overall and residue-slice performance, but the UniProt active-site-only subset still remained lower than the non-active-site background.

I later added a matched residue-position null control. That changed the most careful interpretation: the exact UniProt active-site-only slice is not unusual compared with same-size random position groups, but the broader active-site-neighborhood slice is higher than matched null controls for both ESM-2 8M and 35M.

## Why I Built This

Protein language models are often evaluated with broad variant-effect prediction metrics. That is useful, but enzymes are not just sequence objects. Enzyme fitness can depend on active-site chemistry, catalytic residues, cofactors, substrate positioning, and transition-state stabilization.

A model can look good overall while failing on the exact residues that matter most for protein engineering.

The question I wanted to make measurable was:

> Do protein language models fail differently on catalytic residues than on the rest of the protein?

## Dataset

I used ProteinGym's processed deep mutational scanning assay:

- Dataset: `BLAT_ECOLX_Firnberg_2014`
- Protein: TEM-1 beta-lactamase
- Assay: growth under ampicillin selection
- Variants: 4,783 single amino-acid substitutions
- Fitness target: ProteinGym `DMS_score`, where higher is better

ProteinGym source: <https://github.com/OATML-Markslab/ProteinGym>

## Model

The first real protein language model baselines are:

- ESM-2 8M: `esm2_t6_8M_UR50D`
- ESM-2 35M: `esm2_t12_35M_UR50D`, run on Savio job `35588401`
- Scoring method: masked-marginal log-likelihood ratio
- Comparison baseline: deterministic placeholder conservation scorer

The placeholder is not intended to be biologically meaningful. It exists as a sanity check for the benchmark pipeline.

## Residue Groups

I validated the TEM-1 labels against UniProt P62593 (`BLAT_ECOLX`). UniProt uses natural 286-aa sequence numbering, while many beta-lactamase papers use Ambler/class-A numbering.

| Feature | ProteinGym/UniProt Positions | Common Ambler Positions |
| --- | ---: | --- |
| Active site | 68, 71, 128, 164 | Ser70, Lys73, Ser130, Glu166 |
| Substrate binding | 232-234 | Lys234, Ser235, Gly236 |

Current UniProt active-site set:

```text
[68, 71, 128, 164]
```

This creates 57 active-site variants and 4,726 non-active-site variants in the DMS assay.

I also added two larger mechanism-relevant groups:

- `active_site_neighborhood`: a +/-2 residue window around UniProt-supported active-site and substrate-binding positions.
- `structure_ligand_contact_5a`: residues with any heavy atom within 5.0 Angstrom of the `CB4` inhibitor in PDB 1M40 chain A.

## Result

| Scorer | Overall Spearman | UniProt active-site Spearman | Non-active-site Spearman | Top-5 Enrichment |
| --- | ---: | ---: | ---: | ---: |
| Placeholder | 0.0430 | 0.1231 | 0.0342 | 0.5247 |
| ESM-2 8M | 0.4113 | 0.3023 | 0.4042 | 2.6237 |
| ESM-2 35M | 0.5548 | 0.4596 | 0.5428 | 2.0990 |

Mechanism-relevant residue slices:

| Scorer | Group | Spearman | Outside-group Spearman | Variants |
| --- | --- | ---: | ---: | ---: |
| Placeholder | UniProt active site | 0.1231 | 0.0342 | 57 |
| Placeholder | PDB 1M40 ligand contact, 5 A | 0.1777 | 0.0361 | 277 |
| Placeholder | Active-site neighborhood | 0.2916 | 0.0278 | 461 |
| ESM-2 8M | UniProt active site | 0.3023 | 0.4042 | 57 |
| ESM-2 8M | PDB 1M40 ligand contact, 5 A | 0.6076 | 0.3997 | 277 |
| ESM-2 8M | Active-site neighborhood | 0.6453 | 0.3752 | 461 |
| ESM-2 35M | UniProt active site | 0.4596 | 0.5428 | 57 |
| ESM-2 35M | PDB 1M40 ligand contact, 5 A | 0.7127 | 0.5344 | 277 |
| ESM-2 35M | Active-site neighborhood | 0.7027 | 0.5188 | 461 |

For the ESM-2 8M run, I also added 1,000 bootstrap resamples:

| Group | Spearman | 95% Bootstrap CI |
| --- | ---: | ---: |
| Overall | 0.4113 | 0.3846 to 0.4342 |
| UniProt active-site positions | 0.3023 | 0.0478 to 0.5341 |
| Non-active-site positions | 0.4042 | 0.3783 to 0.4278 |
| PDB 1M40 ligand-contact positions | 0.6076 | 0.5274 to 0.6779 |
| Outside ligand-contact positions | 0.3997 | 0.3755 to 0.4224 |
| Active-site neighborhood | 0.6453 | 0.5825 to 0.6994 |
| Outside active-site neighborhood | 0.3752 | 0.3497 to 0.4006 |

For the ESM-2 35M Savio run, I also computed 1,000 bootstrap resamples:

| Group | Spearman | 95% Bootstrap CI |
| --- | ---: | ---: |
| Overall | 0.5548 | 0.5340 to 0.5757 |
| UniProt active-site positions | 0.4596 | 0.2268 to 0.6418 |
| Non-active-site positions | 0.5428 | 0.5195 to 0.5641 |
| PDB 1M40 ligand-contact positions | 0.7127 | 0.6464 to 0.7695 |
| Outside ligand-contact positions | 0.5344 | 0.5125 to 0.5558 |
| Active-site neighborhood | 0.7027 | 0.6508 to 0.7503 |
| Outside active-site neighborhood | 0.5188 | 0.4944 to 0.5424 |

I also added 1,000 matched residue-position null samples for each mechanism-relevant slice:

| Model | Slice | Observed Spearman | Null Mean | Null 95% Interval | Empirical p | Direction |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| ESM-2 8M | UniProt active site | 0.3023 | 0.3912 | -0.1961 to 0.7948 | 0.680 | inside null |
| ESM-2 8M | PDB ligand contact, 5 A | 0.6076 | 0.3912 | 0.0964 to 0.6385 | 0.082 | inside null |
| ESM-2 8M | Active-site neighborhood | 0.6453 | 0.3726 | 0.1614 to 0.5519 | 0.002 | higher than null |
| ESM-2 35M | UniProt active site | 0.4596 | 0.5245 | 0.0273 to 0.8356 | 0.668 | inside null |
| ESM-2 35M | PDB ligand contact, 5 A | 0.7127 | 0.5303 | 0.2820 to 0.7227 | 0.070 | inside null |
| ESM-2 35M | Active-site neighborhood | 0.7027 | 0.5148 | 0.3188 to 0.6781 | 0.012 | higher than null |

## Interpretation

ESM-2 gives a much stronger zero-shot signal than the placeholder baseline on the TEM-1 assay, and the 35M model improves over the 8M model.

The most interesting observation changed after label validation. ESM-2 is not better on the tiny UniProt active-site-only subset than on the rest of the protein, even after scaling from 8M to 35M:

```text
ESM-2 8M active site:      0.3023
ESM-2 8M non-active-site:  0.4042
ESM-2 35M active site:     0.4596
ESM-2 35M non-active-site: 0.5428
```

But ESM-2 is much stronger on broader chemistry-adjacent slices, especially with the 35M model:

```text
ESM-2 35M ligand contact:          0.7127
ESM-2 35M outside ligand contact:  0.5344
ESM-2 35M active-site neighborhood: 0.7027
ESM-2 35M outside neighborhood:     0.5188
```

The matched null control makes the interpretation more honest. The exact active-site result should not be overclaimed; it is too small to distinguish clearly from same-size random position groups. The more interesting positive result is that the active-site-neighborhood slice is unusually strong relative to matched random controls.

This does not prove catalytic residues are generally easier for protein language models. A few caveats matter:

- The UniProt active-site subset has only 57 variants.
- The ligand-contact group comes from one inhibitor-bound structure.
- TEM-1 beta-lactamase is one enzyme, not a general enzyme benchmark.
- This is only the first scaling step, from ESM-2 8M to ESM-2 35M.
- DMS fitness reflects the assay context, not pure catalytic mechanism.

Still, this is the kind of eval slice I want more life-science AI systems to expose. Aggregate performance can hide the behavior that matters for mechanistic biology.

## What This Repo Demonstrates

This project is not just a notebook result. It is a small, reproducible benchmark scaffold:

- loads ProteinGym DMS data,
- validates mutation strings against the wild-type sequence,
- labels UniProt active-site and substrate-binding variants,
- labels structure-derived ligand-contact variants from PDB 1M40,
- labels active-site-neighborhood variants,
- adds matched residue-position null controls for mechanism-relevant slices,
- runs a swappable scorer interface,
- supports ESM-2 masked-marginal scoring,
- computes overall and subgroup Spearman correlations,
- reports bootstrap confidence intervals,
- writes scored variants, metrics, and SVG plots,
- includes tests and GitHub Actions CI.

## Next Experiments

1. Run ESM-2 150M as the next scaling step.
2. Add ESM-1v or an MSA-based baseline.
3. Repeat the benchmark across multiple enzyme DMS assays.
4. Add additional ligand-bound TEM-1 structures to test contact-label robustness.
5. Turn the result into a short portfolio figure and methods card.

## Why This Matters For AI Biology

For AI systems used in biology, the important question is not only "does the model perform well on average?"

It is also:

- where does the model fail?
- does it fail near chemistry?
- does it fail near binding?
- does it fail on the variants a scientist would prioritize?

This project is my first pass at turning that question into a measurable benchmark.
