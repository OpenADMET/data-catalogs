# BindingDB IC50 activity data

[BindingDB](https://www.bindingdb.org/) binding-affinity data restricted to
`affinity_type == 'IC50'` records. Mirrors `ChEMBL_pChEMBL_IC50` in scope and schema
philosophy, from a different source.

## Deposition: BindingDB20261008_IC50 (CAR, FXR, VDR, LXR_alpha)

- **Source / version / retrieval date**: BindingDB, retrieved 2026-10-08 via the public
  REST API (`https://bindingdb.org/rest/getLigandsByUniprots`). BindingDB's REST API has
  no discrete numbered release the way ChEMBL does, so the retrieval date (`20261008`) is
  used as the deposition's version token.
- **Targets**: constitutive androstane receptor (CAR, UniProt `Q14994`), farnesoid X
  receptor (FXR, UniProt `Q96RI1`), vitamin D receptor (VDR, UniProt `P11473`), liver X
  receptor alpha (LXR_alpha, UniProt `Q13133`). LXR beta was excluded, matching the ChEMBL
  depositions for these targets.
- **Selection criteria**: `getLigandsByUniprots` for each UniProt ID above with
  `cutoff=10000000` (nM, effectively unrestricted), then filtered client-side to
  `affinity_type == 'IC50'` -- the BindingDB API has no server-side type filter. No
  BAO/confidence-score equivalent filtering; BindingDB's ligand-search endpoint doesn't
  expose one. Records lacking a parseable canonical SMILES are dropped before
  aggregation.
- **Aggregation rule**: raw records are canonicalized (RDKit canonical SMILES via
  `openadmet.toolkit.chemoinformatics.rdkit_funcs.canonical_smiles`, salts removed) and
  grouped by (`OPENADMET_CANONICAL_SMILES`, `OPENADMET_INCHIKEY`). For each group, `mean`,
  `median`, and `std` of `standard_value` are reported, plus `n_records`.
  `standard_relation` is **not** consulted in aggregation; censored (`>`, `<`) and exact
  (`=`) measurements are mixed together in the mean/median. Consult the raw file's
  `standard_relation` column before trusting an aggregate for a compound with many
  censored records. Unlike the ChEMBL depositions, there is no `pchembl_value` equivalent
  here -- BindingDB's API returns only the raw affinity value and type, not a normalized
  potency.
- **Units**: all `standard_value*` columns are in nM. BindingDB's API response does not
  carry an explicit units field; nM is BindingDB's documented convention for this
  endpoint and was confirmed by comparing overlapping compound/target pairs against their
  ChEMBL nM values, not asserted from the API response itself.
- **Manual intervention**: none.
- **Known gaps versus the ChEMBL depositions**: BindingDB's `getLigandsByUniprots`
  response does not include publication year, journal, or an assay/document description,
  only `pmid` and `doi` (carried as `doc_pubmed_id`/`doc_doi`). There is no
  `activity_comment` equivalent. These columns are omitted rather than shipped as
  structurally-null placeholders, per this repo's dtype guidance.
- **License / attribution**: BindingDB data is available under CC BY 3.0 (see
  https://www.bindingdb.org/rwd/bind/info.jsp). Attribute as: BindingDB, retrieved
  2026-10-08.

### Note on overlap with ChEMBL

BindingDB and ChEMBL both draw heavily from the same primary literature, so a large
fraction of these records likely duplicate (or near-duplicate) what's already in
`ChEMBL_pChEMBL_IC50`. No deduplication across sources has been performed; anyone merging
the two should dedupe on `OPENADMET_INCHIKEY` + `OPENADMET_TARGET` and decide how to
handle cases where both sources report the same literature value.

## Schema

### `*_raw.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `bindingdb_target_name_queried` | string | Target name as returned by BindingDB for the queried UniProt ID. | `Vitamin D3 receptor` |
| `bindingdb_monomer_id` | string | BindingDB's internal ligand (monomer) ID. | `50389854` |
| `canonical_smiles` | string | SMILES as reported by BindingDB (source, not RDKit-canonicalized). | `COc1ccc(NC(c2ccccc2Cl)c2c(C)[nH]c3ccccc23)cc1` |
| `standard_type` | string | Always `IC50` in this deposition (client-side filter). | `IC50` |
| `affinity` | string | Raw affinity string from BindingDB, including any leading censoring operator; source of `standard_relation`/`standard_value`. | `5800` |
| `doc_pubmed_id` | string | PubMed ID, if known. | `22563729` |
| `doc_doi` | string | Publication DOI, if known. | `10.1021/jm300460c` |
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES (salts removed); the deduplication key. | `COC1=CC=C(NC(C2=CC=CC=C2Cl)C2=C(C)NC3=CC=CC=C23)C=C1` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `NMSSLXZRBIVVTN-UHFFFAOYSA-N` |
| `standard_relation` | string | Censoring operator parsed from `affinity` (`=`, `>`, `<`, `>=`, `<=`); defaults to `=` when `affinity` has no operator. | `=` |
| `standard_value` | float64 | Numeric IC50 parsed from `affinity`, in nM. | `5800.0` |
| `OPENADMET_TARGET` | string | Short target name used in this catalog. | `VDR` |
| `OPENADMET_TARGET_ID` | string | UniProt accession queried. | `P11473` |
| `OPENADMET_ENDPOINT` | string | Always `IC50` in this deposition. | `IC50` |
| `OPENADMET_UNITS` | string | Units of `standard_value`. | `nM` |
| `OPENADMET_SOURCE` | string | Originating database. | `BindingDB` |
| `OPENADMET_SOURCE_VERSION` | string | Retrieval date, `YYYYMMDD` (BindingDB has no release number). | `20261008` |

### `*_aggregated.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES; the deduplication key. | `C=C1/C(=C\C=C2/CCC[C@]3(C)[C@@H]([C@H](C)CCCC(C)(C)O)...` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `GMRQFYUYWCNGIN-NKMMMXOESA-N` |
| `standard_value_mean` | float64 | Mean IC50 (nM) across the compound's records. | `323.268765` |
| `standard_value_median` | float64 | Median IC50 (nM). | `0.95` |
| `standard_value_std` | float64 | Std. dev. of IC50 (nM); null when `n_records == 1` (expected, not missing). | `1437.379246` |
| `n_records` | int64 | Number of raw activity rows behind this compound. | `20` |
| `OPENADMET_TARGET` | string | Short target name. | `VDR` |
| `OPENADMET_TARGET_ID` | string | UniProt accession. | `P11473` |
| `OPENADMET_ENDPOINT` | string | Always `IC50` in this deposition. | `IC50` |
| `OPENADMET_UNITS` | string | Units of the `standard_value_*` columns. | `nM` |
| `OPENADMET_SOURCE` | string | Originating database. | `BindingDB` |
| `OPENADMET_SOURCE_VERSION` | string | Retrieval date. | `20261008` |
