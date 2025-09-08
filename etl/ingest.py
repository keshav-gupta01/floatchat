from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd

from .config import get_config
from .models import create_all, get_session
from .nc_reader import parse_argo_netcdf
from .loader import (
    upsert_float,
    upsert_file,
    sync_variables,
    upsert_profiles,
    insert_measurements,
)


def discover_files(root: Path, patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for pattern in patterns:
        files.extend(root.rglob(pattern))
    return sorted(set(files))


def main() -> None:
    cfg = get_config()
    create_all(cfg.database_url)

    parser = argparse.ArgumentParser(description="Ingest Argo NetCDF into SQL")
    parser.add_argument("--input", type=str, default=cfg.input_dir, help="Input directory with NetCDF files")
    args = parser.parse_args()

    root = Path(args.input).resolve()
    patterns = [p.strip() for p in cfg.include_patterns.split(",") if p.strip()]
    files = discover_files(root, patterns)
    if not files:
        print("No NetCDF files found.")
        return

    with get_session(cfg.database_url) as session:
        total_profiles = 0
        total_measurements = 0
        for fp in files:
            try:
                parsed = parse_argo_netcdf(fp)
                float_row = parsed.floats.iloc[0].to_dict()
                float_obj = upsert_float(session, float_row)
                file_obj = upsert_file(session, parsed.files.iloc[0].to_dict())

                name_to_var_id = sync_variables(session, parsed.variables)
                profiles_df = parsed.profiles
                profiles_df = profiles_df.assign(wmo_id=float_obj.wmo_id)
                cycle_to_profile_id = upsert_profiles(session, float_obj.id, file_obj.id, profiles_df)

                inserted = insert_measurements(session, parsed.measurements, cycle_to_profile_id, name_to_var_id)
                total_measurements += inserted
                total_profiles += len(cycle_to_profile_id)
                session.commit()
                print(f"Ingested {fp.name}: profiles={len(cycle_to_profile_id)} measurements={inserted}")
            except Exception as exc:
                session.rollback()
                print(f"Failed {fp}: {exc}")

        print(f"Done. Total profiles={total_profiles} measurements={total_measurements}")


if __name__ == "__main__":
    main()


