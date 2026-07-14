# P0 Pre-Report Control Upgrade

## Purpose

This upgrade asks whether the P0 mechanism-slice results survive stricter controls before writing the final project report.

The previous control asked:

> Is a mechanism slice unusual compared with random residue-position slices of the same size?

The new control asks:

> Is a mechanism slice still unusual after matching for obvious confounders such as mutation coverage, experimental fitness spread, model-score sensitivity, relative sequence position, and structure-derived burial/exposure proxy?

## What Changed

- Added per-position covariate derivation from each scored-variant table.
- Added structure contact-density covariates from local PDB/AF2 structures.
- Added covariate-matched null controls to `src/p0_zero_shot_fitness/metrics.py`.
- Added `scripts/derive_position_covariates.py`.
- Added `scripts/summarize_control_readouts.py`.
- Added approximate solvent-accessibility/SASA covariates after this pre-report upgrade.
- Added MSA conservation-baseline infrastructure and an MSA availability audit.
- Refreshed all four ESM-2 35M metric JSON files with covariate-matched controls.
- Added a placeholder-vs-ESM-2 comparison artifact as a simple non-ESM baseline check.

## Covariates

| Control | Covariates | What It Tests |
| --- | --- | --- |
| `mutation_count` | number of scored mutants per residue | Whether a slice looks special because it has different mutation coverage. |
| `fitness_variance` | per-position fitness standard deviation | Whether a slice is easier or harder because the experimental fitness values have different spread. |
| `fitness_distribution` | fitness mean, standard deviation, range | Whether a slice is explained by local DMS distribution shape. |
| `model_score_sensitivity` | ESM score mean and standard deviation | Whether a slice is explained by the model already assigning unusually broad/narrow score distributions there. |
| `relative_position` | normalized sequence position | Whether sequence-location effects explain the slice. |
| `structure_contact_density` | C-beta/C-alpha contact count within 10 A | Burial/exposure proxy; not full SASA. |
| `structure_solvent_accessibility` | approximate residue SASA from PDB heavy atoms | Whether a slice is explained by similar solvent exposure. |
| `combined_available` | all available covariates above | A stricter combined nearest-neighbor null. |

Important limitation: this repo does not contain the external ProteinGym MSA `.a2m` files. Therefore this upgrade does **not** claim to have run a true evolutionary conservation baseline yet. It now includes the code path and audit for that baseline, but the actual conservation result remains blocked on staging the MSA files.

## Main Read

The control upgrade makes P0 more honest and more mature.

The old read was:

> TEM-1 active-site neighborhood clears matched-position null controls at 35M.

The new read is:

> TEM-1 active-site neighborhood remains the strongest mechanism-slice signal. It survives mutation-count, fitness-variance, fitness-distribution, and structure-contact controls, but becomes borderline under the strict combined covariate control.

That is exactly the kind of nuance the final P0 report needs.

## Key 35M Control Results

| Dataset | Slice | Position Null | Fitness Variance | Model-Score Sensitivity | Structure Contact | Combined |
| --- | --- | --- | --- | --- | --- | --- |
| TEM-1 | active-site neighborhood | higher, p = 0.012 | higher, p = 0.014 | inside, p = 0.076 | higher, p = 0.022 | inside/borderline, p = 0.058 |
| TEM-1 | ligand contact, 5 A | inside, p = 0.070 | inside, p = 0.062 | inside, p = 0.120 | inside, p = 0.082 | inside, p = 0.092 |
| VIM-2 | active-site neighborhood | inside, p = 0.142 | inside, p = 0.182 | inside, p = 0.194 | higher, p = 0.024 | inside, p = 0.176 |
| VIM-2 | metal-site shell, 5 A | inside, p = 0.084 | inside/borderline, p = 0.058 | inside, p = 0.224 | higher, p = 0.000 | inside/borderline, p = 0.054 |
| AMIE | exact catalytic site | inside, p = 0.408 | inside, p = 0.286 | inside, p = 0.086 | inside, p = 0.202 | lower, p = 0.002 |
| AMIE | catalytic shell, 5 A | inside, p = 0.312 | inside, p = 0.100 | inside, p = 0.066 | lower, p = 0.000 | inside, p = 0.240 |
| Beta-glucosidase | catalytic shell, 5 A | inside, p = 0.654 | inside, p = 0.646 | lower, p = 0.046 | inside, p = 0.130 | inside, p = 0.232 |

## Interpretation By Enzyme

### TEM-1

TEM-1 remains the cleanest positive mechanism-neighborhood result. The active-site neighborhood has observed Spearman `0.7027`. It is higher than:

- position-matched null controls,
- mutation-count controls,
- fitness-variance controls,
- fitness-distribution controls,
- structure-contact controls.

It does not clearly clear model-score-sensitivity matching (`p = 0.076`) or the strict combined covariate control (`p = 0.058`). This means the final report should say:

> TEM-1 active-site-neighborhood signal is robust to several single-confounder controls and borderline under the strict combined control.

Do **not** say:

> ESM-2 generally understands active sites.

### VIM-2

VIM-2 has strong raw mechanism-neighborhood and metal-shell Spearman, but the strict controls make the result more cautious.

The structure-contact control still shows elevated metal-shell and active-neighborhood performance. However, the combined controls are inside or borderline. This suggests:

> VIM-2 mechanism-adjacent regions show real raw signal, but the evidence is not strong enough to claim a general mechanism-specific advantage after all confounders are matched.

### AMIE

AMIE is the clean negative/counterexample case.

The exact catalytic site is weak (`0.0911`) and becomes lower than the strict combined covariate null. The catalytic shell is also lower than structure-contact matched controls.

This strengthens the project because it prevents overclaiming. AMIE says:

> Scaling helps global performance, but not every enzyme gets a mechanism-slice rescue.

### Beta-Glucosidase

Beta-glucosidase stays a scaling counterexample.

The global ESM-2 35M result is much better than 8M, but the catalytic shell does not survive the stricter controls. In fact, it is lower than the model-score-sensitivity matched null.

The final report should use beta-glucosidase to show:

> Bigger model does not automatically mean stronger mechanism-slice signal.

## Baseline Check

The placeholder biochemical baseline remains weak across the four enzymes:

| Dataset | Placeholder Overall | ESM-2 35M Overall |
| --- | ---: | ---: |
| TEM-1 | 0.0430 | 0.5548 |
| VIM-2 | 0.0194 | 0.5280 |
| AMIE | -0.0040 | 0.4082 |
| Beta-glucosidase | 0.0443 | 0.4481 |

This does not replace a true conservation baseline, but it does show that the ESM-2 result is not reproduced by the simple deterministic mutation-class plumbing baseline.

## New Artifacts

- `results/proteingym_blat_esm2_t12_35M/position_covariates.json`
- `results/proteingym_vim2_esm2_t12_35M/position_covariates.json`
- `results/proteingym_amie_esm2_t12_35M/position_covariates.json`
- `results/proteingym_bgly_esm2_t12_35M/position_covariates.json`
- `results/proteingym_four_enzyme_covariate_control_summary.json`
- `results/proteingym_four_enzyme_placeholder_vs_esm2_t12_35M_comparison.json`
- refreshed `results/proteingym_four_enzyme_esm2_t12_35M_comparison.json`

## Best Final P0 Claim After This Upgrade

> ESM-2 scale improves global zero-shot fitness prediction across four enzymes. Mechanism-slice behavior is not universal: TEM-1 active-site neighborhood remains the strongest positive mechanism-local signal after several covariate controls, while VIM-2 is suggestive but not fully controlled, and AMIE and beta-glucosidase act as counterexamples. The evidence supports mechanism-aware evaluation, not a blanket claim that protein language models understand catalysis.

## What Remains External

A true evolutionary conservation-matched control needs per-position MSA-derived conservation scores. The current repository does not include those MSA artifacts, so the final report should state this clearly rather than pretending that the local proxy controls are evolutionary conservation.
