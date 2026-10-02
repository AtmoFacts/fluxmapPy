"""Grid compatibility checks between measurement and quality rasters."""

from pathlib import Path

# Checks the grids of the rasters and the CRS
def assert_same_grid(
    measurement_path: Path,
    measurement_profile: dict,
    quality_path: Path,
    quality_profile: dict,
) -> None:
    """Require measurement and quality rasters to share a spatial grid.

    Parameters
    ----------
    measurement_path : pathlib.Path
        Path to the measurement raster, used in the error message.
    measurement_profile : dict
        Rasterio profile of the measurement raster.
    quality_path : pathlib.Path
        Path to the quality raster, used in the error message.
    quality_profile : dict
        Rasterio profile of the quality raster.

    Returns
    -------
    None
        Returns nothing when the grids match.

    Raises
    ------
    ValueError
        If ``width``, ``height``, ``transform`` or ``crs`` differ,
        naming every field that disagrees.

    Examples
    --------
    >>> from pathlib import Path
    >>> grid = {"width": 64, "height": 64, "transform": None, "crs": "EPSG:4326"}
    >>> assert_same_grid(Path("a.tif"), grid, Path("a_qf.tif"), dict(grid)) is None
    True

    >>> other = dict(grid, width=32)
    >>> assert_same_grid(Path("a.tif"), grid, Path("a_qf.tif"), other)
    Traceback (most recent call last):
        ...
    ValueError: a_qf.tif does not match a.tif for: width
    """
    fields = ("width", "height", "transform", "crs")
    mismatched = [
        field
        for field in fields
        if measurement_profile.get(field) != quality_profile.get(field)
    ]
    if mismatched:
        raise ValueError(
            f"{quality_path} does not match {measurement_path} for: "
            f"{', '.join(mismatched)}"
        )
