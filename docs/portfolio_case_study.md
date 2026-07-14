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

The current repo runs on four ProteinGym enzyme DMS datasets: TEM-1 beta-lactamase, VIM-2 metallo-beta-lactamase, AMIE aliphatic amidase, and beta-glucosidase. It includes ESM-2 8M and 35M masked-marginal scoring for all four enzymes, TEM-1 UniProt/PDB annotation validation, VIM-2 5ACX/WL3 ligand-pocket labels, structure-derived mechanism shells, and matched controls.

Key ESM-2 35M results:

- TEM-1 overall Spearman: 0.5548; active-site-neighborhood Spearman: 0.7027; ligand-contact Spearman: 0.7127
- VIM-2 overall Spearman: 0.5280; WL3 inhibitor-contact Spearman: 0.6613; active-site-neighborhood Spearman: 0.6133; metal-site shell Spearman: 0.5846
- AMIE overall Spearman: 0.4082; active-site-neighborhood Spearman: 0.4335; exact catalytic-site Spearman: 0.0911
- Beta-glucosidase overall Spearman: 0.4481; exact catalytic-site Spearman: 0.5105; catalytic-shell Spearman: 0.3808

The strongest current interpretation is that model scaling improves global zero-shot fitness prediction, while exact catalytic or metal-binding slices remain harder and noisier than broader mechanism-adjacent neighborhoods. Matched-position controls show that the active-site-neighborhood effect is enzyme-dependent rather than automatic.

Beta-glucosidase is the most useful scaling counterexample. At 8M, overall Spearman is only 0.1442, but the AF2 catalytic shell reaches 0.3712 and is higher than matched-position null controls with empirical p = 0.018. At 35M, overall Spearman jumps to 0.4481, but the catalytic shell no longer clears matched controls.

## Next Evidence Upgrade

The next version should compare against ESM-1v or MSA Transformer, create an ESM-2-vs-MSA interpretation figure, and test the story prospectively on a new enzyme-design target.
