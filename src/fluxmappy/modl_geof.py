"""Dataclasses and protocols describing geofenced FluxMap results."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np


class RasterRecordLike(Protocol):
    """Raster record fields required by spatial analysis."""

    site: str
    flux_type: str
    date: str
    path: Path


class FilteredFluxRasterLike(Protocol):
    """Filtered raster interface required by spatial analysis."""

    record: RasterRecordLike
    filtered_bands: np.ma.MaskedArray
    profile: dict


@dataclass(frozen=True)
class VectorFeature:
    """One polygon or multipolygon and its identifying attributes."""

    feature_id: object
    properties: dict[str, object]
    geometry: dict


@dataclass(frozen=True)
class VectorLayer:
    """Vector CRS and its separately identifiable polygon features."""

    path: Path
    crs: object
    features: tuple[VectorFeature, ...]
    id_field: str | None


@dataclass(frozen=True)
class PolygonStatistics:
    """Spatial statistics for one polygon and one raster product."""

    feature_id: object
    properties: dict[str, object]
    site: str
    flux_type: str
    date: str
    product: str
    count: np.ndarray | int
    mean: np.ndarray | float
    minimum: np.ndarray | float
    maximum: np.ndarray | float
    standard_deviation: np.ndarray | float


@dataclass(frozen=True)
class PolygonDiurnalCycle:
    """Mean and cumulative cycles for one region/site/flux group."""

    feature_id: object
    properties: dict[str, object]
    site: str
    flux_type: str
    dates: tuple[str, ...]
    daily_cycles: np.ndarray
    mean_cycle: np.ndarray
    standard_deviation: np.ndarray
    valid_day_count: np.ndarray
    cumulative_cycle: np.ndarray
    timestep_seconds: float | None
    timezone: str = "UTC"


@dataclass
class GeofencedRaster:
    """One filtered raster masked to a vector polygon or kept whole."""

    source: FilteredFluxRasterLike
    feature_id: object
    properties: dict[str, object]
    masked_bands: np.ma.MaskedArray
    polygon_pixel_count: int
    vector_path: Path | None

    @property
    def daily_mean(self) -> np.ma.MaskedArray:
        """Return the per-pixel mean across available half-hourly bands."""
        return np.ma.mean(self.masked_bands, axis=0).astype("float32")

    def statistics(self, product: str = "half-hourly") -> PolygonStatistics:
        """Calculate spatial statistics through the focused calculator."""
        from .def_stat_calc import calculate_region_statistics

        return calculate_region_statistics(self, product=product)
