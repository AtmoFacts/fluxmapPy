"""Quality filtering of one measurement and quality raster pair."""

import numpy as np
import rasterio

from .modl_filt import FilteredFluxRaster, RasterPair
from .def_filt_grid_vali import assert_same_grid
from .def_filt_qf_mask import quality_pass_mask

# Expects 48 bands of FluxMaps
EXPECTED_BANDS_PER_DAY = 48

#Will identify qf and measurement rasters across a day and pairs them
def filter_raster_pair(
    pair: RasterPair,
    qf_threshold: float = 1,
    qf_keep: str = "lte",
) -> FilteredFluxRaster:
    """Read and quality-filter one raster pair entirely in memory.

    Opens both rasters, checks they share a grid, and masks every
    measurement pixel whose quality flag fails the rule. Nothing is
    written to disk.

    Parameters
    ----------
    pair : RasterPair
        Measurement and quality rasters for a single day.
    qf_threshold : float, default 1
        Quality-flag threshold, on the 0-5 FluxMap scale.
    qf_keep : {"lte", "gte"}, default "lte"
        Which side of the threshold to keep.

    Returns
    -------
    FilteredFluxRaster
        Carrying the masked bands, the originating ``record``, the
        ``profile`` and the quality settings applied.

    Raises
    ------
    ValueError
        If the measurement and quality rasters do not share a grid, or if
        the quality band count is neither 1 nor equal to the measurement
        band count.

    Notes
    -----
    A measurement raster that does not hold 48 bands prints a warning to
    stdout and is filtered anyway.

    Examples
    --------
    Requires rasters on disk, so this is shown rather than executed:

    >>> filtered = filter_raster_pair(pair, qf_threshold=1)  # doctest: +SKIP
    >>> filtered.filtered_bands.shape  # doctest: +SKIP
    (48, 64, 64)
    """
    with rasterio.open(pair.measurement.path) as measurement_src:
        if measurement_src.count != EXPECTED_BANDS_PER_DAY:
            print(
                f"Warning: {pair.measurement.path} has "
                f"{measurement_src.count} bands; "
                f"expected {EXPECTED_BANDS_PER_DAY}."
            )

        measurement_data = np.ma.masked_invalid(
            measurement_src.read(masked=True).astype("float32")
        )
        profile = measurement_src.profile.copy()
        band_descriptions = tuple(measurement_src.descriptions)
        tags = measurement_src.tags().copy()

        with rasterio.open(pair.quality_path) as quality_src:
            assert_same_grid(
                measurement_path=pair.measurement.path,
                measurement_profile=measurement_src.profile,
                quality_path=pair.quality_path,
                quality_profile=quality_src.profile,
            )
            passes = quality_pass_mask(
                quality_data=quality_src.read(masked=True),
                measurement_shape=measurement_data.shape,
                qf_threshold=qf_threshold,
                qf_keep=qf_keep,
            )

    return FilteredFluxRaster(
        record=pair.measurement,
        quality_path=pair.quality_path,
        filtered_bands=np.ma.masked_where(~passes, measurement_data),
        profile=profile,
        band_descriptions=band_descriptions,
        tags=tags,
        qf_threshold=qf_threshold,
        qf_keep=qf_keep,
    )
