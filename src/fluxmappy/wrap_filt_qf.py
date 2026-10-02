"Filtering a directory of FluxMaps using a pixel quality threshold"
from __future__ import annotations


from pathlib import Path
from typing import Iterator

from .modl_filt import (
    FilteredFluxRaster,
    RasterPair,
    RasterRecord,
)
from .def_filt_pair import filter_raster_pair
from .def_filt_grid_vali import assert_same_grid
from .def_filt_qf_mask import quality_pass_mask
from .def_filt_rast_name import TIF_NAME_PATTERN, parse_raster_path
from .def_filt_rast_pair import find_raster_pairs


DEFAULT_FLUX_TYPE = "fluxTempEngy"
DEFAULT_QF_THRESHOLD = 1
DEFAULT_QF_KEEP = "lte"


def wrap_filt_qf(
    data: str | Path,
    flux: str = DEFAULT_FLUX_TYPE,
    qf_thsh: float = DEFAULT_QF_THRESHOLD,
    qf_keep: str = DEFAULT_QF_KEEP,
    limit: int | None = None,
) -> Iterator[FilteredFluxRaster]:
    """Yield FluxMaps with low-quality pixels masked out.

    Scans ``data`` for measurement and quality-flag raster pairs, masks
    every pixel whose quality flag fails the threshold, and yields the
    results one day at a time without writing any files.

    Parameters
    ----------
    data : str or pathlib.Path
        Directory holding both the measurement rasters and their
        quality-flag rasters.
    flux : str, default "fluxTempEngy"
        Flux type to read. ``"fluxCo2"`` for carbon flux,
        ``"fluxTempEngy"`` for sensible heat, ``"fluxH2oEngy"`` for
        latent heat.
    qf_thsh : float, default 1
        Quality-flag threshold. Flags run 0-5, where 0 carries the least
        uncertainty.
    qf_keep : {"lte", "gte"}, default "lte"
        Which side of the threshold to keep. ``"lte"`` keeps pixels at or
        below ``qf_thsh``; ``"gte"`` keeps those at or above it.
    limit : int, optional
        Stop after this many raster pairs. ``None`` (default) processes
        every pair found.

    Yields
    ------
    FilteredFluxRaster
        One per measurement/quality pair, carrying the masked bands and
        the originating record.

    Raises
    ------
    ValueError
        If ``data`` holds no matching raster pairs, or if a measurement
        raster and its quality raster do not share the same grid.

    See Also
    --------
    wrap_diu : Diurnal cycles from these rasters.
    wrap_stat : Spatial statistics from these rasters.

    Examples
    --------
    The defaults are exposed as module constants:

    >>> DEFAULT_FLUX_TYPE
    'fluxTempEngy'
    >>> DEFAULT_QF_THRESHOLD
    1
    >>> DEFAULT_QF_KEEP
    'lte'

    Filtering a directory of FluxMaps requires raster files on disk, so
    the call below is shown rather than executed:

    >>> filtered = wrap_filt_qf(
    ...     "KONA", flux="fluxCo2", qf_thsh=1, qf_keep="lte"
    ... )  # doctest: +SKIP
    >>> cycles = wrap_diu(filtered, out_tz="America/Chicago")  # doctest: +SKIP
    """
    pairs = find_raster_pairs(data_dir=Path(data), flux_type=flux)
    if limit is not None:
        pairs = pairs[:limit]

    for pair in pairs:
        yield filter_raster_pair(
            pair=pair,
            qf_threshold=qf_thsh,
            qf_keep=qf_keep,
        )


__all__ = [
    "DEFAULT_FLUX_TYPE",
    "DEFAULT_QF_KEEP",
    "DEFAULT_QF_THRESHOLD",
    "FilteredFluxRaster",
    "RasterPair",
    "RasterRecord",
    "TIF_NAME_PATTERN",
    "assert_same_grid",
    "filter_raster_pair",
    "find_raster_pairs",
    "parse_raster_path",
    "quality_pass_mask",
    "wrap_filt_qf",
]

