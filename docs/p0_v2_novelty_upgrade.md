# P0 v2 Novelty Upgrade: Matched Residue-Position Null Controls

## What Changed

P0 v1 asked:

> Do protein language models fail differently on catalytic residues than on the rest of the protein?

P0 v2 sharpens that into a more defensible research question:

> Are catalytic and mechanism-relevant residue slices unusual compared with random residue-position slices of the same size?

This matters because the exact UniProt active-site slice in TEM-1 beta-lactamase is tiny: 4 residue positions and 57 variants. A reviewer can reasonably ask whether any difference is biology, model behavior, or small-sample noise.

The new v2 metric answers that by building a matched null control.

## The New Control

For each biologically defined residue slice, P0 now:

1. Counts how many residue positions are in the slice.
2. Samples random residue-position sets of the same size.
3. Recomputes Spearman correlation for each random set.
4. Compares the observed slice Spearman against that null distribution.

This is not a new model. It is a better evaluation design.

## Command

```bash
p0-fitness \
  --preset proteingym-blat \
  --scorer esm2 \
  --esm-model esm2_t12_35M_UR50D \
  --output-dir results/proteingym_blat_esm2_t12_35M \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

For existing scored variants, the same metric can be added without rerunning ESM:

```bash
python scripts/refresh_metrics_from_scored_variants.py \
  --metrics-json results/proteingym_blat_esm2_t12_35M/metrics.json \
  --scored-variants-csv results/proteingym_blat_esm2_t12_35M/scored_variants.csv \
  --catalytic-json data/proteingym/BLAT_ECOLX_catalytic_residues.json \
  --residue-groups-json data/proteingym/BLAT_ECOLX_residue_groups.json \
  --bootstrap-iterations 1000 \
  --null-iterations 1000
```

## Main Result

The strongest new result is:

> The active-site-neighborhood slice is higher than matched random residue-position controls for both ESM-2 8M and ESM-2 35M.

That is more novel than simply saying "active-site residues are lower than non-active-site residues."

## Matched Null Results

| Model | Slice | Observed Spearman | Null Mean | Null 95% Interval | Empirical p | Direction |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| ESM-2 8M | UniProt active site | 0.3023 | 0.3912 | -0.1961 to 0.7948 | 0.680 | inside null |
| ESM-2 8M | PDB ligand contact, 5 A | 0.6076 | 0.3912 | 0.0964 to 0.6385 | 0.082 | inside null |
| ESM-2 8M | Active-site neighborhood | 0.6453 | 0.3726 | 0.1614 to 0.5519 | 0.002 | higher than null |
| ESM-2 35M | UniProt active site | 0.4596 | 0.5245 | 0.0273 to 0.8356 | 0.668 | inside null |
| ESM-2 35M | PDB ligand contact, 5 A | 0.7127 | 0.5303 | 0.2820 to 0.7227 | 0.070 | inside null |
| ESM-2 35M | Active-site neighborhood | 0.7027 | 0.5148 | 0.3188 to 0.6781 | 0.012 | higher than null |

## Updated Scientific Interpretation

The exact UniProt active-site-only slice is too small to support a strong standalone claim about model failure. It is lower than the non-active-site background, but it is not unusual relative to same-size random residue-position controls.

The active-site-neighborhood slice is different. It is larger, mechanism-adjacent, and consistently higher than matched position controls. This suggests that ESM-2 has strong signal around the functional neighborhood of the enzyme, even if exact catalytic residues remain hard to interpret statistically.

The ligand-contact slice trends high but remains inside the matched null interval in this first TEM-1-only analysis.

## Why This Makes P0 More Novel

P0 is no longer only a zero-shot ESM benchmark. It is now a mechanism-stratified model behavior audit with a matched null control.

The research contribution becomes:

> Aggregate protein language model performance can hide residue-zone-specific behavior, and mechanism-relevant neighborhoods should be tested against matched random residue-position controls before making claims about active-site failure.

## What This Does Not Prove Yet

This is still one enzyme and one DMS landscape. It does not yet prove a universal law about protein language models.

The next step toward publishable novelty is to repeat this analysis across an enzyme panel:

- TEM-1 beta-lactamase
- kinases
- proteases
- metabolic enzymes
- ligand/cofactor-dependent enzymes

Each enzyme should have:

- DMS or multiplexed variant-effect data,
- curated catalytic residues,
- substrate/ligand-contact labels,
- active-site-neighborhood labels,
- matched residue-position null controls.

## Interview Version

> I upgraded P0 from a simple active-site-vs-background benchmark into a matched-null model behavior audit. The key issue was that catalytic residues are a tiny slice, so I added random residue-position controls matched by slice size. That changed the scientific story: exact active-site residues are not statistically unusual compared with same-size random groups, but the active-site neighborhood is consistently higher than matched null controls for both ESM-2 8M and 35M. The result is more honest and more interesting: sequence-only models may capture functional neighborhood constraints better than exact catalytic chemistry.

