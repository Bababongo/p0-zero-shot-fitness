import pytest

from p0_zero_shot_fitness.mutations import parse_mutation


def test_parse_mutation_validates_wild_type_residue() -> None:
    mutation = parse_mutation("H4A", "MSTHACDEFGHIKLMNPQRSTVWY")

    assert mutation.raw == "H4A"
    assert mutation.wild_type == "H"
    assert mutation.position == 4
    assert mutation.mutant == "A"


def test_parse_mutation_rejects_mismatched_residue() -> None:
    with pytest.raises(ValueError, match="observed H"):
        parse_mutation("A4G", "MSTHACDEFGHIKLMNPQRSTVWY")
