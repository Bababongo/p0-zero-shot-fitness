# ProteinGym Three-Enzyme Comparison

## Purpose

This comparison turns P0 from a single-enzyme case study into the beginning of a mechanism-stratified enzyme benchmark.

The core question is:

> Across enzyme DMS landscapes, do protein language models show different performance in exact catalytic residues, active-site neighborhoods, structure-derived mechanism shells, and non-mechanistic background residues?

For the fourth-enzyme extensions with beta-glucosidase, see [ProteinGym Four-Enzyme ESM-2 8M Comparison](protein_gym_four_enzyme_8m_comparison.md) and [ProteinGym Four-Enzyme ESM-2 35M Comparison](protein_gym_four_enzyme_35m_comparison.md).

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

## ESM-2 35M Results

| Dataset | Overall Spearman | Exact Site Spearman | Background Spearman | Best Mechanism Slice |
| --- | ---: | ---: | ---: | --- |
| TEM-1 | 0.5548 | 0.4596 | 0.5428 | PDB ligand contact, 0.7127; active-site neighborhood, 0.7027 |
| VIM-2 | 0.5280 | 0.3449 | 0.5085 | WL3 inhibitor contact, 0.6613; active-site neighborhood, 0.6133; metal-site shell, 0.5846 |
| AMIE | 0.4082 | 0.0911 | 0.3991 | Active-site neighborhood, 0.4335 |

## 8M To 35M Scaling Read

| Dataset | 8M Overall | 35M Overall | Change | Most Important 35M Observation |
| --- | ---: | ---: | ---: | --- |
| TEM-1 | 0.4113 | 0.5548 | +0.1435 | Active-site neighborhood remains higher than matched null controls. |
| VIM-2 | 0.4305 | 0.5280 | +0.0975 | WL3 inhibitor contact, active-site neighborhood, and metal shell remain strong in raw Spearman, but fall inside matched controls. |
| AMIE | 0.3264 | 0.4082 | +0.0818 | Overall performance improves, but exact catalytic-site performance remains weak. |

## ESM-2 8M Matched-Position Null Read

| Dataset | Exact Site | Structure Slice | Active-Site Neighborhood |
| --- | --- | --- | --- |
| TEM-1 | Inside null | Inside null | Higher than null, p = 0.002 |
| VIM-2 | Inside null | Higher than null, p = 0.000 | Higher than null, p = 0.012 |
| AMIE | Inside null | Inside null | Inside null |

## ESM-2 35M Matched-Position Null Read

| Dataset | Exact Site | Structure Slice | Active-Site Neighborhood |
| --- | --- | --- | --- |
| TEM-1 | Inside null, p = 0.668 | Inside null, p = 0.070 | Higher than null, p = 0.012 |
| VIM-2 | Inside null, p = 0.476 | Inside null, p = 0.084 | Inside null, p = 0.142 |
| AMIE | Inside null, p = 0.408 | Inside null, p = 0.312 | Inside null, p = 0.778 |

## Interpretation

The strongest current claim is not "ESM fails at catalytic residues."

The stronger and more defensible claim is:

> Exact catalytic-site slices are usually too sparse and noisy to interpret alone. Broader active-site neighborhoods often show stronger model signal, but the strength of that signal is enzyme-dependent and must be tested against matched-position null controls.

The 35M scaling run strengthens the global zero-shot result while narrowing the mechanistic claim. TEM-1 still supports the functional-neighborhood hypothesis after matched controls. VIM-2 and AMIE show useful raw active-site-neighborhood signal, but their 35M mechanism slices are inside matched-position null intervals.

The mature claim is therefore:

> Scaling improves global zero-shot performance, but exact catalytic chemistry remains harder than broader sequence and structure constraints. Broad mechanism neighborhoods can be strong, but matched-position controls show that the effect is enzyme-dependent, not automatic.

## Artifacts

- `results/proteingym_three_enzyme_esm2_t6_8M_comparison.json`
- `results/proteingym_three_enzyme_esm2_t12_35M_comparison.json`
- `results/proteingym_blat_esm2_t6_8M/metrics.json`
- `results/proteingym_vim2_esm2_t6_8M/metrics.json`
- `results/proteingym_amie_esm2_t6_8M/metrics.json`
- `results/proteingym_blat_esm2_t12_35M/metrics.json`
- `results/proteingym_vim2_esm2_t12_35M/metrics.json`
- `results/proteingym_amie_esm2_t12_35M/metrics.json`
