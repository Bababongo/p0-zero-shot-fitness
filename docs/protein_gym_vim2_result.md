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
- Current scorer: placeholder conservation scorer

## Residue Labels

The exact curated metal-binding/catalytic-site labels are:

```text
[114, 116, 118, 179, 198, 240]
```

These are 1-indexed positions in the 266-aa ProteinGym target sequence.

Important caveat:

UniProt accession A4GRB6 is inactive/deleted, so this first VIM-2 benchmark uses transparent conserved B1 metallo-beta-lactamase motif curation rather than UniProt feature annotations. This should be upgraded with structure-derived labels before making stronger biological claims.

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
| Active-site neighborhood | 0.2003 | -0.0006 | 448 |

Matched-position null result:

| Slice | Observed Spearman | Null Mean | Null 95% Interval | Empirical p | Direction |
| --- | ---: | ---: | ---: | ---: | --- |
| Curated metal-binding site | 0.1214 | 0.0141 | -0.3536 to 0.4080 | 0.606 | inside null |
| Active-site neighborhood | 0.2003 | -0.0009 | -0.1638 to 0.1883 | 0.030 | higher than null |

## Interpretation

This is not the final scientific model result because the placeholder scorer is deliberately simple.

What this result proves:

- VIM-2 data ingestion works.
- VIM-2 mutation parsing works.
- VIM-2 curated residue labels work.
- Bootstrap intervals and matched-position null controls run on a second enzyme.
- P0 is no longer structurally hard-coded to TEM-1.

What it does not prove yet:

- It does not show how ESM-2 behaves on VIM-2.
- It does not prove the active-site-neighborhood signal generalizes.
- It does not yet include structure-derived ligand or substrate contact labels.

## Next Step

Run ESM-2 on `A4GRB6_PSEAI_Chen_2020`, then compare the VIM-2 residue-zone pattern against the TEM-1 result.
