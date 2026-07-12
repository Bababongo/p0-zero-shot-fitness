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
| `R1AB_SARS2_Flynn_2022` | SARS-CoV-2 Mpro | Cysteine protease | 5,725 | Well-known catalytic dyad, drug-design relevance, and strong mechanistic interpretability. |
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

The next implementation target should be:

> Build a dataset registry loader that reads `data/panels/p0_enzyme_panel_candidates.csv` and validates that each candidate has the required ProteinGym metadata fields.

This should not run ESM yet.

It should produce:

- `results/panel_registry_validation.json`
- a pass/fail status for each candidate,
- missing annotation fields,
- estimated compute cost based on number of single mutants and sequence length,
- recommended first three datasets.

## First Three Datasets To Add

Start with:

1. `A4GRB6_PSEAI_Chen_2020` - VIM-2 beta-lactamase.
2. `R1AB_SARS2_Flynn_2022` - SARS-CoV-2 Mpro.
3. `AMIE_PSEAE_Wrenbeck_2017` - aliphatic amidase.

Why these three:

- They cover different enzyme mechanisms.
- They have thousands of single mutants.
- They have ProteinGym structure references.
- Their active sites should be curatable.
- Together, they move P0 beyond TEM-1 without making the scope explode.

## Success Criteria

P0 v3 is successful when it can answer:

1. Does active-site-neighborhood signal remain higher than matched null across multiple enzymes?
2. Is exact catalytic-site performance generally noisy, low, or dataset-dependent?
3. Do ligand/cofactor-contact regions behave differently from active-site neighborhoods?
4. Does model family change the residue-zone pattern?
5. Can we explain the result in terms of mechanism, conservation, structure, or assay type?

## Interview Version

> P0 started as one TEM-1 case study. I upgraded it into the start of a mechanism-stratified enzyme benchmark. The key idea is that average DMS correlation is not enough; I want to know where inside enzymes protein language models work. The next phase expands from TEM-1 to a panel of enzymes and asks whether the active-site-neighborhood signal is systematic after controlling for slice size, conservation, solvent accessibility, and mutation class.

