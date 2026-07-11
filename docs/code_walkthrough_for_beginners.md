# P0 Code Walkthrough for Beginners

This guide explains how the P0 code turns a biological question into a reproducible benchmark.

## The Question

P0 asks:

> Does ESM-2 rank mutation effects differently near the chemistry of an enzyme than elsewhere in the protein?

For each TEM-1 mutation, the program combines:

1. the mutation string, such as `S68A`;
2. experimental fitness from deep mutational scanning;
3. a zero-shot ESM-2 score;
4. biological labels from UniProt and PDB.

It then compares the model and experimental rankings with Spearman correlation.

## Run the Teaching Example

From the repository root:

```bash
PYTHONPATH=src python examples/beginner_walkthrough.py
```

The script follows one catalytic mutation through loading, parsing, labeling,
scoring, and metrics. It uses the placeholder scorer so it runs without ESM.

## Program Flow

```text
CLI arguments
    |
    v
pipeline.py
    |-- io.py loads FASTA, CSV, and JSON
    |-- mutations.py validates mutation strings
    |-- labeling.py assigns biological groups
    |-- scorers.py assigns a model score
    |-- models.py stores each complete record
    |-- metrics.py compares scores with fitness
    '-- plotting/svg.py and io.py write outputs
```

## The Central Data Object

`VariantRecord` is the row that the analysis needs:

```python
@dataclass(frozen=True)
class VariantRecord:
    mutation: Mutation
    fitness: float
    is_catalytic: bool
    model_score: float
    residue_groups: frozenset[str] = frozenset()
```

A dataclass is a convenient container. `frozen=True` means a record cannot be
accidentally changed after it is created.

## Mutation Parsing

`parse_mutation("S68A", sequence)` separates:

- wild type: `S`
- position: `68`
- mutant: `A`

The important line is:

```python
observed = sequence[position - 1]
```

Biologists count residues from 1. Python lists and strings count from 0.
Therefore residue 68 is stored at Python index 67.

The function raises `ValueError` if the mutation format is wrong, the position
is outside the sequence, or the claimed wild-type residue does not match.

## ESM-2 Scoring

For mutation `S68A`, the scorer:

1. replaces residue 68 with ESM's mask token;
2. asks ESM-2 for probabilities of all amino acids at that position;
3. reads the log probability of `A`;
4. reads the log probability of wild-type `S`;
5. subtracts them.

```python
score = log_probability_mutant - log_probability_wild_type
```

Positive means ESM prefers the mutant to wild type. Negative means it prefers
wild type. This is a ranking signal, not a direct physical fitness value.

The `_position_log_probs` method is cached. TEM-1 has thousands of mutations but
only hundreds of positions, so the model needs one masked forward pass per
position rather than one per mutation.

## Biological Labels

The code uses integer residue sets:

```python
catalytic_residues = {68, 71, 128, 164}
```

A mutation is catalytic when:

```python
mutation.position in catalytic_residues
```

Additional groups include active-site neighborhoods, UniProt substrate-binding
positions, and residues within 5 Angstrom of an inhibitor in PDB 1M40.

## Spearman Correlation

Spearman asks whether two lists have a similar ordering.

```python
spearman(model_scores, experimental_fitness)
```

- `1.0`: identical ranking
- `0.0`: no monotonic ranking relationship
- `-1.0`: opposite ranking

The implementation converts both lists to ranks and then calculates Pearson
correlation on those ranks.

## Bootstrap Confidence Intervals

The code repeatedly resamples variants with replacement, recalculates
Spearman, and takes the central 95% of the estimates.

The catalytic set has only 57 variants, so its confidence interval is much
wider than the interval for the 4,726 non-catalytic variants.

## Tests

Tests are small experiments for the code:

```python
def test_spearman_identifies_perfect_rank_correlation() -> None:
    assert spearman([1, 2, 3], [10, 20, 30]) == pytest.approx(1.0)
```

This does not prove the biological conclusion. It proves that a specific code
behavior matches our expectation.

Run all tests:

```bash
python -m pytest
```

## Beginner Learning Order

1. Run `examples/beginner_walkthrough.py`.
2. Read `models.py` and `mutations.py`.
3. Change the example mutation from `S68A` to `H24S`.
4. Read `labeling.py` and print the groups for both mutations.
5. Read `metrics.py` and calculate Spearman for two three-number lists.
6. Read `pipeline.py` and trace one loop iteration.
7. Read `scorers.py` last; ESM is the most specialized part.
8. Add or modify one test and run `pytest`.

## First Coding Exercises

### Exercise 1

Print the wild-type amino acid at position 68:

```python
print(wild_type_sequence[67])
```

### Exercise 2

Count variants with fitness above `0.7`:

```python
count = sum(float(row["DMS_score"]) >= 0.7 for row in dms_rows)
print(count)
```

### Exercise 3

Add a function that returns the mean fitness for a list of records. Write a
test with three hand-created `VariantRecord` objects.

### Exercise 4

Fix the scatter plot's hard-coded x-axis label. Pass the scorer name into
`write_scatter_svg` and test the generated SVG text.

## What You Need to Be Able to Explain

You do not need to memorize every line. You should be able to explain:

- what one input row means;
- why mutation validation is necessary;
- how masked-marginal ESM scoring works;
- why biological subgroup labels matter;
- what Spearman and bootstrap intervals mean;
- how tests protect the pipeline;
- what this one-enzyme result does not prove.
