# Cleaned & Processed PubChem Data

Full description of data tables processed with `process_tox21.ipynb`

| Column Name              | Data Type | Description                             | Example           |
|--------------------------|-----------|-----------------------------------------|-------------------|
| INCHIKEY                 | string    | Unique identifier for compound, calculated via `CSVProcessing`.             | ADAKRBAJFHTIEW-UHFFFAOYSA-N|
| OPENADMET_CANONICAL_SMILES     | string     | compound's canonical SMILES string, calculated via `CSVProcessing`.     | O=C=NC1=CC=C(Cl)C=C1 |
| OPENADMET_LOGAC50| float     | Mean of pAC50 value of activity of both technical & biological replicates, calculated from "Potency (uM)". Order of operations: calculate pAC50, then average. | 5.297074 |
| OPENADMET_LOGAC50_STD| float     | Standard deviation of pAC50 value. | 1.187785	 |
| OPENADMET_ACTIVITY_COMMENT| string     | Record of specific type of activity value of pAC50, e.g. one of "IC50", "XC50", "EC50", "Ki", "Kd", "Potency", "ED50". Must be user determined by examining assay protocol. | EC50  |
| OPENADMET_ACTIVITY_OUTCOME| string     | Compound's activity outcome as determined from "PUBCHEM_ACTIVITY_OUTCOME", e.g. one of "active", "inactive", "inconclusive" | active              |
| OPENADMET_COUNTERSCREEN_VIABLE| bool     | True if there is something that likely compromises activity, e.g. cytotoxicity. From counter screen "Phenotype" column. | False  |
| fit_hillslope_mean| float     | Mean of slope of Hill equation (used for determining AC50) | 2.284967  |
| fit_hillslope_std| float     | Standard deviation of slope of Hill equation | 2.312771   |
| fit_r2_mean| float     | Mean of R^2 of Hill equation fit. | 0.905633  |
| fit_r2_std| float     | Standard deviation of R^2 of Hill equation fit. | 0.044800   |