# ChEMBL IC50 pChEMBL activity data

ChEMBL activity data restricted to `standard_type == 'IC50'` records that carry a reported
pChEMBL value, with no further assay-quality curation beyond ChEMBL's own reporting.

## Deposition: ChEMBL37_IC50 (CAR, FXR, VDR, LXR_alpha)

- **Source / version / retrieval date**: ChEMBL, release 37, retrieved 2026-10-08 via the
  ChEMBL REST API (`https://www.ebi.ac.uk/chembl/api/data/activity.json`), not the
  `chembl_downloader` SQLite dump the committed notebook uses. The live REST API only
  serves the current release, so ChEMBL37 is what's available through it; ChEMBL35 is not
  included in this deposition.
- **Targets**: constitutive androstane receptor (CAR, `CHEMBL5503`), farnesoid X receptor
  (FXR, `CHEMBL2047`), vitamin D receptor (VDR, `CHEMBL1977`), liver X receptor alpha
  (LXR_alpha, `CHEMBL2808`). LXR beta (`CHEMBL4093`) was deliberately excluded.
- **Selection criteria**: `target_chembl_id` matches the target above (human, single
  protein); `standard_type == 'IC50'`; `pchembl_value` is not null; `standard_units ==
  'nM'`. No BAO term restriction, no confidence-score floor, no document/mutant/assay-size
  filtering. Records lacking a parseable canonical SMILES are dropped before aggregation.
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
  are unitless (−log10 of the molar IC50).
- **Manual intervention**: none. Two mechanical fixes were applied post-generation: a typo
  in a document-field rename (`document_journal` → `doc_journal`) and a float-formatting
  artifact in `doc_pubmed_id` (e.g. `"16250653.0"` → `"16250653"`); both are generation
  bugs in the one-off script used for this deposition, not edits to source values.
- **License / attribution**: ChEMBL data is distributed under CC BY-SA 3.0 Unported.
  Attribute as: ChEMBL (EMBL-EBI), release 37.

### Known caveat affecting other depositions in this collection

The committed `curate_data_IC50.ipynb` calls `PermissiveChEMBLTargetCurator(
chembl_target_id=..., version=chembl_ver, standard_type="IC50", ...)`, but the curator's
actual field is `chembl_version` (default `34`); pydantic silently drops the unrecognized
`version` kwarg. Every notebook-driven deposition in this collection (`ChEMBL35_IC50`,
`ChEMBL37_IC50` for AHR/PXR/CYP1A2/CYP3A4/CYP2C9/CYP2D6/CYP2J2/HERG) therefore likely
queried ChEMBL34 regardless of the version in its directory name. A 2026-09-30 commit
("Rerun all data curation for correct ChEMBL versions") added an assertion that would
catch this (`assert pctc.chembl_version == chembl_ver`), but the notebook's saved cell
outputs for that commit are byte-identical to the prior run's outputs, consistent with the
assertion failing and the stale outputs being left in place rather than a successful
rerun. This deposition (CAR/FXR/VDR/LXR_alpha, built via the REST API, not the buggy
curator path) is not affected. The other targets' depositions were not touched or
regenerated as part of this work.

## Schema

### `*_raw.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `activity_id` | string | ChEMBL activity record ID. | `1610246` |
| `assay_chembl_id` | string | ChEMBL assay ID. | `CHEMBL881762` |
| `assay_description` | string | Free-text assay description from ChEMBL. | `Inhibitory concentration against Farnesoid X receptor; range from 50-100000` |
| `assay_type` | string | ChEMBL assay type code. | `B` |
| `bao_endpoint` | string | BioAssay Ontology endpoint term. | `BAO_0000190` |
| `canonical_smiles` | string | SMILES as reported by ChEMBL (source, not RDKit-canonicalized). | `C/C=C1\C(=O)C[C@H]2...` |
| `molecule_chembl_id` | string | ChEMBL compound ID for the tested record. | `CHEMBL410683` |
| `parent_molecule_chembl_id` | string | ChEMBL compound ID of the parent (salt-stripped) molecule. | `CHEMBL410683` |
| `molecule_pref_name` | string | ChEMBL preferred compound name, if any. | `GUGGULSTERONE` |
| `pchembl_value` | float64 | −log10 of the molar IC50, as reported by ChEMBL. | `4.00` |
| `standard_relation` | string | Censoring operator (`=`, `>`, `<`, etc.). | `=` |
| `standard_type` | string | Always `IC50` in this deposition (query filter). | `IC50` |
| `standard_units` | string | Units of `standard_value`; always `nM` (query filter). | `nM` |
| `standard_value` | float64 | Reported IC50 in `standard_units`. | `100000.0` |
| `activity_comment` | string | Free-text activity comment from ChEMBL (e.g. "inactive"), if any. | `null` |
| `target_chembl_id` | string | ChEMBL target ID. | `CHEMBL2047` |
| `target_organism` | string | Target organism. | `Homo sapiens` |
| `doc_id` | string | ChEMBL document ID. | `CHEMBL1140376` |
| `doc_year` | string | Publication year. | `2005` |
| `doc_journal` | string | Journal name. | `J Med Chem` |
| `doc_doi` | string | Publication DOI, if known. | `10.1021/jm0505056` |
| `doc_pubmed_id` | string | PubMed ID, if known. | `16250653` |
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES (salts removed); the deduplication key. | `C/C=C1\C(=O)C[C@H]2[C@@H]3CC=C4...` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `IVLRQLIWEVLAQF-OSJVMJFVSA-N` |
| `OPENADMET_TARGET` | string | Short target name used in this catalog. | `FXR` |
| `OPENADMET_TARGET_ID` | string | ChEMBL target ID (duplicate of `target_chembl_id`, provided for the standard schema). | `CHEMBL2047` |
| `OPENADMET_ENDPOINT` | string | Always `IC50` in this deposition. | `IC50` |
| `OPENADMET_UNITS` | string | Units of `standard_value`. | `nM` |
| `OPENADMET_SOURCE` | string | Originating database. | `ChEMBL` |
| `OPENADMET_SOURCE_VERSION` | string | ChEMBL release. | `37` |

### `*_aggregated.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES; the deduplication key. | `C/C=C1/C(=O)C[C@H]2...` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `IVLRQLIWEVLAQF-AUKWTSKRSA-N` |
| `pchembl_value_mean` | float64 | Mean `pchembl_value` (IC50) across the compound's records. | `4.803333` |
| `pchembl_value_median` | float64 | Median `pchembl_value`. | `4.89` |
| `pchembl_value_std` | float64 | Std. dev. of `pchembl_value`; null when `n_records == 1` (expected, not missing). | `0.493786` |
| `standard_value_mean` | float64 | Mean IC50 (nM) across the compound's records. | `27477.777778` |
| `standard_value_median` | float64 | Median IC50 (nM). | `13000.0` |
| `standard_value_std` | float64 | Std. dev. of IC50 (nM); null when `n_records == 1`. | `31197.346753` |
| `n_records` | int64 | Number of raw activity rows behind this compound. | `9` |
| `OPENADMET_TARGET` | string | Short target name. | `FXR` |
| `OPENADMET_TARGET_ID` | string | ChEMBL target ID. | `CHEMBL2047` |
| `OPENADMET_ENDPOINT` | string | Always `IC50` in this deposition. | `IC50` |
| `OPENADMET_UNITS` | string | Units of the `standard_value_*` columns. | `nM` |
| `OPENADMET_SOURCE` | string | Originating database. | `ChEMBL` |
| `OPENADMET_SOURCE_VERSION` | string | ChEMBL release. | `37` |
