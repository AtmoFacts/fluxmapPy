"""Spatial statistics for whole FluxMaps or polygons within them."""

from collections.abc import Iterable
from pathlib import Path

import numpy as np

from .modl_geof import FilteredFluxRasterLike, PolygonStatistics
from .def_stat_iter import iter_polygon_statistics


def wrap_stat(
    filtered_rasters: Iterable[FilteredFluxRasterLike],
    vector: str | Path | None = None,
    product: str = "half-hourly",
    id_field: str | None = None,
    all_touched: bool = False,
) -> list[PolygonStatistics]:
    """Return spatial statistics for whole FluxMaps or polygons within them.

    Reads quality-filtered FluxMaps and computes pixel statistics across
    each raster, or within each polygon of a vector file when one is
    supplied.

    Parameters
    ----------
    filtered_rasters : iterable of FilteredFluxRaster
        Quality-filtered rasters, typically the output of
        :func:`~fluxmappy.wrap_filt_qf`.
    vector : str or pathlib.Path, optional
        Polygon vector file to summarise within. When ``None`` (default)
        each raster is summarised as a whole.
    product : {"half-hourly", "daily"}, default "half-hourly"
        Temporal resolution of the statistics. ``"half-hourly"`` returns
        48-element arrays, one value per band. ``"daily"`` averages the
        bands into a single daily layer first and returns scalars.
    id_field : str, optional
        Vector attribute identifying each polygon. When ``None`` the
        feature index is used.
    all_touched : bool, default False
        Include every pixel touched by a polygon, not only those whose
        centre falls inside it.

    Returns
    -------
    list of PolygonStatistics
        One entry per raster and region, each holding ``count``, ``mean``,
        ``minimum``, ``maximum`` and ``standard_deviation`` alongside the
        identifying ``feature_id``, ``site``, ``flux_type`` and ``date``.

    Raises
    ------
    ValueError
        If ``product`` is neither ``"half-hourly"`` nor ``"daily"``, or if
        a raster lacks the spatial metadata needed to apply a vector.

    See Also
    --------
    wrap_filt_qf : Produce the filtered rasters this function consumes.
    wrap_diu : Diurnal cycles from the same rasters.

    Notes
    -----
    ``standard_deviation`` here is *spatial* — the spread across pixels
    within the region at each timestep. This differs from the field of the
    same name on :class:`~fluxmappy.PolygonDiurnalCycle`, which measures
    variability across days.

    Examples
    --------
    Two days of synthetic single-pixel rasters, summarised whole:

    >>> rasters = [_example_raster(d) for d in ("20260101", "20260102")]
    >>> stats = wrap_stat(rasters)
    >>> len(stats)
    2
    >>> stats[0].product
    'half-hourly'
    >>> stats[0].mean[:4]
    array([0., 1., 2., 3.])

    Collapsing each day to a single value instead:

    >>> daily = wrap_stat(rasters, product="daily")
    >>> daily[0].product
    'daily'
    >>> float(daily[0].mean)
    23.5
    >>> int(daily[0].count)
    1
    """
    resolved_path = None if vector is None else Path(vector)
    return list(
        iter_polygon_statistics(
            filtered_rasters=filtered_rasters,
            vector=resolved_path,
            product=product,
            id_field=id_field,
            all_touched=all_touched,
        )
    )


def _example_raster(date: str) -> object:
    """Build a one-pixel filtered raster for the docstring examples."""
    from types import SimpleNamespace

    return SimpleNamespace(
        record=SimpleNamespace(
            site="KONA",
            flux_type="fluxCo2",
            date=date,
            path=Path(f"{date}.tif"),
        ),
        filtered_bands=np.ma.array(
            np.arange(48, dtype=np.float32)[:, None, None]
        ),
        profile={"height": 1, "width": 1},
    )
