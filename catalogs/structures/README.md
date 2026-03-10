# Structures

Protein structure files for ADMET-relevant targets, downloaded from [RCSB PDB](https://www.rcsb.org/) and processed for use in computational workflows.

## Targets

| Target | UniProt ID |
|--------|-----------|
| AHR | P35869 |
| CYP1A2 | P05177 |
| CYP2C9 | P11712 |
| CYP2D6 | P10635 |
| CYP3A4 | P08684 |
| PXR | O75469 |

## Directory Structure

```
structures/
├── notebooks/          # Notebooks to download and process structures
├── mmCIF/              # mmCIF structure files (preferred format)
│   └── <TARGET>/
│       ├── raw_cif/    # Raw files downloaded from RCSB
│       └── cleaned/    # Processed files ({ID}_cleaned.cif)
└── PDB/                # PDB structure files
    └── <TARGET>/
        ├── raw_pdb/    # Raw/initial files downloaded from RCSB ({id}_initial.pdb)
        └── modified/   # Processed files ({id}.pdb)
```

## Notebooks

### `download_rcsb_files.ipynb`
Downloads raw structure files from RCSB PDB using the [openadmet-toolkit](https://github.com/OpenADMET/openadmet-toolkit) library.

1. Set your target (e.g., `target = "CYP3A4"`)
2. Query PDB IDs by UniProt ID via the RCSB search API
3. Download mmCIF files (default) or PDB files for all IDs

For PDB downloads, the notebook falls back to mmCIF-to-PDB conversion via `gemmi` when a PDB file is not available from RCSB. This is common for newer structures, as the PDB format is deprecated.

### `process_structures.ipynb`
Processes raw downloaded structure files using [openadmet-toolkit](https://github.com/OpenADMET/openadmet-toolkit).

- Filters to the relevant protein chain (identified by UniProt ID)
- Removes common co-crystallization artifacts (solvents, ions, detergents)
- Retains ligands and cofactors (e.g., HEM/HEC for CYPs)
- Saves cleaned output files

> **Note:** Always visually inspect processed structures. Some edge cases require manual cleanup. For example, CYP3A4 6DAJ has a floating GLN group that must be removed by hand after automated processing.

### `legacy_download_process_pdb.ipynb`
Earlier notebook with manual implementations of download and processing functions. Superseded by `download_rcsb_files.ipynb` and `process_structures.ipynb`, which use the openadmet-toolkit library. Retained for reference.

## File Counts

| Target | mmCIF (raw / cleaned) | PDB (raw / modified) |
|--------|-----------------------|----------------------|
| AHR | 3 / 3 | 3 / 3 |
| CYP1A2 | 1 / 1 | 1 / 1 |
| CYP2C9 | 15 / 15 | 15 / 15 |
| CYP2D6 | 14 / 14 | 14 / 14 |
| CYP3A4 | 122 / 122 | 121 / 121 |
| PXR | 80 / 80 | 74 / 74 |

> CYP3A4 and PXR PDB counts are lower than mmCIF because some structures are only available as mmCIF and were converted to PDB via gemmi.
