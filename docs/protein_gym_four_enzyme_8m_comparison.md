# ProteinGym Four-Enzyme ESM-2 8M Comparison

## Purpose

This comparison extends P0 from three enzymes to four enzymes at the local ESM-2 8M scale. It adds beta-glucosidase as a glycoside hydrolase case before the heavier Savio 35M run.

## Enzymes

| Dataset | Enzyme | Mechanism Class | Variants |
| --- | --- | --- | ---: |
| `BLAT_ECOLX_Firnberg_2014` | TEM-1 beta-lactamase | Serine beta-lactamase | 4,783 |
| `A4GRB6_PSEAI_Chen_2020` | VIM-2 beta-lactamase | Metallo-beta-lactamase | 5,004 |
| `AMIE_PSEAE_Wrenbeck_2017` | AMIE aliphatic amidase | Hydrolase amidase | 6,227 |
| `Q59976_STRSQ_Romero_2015` | Beta-glucosidase | GH1 glycoside hydrolase | 2,999 |

## ESM-2 8M Results

| Dataset | Overall Spearman | Exact Site Spearman | Background Spearman | Best Mechanism Slice |
| --- | ---: | ---: | ---: | --- |
| TEM-1 | 0.4113 | 0.3023 | 0.4042 | Active-site neighborhood, 0.6453 |
| VIM-2 | 0.4305 | 0.3702 | 0.4123 | Active-site neighborhood, 0.6128 |
| AMIE | 0.3264 | 0.2057 | 0.3157 | Active-site neighborhood, 0.4092 |
| Beta-glucosidase | 0.1442 | 0.4196 | 0.1363 | AF2 catalytic shell, 0.3712 |

## Matched-Position Null Read

| Dataset | Exact Site | Structure Slice | Active-Site Neighborhood |
| --- | --- | --- | --- |
| TEM-1 | Inside null | Inside null | Higher than null, p = 0.002 |
| VIM-2 | Inside null | Higher than null, p = 0.000 | Higher than null, p = 0.012 |
| AMIE | Inside null | Inside null | Inside null |
| Beta-glucosidase | Inside null, p = 0.548 | Higher than null, p = 0.018 | Inside null, p = 0.210 |

## Interpretation

The four-enzyme 8M panel strengthens the main P0 theme:

> Average DMS correlation is not enough. The biologically interesting question is where inside the enzyme the model works or fails.

TEM-1 and VIM-2 show strong active-site-neighborhood signals at 8M. AMIE is a counterexample where the mechanism slices do not beat matched-position controls. Beta-glucosidase adds a different pattern: the overall score is low, but the structure-derived catalytic shell is unusually strong relative to matched controls.

This is the first hint that the best mechanism slice may differ by enzyme family:

- beta-lactamases: active-site neighborhood can be strong,
- AMIE: raw neighborhood signal exists but is not unusual under matched controls,
- beta-glucosidase: the AF2 catalytic shell is the strongest controlled slice.

## Artifacts

- `results/proteingym_four_enzyme_esm2_t6_8M_comparison.json`
- `results/proteingym_bgly_esm2_t6_8M/metrics.json`
- `docs/protein_gym_beta_glucosidase_result.md`
