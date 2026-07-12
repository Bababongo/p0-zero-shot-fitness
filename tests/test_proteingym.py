import zipfile

from p0_zero_shot_fitness.proteingym import materialize_proteingym_dataset


def test_materialize_proteingym_dataset_writes_fasta_metadata_and_extracts_dms(tmp_path) -> None:
    metadata_csv = tmp_path / "DMS_substitutions.csv"
    metadata_csv.write_text(
        "DMS_id,DMS_filename,UniProt_ID,target_seq,seq_len,DMS_number_single_mutants,"
        "molecule_name,selection_assay,raw_DMS_phenotype_name,raw_DMS_mutant_column,pdb_file,"
        "includes_multiple_mutants,selection_type\n"
        "TEST_ID,TEST_ID.csv,TEST_PROT,ACD,3,2,Test enzyme,activity,DMS_score,mutant,TEST.pdb,FALSE,Activity\n",
        encoding="utf-8",
    )

    archive_path = tmp_path / "substitutions.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("DMS_ProteinGym_substitutions/TEST_ID.csv", "mutant,DMS_score\nA1C,0.1\n")

    payload = materialize_proteingym_dataset(
        dms_id="TEST_ID",
        metadata_csv=metadata_csv,
        output_dir=tmp_path / "out",
        archive_path=archive_path,
    )

    assert payload["dms_csv_exists"] is True
    assert payload["dms_csv_extracted"] is True
    assert payload["sequence_length"] == 3
    assert (tmp_path / "out" / "TEST_PROT.fasta").read_text(encoding="utf-8").startswith(
        ">TEST_PROT ProteinGym target sequence for TEST_ID\nACD\n"
    )
    assert (tmp_path / "out" / "TEST_ID.csv").read_text(encoding="utf-8") == "mutant,DMS_score\nA1C,0.1\n"
