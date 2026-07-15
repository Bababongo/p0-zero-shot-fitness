# P0 Extensive Project Report: Zero-Shot Fitness

Report date: 2026-07-14

Project repository: `p0-zero-shot-fitness`

Core question:

> Do protein language models fail differently on catalytic residues than on the rest of the protein?

## 1. Executive Summary

P0 is a benchmark project that evaluates whether a protein language model can predict experimental mutation effects equally well across different biological regions of enzymes. The project now runs on four ProteinGym enzyme DMS datasets: TEM-1 beta-lactamase, VIM-2 metallo-beta-lactamase, AMIE aliphatic amidase, and beta-glucosidase. It scores single amino-acid variants with ESM-2, compares model scores against experimental fitness, and slices performance by exact catalytic sites, structure-derived mechanism shells, ligand-bound contact groups, active-site neighborhoods, and background residues.

The scientific motivation is simple: a protein language model can look good overall while still failing on the residues that matter most for enzyme engineering. Enzyme function is not only about broad evolutionary conservation or stability. It can depend on active-site chemistry, substrate positioning, cofactors, binding-pocket geometry, and transition-state stabilization. P0 turns that concern into a measurable benchmark.

The project is not just a notebook. It is a small production-style Python repo with a command-line interface, typed data models, mutation parsing, residue annotation, model scoring, statistical metrics, plots, tests, GitHub Actions, and Savio HPC run scripts.

The main scaling result is that ESM-2 clearly improves from 8M to 35M parameters across TEM-1, VIM-2, AMIE, and beta-glucosidase. However, exact catalytic or metal-binding slices remain weaker, noisier, or less interpretable than broader mechanism-adjacent slices. The strongest controlled 35M signal is TEM-1 active-site neighborhood; VIM-2, AMIE, and beta-glucosidase show useful raw mechanism-slice signal, but those slices remain inside matched-position null intervals at 35M.

The short interpretation:

- ESM-2 captures meaningful zero-shot signal on TEM-1 beta-lactamase DMS data.
- Scaling from ESM-2 8M to ESM-2 35M improves performance across most slices.
- UniProt catalytic-site-only performance is positive but lower than the non-active-site background.
- Broader active-site and ligand-contact regions show strong model signal.
- A v2 matched-position null-control upgrade shows that exact active-site-only slices are not unusual relative to same-size random residue-position controls, while the TEM-1 active-site-neighborhood slice is higher than matched null controls for both ESM-2 8M and 35M.
- The project demonstrates how to evaluate not only whether a model works, but where it works.

P0 v1 and v2 are complete as portfolio artifacts. The v3 scaffold is now a real four-enzyme benchmark seed: the enzyme-panel registry exists, validates against ProteinGym metadata, and VIM-2, AMIE, and beta-glucosidase have placeholder, ESM-2 8M, and ESM-2 35M baselines.

## 1.1 v2 Addendum: Matched Residue-Position Null Controls

After the initial report, P0 was upgraded with matched residue-position null controls. This directly addresses a key statistical concern: exact catalytic residues are a very small slice. In TEM-1 beta-lactamase, the UniProt active-site label covers 4 residue positions and 57 variants.

For each mechanism-relevant residue slice, the upgraded analysis samples random residue-position groups of the same size and recomputes Spearman correlation. The observed slice is then compared against that matched null distribution.

The upgraded result is more nuanced:

- Exact UniProt active-site-only slices are not unusually low or high relative to same-size random position controls.
- In TEM-1, active-site-neighborhood slices are higher than matched random position controls for both ESM-2 8M and ESM-2 35M.
- PDB ligand-contact slices trend high, but remain inside the matched null interval in this first TEM-1-only analysis.

This changes the strongest scientific claim from "ESM-2 fails at catalytic residues" to:

> Sequence-only protein language models may capture functional-neighborhood constraints better than exact catalytic chemistry, and residue-zone claims should be tested against matched random position controls.

The full v2 note is in `docs/p0_v2_novelty_upgrade.md`.

## 1.2 v3 Addendum: Enzyme Panel Registry

After the v2 null-control upgrade, P0 was extended from a single-enzyme result into a multi-enzyme benchmark plan. The new registry is:

```text
data/panels/p0_enzyme_panel_candidates.csv
```

It contains 18 enzyme DMS candidates across beta-lactamases, proteases, hydrolases, kinases, oxidoreductases, phosphatases, and other mechanism classes. The point is to test whether the TEM-1 pattern is systematic or just a one-enzyme artifact.

The validator is:

```text
scripts/validate_panel_registry.py
```

It checks each candidate against local ProteinGym metadata, estimates masked-marginal scoring cost, checks whether local DMS/FASTA/annotation files are present, and writes:

```text
results/panel_registry_validation.json
```

Current validation result:

| Check | Result |
| --- | ---: |
| Candidate enzyme datasets | 17 |
| ProteinGym metadata matches | 17 |
| Ready for current P0 pipeline | 4 |
| Need local data and annotations | 13 |

Completed first expansions:

1. `A4GRB6_PSEAI_Chen_2020` - VIM-2 beta-lactamase placeholder, ESM-2 8M, and ESM-2 35M baselines.
2. `AMIE_PSEAE_Wrenbeck_2017` - AMIE aliphatic amidase placeholder, ESM-2 8M, and ESM-2 35M baselines.
3. `Q59976_STRSQ_Romero_2015` - beta-glucosidase placeholder, ESM-2 8M, and ESM-2 35M baselines.

Recommended next expansion:

1. Add conservation-matched and solvent-accessibility-matched controls.
2. Add mutation-count-matched and fitness-variance-matched controls.
3. Upgrade AMIE labels with stronger primary-source or experimental-structure provenance.

This is scientifically important because it turns P0 from "one interesting TEM-1 result" into a controlled plan for asking whether residue-zone behavior generalizes across mechanisms.

## 1.3 v3 Addendum: VIM-2 Second-Enzyme Case

VIM-2 is the first second-enzyme case in P0.

Dataset:

- ProteinGym dataset: `A4GRB6_PSEAI_Chen_2020`
- Protein: VIM-2 metallo-beta-lactamase
- Variants: 5,004 single mutants
- Current runs: placeholder, ESM-2 8M, and ESM-2 35M baselines with bootstrap intervals and matched-position null controls

The exact curated metal-binding/catalytic-site positions are:

```text
[114, 116, 118, 179, 198, 240]
```

These are motif-curated B1 metallo-beta-lactamase positions in the 266-aa ProteinGym target sequence. UniProt accession A4GRB6 is inactive/deleted, so this is intentionally not presented as a UniProt-backed annotation.

ESM-2 35M result:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.5280 | - | 5,004 |
| Curated metal-binding site | 0.3449 | 0.5085 | 113 |
| Active-site neighborhood | 0.6133 | 0.4897 | 448 |
| 5ACX WL3 inhibitor contact, 5 A | 0.6613 | 0.5207 | 247 |
| AF2 structure metal-site shell, 5 A | 0.5846 | 0.4778 | 802 |

The 35M model improves VIM-2 overall performance. The exact curated metal-binding-site slice remains inside the matched-position null. The new 5ACX/WL3 inhibitor-contact group is the strongest raw VIM-2 mechanism slice, but it also remains inside matched-position and conservation-plus-SASA controls. This keeps the VIM-2 story careful: model scale helps globally, but even ligand-bound pocket labels need controls before they become biological claims.

## 1.4 v3 Addendum: AMIE Non-Beta-Lactamase Case

AMIE is the first non-beta-lactamase enzyme case in P0.

Dataset:

- ProteinGym dataset: `AMIE_PSEAE_Wrenbeck_2017`
- Protein: AMIE aliphatic amidase
- Variants: 6,227 single mutants
- Current runs: placeholder, ESM-2 8M, and ESM-2 35M baselines with bootstrap intervals and matched-position null controls

The current conservative catalytic-site labels are:

```text
[59, 134, 166]
```

These are motif and AF2-geometry curated labels, not UniProt-backed AMIE feature annotations. The AF2 structure places Cys166 close to Glu59 and Lys134, supporting a catalytic-geometry slice, but AMIE label provenance should be upgraded later.

ESM-2 35M result:

| Slice | Spearman | Outside Spearman | Variants |
| --- | ---: | ---: | ---: |
| Overall | 0.4082 | - | 6,227 |
| Curated catalytic site | 0.0911 | 0.3991 | 57 |
| AF2 catalytic shell, 5 A | 0.3071 | 0.4069 | 621 |
| Active-site neighborhood | 0.4335 | 0.3902 | 259 |

AMIE is scientifically useful because it does not simply repeat the TEM-1 result. The active-site-neighborhood slice is stronger than its outside background, but remains inside same-size matched-position null controls. The exact catalytic-site slice remains weak at 35M. That makes the panel claim more honest: model scale helps globally, but mechanism-neighborhood signal is enzyme-dependent and must be tested against null controls.

## 1.5 v3 Addendum: Four-Enzyme 35M Scaling

The first four-enzyme 35M panel is now complete.

| Dataset | Enzyme | Overall ESM-2 35M | Exact Site | Background | Best Mechanism Slice |
| --- | --- | ---: | ---: | ---: | --- |
| `BLAT_ECOLX_Firnberg_2014` | TEM-1 beta-lactamase | 0.5548 | 0.4596 | 0.5428 | PDB ligand contact, 0.7127; active-site neighborhood, 0.7027 |
| `A4GRB6_PSEAI_Chen_2020` | VIM-2 metallo-beta-lactamase | 0.5280 | 0.3449 | 0.5085 | WL3 inhibitor contact, 0.6613; active-site neighborhood, 0.6133; metal-site shell, 0.5846 |
| `AMIE_PSEAE_Wrenbeck_2017` | AMIE aliphatic amidase | 0.4082 | 0.0911 | 0.3991 | Active-site neighborhood, 0.4335 |
| `Q59976_STRSQ_Romero_2015` | Beta-glucosidase | 0.4481 | 0.5105 | 0.4434 | Active-site neighborhood, 0.4327; catalytic shell, 0.3808 |

Matched-position null controls at 35M:

| Dataset | Exact Site | Structure Slice | Active-Site Neighborhood |
| --- | --- | --- | --- |
| TEM-1 | Inside null, p = 0.668 | Inside null, p = 0.070 | Higher than null, p = 0.012 |
| VIM-2 | Inside null, p = 0.476 | Inside null, p = 0.084; WL3 inhibitor contact inside null, p = 0.186 | Inside null, p = 0.142 |
| AMIE | Inside null, p = 0.408 | Inside null, p = 0.312 | Inside null, p = 0.778 |
| Beta-glucosidase | Inside null, p = 0.772 | Inside null, p = 0.654 | Inside null, p = 0.984 |

This makes the project more novel and more careful. The result is not a blanket claim that active-site neighborhoods are always special. The result is that model scale improves global zero-shot fitness prediction, while mechanism-specific claims require residue-zone controls. TEM-1 remains the strongest positive functional-neighborhood case. VIM-2, AMIE, and beta-glucosidase show why controls matter.

## 1.6 v4 Addendum: ProteinMPNN Model-Family Comparison

P0 now includes a structure-conditioned ProteinMPNN baseline for the three enzymes whose available structures directly match the ProteinGym DMS target sequence: VIM-2, AMIE, and beta-glucosidase. TEM-1 is intentionally excluded from this first pass because `1M40.pdb` starts at residue 26 and does not directly match the full 286-aa DMS target sequence.

The comparison now separates three model families:

| Model family | Biological signal |
| --- | --- |
| ESM-2 masked marginal | Sequence-context plausibility |
| MSA conservation | Family-level evolutionary constraint |
| ProteinMPNN | Fixed-backbone structure compatibility |

Ready-enzyme result:

| Dataset | ESM-2 35M Overall | MSA Overall | ProteinMPNN Overall | ProteinMPNN Exact Site | ProteinMPNN Background |
| --- | ---: | ---: | ---: | ---: | ---: |
| VIM-2 | 0.5280 | 0.4931 | 0.6259 | 0.2583 | 0.6197 |
| AMIE | 0.4082 | 0.4306 | 0.3457 | 0.2662 | 0.3371 |
| Beta-glucosidase | 0.4481 | 0.5615 | 0.3618 | 0.6364 | 0.3571 |

The most important result is VIM-2. ProteinMPNN is strongest overall, but it is much weaker at curated metal-binding residues than in the non-metal background. That is exactly the kind of model-family disagreement P0 was built to expose.

The final interpretation becomes sharper:

> Global mutation ranking can be improved by different model families, but mechanism-local residues still need separate evaluation. Fixed-backbone compatibility does not fully explain catalytic or metal-site behavior.

## 2. The 30-Second Explanation

P0 asks whether protein language models fail differently near catalytic residues. I started with a public TEM-1 beta-lactamase deep mutational scanning dataset from ProteinGym, scored mutations with ESM-2, and compared model scores to experimental fitness. I then expanded the benchmark to VIM-2 metallo-beta-lactamase, AMIE aliphatic amidase, and beta-glucosidase. Instead of only reporting one overall correlation, I split each assay into biologically meaningful residue groups: exact catalytic or metal-binding sites, structure-derived mechanism shells, active-site neighborhoods, and the rest of the protein.

The result: ESM-2 performs much better than a placeholder baseline, and 35M improves overall performance across TEM-1, VIM-2, AMIE, and beta-glucosidase. TEM-1 active-site-neighborhood regions show unusually strong signal relative to matched-position null controls. VIM-2, AMIE, and beta-glucosidase have useful raw mechanism-slice signal, but their 35M slices remain inside matched random-position controls. That matters because aggregate model performance can hide biologically important failure modes, and matched controls prevent overclaiming small mechanistic slices.

## 3. Why This Project Exists

Protein language models are often evaluated using broad benchmarks: one dataset, one model score, one correlation. That is useful, but it can miss the way biology is structured.

For enzymes, not all residues carry the same meaning:

- Some residues mainly affect folding or stability.
- Some residues affect evolutionary conservation.
- Some residues shape the active-site environment.
- Some residues contact substrate or ligand.
- Some residues directly participate in catalysis.

A model can be good at recognizing broad sequence constraints while still being weaker at residues where chemistry matters most. For protein engineering, this distinction is not academic. If a model fails near catalytic chemistry, then a scientist needs to know that before trusting the model to prioritize variants.

P0 was built to make that failure mode measurable.

The guiding hypothesis was:

> Sequence-only protein language models should capture broad evolutionary and stability constraints, but may struggle when experimental fitness depends on active-site chemistry, substrate binding, or catalytic mechanism.

## 4. Scientific Question

The elegant question:

> Do protein language models fail differently on catalytic residues than on the rest of the protein?

This question is useful because it is narrow enough to test, but broad enough to matter. It connects:

- protein language models,
- zero-shot variant-effect prediction,
- deep mutational scanning,
- enzyme mechanism,
- residue annotation,
- statistical evaluation,
- and model failure analysis.

The project is therefore not merely "run ESM on a dataset." It is a model behavior audit framed around biological mechanism.

## 5. Biological System

The first real benchmark uses TEM-1 beta-lactamase.

Dataset:

- ProteinGym dataset: `BLAT_ECOLX_Firnberg_2014`
- Protein: TEM-1 beta-lactamase
- Source organism annotation: `BLAT_ECOLX`
- DMS assay context: growth under ampicillin selection
- Fitness target: ProteinGym `DMS_score`
- Variants analyzed: 4,783 single amino-acid substitutions

TEM-1 beta-lactamase is useful for this project because it is an enzyme with known active-site biology and a public deep mutational scanning assay. That lets the benchmark compare model predictions against experimental effects, while also asking whether model behavior differs across catalytic and non-catalytic regions.

## 6. Residue Annotation Strategy

The project does not rely only on raw sequence positions. It annotates variants by biologically meaningful residue groups.

### 6.1 UniProt Active-Site Residues

The catalytic labels were validated against UniProt P62593 for `BLAT_ECOLX`.

The active-site residues used in this benchmark are:

```text
68, 71, 128, 164
```

These correspond to commonly discussed class-A beta-lactamase catalytic positions:

| ProteinGym/UniProt numbering | Common Ambler numbering |
| ---: | --- |
| 68 | Ser70 |
| 71 | Lys73 |
| 128 | Ser130 |
| 164 | Glu166 |

The UniProt active-site group contains 57 variants in the DMS dataset.

### 6.2 UniProt Substrate-Binding Residues

The substrate-binding group uses UniProt positions:

```text
232-234
```

This group contains 55 variants in the DMS dataset.

### 6.3 PDB 1M40 Ligand-Contact Residues

The project also adds a structure-derived group from PDB 1M40. It identifies residues in chain A with any heavy atom within 5.0 Angstrom of the `CB4` inhibitor.

This creates the group:

```text
structure_ligand_contact_5a
```

This group contains 277 variants.

The purpose of this group is to move beyond a tiny active-site-only label and ask whether ESM-2 behaves differently around a broader binding or ligand-contact environment.

### 6.4 Active-Site Neighborhood

The project also defines:

```text
active_site_neighborhood
```

This is a broader mechanism-adjacent group around validated active-site and substrate-binding positions. It contains 461 variants.

This group is useful because the exact active-site residues are too few to support a confident general conclusion by themselves. A neighborhood group gives a larger chemistry-adjacent slice while staying biologically interpretable.

## 7. Model and Scoring Method

The project compares three scorers:

| Scorer | Purpose |
| --- | --- |
| Placeholder conservation scorer | Deterministic sanity check for the pipeline |
| ESM-2 8M | First local protein language model baseline |
| ESM-2 35M | First larger-model Savio HPC scaling run |

### 7.1 Placeholder Scorer

The placeholder scorer is intentionally simple. It is not intended to be biologically competitive. It exists so the full analysis pipeline can be tested before running real ESM models.

This is important engineering practice. Before spending compute, the repo proves that it can:

- load data,
- parse mutations,
- label residues,
- score variants,
- compute metrics,
- write output files,
- and generate plots.

### 7.2 ESM-2 Masked-Marginal Scoring

The real model scorer is `ESM2MaskedMarginalScorer`.

For each mutation, the scorer:

1. Takes the wild-type sequence.
2. Masks the mutated position.
3. Uses ESM-2 to estimate log probabilities for amino acids at that position.
4. Computes a log-likelihood ratio:

```text
score = log P(mutant amino acid | masked wild-type context)
        - log P(wild-type amino acid | masked wild-type context)
```

Higher scores should indicate variants that ESM-2 finds more plausible relative to the wild type.

This is a zero-shot method. The model is not trained on this DMS assay. It uses pretrained sequence knowledge to rank mutations.

## 8. Evaluation Metrics

The project reports several metrics.

### 8.1 Spearman Correlation

Spearman correlation measures whether model-ranked variants agree with experimentally ranked variants. It is rank-based, so it does not require the model score to be calibrated in the same units as experimental fitness.

The project reports:

- overall Spearman,
- UniProt active-site Spearman,
- non-active-site Spearman,
- substrate-binding Spearman,
- ligand-contact Spearman,
- active-site-neighborhood Spearman,
- and outside-group Spearman for comparison.

### 8.2 Top-k Enrichment

Top-k enrichment asks whether the highest-scoring model variants are enriched for experimentally high-fitness variants.

The current metric is:

```text
top_5_enrichment_fitness_ge_0_7
```

This asks whether the top 5 model-ranked variants are enriched for variants with fitness at least 0.7 relative to the background rate.

### 8.3 Mutation-Class Breakdown

The project also groups mutations by broad amino-acid class changes:

- charge_preserving,
- class_changing,
- hydrophobic_or_special_preserving,
- polar_preserving.

This helps test whether model performance differs by mutation type, not only by residue location.

### 8.4 Bootstrap Confidence Intervals

The project computes bootstrap confidence intervals for Spearman metrics. This matters because some residue slices are small. The active-site group, for example, contains only 57 variants.

The bootstrap intervals are not decorative. They tell the reader how uncertain the subgroup estimates are.

## 9. Main Results

### 9.1 Overall Model Comparison

| Scorer | Overall Spearman | UniProt active-site Spearman | Non-active-site Spearman | Top-5 Enrichment |
| --- | ---: | ---: | ---: | ---: |
| Placeholder | 0.0430 | 0.1231 | 0.0342 | 0.5247 |
| ESM-2 8M | 0.4113 | 0.3023 | 0.4042 | 2.6237 |
| ESM-2 35M | 0.5548 | 0.4596 | 0.5428 | 2.0990 |

Interpretation:

- The placeholder scorer is close to uninformative overall.
- ESM-2 8M shows meaningful zero-shot signal.
- ESM-2 35M improves over ESM-2 8M overall.
- Active-site-only performance improves with model size but remains below non-active-site performance.

### 9.2 Mechanism-Relevant Slices

| Scorer | Group | Spearman | Outside-group Spearman | Variants |
| --- | --- | ---: | ---: | ---: |
| Placeholder | UniProt active site | 0.1231 | 0.0342 | 57 |
| Placeholder | UniProt substrate-binding site | -0.0350 | 0.0368 | 55 |
| Placeholder | PDB 1M40 ligand contact, 5 A | 0.1777 | 0.0361 | 277 |
| Placeholder | Active-site neighborhood | 0.2916 | 0.0278 | 461 |
| ESM-2 8M | UniProt active site | 0.3023 | 0.4042 | 57 |
| ESM-2 8M | UniProt substrate-binding site | 0.4383 | 0.3992 | 55 |
| ESM-2 8M | PDB 1M40 ligand contact, 5 A | 0.6076 | 0.3997 | 277 |
| ESM-2 8M | Active-site neighborhood | 0.6453 | 0.3752 | 461 |
| ESM-2 35M | UniProt active site | 0.4596 | 0.5428 | 57 |
| ESM-2 35M | UniProt substrate-binding site | 0.4965 | 0.5453 | 55 |
| ESM-2 35M | PDB 1M40 ligand contact, 5 A | 0.7127 | 0.5344 | 277 |
| ESM-2 35M | Active-site neighborhood | 0.7027 | 0.5188 | 461 |

Interpretation:

- Ligand-contact and active-site-neighborhood groups show strong ESM-2 signal.
- The UniProt active-site-only group is small and uncertain.
- ESM-2 appears stronger around broader active-site environments than on the exact catalytic positions alone.
- This supports a nuanced claim: ESM-2 captures constraints near functional regions, but catalytic residues themselves remain a difficult and noisy slice.

### 9.3 Bootstrap Intervals for ESM-2 35M

| Group | Spearman | 95% Bootstrap CI | n |
| --- | ---: | ---: | ---: |
| Overall | 0.5548 | 0.5340 to 0.5757 | 4,783 |
| UniProt active site | 0.4596 | 0.2268 to 0.6418 | 57 |
| Non-active-site | 0.5428 | 0.5195 to 0.5641 | 4,726 |
| UniProt substrate-binding site | 0.4965 | 0.2318 to 0.7061 | 55 |
| Outside substrate-binding site | 0.5453 | 0.5226 to 0.5654 | 4,728 |
| PDB 1M40 ligand contact, 5 A | 0.7127 | 0.6464 to 0.7695 | 277 |
| Outside ligand-contact group | 0.5344 | 0.5125 to 0.5558 | 4,506 |
| Active-site neighborhood | 0.7027 | 0.6508 to 0.7503 | 461 |
| Outside active-site neighborhood | 0.5188 | 0.4944 to 0.5424 | 4,322 |

The confidence intervals show why the active-site-only result should be interpreted carefully. The interval is wide because the group is small. By contrast, the ligand-contact and active-site-neighborhood groups have more variants and narrower intervals.

### 9.4 Mutation-Class Breakdown for ESM-2 35M

| Mutation class | n | Mean fitness | Mean model score | Spearman |
| --- | ---: | ---: | ---: | ---: |
| charge_preserving | 277 | 0.6771 | -1.7223 | 0.5343 |
| class_changing | 3,050 | 0.5065 | -3.0481 | 0.5730 |
| hydrophobic_or_special_preserving | 1,179 | 0.4541 | -2.7983 | 0.4702 |
| polar_preserving | 277 | 0.6127 | -2.8855 | 0.6319 |

This tells a second story beyond residue location. Model agreement with experimental fitness also varies by mutation class.

## 10. Scientific Interpretation

The key scientific interpretation is not "ESM-2 fails at catalytic residues." That would be too strong.

A better interpretation is:

> ESM-2 captures meaningful zero-shot signal in TEM-1 beta-lactamase. Scaling from 8M to 35M improves performance. However, the exact UniProt active-site-only subset remains small, uncertain, and lower than the non-active-site background. Broader mechanism-adjacent groups, especially ligand-contact and active-site-neighborhood residues, show strong signal.

This matters because it shows the value of residue-slice evaluation. If we only reported the overall Spearman correlation, we would miss the biological structure of the model's behavior.

The broader lesson:

> A model's average performance is not enough. For scientific AI, we need to ask where the model is reliable, where it is uncertain, and where biology makes the task qualitatively different.

## 11. What P0 Proves

P0 proves that I can:

- frame a biologically meaningful model-evaluation question,
- turn that question into a reproducible benchmark,
- use public DMS data responsibly,
- validate residue labels against external biological annotation,
- derive a structure-informed residue group from PDB data,
- run zero-shot ESM-2 scoring,
- compare local and HPC model runs,
- compute subgroup statistics and confidence intervals,
- write production-style Python around scientific analysis,
- and communicate the result as a scientific argument.

P0 does not prove:

- that ESM-2 generally fails at all catalytic residues,
- that TEM-1 represents all enzymes,
- that ligand-contact performance generalizes across all structures,
- that the benchmark is a full enzyme-design platform,
- or that zero-shot scoring replaces experimental validation.

This distinction is important. Good scientific communication includes what the project does not claim.

## 12. Code Architecture

The repo is organized as a small Python package rather than a loose notebook.

Main package:

```text
src/p0_zero_shot_fitness/
```

Important modules:

| File | Role |
| --- | --- |
| `cli.py` | Command-line entry point. Parses user options and dispatches to the correct benchmark pipeline. |
| `pipeline.py` | Main analysis flow. Loads data, builds variant records, scores variants, computes metrics, and writes outputs. |
| `io.py` | Data loading and output writing helpers. |
| `mutations.py` | Mutation string parsing and validation against the wild-type sequence. |
| `labeling.py` | Catalytic and residue-group labeling. |
| `scorers.py` | Swappable scoring interface, placeholder scorer, and ESM-2 scorer. |
| `metrics.py` | Spearman correlation, enrichment, subgroup breakdowns, and bootstrap intervals. |
| `panel.py` | Enzyme-panel registry loading, ProteinGym metadata validation, cost estimation, and first-panel recommendation. |
| `models.py` | Typed dataclasses for mutations and scored variant records. |
| `plotting/svg.py` | Lightweight SVG scatter plot generation. |

Supporting folders:

| Folder | Role |
| --- | --- |
| `data/proteingym/` | TEM-1 DMS data, FASTA, residue annotations, source records, and structure-derived labels. |
| `data/panels/` | Candidate enzyme-panel registry for P0 v3 expansion. |
| `results/` | Metrics, scored variants, comparison JSON, and plots. |
| `scripts/` | Utility scripts for comparing metrics and deriving structure contacts. |
| `hpc/` | SLURM scripts and Savio runbook. |
| `tests/` | Pytest suite for mutation parsing, metrics, CLI, and pipeline behavior. |
| `docs/` | Public writeups, data documentation, code walkthroughs, and portfolio artifacts. |

## 13. Pipeline Flow

Conceptual flow:

```text
User command
  -> cli.py parses arguments
  -> build_scorer selects placeholder or ESM-2
  -> pipeline loads DMS data, FASTA, catalytic labels, and residue groups
  -> mutations.py validates each mutation against the wild-type sequence
  -> labeling.py assigns catalytic and mechanism-relevant residue labels
  -> scorer assigns a model score to each mutation
  -> metrics.py compares model scores to experimental fitness
  -> outputs are written as JSON, CSV, and SVG
```

Beginner analogy:

- `cli.py` is the front desk. It receives the user's command and fills out the intake form.
- `build_parser()` designs the intake form.
- `parse_args()` fills the form with the user's choices.
- `build_scorer()` checks out the scoring machine.
- The placeholder scorer is a practice machine.
- The ESM-2 scorer is the real microscope.
- `pipeline.py` is the lab assembly line.
- `metrics.py` is the data analysis bench.
- `results/` is the lab notebook drawer.

This structure matters because each part has a clear job. That is what makes the project explainable, testable, and extensible.

## 14. Command-Line Interface

The CLI supports three presets:

```text
fixture
proteingym-blat
external
```

The most important run commands are:

Placeholder baseline:

```bash
p0-fitness \
  --preset proteingym-blat \
  --output-dir results/proteingym_blat_placeholder
```

ESM-2 8M local run:

```bash
p0-fitness \
  --preset proteingym-blat \
  --scorer esm2 \
  --esm-model esm2_t6_8M_UR50D \
  --output-dir results/proteingym_blat_esm2_t6_8M
```

ESM-2 35M Savio run:

```bash
p0-fitness \
  --preset proteingym-blat \
  --scorer esm2 \
  --esm-model esm2_t12_35M_UR50D \
  --bootstrap-iterations 1000 \
  --output-dir results/proteingym_blat_esm2_t12_35M
```

The external preset is important because it means the pipeline is not hard-coded only to TEM-1. It can be reused with another DMS CSV, FASTA file, catalytic-residue JSON, and optional residue-group JSON.

## 15. HPC and Savio Work

The project includes a concrete Savio runbook and SLURM scripts.

Successful larger-model runs:

| Dataset | Platform | Job ID | Model | Output Folder | Status |
| --- | --- | --- | --- | --- | --- |
| TEM-1 | Savio | `35588401` | `esm2_t12_35M_UR50D` | `results/proteingym_blat_esm2_t12_35M` | completed |
| VIM-2 | Savio | `35616346` | `esm2_t12_35M_UR50D` | `results/proteingym_vim2_esm2_t12_35M` | completed |
| AMIE | Savio | `35616308` | `esm2_t12_35M_UR50D` | `results/proteingym_amie_esm2_t12_35M` | completed |
| Beta-glucosidase | Savio | `35618003` | `esm2_t12_35M_UR50D` | `results/proteingym_bgly_esm2_t12_35M` | completed |

This is useful portfolio evidence because it shows more than local scripting. It shows the ability to:

- clone the repo on HPC,
- create an environment,
- install the package,
- submit a GPU job,
- retrieve outputs,
- compare metrics,
- and fold the results back into the local repo and public writeup.

## 16. Outputs and Artifacts

Important result artifacts:

| Artifact | Meaning |
| --- | --- |
| `results/proteingym_blat_placeholder/metrics.json` | Placeholder baseline metrics |
| `results/proteingym_blat_esm2_t6_8M/metrics.json` | Local ESM-2 8M metrics |
| `results/proteingym_blat_esm2_t12_35M/metrics.json` | Savio ESM-2 35M metrics |
| `results/proteingym_blat_esm2_t12_35M/scored_variants.csv` | Per-variant model scores and labels |
| `results/proteingym_blat_esm2_t12_35M/fitness_scatter.svg` | Scatter plot of model score vs experimental fitness |
| `results/proteingym_blat_esm2_8m_vs_35m.json` | Comparison artifact for ESM-2 scaling |
| `results/proteingym_vim2_placeholder/metrics.json` | VIM-2 placeholder baseline with bootstrap and matched-position null controls |
| `results/proteingym_vim2_esm2_t6_8M/metrics.json` | VIM-2 ESM-2 8M baseline with bootstrap and matched-position null controls |
| `results/proteingym_vim2_esm2_t12_35M/metrics.json` | VIM-2 ESM-2 35M baseline with bootstrap and matched-position null controls |
| `results/proteingym_vim2_placeholder_vs_esm2_t6_8M.json` | VIM-2 placeholder-vs-ESM-2 comparison artifact |
| `results/proteingym_amie_esm2_t6_8M/metrics.json` | AMIE ESM-2 8M baseline with bootstrap and matched-position null controls |
| `results/proteingym_amie_esm2_t12_35M/metrics.json` | AMIE ESM-2 35M baseline with bootstrap and matched-position null controls |
| `results/proteingym_bgly_esm2_t6_8M/metrics.json` | Beta-glucosidase ESM-2 8M baseline with bootstrap and matched-position null controls |
| `results/proteingym_bgly_esm2_t12_35M/metrics.json` | Beta-glucosidase ESM-2 35M baseline with bootstrap and matched-position null controls |
| `results/proteingym_three_enzyme_esm2_t12_35M_comparison.json` | Three-enzyme ESM-2 35M comparison artifact |
| `results/proteingym_four_enzyme_esm2_t12_35M_comparison.json` | Four-enzyme ESM-2 35M comparison artifact |
| `results/panel_registry_validation.json` | Validated enzyme-panel status and recommended first expansion |
| `docs/public_writeup.md` | Public-facing result explanation |
| `docs/code_walkthrough_for_beginners.md` | Beginner-oriented code walkthrough |
| `docs/enzyme_panel_plan.md` | P0 v3 scientific expansion plan |
| `docs/protein_gym_vim2_result.md` | First second-enzyme result note |
| `hpc/SAVIO.md` | Savio runbook |

## 17. Testing and Engineering Quality

The repo uses pytest and includes tests for:

- mutation parsing,
- metrics,
- pipeline behavior,
- CLI behavior,
- ProteinGym dataset materialization,
- and enzyme-panel registry validation.

The project also includes GitHub Actions CI.

This matters because a scientific benchmark is only useful if the reader can trust that the basic machinery works. In this project, tests protect the parts most likely to silently break:

- parsing mutation strings,
- validating mutations against wild-type sequence,
- calculating Spearman correlations,
- filtering records,
- and running the CLI.

The most recent verification state after the beta-glucosidase 35M update was:

```text
20 tests passed
```

## 18. Interview Explanation

### 18.1 Two-Minute Version

I built P0 to test whether protein language models fail differently near catalytic residues. The motivation is that a model can rank mutations well overall but still be weaker around enzyme chemistry, which is exactly where a protein engineer might care most.

I used the ProteinGym TEM-1 beta-lactamase DMS dataset with 4,783 single mutants. I validated catalytic residues against UniProt, added substrate-binding labels, and derived a PDB ligand-contact group from the 1M40 inhibitor-bound structure. Then I scored all single mutants with ESM-2 using masked-marginal log-likelihood ratios.

I compared model scores to experimental fitness using Spearman correlation overall and within biologically meaningful residue groups. ESM-2 8M had an overall Spearman around 0.41, and ESM-2 35M improved to about 0.55. The active-site-only group improved with scale but remained lower than the non-active-site background. Broader ligand-contact and active-site-neighborhood groups had stronger correlations, around 0.71 and 0.70 for the 35M model.

The conclusion is not that ESM fails at catalytic residues generally. The more careful conclusion is that aggregate performance hides important residue-slice behavior. ESM-2 captures strong constraints around active-site environments, but exact catalytic residues are a small and uncertain slice. The project demonstrates a way to evaluate model behavior in terms a biologist would care about.

### 18.2 What To Emphasize For A Life-Science AI Role

Emphasize:

- you framed a biologically meaningful evaluation question,
- you did not just run a model,
- you validated annotations,
- you separated model performance by mechanism-relevant slices,
- you ran a larger model on HPC,
- you reported uncertainty,
- and you built the benchmark as a reusable Python package.

### 18.3 What To Emphasize For A Protein Engineering Role

Emphasize:

- active-site chemistry matters,
- DMS fitness is assay-context dependent,
- catalytic residues, binding pockets, and ligand contacts are different biological objects,
- model rankings need to be interpreted through mechanism,
- and computational ranking should guide experiments, not replace them.

### 18.4 What To Emphasize For A Software or Eval Role

Emphasize:

- modular CLI,
- swappable scorer interface,
- typed data records,
- tests,
- reproducible outputs,
- JSON/CSV/SVG artifacts,
- benchmark extensibility,
- and clear separation between data loading, scoring, labeling, and metrics.

## 19. Likely Interview Questions and Strong Answers

### Question: Why did you use Spearman correlation?

Because the model score and experimental fitness are not in the same units. Spearman asks whether the model ranks variants in a similar order to the experiment. For zero-shot variant-effect prediction, ranking is often more meaningful than absolute score calibration.

### Question: Why is the active-site result uncertain?

Because the active-site-only group contains only 57 variants across four positions. That makes the estimate noisy. That is why I added bootstrap confidence intervals and broader mechanism-relevant groups like ligand contacts and active-site neighborhoods.

### Question: Why did ligand-contact residues perform better than exact catalytic residues?

One explanation is sample size: the ligand-contact group has 277 variants, which gives a more stable estimate. Another is biology: ESM-2 may capture structural and evolutionary constraints around the active-site environment better than the exact chemistry of catalytic residues. The result suggests ESM-2 has useful signal near functional regions, but it does not prove the model understands catalytic mechanism.

### Question: What does masked-marginal scoring mean?

For each mutation, I mask the wild-type position and ask ESM-2 how likely the mutant amino acid is compared with the wild-type amino acid in that sequence context. The score is the mutant log probability minus the wild-type log probability.

### Question: Why include a placeholder scorer?

The placeholder scorer is an engineering sanity check. It lets me prove the pipeline works before depending on PyTorch, ESM, model downloads, or GPU compute. It is like testing the plumbing before turning on the expensive instrument.

### Question: What would you do next?

I added a ProteinMPNN structure-conditioned baseline after the MSA conservation and conservation-plus-SASA controls. The clean next move is a single ESM-2-vs-MSA-vs-ProteinMPNN figure and a target-aligned TEM-1 ProteinMPNN run if a defensible full-length structure or remap is staged.

## 20. Limitations

The project has clear limitations:

1. The active-site-only groups are small, especially beta-glucosidase with only 12 exact catalytic-site variants.
2. The ligand-contact groups come from one inhibitor-bound TEM-1 structure and one inhibitor-bound VIM-2 structure.
3. DMS fitness reflects an assay context, not pure catalytic chemistry.
4. ESM-2 is sequence-only and does not explicitly model ligand chemistry or transition states.
5. The first ProteinMPNN pass excludes TEM-1 because the available structure is not target-aligned to the full DMS sequence.
6. The project is retrospective, not a prospective design campaign.

These limitations do not weaken the project. They make the claims precise.

## 21. Next Scientific Steps

High-priority next steps:

1. Add an explicit ESM-2-vs-MSA-vs-ProteinMPNN interpretation figure.
2. Add TEM-1 ProteinMPNN only after staging a target-aligned BLAT_ECOLX structure or defensible profile remap.
3. Compare against MSA Transformer only if ProteinMPNN leaves a specific MSA-aware model ambiguity.
4. Add more ligand-bound or cofactor-aware labels where clean experimental structures exist.
5. Upgrade AMIE substrate-pocket labels with stronger provenance.
6. Add prospective validation on a new enzyme-design target.
7. Turn the four-enzyme result into a clean methods card.

## 22. Portfolio Value

P0 is strong portfolio evidence because it demonstrates five things at once.

### Biology Depth

The project uses enzyme DMS data, catalytic residues, substrate-binding residues, PDB/mmCIF ligand contacts, metal-site labels, and active-site-neighborhood annotations.

### ML and Evaluation Depth

The project uses zero-shot ESM-2 scoring, rank correlation, subgroup evaluation, bootstrap confidence intervals, and model-size comparison.

### Production Python

The repo has a package structure, CLI, typed records, modular boundaries, tests, scripts, data documentation, and CI.

### HPC and Compute Readiness

The project includes Savio setup, SLURM scripts, GPU execution, and artifact transfer.

### Scientific Communication

The project includes a public writeup, social post draft, beginner code walkthrough, portfolio case study, and now this extensive report.

## 23. Current Status

P0 v1 and v2 are complete. P0 v3 has its first infrastructure step complete, its first four-enzyme ESM-2 35M panel complete, its MSA conservation baseline complete, and its first ProteinMPNN model-family comparison complete for the three target-aligned ready enzymes.

Complete means:

- real dataset selected,
- ESM-2 8M run locally,
- ESM-2 35M run on Savio for TEM-1, VIM-2, AMIE, and beta-glucosidase,
- ESM-2 8M run locally for beta-glucosidase,
- MSA conservation baseline completed across the four-enzyme panel,
- ProteinMPNN baseline completed for VIM-2, AMIE, and beta-glucosidase,
- outputs copied back,
- metrics compared,
- enzyme-panel registry validated,
- VIM-2 data, placeholder baseline, ESM-2 8M baseline, and ESM-2 35M baseline added,
- AMIE data, placeholder baseline, ESM-2 8M baseline, and ESM-2 35M baseline added,
- beta-glucosidase data, placeholder baseline, ESM-2 8M baseline, and ESM-2 35M baseline added,
- GitHub updated,
- Obsidian updated,
- tests passing,
- and the result has a coherent scientific interpretation.

It does not mean the research direction is exhausted. It means the first credible project artifact is finished.

## 24. Final Takeaway

P0 is a benchmark for asking whether protein language model performance changes near catalytic and mechanism-relevant regions of an enzyme.

The most important lesson is:

> Overall model performance is not enough. In AI biology, the interesting question is where the model works, where it fails, and whether those failure modes line up with the biology a scientist actually cares about.

This project turns that lesson into code, metrics, plots, and a reproducible public artifact.
