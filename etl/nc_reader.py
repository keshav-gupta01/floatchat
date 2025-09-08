from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd
import xarray as xr


@dataclass
class ParsedNetCDF:
    floats: pd.DataFrame
    profiles: pd.DataFrame
    variables: pd.DataFrame
    measurements: pd.DataFrame
    files: pd.DataFrame


def _safe_attr(ds: xr.Dataset, key: str) -> Optional[str]:
    return ds.attrs.get(key)


def _to_datetime64(time_values: np.ndarray, units: Optional[str]) -> np.ndarray:
    if units is None:
        return pd.to_datetime(time_values, utc=True, errors="coerce").values
    try:
        # xarray can decode CF times if decode_times=True, but we keep a fallback
        return xr.coding.times.decode_cf_datetime(time_values, units).values
    except Exception:
        return pd.to_datetime(time_values, utc=True, errors="coerce").values


def parse_argo_netcdf(file_path: Path) -> ParsedNetCDF:
    ds = xr.open_dataset(file_path, mask_and_scale=True, decode_times=False)

    # Identify dims
    n_prof = int(ds.dims.get("N_PROF", ds.dims.get("n_prof", 1)))
    n_levels = int(ds.dims.get("N_LEVELS", ds.dims.get("n_levels", ds.dims.get("N_LEVEL", 0))))

    # Common variables
    lat = ds.get("LATITUDE")
    lon = ds.get("LONGITUDE")
    time = ds.get("JULD") or ds.get("TIME")
    cycle = ds.get("CYCLE_NUMBER")
    position_qc = ds.get("POSITION_QC")

    time_units = time.attrs.get("units") if time is not None else None
    time_vals = _to_datetime64(time.values, time_units) if time is not None else np.array([np.datetime64("NaT")] * n_prof)

    # Float identifiers
    wmo_id = _safe_attr(ds, "PLATFORM_NUMBER") or (ds.get("PLATFORM_NUMBER").values if ds.get("PLATFORM_NUMBER") is not None else None)
    if isinstance(wmo_id, np.ndarray):
        try:
            wmo_id = "".join([chr(c) for c in wmo_id.flatten() if int(c) != 0]).strip()
        except Exception:
            wmo_id = str(wmo_id.tolist())

    floats_df = pd.DataFrame(
        [
            {
                "wmo_id": str(wmo_id) if wmo_id is not None else None,
                "platform_type": _safe_attr(ds, "PLATFORM_TYPE"),
                "dac": _safe_attr(ds, "DAC"),
                "maker": _safe_attr(ds, "MANUFACTURER"),
                "launch_date": _safe_attr(ds, "LAUNCH_DATE"),
            }
        ]
    )

    profiles_df = pd.DataFrame(
        {
            "wmo_id": [str(wmo_id)] * n_prof,
            "cycle_number": cycle.values.astype(int) if cycle is not None else np.arange(n_prof, dtype=int),
            "time": time_vals,
            "latitude": lat.values.astype(float) if lat is not None else np.full(n_prof, np.nan),
            "longitude": lon.values.astype(float) if lon is not None else np.full(n_prof, np.nan),
            "position_qc": [None] * n_prof if position_qc is None else pd.array(position_qc.values).astype("string").tolist(),
        }
    )

    # Build variables dictionary from data variables that are 2D (N_PROF x N_LEVELS)
    var_rows = []
    measurement_rows: list[dict] = []
    for var_name, da in ds.data_vars.items():
        if da.ndim != 2:
            continue
        dims = list(da.dims)
        if not ("N_PROF" in dims or "n_prof" in dims) or not ("N_LEVELS" in dims or "n_levels" in dims or "N_LEVEL" in dims):
            continue

        var_rows.append(
            {
                "name": var_name,
                "standard_name": da.attrs.get("standard_name"),
                "long_name": da.attrs.get("long_name"),
                "units": da.attrs.get("units"),
            }
        )

        # Find related QC and adjusted variables if present
        qc_var = ds.get(f"{var_name}_QC")
        adj_var = ds.get(f"{var_name}_ADJUSTED")
        adj_qc_var = ds.get(f"{var_name}_ADJUSTED_QC")
        pres = ds.get("PRES") or ds.get("PRES_ADJUSTED")

        data = da.values
        qc = qc_var.values if qc_var is not None else None
        adj = adj_var.values if adj_var is not None else None
        adj_qc = adj_qc_var.values if adj_qc_var is not None else None
        pres_vals = pres.values if pres is not None else None

        # Iterate profiles and levels
        for iprof in range(min(n_prof, data.shape[0])):
            for ilev in range(min(n_levels, data.shape[1]) if n_levels else data.shape[1]):
                value = data[iprof, ilev]
                if np.isnan(value):
                    continue
                row = {
                    "wmo_id": str(wmo_id),
                    "cycle_number": int(profiles_df.loc[iprof, "cycle_number"]),
                    "variable_name": var_name,
                    "level_index": ilev,
                    "pressure_dbar": None if pres_vals is None or np.isnan(pres_vals[iprof, ilev]) else float(pres_vals[iprof, ilev]),
                    "value": float(value),
                    "value_qc": None if qc is None else (str(qc[iprof, ilev]) if not pd.isna(qc[iprof, ilev]) else None),
                    "adjusted_value": None if adj is None or np.isnan(adj[iprof, ilev]) else float(adj[iprof, ilev]),
                    "adjusted_qc": None if adj_qc is None else (str(adj_qc[iprof, ilev]) if not pd.isna(adj_qc[iprof, ilev]) else None),
                }
                measurement_rows.append(row)

    variables_df = pd.DataFrame(var_rows).drop_duplicates(subset=["name"]) if var_rows else pd.DataFrame(columns=["name","standard_name","long_name","units"]) 
    measurements_df = pd.DataFrame(measurement_rows) if measurement_rows else pd.DataFrame(columns=[
        "wmo_id","cycle_number","variable_name","level_index","pressure_dbar","value","value_qc","adjusted_value","adjusted_qc"
    ])

    files_df = pd.DataFrame([
        {"path": str(file_path), "md5": None, "version": ds.attrs.get("history")}
    ])

    ds.close()

    return ParsedNetCDF(
        floats=floats_df,
        profiles=profiles_df,
        variables=variables_df,
        measurements=measurements_df,
        files=files_df,
    )


