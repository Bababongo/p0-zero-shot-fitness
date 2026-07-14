# P0 Final Report - Mechanism-Sliced Zero-Shot Fitness

## Executive Read

P0 asks:

> Do protein language models fail differently on catalytic residues than on the rest of the protein?

The answer is not a simple yes or no. Across four ProteinGym enzyme DMS assays, ESM-2 35M improves global zero-shot fitness prediction, but mechanism-local behavior is enzyme-specific. TEM-1 and VIM-2 show the strongest mechanism-local signals. AMIE and beta-glucosidase prevent overclaiming: larger ESM-2 models can improve global ranking without reliably improving catalytic-site or catalytic-shell ranking.

Best current claim:

> ESM-2 captures broad evolutionary and stability-like constraints across enzymes, but mechanism-aware residue slices reveal heterogeneous failure modes. The project supports mechanism-sliced evaluation as a necessary audit layer for enzyme engineering, not a blanket claim that protein language models understand catalysis.

## What Was Built

This repo implements a reproducible Python benchmark for enzyme variant-effect prediction:

- fixture-first tests for mutation parsing, scoring, metrics, and CLI behavior,
- real ProteinGym enzyme DMS inputs,
- ESM-2 masked-marginal zero-shot scoring,
- residue-slice labeling for catalytic residues, active-site neighborhoods, ligand/metal/catalytic shells, and background residues,
- matched residue-position null controls,
- covariate-matched controls for mutation coverage, DMS variance, model-score sensitivity, relative sequence position, structure contact density, and approximate solvent accessibility,
- MSA conservation baseline across all four enzymes,
- Savio/LBNL SLURM scripts for 35M model runs,
- public-facing reports and portfolio artifacts.

## Dataset Panel

| Dataset | Enzyme | Chemistry / Role | Single Mutants | Main Mechanism Slices |
| --- | --- | --- | ---: | --- |
| `BLAT_ECOLX_Firnberg_2014` | TEM-1 beta-lactamase | Serine beta-lactam hydrolysis | 4,783 | UniProt catalytic site, substrate-binding site, PDB ligand contacts, active-site neighborhood |
| `A4GRB6_PSEAI_Chen_2020` | VIM-2 metallo-beta-lactamase | Zinc-dependent beta-lactam hydrolysis | 5,004 | Metal-binding site, AF2 metal-site shell, 5ACX/WL3 inhibitor contact, active-site neighborhood |
| `AMIE_PSEAE_Wrenbeck_2017` | Aliphatic amidase | Amidase/nitrilase-like hydrolysis | 6,227 | Curated catalytic site, AF2 catalytic shell, active-site neighborhood |
| `Q59976_STRSQ_Romero_2015` | Beta-glucosidase | Glycoside hydrolysis | 2,999 | Curated catalytic site, AF2 catalytic shell, active-site neighborhood |

Total evaluated single mutants: 19,013.

## Scoring Approach

### ESM-2 Masked-Marginal Score

For a single mutation, the scorer masks the wild-type residue position, asks ESM-2 for amino-acid log probabilities at that masked position, and computes:

```text
score = log P(mutant amino acid at position) - log P(wild-type amino acid at position)
```

Higher scores should correspond to mutations that the model considers more plausible under its learned protein-sequence distribution.

### Placeholder Baseline

The placeholder scorer is a deterministic plumbing baseline. It is useful for verifying the pipeline, but it is not a scientific conservation model.

### MSA Conservation Baseline

This version adds a real MSA-conservation pathway:

- `src/p0_zero_shot_fitness/conservation.py`
- `scripts/derive_msa_conservation.py`
- `scripts/score_msa_conservation_baseline.py`
- `scripts/audit_msa_conservation_inputs.py`

The conservation scorer uses alignment-derived amino-acid frequencies:

```text
score = log frequency(mutant amino acid) - log frequency(wild-type amino acid)
```

Status: run on the four-enzyme panel using the official ProteinGym MSA bundle. Raw `.a2m` files are kept out of Git because they are large external source data; derived conservation profiles and result artifacts are stored in `results/`.

```text
results/proteingym_msa_conservation_status.json
```

The four MSA files used locally were:

- `BLAT_ECOLX_full_11-26-2021_b02.a2m`
- `A4GRB6_PSEAI_full_11-26-2021_b03.a2m`
- `AMIE_PSEAE_full_11-26-2021_b02.a2m`
- `Q59976_STRSQ_full_11-26-2021_b03.a2m`

ProteinGym A2M files include match-state and query-only/lowercase positions. The scorer maps covered match-state positions to real amino-acid frequencies and assigns neutral uniform frequencies to query-only positions, then records match-state coverage.

| Dataset | Match-State Coverage | ESM-2 35M Overall | MSA Overall | ESM-2 35M Catalytic | MSA Catalytic |
| --- | ---: | ---: | ---: | ---: | ---: |
| TEM-1 | 215 / 286 | 0.5548 | 0.4247 | 0.4596 | 0.4824 |
| VIM-2 | 193 / 266 | 0.5280 | 0.4931 | 0.3449 | 0.3079 |
| AMIE | 251 / 346 | 0.4082 | 0.4306 | 0.0911 | 0.2944 |
| Beta-glucosidase | 442 / 501 | 0.4481 | 0.5615 | 0.5105 | 0.4406 |

Interpretation: ESM-2 35M is strongest overall for TEM-1 and slightly ahead for VIM-2, while family-specific MSA conservation is stronger overall for AMIE and beta-glucosidase. This makes the benchmark sharper: the question is not just whether ESM-2 works, but whether it adds value beyond classical family conservation in the same mechanism slices.

## Metrics

Primary metrics:

- Spearman correlation between model score and experimental DMS fitness,
- Spearman within catalytic or mechanism-relevant residue groups,
- Spearman outside each mechanism group,
- top-k enrichment,
- mutation-class breakdown,
- bootstrap confidence intervals,
- matched null controls.

The central design choice is to evaluate not just "does the model work overall?" but:

> Where does it work, and where does it break relative to residues that matter mechanistically?

## Control Strategy

### Position-Matched Null

This asks whether a residue slice is unusual compared with random residue slices of the same size.

### Covariate-Matched Null

This asks whether a residue slice is unusual after matching residues by possible confounders:

| Control | Meaning |
| --- | --- |
| `mutation_count` | Same number of observed mutants per residue |
| `fitness_variance` | Similar experimental DMS spread |
| `fitness_distribution` | Similar local mean, spread, and range of DMS fitness |
| `model_score_sensitivity` | Similar local ESM score mean and spread |
| `relative_position` | Similar normalized sequence position |
| `structure_contact_density` | Similar C-beta/C-alpha contact density |
| `structure_solvent_accessibility` | Similar approximate residue solvent accessibility |
| `combined_available` | All available covariates together |

The new solvent-accessibility control uses a lightweight Shrake-Rupley-style approximation over PDB heavy atoms. It estimates residue solvent-accessible surface area and adds:

- `structure_sasa_approx`
- `structure_relative_sasa_approx`
- `structure_burial_approx`

## Four-Enzyme ESM-2 35M Results

| Dataset | Overall Spearman | Catalytic Spearman | Non-Catalytic Spearman |
| --- | ---: | ---: | ---: |
| TEM-1 | 0.5548 | 0.4596 | 0.5428 |
| VIM-2 | 0.5280 | 0.3449 | 0.5085 |
| AMIE | 0.4082 | 0.0911 | 0.3991 |
| Beta-glucosidase | 0.4481 | 0.5105 | 0.4434 |

Main read:

- ESM-2 35M gives useful global signal on all four enzymes.
- Catalytic-only slices are small and unstable.
- Mechanism-neighborhood or structure-shell slices are more informative than exact catalytic residues alone.

## Mechanism-Slice Readouts

### TEM-1

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Active-site neighborhood | 0.7027 | 0.5188 | 461 |
| Structure ligand contact, 5 A | 0.7127 | 0.5344 | 277 |

TEM-1 remains the clearest active-site-neighborhood case. The active-site neighborhood is higher than contact-density-matched controls (`p = 0.022`) and remains near the upper edge of the solvent-accessibility control (`p = 0.094`) and combined control (`p = 0.080`).

Interpretation: TEM-1 supports a mechanism-local signal, but the strictest controls make it a strong, careful result rather than an overconfident claim.

### VIM-2

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| 5ACX WL3 inhibitor contact, 5 A | 0.6613 | 0.5207 | 247 |
| Active-site neighborhood | 0.6133 | 0.4897 | 448 |
| Structure metal-site shell, 5 A | 0.5846 | 0.4778 | 802 |
| Curated metal-binding site | 0.3449 | 0.5085 | 113 |

VIM-2 now has the cleanest ligand-bound label upgrade in the panel: a 5ACX/WL3 inhibitor-contact group derived from experimental mmCIF coordinates using direct target-sequence numbering. It is the strongest raw VIM-2 mechanism slice at `0.6613`.

The controls make the read more cautious:

- position-matched null: inside, `p = 0.186`,
- solvent-accessibility matching: inside, `p = 0.092`,
- conservation-plus-SASA matching: inside, `p = 0.876`,
- strict combined covariate matching: inside, `p = 0.782`.

Interpretation: ESM-2 performs well in the VIM-2 ligand/metal neighborhood in raw correlation, but the strict controls say this is not enough to claim atomistic catalytic or ligand-chemistry understanding. The more defensible claim is that VIM-2 has strong mechanism-adjacent signal that overlaps with conservation and structural-exposure effects.

### AMIE

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Active-site neighborhood | 0.4335 | 0.3902 | 259 |
| Structure catalytic shell, 5 A | 0.3071 | 0.4069 | 621 |
| Curated catalytic site | 0.0911 | 0.3991 | 57 |

AMIE is a counterexample. The exact catalytic site is much weaker than the background and lower than the combined covariate-matched null (`p = 0.008`).

Interpretation: global sequence plausibility can improve while chemistry-critical positions remain poorly ranked.

### Beta-Glucosidase

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Active-site neighborhood | 0.4327 | 0.4341 | 60 |
| Structure catalytic shell, 5 A | 0.3808 | 0.4286 | 149 |
| Curated catalytic site | 0.5105 | 0.4434 | 12 |

Beta-glucosidase is a scale and control counterexample. The global 35M result is useful, but the catalytic shell does not clear position, contact-density, solvent-accessibility, or combined covariate controls.

Interpretation: scaling ESM-2 does not automatically produce stronger mechanism-slice behavior.

## Scientific Interpretation

P0 is strongest as an evaluation-design project.

The main contribution is not "ESM-2 solves enzyme design." It is:

> A protein language model can look good globally while having residue-class-specific strengths and failures. Enzyme projects should therefore evaluate model scores by mechanism-aware residue groups and matched controls, not only by whole-protein correlation.

The results suggest three kinds of behavior:

1. Broad global signal: all four enzymes show positive whole-protein Spearman.
2. Neighborhood signal: TEM-1 active-site neighborhood and VIM-2 ligand/metal neighborhoods show the strongest raw mechanism-local lifts.
3. Mechanism failure or ambiguity: AMIE and beta-glucosidase show that catalytic sites and catalytic shells can remain weak despite global model utility.

## What Is Novel Enough

This is not a new foundation model. It is a portfolio-scale scientific benchmark with a sharper question than "run ESM on DMS."

Novelty comes from:

- mechanism-sliced zero-shot evaluation,
- multi-enzyme panel design,
- matched null controls,
- explicit separation between exact catalytic residues, active-site neighborhoods, and structure-derived shells,
- showing positive and negative cases,
- running true MSA conservation baselines and SASA-matched controls,
- adding conservation-plus-SASA matched controls to test whether mechanism slices remain unusual after matching both family conservation and structural exposure,
- adding an experimental 5ACX/WL3 ligand-bound VIM-2 contact group with mmCIF target-sequence mapping.

The intellectual move is to treat zero-shot PLM scores as something to audit mechanistically, not just leaderboard-rank globally.

## Limitations

- Raw ProteinGym MSA files are external and intentionally not committed; derived conservation profiles are committed.
- AMIE catalytic labels are now UniProt P11436-backed, but substrate-pocket labels beyond the catalytic triad remain future work.
- VIM-2 exact metal-site labels are supported by VIM-2 reference records and PDB-backed structure features, and the WL3 contact group is supported by RCSB 5ACX. A4GRB6 itself is inactive/deleted in UniProt and the ProteinGym sequence differs from reviewed Q5U7L7 at one non-site residue.
- TEM-1 ligand contacts use one structure/contact rule and could be expanded to multiple ligand-bound structures.
- Approximate SASA is useful for control matching but not a substitute for a dedicated structural-biology package.
- Spearman on exact catalytic residues can be noisy because the number of catalytic positions is small.
- The conservation-plus-SASA control is a matched-null analysis, not a prospective supervised model; it controls interpretation of mechanism slices rather than replacing ESM-2 as a global predictor.

## Reproducibility

Core tests:

```bash
python -m pytest
```

Regenerate structure covariates:

```bash
python scripts/derive_position_covariates.py \
  --scored-variants-csv results/proteingym_blat_esm2_t12_35M/scored_variants.csv \
  --output-json results/proteingym_blat_esm2_t12_35M/position_covariates.json \
  --dataset-name "ProteinGym BLAT_ECOLX_Firnberg_2014" \
  --pdb data/proteingym/structures/1M40.pdb \
  --conservation-json results/proteingym_blat_msa_conservation/conservation.json
```

Audit MSA availability:

```bash
python scripts/audit_msa_conservation_inputs.py \
  --output-json results/proteingym_msa_conservation_status.json
```

Regenerate the MSA baseline after staging ProteinGym MSA files locally:

```bash
python scripts/derive_msa_conservation.py \
  --msa-a2m data/proteingym/msas/BLAT_ECOLX_full_11-26-2021_b02.a2m \
  --wild-type-fasta data/proteingym/BLAT_ECOLX.fasta \
  --output-json results/proteingym_blat_msa_conservation/conservation.json \
  --dataset-name "ProteinGym BLAT_ECOLX_Firnberg_2014"

python scripts/score_msa_conservation_baseline.py \
  --scored-variants-csv results/proteingym_blat_esm2_t12_35M/scored_variants.csv \
  --conservation-json results/proteingym_blat_msa_conservation/conservation.json \
  --output-dir results/proteingym_blat_msa_conservation \
  --dataset-name "ProteinGym BLAT_ECOLX_Firnberg_2014"
```

## Interview-Ready Explanation

If asked what P0 proves:

> I built a zero-shot enzyme fitness benchmark around a mechanism-aware question. Instead of only asking whether ESM-2 correlates with DMS fitness globally, I split residues into catalytic sites, active-site neighborhoods, ligand or metal shells, and background residues. Then I added matched null controls so I could tell whether a mechanism slice was genuinely unusual or just confounded by mutation coverage, variance, model-score spread, position, burial, conservation, or solvent exposure. The result is nuanced: ESM-2 35M works globally across four enzymes, VIM-2 and TEM-1 show the strongest raw mechanism-local signals, and AMIE/beta-glucosidase show that PLMs can still fail on chemistry-relevant residues.

If asked what you would improve next:

> I would next add ProteinMPNN as a structure-conditioned baseline. The current project already compares ESM-2 against MSA conservation and conservation-plus-SASA controls, so ProteinMPNN is the cleaner next model-family test: it asks whether a fixed-backbone inverse-folding model sees the same catalytic, ligand-contact, and metal-shell signals. I would only add MSA Transformer after that if ProteinMPNN leaves a specific ambiguity about MSA-aware neural models.
