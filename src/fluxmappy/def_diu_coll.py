"""Collection of half-hourly spatial means into region/date groups."""

from collections.abc import Iterable
from pathlib import Path

import numpy as np

from .modl_geof import FilteredFluxRasterLike
from .def_stat_iter import iter_polygon_statistics


CycleGroup = dict[str, object]
CycleGroups = dict[tuple[object, str, str], CycleGroup]


def collect_dated_cycles(
    filtered_rasters: Iterable[FilteredFluxRasterLike],
    vector_path: Path | None,
    id_field: str | None,
    all_touched: bool,
) -> CycleGroups:
    """Collect 48 spatial means for every region and source date.

    Runs the statistics pass over every raster and files each day's 48
    half-hourly means under its ``(feature_id, site, flux_type)`` group,
    ready for averaging into a diurnal cycle.

    Parameters
    ----------
    filtered_rasters : iterable of FilteredFluxRaster
        Quality-filtered rasters, one per day.
    vector_path : pathlib.Path or None
        Polygon vector file to summarise within, or ``None`` to
        summarise each raster whole.
    id_field : str or None
        Vector attribute identifying each polygon, or ``None`` to use the
        feature index.
    all_touched : bool
        Include every pixel touched by a polygon, not only those whose
        centre falls inside it.

    Returns
    -------
    dict
        Keyed by ``(feature_id, site, flux_type)``. Each value holds the
        feature ``properties`` and a ``dated_cycles`` list of
        ``(date, values)`` pairs.

    Raises
    ------
    ValueError
        If any raster does not yield exactly 48 half-hourly means, or if
        no statistics were available at all.

    Examples
    --------
    >>> rasters = [_example_raster(d) for d in ("20260101", "20260102")]
    >>> grouped = collect_dated_cycles(rasters, None, None, False)
    >>> list(grouped)
    [('whole_raster', 'KONA', 'fluxCo2')]
    >>> len(grouped[('whole_raster', 'KONA', 'fluxCo2')]["dated_cycles"])
    2
    """
    grouped: CycleGroups = {}
    for statistics in iter_polygon_statistics(
        filtered_rasters=filtered_rasters,
        vector=vector_path,
        product="half-hourly",
        id_field=id_field,
        all_touched=all_touched,
    ):
        mean_values = np.asarray(statistics.mean, dtype=float)
        if mean_values.shape != (48,):
            raise ValueError(
                f"Expected 48 half-hourly means for feature "
                f"{statistics.feature_id!r} on {statistics.date}; "
                f"received shape {mean_values.shape}"
            )

        key = (
            statistics.feature_id,
            statistics.site,
            statistics.flux_type,
        )
        group = grouped.setdefault(
            key,
            {
                "properties": statistics.properties.copy(),
                "dated_cycles": [],
            },
        )
        dated_cycles = group["dated_cycles"]
        assert isinstance(dated_cycles, list)
        dated_cycles.append((statistics.date, mean_values))

    if not grouped:
        raise ValueError("No polygon statistics were available to aggregate")
    return grouped


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
