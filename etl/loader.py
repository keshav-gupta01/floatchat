from __future__ import annotations

from typing import Dict

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import FloatPlatform, Profile, Variable, Measurement, SourceFile


def upsert_float(session: Session, float_row: dict) -> FloatPlatform:
    existing = session.execute(
        select(FloatPlatform).where(FloatPlatform.wmo_id == float_row.get("wmo_id"))
    ).scalar_one_or_none()
    if existing:
        # Update some mutable fields
        existing.platform_type = float_row.get("platform_type") or existing.platform_type
        existing.dac = float_row.get("dac") or existing.dac
        existing.maker = float_row.get("maker") or existing.maker
        session.flush()
        return existing
    fp = FloatPlatform(**float_row)
    session.add(fp)
    session.flush()
    return fp


def upsert_file(session: Session, file_row: dict) -> SourceFile:
    existing = session.execute(
        select(SourceFile).where(SourceFile.path == file_row.get("path"))
    ).scalar_one_or_none()
    if existing:
        existing.md5 = file_row.get("md5") or existing.md5
        existing.version = file_row.get("version") or existing.version
        session.flush()
        return existing
    f = SourceFile(**file_row)
    session.add(f)
    session.flush()
    return f


def sync_variables(session: Session, variables_df: pd.DataFrame) -> Dict[str, int]:
    name_to_id: Dict[str, int] = {}
    for _, row in variables_df.iterrows():
        name = row["name"]
        existing = session.execute(select(Variable).where(Variable.name == name)).scalar_one_or_none()
        if existing:
            # update metadata
            existing.standard_name = row.get("standard_name") or existing.standard_name
            existing.long_name = row.get("long_name") or existing.long_name
            existing.units = row.get("units") or existing.units
            session.flush()
            name_to_id[name] = existing.id
        else:
            v = Variable(
                name=name,
                standard_name=row.get("standard_name"),
                long_name=row.get("long_name"),
                units=row.get("units"),
            )
            session.add(v)
            session.flush()
            name_to_id[name] = v.id
    return name_to_id


def upsert_profiles(session: Session, float_id: int, file_id: int, profiles_df: pd.DataFrame) -> Dict[int, int]:
    cycle_to_profile_id: Dict[int, int] = {}
    for _, row in profiles_df.iterrows():
        cycle_number = int(row["cycle_number"]) if pd.notna(row["cycle_number"]) else None
        existing = session.execute(
            select(Profile).where(Profile.float_id == float_id, Profile.cycle_number == cycle_number)
        ).scalar_one_or_none()
        if existing:
            existing.time = row.get("time")
            existing.latitude = row.get("latitude")
            existing.longitude = row.get("longitude")
            existing.position_qc = row.get("position_qc")
            existing.file_id = file_id or existing.file_id
            session.flush()
            cycle_to_profile_id[cycle_number] = existing.id
        else:
            p = Profile(
                float_id=float_id,
                cycle_number=cycle_number,
                time=row.get("time"),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
                position_qc=row.get("position_qc"),
                file_id=file_id,
            )
            session.add(p)
            session.flush()
            cycle_to_profile_id[cycle_number] = p.id
    return cycle_to_profile_id


def insert_measurements(session: Session, measurements_df: pd.DataFrame, cycle_to_profile_id: Dict[int, int], name_to_var_id: Dict[str, int]) -> int:
    inserted = 0
    if measurements_df.empty:
        return inserted
    rows: list[Measurement] = []
    for _, row in measurements_df.iterrows():
        cycle = int(row["cycle_number"]) if pd.notna(row["cycle_number"]) else None
        profile_id = cycle_to_profile_id.get(cycle)
        variable_id = name_to_var_id.get(row["variable_name"]) if pd.notna(row["variable_name"]) else None
        if profile_id is None or variable_id is None:
            continue
        m = Measurement(
            profile_id=profile_id,
            variable_id=variable_id,
            level_index=int(row["level_index"]) if pd.notna(row["level_index"]) else 0,
            pressure_dbar=row.get("pressure_dbar"),
            value=row.get("value"),
            value_qc=row.get("value_qc"),
            adjusted_value=row.get("adjusted_value"),
            adjusted_qc=row.get("adjusted_qc"),
        )
        rows.append(m)
        if len(rows) >= 5000:
            session.bulk_save_objects(rows)
            session.flush()
            inserted += len(rows)
            rows = []
    if rows:
        session.bulk_save_objects(rows)
        session.flush()
        inserted += len(rows)
    return inserted


