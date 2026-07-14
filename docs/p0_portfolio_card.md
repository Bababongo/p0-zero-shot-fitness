# P0 Portfolio Card: Mechanism-Sliced Zero-Shot Fitness

## One-Line Summary

I built a reproducible enzyme DMS benchmark showing that ESM-2 scale improves global zero-shot fitness prediction, while mechanism-specific claims need residue-slice controls.

## Main Figure

![P0 four-enzyme ESM-2 35M portfolio figure](assets/p0_four_enzyme_35m_portfolio_figure.svg)

## Scientific Question

Do protein language models fail differently near catalytic and mechanism-relevant residues than across the rest of an enzyme?

## What I Built

- A Python benchmark package with a CLI, tests, typed records, and reproducible JSON/CSV/SVG outputs.
- A four-enzyme ProteinGym panel: TEM-1, VIM-2, AMIE, and beta-glucosidase.
- ESM-2 masked-marginal scoring at 8M and 35M scale.
- Residue-slice evaluation for exact catalytic or metal-binding sites, active-site neighborhoods, structure-derived mechanism shells, and background residues.
- Bootstrap intervals, matched residue-position null controls, and covariate-matched null controls.
- Savio SLURM workflows for GPU scoring and artifact recovery.

## Result Snapshot

| Enzyme | Overall Spearman | Exact Site | Active-Site Neighborhood | Matched-Null Read |
| --- | ---: | ---: | ---: | --- |
| TEM-1 | 0.5548 | 0.4596 | 0.7027 | Active-site neighborhood clears null, p = 0.012 |
| VIM-2 | 0.5280 | 0.3449 | 0.6133 | Inside null, p = 0.142 |
| AMIE | 0.4082 | 0.0911 | 0.4335 | Inside null, p = 0.778 |
| Beta-glucosidase | 0.4481 | 0.5105 | 0.4327 | Inside null, p = 0.984 |

## Interview Explanation

P0 started as a simple question: does ESM-2 behave differently near enzyme catalytic residues? I began with TEM-1 beta-lactamase, then expanded to VIM-2, AMIE, and beta-glucosidase so the result would not be a one-enzyme story.

The key result is that ESM-2 35M improves global zero-shot ranking across all four enzymes, but exact catalytic-site slices are small and noisy. TEM-1 active-site neighborhood is the only 35M mechanism slice that clears matched-position null controls. VIM-2, AMIE, and beta-glucosidase show why matched controls matter: raw mechanism-slice scores can look strong but still be ordinary relative to same-size random residue-position groups.

The pre-report control upgrade narrows the claim further. TEM-1 active-site neighborhood remains the strongest positive mechanism-local signal after mutation-count, fitness-variance, fitness-distribution, and structure-contact controls, but it becomes borderline under the strict combined covariate control. AMIE and beta-glucosidase become useful counterexamples rather than inconvenient results.

Beta-glucosidase is the useful scaling counterexample. At 8M, its AF2 catalytic shell cleared matched controls. At 35M, global performance improved sharply, but the shell no longer cleared matched controls.

## What This Proves

- Aggregate model performance can hide biology-specific behavior.
- Model scale helps the global DMS ranking task.
- Residue-zone claims need matched controls before becoming biological claims.
- Covariate-matched controls make the final claim narrower, not weaker: the project now distinguishes robust, borderline, and negative mechanism-slice evidence.
- A protein ML benchmark is stronger when it separates exact catalytic chemistry, local mechanism environment, and background stability/evolutionary signal.

## What This Does Not Prove

- It does not prove ESM-2 understands catalysis.
- It does not prove active-site neighborhoods are always special.
- It does not yet include a true MSA-derived evolutionary conservation baseline.
- Structure contact density is a burial/exposure proxy, not full solvent-accessibility calculation.
- It is retrospective, not a prospective enzyme-design campaign.

## Next Scientific Upgrade

1. Add a true MSA-derived conservation baseline when per-position MSA features are available.
2. Compare against ESM-1v or MSA Transformer.
3. Add prospective validation on a new enzyme-design target.

## Website Blurb

**Mechanism-sliced zero-shot protein fitness.** I built a reproducible Python benchmark that scores enzyme DMS mutations with ESM-2 and asks where inside enzymes the model works. Across TEM-1, VIM-2, AMIE, and beta-glucosidase, ESM-2 35M improves global mutation ranking, but mechanism-slice effects are enzyme-specific and require matched controls. The project demonstrates biology-aware evaluation, HPC execution, production Python, and scientific communication.
