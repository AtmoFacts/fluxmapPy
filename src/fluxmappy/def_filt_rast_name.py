"""Parsing of site, flux type and date out of FluxMap filenames."""

from pathlib import Path
import re

from .modl_filt import RasterRecord


TIF_NAME_PATTERN = re.compile(
    r"(?:^|_)(?P<site>[^_]+)_(?P<flux_type>[^_]+)_"
    r"(?P<date>\d{8})(?P<quality>_(?:qa|qf))?\.tiff?$",
    re.IGNORECASE,
)


def parse_raster_path(path: Path) -> RasterRecord | None:
    """Parse site, flux type, date and quality suffix from a filename.

    Parameters
    ----------
    path : pathlib.Path
        Raster path whose filename follows
        ``<site>_<flux_type>_<YYYYMMDD>[_qf].tif``.

    Returns
    -------
    RasterRecord or None
        The parsed record, or ``None`` if the filename does not match the
        expected pattern.

    Examples
    --------
    >>> from pathlib import Path
    >>> record = parse_raster_path(Path("KONA_fluxCo2_20260101.tif"))
    >>> record.site, record.flux_type, record.date
    ('KONA', 'fluxCo2', '20260101')
    >>> record.is_quality
    False

    A ``_qf`` suffix marks the quality-flag raster of the same day:

    >>> parse_raster_path(Path("KONA_fluxCo2_20260101_qf.tif")).is_quality
    True

    Names that do not match return ``None`` rather than raising:

    >>> parse_raster_path(Path("notes.txt")) is None
    True
    """
    match = TIF_NAME_PATTERN.search(path.name)
    if match is None:
        return None

    return RasterRecord(
        site=match.group("site"),
        flux_type=match.group("flux_type"),
        date=match.group("date"),
        is_quality=match.group("quality") is not None,
        path=path,
    )
