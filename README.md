# OpenADMET Data Catalogs

As part of our open-science mission, OpenADMET aims to curate and disseminate ADMET (Absorption, Distribution, Metabolism, Excretion, and Toxicity) data used to train our models for general use.

## Overview
An easy and convenient way of sharing and accessing these datasets (largely borrowed from the geosciences) is via `Intake` catalogs. `Intake` is a lightweight, user-friendly data access tool that simplifies data discovery, loading, and sharing.
See here for more information: https://intake.readthedocs.io/en/latest/index.html

This repository hosts `Intake` catalogs for various ADMET datasets curated by OpenADMET as well as the curation steps as implemented in `openadmet_toolkit`: https://github.com/OpenADMET/openadmet_toolkit

## NOTE:

This repo is under very active development, we make no guarantees about the stability or correctness of any catalogs contained herein. 

## Installation
To use the `Intake` catalogs, install the required dependencies:

```bash
pip install intake
```

## Usage


2. Open a Python session or Jupyter session and load a catalog:

   ```python
   import intake
   catalog = intake.open_catalog("https://github.com/OpenADMET/data-catalogs/blob/main/catalogs/activities/ChEMBL_pChEMBL_permissive/CATALOG_ChEMBL35_permissive.yaml")
   # also available on S3 
   ```

3. List available datasets:

   ```python
   catalog
   ```

4. Load a specific dataset:

   ```python
   print(catalog.entries) 
   >>> ...
   df = catalog["PXR_aggregated"].read()
   ```


## License
This repository is distributed under an open license to promote accessibility and collaboration. Please refer to the LICENSE file for more details.

## Contact
For questions, suggestions, or collaborations, please reach out via the OpenADMET organization or submit an issue in this repository.

