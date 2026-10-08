# BindingDB Ki activity data

[BindingDB](https://www.bindingdb.org/) binding-affinity data restricted to
`affinity_type == 'Ki'` records. Mirrors `ChEMBL_pChEMBL_Ki` in scope and schema
philosophy, from a different source.

## Deposition: BindingDB20261008_Ki (LXR_alpha only)

- **Source / version / retrieval date**: BindingDB, retrieved 2026-10-08 via the public
  REST API (`https://bindingdb.org/rest/getLigandsByUniprots`). BindingDB's REST API has
  no discrete numbered release the way ChEMBL does, so the retrieval date (`20261008`) is
  used as the deposition's version token.
- **Targets**: liver X receptor alpha (LXR_alpha, UniProt `Q13133`) only, mirroring the
  target scope already chosen for `ChEMBL_pChEMBL_Ki`. **Caveat**: that scoping decision
  was made against ChEMBL's Ki counts (CAR=1, FXR=0, VDR=16, LXR_alpha=341), which are
  genuinely sparse for the first three. BindingDB's own Ki counts are different --
  CAR=1, FXR=2, but **VDR=187**, which is not sparse. This deposition was built mirroring
  the existing ChEMBL_pChEMBL_Ki notebook's target list rather than re-deriving scope
  per-source, so a BindingDB-specific VDR Ki deposition (187 records) is being left out
  for now. Revisit if VDR Ki data is needed.
- **Selection criteria**: `getLigandsByUniprots` for `Q13133` with `cutoff=10000000`
  (nM, effectively unrestricted), then filtered client-side to `affinity_type == 'Ki'`
  -- the BindingDB API has no server-side type filter. No BAO/confidence-score
  equivalent filtering; BindingDB's ligand-search endpoint doesn't expose one. Records
  lacking a parseable canonical SMILES are dropped before aggregation.
- **Aggregation rule**: raw records are canonicalized (RDKit canonical SMILES via
  `openadmet.toolkit.chemoinformatics.rdkit_funcs.canonical_smiles`, salts removed) and
  grouped by (`OPENADMET_CANONICAL_SMILES`, `OPENADMET_INCHIKEY`). For each group, `mean`,
  `median`, and `std` of `standard_value` are reported, plus `n_records`.
  `standard_relation` is **not** consulted in aggregation; censored (`>`, `<`) and exact
  (`=`) measurements are mixed together in the mean/median (this deposition has 323 exact
  and 75 `>`-censored records; consult the raw file's `standard_relation` column before
  trusting an aggregate for a compound with many censored records). Unlike the ChEMBL
  depositions, there is no `pchembl_value` equivalent here -- BindingDB's API returns only
  the raw affinity value and type, not a normalized potency.
- **Units**: all `standard_value*` columns are in nM. BindingDB's API response does not
  carry an explicit units field; nM is BindingDB's documented convention for this
  endpoint and was confirmed by comparing overlapping compound/target pairs against their
  ChEMBL nM values, not asserted from the API response itself.
- **Manual intervention**: none beyond the target-list restriction above.
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
`ChEMBL_pChEMBL_Ki`. No deduplication across sources has been performed; anyone merging
the two should dedupe on `OPENADMET_INCHIKEY` + `OPENADMET_TARGET` and decide how to
handle cases where both sources report the same literature value.

## Schema

### `*_raw.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `bindingdb_target_name_queried` | string | Target name as returned by BindingDB for the queried UniProt ID. | `Oxysterols receptor LXR-alpha` |
| `bindingdb_monomer_id` | string | BindingDB's internal ligand (monomer) ID. | `20176` |
| `canonical_smiles` | string | SMILES as reported by BindingDB (source, not RDKit-canonicalized). | `CC(C)CC[C@H](O)[C@@H](C)[C@H]1CC[C@H]2[C@@H]3CC=C4...` |
| `standard_type` | string | Always `Ki` in this deposition (client-side filter). | `Ki` |
| `affinity` | string | Raw affinity string from BindingDB, including any leading censoring operator; source of `standard_relation`/`standard_value`. | `250` |
| `doc_pubmed_id` | string | PubMed ID, if known. | `12893846` |
| `doc_doi` | string | Publication DOI, if known. | `10.1124/jpet.103.052852` |
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES (salts removed); the deduplication key. | `CC(C)CC[C@H](O)[C@@H](C)[C@H]1CC[C@H]2[C@@H]3CC=C4C[C@@H](O)CC[C@]4(C)[C@H]3CC[C@]12C` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `RZPAXNJLEKLXNO-QUOSNDFLSA-N` |
| `standard_relation` | string | Censoring operator parsed from `affinity` (`=`, `>`, `<`, `>=`, `<=`); defaults to `=` when `affinity` has no operator. | `=` |
| `standard_value` | float64 | Numeric Ki parsed from `affinity`, in nM. | `250.0` |
| `OPENADMET_TARGET` | string | Short target name used in this catalog. | `LXR_alpha` |
| `OPENADMET_TARGET_ID` | string | UniProt accession queried. | `Q13133` |
| `OPENADMET_ENDPOINT` | string | Always `Ki` in this deposition. | `Ki` |
| `OPENADMET_UNITS` | string | Units of `standard_value`. | `nM` |
| `OPENADMET_SOURCE` | string | Originating database. | `BindingDB` |
| `OPENADMET_SOURCE_VERSION` | string | Retrieval date, `YYYYMMDD` (BindingDB has no release number). | `20261008` |

### `*_aggregated.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES; the deduplication key. | `CC1(O)CCC(C(=O)N2CCN(C3=CC=CC(S(C)(=O)=O)=C3)C[C@@H]2C2=CC=CC=C2)CC1` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `PICJKSLPJSZRIV-JKJRPBHFSA-N` |
| `standard_value_mean` | float64 | Mean Ki (nM) across the compound's records. | `2013.666667` |
| `standard_value_median` | float64 | Median Ki (nM). | `1270.0` |
| `standard_value_std` | float64 | Std. dev. of Ki (nM); null when `n_records == 1` (expected, not missing). | `2235.289765` |
| `n_records` | int64 | Number of raw activity rows behind this compound. | `3` |
| `OPENADMET_TARGET` | string | Short target name. | `LXR_alpha` |
| `OPENADMET_TARGET_ID` | string | UniProt accession. | `Q13133` |
| `OPENADMET_ENDPOINT` | string | Always `Ki` in this deposition. | `Ki` |
| `OPENADMET_UNITS` | string | Units of the `standard_value_*` columns. | `nM` |
| `OPENADMET_SOURCE` | string | Originating database. | `BindingDB` |
| `OPENADMET_SOURCE_VERSION` | string | Retrieval date. | `20261008` |
