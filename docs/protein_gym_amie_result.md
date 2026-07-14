# ProteinGym AMIE Result

## Question

Do protein language models fail differently on catalytic residues than on the rest of the protein?

## Why AMIE Was Added

TEM-1 and VIM-2 are both beta-lactamases. AMIE aliphatic amidase adds a non-beta-lactamase hydrolase case, which makes P0 a stronger test of whether residue-zone behavior generalizes beyond one enzyme family.

This is the first non-beta-lactamase enzyme case in the P0 v3 panel.

## Dataset

- ProteinGym dataset: `AMIE_PSEAE_Wrenbeck_2017`
- Protein: AMIE aliphatic amidase
- ProteinGym protein ID: `AMIE_PSEAE`
- Variants: 6,227 single mutants
- Assay context: enzyme activity
- Scorers: placeholder conservation scorer and ESM-2 8M masked-marginal scorer

## Residue Labels

The exact curated catalytic-site labels are:

```text
[59, 134, 166]
```

These are 1-indexed positions in the 346-aa ProteinGym target sequence.

Important caveat: these AMIE labels are conservative nitrilase-like motif and AF2-geometry annotations. They are not currently presented as UniProt-backed AMIE feature labels. The AF2 structure places Cys166 close to Glu59 and Lys134, supporting the local catalytic-geometry hypothesis, but a future pass should upgrade the provenance with a stronger AMIE-specific primary source or experimental structure.

The structure-derived upgrade is:

- `structure_catalytic_shell_5a`: residues with any heavy atom within 5.0 Angstrom of any curated catalytic-site residue heavy atom in the ProteinGym AF2 structure.

## Placeholder Baseline Result

Command:

```bash
p0-fitness \
  --preset proteingym-amie \
  --output-dir results/proteingym_amie_placeholder \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

Metrics:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | -0.0040 | - | 6,227 |
| Curated catalytic site | 0.1202 | -0.0116 | 57 |
| AF2 catalytic shell, 5 A | 0.1723 | -0.0165 | 621 |
| Active-site neighborhood | 0.2125 | -0.0124 | 259 |

Matched-position null result:

| Slice | Observed Spearman | Null Mean | Null 95% Interval | Empirical p | Direction |
| --- | ---: | ---: | ---: | ---: | --- |
| Curated catalytic site | 0.1202 | 0.0122 | -0.4818 to 0.4568 | 0.722 | inside null |
| AF2 catalytic shell, 5 A | 0.1723 | -0.0115 | -0.1498 to 0.1245 | 0.004 | higher than null |
| Active-site neighborhood | 0.2125 | -0.0130 | -0.2286 to 0.2084 | 0.048 | higher than null |

## ESM-2 8M Result

Command:

```bash
p0-fitness \
  --preset proteingym-amie \
  --scorer esm2 \
  --esm-model esm2_t6_8M_UR50D \
  --output-dir results/proteingym_amie_esm2_t6_8M \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

Metrics:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.3264 | - | 6,227 |
| Curated catalytic site | 0.2057 | 0.3157 | 57 |
| AF2 catalytic shell, 5 A | 0.2630 | 0.3152 | 621 |
| Active-site neighborhood | 0.4092 | 0.3017 | 259 |

Bootstrap intervals:

| Slice | Spearman | 95% Bootstrap CI |
| --- | ---: | ---: |
| Overall | 0.3264 | 0.3047 to 0.3500 |
| Curated catalytic site | 0.2057 | -0.1283 to 0.5028 |
| Non-catalytic background | 0.3157 | 0.2909 to 0.3380 |
| AF2 catalytic shell, 5 A | 0.2630 | 0.1885 to 0.3313 |
| Outside AF2 catalytic shell | 0.3152 | 0.2904 to 0.3394 |
| Active-site neighborhood | 0.4092 | 0.3103 to 0.5144 |
| Outside active-site neighborhood | 0.3017 | 0.2749 to 0.3248 |

Matched-position null result:

| Slice | Observed Spearman | Null Mean | Null 95% Interval | Empirical p | Direction |
| --- | ---: | ---: | ---: | ---: | --- |
| Curated catalytic site | 0.2057 | 0.2631 | -0.3958 to 0.7488 | 0.784 | inside null |
| AF2 catalytic shell, 5 A | 0.2630 | 0.3126 | 0.1148 to 0.4835 | 0.598 | inside null |
| Active-site neighborhood | 0.4092 | 0.2972 | -0.0113 to 0.5694 | 0.450 | inside null |

## Interpretation

AMIE is useful because it does not simply repeat the TEM-1 and VIM-2 story.

ESM-2 8M has meaningful overall zero-shot signal on AMIE, but the exact catalytic site and AF2 catalytic shell are weaker than the non-catalytic background. The active-site-neighborhood slice is higher than its outside background, but it is not higher than same-size matched random residue-position controls.

That makes the current three-enzyme story more honest:

- TEM-1 and VIM-2 show unusually strong active-site-neighborhood signal.
- AMIE shows an active-site-neighborhood lift, but not a matched-null significant lift.
- Exact catalytic-site slices remain small, noisy, and easy to overclaim.

## ESM-2 35M Result

Command:

```bash
p0-fitness \
  --preset proteingym-amie \
  --scorer esm2 \
  --esm-model esm2_t12_35M_UR50D \
  --output-dir results/proteingym_amie_esm2_t12_35M \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

Metrics:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.4082 | - | 6,227 |
| Curated catalytic site | 0.0911 | 0.3991 | 57 |
| AF2 catalytic shell, 5 A | 0.3071 | 0.4069 | 621 |
| Active-site neighborhood | 0.4335 | 0.3902 | 259 |

Matched-position null result:

| Slice | Observed Spearman | Null Mean | Null 95% Interval | Empirical p | Direction |
| --- | ---: | ---: | ---: | ---: | --- |
| Curated catalytic site | 0.0911 | 0.3343 | -0.3468 to 0.7840 | 0.408 | inside null |
| AF2 catalytic shell, 5 A | 0.3071 | 0.4041 | 0.2187 to 0.5722 | 0.312 | inside null |
| Active-site neighborhood | 0.4335 | 0.3812 | 0.0841 to 0.6191 | 0.778 | inside null |

## 35M Interpretation

The 35M model improves AMIE overall performance from 0.3264 to 0.4082. The active-site neighborhood also increases slightly from 0.4092 to 0.4335.

The exact catalytic-site slice remains weak, and every AMIE mechanism slice remains inside the matched-position null interval. This makes AMIE the clearest counterexample in the current panel: model scale helps globally, but it does not automatically make catalytic or mechanism-adjacent slices unusually strong.

## Next Step

Upgrade AMIE label provenance, then add conservation-matched and solvent-accessibility-matched controls. AMIE should stay in the panel because it prevents the project from overclaiming a pattern that only holds cleanly in TEM-1.
