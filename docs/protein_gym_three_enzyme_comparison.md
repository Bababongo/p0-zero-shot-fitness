# ProteinGym Three-Enzyme Comparison

## Purpose

This comparison turns P0 from a single-enzyme case study into the beginning of a mechanism-stratified enzyme benchmark.

The core question is:

> Across enzyme DMS landscapes, do protein language models show different performance in exact catalytic residues, active-site neighborhoods, structure-derived mechanism shells, and non-mechanistic background residues?

## Enzymes

| Dataset | Enzyme | Mechanism Class | Variants |
| --- | --- | --- | ---: |
| `BLAT_ECOLX_Firnberg_2014` | TEM-1 beta-lactamase | Serine beta-lactamase | 4,783 |
| `A4GRB6_PSEAI_Chen_2020` | VIM-2 beta-lactamase | Metallo-beta-lactamase | 5,004 |
| `AMIE_PSEAE_Wrenbeck_2017` | AMIE aliphatic amidase | Hydrolase amidase | 6,227 |

## ESM-2 8M Results

| Dataset | Overall Spearman | Exact Site Spearman | Background Spearman | Best Mechanism Slice |
| --- | ---: | ---: | ---: | --- |
| TEM-1 | 0.4113 | 0.3023 | 0.4042 | Active-site neighborhood, 0.6453 |
| VIM-2 | 0.4305 | 0.3702 | 0.4123 | Active-site neighborhood, 0.6128 |
| AMIE | 0.3264 | 0.2057 | 0.3157 | Active-site neighborhood, 0.4092 |

## Matched-Position Null Read

| Dataset | Exact Site | Structure Slice | Active-Site Neighborhood |
| --- | --- | --- | --- |
| TEM-1 | Inside null | Inside null | Higher than null, p = 0.002 |
| VIM-2 | Inside null | Higher than null, p = 0.000 | Higher than null, p = 0.012 |
| AMIE | Inside null | Inside null | Inside null |

## Interpretation

The strongest current claim is not "ESM fails at catalytic residues."

The stronger and more defensible claim is:

> Exact catalytic-site slices are usually too sparse and noisy to interpret alone. Broader active-site neighborhoods often show stronger model signal, but the strength of that signal is enzyme-dependent and must be tested against matched-position null controls.

TEM-1 and VIM-2 support the functional-neighborhood hypothesis. AMIE adds a useful counterweight: it shows an active-site-neighborhood lift relative to the outside background, but not relative to matched random residue groups.

## Artifacts

- `results/proteingym_three_enzyme_esm2_t6_8M_comparison.json`
- `results/proteingym_blat_esm2_t6_8M/metrics.json`
- `results/proteingym_vim2_esm2_t6_8M/metrics.json`
- `results/proteingym_amie_esm2_t6_8M/metrics.json`

