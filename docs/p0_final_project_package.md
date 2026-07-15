# P0 Final Project Package

Project: `p0-zero-shot-fitness`

Status: completed portfolio artifact, with clear next research extensions

Core question:

> Do protein language models fail differently on catalytic residues than on the rest of the protein?

## 1. What This Package Is

This is the complete, interview-ready package for P0. It is meant to answer four questions without making the reader hunt through the repo:

1. What scientific question did P0 ask?
2. What exactly was built?
3. What did the results show?
4. Why is this evidence of biology depth, ML/eval depth, production Python, HPC execution, and scientific communication?

The shortest version:

> P0 is a mechanism-sliced zero-shot protein fitness benchmark. It evaluates ESM-2, MSA conservation, and ProteinMPNN on enzyme DMS datasets, then asks whether model performance changes near catalytic, metal-binding, ligand-contact, and active-site-neighborhood residues.

## 2. Final Artifact Map

Open these in order.

| Artifact | Path | Purpose |
| --- | --- | --- |
| Final project package | `docs/p0_final_project_package.md` | The canonical complete explanation |
| Final report | `docs/p0_final_report.md` | Scientific report with methods and results |
| ProteinMPNN comparison | `docs/protein_mpnn_model_family_comparison.md` | Model-family comparison result |
| Public writeup | `docs/public_writeup.md` | Blog-style explanation |
| Portfolio card | `docs/p0_portfolio_card.md` | Short portfolio-facing summary |
| ESM-2 35M figure | `docs/assets/p0_four_enzyme_35m_portfolio_figure.svg` | Four-enzyme ESM-2 result visual |
| Model-family figure | `docs/assets/p0_model_family_comparison.svg` | ESM-2 vs MSA vs ProteinMPNN visual |
| Main model-family JSON | `results/proteingym_ready_enzyme_model_family_comparison.json` | Machine-readable final comparison |

## 3. One-Sentence Claim

P0 shows that global zero-shot fitness ranking and mechanism-local residue behavior can diverge, so enzyme model evaluation needs residue-sliced metrics and matched controls rather than only whole-protein correlation.

## 4. What Makes This More Than "Run ESM On ProteinGym"

The project is not just a model call. It adds a mechanism-aware evaluation layer:

- It uses real enzyme DMS datasets.
- It scores mutations with multiple model families.
- It labels catalytic, metal, ligand-contact, active-site-neighborhood, and background residues.
- It compares global model performance against mechanism-local performance.
- It adds matched null controls so small residue slices are not overclaimed.
- It separates sequence-context signal, family-conservation signal, and fixed-backbone structure signal.
- It packages the work as a reproducible Python repo with tests, CLI, scripts, docs, figures, and HPC runbooks.

## 5. Dataset Panel

P0 currently covers four ProteinGym enzyme DMS datasets.

| Dataset | Enzyme | Mechanism class | Single mutants | Main biological labels |
| --- | --- | --- | ---: | --- |
| `BLAT_ECOLX_Firnberg_2014` | TEM-1 beta-lactamase | Serine beta-lactam hydrolysis | 4,783 | UniProt catalytic site, substrate-binding site, PDB ligand contact, active-site neighborhood |
| `A4GRB6_PSEAI_Chen_2020` | VIM-2 metallo-beta-lactamase | Zinc-dependent beta-lactam hydrolysis | 5,004 | Curated metal-binding site, 5ACX/WL3 inhibitor contact, metal-site shell, active-site neighborhood |
| `AMIE_PSEAE_Wrenbeck_2017` | AMIE aliphatic amidase | Amidase/nitrilase-like hydrolysis | 6,227 | UniProt catalytic triad, catalytic shell, active-site neighborhood |
| `Q59976_STRSQ_Romero_2015` | Beta-glucosidase | Glycoside hydrolysis | 2,999 | Curated catalytic site, catalytic shell, active-site neighborhood |

Total evaluated single mutants: 19,013.

## 6. Model Families

P0 compares three biological signals.

| Model family | Concrete scorer | What it tests |
| --- | --- | --- |
| Sequence language model | ESM-2 masked marginal | Sequence-context plausibility learned from protein sequences |
| Evolutionary conservation | MSA log-odds conservation baseline | Family-level amino-acid conservation |
| Structure-conditioned inverse folding | ProteinMPNN profile scorer | Fixed-backbone amino-acid compatibility |

## 7. Scoring Definitions

### 7.1 ESM-2

For each single mutation:

```text
ESM-2 score = log P(mutant amino acid at masked position) - log P(wild-type amino acid at masked position)
```

Meaning:

- High score: ESM-2 thinks the mutant residue is plausible in the sequence context.
- Low score: ESM-2 thinks the mutant residue is unlikely in the sequence context.

### 7.2 MSA Conservation

For each single mutation:

```text
MSA score = log frequency(mutant amino acid at aligned position) - log frequency(wild-type amino acid at aligned position)
```

Meaning:

- High score: the mutant is tolerated or common in the protein family.
- Low score: the mutant is rare or disfavored in the protein family.

### 7.3 ProteinMPNN

For each single mutation:

```text
ProteinMPNN score = log P(mutant amino acid | backbone) - log P(wild-type amino acid | backbone)
```

Meaning:

- High score: ProteinMPNN thinks the mutant residue fits the fixed backbone.
- Low score: ProteinMPNN thinks the mutant residue is structurally implausible for that backbone.

Important caveat:

> ProteinMPNN is not an enzyme activity model. It does not know the ligand, transition state, assay, or catalytic chemistry. It is a structure-conditioned baseline.

## 8. Evaluation Metrics

Primary metric:

```text
Spearman correlation(model score, experimental DMS fitness)
```

Why Spearman:

- It measures rank correlation.
- Protein engineering often cares about prioritization.
- It does not require the model score and DMS fitness to be on the same numeric scale.

P0 computes:

- overall Spearman across all single mutants,
- catalytic or metal-site Spearman,
- non-catalytic or background Spearman,
- active-site-neighborhood Spearman,
- ligand-contact or catalytic-shell Spearman,
- top-k enrichment,
- mutation-class breakdown,
- bootstrap intervals,
- matched null controls.

## 9. Controls

P0 includes controls because mechanism slices can be small.

### 9.1 Position-Matched Null

Question:

> Is this catalytic or active-site slice unusual compared with random residue groups of the same size?

Procedure:

1. Count how many residue positions are in the biological slice.
2. Randomly sample residue groups of the same size.
3. Recompute Spearman for each random group.
4. Compare the observed mechanism slice to the null distribution.

Why it matters:

- Exact catalytic residues can be tiny.
- A high or low Spearman can happen by chance when there are few positions.

### 9.2 Covariate-Matched Null

Question:

> Is this mechanism slice still unusual after matching on obvious confounders?

Controls include:

- mutation count per residue,
- local DMS fitness variance,
- local DMS fitness distribution,
- model-score sensitivity,
- relative sequence position,
- structure contact density,
- approximate solvent accessibility,
- conservation plus solvent accessibility.

Why it matters:

> A pocket residue can look special because it is buried, conserved, mutation-rich, or experimentally variable. The control asks whether the biology label adds information beyond those confounders.

## 10. Key Result 1 - ESM-2 35M Across Four Enzymes

| Dataset | Overall Spearman | Exact catalytic or metal site | Background |
| --- | ---: | ---: | ---: |
| TEM-1 | 0.5548 | 0.4596 | 0.5428 |
| VIM-2 | 0.5280 | 0.3449 | 0.5085 |
| AMIE | 0.4082 | 0.0911 | 0.3991 |
| Beta-glucosidase | 0.4481 | 0.5105 | 0.4434 |

Interpretation:

- ESM-2 35M gives useful global signal on all four enzymes.
- Exact catalytic or metal-site behavior is not uniformly strong.
- AMIE is the clearest warning case: exact catalytic-site Spearman is only `0.0911`.

## 11. Key Result 2 - Mechanism Neighborhoods Are More Informative Than Exact Sites Alone

| Dataset | Best ESM-2 35M mechanism slice | Spearman | Read |
| --- | --- | ---: | --- |
| TEM-1 | PDB ligand contact | 0.7127 | Strong raw ligand-neighborhood signal |
| TEM-1 | Active-site neighborhood | 0.7027 | Strongest matched-null active-neighborhood case |
| VIM-2 | 5ACX/WL3 inhibitor contact | 0.6613 | Strong raw pocket signal, but inside strict controls |
| VIM-2 | Active-site neighborhood | 0.6133 | Strong raw mechanism-adjacent signal |
| AMIE | Active-site neighborhood | 0.4335 | Slightly above background, not strongly controlled |
| Beta-glucosidase | Active-site neighborhood | 0.4327 | Similar to background |

Interpretation:

> Exact catalytic residues are often too small and chemically specific. Broader mechanism neighborhoods give more stable readouts, but still need matched controls.

## 12. Key Result 3 - MSA Conservation Changes The Story

| Dataset | ESM-2 35M Overall | MSA Overall | Winner |
| --- | ---: | ---: | --- |
| TEM-1 | 0.5548 | 0.4247 | ESM-2 |
| VIM-2 | 0.5280 | 0.4931 | ESM-2, slightly |
| AMIE | 0.4082 | 0.4306 | MSA |
| Beta-glucosidase | 0.4481 | 0.5615 | MSA |

Interpretation:

> ESM-2 is not automatically better than a classical family-conservation signal. On AMIE and beta-glucosidase, the MSA baseline wins globally.

This makes P0 stronger because it avoids a shallow "foundation model beats everything" story.

## 13. Key Result 4 - ProteinMPNN Adds A Structure-Conditioned Test

ProteinMPNN was run on the three target-aligned ready structures:

- VIM-2
- AMIE
- beta-glucosidase

TEM-1 was excluded from this pass because `1M40.pdb` is not target-aligned to the full 286-aa ProteinGym DMS sequence.

| Dataset | ESM-2 35M Overall | MSA Overall | ProteinMPNN Overall | ProteinMPNN mechanism read |
| --- | ---: | ---: | ---: | --- |
| VIM-2 | 0.5280 | 0.4931 | 0.6259 | Best overall, weak at curated metal site |
| AMIE | 0.4082 | 0.4306 | 0.3457 | Weakest overall |
| Beta-glucosidase | 0.4481 | 0.5615 | 0.3618 | High exact catalytic-site result, but tiny slice |

## 14. Most Important Final Result

VIM-2 ProteinMPNN:

| Metric | Spearman |
| --- | ---: |
| Overall | 0.6259 |
| Curated metal site | 0.2583 |
| Non-metal background | 0.6197 |
| Active-site neighborhood | 0.5078 |
| Metal-site shell | 0.4495 |

Interpretation:

> ProteinMPNN is strong globally on VIM-2 but weak at metal-site residues. Fixed-backbone compatibility does not fully explain mechanism-local metal-site behavior.

This is the cleanest model-family result from P0.

## 15. Main Scientific Conclusion

The final claim is:

> Sequence-context, family-conservation, and fixed-backbone structure signals all help explain enzyme DMS fitness, but none of them remove the need for mechanism-sliced evaluation. A model can perform well globally while failing, weakening, or behaving ambiguously near catalytic, metal-binding, or active-site residues.

This is the intellectual contribution:

> Evaluate protein models where the biology happens, not only across the whole sequence.

## 16. What P0 Proves

P0 supports these claims:

- ESM-2 35M gives useful zero-shot signal on multiple enzyme DMS datasets.
- Model performance differs across residue classes.
- Exact catalytic-site analysis is often too small to overclaim.
- Broader active-site neighborhoods and ligand/metal shells can show stronger signal.
- Matched controls are required before interpreting mechanism-slice lifts.
- MSA conservation can beat ESM-2 on some enzymes.
- ProteinMPNN can be strong overall while weak at mechanism-local residues.
- A model-family comparison reveals different biological inductive biases.

## 17. What P0 Does Not Prove

P0 does not prove:

- ESM-2 understands catalysis.
- ProteinMPNN understands enzyme activity.
- Mechanism neighborhoods are always special.
- Active-site residues always have lower model performance.
- Retrospective DMS correlation is enough for enzyme design.
- A single exact catalytic-site Spearman with tiny `n` is conclusive.

## 18. Code Architecture

The repo is organized as a small production-style Python project.

| Area | Path | Role |
| --- | --- | --- |
| CLI | `src/p0_zero_shot_fitness/cli.py` | Parses commands and dispatches benchmark presets |
| Pipeline | `src/p0_zero_shot_fitness/pipeline.py` | Loads datasets, scores variants, writes outputs |
| Mutation parsing | `src/p0_zero_shot_fitness/mutations.py` | Validates strings like `A42G` against wild type |
| Data models | `src/p0_zero_shot_fitness/models.py` | Typed records for variants, scores, datasets |
| Metrics | `src/p0_zero_shot_fitness/metrics.py` | Spearman, top-k enrichment, subgroup metrics |
| Null controls | `src/p0_zero_shot_fitness/nulls.py` | Position and covariate-matched null logic |
| ESM scoring | `src/p0_zero_shot_fitness/scorers.py` | Placeholder and ESM-2 scorer interface |
| MSA conservation | `src/p0_zero_shot_fitness/conservation.py` | Alignment-derived conservation profile logic |
| Structure profiles | `src/p0_zero_shot_fitness/structure_profiles.py` | ProteinMPNN profile scoring |
| SVG plotting | `src/p0_zero_shot_fitness/plotting/svg.py` | Lightweight plot output |
| Tests | `tests/` | Unit and script-level regression tests |

## 19. Script Map

| Script | Role |
| --- | --- |
| `scripts/materialize_proteingym_dataset.py` | Pulls selected ProteinGym datasets from source archives |
| `scripts/derive_position_covariates.py` | Builds residue-level covariates for controls |
| `scripts/derive_msa_conservation.py` | Converts A2M alignments into conservation profiles |
| `scripts/score_msa_conservation_baseline.py` | Scores DMS variants with MSA conservation |
| `scripts/convert_proteinmpnn_npz_to_profile.py` | Converts ProteinMPNN `.npz` probabilities into P0 profile JSON |
| `scripts/score_structure_profile_baseline.py` | Scores variants using ProteinMPNN structure profiles |
| `scripts/compare_model_family_metrics.py` | Compares ESM-2, MSA, and ProteinMPNN metrics |
| `scripts/build_portfolio_figure.py` | Builds the four-enzyme ESM-2 visual |
| `scripts/build_model_family_figure.py` | Builds the ESM-2 vs MSA vs ProteinMPNN visual |

## 20. HPC and Compute Evidence

The project includes Savio/LBNL-style HPC execution:

- ESM-2 35M scoring jobs,
- ProteinMPNN profile generation,
- ProteinMPNN profile scoring,
- artifact transfer from Savio back to local repo,
- committed results and reproducible logs/runbooks.

Relevant files:

- `hpc/SAVIO.md`
- `hpc/SAVIO_PROTEINMPNN.md`
- `hpc/savio_esm2_35m_bgly.slurm`
- `hpc/savio_generate_proteinmpnn_profiles.slurm`
- `hpc/savio_score_proteinmpnn_profiles.slurm`

## 21. Reproducibility

Run tests:

```bash
python -m pytest
```

Current expected result:

```text
42 passed
```

Regenerate the model-family figure:

```bash
python scripts/build_model_family_figure.py
```

Regenerate the ProteinMPNN model-family comparison:

```bash
python scripts/compare_model_family_metrics.py \
  results/proteingym_vim2_esm2_t12_35M/metrics.json \
  results/proteingym_vim2_msa_conservation/metrics.json \
  results/proteingym_vim2_proteinmpnn/metrics.json \
  results/proteingym_amie_esm2_t12_35M/metrics.json \
  results/proteingym_amie_msa_conservation/metrics.json \
  results/proteingym_amie_proteinmpnn/metrics.json \
  results/proteingym_bgly_esm2_t12_35M/metrics.json \
  results/proteingym_bgly_msa_conservation/metrics.json \
  results/proteingym_bgly_proteinmpnn/metrics.json \
  --output results/proteingym_ready_enzyme_model_family_comparison.json
```

## 22. The Interview Explanation

Use this version:

> I built P0 to test whether protein language models fail differently near enzyme catalytic residues. Instead of only reporting whole-protein DMS correlation, I split variants by catalytic sites, metal sites, ligand contacts, catalytic shells, active-site neighborhoods, and background residues. Then I added matched controls so I could avoid overclaiming tiny residue groups. The benchmark compares ESM-2, MSA conservation, and ProteinMPNN, which separates sequence-context, evolutionary-family, and fixed-backbone structural signals. The most interesting final result is VIM-2: ProteinMPNN is best overall with Spearman 0.6259, but weak at curated metal-site residues with Spearman 0.2583 versus 0.6197 outside that group. That shows global mutation ranking can look strong while mechanism-local behavior remains a distinct failure mode.

## 23. The 30-Second Version

> P0 is a mechanism-aware evaluation harness for enzyme DMS prediction. It asks whether models work equally well at catalytic or mechanism-relevant residues. The answer is no: global performance and mechanism-local performance can diverge. ESM-2 works globally, MSA conservation wins on some enzymes, and ProteinMPNN is strong overall on VIM-2 but weak at metal-site residues. The takeaway is that protein ML models need mechanism-sliced evaluation before being trusted for enzyme engineering.

## 24. The 10-Second Version

> I built a benchmark showing that protein models can rank enzyme mutations well overall while still behaving differently at catalytic or metal-site residues.

## 25. What To Show On A Website

Recommended website block:

```text
Mechanism-sliced zero-shot protein fitness

Built a reproducible Python benchmark comparing ESM-2, MSA conservation,
and ProteinMPNN on enzyme DMS assays. The key result: ProteinMPNN is strongest
overall on VIM-2, but much weaker at curated metal-binding residues, showing
that global mutation ranking can hide mechanism-local failure modes.
```

Numbers to show:

```text
VIM-2 ProteinMPNN overall: 0.6259
VIM-2 ProteinMPNN metal site: 0.2583
VIM-2 ProteinMPNN background: 0.6197
```

Figure to show:

```text
docs/assets/p0_model_family_comparison.svg
```

## 26. Why This Helps For Research Scientist Roles

P0 demonstrates:

| Evidence category | What P0 shows |
| --- | --- |
| Biology depth | Enzyme mechanism labels, catalytic residues, metal sites, ligand contacts, DMS interpretation |
| ML/eval depth | Zero-shot scoring, model-family comparison, subgroup metrics, null controls |
| Production Python | Package structure, CLI, typed records, tests, scripts, reproducible outputs |
| Agentic systems thinking | Swappable scorer interfaces and workflow automation across local and HPC runs |
| Scientific communication | Final reports, public writeup, figures, Obsidian notes, interview framing |

## 27. Current Limitations

Important limitations:

1. Exact catalytic slices can be small.
2. ProteinMPNN was only run on the three target-aligned ready enzymes.
3. TEM-1 ProteinMPNN needs a target-aligned full-length structure or careful profile remap.
4. Retrospective DMS correlation is not the same as prospective design success.
5. ProteinMPNN does not model ligands, transition states, or catalytic chemistry.
6. MSA baselines depend on alignment quality and coverage.
7. Approximate SASA is useful for control matching, but not a replacement for specialized structural biology tooling.

## 28. Best Next Scientific Step

The next scientific step is not to add models endlessly.

The best next step is:

> Design a prospective validation protocol where the P0 evaluation logic is used to choose variants before experimental or higher-fidelity computational validation.

If staying retrospective, the next clean additions are:

1. Add a target-aligned TEM-1 ProteinMPNN profile.
2. Add one model-family summary table or figure for the website.
3. Only add MSA Transformer if it answers a specific unresolved question.

## 29. Final Read

P0 is complete as a portfolio project because it has:

- a sharp scientific question,
- real public biological datasets,
- multiple model families,
- mechanism-aware residue labels,
- matched controls,
- HPC execution,
- reproducible code,
- committed result artifacts,
- visual summaries,
- interview-ready explanations.

Final sentence:

> P0 turns a vague concern - "protein models may fail near catalytic chemistry" - into a concrete, reproducible, mechanism-sliced evaluation benchmark.

