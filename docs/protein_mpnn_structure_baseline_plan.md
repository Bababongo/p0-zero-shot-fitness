# ProteinMPNN Structure Baseline Plan

## Why Add ProteinMPNN

ProteinMPNN is the right next model-family comparison because it changes the question from:

> Does a sequence language model rank enzyme mutations well?

to:

> Does a structure-conditioned inverse-folding model rank the same mutations differently?

That matters for P0 because catalytic, ligand-contact, and metal-shell residues are not only sequence-context questions. They are also fixed-backbone compatibility questions. ProteinMPNN gives a lightweight way to ask whether the current ESM-2 mechanism-slice results are mostly sequence/evolutionary signal or whether a backbone-conditioned model sees a different pattern.

## Scientific Role

Treat ProteinMPNN as a structure-conditioned baseline, not as a direct enzyme-activity model.

ProteinMPNN does not know the DMS assay, ligand chemistry, transition states, or catalytic mechanism. It asks whether a residue is plausible for a given backbone. That makes it useful as a control:

- if ProteinMPNN matches ESM-2, the signal may be mostly structural compatibility/conservation-like constraint;
- if ESM-2 beats ProteinMPNN globally, ESM-2 may add sequence-family or evolutionary fitness signal beyond fixed-backbone recovery;
- if ProteinMPNN is stronger in buried/structured regions but weak at catalytic chemistry, that supports the idea that mechanism-local activity is not reducible to backbone compatibility.

## Score Definition

For each single mutant:

```text
ProteinMPNN score = log P(mutant amino acid | backbone) - log P(wild type amino acid | backbone)
```

Higher means the mutant amino acid is more compatible with the fixed backbone relative to the wild-type amino acid under the structure-conditioned profile.

This mirrors the ESM-2 masked-marginal log-ratio setup, but the conditioning signal is structure instead of sequence context.

## Profile Format

The repo expects a structure profile JSON:

```json
{
  "format": "p0_structure_log_probability_profile.v1",
  "scorer": "ProteinMPNNProfileScorer",
  "protein": "BLAT_ECOLX",
  "structure": "1M40",
  "chain": "A",
  "positions": {
    "1": {
      "wild_type": "H",
      "log_probabilities": {
        "A": -3.2,
        "C": -6.4,
        "D": -4.0
      }
    }
  }
}
```

The `positions` object should contain all amino-acid positions used by the DMS assay. Each position can use either:

- `log_probabilities`, preferred; or
- `probabilities`, which the scorer converts to log probabilities.

## Run Template

After generating a ProteinMPNN profile for one enzyme, score it with:

```bash
python scripts/score_structure_profile_baseline.py \
  --scored-variants-csv results/proteingym_blat_esm2_t12_35M/scored_variants.csv \
  --structure-profile-json results/proteingym_blat_proteinmpnn/profile.json \
  --position-covariates-json results/proteingym_blat_esm2_t12_35M/position_covariates.json \
  --dataset-name "ProteinGym BLAT_ECOLX_Firnberg_2014" \
  --output-dir results/proteingym_blat_proteinmpnn \
  --bootstrap-iterations 1000 \
  --null-iterations 1000 \
  --covariate-null-iterations 1000
```

Repeat for VIM-2, AMIE, and beta-glucosidase using the matching existing `scored_variants.csv` and `position_covariates.json`.

## Minimum Valuable Comparison

Run ProteinMPNN on all four enzymes and compare:

- overall Spearman,
- exact catalytic or metal-site Spearman,
- ligand-contact / catalytic-shell / metal-shell Spearman,
- matched-position null controls,
- conservation-plus-SASA matched controls.

Do not start with MSA Transformer unless the ProteinMPNN comparison changes the story or leaves a clear ambiguity.

## Readiness Audit

Use:

```bash
python scripts/audit_proteinmpnn_targets.py \
  --output-json results/proteinmpnn_target_audit.json
```

Current audit result:

| Dataset | Structure | Ready? | Reason |
| --- | --- | --- | --- |
| TEM-1 / `BLAT_ECOLX_Firnberg_2014` | `1M40.pdb` | No | Experimental structure starts at PDB residue 26, has 263 residues, and does not directly match the 286-aa DMS target sequence. Stage a target-aligned BLAT_ECOLX structure or remap the ProteinMPNN profile before scoring. |
| VIM-2 / `A4GRB6_PSEAI_Chen_2020` | `A4GRB6_PSEAI.pdb` | Yes | Structure sequence matches the 266-aa DMS target sequence. |
| AMIE / `AMIE_PSEAE_Wrenbeck_2017` | `AMIE_PSEAE.pdb` | Yes | Structure sequence matches the 346-aa DMS target sequence. |
| Beta-glucosidase / `Q59976_STRSQ_Romero_2015` | `Q59976_STRSQ.pdb` | Yes | Structure sequence matches the 501-aa DMS target sequence. |

This means the first ProteinMPNN run should use VIM-2, AMIE, and beta-glucosidase. Add TEM-1 after a target-aligned BLAT_ECOLX structure is staged.

## Expected Interpretation

The strongest final claim would not be "ProteinMPNN wins" or "ESM-2 wins."

The stronger claim is:

> P0 compares sequence-conditioned, family-conservation, and structure-conditioned zero-shot signals on the same enzyme DMS assays and the same mechanism-local residue labels.

That is a mature model-family comparison: same data, same labels, same controls, different biological inductive biases.

## Stop Rule

Stop after ProteinMPNN unless one of these is true:

- ProteinMPNN strongly disagrees with ESM-2 in a mechanism-local slice;
- ProteinMPNN explains all the apparent ESM-2 mechanism-local signal;
- a reviewer/interviewer asks whether an MSA-aware neural model changes the result.

Only then add MSA Transformer.
