"""Summary statistics across the daily cycles of one region."""

# Requires Numpy package 
import numpy as np


# Function that summerizes daily means from filtered FluxMaps. Returns mean, deviation, valid counts, and cumulative cycle.
def summarize_daily_cycles(
    daily_cycles: np.ndarray,
    timestep_seconds: float | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Summarise stacked daily cycles into mean, spread, counts and totals.

    Parameters
    ----------
    daily_cycles : numpy.ndarray
        Array of shape ``(n_days, 48)`` holding one spatial mean per
        half-hour slot for each day.
    timestep_seconds : float or None
        Seconds represented by each slot, used to scale the cumulative
        cycle. ``None`` leaves the cumulative sum unscaled.

    Returns
    -------
    mean_cycle : numpy.ndarray
        Per-slot mean across days, shape ``(48,)``.
    standard_deviation : numpy.ndarray
        Per-slot standard deviation *across days*, not across pixels.
    valid_day_count : numpy.ndarray
        Number of finite observations contributing to each slot.
    cumulative_cycle : numpy.ndarray
        Running total of ``mean_cycle`` scaled by ``timestep_seconds``.

    Examples
    --------
    >>> import numpy as np
    >>> days = np.array([[1.0, 2.0], [3.0, 4.0]])
    >>> mean, sd, n, cum = summarize_daily_cycles(days, 1800.0)
    >>> mean
    array([2., 3.])
    >>> sd
    array([1., 1.])
    >>> n
    array([2, 2])
    >>> cum
    array([3600., 9000.])

    A day missing one slot is skipped for that slot only:

    >>> days = np.array([[1.0, np.nan], [3.0, 4.0]])
    >>> mean, sd, n, cum = summarize_daily_cycles(days, None)
    >>> mean
    array([2., 4.])
    >>> n
    array([2, 1])
    """
    masked_cycles = np.ma.masked_invalid(daily_cycles)
    mean_cycle = np.asarray(
        np.ma.mean(masked_cycles, axis=0).filled(np.nan),
        dtype=float,
    )
    standard_deviation = np.asarray(
        np.ma.std(masked_cycles, axis=0).filled(np.nan),
        dtype=float,
    )
    valid_day_count = np.sum(np.isfinite(daily_cycles), axis=0)

    interval_scale = 1.0 if timestep_seconds is None else timestep_seconds
    increments = np.ma.masked_invalid(mean_cycle * interval_scale)
    cumulative_cycle = np.asarray(
        np.ma.cumsum(increments).filled(np.nan),
        dtype=float,
    )
    return (
        mean_cycle,
        standard_deviation,
        valid_day_count,
        cumulative_cycle,
    )


    # To call and plot, use results.mean or results.cumulative to see pattern. 
