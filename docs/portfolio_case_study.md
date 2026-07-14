# Portfolio Case Study: Catalytic Residue Failure Modes In Zero-Shot Protein ML

## Research Question

Do protein language models fail differently on catalytic residues than on the rest of the protein?

## Hypothesis

Sequence-only protein language models should capture broad evolutionary constraint, but may struggle when experimental fitness depends on active-site chemistry, cofactors, or transition-state stabilization.

## Benchmark Design

The benchmark separates variants into exact catalytic-site, substrate-binding, structure-derived mechanism-shell, active-site-neighborhood, and background groups. It computes model scores for each mutation and compares those scores to experimental DMS fitness using Spearman correlation.

## Why This Is Relevant To Life-Science AI Roles

Frontier AI systems for biology need evaluation tasks that reflect where scientific workflows actually break. A model that performs well overall can still fail on mechanism-critical subsets. This project makes that failure mode measurable.

## Current Evidence

The current repo runs on three ProteinGym enzyme DMS datasets: TEM-1 beta-lactamase, VIM-2 metallo-beta-lactamase, and AMIE aliphatic amidase. It includes ESM-2 8M masked-marginal scoring, TEM-1 UniProt/PDB annotation validation, VIM-2 and AMIE structure-derived mechanism shells, and matched-position null controls.

Key ESM-2 8M results:

- TEM-1 overall Spearman: 0.4113; active-site-neighborhood Spearman: 0.6453
- VIM-2 overall Spearman: 0.4305; active-site-neighborhood Spearman: 0.6128
- AMIE overall Spearman: 0.3264; active-site-neighborhood Spearman: 0.4092

## Next Evidence Upgrade

The next version should run larger ESM-2 models or ESM-1v on LBNL compute, add conservation-matched controls, and extend the panel to beta-glucosidase.
