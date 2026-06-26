# Do Protein Language Models Fail Differently On Catalytic Residues?

## Short Answer

In this first TEM-1 beta-lactamase benchmark, ESM-2 8M performs better than a simple placeholder baseline overall. It also performs better on mutations at catalytic positions and within a first-pass active-site motif neighborhood than on the rest of the protein.

That result is interesting, but not final. The catalytic subset is small, the labels are first-pass motif mappings, and this run uses the smallest ESM-2 model. The main contribution is the evaluation shape: separating aggregate protein language model performance from performance on chemically important residue subsets.

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

The first real protein language model baseline is:

- ESM-2 8M: `esm2_t6_8M_UR50D`
- Scoring method: masked-marginal log-likelihood ratio
- Comparison baseline: deterministic placeholder conservation scorer

The placeholder is not intended to be biologically meaningful. It exists as a sanity check for the benchmark pipeline.

## Catalytic Residue Group

I mapped TEM-family active-site motifs onto the 286-aa ProteinGym target sequence:

| Motif | Target Positions |
| --- | ---: |
| `SXXK` | 68, 71 |
| `SDN` | 128 |
| `E166` | 166 |
| `KSG` | 232 |

Current catalytic set:

```text
[68, 71, 128, 166, 232]
```

This creates 81 catalytic-position variants and 4,702 non-catalytic variants in the DMS assay.

This label set should be treated as first-pass. The next version should validate the positions against UniProt feature annotations and a structure-derived active site or ligand-contact map.

I also added an `active_site_neighborhood` group around these motif windows. This group contains 480 single-mutant assay rows. It is not a structure-derived binding pocket yet; it is a transparent motif-neighborhood slice that can later be replaced or compared against ligand-contact labels.

## Result

| Scorer | Overall Spearman | Catalytic Spearman | Non-catalytic Spearman | Top-5 Enrichment |
| --- | ---: | ---: | ---: | ---: |
| Placeholder | 0.0430 | 0.3922 | 0.0362 | 0.5247 |
| ESM-2 8M | 0.4113 | 0.6230 | 0.3889 | 2.6237 |

Active-site-neighborhood slice:

| Scorer | Active-site-neighborhood Spearman | Outside-neighborhood Spearman | Neighborhood Variants |
| --- | ---: | ---: | ---: |
| Placeholder | 0.3076 | 0.0249 | 480 |
| ESM-2 8M | 0.5949 | 0.3785 | 480 |

For the ESM-2 8M run, I also added 1,000 bootstrap resamples:

| Group | Spearman | 95% Bootstrap CI |
| --- | ---: | ---: |
| Overall | 0.4113 | 0.3846 to 0.4342 |
| Catalytic positions | 0.6230 | 0.4219 to 0.7643 |
| Non-catalytic positions | 0.3889 | 0.3643 to 0.4133 |
| Active-site neighborhood | 0.5949 | 0.5302 to 0.6564 |
| Outside active-site neighborhood | 0.3785 | 0.3510 to 0.4054 |

## Interpretation

ESM-2 8M gives a much stronger zero-shot signal than the placeholder baseline on the TEM-1 assay.

The most interesting first-pass observation is that ESM-2's catalytic-position Spearman correlation is higher than its non-catalytic Spearman correlation:

```text
catalytic:      0.6230
non-catalytic:  0.3889
overall:        0.4113
```

This does not prove catalytic residues are generally easier for protein language models. A few caveats matter:

- The catalytic-position subset has only 81 variants.
- The catalytic and active-site-neighborhood labels are motif-derived and need external validation.
- TEM-1 beta-lactamase is one enzyme, not a general enzyme benchmark.
- ESM-2 8M is a small model; scaling behavior may differ.
- DMS fitness reflects the assay context, not pure catalytic mechanism.

Still, this is the kind of eval slice I want more life-science AI systems to expose. Aggregate performance can hide the behavior that matters for mechanistic biology.

## What This Repo Demonstrates

This project is not just a notebook result. It is a small, reproducible benchmark scaffold:

- loads ProteinGym DMS data,
- validates mutation strings against the wild-type sequence,
- labels catalytic-position variants,
- labels first-pass active-site-neighborhood variants,
- runs a swappable scorer interface,
- supports ESM-2 masked-marginal scoring,
- computes overall and subgroup Spearman correlations,
- reports bootstrap confidence intervals,
- writes scored variants, metrics, and SVG plots,
- includes tests and GitHub Actions CI.

## Next Experiments

1. Validate catalytic labels against UniProt and structure annotations.
2. Replace or compare the motif-neighborhood group with structure-derived ligand-contact labels.
3. Run larger ESM-2 models on LBNL compute.
4. Run the existing SLURM templates on LBNL compute for larger ESM-2 models.
5. Repeat the benchmark across multiple enzyme DMS assays.

## Why This Matters For AI Biology

For AI systems used in biology, the important question is not only "does the model perform well on average?"

It is also:

- where does the model fail?
- does it fail near chemistry?
- does it fail near binding?
- does it fail on the variants a scientist would prioritize?

This project is my first pass at turning that question into a measurable benchmark.
