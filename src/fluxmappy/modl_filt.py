"""Dataclasses describing raster records and quality-filtered FluxMaps."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class RasterRecord:
    """Information parsed from one measurement or quality raster."""

    site: str
    flux_type: str
    date: str
    is_quality: bool
    path: Path


@dataclass(frozen=True)
class RasterPair:
    """One measurement raster and its matching quality raster."""

    measurement: RasterRecord
    quality_path: Path


@dataclass
class FilteredFluxRaster:
    """An in-memory QA-filtered raster ready for downstream analysis."""

    record: RasterRecord
    quality_path: Path
    filtered_bands: np.ma.MaskedArray
    profile: dict
    band_descriptions: tuple[str | None, ...]
    tags: dict[str, str]
    qf_threshold: float
    qf_keep: str

    @property
    def crs(self):
        return self.profile.get("crs")

    @property
    def transform(self):
        return self.profile.get("transform")

    @property
    def shape(self) -> tuple[int, int, int]:
        return self.filtered_bands.shape


@dataclass
class OpenedFluxMap:
    """One quality-filtered band opened from a flux-map raster."""

    record: RasterRecord
    quality_path: Path
    band: int
    data: np.ma.MaskedArray
    profile: dict
    description: str | None
    tags: dict[str, str]
    qf_threshold: float
    qf_keep: str

    @property
    def shape(self) -> tuple[int, int]:
        return self.data.shape
