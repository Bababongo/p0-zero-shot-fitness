# Data Notes

## ProteinGym Assays

This repository includes processed ProteinGym substitution assays for:

- `BLAT_ECOLX_Firnberg_2014` - TEM-1 beta-lactamase.
- `A4GRB6_PSEAI_Chen_2020` - VIM-2 metallo-beta-lactamase.

ProteinGym source:

- Source repository: <https://github.com/OATML-Markslab/ProteinGym>
- Data archive: <https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/DMS_ProteinGym_substitutions.zip>
- AF2 structure archive: <https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/ProteinGym_AF2_structures.zip>

Use `scripts/materialize_proteingym_dataset.py` to extract one dataset from the public ProteinGym substitutions archive and generate local FASTA/metadata files from `data/proteingym/DMS_substitutions.csv`.

## TEM-1 Assay

This repository includes a processed ProteinGym substitution assay:

- `data/proteingym/BLAT_ECOLX_Firnberg_2014.csv`
- Dataset ID: `BLAT_ECOLX_Firnberg_2014`
- Protein: TEM-1 beta-lactamase (`BLAT_ECOLX`)
- Source: ProteinGym DMS substitutions benchmark
The assay file is used here as a portfolio benchmark for zero-shot variant-effect prediction. The repository also includes local metadata, catalytic-residue annotations, and residue-group annotations so the analysis can run reproducibly.

## TEM-1 Catalytic Residue Labels

The UniProt-validated active-site set is:

```text
[68, 71, 128, 164]
```

UniProt P62593 (`BLAT_ECOLX`) annotates active sites at positions 68, 71, 128, and 164 in natural 286-aa sequence numbering. It also annotates a substrate-binding site spanning positions 232-234.

Many beta-lactamase papers use Ambler/class-A numbering. In that convention, the corresponding common residue names are Ser70, Lys73, Ser130, Glu166, and Lys234. The benchmark uses ProteinGym/UniProt numbering.

## TEM-1 Residue Groups

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

## VIM-2 Assay

This repository includes the first second-enzyme ProteinGym assay:

- `data/proteingym/A4GRB6_PSEAI_Chen_2020.csv`
- Dataset ID: `A4GRB6_PSEAI_Chen_2020`
- Protein: VIM-2 metallo-beta-lactamase (`A4GRB6_PSEAI`)
- Variants: 5,004 single amino-acid substitutions
- Fitness column: `DMS_score`
- Mutation column: `mutant`

Local support files:

- `data/proteingym/A4GRB6_PSEAI.fasta`
- `data/proteingym/A4GRB6_PSEAI_Chen_2020_metadata.json`
- `data/proteingym/A4GRB6_PSEAI_catalytic_residues.json`
- `data/proteingym/A4GRB6_PSEAI_residue_groups.json`
- `data/proteingym/structures/A4GRB6_PSEAI.pdb`
- `data/proteingym/source_records/A4GRB6_PSEAI_metal_site_shell_5A.json`

## VIM-2 Catalytic / Metal-Site Labels

The VIM-2 exact site is:

```text
[114, 116, 118, 179, 198, 240]
```

These are 1-indexed positions in the 266-aa ProteinGym target sequence. The labels are curated from conserved B1 metallo-beta-lactamase active-site and zinc-binding motifs. UniProt accession A4GRB6 is inactive/deleted, so these labels are intentionally marked as motif-curated rather than UniProt-backed.

## VIM-2 Residue Groups

The VIM-2 residue-group file defines:

- `curated_metal_binding_site`: positions 114, 116, 118, 179, 198, and 240.
- `active_site_neighborhood`: a +/-2 residue window around those curated motif positions.
- `structure_metal_site_shell_5a`: residues with any heavy atom within 5.0 Angstrom of any curated metal-binding residue heavy atom in the ProteinGym AF2 structure `A4GRB6_PSEAI.pdb`.

The structure shell is not a ligand-bound experimental contact map. It is a structure-derived metal-site proximity slice from the ProteinGym AF2 model. A ligand-bound VIM-2 contact group should still be added later if a suitable experimental structure and reproducible ligand/contact rule are selected.

## Model Outputs

The `results/` directory contains reproducible benchmark outputs from:

- placeholder conservation scorer,
- ESM-2 8M masked-marginal scorer.

ESM model weights are not stored in this repository.
