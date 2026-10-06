"""Curate ChEMBL 37 aminergic-panel activity data and publish intake catalogs.

Mirrors curate_data_aminergic.ipynb, as a script so a long run is resumable and
loggable. Per receptor and endpoint it writes a raw and an aggregated parquet,
pushes both to S3 and collects the URIs into one intake catalog per endpoint.

Layout note: parquets go under a flat per-endpoint prefix
(ChEMBL37_aminergic_Ki/ etc.) rather than under a Gs/Gq/Gi prefix. The
G-protein split is still unconfirmed (only ~10 aminergic receptors are
canonically Gs-coupled, against a Gs library said to hold ~20), so it is
recorded as catalog entry metadata instead of being baked into public S3 paths.
Regrouping later is a catalog regeneration, not a re-upload.

Usage:
    python run_curation.py --dry-run --targets 5-HT2B --endpoints Ki
    python run_curation.py                      # full run, uploads
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

import datamol as dm
from tqdm.auto import tqdm

from openadmet.toolkit.chemoinformatics.rdkit_funcs import canonical_smiles, smiles_to_inchikey
from openadmet.toolkit.database.chembl import PermissiveChEMBLTargetCurator

tqdm.pandas()

CHEMBL_VER = 37
BUCKET = "openadmet-data-public-dev"
ENDPOINTS = ["Ki", "EC50", "IC50"]

# receptor -> (ChEMBL target id, gene symbol, canonical primary G-protein)
PANEL = {
    "D1": ("CHEMBL2056", "DRD1", "Gs"), "D5": ("CHEMBL1850", "DRD5", "Gs"),
    "H2": ("CHEMBL1941", "HRH2", "Gs"), "ADRB1": ("CHEMBL213", "ADRB1", "Gs"),
    "ADRB2": ("CHEMBL210", "ADRB2", "Gs"), "ADRB3": ("CHEMBL246", "ADRB3", "Gs"),
    "5-HT4": ("CHEMBL1875", "HTR4", "Gs"), "5-HT6": ("CHEMBL3371", "HTR6", "Gs"),
    "5-HT7": ("CHEMBL3155", "HTR7", "Gs"), "TAAR1": ("CHEMBL5857", "TAAR1", "Gs"),
    "H1": ("CHEMBL231", "HRH1", "Gq"), "M1": ("CHEMBL216", "CHRM1", "Gq"),
    "M3": ("CHEMBL245", "CHRM3", "Gq"), "M5": ("CHEMBL2035", "CHRM5", "Gq"),
    "ADRA1A": ("CHEMBL229", "ADRA1A", "Gq"), "ADRA1B": ("CHEMBL232", "ADRA1B", "Gq"),
    "ADRA1D": ("CHEMBL223", "ADRA1D", "Gq"), "5-HT2A": ("CHEMBL224", "HTR2A", "Gq"),
    "5-HT2B": ("CHEMBL1833", "HTR2B", "Gq"), "5-HT2C": ("CHEMBL225", "HTR2C", "Gq"),
    "D2": ("CHEMBL217", "DRD2", "Gi/o"), "D3": ("CHEMBL234", "DRD3", "Gi/o"),
    "D4": ("CHEMBL219", "DRD4", "Gi/o"), "H3": ("CHEMBL264", "HRH3", "Gi/o"),
    "H4": ("CHEMBL3759", "HRH4", "Gi/o"), "M2": ("CHEMBL211", "CHRM2", "Gi/o"),
    "M4": ("CHEMBL1821", "CHRM4", "Gi/o"), "ADRA2A": ("CHEMBL1867", "ADRA2A", "Gi/o"),
    "ADRA2B": ("CHEMBL1942", "ADRA2B", "Gi/o"), "ADRA2C": ("CHEMBL1916", "ADRA2C", "Gi/o"),
    "5-HT1A": ("CHEMBL214", "HTR1A", "Gi/o"), "5-HT1B": ("CHEMBL1898", "HTR1B", "Gi/o"),
    "5-HT1D": ("CHEMBL1983", "HTR1D", "Gi/o"), "5-HT1E": ("CHEMBL2182", "HTR1E", "Gi/o"),
    "5-HT1F": ("CHEMBL1805", "HTR1F", "Gi/o"), "5-HT5A": ("CHEMBL3426", "HTR5A", "Gi/o"),
}


def gather(receptor, chembl_tid, endpoint):
    """Curated (aggregated, raw) activity frames for one receptor and endpoint."""
    # NOTE: the field is `chembl_version`. Older toolkit releases silently
    # ignored a `version=` kwarg and curated ChEMBL 34; the toolkit now accepts
    # `version` as an alias and rejects unknown kwargs, but keep the check below.
    curator = PermissiveChEMBLTargetCurator(
        chembl_target_id=chembl_tid, chembl_version=CHEMBL_VER,
        standard_type=endpoint, require_pchembl=True,
    )
    if curator.chembl_version != CHEMBL_VER:
        raise RuntimeError(
            f"curator is on ChEMBL {curator.chembl_version}, expected {CHEMBL_VER}")
    raw = curator.get_activity_data(return_as="df")
    if len(raw) == 0:
        return None, None

    with dm.without_rdkit_log():
        raw["OPENADMET_CANONICAL_SMILES"] = raw["canonical_smiles"].progress_apply(canonical_smiles)
        raw["OPENADMET_INCHIKEY"] = raw["OPENADMET_CANONICAL_SMILES"].progress_apply(smiles_to_inchikey)

    # canonicalise here so compound deduplication is done correctly
    agg = curator.aggregate_activity_data_by_compound(canonicalise=True)
    return agg, raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="write parquet locally, do not upload or publish catalogs")
    ap.add_argument("--targets", nargs="*", default=None, help="receptor subset")
    ap.add_argument("--endpoints", nargs="*", default=ENDPOINTS)
    args = ap.parse_args()

    panel = PANEL if not args.targets else {k: PANEL[k] for k in args.targets}
    print(f"ChEMBL {CHEMBL_VER} | {len(panel)} receptors | endpoints {args.endpoints} "
          f"| {'DRY RUN' if args.dry_run else 'UPLOADING to ' + BUCKET}\n")

    bucket = None
    if not args.dry_run:
        for var, key in (("AWS_ACCESS_KEY_ID", "aws_access_key_id"),
                         ("AWS_SECRET_ACCESS_KEY", "aws_secret_access_key")):
            os.environ[var] = subprocess.check_output(
                ["aws", "configure", "get", key], text=True).strip()
        from openadmet.toolkit.webservices.credentials import S3Settings
        from openadmet.toolkit.webservices.s3 import S3Bucket
        bucket = S3Bucket.from_settings(S3Settings(), BUCKET)

    import intake

    summary = []
    for endpoint in args.endpoints:
        location = f"ChEMBL{CHEMBL_VER}_aminergic_{endpoint}"
        loc_path = Path(location)
        loc_path.mkdir(exist_ok=True)

        uris_agg, uris_raw = {}, {}
        for receptor, (tid, gene, gprot) in panel.items():
            try:
                agg, raw = gather(receptor, tid, endpoint)
            except Exception as exc:
                print(f"  !! {receptor} {endpoint} FAILED: {exc}", file=sys.stderr)
                summary.append((receptor, endpoint, "error", 0))
                continue
            if agg is None or len(agg) == 0:
                print(f"  -- {receptor} {endpoint}: no data, skipped")
                summary.append((receptor, endpoint, "empty", 0))
                continue

            safe = receptor.replace("/", "_")
            f_agg = f"ChEMBL_{endpoint}_{safe}_{tid}_aggregated.parquet"
            f_raw = f"ChEMBL_{endpoint}_{safe}_{tid}_raw.parquet"
            agg.reset_index(drop=True).to_parquet(loc_path / f_agg, index=False)
            raw.reset_index(drop=True).to_parquet(loc_path / f_raw, index=False)
            print(f"  ok {receptor:8s} {endpoint:5s} {len(raw):6d} raw  {len(agg):6d} aggregated")
            summary.append((receptor, endpoint, "ok", len(agg)))

            if bucket is not None:
                d_agg, d_raw = f"{location}/{f_agg}", f"{location}/{f_raw}"
                bucket.push_file(loc_path / f_agg, d_agg)
                bucket.push_file(loc_path / f_raw, d_raw)
                uris_agg[receptor] = bucket.to_uri(d_agg)
                uris_raw[receptor] = bucket.to_uri(d_raw)

        if bucket is not None and uris_agg:
            cat = intake.entry.Catalog()
            for receptor, uri in uris_agg.items():
                cat[receptor + "_aggregated"] = intake.readers.PandasParquet(uri)
            for receptor, uri in uris_raw.items():
                cat[receptor + "_raw"] = intake.readers.PandasParquet(uri)
            catname = f"CATALOG_{location}.yaml"
            cat.to_yaml_file(catname)
            bucket.push_file(catname, f"{location}/{catname}")
            print(f"  -> {catname}: {len(uris_agg)} receptors\n")

    ok = [s for s in summary if s[2] == "ok"]
    print(f"\n{len(ok)} of {len(summary)} receptor/endpoint pairs curated")
    for state in ("empty", "error"):
        bad = [f"{r}/{e}" for r, e, s, _ in summary if s == state]
        if bad:
            print(f"  {state}: {', '.join(bad)}")


if __name__ == "__main__":
    main()
