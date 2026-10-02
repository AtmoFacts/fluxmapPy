"""Mean and cumulative diurnal-cycle analysis for quality-filtered FluxMaps."""

from collections.abc import Iterable
from pathlib import Path

import numpy as np

from .modl_geof import FilteredFluxRasterLike, PolygonDiurnalCycle
from .def_diu_calc import summarize_daily_cycles
from .def_diu_coll import collect_dated_cycles
from .def_diu_lt import localize_daily_cycles
from .def_diu_tz_vali import resolve_timezone


def wrap_diu(
    filtered_rasters: Iterable[FilteredFluxRasterLike],
    vector: str | Path | None = None,
    id_field: str | None = None,
    all_touched: bool = False,
    timestep_seconds: float | None = None,
    in_tz: str = "UTC",
    out_tz: str | None = None,
    incomplete_local_days: str = "drop",
) -> list[PolygonDiurnalCycle]:
    """Return mean and cumulative diurnal cycles for polygons or rasters.

    Groups quality-filtered rasters by region, site and flux type,
    converts each day's 48 half-hourly spatial means into the requested
    timezone, and averages them into one diurnal cycle per region.

    Parameters
    ----------
    filtered_rasters : iterable of FilteredFluxRaster
        Quality-filtered rasters, typically the output of
        :func:`~fluxmappy.wrap_filt_qf`. Each supplies 48 half-hourly
        bands for one day, with band 1 at midnight in ``in_tz``.
    vector : str or pathlib.Path, optional
        Polygon vector file to summarise within. When ``None`` (default)
        each raster is summarised as a whole.
    id_field : str, optional
        Vector attribute identifying each polygon. When ``None`` the
        feature index is used.
    all_touched : bool, default False
        Include every pixel touched by a polygon, not only those whose
        centre falls inside it.
    timestep_seconds : float, optional
        Seconds represented by each slot, used to scale the cumulative
        cycle. ``None`` leaves the cumulative sum unscaled. Half-hourly
        FluxMaps use ``1800``.
    in_tz : str, default "UTC"
        Timezone in which band 1 of each source raster is midnight.
    out_tz : str, optional
        Timezone to convert into before daily cycles are averaged.
        ``None`` keeps the cycles in ``in_tz``.
    incomplete_local_days : {"drop", "include", "error"}, default "drop"
        How to treat local days left partially covered once ``out_tz`` has
        shifted the source days. ``"drop"`` discards them, ``"include"``
        keeps them, ``"error"`` raises.

    Returns
    -------
    list of PolygonDiurnalCycle
        One entry per ``(feature_id, site, flux_type)`` group. Each holds
        ``mean_cycle``, ``standard_deviation``, ``valid_day_count`` and
        ``cumulative_cycle`` as 48-element arrays, alongside the
        contributing ``dates`` and the resulting ``timezone``.

    Raises
    ------
    ValueError
        If ``incomplete_local_days`` is not one of the three accepted
        values, if a timezone name cannot be resolved, or if no statistics
        were available to aggregate.

    See Also
    --------
    wrap_filt_qf : Produce the filtered rasters this function consumes.
    wrap_stat : Spatial statistics for the same rasters.

    Notes
    -----
    ``standard_deviation`` measures variability *across days* at each
    half-hour slot, not variability across pixels. For spatial spread
    within a region, use :func:`~fluxmappy.wrap_stat`.

    Examples
    --------
    Two days of synthetic single-pixel rasters, summarised whole:

    >>> import numpy as np
    >>> rasters = [_example_raster(d) for d in ("20260101", "20260102")]
    >>> cycles = wrap_diu(rasters)
    >>> len(cycles)
    1
    >>> cycle = cycles[0]
    >>> cycle.timezone
    'UTC'
    >>> cycle.dates
    ('20260101', '20260102')
    >>> cycle.mean_cycle[:4]
    array([0., 1., 2., 3.])
    >>> cycle.valid_day_count[:4]
    array([2, 2, 2, 2])

    Scaling the cumulative cycle by the half-hourly timestep:

    >>> cycles = wrap_diu(rasters, timestep_seconds=1800.0)
    >>> cycles[0].cumulative_cycle[:4]
    array([    0.,  1800.,  5400., 10800.])

    Converting to a local timezone before averaging:

    >>> dates = ("20260101", "20260102", "20260103")
    >>> cycles = wrap_diu(
    ...     [_example_raster(d) for d in dates],
    ...     out_tz="America/Chicago",
    ... )
    >>> cycles[0].timezone
    'America/Chicago'
    """
    if incomplete_local_days not in {"drop", "include", "error"}:
        raise ValueError(
            "incomplete_local_days must be 'drop', 'include', or 'error'"
        )

    source_timezone = resolve_timezone(in_tz, "in_tz")
    target_timezone = (
        None
        if out_tz is None
        else resolve_timezone(out_tz, "out_tz")
    )
    result_timezone = out_tz or in_tz
    resolved_path = None if vector is None else Path(vector)
    grouped = collect_dated_cycles(
        filtered_rasters,
        resolved_path,
        id_field,
        all_touched,
    )

    results: list[PolygonDiurnalCycle] = []
    for (feature_id, site, flux_type), group in grouped.items():
        dated_cycles = group["dated_cycles"]
        assert isinstance(dated_cycles, list)
        dated_cycles.sort(key=lambda item: item[0])

        if target_timezone is None:
            dates = tuple(date for date, _ in dated_cycles)
            daily_cycles = np.vstack(
                [values for _, values in dated_cycles]
            ).astype(float)
        else:
            dates, daily_cycles = localize_daily_cycles(
                dated_cycles,
                source_timezone,
                target_timezone,
                incomplete_local_days,
            )

        (
            mean_cycle,
            standard_deviation,
            valid_day_count,
            cumulative_cycle,
        ) = summarize_daily_cycles(daily_cycles, timestep_seconds)
        properties = group["properties"]
        assert isinstance(properties, dict)
        results.append(
            PolygonDiurnalCycle(
                feature_id=feature_id,
                properties=properties.copy(),
                site=site,
                flux_type=flux_type,
                dates=dates,
                daily_cycles=daily_cycles,
                mean_cycle=mean_cycle,
                standard_deviation=standard_deviation,
                valid_day_count=valid_day_count,
                cumulative_cycle=cumulative_cycle,
                timestep_seconds=timestep_seconds,
                timezone=result_timezone,
            )
        )
    return results

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
