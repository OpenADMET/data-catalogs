# ChEMBL Ki pChEMBL activity data

ChEMBL activity data restricted to `standard_type == 'Ki'` records that carry a reported
pChEMBL value, with no further assay-quality curation beyond ChEMBL's own reporting.

## Deposition: ChEMBL37_Ki (LXR_alpha only)

- **Source / version / retrieval date**: ChEMBL, release 37, retrieved 2026-10-08 via the
  ChEMBL REST API (`https://www.ebi.ac.uk/chembl/api/data/activity.json`), not the
  `chembl_downloader` SQLite dump the committed notebook uses. The live REST API only
  serves the current release, so ChEMBL37 is what's available through it; ChEMBL35 is not
  included in this deposition.
- **Targets**: liver X receptor alpha (LXR_alpha, `CHEMBL2808`) only. CAR (`CHEMBL5503`),
  FXR (`CHEMBL2047`), and VDR (`CHEMBL1977`) were evaluated and dropped from this endpoint:
  a preview query against the ChEMBL REST API returned 1, 0, and 16 pChEMBL-bearing Ki
  records respectively, too sparse to be useful as a Ki dataset.
- **Selection criteria**: `target_chembl_id == 'CHEMBL2808'` (human, single protein);
  `standard_type == 'Ki'`; `pchembl_value` is not null; `standard_units == 'nM'`. No BAO
  term restriction, no confidence-score floor, no document/mutant/assay-size filtering.
  Records lacking a parseable canonical SMILES are dropped before aggregation.
- **Aggregation rule**: raw records are canonicalized (RDKit canonical SMILES via
  `openadmet.toolkit.chemoinformatics.rdkit_funcs.canonical_smiles`, salts removed) and
  grouped by (`OPENADMET_CANONICAL_SMILES`, `OPENADMET_INCHIKEY`). For each group, `mean`,
  `median`, and `std` are reported for both `pchembl_value` and `standard_value`, plus
  `n_records`. `standard_relation` is **not** consulted in aggregation; censored (`>`, `<`)
  and exact (`=`) measurements are mixed together in the mean/median. Consult the raw
  file's `standard_relation` column before trusting an aggregate for a compound with many
  censored records.
- **Units**: `standard_value` / `standard_value_mean` / `standard_value_median` /
  `standard_value_std` are in nM (`OPENADMET_UNITS`). `pchembl_value` and its aggregates
  are unitless (−log10 of the molar Ki).
- **Manual intervention**: none beyond the target-list restriction above. Two mechanical
  fixes were applied post-generation: a typo in a document-field rename
  (`document_journal` → `doc_journal`) and a float-formatting artifact in `doc_pubmed_id`
  (e.g. `"11300870.0"` → `"11300870"`); both are generation bugs in the one-off script used
  for this deposition, not edits to source values.
- **License / attribution**: ChEMBL data is distributed under CC BY-SA 3.0 Unported.
  Attribute as: ChEMBL (EMBL-EBI), release 37.

### Known caveat affecting other depositions in this collection

The committed `curate_data_Ki.ipynb` calls `PermissiveChEMBLTargetCurator(
chembl_target_id=..., version=chembl_ver, standard_type="Ki", ...)`, but the curator's
actual field is `chembl_version` (default `34`); pydantic silently drops the unrecognized
`version` kwarg. Every notebook-driven deposition in this collection (`ChEMBL35_Ki`,
`ChEMBL37_Ki` for AHR/PXR/CYP1A2/CYP3A4/CYP2C9/CYP2D6/CYP2J2/HERG) therefore likely
queried ChEMBL34 regardless of the version in its directory name. A 2026-09-30 commit
("Rerun all data curation for correct ChEMBL versions") added an assertion that would
catch this (`assert pctc.chembl_version == chembl_ver`), but the notebook's saved cell
outputs for that commit are byte-identical to the prior run's outputs, consistent with the
assertion failing and the stale outputs being left in place rather than a successful
rerun. This deposition (LXR_alpha, built via the REST API, not the buggy curator path) is
not affected. The other targets' depositions were not touched or regenerated as part of
this work.

## Schema

### `*_raw.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `activity_id` | string | ChEMBL activity record ID. | `825726` |
| `assay_chembl_id` | string | ChEMBL assay ID. | `CHEMBL710259` |
| `assay_description` | string | Free-text assay description from ChEMBL. | `Binding affinity towards LXR alpha receptor was determined in LiSA` |
| `assay_type` | string | ChEMBL assay type code. | `B` |
| `bao_endpoint` | string | BioAssay Ontology endpoint term. | `BAO_0000192` |
| `canonical_smiles` | string | SMILES as reported by ChEMBL (source, not RDKit-canonicalized). | `CC(C)CC[C@H](O)[C@@H](C)[C@H]1...` |
| `molecule_chembl_id` | string | ChEMBL compound ID for the tested record. | `CHEMBL1243244` |
| `parent_molecule_chembl_id` | string | ChEMBL compound ID of the parent (salt-stripped) molecule. | `CHEMBL1243244` |
| `molecule_pref_name` | string | ChEMBL preferred compound name, if any. | `null` |
| `pchembl_value` | float64 | −log10 of the molar Ki, as reported by ChEMBL. | `6.75` |
| `standard_relation` | string | Censoring operator (`=`, `>`, `<`, etc.). | `=` |
| `standard_type` | string | Always `Ki` in this deposition (query filter). | `Ki` |
| `standard_units` | string | Units of `standard_value`; always `nM` (query filter). | `nM` |
| `standard_value` | float64 | Reported Ki in `standard_units`. | `180.0` |
| `activity_comment` | string | Free-text activity comment from ChEMBL (e.g. "inactive"), if any. | `null` |
| `target_chembl_id` | string | ChEMBL target ID. | `CHEMBL2808` |
| `target_organism` | string | Target organism. | `Homo sapiens` |
| `doc_id` | string | ChEMBL document ID. | `CHEMBL1134370` |
| `doc_year` | string | Publication year. | `2001` |
| `doc_journal` | string | Journal name. | `J Med Chem` |
| `doc_doi` | string | Publication DOI, if known. | `10.1021/jm0004749` |
| `doc_pubmed_id` | string | PubMed ID, if known. | `11300870` |
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES (salts removed); the deduplication key. | `CC(C)CC[C@H](O)[C@@H](C)[C@H]1CC[C@H]2...` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `RZPAXNJLEKLXNO-QUOSNDFLSA-N` |
| `OPENADMET_TARGET` | string | Short target name used in this catalog. | `LXR_alpha` |
| `OPENADMET_TARGET_ID` | string | ChEMBL target ID (duplicate of `target_chembl_id`, provided for the standard schema). | `CHEMBL2808` |
| `OPENADMET_ENDPOINT` | string | Always `Ki` in this deposition. | `Ki` |
| `OPENADMET_UNITS` | string | Units of `standard_value`. | `nM` |
| `OPENADMET_SOURCE` | string | Originating database. | `ChEMBL` |
| `OPENADMET_SOURCE_VERSION` | string | ChEMBL release. | `37` |

### `*_aggregated.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES; the deduplication key. | `CCC(O)C1=CN=C(N2CCN3C(=NC4=CC(CO)=C(...` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `OEALQQJYLLGJFL-WHCXFUJUSA-N` |
| `pchembl_value_mean` | float64 | Mean `pchembl_value` (Ki) across the compound's records. | `7.055` |
| `pchembl_value_median` | float64 | Median `pchembl_value`. | `7.055` |
| `pchembl_value_std` | float64 | Std. dev. of `pchembl_value`; null when `n_records == 1` (expected, not missing). | `0.098150` |
| `standard_value_mean` | float64 | Mean Ki (nM) across the compound's records. | `89.0` |
| `standard_value_median` | float64 | Median Ki (nM). | `89.0` |
| `standard_value_std` | float64 | Std. dev. of Ki (nM); null when `n_records == 1`. | `19.629909` |
| `n_records` | int64 | Number of raw activity rows behind this compound. | `4` |
| `OPENADMET_TARGET` | string | Short target name. | `LXR_alpha` |
| `OPENADMET_TARGET_ID` | string | ChEMBL target ID. | `CHEMBL2808` |
| `OPENADMET_ENDPOINT` | string | Always `Ki` in this deposition. | `Ki` |
| `OPENADMET_UNITS` | string | Units of the `standard_value_*` columns. | `nM` |
| `OPENADMET_SOURCE` | string | Originating database. | `ChEMBL` |
| `OPENADMET_SOURCE_VERSION` | string | ChEMBL release. | `37` |
