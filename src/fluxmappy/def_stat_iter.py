"""Streaming of spatial statistics one region at a time."""

from collections.abc import Iterable, Iterator
from pathlib import Path

from .modl_geof import FilteredFluxRasterLike, PolygonStatistics
from .def_stat_mask import iter_geofenced_rasters
from .def_stat_calc import calculate_region_statistics


def iter_polygon_statistics(
    filtered_rasters: Iterable[FilteredFluxRasterLike],
    vector: Path | None = None,
    product: str = "half-hourly",
    id_field: str | None = None,
    all_touched: bool = False,
) -> Iterator[PolygonStatistics]:
    """Yield spatial statistics one region at a time.

    The streaming form behind :func:`~fluxmappy.wrap_stat`, which collects
    the results into a list. Unlike ``wrap_stat``, ``vector`` must already
    be a :class:`~pathlib.Path`.

    Parameters
    ----------
    filtered_rasters : iterable of FilteredFluxRaster
        Quality-filtered rasters, typically the output of
        :func:`~fluxmappy.wrap_filt_qf`.
    vector : pathlib.Path, optional
        Polygon vector file to summarise within. When ``None`` (default)
        each raster is summarised as a whole.
    product : {"half-hourly", "daily"}, default "half-hourly"
        Temporal resolution of the statistics. ``"half-hourly"`` returns
        one value per band; ``"daily"`` first averages the bands into a
        single daily layer.
    id_field : str, optional
        Vector attribute identifying each polygon. When ``None`` the
        feature index is used.
    all_touched : bool, default False
        Include every pixel touched by a polygon, not only those whose
        centre falls inside it.

    Yields
    ------
    PolygonStatistics
        One entry per raster and region.

    See Also
    --------
    wrap_stat : Collect the same statistics into a list.

    Examples
    --------
    >>> from fluxmappy.wrap_stat import _example_raster
    >>> rasters = [_example_raster(d) for d in ("20260101", "20260102")]
    >>> stats = list(iter_polygon_statistics(rasters, product="daily"))
    >>> len(stats)
    2
    >>> float(stats[0].mean)
    23.5
    """
    for region in iter_geofenced_rasters(
        filtered_rasters=filtered_rasters,
        vector_path=vector,
        id_field=id_field,
        all_touched=all_touched,
    ):
        yield calculate_region_statistics(region, product=product)
