# P0 v3 Enzyme Panel Plan

## Purpose

P0 is no longer just a TEM-1 beta-lactamase case study. The next scientific upgrade is to test whether the v2 pattern is systematic across enzymes:

> Sequence-only protein language models may capture functional-neighborhood constraints better than exact catalytic chemistry.

The way to test that is an enzyme panel.

## Core Research Question

> Across enzyme DMS landscapes, do protein language models show different performance in exact catalytic residues, active-site neighborhoods, ligand-contact pockets, and non-mechanistic background residues?

## Stronger Hypothesis

The strongest hypothesis is not "ESM fails at active sites."

The stronger hypothesis is:

> Protein language models do not explicitly model catalytic chemistry, but they can capture evolutionary and structural constraints around the catalytic neighborhood. Exact catalytic residues may be too sparse and chemistry-specific to interpret alone, while active-site neighborhoods may show systematic signal because they encode fold, substrate positioning, and local evolutionary constraints.

This separates four ideas that are usually blurred together:

- exact catalytic chemistry,
- local functional neighborhood,
- ligand/substrate contact geometry,
- global stability and evolutionary constraint.

## Why The Current P0 Is Not Enough

The current TEM-1 result is strong as a portfolio artifact, but scientifically incomplete.

Current limitations:

- One enzyme.
- One assay context.
- One protein family.
- One exact active-site set with only 4 residue positions.
- One ligand-bound structure for contact labels.
- No conservation-matched or solvent-accessibility-matched controls yet.

The v2 matched-position null controls made the story more honest. The v3 enzyme panel is what makes it broadly meaningful.

## Panel Selection Principles

Each candidate enzyme should ideally have:

- public DMS or multiplexed variant-effect data,
- at least 1,000 single mutants,
- a wild-type sequence,
- ProteinGym metadata,
- a structure or high-confidence structural model,
- known or curatable catalytic residues,
- a mechanism-relevant assay, preferably activity or organismal fitness tied to enzyme function,
- enough biological diversity to avoid a beta-lactamase-only story.

## Priority Candidate Panel

The candidate registry is saved at:

`data/panels/p0_enzyme_panel_candidates.csv`

### Tier 0: Seed Case

| Dataset | Protein | Why It Matters |
| --- | --- | --- |
| `BLAT_ECOLX_Firnberg_2014` | TEM-1 beta-lactamase | Completed seed case. Use as the regression test for every v3 pipeline change. |

### Tier 1: First Real Panel

These are the highest-value next enzymes because they are biologically diverse, have enough single mutants, and should support active-site or pocket annotation.

| Dataset | Protein | Enzyme Type | Single Mutants | Why Add It |
| --- | --- | --- | ---: | --- |
| `A4GRB6_PSEAI_Chen_2020` | VIM-2 beta-lactamase | Metallo-beta-lactamase | 5,004 | Tests whether beta-lactamase findings transfer from serine to metal-dependent chemistry. |
| `AMIE_PSEAE_Wrenbeck_2017` | Aliphatic amidase | Hydrolase | 6,227 | Classic enzyme-function DMS with substrate-specific framing. |
| `Q59976_STRSQ_Romero_2015` | Beta-glucosidase | Glycoside hydrolase | 2,999 | Direct enzyme-function DMS in a different fold and chemistry class. |
| `TPK1_HUMAN_Weile_2017` | Thiamin pyrophosphokinase 1 | Kinase / phosphotransferase | 3,181 | Compact human enzyme complementation case. |
| `UBC9_HUMAN_Weile_2017` | SUMO-conjugating enzyme UBC9 | E2 conjugating enzyme | 2,563 | Small transferase with active cysteine chemistry. |
| `DYR_ECOLI_Thompson_2019` | DHFR | Oxidoreductase | 2,363 | Classic enzyme where stability, abundance, and catalytic function can be entangled. |

### Tier 2: Expansion Panel

| Dataset | Protein | Enzyme Type | Why Add It |
| --- | --- | --- | --- |
| `CP2C9_HUMAN_Amorosi_2021_activity` | Cytochrome P450 2C9 | Heme monooxygenase | Cofactor and ligand chemistry likely expose limits of sequence-only models. |
| `PTEN_HUMAN_Mighell_2018` | PTEN | Lipid phosphatase | Clinically important enzyme with catalytic pocket and disease relevance. |
| `OXDA_RHOTO_Vanella_2023_activity` | D-amino acid oxidase | Flavoenzyme oxidase | Paired expression/activity datasets can separate abundance from catalytic activity. |
| `KKA2_KLEPN_Melnikov_2014` | APH(3')II | Antibiotic-resistance kinase | Antibiotic resistance enzyme with ATP and aminoglycoside-binding chemistry. |
| `SRC_HUMAN_Ahler_2019` | SRC | Tyrosine kinase | Human kinase with regulatory/catalytic coupling. |
| `ANCSZ_Hobbs_2022` | Ancestral spleen tyrosine kinase | Tyrosine kinase | Adds evolutionary and ancestral-sequence angle. |

## Required Residue Zones

For every enzyme, create the same zone labels:

1. `exact_catalytic_site`
2. `active_site_neighborhood`
3. `substrate_or_ligand_contact`
4. `cofactor_contact`
5. `buried_core`
6. `surface`
7. `distal_conserved`
8. `background`

The purpose is to separate mechanism from confounders.

## Controls Needed For Novelty

The v2 matched-position null control is necessary but not sufficient.

Next controls:

| Control | Why It Matters |
| --- | --- |
| Position-count matched null | Controls for tiny slice size. Already implemented. |
| Mutation-count matched null | Controls for uneven numbers of mutations per residue. |
| Conservation-matched null | Tests whether active-site-neighborhood signal is just conservation. |
| Solvent-accessibility-matched null | Tests whether the signal is just buried/core stability. |
| Distance-to-active-site bins | Tests whether signal changes smoothly with mechanistic proximity. |
| Fitness-variance-matched null | Controls for groups with wider or narrower experimental dynamic range. |
| Mutation-class-matched null | Controls for amino-acid chemistry mix. |

## Model Comparisons

Do not only scale ESM-2.

Minimum model panel:

- Placeholder baseline,
- ESM-2 8M,
- ESM-2 35M,
- ESM-2 150M or 650M if compute allows,
- ESM-1v,
- MSA Transformer,
- EVmutation or simple conservation baseline.

The intellectual question is:

> Do sequence-only PLMs, MSA-aware models, and conservation baselines differ in where they succeed inside enzymes?

## First v3 Implementation Step

Status: completed.

The first implementation target was:

> Build a dataset registry loader that reads `data/panels/p0_enzyme_panel_candidates.csv` and validates that each candidate has the required ProteinGym metadata fields.

This does not run ESM yet. It is an intake-check step before spending compute.

It produces:

- `results/panel_registry_validation.json`
- a pass/fail status for each candidate,
- missing annotation fields,
- estimated compute cost based on number of single mutants and sequence length,
- recommended first three datasets.

Run it with:

```bash
python scripts/validate_panel_registry.py
```

Current validator result:

| Check | Result |
| --- | ---: |
| Candidate enzyme datasets | 17 |
| ProteinGym metadata matches | 17 |
| Ready for current P0 pipeline | 4 |
| Need local data and annotations | 13 |

The ready datasets are:

- `BLAT_ECOLX_Firnberg_2014` - TEM-1 beta-lactamase.
- `A4GRB6_PSEAI_Chen_2020` - VIM-2 metallo-beta-lactamase.
- `AMIE_PSEAE_Wrenbeck_2017` - AMIE aliphatic amidase.
- `Q59976_STRSQ_Romero_2015` - beta-glucosidase.

The other 13 ProteinGym candidates have matching metadata, but still need local DMS CSV, FASTA, catalytic-residue JSON, and residue-group JSON files before they can run through the current P0 pipeline.

## First Second-Enzyme Case

Status: VIM-2 placeholder baseline, ESM-2 8M baseline, ESM-2 35M baseline, ProteinGym AF2 structure-derived metal-site shell, and RCSB 5ACX/WL3 inhibitor-contact label completed.

Dataset:

- `A4GRB6_PSEAI_Chen_2020`
- Protein: VIM-2 metallo-beta-lactamase
- Variants: 5,004 single mutants
- Exact curated metal-binding/catalytic-site variants: 113
- Active-site-neighborhood variants: 448
- 5ACX/WL3 inhibitor-contact variants: 247

Current VIM-2 ESM-2 35M result:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.5280 | - | 5,004 |
| Curated metal-binding site | 0.3449 | 0.5085 | 113 |
| 5ACX WL3 inhibitor contact, 5 A | 0.6613 | 0.5207 | 247 |
| AF2 structure metal-site shell, 5 A | 0.5846 | 0.4778 | 802 |
| Active-site neighborhood | 0.6133 | 0.4897 | 448 |

The 35M model improves VIM-2 overall performance, and the WL3 inhibitor-contact, active-site-neighborhood, and metal-site shell remain strong in raw Spearman. However, these slices fall inside matched-position or stricter conservation-plus-SASA controls at 35M, while the exact curated metal-binding-site slice also remains inside the matched null.

## First Panel Dataset Status

Current status:

1. `A4GRB6_PSEAI_Chen_2020` - added, placeholder, ESM-2 8M, and ESM-2 35M complete.
2. `AMIE_PSEAE_Wrenbeck_2017` - added, placeholder, ESM-2 8M, and ESM-2 35M complete.
3. `Q59976_STRSQ_Romero_2015` - added, placeholder, ESM-2 8M, and ESM-2 35M complete.

Why these three:

- VIM-2, amidase, and beta-glucosidase cover public DMS cases with thousands of single mutants.
- They avoid pathogen-linked targets while still testing mechanistically distinct enzyme chemistry.
- All three require explicit active-site, pocket, or cofactor residue zones.
- Together, they move P0 beyond TEM-1 without making the scope explode.

## First Non-Beta-Lactamase Case

AMIE aliphatic amidase is now local and runnable:

- Dataset: `AMIE_PSEAE_Wrenbeck_2017`
- Variants: 6,227 single mutants
- Exact curated catalytic-site variants: 57
- ProteinGym AF2 catalytic-shell variants: 621
- Active-site-neighborhood variants: 259
- Current scorers: placeholder baseline, ESM-2 8M, and ESM-2 35M

AMIE ESM-2 35M:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.4082 | - | 6,227 |
| Curated catalytic site | 0.0911 | 0.3991 | 57 |
| AF2 catalytic shell, 5 A | 0.3071 | 0.4069 | 621 |
| Active-site neighborhood | 0.4335 | 0.3902 | 259 |

The active-site-neighborhood slice is stronger than the outside background, but remains inside same-size random residue-position controls for ESM-2 35M. This is a valuable counterexample to overclaiming the TEM-1 pattern.

## Fourth Enzyme Case

Beta-glucosidase is now local and runnable:

- Dataset: `Q59976_STRSQ_Romero_2015`
- Variants: 2,999 single mutants
- Exact curated catalytic-site variants: 12
- ProteinGym AF2 catalytic-shell variants: 149
- Active-site-neighborhood variants: 60
- Current scorers: placeholder baseline, ESM-2 8M, and ESM-2 35M
- Savio script: `hpc/savio_esm2_35m_bgly.slurm`

Beta-glucosidase ESM-2 8M:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.1442 | - | 2,999 |
| Curated catalytic site | 0.4196 | 0.1363 | 12 |
| AF2 catalytic shell, 5 A | 0.3712 | 0.1101 | 149 |
| Active-site neighborhood | 0.3595 | 0.1222 | 60 |

The beta-glucosidase AF2 catalytic shell is higher than matched random residue-position controls at 8M: observed Spearman `0.3712`, null 95% interval `-0.0969 to 0.3450`, empirical p = `0.018`.

Beta-glucosidase ESM-2 35M:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.4481 | - | 2,999 |
| Curated catalytic site | 0.5105 | 0.4434 | 12 |
| AF2 catalytic shell, 5 A | 0.3808 | 0.4286 | 149 |
| Active-site neighborhood | 0.4327 | 0.4341 | 60 |

At 35M, beta-glucosidase has the largest global rescue in the panel, improving from `0.1442` to `0.4481`. But its catalytic shell, active-site neighborhood, and exact catalytic site all remain inside matched-position null controls. This is a different pattern from the 8M result and a useful warning against overclaiming one model-size slice.

## Four-Enzyme 35M Comparison

| Dataset | Enzyme | Overall ESM-2 35M | Exact Site | Best Mechanism Slice |
| --- | --- | ---: | ---: | --- |
| `BLAT_ECOLX_Firnberg_2014` | TEM-1 beta-lactamase | 0.5548 | 0.4596 | PDB ligand contact, 0.7127; active-site neighborhood, 0.7027 |
| `A4GRB6_PSEAI_Chen_2020` | VIM-2 metallo-beta-lactamase | 0.5280 | 0.3449 | WL3 inhibitor contact, 0.6613; active-site neighborhood, 0.6133; metal-site shell, 0.5846 |
| `AMIE_PSEAE_Wrenbeck_2017` | AMIE aliphatic amidase | 0.4082 | 0.0911 | Active-site neighborhood, 0.4335 |
| `Q59976_STRSQ_Romero_2015` | Beta-glucosidase | 0.4481 | 0.5105 | Active-site neighborhood, 0.4327; catalytic shell, 0.3808 |

## Four-Enzyme 8M Comparison

| Dataset | Enzyme | Overall ESM-2 8M | Exact Site | Best Mechanism Slice |
| --- | --- | ---: | ---: | --- |
| `BLAT_ECOLX_Firnberg_2014` | TEM-1 beta-lactamase | 0.4113 | 0.3023 | Active-site neighborhood, 0.6453 |
| `A4GRB6_PSEAI_Chen_2020` | VIM-2 metallo-beta-lactamase | 0.4305 | 0.3702 | Active-site neighborhood, 0.6128 |
| `AMIE_PSEAE_Wrenbeck_2017` | AMIE aliphatic amidase | 0.3264 | 0.2057 | Active-site neighborhood, 0.4092 |
| `Q59976_STRSQ_Romero_2015` | Beta-glucosidase | 0.1442 | 0.4196 | AF2 catalytic shell, 0.3712 |

## Success Criteria

P0 v3 is successful when it can answer:

1. Does active-site-neighborhood signal remain higher than matched null across multiple enzymes?
2. Is exact catalytic-site performance generally noisy, low, or dataset-dependent?
3. Do ligand/cofactor-contact regions behave differently from active-site neighborhoods?
4. Does model family change the residue-zone pattern?
5. Can we explain the result in terms of mechanism, conservation, structure, or assay type?

## Interview Version

> P0 started as one TEM-1 case study. I upgraded it into a mechanism-stratified enzyme benchmark seed across TEM-1, VIM-2, AMIE, and beta-glucosidase. All four enzymes now have ESM-2 8M and 35M results. The key idea is that average DMS correlation is not enough; I want to know where inside enzymes protein language models work. The current result says scale improves global zero-shot performance, exact catalytic-site slices remain small and noisy, and mechanism-neighborhood or structure-shell signal is enzyme-dependent and must be tested against matched controls.
