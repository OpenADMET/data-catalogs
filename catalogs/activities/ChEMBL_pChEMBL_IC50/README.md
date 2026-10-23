# ChEMBL IC50 pChEMBL activity data

ChEMBL activity data restricted to `standard_type == 'IC50'` records that carry a reported
pChEMBL value, with no further assay-quality curation beyond ChEMBL's own reporting.

## Deposition: ChEMBL37_IC50 (CAR, FXR, VDR, LXR_alpha)

- **Source / version / generation date**: ChEMBL, release 37, generated 2026-10-23 by running
  `curate_data_IC50.ipynb`'s `PermissiveChEMBLTargetCurator` against the official
  `chembl_downloader` SQLite dump for release 37. ChEMBL35 is not included in this
  deposition.
- **Targets**: constitutive androstane receptor (CAR, `CHEMBL5503`), farnesoid X receptor
  (FXR, `CHEMBL2047`), vitamin D receptor (VDR, `CHEMBL1977`), liver X receptor alpha
  (LXR_alpha, `CHEMBL2808`). LXR beta (`CHEMBL4093`) was deliberately excluded.
- **Selection criteria** (from `PermissiveChEMBLTargetCurator.get_templated_query`):
  `target_chembl_id` matches the target above; `standard_type == 'IC50'`; `pchembl_value` is
  not null (`require_pchembl=True`); `standard_units == 'nM'` (`require_units='nM'`);
  `activities.data_validity_comment IS NULL`. No BAO term restriction, confidence-score
  floor, or document/mutant/assay-size filtering. `standard_relation` is not retrieved by
  this query, so censored (`>`, `<`) measurements are not distinguishable from exact (`=`)
  ones in this deposition; consult ChEMBL directly by `assay_id`/`doc_id` if censoring
  matters for a given record.
- **Aggregation rule**: raw records are canonicalized (RDKit canonical SMILES via
  `openadmet.toolkit.chemoinformatics.rdkit_funcs.canonical_smiles`, salts removed) and
  grouped by (`OPENADMET_CANONICAL_SMILES`, `OPENADMET_INCHIKEY`). For each group, `mean`,
  `median`, and `std` are reported for both `pchembl_value` and `standard_value`, plus
  `assay_id_count` (the number of raw rows behind the compound; not the number of distinct
  assays).
- **Units**: `standard_value` and its aggregates are in nM (enforced by the query's
  `require_units='nM'` filter; not carried as its own column). `pchembl_value` and its
  aggregates are unitless (−log10 of the molar IC50).
- **Manual intervention**: none. These are the direct output of the notebook's main loop
  (`agg.to_parquet(...)` / `raw.to_parquet(...)`), with no post-hoc edits.
- **Known schema gap**: unlike other collections in this catalog, these raw/aggregated files
  do not carry the `OPENADMET_TARGET`, `OPENADMET_TARGET_ID`, `OPENADMET_ENDPOINT`,
  `OPENADMET_UNITS`, `OPENADMET_SOURCE`, or `OPENADMET_SOURCE_VERSION` standard-schema
  columns; `PermissiveChEMBLTargetCurator`'s output doesn't populate them. A consumer must
  track target/endpoint/source/version from the filename and this README rather than from
  the data itself.
- **License / attribution**: ChEMBL data is distributed under CC BY-SA 3.0 Unported.
  Attribute as: ChEMBL (EMBL-EBI), release 37.

### ChEMBL37 cache repair (2026-10-23)

`curate_data_IC50.ipynb`'s `chembl_downloader` cache for release 37 was found corrupted
(`PRAGMA integrity_check` failed with "database disk image is malformed"), which is why the
main loop couldn't run. A clean copy was downloaded and integrity-checked
(`activities`: 24,527,044 rows; `molecule_dictionary`: 2,921,148 rows; `compound_structures`:
2,897,819 rows) before this deposition was generated.

### Known caveat affecting other depositions in this collection

The committed `curate_data_IC50.ipynb` calls `PermissiveChEMBLTargetCurator(
chembl_target_id=..., version=chembl_ver, standard_type="IC50", ...)`, but the curator's
actual field is `chembl_version` (default `34`); older versions of `openadmet-toolkit`
silently dropped the unrecognized `version` kwarg via pydantic. Every notebook-driven
deposition in this collection run before that was fixed (`ChEMBL35_IC50`, `ChEMBL37_IC50`
for AHR/PXR/CYP1A2/CYP3A4/CYP2C9/CYP2D6/CYP2J2/HERG) likely queried ChEMBL34 regardless of
the version in its directory name. `openadmet-toolkit` commit `a7c110e` ("Fix issue 111
ChEMBL version bug in curators") fixed this by aliasing `version` to `chembl_version`. This
deposition (CAR/FXR/VDR/LXR_alpha) was generated after that fix and is not affected; the
other targets' depositions were not touched or regenerated as part of this work.

## Schema

### `*_raw.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `assay_id` | int64 | ChEMBL internal numeric assay ID. | `1729516` |
| `doc_id` | int64 | ChEMBL internal numeric document ID. | `107021` |
| `standard_value` | float64 | Reported IC50 in nM (query-filtered to `nM`). | `4510.0` |
| `molregno` | int64 | ChEMBL internal parent-molecule registry number. | `2263896` |
| `canonical_smiles` | string | SMILES as reported by ChEMBL (source, not RDKit-canonicalized). | `Cc1ccc2nc([C@H](CC3CCNCC3)N3C(=O)CN(c4ccc(Oc5ccccc5)cc4)C3=O)n(C)c2c1` |
| `standard_inchi_key` | string | InChIKey as reported by ChEMBL (source). | `OSIAUSSYLUETML-NDEPHWFRSA-N` |
| `tid` | int64 | ChEMBL internal numeric target ID. | `11180` |
| `target_chembl_id` | string | ChEMBL target ID. | `CHEMBL2047` |
| `pchembl_value` | float64 | −log10 of the molar IC50, as reported by ChEMBL. | `5.35` |
| `compound_name` | string | ChEMBL preferred compound name, if any. | `null` |
| `standard_type` | string | Always `IC50` in this deposition (query filter). | `IC50` |
| `bao_endpoint` | string | BioAssay Ontology endpoint term. | `BAO_0000190` |
| `assay_description` | string | Free-text assay description from ChEMBL. | `Antagonist activity at human FXR expressed in Hep3B cells assessed as inhibition of CDCA-induced FXR response element driven luciferase activity after 24 hrs` |
| `assay_organism` | string | Assay organism. | `Homo sapiens` |
| `assay_strain` | string | Assay strain, if any. | `null` |
| `assay_tissue` | string | Assay tissue, if any. | `null` |
| `assay_type` | string | ChEMBL assay type code. | `B` |
| `assay_cell_type` | string | Assay cell line, if any. | `null` |
| `assay_subcellular_fraction` | string | Assay subcellular fraction, if any. | `null` |
| `variant_id` | Int64 | ChEMBL variant ID, if the assay used a mutant. | `null` |
| `doc_year` | int64 | Publication year. | `2018` |
| `doc_journal` | string | Journal name. | `ACS Med Chem Lett` |
| `doc_doi` | string | Publication DOI, if known. | `10.1021/acsmedchemlett.7b00363` |
| `doc_title` | string | Publication title. | `Nonacidic Chemotype Possessing N-Acylated Piperidine Moiety as Potent Farnesoid X Receptor (FXR) Antagonists.` |
| `doc_authors` | string | Publication author list. | `Teno N, Yamashita Y, Iguchi Y, ...` |
| `doc_abstract` | string | Publication abstract. | `Farnesoid X receptor (FXR) plays a major role...` |
| `doc_patent_id` | string | Patent ID, if the document is a patent. | `null` |
| `doc_pubmed_id` | Int64 | PubMed ID, if known. | `29456791` |
| `doc_chembl_release_id` | int64 | Internal ID into ChEMBL's own `chembl_release` table (**not** a human-readable release number like `"37"`). | `26` |
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES (salts removed); the deduplication key. | `CC1=CC=C2N=C([C@H](CC3CCNCC3)N3C(O)=CN(C4=CC=C(OC5=CC=CC=C5)C=C4)C3=O)N(C)C2=C1` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `XBPJRGYFYIJUNK-NDEPHWFRSA-N` |

### `*_aggregated.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES; the deduplication key. | `C/C=C1/C(=O)C[C@H]2...` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `IVLRQLIWEVLAQF-AUKWTSKRSA-N` |
| `assay_id_count` | int64 | Number of raw activity rows behind this compound (not the number of distinct assays). | `9` |
| `standard_value_mean` | float64 | Mean IC50 (nM) across the compound's records. | `27477.777778` |
| `standard_value_median` | float64 | Median IC50 (nM). | `13000.0` |
| `standard_value_std` | float64 | Std. dev. of IC50 (nM); null when `assay_id_count == 1`. | `31197.346753` |
| `pchembl_value_mean` | float64 | Mean `pchembl_value` (IC50) across the compound's records. | `4.803333` |
| `pchembl_value_median` | float64 | Median `pchembl_value`. | `4.89` |
| `pchembl_value_std` | float64 | Std. dev. of `pchembl_value`; null when `assay_id_count == 1`. | `0.493786` |
