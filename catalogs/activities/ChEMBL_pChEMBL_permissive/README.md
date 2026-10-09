# ChEMBL permissive pChEMBL activity data

Permissively curated ChEMBL activity data: any record with a reported pChEMBL value, with
no restriction on assay type, assay quality, or confidence score beyond what ChEMBL itself
reports. This is the broadest, least-filtered endpoint in this catalog's ChEMBL family and
is intended as a baseline, not a high-confidence dataset.

## Deposition: ChEMBL37_permissive (CAR, FXR, VDR, LXR_alpha)

- **Source / version / retrieval date**: ChEMBL, release 37, retrieved 2026-10-08 via the
  ChEMBL REST API (`https://www.ebi.ac.uk/chembl/api/data/activity.json`), not the
  `chembl_downloader` SQLite dump the committed notebook uses. The live REST API only
  serves the current release, so ChEMBL37 is what's available through it; ChEMBL35 is not
  included in this deposition.
- **Targets**: constitutive androstane receptor (CAR, `CHEMBL5503`), farnesoid X receptor
  (FXR, `CHEMBL2047`), vitamin D receptor (VDR, `CHEMBL1977`), liver X receptor alpha
  (LXR_alpha, `CHEMBL2808`). LXR beta (`CHEMBL4093`) was deliberately excluded.
- **Selection criteria**: `target_chembl_id` matches the target above (human, single
  protein); `pchembl_value` is not null; `standard_units == 'nM'`. No restriction on
  `standard_type` (IC50, Ki, EC50, AC50, Potency, etc. are all included), no BAO term
  restriction, no confidence-score floor, and no document/mutant/assay-size filtering.
  Records lacking a parseable canonical SMILES are dropped before aggregation (null
  `OPENADMET_CANONICAL_SMILES`/`OPENADMET_INCHIKEY` can still appear in the raw file).
- **Aggregation rule**: raw records are canonicalized (RDKit canonical SMILES via
  `openadmet.toolkit.chemoinformatics.rdkit_funcs.canonical_smiles`, salts removed) and
  grouped by (`OPENADMET_CANONICAL_SMILES`, `OPENADMET_INCHIKEY`). For each group, `mean`,
  `median`, and `std` are reported for both `pchembl_value` and `standard_value`, plus
  `n_records` (count of source activity rows in the group). `standard_relation` is **not**
  consulted in aggregation; censored (`>`, `<`) and exact (`=`) measurements are mixed
  together in the mean/median. Treat aggregated values for compounds with a high fraction
  of censored records with caution; consult the raw file's `standard_relation` column to
  check.
- **Units**: `standard_value` / `standard_value_mean` / `standard_value_median` /
  `standard_value_std` are in nM (`OPENADMET_UNITS`). `pchembl_value` and its aggregates
  are unitless (−log10 of the molar activity).
- **Manual intervention**: none. Two mechanical fixes were applied post-generation: a typo
  in a document-field rename (`document_journal` → `doc_journal`) and a float-formatting
  artifact in `doc_pubmed_id` (e.g. `"16250653.0"` → `"16250653"`); both are generation
  bugs in the one-off script used for this deposition, not edits to source values.
- **License / attribution**: ChEMBL data is distributed under CC BY-SA 3.0 Unported.
  Attribute as: ChEMBL (EMBL-EBI), release 37.

### Known caveat affecting other depositions in this collection

The committed `curate_data_permissive.ipynb` calls
`PermissiveChEMBLTargetCurator(chembl_target_id=..., version=chembl_ver, ...)`, but the
curator's actual field is `chembl_version` (default `34`); pydantic silently drops the
unrecognized `version` kwarg. Every notebook-driven deposition in this collection
(`ChEMBL35_permissive`, `ChEMBL37_permissive` for AHR/PXR/CYP1A2/CYP3A4/CYP2C9/CYP2D6/
CYP2J2/HERG) therefore likely queried ChEMBL34 regardless of the version in its directory
name. A 2026-09-30 commit ("Rerun all data curation for correct ChEMBL versions") added an
assertion that would catch this (`assert pctc.chembl_version == chembl_ver`), but the
notebook's saved cell outputs for that commit are byte-identical to the prior run's
outputs, consistent with the assertion failing and the stale outputs being left in place
rather than a successful rerun. This deposition (CAR/FXR/VDR/LXR_alpha, built via the REST
API, not the buggy curator path) is not affected. The other targets' depositions were not
touched or regenerated as part of this work.

## Schema

### `*_raw.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `activity_id` | string | ChEMBL activity record ID. | `756238` |
| `assay_chembl_id` | string | ChEMBL assay ID. | `CHEMBL710256` |
| `assay_description` | string | Free-text assay description from ChEMBL. | `Ligand-dependent recruitment of steroid receptor co-activator 1 (SRC1) to Liver X receptor-alpha` |
| `assay_type` | string | ChEMBL assay type code. | `B` |
| `bao_endpoint` | string | BioAssay Ontology endpoint term. | `BAO_0000188` |
| `canonical_smiles` | string | SMILES as reported by ChEMBL (source, not RDKit-canonicalized). | `O=C(O)Cc1cccc(...)c1` |
| `molecule_chembl_id` | string | ChEMBL compound ID for the tested record. | `CHEMBL59030` |
| `parent_molecule_chembl_id` | string | ChEMBL compound ID of the parent (salt-stripped) molecule. | `CHEMBL59030` |
| `molecule_pref_name` | string | ChEMBL preferred compound name, if any. | `null` |
| `pchembl_value` | float64 | −log10 of the molar activity value, as reported by ChEMBL. | `6.9` |
| `standard_relation` | string | Censoring operator (`=`, `>`, `<`, etc.). | `=` |
| `standard_type` | string | Assay endpoint type. | `EC50` |
| `standard_units` | string | Units of `standard_value`; always `nM` in this deposition (query filter). | `nM` |
| `standard_value` | float64 | Reported activity value in `standard_units`. | `125.0` |
| `activity_comment` | string | Free-text activity comment from ChEMBL (e.g. "inactive"), if any. | `null` |
| `target_chembl_id` | string | ChEMBL target ID. | `CHEMBL2808` |
| `target_organism` | string | Target organism. | `Homo sapiens` |
| `doc_id` | string | ChEMBL document ID. | `CHEMBL1135404` |
| `doc_year` | string | Publication year. | `2002` |
| `doc_journal` | string | Journal name. | `J Med Chem` |
| `doc_doi` | string | Publication DOI, if known. | `10.1021/jm0255116` |
| `doc_pubmed_id` | string | PubMed ID, if known. | `11985463` |
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES (salts removed); the deduplication key. | `O=C(O)CC1=CC=CC(...)=C1` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `NAXSRXHZFIBFMI-UHFFFAOYSA-N` |
| `OPENADMET_TARGET` | string | Short target name used in this catalog. | `LXR_alpha` |
| `OPENADMET_TARGET_ID` | string | ChEMBL target ID (duplicate of `target_chembl_id`, provided for the standard schema). | `CHEMBL2808` |
| `OPENADMET_ENDPOINT` | string | `pChEMBL_permissive` for this collection (mixed `standard_type`). | `pChEMBL_permissive` |
| `OPENADMET_UNITS` | string | Units of `standard_value`. | `nM` |
| `OPENADMET_SOURCE` | string | Originating database. | `ChEMBL` |
| `OPENADMET_SOURCE_VERSION` | string | ChEMBL release. | `37` |

### `*_aggregated.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES; the deduplication key. | `O=S(=O)(C1=CC=CC=C1)N(CC(F)(F)F)...` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `SGIWFELWJPNFDH-UHFFFAOYSA-N` |
| `pchembl_value_mean` | float64 | Mean `pchembl_value` across the compound's records. | `7.121269841269841` |
| `pchembl_value_median` | float64 | Median `pchembl_value`. | `7.07` |
| `pchembl_value_std` | float64 | Std. dev. of `pchembl_value`; null when `n_records == 1` (expected, not missing). | `0.6921297008404261` |
| `standard_value_mean` | float64 | Mean `standard_value` (nM) across the compound's records. | `389.6793650793651` |
| `standard_value_median` | float64 | Median `standard_value` (nM). | `85.0` |
| `standard_value_std` | float64 | Std. dev. of `standard_value`; null when `n_records == 1`. | `1758.9426641757416` |
| `n_records` | int64 | Number of raw activity rows behind this compound. | `63` |
| `OPENADMET_TARGET` | string | Short target name. | `LXR_alpha` |
| `OPENADMET_TARGET_ID` | string | ChEMBL target ID. | `CHEMBL2808` |
| `OPENADMET_ENDPOINT` | string | `pChEMBL_permissive` for this collection. | `pChEMBL_permissive` |
| `OPENADMET_UNITS` | string | Units of the `standard_value_*` columns. | `nM` |
| `OPENADMET_SOURCE` | string | Originating database. | `ChEMBL` |
| `OPENADMET_SOURCE_VERSION` | string | ChEMBL release. | `37` |
