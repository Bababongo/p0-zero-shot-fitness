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
- Scorers: placeholder conservation scorer, ESM-2 8M masked-marginal scorer, and ESM-2 35M masked-marginal scorer

## Residue Labels

The exact curated metal-binding/catalytic-site labels are:

```text
[114, 116, 118, 179, 198, 240]
```

These are 1-indexed positions in the 266-aa ProteinGym target sequence.

Structure-derived upgrades:

UniProt accession A4GRB6 is inactive/deleted, so this VIM-2 benchmark uses transparent conserved B1 metallo-beta-lactamase motif curation rather than UniProt feature annotations. It now also adds a ProteinGym AF2-derived `structure_metal_site_shell_5a` group: residues with any heavy atom within 5.0 Angstrom of any curated metal-binding residue heavy atom.

It also adds an experimental ligand-bound contact group from RCSB 5ACX, a VIM-2 structure crystallized with the WL3 inhibitor. The group is named `structure_wl3_inhibitor_contact_5a` and contains residues with any protein heavy atom within 5.0 Angstrom of WL3 heavy atoms. The script uses mmCIF `label_seq_id` numbering so structure residues map directly back to the 266-aa ProteinGym target sequence.

```text
[62, 67, 87, 116, 117, 118, 179, 198, 201, 205, 209, 210, 240]
```

Chain A and chain B in 5ACX produced the same target-position set. The source record is `data/proteingym/source_records/5ACX_WL3_contacts_5A.json`.

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
| 5ACX WL3 inhibitor contact, 5 A | 0.3257 | 0.0022 | 247 |
| AF2 structure metal-site shell, 5 A | 0.1720 | -0.0236 | 802 |
| Active-site neighborhood | 0.2003 | -0.0006 | 448 |

Matched-position null result:

| Slice | Observed Spearman | Null Mean | Null 95% Interval | Empirical p | Direction |
| --- | ---: | ---: | ---: | ---: | --- |
| Curated metal-binding site | 0.1214 | 0.0141 | -0.3536 to 0.4080 | 0.606 | inside null |
| 5ACX WL3 inhibitor contact, 5 A | 0.3257 | 0.0026 | -0.2522 to 0.2609 | 0.022 | higher than null |
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
- It now includes both an AF2 structure-derived metal-site shell and an experimental 5ACX/WL3 ligand-bound contact map.

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
| 5ACX WL3 inhibitor contact, 5 A | 0.4841 | 0.4316 | 247 |
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
| 5ACX WL3 inhibitor contact, 5 A | 0.4841 | 0.4188 | 0.1224 to 0.6421 | 0.668 | inside null |
| AF2 structure metal-site shell, 5 A | 0.5734 | 0.3821 | 0.2323 to 0.5188 | 0.000 | higher than null |
| Active-site neighborhood | 0.6128 | 0.3827 | 0.1787 to 0.5736 | 0.012 | higher than null |

## Updated Interpretation

ESM-2 8M has meaningful zero-shot signal on VIM-2 overall. The exact curated metal-binding-site slice is positive but inside the same-size random-position null, which means it should not be overinterpreted by itself.

The AF2 structure metal-site shell and active-site-neighborhood slices are the stronger results: ESM-2 is substantially better there than outside those groups, and both are higher than same-size random residue-position controls.

This mirrors the TEM-1 pattern: the exact catalytic or metal-site slice is small and hard to interpret alone, while the broader functional neighborhood shows a stronger and more reproducible signal.

## ESM-2 35M Result

Command:

```bash
p0-fitness \
  --preset proteingym-vim2 \
  --scorer esm2 \
  --esm-model esm2_t12_35M_UR50D \
  --output-dir results/proteingym_vim2_esm2_t12_35M \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

Metrics:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.5280 | - | 5,004 |
| Curated metal-binding site | 0.3449 | 0.5085 | 113 |
| 5ACX WL3 inhibitor contact, 5 A | 0.6613 | 0.5207 | 247 |
| AF2 structure metal-site shell, 5 A | 0.5846 | 0.4778 | 802 |
| Active-site neighborhood | 0.6133 | 0.4897 | 448 |

Matched-position null result:

| Slice | Observed Spearman | Null Mean | Null 95% Interval | Empirical p | Direction |
| --- | ---: | ---: | ---: | ---: | --- |
| Curated metal-binding site | 0.3449 | 0.4739 | 0.0464 to 0.7853 | 0.476 | inside null |
| 5ACX WL3 inhibitor contact, 5 A | 0.6613 | 0.5053 | 0.2484 to 0.7076 | 0.186 | inside null |
| AF2 structure metal-site shell, 5 A | 0.5846 | 0.4735 | 0.3448 to 0.5985 | 0.084 | inside null, near high edge |
| Active-site neighborhood | 0.6133 | 0.4809 | 0.2821 to 0.6508 | 0.142 | inside null |

## 35M Interpretation

The 35M model improves VIM-2 overall performance from 0.4305 to 0.5280. The new 5ACX/WL3 inhibitor-contact group is the strongest raw VIM-2 slice at 0.6613, but it remains inside the same-size matched-position null and inside the stricter conservation-plus-SASA control.

This weakens a simple "VIM-2 mechanism neighborhoods are always unusually high" claim, but it strengthens the project scientifically. The result now says that model scale improves global zero-shot fitness prediction while exact metal-binding chemistry remains difficult, and that even experimentally ligand-bound pocket slices need matched controls rather than only outside-background comparisons.

## Next Step

The ligand-bound VIM-2 contact-label upgrade is complete. The next VIM-2-specific upgrade is model-family comparison: test whether a ProteinMPNN structure-conditioned baseline behaves differently on the exact metal site, AF2 metal shell, and 5ACX/WL3 inhibitor-contact group.
