# Portfolio Case Study: Catalytic Residue Failure Modes In Zero-Shot Protein ML

## Research Question

Do protein language models fail differently on catalytic residues than on the rest of the protein?

## Hypothesis

Sequence-only protein language models should capture broad evolutionary constraint, but may struggle when experimental fitness depends on active-site chemistry, cofactors, or transition-state stabilization.

## Benchmark Design

The benchmark separates variants into catalytic and non-catalytic residue groups, computes model scores for each mutation, and compares those scores to experimental DMS fitness using Spearman correlation.

## Why This Is Relevant To Life-Science AI Roles

Frontier AI systems for biology need evaluation tasks that reflect where scientific workflows actually break. A model that performs well overall can still fail on mechanism-critical subsets. This project makes that failure mode measurable.

## Current Limitation

The initial repo uses fixture data and a placeholder scorer. It proves the pipeline shape, not a biological result.

## Next Evidence Upgrade

The next version should add real ESM-2 scoring and a public enzyme DMS dataset, then produce a short report with figures and failure analysis.
