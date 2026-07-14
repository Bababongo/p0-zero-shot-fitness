import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "derive_ligand_contacts.py"
SPEC = importlib.util.spec_from_file_location("derive_ligand_contacts", SCRIPT_PATH)
derive_ligand_contacts = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(derive_ligand_contacts)


def test_mmcif_contacts_use_label_seq_id_for_target_position() -> None:
    mmcif_text = """
data_example
loop_
_atom_site.group_PDB
_atom_site.id
_atom_site.type_symbol
_atom_site.label_atom_id
_atom_site.label_alt_id
_atom_site.label_comp_id
_atom_site.label_asym_id
_atom_site.label_entity_id
_atom_site.label_seq_id
_atom_site.pdbx_PDB_ins_code
_atom_site.Cartn_x
_atom_site.Cartn_y
_atom_site.Cartn_z
_atom_site.occupancy
_atom_site.B_iso_or_equiv
_atom_site.pdbx_formal_charge
_atom_site.auth_seq_id
_atom_site.auth_comp_id
_atom_site.auth_asym_id
_atom_site.auth_atom_id
_atom_site.pdbx_PDB_model_num
ATOM   1 C CA . HIS A 1 114 ? 0.000 0.000 0.000 1.00 10.00 ? 116 HIS A CA 1
HETATM 2 O O15 . WL3 F 3 .   ? 1.000 0.000 0.000 1.00 10.00 ? 1298 WL3 A O15 1
#
"""

    contacts = derive_ligand_contacts.derive_mmcif_ligand_contacts(
        mmcif_text=mmcif_text,
        protein_chain="A",
        ligand_chain="A",
        ligand="WL3",
        cutoff_angstrom=5.0,
    )

    assert sorted(contacts) == [114]
    assert contacts[114]["pdb_position"] == 116
