"""Conversion of UTC daily cycles into local-time diurnal slots."""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np

from .def_diu_tz_vali import parse_cycle_date

#Function that takes in the specified time zone and targets the FluxMaps to them. 
def expected_local_day_instants(
    local_date: str,
    target_timezone: ZoneInfo,
) -> set[datetime]:
    """Return the UTC half-hour instants making up one full local day.

    Used to decide whether a local day is fully covered by the source
    rasters once a timezone shift has been applied.

    Parameters
    ----------
    local_date : str
        Local date in ``YYYYMMDD`` form.
    target_timezone : zoneinfo.ZoneInfo
        Timezone the local day is measured in.

    Returns
    -------
    set of datetime.datetime
        Every half-hour instant of that local day, in UTC. Normally 48
        instants, but 46 or 50 across a daylight-saving transition.

    Examples
    --------
    >>> from zoneinfo import ZoneInfo
    >>> len(expected_local_day_instants("20260101", ZoneInfo("UTC")))
    48

    A spring-forward day is an hour shorter, so two slots do not exist:

    >>> len(expected_local_day_instants("20260308", ZoneInfo("America/Chicago")))
    46

    A fall-back day gains an hour:

    >>> len(expected_local_day_instants("20261101", ZoneInfo("America/Chicago")))
    50
    """
    local_midnight = parse_cycle_date(local_date).replace(
        tzinfo=target_timezone
    )
    next_local_midnight = (
        parse_cycle_date(local_date) + timedelta(days=1)
    ).replace(tzinfo=target_timezone)

    instant = local_midnight.astimezone(timezone.utc)
    end_utc = next_local_midnight.astimezone(timezone.utc)
    expected: set[datetime] = set()
    while instant < end_utc:
        expected.add(instant)
        instant += timedelta(minutes=30)
    return expected


# Function that converts the UTC timezone to the output time zone. 
def localize_daily_cycles(
    dated_cycles: list[tuple[str, np.ndarray]],
    input_timezone: ZoneInfo,
    output_timezone: ZoneInfo,
    incomplete_local_days: str,
) -> tuple[tuple[str, ...], np.ndarray]:
    """Regroup daily cycles from source dates into local dates.

    Each band is timestamped from its source date and timezone, converted
    into ``output_timezone``, and filed under the local date and
    half-hour slot it lands in. Slots receiving more than one value, as
    happens on a fall-back day, are averaged.

    Parameters
    ----------
    dated_cycles : list of (str, numpy.ndarray)
        Source date in ``YYYYMMDD`` form paired with that day's 48
        half-hourly values.
    input_timezone : zoneinfo.ZoneInfo
        Timezone in which band 1 of each source day is midnight.
    output_timezone : zoneinfo.ZoneInfo
        Timezone to regroup into.
    incomplete_local_days : {"drop", "include", "error"}
        What to do with local days the source data only partly covers.

    Returns
    -------
    dates : tuple of str
        Local dates retained, in ascending order.
    daily_cycles : numpy.ndarray
        Array of shape ``(len(dates), 48)``. Slots with no contributing
        value are ``nan``.

    Raises
    ------
    ValueError
        If ``incomplete_local_days`` is ``"error"`` and any local day is
        incomplete, or if no local days survive the policy.

    Examples
    --------
    >>> import numpy as np
    >>> from zoneinfo import ZoneInfo
    >>> cycles = [(d, np.arange(48, dtype=float))
    ...           for d in ("20260101", "20260102", "20260103")]
    >>> dates, values = localize_daily_cycles(
    ...     cycles, ZoneInfo("UTC"), ZoneInfo("America/Chicago"), "drop"
    ... )
    >>> values.shape
    (2, 48)
    >>> dates
    ('20260101', '20260102')
    """
    values_by_date: dict[str, list[list[float]]] = {}
    instants_by_date: dict[str, set[datetime]] = {}

    for source_date, values in dated_cycles:
        source_midnight = parse_cycle_date(source_date).replace(
            tzinfo=input_timezone
        )
        source_start_utc = source_midnight.astimezone(timezone.utc)

        for band_index, value in enumerate(values):
            instant_utc = source_start_utc + timedelta(
                minutes=30 * band_index
            )
            local_timestamp = instant_utc.astimezone(output_timezone)
            local_date = local_timestamp.strftime("%Y%m%d")
            local_slot = local_timestamp.hour * 2 + local_timestamp.minute // 30
            date_values = values_by_date.setdefault(
                local_date,
                [[] for _ in range(48)],
            )
            date_values[local_slot].append(float(value))
            instants_by_date.setdefault(local_date, set()).add(instant_utc)

    incomplete_dates = {
        local_date
        for local_date, observed_instants in instants_by_date.items()
        if not expected_local_day_instants(
            local_date,
            output_timezone,
        ).issubset(observed_instants)
    }
    if incomplete_local_days == "error" and incomplete_dates:
        dates = ", ".join(sorted(incomplete_dates))
        raise ValueError(
            f"Timezone conversion produced incomplete local days: {dates}"
        )

    selected_dates = tuple(
        local_date
        for local_date in sorted(values_by_date)
        if incomplete_local_days == "include"
        or local_date not in incomplete_dates
    )
    if not selected_dates:
        raise ValueError(
            "No complete local days remained after timezone conversion; "
            "provide adjacent UTC dates or use "
            "incomplete_local_days='include'"
        )

    daily_cycles = np.full((len(selected_dates), 48), np.nan, dtype=float)
    for day_index, local_date in enumerate(selected_dates):
        for local_slot, slot_values in enumerate(values_by_date[local_date]):
            if not slot_values:
                continue
            masked_values = np.ma.masked_invalid(
                np.asarray(slot_values, dtype=float)
            )
            if masked_values.count() > 0:
                daily_cycles[day_index, local_slot] = float(
                    np.ma.mean(masked_values)
                )

    return selected_dates, daily_cycles
