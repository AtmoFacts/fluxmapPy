"""Timezone and date validation for diurnal-cycle conversion."""

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def resolve_timezone(name: str, parameter: str) -> ZoneInfo:
    """Return an IANA timezone, or raise a clear configuration error.

    Parameters
    ----------
    name : str
        IANA timezone name, such as ``"UTC"`` or ``"America/Chicago"``.
    parameter : str
        Name of the calling argument, used to make the error message
        point at the right place.

    Returns
    -------
    zoneinfo.ZoneInfo
        The resolved timezone.

    Raises
    ------
    ValueError
        If ``name`` is not a known IANA timezone.

    Examples
    --------
    >>> resolve_timezone("America/Chicago", "out_tz")
    zoneinfo.ZoneInfo(key='America/Chicago')

    >>> resolve_timezone("Mars/Olympus", "out_tz")
    Traceback (most recent call last):
        ...
    ValueError: Unknown out_tz 'Mars/Olympus'; use an IANA timezone name such as 'UTC', 'Europe/Madrid', or 'America/Chicago'
    """
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            f"Unknown {parameter} {name!r}; use an IANA timezone name such "
            "as 'UTC', 'Europe/Madrid', or 'America/Chicago'"
        ) from exc


def parse_cycle_date(date: str) -> datetime:
    """Parse a ``YYYYMMDD`` raster date for timezone conversion.

    Parameters
    ----------
    date : str
        Date as it appears in the raster filename, e.g. ``"20260101"``.

    Returns
    -------
    datetime.datetime
        Midnight on that date, with no timezone attached.

    Raises
    ------
    ValueError
        If ``date`` is not eight digits in ``YYYYMMDD`` order.

    Examples
    --------
    >>> parse_cycle_date("20260101")
    datetime.datetime(2026, 1, 1, 0, 0)

    >>> parse_cycle_date("01-01-2026")
    Traceback (most recent call last):
        ...
    ValueError: Raster date '01-01-2026' must use YYYYMMDD format for timezone conversion
    """
    try:
        return datetime.strptime(date, "%Y%m%d")
    except ValueError as exc:
        raise ValueError(
            f"Raster date {date!r} must use YYYYMMDD format for timezone "
            "conversion"
        ) from exc
