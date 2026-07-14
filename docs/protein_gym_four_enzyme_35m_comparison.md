# ProteinGym Four-Enzyme ESM-2 35M Comparison

## Purpose

This comparison is the first completed P0 enzyme-panel scaling result. It asks whether the mechanism-slice story survives when ESM-2 is scaled from the local 8M model to the Savio-run 35M model across four mechanistically different enzymes.

## Enzymes

| Dataset | Enzyme | Mechanism Class | Variants |
| --- | --- | --- | ---: |
| `BLAT_ECOLX_Firnberg_2014` | TEM-1 beta-lactamase | Serine beta-lactamase | 4,783 |
| `A4GRB6_PSEAI_Chen_2020` | VIM-2 beta-lactamase | Metallo-beta-lactamase | 5,004 |
| `AMIE_PSEAE_Wrenbeck_2017` | AMIE aliphatic amidase | Hydrolase amidase | 6,227 |
| `Q59976_STRSQ_Romero_2015` | Beta-glucosidase | GH1 glycoside hydrolase | 2,999 |

## ESM-2 35M Results

![P0 four-enzyme ESM-2 35M portfolio figure](assets/p0_four_enzyme_35m_portfolio_figure.svg)

| Dataset | Overall Spearman | Exact Site Spearman | Background Spearman | Best Mechanism Slice |
| --- | ---: | ---: | ---: | --- |
| TEM-1 | 0.5548 | 0.4596 | 0.5428 | Ligand contact, 0.7127; active-site neighborhood, 0.7027 |
| VIM-2 | 0.5280 | 0.3449 | 0.5085 | WL3 inhibitor contact, 0.6613; active-site neighborhood, 0.6133; metal-site shell, 0.5846 |
| AMIE | 0.4082 | 0.0911 | 0.3991 | Active-site neighborhood, 0.4335 |
| Beta-glucosidase | 0.4481 | 0.5105 | 0.4434 | Active-site neighborhood, 0.4327; catalytic shell, 0.3808 |

## 8M To 35M Scaling

| Dataset | 8M Overall | 35M Overall | Change | Key Read |
| --- | ---: | ---: | ---: | --- |
| TEM-1 | 0.4113 | 0.5548 | +0.1435 | Stronger global ranking and strongest controlled active-site-neighborhood signal. |
| VIM-2 | 0.4305 | 0.5280 | +0.0975 | Strong raw metal/neighborhood signal, but inside matched-position null at 35M. |
| AMIE | 0.3264 | 0.4082 | +0.0818 | Useful counterexample: global scale helps, exact catalytic site remains weak. |
| Beta-glucosidase | 0.1442 | 0.4481 | +0.3039 | Largest global rescue, but the 8M catalytic-shell matched-null hit does not persist at 35M. |

## Matched-Position Null Read

| Dataset | Exact Site | Structure Slice | Active-Site Neighborhood |
| --- | --- | --- | --- |
| TEM-1 | Inside null, p = 0.668 | Inside null, p = 0.070 | Higher than null, p = 0.012 |
| VIM-2 | Inside null, p = 0.476 | Inside null, p = 0.084; WL3 inhibitor contact inside null, p = 0.186 | Inside null, p = 0.142 |
| AMIE | Inside null, p = 0.408 | Inside null, p = 0.312 | Inside null, p = 0.778 |
| Beta-glucosidase | Inside null, p = 0.772 | Inside null, p = 0.654 | Inside null, p = 0.984 |

## Covariate-Matched Null Read

After the pre-report control upgrade, each mechanism slice is also compared against nearest-neighbor residue-position samples matched on local covariates derived from the scored DMS table and structure:

- mutation coverage,
- experimental fitness variance,
- experimental fitness distribution,
- model-score sensitivity,
- relative sequence position,
- structure contact density as a burial/exposure proxy,
- and a strict combined covariate control.

| Dataset | Slice | Strongest Controlled Read |
| --- | --- | --- |
| TEM-1 | Active-site neighborhood | Still strongest positive slice: higher than fitness-variance control, p = 0.014; higher than structure-contact control, p = 0.022; borderline under combined control, p = 0.058. |
| TEM-1 | Ligand contact, 5 A | Suggestive but inside the strict controls: combined p = 0.092. |
| VIM-2 | Active-site neighborhood | Raw signal remains high, but combined control is inside null, p = 0.176. |
| VIM-2 | Metal-site shell, 5 A | Structure-contact control is high, p = 0.000, but combined control is only borderline, p = 0.054. |
| VIM-2 | WL3 inhibitor contact, 5 A | Strongest raw VIM-2 slice at 0.6613, but inside strict combined control, p = 0.782. |
| AMIE | Exact catalytic site | Negative control: lower than strict combined covariate null, p = 0.002. |
| Beta-glucosidase | Catalytic shell, 5 A | Does not survive stricter controls; lower than model-score-sensitivity control, p = 0.046. |

The control upgrade makes the final claim narrower and stronger. TEM-1 active-site neighborhood is the best positive mechanism-local result, VIM-2 is suggestive but not fully controlled, and AMIE/beta-glucosidase prevent a blanket "mechanism slices are special" conclusion.

## MSA Conservation Baseline Read

The true MSA conservation baseline asks whether ESM-2 is doing more than family-specific evolutionary conservation.

| Dataset | ESM-2 35M Overall | MSA Overall | ESM-2 Exact Site | MSA Exact Site |
| --- | ---: | ---: | ---: | ---: |
| TEM-1 | 0.5548 | 0.4247 | 0.4596 | 0.4824 |
| VIM-2 | 0.5280 | 0.4931 | 0.3449 | 0.3079 |
| AMIE | 0.4082 | 0.4306 | 0.0911 | 0.2944 |
| Beta-glucosidase | 0.4481 | 0.5615 | 0.5105 | 0.4406 |

Interpretation: ESM-2 35M is clearly stronger than MSA conservation for TEM-1 overall and slightly stronger for VIM-2 overall. MSA conservation is stronger overall for AMIE and beta-glucosidase. This makes the project more interesting, not weaker: the benchmark can now distinguish broad pretrained sequence-model signal from family-specific evolutionary conservation.

## Conservation-Plus-SASA Control

The strongest control now matches mechanism slices against random residue slices with similar MSA conservation and approximate solvent exposure. This asks whether a mechanism-local ESM-2 signal is unusual after accounting for two powerful non-mechanistic explanations: evolutionary conservation and structural burial/exposure.

| Dataset | Slice | Observed Spearman | Null 95% Interval | Empirical p | Direction |
| --- | --- | ---: | ---: | ---: | --- |
| TEM-1 | Active-site neighborhood | 0.7027 | 0.4481 to 0.7133 | 0.094 | Inside conservation+SASA null |
| TEM-1 | Ligand contact, 5 A | 0.7127 | 0.3901 to 0.7625 | 0.212 | Inside conservation+SASA null |
| VIM-2 | Active-site neighborhood | 0.6133 | 0.3234 to 0.6468 | 0.178 | Inside conservation+SASA null |
| VIM-2 | Metal-site shell, 5 A | 0.5846 | 0.3734 to 0.6016 | 0.110 | Inside conservation+SASA null |
| VIM-2 | WL3 inhibitor contact, 5 A | 0.6613 | 0.3873 to 0.7863 | 0.876 | Inside conservation+SASA null |
| AMIE | Exact catalytic site | 0.0911 | 0.1799 to 0.6217 | 0.002 | Lower than conservation+SASA null |
| AMIE | Catalytic shell, 5 A | 0.3071 | 0.3496 to 0.5602 | 0.004 | Lower than conservation+SASA null |
| Beta-glucosidase | Catalytic shell, 5 A | 0.3808 | 0.3407 to 0.6218 | 0.166 | Inside conservation+SASA null |

This does not make P0 weaker. It makes the benchmark more credible: the project can now say that global ESM-2 signal is real, but mechanism-slice claims must survive conservation and structural-exposure controls before being treated as evidence for catalytic understanding.

## Interpretation

The four-enzyme 35M panel makes P0 more mature because it separates three claims that would otherwise get blurred together:

1. ESM-2 scale improves global zero-shot DMS ranking.
2. Exact catalytic-site slices are small and hard to interpret alone.
3. Mechanism-adjacent regions can be strong, but the strongest 35M mechanism slices do not cleanly clear the stricter conservation-plus-SASA control.

The beta-glucosidase result is especially useful. At 8M, the AF2 catalytic shell looked unusually strong relative to matched random residue groups. At 35M, global performance improves dramatically, but the shell no longer clears the matched-position null. That means the project should not claim "catalytic shells always get better with scale." The better claim is:

> Model scale improves aggregate performance, while residue-zone effects are enzyme-specific and need matched controls.

## Artifacts

- `results/proteingym_four_enzyme_esm2_t12_35M_comparison.json`
- `results/proteingym_four_enzyme_msa_conservation_comparison.json`
- `results/proteingym_four_enzyme_esm2_t12_35M_vs_msa_conservation.json`
- `results/proteingym_four_enzyme_covariate_control_summary.json`
- `results/proteingym_four_enzyme_placeholder_vs_esm2_t12_35M_comparison.json`
- `results/proteingym_blat_esm2_t12_35M/metrics.json`
- `results/proteingym_vim2_esm2_t12_35M/metrics.json`
- `results/proteingym_amie_esm2_t12_35M/metrics.json`
- `results/proteingym_bgly_esm2_t12_35M/metrics.json`

## Next Scientific Step

The pre-report control upgrade added local covariate controls, the MSA upgrade added a true evolutionary-conservation baseline, and the conservation-plus-SASA control added the strictest mechanism-slice test so far. The next scientific upgrades are now:

- model-family comparisons such as ESM-1v and MSA Transformer,
- additional ligand-bound or cofactor-aware labels where clean experimental structures are available,
- and prospective validation on a new enzyme-design target.
