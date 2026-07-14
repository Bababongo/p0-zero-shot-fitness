# AnFdc1 External Target Plan

AnFdc1 is the safe external enzyme-engineering bridge between P0 and the Fdc1 AI-guided engineering project.

It is not a ProteinGym dataset yet. In the panel registry it is marked as `ANFDC1_EXTERNAL`, which means the validator should not expect ProteinGym metadata. Instead, it should ask whether we have the local scientific ingredients needed for a mechanism-aware benchmark.

## Why Add AnFdc1

AnFdc1 is a UbiD-family, prFMN-dependent ferulic acid decarboxylase. It is useful for P0 because the biological question depends on chemically meaningful residue groups:

- exact catalytic or cofactor-contact residues,
- prFMN pocket residues,
- substrate-pocket residues,
- active-site neighborhood residues,
- distal background residues.

This lets P0 ask whether sequence-only protein language models behave differently near cofactor-dependent chemistry than they do in generic protein background positions.

## Required Local Files

Before AnFdc1 can run through the P0 pipeline, collect:

1. Wild-type FASTA sequence.
2. Structure file, either experimental or trusted predicted structure.
3. Catalytic/cofactor residue JSON.
4. Residue-group JSON with prFMN pocket, substrate pocket, active-site neighborhood, surface, core, and background labels.
5. Variant table with mutation strings and measured activity, fitness, or enrichment.

## Current Status

`ANFDC1_EXTERNAL` is present in `data/panels/p0_enzyme_panel_candidates.csv`.

The registry validator correctly classifies it as:

`external_target_needs_dataset_and_annotations`

That is the right state. It means the project knows AnFdc1 is intentional, safe, and scientifically relevant, while also being honest that it cannot be scored until the external data package exists.

## Next Actions

- [ ] Add AnFdc1 FASTA.
- [ ] Add AnFdc1 structure.
- [ ] Define prFMN/cofactor residues.
- [ ] Define substrate-pocket residues.
- [ ] Define active-site-neighborhood shell.
- [ ] Add or design a variant table.
- [ ] Run placeholder scoring as a pipeline check.
- [ ] Run ESM-2 masked-marginal scoring when the variant table is ready.
