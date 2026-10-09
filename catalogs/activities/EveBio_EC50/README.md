# EveBio EC50 activity data

[EveBio](https://evebio.org/) nuclear-receptor TR-FRET assay data, agonist-mode records
only. EveBio screens a fixed library of mostly-FDA-approved drugs against dozens of
targets, reporting both a binary active/inactive call and, for a subset, a fitted potency
(`pXC50`). This collection is EveBio's analog of `ChEMBL_pChEMBL_EC50` and
`BindingDB_EC50`.

**Spelling note**: the company stylizes its name "EvE Bio" (logo/footer: "EvE Bio, LLC";
Hugging Face org: `eve-bio`). This collection uses "EveBio" (one token, no space)
throughout -- directory names, `OPENADMET_SOURCE`, catalog prefixes -- since the
`<SOURCE>_<ENDPOINT>` directory convention used across this repo doesn't accommodate a
space in `<SOURCE>`, and a single consistent token is required so
`OPENADMET_SOURCE == 'EveBio'` matches across every future EveBio deposition.

**Why "EC50" when EveBio calls this "Agonist" mode**: EveBio's own schema doesn't label
the measurement as EC50 or IC50, only assay `mode` (Agonist/Antagonist). Mechanistically
they're the same thing: an agonist-mode TR-FRET recruitment assay titrates a compound and
fits the concentration at which the recruitment signal reaches half its maximum increase
-- the textbook definition of EC50. (The antagonist-mode counterpart, where a compound is
titrated against a fixed reference agonist and inhibits that signal, is `EveBio_IC50`.)
`mode == 'Agonist'` is still the underlying filter applied to the EveBio source data; see
the curation notebook's `MODE` parameter.

**License note**: unlike ChEMBL (CC BY-SA) and BindingDB (CC BY) already in this repo,
EveBio's data is **CC BY-NC-SA 4.0 (non-commercial)**. Check that license is acceptable
for your use before relying on this collection.

## Deposition: EveBio20261008_EC50 (CAR, FXR, VDR, LXR_alpha)

- **Source / version / retrieval date**: EveBio, retrieved 2026-10-08 from the gated
  `eve-bio/drug-target-activity` dataset on Hugging Face (`train.parquet`). EveBio's own
  `release` column varies per target/assay batch within the file (not a single
  whole-dataset version), so the retrieval date (`20261008`) is used as this
  deposition's version token, same convention as `BindingDB20261008_*`. Access requires
  an HF account that has accepted EveBio's gated-dataset terms and a bearer token; the
  curation notebook reads it from the `HF_TOKEN` environment variable and never writes it
  to notebook source or output.
- **Targets**: constitutive androstane receptor (CAR, gene `NR1I3`, UniProt `Q14994`),
  farnesoid X receptor (FXR, gene `NR1H4`, UniProt `Q96RI1`), vitamin D receptor (VDR,
  gene `VDR`, UniProt `P11473`), liver X receptor alpha (LXR_alpha, gene `NR1H3`, UniProt
  `Q13133`). LXR beta was excluded, matching the ChEMBL/BindingDB depositions for these
  targets.
- **Selection criteria**: rows where `target__gene` matches the gene symbol above (see
  caveat below on why gene, not UniProt) and `mode == 'Agonist'`. CAR and VDR each have
  one assay mechanism (`Co-Activator`, cofactor-recruitment TR-FRET); FXR and LXR_alpha
  additionally have a `Heterodimer` mechanism (RXR-heterodimerization TR-FRET), so they
  carry roughly twice the raw row count. No further filtering: every compound in EveBio's
  library gets a row per assay per target, whether or not it was judged active.
- **Aggregation rule**: raw records are canonicalized (RDKit canonical SMILES via
  `openadmet.toolkit.chemoinformatics.rdkit_funcs.canonical_smiles`) and grouped by
  (`OPENADMET_CANONICAL_SMILES`, `OPENADMET_INCHIKEY`), **after first dropping rows with
  no fitted `outcome_potency_pxc50`** -- EveBio's equivalent of requiring a pChEMBL value.
  Most raw rows are qualitative active/inactive-only calls with no potency fit; those stay
  in the raw file but are excluded from the aggregate. For each remaining group, `mean`,
  `median`, and `std` of `pxc50` are reported, plus `n_records`. Rows from different assay
  mechanisms (`Co-Activator` vs. `Heterodimer`) are pooled together in one aggregate per
  compound, the same way the ChEMBL/BindingDB permissive collections pool across assay
  formats; `assay__mechanism` is preserved per row in the raw file so this can be undone
  if mechanism-level separation is needed.
- **Units**: `pxc50_mean`/`pxc50_median`/`pxc50_std` (and raw `outcome_potency_pxc50`) are
  unitless, −log10 of EC50 in molar. EveBio does not report EC50 in molar/nM directly,
  only the fitted pXC50 value.
- **Manual intervention**: dropped `viability_assay_id` and `assay__detailed_mechanism`
  from the raw schema (both structurally all-null across every row in this deposition:
  `viability_assay_id` is EveBio's counterscreen-viability linkage, not applicable to
  these NR assays; `assay__detailed_mechanism` is unpopulated for every NR
  `assay__mechanism` value present here). `pxc50_std` is null for every row in the CAR,
  VDR, and LXR_alpha aggregated files specifically -- not because it was dropped, but
  because every compound in those files has `n_records == 1` (no repeat measurement to
  compute a spread over), which the deposition guidelines treat as expected, not missing.
- **No document provenance (`doc_id`/`doc_doi`/`doc_pubmed_id`/`doc_year`)**: EveBio is
  the generator's own primary screening data, not a literature-curated database like
  ChEMBL or BindingDB, so there is no publication to cite per measurement. `assay_id` and
  `release` are the closest available provenance (which EveBio assay batch and release
  produced the row).
- **Known data-quality issues in the source, not introduced here**:
  - `target__uniprot_id` is wrong for `Heterodimer`-mechanism rows: it's overwritten with
    the heterodimer partner's accession (`RXRA`) instead of the queried target's own
    UniProt ID. Matching was done on `target__gene` instead, which stays correct.
    `OPENADMET_TARGET_ID` is set from our own known-good UniProt mapping (table above),
    not copied from this source column.
  - `target__chembl_target_id` and `target__pubchem_target_id` are similarly unreliable
    on `Heterodimer` rows (e.g. `target__chembl_target_id` holding a UniProt accession;
    `target__pubchem_target_id` holding a comma-joined mix of UniProt/ChEMBL/PubChem IDs
    for the heterodimer pair). Both are kept as-is in the raw file for transparency but
    should not be trusted for `Heterodimer`-mechanism rows.
- **License / attribution**: CC BY-NC-SA 4.0. Attribute as: EveBio
  (https://evebio.org/), retrieved 2026-10-08. Non-commercial use only.

## Schema

### `*_raw.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `assay_id` | string | EveBio assay ID. | `P00451` |
| `target_id` | string | EveBio target/complex ID (reflects the heterodimer pair name on `Heterodimer` rows). | `LXRa-RXRa` |
| `compound_id` | string | EveBio compound ID. | `EB000273` |
| `mode` | string | Always `Agonist` in this deposition (the source-side filter this collection corresponds to). | `Agonist` |
| `assay__mechanism` | string | Assay mechanism: `Co-Activator`, `Co-Repressor`, or `Heterodimer`. | `Heterodimer` |
| `assay__technology` | string | Assay detection technology. | `TR-FRET` |
| `outcome_is_active` | bool | EveBio's binary active/inactive call. | `true` |
| `outcome_potency_pxc50` | float64 | Fitted potency, −log10(EC50, M); null for qualitative-only rows. | `7.4` |
| `outcome_max_activity` | float64 | Fitted maximum response from the concentration-response curve. | `33.7` |
| `observed_max` | float64 | Observed (not fitted) maximum response. | `36.0` |
| `is_quantified` | bool | Whether this row has a fitted potency (mirrors `outcome_potency_pxc50` non-null). | `true` |
| `frequency_flag` | string | EveBio frequent-hitter flag. | `False` |
| `viability_flag` | bool | Whether cytotoxicity/viability concerns were flagged for this compound. | `false` |
| `pxc50_modifier` | string | Censoring operator on the potency fit, if any. | `=` |
| `slope` | float64 | Hill slope of the fitted curve. | `1.4` |
| `asymp_min` | float64 | Fitted curve lower asymptote. | `1.8` |
| `asymp_max` | float64 | Fitted curve upper asymptote. | `33.7` |
| `target__class` | string | EveBio target class. | `NR` |
| `target__gene` | string | Gene symbol; the identifier this deposition matches targets on. | `NR1H3` |
| `target__uniprot_id` | string | UniProt accession as reported by EveBio; unreliable on `Heterodimer` rows (see caveat above). | `RXRA` |
| `target__chembl_target_id` | string | ChEMBL target ID as reported by EveBio; unreliable on `Heterodimer` rows (see caveat above). | `Q13133` |
| `target__pubchem_target_id` | string | PubChem target identifier(s) as reported by EveBio; unreliable on `Heterodimer` rows (see caveat above). | `P19793,CHEMBL2808,10062` |
| `target__is_mutant` | bool | Whether the target construct is a mutant. | `false` |
| `target__wildtype_id` | string | Wild-type target ID, if this is a mutant. | `LXRa-RXRa` |
| `target__name` | string | Full target name. | `Liver X receptor-α-Retinoid X receptor-α heterodimer` |
| `compound__name` | string | Compound name. | `Calcifediol` |
| `compound__smiles` | string | SMILES as reported by EveBio (source, not RDKit-canonicalized). | `[H][C@@]1(CC[C@@]2(...)[H])...` |
| `compound__drugbank_id` | string | DrugBank ID, if known. | `DB00146` |
| `compound__cas` | string | CAS number, if known. | `19356-17-3` |
| `compound__unii` | string | FDA UNII code, if known. | `T0WXW8F54E` |
| `compound_inchikey_source` | string | InChIKey as reported by EveBio (source, not recomputed). | `JWUBBDSIWDLEOM-DTOXIADCSA-N` |
| `progressed` | bool | Whether this compound progressed to further EveBio screening. | `true` |
| `release` | string | EveBio's own per-batch release tag (varies by target/assay, not by whole dataset). | `11` |
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES; the deduplication key. | `C=C1CC[C@H](O)C/C1=C/C=C1\CCC[C@]2(C)...` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `JWUBBDSIWDLEOM-DTOXIADCSA-N` |
| `OPENADMET_TARGET` | string | Short target name used in this catalog. | `LXR_alpha` |
| `OPENADMET_TARGET_ID` | string | UniProt accession, from this repo's known-good mapping (not copied from `target__uniprot_id`). | `Q13133` |
| `OPENADMET_ENDPOINT` | string | Always `EC50` in this deposition. | `EC50` |
| `OPENADMET_UNITS` | string | Units of `outcome_potency_pxc50`. | `pXC50 (unitless, -log10 of unspecified XC50 in M)` |
| `OPENADMET_SOURCE` | string | Originating database. | `EveBio` |
| `OPENADMET_SOURCE_VERSION` | string | Retrieval date, `YYYYMMDD` (EveBio has no single dataset-wide release number). | `20261008` |

### `*_aggregated.parquet`

| Column | Type | Description | Example |
|---|---|---|---|
| `OPENADMET_CANONICAL_SMILES` | string | RDKit-canonical SMILES; the deduplication key. | `OC[C@H]1OC(S)[C@H](O)[C@@H](O)[C@@H]1O` |
| `OPENADMET_INCHIKEY` | string | InChIKey derived from `OPENADMET_CANONICAL_SMILES`. | `JUSMHIGDXPKSID-GASJEMHNSA-N` |
| `pxc50_mean` | float64 | Mean pXC50 (EC50 scale) across the compound's quantified records. | `5.2` |
| `pxc50_median` | float64 | Median pXC50. | `5.2` |
| `pxc50_std` | float64 | Std. dev. of pXC50; null when `n_records == 1` (expected, not missing). | `0.141421` |
| `n_records` | int64 | Number of quantified raw rows behind this compound. | `2` |
| `OPENADMET_TARGET` | string | Short target name. | `LXR_alpha` |
| `OPENADMET_TARGET_ID` | string | UniProt accession. | `Q13133` |
| `OPENADMET_ENDPOINT` | string | Always `EC50` in this deposition. | `EC50` |
| `OPENADMET_UNITS` | string | Units of the `pxc50_*` columns. | `pXC50 (unitless, -log10 of unspecified XC50 in M)` |
| `OPENADMET_SOURCE` | string | Originating database. | `EveBio` |
| `OPENADMET_SOURCE_VERSION` | string | Retrieval date. | `20261008` |
