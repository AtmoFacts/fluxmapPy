"""Boolean pass/fail masks built from FluxMap quality-flag bands."""

import numpy as np

#Creates mask based on qf_threshold
#Needs to know if its less than the qf threshold or greater than using qf_keep. 
def quality_pass_mask(
    quality_data: np.ma.MaskedArray,
    measurement_shape: tuple[int, int, int],
    qf_threshold: float,
    qf_keep: str,
) -> np.ndarray:
    """Return ``True`` where a measurement pixel passes the quality rule.

    Parameters
    ----------
    quality_data : numpy.ma.MaskedArray
        Quality-flag bands, shaped either like ``measurement_shape`` or
        with a single band to broadcast across all of them.
    measurement_shape : tuple of int
        Shape ``(bands, rows, columns)`` of the measurement raster the
        mask will be applied to.
    qf_threshold : float
        Quality-flag threshold, on the 0-5 FluxMap scale.
    qf_keep : {"lte", "gte"}
        Which side of the threshold passes. ``"lte"`` passes flags at or
        below the threshold; ``"gte"`` passes those at or above it.

    Returns
    -------
    numpy.ndarray
        Boolean array of ``measurement_shape``. Masked or non-finite
        quality values never pass.

    Raises
    ------
    ValueError
        If ``qf_keep`` is not ``"lte"`` or ``"gte"``, or if the quality
        band count is neither 1 nor equal to the measurement band count.

    Examples
    --------
    >>> import numpy as np
    >>> quality = np.ma.array([[[0, 1], [2, 3]]])
    >>> quality_pass_mask(quality, (1, 2, 2), qf_threshold=1, qf_keep="lte")
    array([[[ True,  True],
            [False, False]]])

    Keeping the other side of the same threshold inverts the result:

    >>> quality_pass_mask(quality, (1, 2, 2), qf_threshold=1, qf_keep="gte")
    array([[[False,  True],
            [ True,  True]]])

    A single quality band broadcasts across every measurement band:

    >>> quality_pass_mask(quality, (48, 2, 2), qf_threshold=1, qf_keep="lte").shape
    (48, 2, 2)

    >>> quality_pass_mask(quality, (1, 2, 2), qf_threshold=1, qf_keep="eq")
    Traceback (most recent call last):
        ...
    ValueError: qf_keep must be either 'lte' or 'gte'
    """
    quality_data = np.ma.masked_invalid(quality_data.astype("float32"))

    if qf_keep == "lte":
        quality_passes = quality_data <= qf_threshold
    elif qf_keep == "gte":
        quality_passes = quality_data >= qf_threshold
    else:
        raise ValueError("qf_keep must be either 'lte' or 'gte'")

    quality_passes = np.asarray(quality_passes.filled(False), dtype=bool)
    if quality_passes.shape == measurement_shape:
        return quality_passes
    if (
        quality_passes.shape[0] == 1
        and quality_passes.shape[1:] == measurement_shape[1:]
    ):
        return np.broadcast_to(quality_passes, measurement_shape)

    raise ValueError(
        "Quality raster band count must be 1 or match the measurement "
        "raster band count."
    )
