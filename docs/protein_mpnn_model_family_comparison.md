# ProteinMPNN Model-Family Comparison

## Question

Does a structure-conditioned inverse-folding model see the same mechanism-local mutation patterns as ESM-2 and MSA conservation?

This is the first P0 model-family comparison across three ready enzymes:

- VIM-2 metallo-beta-lactamase
- AMIE aliphatic amidase
- beta-glucosidase

TEM-1 is intentionally excluded from this first ProteinMPNN pass because the available `1M40.pdb` structure is not target-aligned to the full 286-aa ProteinGym DMS sequence.

## Model Families

| Model family | Signal tested |
| --- | --- |
| ESM-2 masked marginal | Sequence-context protein language model signal |
| MSA conservation | Family-conservation log-odds signal |
| ProteinMPNN profile | Fixed-backbone structure-compatibility signal |

ProteinMPNN is not treated as an activity model. It asks whether a mutant amino acid is plausible for the fixed backbone:

```text
score = log P(mutant amino acid | backbone) - log P(wild-type amino acid | backbone)
```

## Overall Results

| Dataset | ESM-2 35M Overall | MSA Overall | ProteinMPNN Overall | Read |
| --- | ---: | ---: | ---: | --- |
| VIM-2 | 0.5280 | 0.4931 | 0.6259 | ProteinMPNN is strongest overall, but weak at metal-site residues. |
| AMIE | 0.4082 | 0.4306 | 0.3457 | MSA is strongest overall; ProteinMPNN is weakest. |
| Beta-glucosidase | 0.4481 | 0.5615 | 0.3618 | MSA is strongest overall; ProteinMPNN is weak globally. |

## Mechanism-Slice Results

### VIM-2

| Scorer | Overall | Curated Metal Site | Non-Metal Background | Active-Site Neighborhood | Metal-Site Shell |
| --- | ---: | ---: | ---: | ---: | ---: |
| ESM-2 35M | 0.5280 | 0.3449 | 0.5085 | 0.6133 | 0.5846 |
| MSA conservation | 0.4931 | 0.3079 | 0.4724 | 0.6342 | 0.5699 |
| ProteinMPNN | 0.6259 | 0.2583 | 0.6197 | 0.5078 | 0.4495 |

VIM-2 is the strongest new result. ProteinMPNN is best overall, but drops sharply on curated metal-binding residues and the metal-site shell. The metal-site shell is lower than the position-matched null (`p = 0.0`) but inside the stricter covariate-matched null (`p = 0.29`).

Interpretation: fixed-backbone compatibility explains broad VIM-2 mutation tolerance well, but does not recover the chemistry-local metal-site behavior.

### AMIE

| Scorer | Overall | Curated Catalytic Site | Non-Catalytic Background | Active-Site Neighborhood | Catalytic Shell |
| --- | ---: | ---: | ---: | ---: | ---: |
| ESM-2 35M | 0.4082 | 0.0911 | 0.3991 | 0.4335 | 0.3071 |
| MSA conservation | 0.4306 | 0.2944 | 0.4217 | 0.4620 | 0.3110 |
| ProteinMPNN | 0.3457 | 0.2662 | 0.3371 | 0.3884 | 0.2579 |

AMIE remains a counterexample to overclaiming. MSA conservation is the strongest overall model family. ProteinMPNN does not rescue the weak ESM-2 catalytic-site story.

Interpretation: AMIE's mutation effects are not cleanly explained by either sequence-context PLM scores or fixed-backbone compatibility alone.

### Beta-Glucosidase

| Scorer | Overall | Curated Catalytic Site | Non-Catalytic Background | Active-Site Neighborhood | Catalytic Shell |
| --- | ---: | ---: | ---: | ---: | ---: |
| ESM-2 35M | 0.4481 | 0.5105 | 0.4434 | 0.4327 | 0.3808 |
| MSA conservation | 0.5615 | 0.4406 | 0.5585 | 0.3759 | 0.3596 |
| ProteinMPNN | 0.3618 | 0.6364 | 0.3571 | 0.3219 | 0.2633 |

ProteinMPNN has the highest exact catalytic-site correlation, but that slice has only 12 variants. It is inside the position-matched null (`p = 0.484`) and borderline under the strict covariate-matched null (`p = 0.052`).

Interpretation: the exact catalytic-site result is intriguing but too small to carry the conclusion alone. The broader catalytic shell is weak for ProteinMPNN.

## Main Scientific Read

The ProteinMPNN comparison makes P0 stronger because it separates three biological signals:

1. ESM-2: sequence-context plausibility.
2. MSA conservation: family-level evolutionary constraint.
3. ProteinMPNN: fixed-backbone structural compatibility.

The key result is not that one model wins everywhere. The key result is that the model families disagree in mechanism-relevant regions.

Best current claim:

> Structure-conditioned ProteinMPNN can improve global VIM-2 mutation ranking, but it does not eliminate the mechanism-local failure pattern. Across ready enzymes, catalytic and metal-site behavior remains model-family dependent and cannot be reduced to fixed-backbone compatibility alone.

## Artifacts

- `results/proteingym_vim2_proteinmpnn/metrics.json`
- `results/proteingym_amie_proteinmpnn/metrics.json`
- `results/proteingym_bgly_proteinmpnn/metrics.json`
- `results/proteingym_ready_enzyme_model_family_comparison.json`

## What To Say In An Interview

> After comparing ESM-2 against MSA conservation, I added ProteinMPNN as a structure-conditioned baseline. That let me ask whether the same DMS mutations are explained by sequence context, family conservation, or fixed-backbone compatibility. VIM-2 was the most interesting: ProteinMPNN was best overall, but much worse at metal-site residues than at the rest of the protein. That supports the core P0 argument: global mutation ranking can look good while mechanism-local chemistry remains a distinct evaluation problem.
