# OpenADMET Data Catalogs
[![Logo](https://img.shields.io/badge/OSMF-OpenADMET-%23002f4a)](https://openadmet.org/)


As part of our open-science mission, OpenADMET aims to curate and disseminate ADMET (Absorption, Distribution, Metabolism, Excretion, and Toxicity) data used to train our models for general use.

## Overview
An easy and convenient way of sharing and accessing these datasets (largely borrowed from the geosciences) is via `Intake` catalogs. `Intake` is a lightweight, user-friendly data access tool that simplifies data discovery, loading, and sharing.
See here for more information: https://intake.readthedocs.io/en/latest/index.html

This repository hosts `Intake` catalogs for various ADMET datasets curated by OpenADMET as well as the curation steps as implemented in `openadmet_toolkit`: https://github.com/OpenADMET/openadmet_toolkit

## NOTE:

This repo is under very active development, we make no guarantees about the stability or correctness of any catalogs contained herein. 

## Use directly!

You can use the data contained here directly by downloading it or cloning the repo

## Usage of Catalogs

1. To use the `Intake` catalogs, install the required dependencies:

```bash
pip install intake
```

2. Open a Python session or Jupyter session and load a catalog. Here we are loading a catalog of [pChEMBL](https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/chembl-data-questions#what-is-pchembl) curated from [ChEMBL](https://www.ebi.ac.uk/chembl/) for a set of targets with functionality available in `openadmet_toolkit`: 

   ```python
   import intake
   catalog = intake.open_catalog("https://github.com/OpenADMET/data-catalogs/blob/main/catalogs/activities/ChEMBL_pChEMBL_permissive/CATALOG_ChEMBL35_permissive.yaml")
   # also available on S3 
   ```
3. List available datasets:
   ```python
   catalog
   ```
4. Load a specific dataset, here for the Pregnane X receptor (PXR, CHEMBL3401)
   ```python
   print(catalog.entries) 
   >>> ...
   df = catalog["PXR_aggregated"].read()
   ```


## License
This repository is distributed under an open license to promote accessibility and collaboration. Please refer to the LICENSE file for more details.

## Contact
For questions, suggestions, or collaborations, please reach out via the OpenADMET organization or submit an issue in this repository.

