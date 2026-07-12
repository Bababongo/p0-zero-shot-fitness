from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path

from p0_zero_shot_fitness.models import JsonDict


def load_metadata_row(metadata_csv: Path, dms_id: str) -> dict[str, str]:
    with metadata_csv.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["DMS_id"] == dms_id:
                return row
    raise ValueError(f"ProteinGym metadata does not contain DMS_id={dms_id!r}")


def fasta_text(uniprot_id: str, dms_id: str, sequence: str) -> str:
    return f">{uniprot_id} ProteinGym target sequence for {dms_id}\n{sequence}\n"


def metadata_payload(row: dict[str, str]) -> JsonDict:
    keys = [
        "DMS_id",
        "DMS_filename",
        "UniProt_ID",
        "molecule_name",
        "selection_assay",
        "raw_DMS_phenotype_name",
        "raw_DMS_mutant_column",
        "seq_len",
        "DMS_number_single_mutants",
        "includes_multiple_mutants",
        "pdb_file",
        "selection_type",
    ]
    return {key: row.get(key, "") for key in keys}


def find_archive_member(archive: zipfile.ZipFile, filename: str) -> str:
    matches = [name for name in archive.namelist() if name.endswith(f"/{filename}") or name == filename]
    if not matches:
        raise ValueError(f"Archive does not contain {filename!r}")
    if len(matches) > 1:
        exact_matches = [name for name in matches if name == filename]
        if len(exact_matches) == 1:
            return exact_matches[0]
    return sorted(matches, key=len)[0]


def extract_dms_csv(archive_path: Path, dms_filename: str, output_dir: Path) -> Path:
    output_path = output_dir / dms_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        member = find_archive_member(archive, dms_filename)
        with archive.open(member) as source, output_path.open("wb") as destination:
            destination.write(source.read())
    return output_path


def materialize_proteingym_dataset(
    dms_id: str,
    metadata_csv: Path,
    output_dir: Path,
    archive_path: Path | None = None,
) -> JsonDict:
    row = load_metadata_row(metadata_csv, dms_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    uniprot_id = row["UniProt_ID"]
    dms_filename = row["DMS_filename"]
    fasta_path = output_dir / f"{uniprot_id}.fasta"
    metadata_path = output_dir / f"{dms_id}_metadata.json"
    dms_csv_path = output_dir / dms_filename

    fasta_path.write_text(
        fasta_text(uniprot_id=uniprot_id, dms_id=dms_id, sequence=row["target_seq"]),
        encoding="utf-8",
    )
    metadata_path.write_text(json.dumps(metadata_payload(row), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    extracted_dms = False
    if archive_path is not None:
        dms_csv_path = extract_dms_csv(archive_path=archive_path, dms_filename=dms_filename, output_dir=output_dir)
        extracted_dms = True

    return {
        "dms_id": dms_id,
        "uniprot_id": uniprot_id,
        "dms_csv": str(dms_csv_path),
        "dms_csv_exists": dms_csv_path.exists(),
        "dms_csv_extracted": extracted_dms,
        "fasta": str(fasta_path),
        "metadata_json": str(metadata_path),
        "sequence_length": int(row["seq_len"]),
        "single_mutants": int(row["DMS_number_single_mutants"]),
        "variant_column": row["raw_DMS_mutant_column"],
        "fitness_column": "DMS_score",
    }
