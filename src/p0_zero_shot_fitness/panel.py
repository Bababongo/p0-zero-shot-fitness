from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from p0_zero_shot_fitness.models import JsonDict


PANEL_REQUIRED_COLUMNS = [
    "tier",
    "dms_id",
    "uniprot_id",
    "molecule_name",
    "enzyme_class_or_family",
    "assay_readout",
    "selection_type",
    "single_mutants",
    "sequence_length",
    "structure_file",
    "primary_reason_to_include",
    "main_annotation_need",
]

PROTEINGYM_REQUIRED_FIELDS = [
    "DMS_id",
    "DMS_filename",
    "UniProt_ID",
    "target_seq",
    "seq_len",
    "DMS_number_single_mutants",
    "molecule_name",
    "selection_assay",
    "raw_DMS_phenotype_name",
    "raw_DMS_mutant_column",
    "pdb_file",
]

FIRST_PANEL_RECOMMENDATION_ORDER = [
    "A4GRB6_PSEAI_Chen_2020",
    "AMIE_PSEAE_Wrenbeck_2017",
    "Q59976_STRSQ_Romero_2015",
]


@dataclass(frozen=True)
class PanelCandidate:
    tier: int
    dms_id: str
    uniprot_id: str
    molecule_name: str
    enzyme_class_or_family: str
    assay_readout: str
    selection_type: str
    single_mutants: int
    sequence_length: int
    structure_file: str
    primary_reason_to_include: str
    main_annotation_need: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "PanelCandidate":
        return cls(
            tier=int(row["tier"]),
            dms_id=row["dms_id"],
            uniprot_id=row["uniprot_id"],
            molecule_name=row["molecule_name"],
            enzyme_class_or_family=row["enzyme_class_or_family"],
            assay_readout=row["assay_readout"],
            selection_type=row["selection_type"],
            single_mutants=int(row["single_mutants"]),
            sequence_length=int(row["sequence_length"]),
            structure_file=row["structure_file"],
            primary_reason_to_include=row["primary_reason_to_include"],
            main_annotation_need=row["main_annotation_need"],
        )


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def missing_columns(rows: list[dict[str, str]], required_columns: list[str]) -> list[str]:
    if not rows:
        return required_columns
    return [column for column in required_columns if column not in rows[0]]


def load_panel_candidates(path: Path) -> list[PanelCandidate]:
    rows = load_csv_rows(path)
    missing = missing_columns(rows, PANEL_REQUIRED_COLUMNS)
    if missing:
        raise ValueError(f"Panel registry is missing required columns: {', '.join(missing)}")
    return [PanelCandidate.from_row(row) for row in rows]


def load_proteingym_metadata(path: Path) -> dict[str, dict[str, str]]:
    rows = load_csv_rows(path)
    missing = missing_columns(rows, PROTEINGYM_REQUIRED_FIELDS)
    if missing:
        raise ValueError(f"ProteinGym metadata is missing required columns: {', '.join(missing)}")
    return {row["DMS_id"]: row for row in rows}


def cost_units(single_mutants: int, sequence_length: int) -> int:
    return single_mutants * sequence_length


def cost_category(units: int) -> str:
    if units < 1_000_000:
        return "small"
    if units < 2_500_000:
        return "medium"
    if units < 5_000_000:
        return "large"
    return "very_large"


def local_annotation_status(candidate: PanelCandidate, data_dir: Path) -> dict[str, bool]:
    return {
        "has_local_dms_csv": (data_dir / f"{candidate.dms_id}.csv").exists(),
        "has_local_fasta": (data_dir / f"{candidate.uniprot_id}.fasta").exists(),
        "has_local_catalytic_json": (data_dir / f"{candidate.uniprot_id}_catalytic_residues.json").exists(),
        "has_local_residue_groups_json": (data_dir / f"{candidate.uniprot_id}_residue_groups.json").exists(),
    }


def candidate_mismatches(candidate: PanelCandidate, metadata: dict[str, str]) -> list[str]:
    mismatches = []
    checks = [
        ("uniprot_id", candidate.uniprot_id, metadata.get("UniProt_ID", "")),
        ("single_mutants", str(candidate.single_mutants), metadata.get("DMS_number_single_mutants", "")),
        ("sequence_length", str(candidate.sequence_length), metadata.get("seq_len", "")),
        ("structure_file", candidate.structure_file, metadata.get("pdb_file", "")),
    ]
    for name, candidate_value, metadata_value in checks:
        if metadata_value and candidate_value != metadata_value:
            mismatches.append(f"{name}: registry={candidate_value}, proteingym={metadata_value}")
    return mismatches


def validation_status(
    metadata_found: bool,
    missing_metadata_fields: list[str],
    mismatches: list[str],
    local_status: dict[str, bool],
) -> str:
    if not metadata_found:
        return "missing_proteingym_metadata"
    if missing_metadata_fields or mismatches:
        return "metadata_needs_review"
    if all(local_status.values()):
        return "ready_for_p0_pipeline"
    return "metadata_ready_needs_local_data_and_annotations"


def summarize_candidate(
    candidate: PanelCandidate,
    metadata_by_id: dict[str, dict[str, str]],
    data_dir: Path,
) -> JsonDict:
    metadata = metadata_by_id.get(candidate.dms_id)
    units = cost_units(candidate.single_mutants, candidate.sequence_length)
    if metadata is None:
        missing_metadata_fields = PROTEINGYM_REQUIRED_FIELDS
        mismatches: list[str] = []
        metadata_found = False
    else:
        missing_metadata_fields = [field for field in PROTEINGYM_REQUIRED_FIELDS if not metadata.get(field)]
        mismatches = candidate_mismatches(candidate, metadata)
        metadata_found = True

    local_status = local_annotation_status(candidate, data_dir)
    return {
        "tier": candidate.tier,
        "dms_id": candidate.dms_id,
        "uniprot_id": candidate.uniprot_id,
        "molecule_name": candidate.molecule_name,
        "enzyme_class_or_family": candidate.enzyme_class_or_family,
        "selection_type": candidate.selection_type,
        "single_mutants": candidate.single_mutants,
        "sequence_length": candidate.sequence_length,
        "estimated_masked_marginal_score_units": units,
        "compute_cost_category": cost_category(units),
        "structure_file": candidate.structure_file,
        "primary_reason_to_include": candidate.primary_reason_to_include,
        "main_annotation_need": candidate.main_annotation_need,
        "metadata_found": metadata_found,
        "missing_proteingym_fields": missing_metadata_fields,
        "metadata_mismatches": mismatches,
        "local_status": local_status,
        "status": validation_status(
            metadata_found,
            missing_metadata_fields,
            mismatches,
            local_status,
        ),
    }


def recommended_first_panel(candidates: list[JsonDict]) -> list[JsonDict]:
    by_id = {str(candidate["dms_id"]): candidate for candidate in candidates}
    recommendations = [
        by_id[dms_id]
        for dms_id in FIRST_PANEL_RECOMMENDATION_ORDER
        if dms_id in by_id and by_id[dms_id]["metadata_found"]
    ]
    if len(recommendations) >= 3:
        return recommendations[:3]
    remaining = [
        candidate
        for candidate in candidates
        if candidate not in recommendations and candidate["metadata_found"] and candidate["tier"] == 1
    ]
    remaining = sorted(remaining, key=lambda item: item["estimated_masked_marginal_score_units"])
    return (recommendations + remaining)[:3]


def validate_panel_registry(panel_csv: Path, proteingym_metadata_csv: Path, data_dir: Path) -> JsonDict:
    panel_candidates = load_panel_candidates(panel_csv)
    metadata_by_id = load_proteingym_metadata(proteingym_metadata_csv)
    candidate_summaries = [
        summarize_candidate(candidate, metadata_by_id=metadata_by_id, data_dir=data_dir)
        for candidate in panel_candidates
    ]
    status_counts: dict[str, int] = {}
    for candidate in candidate_summaries:
        status = str(candidate["status"])
        status_counts[status] = status_counts.get(status, 0) + 1

    recommendations = recommended_first_panel(candidate_summaries)
    return {
        "panel_csv": str(panel_csv),
        "proteingym_metadata_csv": str(proteingym_metadata_csv),
        "data_dir": str(data_dir),
        "n_candidates": len(candidate_summaries),
        "n_metadata_matches": sum(bool(candidate["metadata_found"]) for candidate in candidate_summaries),
        "status_counts": status_counts,
        "recommended_first_three": [
            {
                "dms_id": candidate["dms_id"],
                "molecule_name": candidate["molecule_name"],
                "enzyme_class_or_family": candidate["enzyme_class_or_family"],
                "estimated_masked_marginal_score_units": candidate["estimated_masked_marginal_score_units"],
                "compute_cost_category": candidate["compute_cost_category"],
                "main_annotation_need": candidate["main_annotation_need"],
            }
            for candidate in recommendations
        ],
        "candidate_summaries": candidate_summaries,
    }
