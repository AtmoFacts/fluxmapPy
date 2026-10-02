"""Spatial statistics for one geofenced or whole FluxMap."""

import numpy as np

from .modl_geof import GeofencedRaster, PolygonStatistics

# Making mask of defined area if vector is given
def _filled_statistic(values: np.ma.MaskedArray) -> np.ndarray:
    """Convert a masked statistic to floats, using NaN when empty."""
    return np.asarray(np.ma.asarray(values).filled(np.nan), dtype=float)

#Calculating suite of statistics
def calculate_region_statistics(
    region: GeofencedRaster,
    product: str = "half-hourly",
) -> PolygonStatistics:
    """Calculate spatial statistics for one masked or whole raster.

    Reduces a region's pixels to summary values, either per half-hourly
    band or collapsed to a single daily layer first.

    Parameters
    ----------
    region : GeofencedRaster
        Raster already masked to a polygon, or kept whole.
    product : {"half-hourly", "daily"}, default "half-hourly"
        Temporal resolution. ``"half-hourly"`` returns one value per
        band; ``"daily"`` averages the bands first and returns scalars.

    Returns
    -------
    PolygonStatistics
        Holding ``count``, ``mean``, ``minimum``, ``maximum`` and
        ``standard_deviation``. These are 48-element arrays for
        ``"half-hourly"`` and Python scalars for ``"daily"``.

    Raises
    ------
    ValueError
        If ``product`` is neither ``"half-hourly"`` nor ``"daily"``.

    Notes
    -----
    ``standard_deviation`` is computed across the spatial axes, so it
    describes variation between pixels within the region at each
    timestep.

    Examples
    --------
    A 2x2 region with two half-hourly bands:

    >>> region = _example_region()
    >>> stats = calculate_region_statistics(region, product="half-hourly")
    >>> stats.mean
    array([2.5, 6.5])
    >>> stats.minimum
    array([1., 5.])
    >>> stats.count
    array([4, 4])

    Collapsing the bands to one daily layer instead:

    >>> daily = calculate_region_statistics(region, product="daily")
    >>> float(daily.mean)
    4.5
    >>> daily.product
    'daily'
    """
    if product in {"half-hourly", "half_hourly"}:
        values = region.masked_bands
        product_name = "half-hourly"
    elif product == "daily":
        values = region.daily_mean[np.newaxis, ...]
        product_name = "daily"
    else:
        raise ValueError("product must be 'half-hourly' or 'daily'")

    axes = (-2, -1)
    count = np.asarray(np.ma.count(values, axis=axes), dtype=int)
    mean = _filled_statistic(np.ma.mean(values, axis=axes))
    minimum = _filled_statistic(np.ma.min(values, axis=axes))
    maximum = _filled_statistic(np.ma.max(values, axis=axes))
    standard_deviation = _filled_statistic(np.ma.std(values, axis=axes))

    if product_name == "daily":
        count_output: np.ndarray | int = int(count[0])
        mean_output: np.ndarray | float = float(mean[0])
        minimum_output: np.ndarray | float = float(minimum[0])
        maximum_output: np.ndarray | float = float(maximum[0])
        deviation_output: np.ndarray | float = float(standard_deviation[0])
    else:
        count_output = count
        mean_output = mean
        minimum_output = minimum
        maximum_output = maximum
        deviation_output = standard_deviation

    return PolygonStatistics(
        feature_id=region.feature_id,
        properties=region.properties.copy(),
        site=region.source.record.site,
        flux_type=region.source.record.flux_type,
        date=region.source.record.date,
        product=product_name,
        count=count_output,
        mean=mean_output,
        minimum=minimum_output,
        maximum=maximum_output,
        standard_deviation=deviation_output,
    )


def _example_region() -> GeofencedRaster:
    """Build a small geofenced raster for the docstring examples."""
    from types import SimpleNamespace

    return GeofencedRaster(
        source=SimpleNamespace(
            record=SimpleNamespace(
                site="KONA",
                flux_type="fluxCo2",
                date="20260101",
            )
        ),
        feature_id=0,
        properties={},
        masked_bands=np.ma.array(
            np.array(
                [[[1.0, 2.0], [3.0, 4.0]], [[5.0, 6.0], [7.0, 8.0]]],
                dtype="float32",
            )
        ),
        polygon_pixel_count=4,
        vector_path=None,
    )
