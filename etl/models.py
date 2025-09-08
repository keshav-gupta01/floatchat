from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    create_engine,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


metadata_obj = MetaData()


class Base(DeclarativeBase):
    metadata = metadata_obj


class FloatPlatform(Base):
    __tablename__ = "floats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wmo_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    platform_type: Mapped[Optional[str]] = mapped_column(String(64))
    dac: Mapped[Optional[str]] = mapped_column(String(64))
    maker: Mapped[Optional[str]] = mapped_column(String(128))
    launch_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)

    profiles: Mapped[list[Profile]] = relationship(back_populates="float_platform", cascade="all, delete-orphan")


class SourceFile(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(Text)
    md5: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    version: Mapped[Optional[str]] = mapped_column(String(64))


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    float_id: Mapped[int] = mapped_column(ForeignKey("floats.id", ondelete="CASCADE"), index=True)
    cycle_number: Mapped[int] = mapped_column(Integer)

    time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    position_qc: Mapped[Optional[str]] = mapped_column(String(8))

    file_id: Mapped[Optional[int]] = mapped_column(ForeignKey("files.id", ondelete="SET NULL"))

    __table_args__ = (
        UniqueConstraint("float_id", "cycle_number", name="uq_profile_float_cycle"),
    )

    float_platform: Mapped[FloatPlatform] = relationship(back_populates="profiles")
    measurements: Mapped[list[Measurement]] = relationship(back_populates="profile", cascade="all, delete-orphan")


class Variable(Base):
    __tablename__ = "variables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    standard_name: Mapped[Optional[str]] = mapped_column(String(128))
    long_name: Mapped[Optional[str]] = mapped_column(String(256))
    units: Mapped[Optional[str]] = mapped_column(String(64))


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"), index=True)
    variable_id: Mapped[int] = mapped_column(ForeignKey("variables.id", ondelete="CASCADE"), index=True)

    level_index: Mapped[int] = mapped_column(Integer)  # 0..N_LEVELS-1
    pressure_dbar: Mapped[Optional[float]] = mapped_column(Float)
    value: Mapped[Optional[float]] = mapped_column(Float)
    value_qc: Mapped[Optional[str]] = mapped_column(String(8))
    adjusted_value: Mapped[Optional[float]] = mapped_column(Float)
    adjusted_qc: Mapped[Optional[str]] = mapped_column(String(8))

    profile: Mapped[Profile] = relationship(back_populates="measurements")


def create_all(database_url: str) -> None:
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)


def get_session(database_url: str) -> Session:
    engine = create_engine(database_url)
    return Session(engine)


