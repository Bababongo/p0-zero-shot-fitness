# ProteinGym VIM-2 Result

## Question

Do protein language models fail differently on catalytic residues than on the rest of the protein?

## Why VIM-2 Was Added

TEM-1 beta-lactamase is a serine beta-lactamase. VIM-2 is a metallo-beta-lactamase. Adding VIM-2 tests whether the P0 residue-zone framework can move from serine-based catalysis to metal-dependent beta-lactamase chemistry.

This is the first second-enzyme case in the P0 v3 panel.

## Dataset

- ProteinGym dataset: `A4GRB6_PSEAI_Chen_2020`
- Protein: VIM-2 metallo-beta-lactamase
- ProteinGym protein ID: `A4GRB6_PSEAI`
- Variants: 5,004 single mutants
- Assay context: beta-lactam antibiotic resistance
- Scorers: placeholder conservation scorer and ESM-2 8M masked-marginal scorer

## Residue Labels

The exact curated metal-binding/catalytic-site labels are:

```text
[114, 116, 118, 179, 198, 240]
```

These are 1-indexed positions in the 266-aa ProteinGym target sequence.

Structure-derived upgrade:

UniProt accession A4GRB6 is inactive/deleted, so this VIM-2 benchmark uses transparent conserved B1 metallo-beta-lactamase motif curation rather than UniProt feature annotations. It now also adds a ProteinGym AF2-derived `structure_metal_site_shell_5a` group: residues with any heavy atom within 5.0 Angstrom of any curated metal-binding residue heavy atom.

Important caveat: this structure shell is not a ligand-bound experimental contact map. It is a structure-derived metal-site proximity slice.

## Placeholder Baseline Result

Command:

```bash
p0-fitness \
  --preset proteingym-vim2 \
  --output-dir results/proteingym_vim2_placeholder \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

Metrics:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.0194 | - | 5,004 |
| Curated metal-binding site | 0.1214 | 0.0045 | 113 |
| AF2 structure metal-site shell, 5 A | 0.1720 | -0.0236 | 802 |
| Active-site neighborhood | 0.2003 | -0.0006 | 448 |

Matched-position null result:

| Slice | Observed Spearman | Null Mean | Null 95% Interval | Empirical p | Direction |
| --- | ---: | ---: | ---: | ---: | --- |
| Curated metal-binding site | 0.1214 | 0.0141 | -0.3536 to 0.4080 | 0.606 | inside null |
| AF2 structure metal-site shell, 5 A | 0.1720 | -0.0260 | -0.1491 to 0.0978 | 0.000 | higher than null |
| Active-site neighborhood | 0.2003 | -0.0009 | -0.1638 to 0.1883 | 0.030 | higher than null |

## Placeholder Interpretation

This is not the final scientific model result because the placeholder scorer is deliberately simple.

What this result proves:

- VIM-2 data ingestion works.
- VIM-2 mutation parsing works.
- VIM-2 curated residue labels work.
- Bootstrap intervals and matched-position null controls run on a second enzyme.
- P0 is no longer structurally hard-coded to TEM-1.

What it does not prove yet:

- It does not prove the active-site-neighborhood signal generalizes.
- It now includes an AF2 structure-derived metal-site shell, but not an experimental ligand-bound contact map.

## ESM-2 8M Result

Command:

```bash
p0-fitness \
  --preset proteingym-vim2 \
  --scorer esm2 \
  --esm-model esm2_t6_8M_UR50D \
  --output-dir results/proteingym_vim2_esm2_t6_8M \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

Metrics:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.4305 | - | 5,004 |
| Curated metal-binding site | 0.3702 | 0.4123 | 113 |
| AF2 structure metal-site shell, 5 A | 0.5734 | 0.3843 | 802 |
| Active-site neighborhood | 0.6128 | 0.3936 | 448 |

Bootstrap intervals:

| Slice | Spearman | 95% Bootstrap CI |
| --- | ---: | ---: |
| Overall | 0.4305 | 0.4075 to 0.4522 |
| Curated metal-binding site | 0.3702 | 0.2081 to 0.5020 |
| Non-metal-site background | 0.4123 | 0.3859 to 0.4361 |
| AF2 structure metal-site shell, 5 A | 0.5734 | 0.5232 to 0.6230 |
| Outside AF2 structure shell | 0.3843 | 0.3565 to 0.4095 |
| Active-site neighborhood | 0.6128 | 0.5422 to 0.6720 |
| Outside active-site neighborhood | 0.3936 | 0.3692 to 0.4180 |

Matched-position null result:

| Slice | Observed Spearman | Null Mean | Null 95% Interval | Empirical p | Direction |
| --- | ---: | ---: | ---: | ---: | --- |
| Curated metal-binding site | 0.3702 | 0.3830 | -0.0700 to 0.7427 | 0.896 | inside null |
| AF2 structure metal-site shell, 5 A | 0.5734 | 0.3821 | 0.2323 to 0.5188 | 0.000 | higher than null |
| Active-site neighborhood | 0.6128 | 0.3827 | 0.1787 to 0.5736 | 0.012 | higher than null |

## Updated Interpretation

ESM-2 8M has meaningful zero-shot signal on VIM-2 overall. The exact curated metal-binding-site slice is positive but inside the same-size random-position null, which means it should not be overinterpreted by itself.

The AF2 structure metal-site shell and active-site-neighborhood slices are the stronger results: ESM-2 is substantially better there than outside those groups, and both are higher than same-size random residue-position controls.

This mirrors the TEM-1 pattern: the exact catalytic or metal-site slice is small and hard to interpret alone, while the broader functional neighborhood shows a stronger and more reproducible signal.

## Next Step

Run a larger ESM-2 model for VIM-2 model-size comparison. A ligand-bound experimental contact group remains a later upgrade if a suitable VIM-2 structure and ligand/contact rule are selected.
