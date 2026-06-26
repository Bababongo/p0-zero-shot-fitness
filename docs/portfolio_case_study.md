# Portfolio Case Study: Catalytic Residue Failure Modes In Zero-Shot Protein ML

## Research Question

Do protein language models fail differently on catalytic residues than on the rest of the protein?

## Hypothesis

Sequence-only protein language models should capture broad evolutionary constraint, but may struggle when experimental fitness depends on active-site chemistry, cofactors, or transition-state stabilization.

## Benchmark Design

The benchmark separates variants into UniProt active-site, substrate-binding, PDB ligand-contact, active-site-neighborhood, and background groups. It computes model scores for each mutation and compares those scores to experimental DMS fitness using Spearman correlation.

## Why This Is Relevant To Life-Science AI Roles

Frontier AI systems for biology need evaluation tasks that reflect where scientific workflows actually break. A model that performs well overall can still fail on mechanism-critical subsets. This project makes that failure mode measurable.

## Current Evidence

The current repo runs on ProteinGym `BLAT_ECOLX_Firnberg_2014` for TEM-1 beta-lactamase. It includes ESM-2 8M masked-marginal scoring, UniProt P62593 annotation validation, and a structure-derived ligand-contact group from PDB 1M40.

Key ESM-2 8M results:

- overall Spearman: 0.4113
- UniProt active-site Spearman: 0.3023 across 57 variants
- PDB 1M40 ligand-contact Spearman: 0.6076 across 277 variants
- active-site-neighborhood Spearman: 0.6453 across 461 variants

## Next Evidence Upgrade

The next version should run larger ESM-2 models or ESM-1v on LBNL compute, then repeat the same validated residue-slice analysis.
