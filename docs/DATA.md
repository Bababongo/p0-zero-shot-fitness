# Data Notes

## ProteinGym TEM-1 Assay

This repository includes a processed ProteinGym substitution assay:

- `data/proteingym/BLAT_ECOLX_Firnberg_2014.csv`
- Dataset ID: `BLAT_ECOLX_Firnberg_2014`
- Protein: TEM-1 beta-lactamase (`BLAT_ECOLX`)
- Source: ProteinGym DMS substitutions benchmark
- Source repository: <https://github.com/OATML-Markslab/ProteinGym>
- Data archive: <https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/DMS_ProteinGym_substitutions.zip>

The assay file is used here as a portfolio benchmark for zero-shot variant-effect prediction. The repository also includes local metadata, catalytic-residue annotations, and residue-group annotations so the analysis can run reproducibly.

## Catalytic Residue Labels

The UniProt-validated active-site set is:

```text
[68, 71, 128, 164]
```

UniProt P62593 (`BLAT_ECOLX`) annotates active sites at positions 68, 71, 128, and 164 in natural 286-aa sequence numbering. It also annotates a substrate-binding site spanning positions 232-234.

Many beta-lactamase papers use Ambler/class-A numbering. In that convention, the corresponding common residue names are Ser70, Lys73, Ser130, Glu166, and Lys234. The benchmark uses ProteinGym/UniProt numbering.

## Residue Groups

The residue-group file is:

- `data/proteingym/BLAT_ECOLX_residue_groups.json`

It defines:

- `uniprot_active_site`: positions 68, 71, 128, and 164
- `uniprot_substrate_binding_site`: positions 232-234
- `active_site_neighborhood`: a +/-2 residue window around the UniProt-supported active-site and substrate-binding positions
- `structure_ligand_contact_5a`: residues with any heavy atom within 5.0 Angstrom of the `CB4` inhibitor in PDB 1M40 chain A

The PDB residue numbers in 1M40 are offset by +2 relative to ProteinGym/UniProt target numbering. The contact derivation uses `scripts/derive_ligand_contacts.py` with `--pdb-to-target-offset -2`.

Source records:

- `data/proteingym/source_records/uniprot_P62593_BLAT_ECOLX.json`
- `data/proteingym/source_records/rcsb_1M40_entry.json`
- `data/proteingym/source_records/1M40_CB4_contacts_5A.json`
- `data/proteingym/structures/1M40.pdb`

## Model Outputs

The `results/` directory contains reproducible benchmark outputs from:

- placeholder conservation scorer,
- ESM-2 8M masked-marginal scorer.

ESM model weights are not stored in this repository.
