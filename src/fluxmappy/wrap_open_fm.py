"Opens a band from a FluxMap to allow for raster visualization"

from pathlib import Path

import numpy as np
import rasterio

from .def_filt_grid_vali import assert_same_grid
from .def_filt_qf_mask import quality_pass_mask
from .def_filt_rast_name import parse_raster_path
from .modl_filt import OpenedFluxMap
from .def_open_qf_path import resolve_quality_path


def wrap_open_fm(
    raster_path: str | Path,
    band: int,
    *,
    qf_thsh: float = 4,
    qf_keep: str = "lte",
    qf_path: str | Path | None = None,
) -> OpenedFluxMap:
    """Open one band of a FluxMap with low-quality pixels masked out.

    Reads a single band from a measurement raster, applies the matching
    quality-flag raster, and returns the masked band together with its
    spatial metadata, ready for plotting.

    Parameters
    ----------
    raster_path : str or pathlib.Path
        Measurement FluxMap raster to open.
    band : int
        Which band to read, **1-based**: band 1 is midnight, band 48 the
        final half-hour of the day.
    qf_thsh : float, default 4
        Quality-flag threshold. Flags run 0-5, where 0 carries the least
        uncertainty.
    qf_keep : {"lte", "gte"}, default "lte"
        Which side of the threshold to keep. ``"lte"`` keeps pixels at or
        below ``qf_thsh``; ``"gte"`` keeps those at or above it.
    qf_path : str or pathlib.Path, optional
        Quality-flag raster. When ``None`` (default) it is located
        alongside ``raster_path`` by naming convention.

    Returns
    -------
    OpenedFluxMap
        With ``data`` (the masked 2-D band), ``band``, ``description``,
        ``profile``, ``tags``, ``record`` and ``quality_path``, plus the
        ``qf_threshold`` and ``qf_keep`` that were applied.

    Raises
    ------
    ValueError
        If ``band`` is not a positive 1-based integer, if it exceeds the
        band count of the raster, or if the measurement and quality
        rasters do not share the same grid.

    See Also
    --------
    wrap_filt_qf : Filter a whole directory of FluxMaps at once.

    Examples
    --------
    Bands are numbered from 1, so band 0 is rejected before any file is
    read:

    >>> wrap_open_fm("KONA/fluxCo2_20260101.tif", band=0)
    Traceback (most recent call last):
        ...
    ValueError: band must be a positive 1-based integer

    Opening a real FluxMap requires the raster on disk, so this is shown
    rather than executed:

    >>> fluxmap = wrap_open_fm(
    ...     "KONA/fluxCo2_20260101.tif", band=20, qf_thsh=1
    ... )  # doctest: +SKIP
    >>> fluxmap.data.shape  # doctest: +SKIP
    (64, 64)
    """
    if isinstance(band, bool) or not isinstance(band, int) or band < 1:
        raise ValueError("band must be a positive 1-based integer")

    measurement_path, resolved_quality_path = resolve_quality_path(
        raster_path,
        qf_path,
    )
    record = parse_raster_path(measurement_path)
    assert record is not None

    with rasterio.open(measurement_path) as measurement_src:
        if band > measurement_src.count:
            raise ValueError(
                f"Band {band} does not exist in {measurement_path}; "
                f"available bands are 1-{measurement_src.count}"
            )

        measurement_data = np.ma.masked_invalid(
            measurement_src.read(band, masked=True).astype("float32")
        )
        profile = measurement_src.profile.copy()
        profile.update(count=1)
        description = measurement_src.descriptions[band - 1]
        tags = measurement_src.tags(band).copy()

        with rasterio.open(resolved_quality_path) as quality_src:
            assert_same_grid(
                measurement_path=measurement_path,
                measurement_profile=measurement_src.profile,
                quality_path=resolved_quality_path,
                quality_profile=quality_src.profile,
            )
            if quality_src.count == 1:
                quality_band = 1
            elif quality_src.count == measurement_src.count:
                quality_band = band
            else:
                raise ValueError(
                    "Quality raster band count must be 1 or match the "
                    "measurement raster band count."
                )

            quality_data = quality_src.read(quality_band, masked=True)
            passes = quality_pass_mask(
                quality_data=quality_data[np.newaxis, ...],
                measurement_shape=(1, *measurement_data.shape),
                qf_threshold=qf_thsh,
                qf_keep=qf_keep,
            )[0]

    return OpenedFluxMap(
        record=record,
        quality_path=resolved_quality_path,
        band=band,
        data=np.ma.masked_where(~passes, measurement_data),
        profile=profile,
        description=description,
        tags=tags,
        qf_threshold=qf_thsh,
        qf_keep=qf_keep,
    )
