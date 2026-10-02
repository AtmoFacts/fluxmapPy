"""Location of the quality-flag raster that partners a FluxMap."""

from pathlib import Path

from .def_filt_rast_name import parse_raster_path

# Locates quality path and validates the files, will return error if none found or naming issue. 
def resolve_quality_path(
    measurement_path: str | Path,
    quality_path: str | Path | None = None,
) -> tuple[Path, Path]:
    """Validate a measurement path and locate its quality raster.

    Parameters
    ----------
    measurement_path : str or pathlib.Path
        Measurement raster that must already exist on disk.
    quality_path : str or pathlib.Path, optional
        Explicit quality raster. When ``None`` (default) a sibling file
        with a ``_qf`` or ``_qa`` suffix is looked for alongside the
        measurement raster.

    Returns
    -------
    measurement : pathlib.Path
        The validated measurement raster.
    quality : pathlib.Path
        The quality raster to pair with it.

    Raises
    ------
    FileNotFoundError
        If the measurement raster does not exist, or if no quality raster
        could be found or the one given is missing.

    Examples
    --------
    Both paths are checked on disk, so this is shown rather than
    executed:

    >>> resolve_quality_path("KONA/KONA_fluxCo2_20260101.tif")  # doctest: +SKIP
    (PosixPath('KONA/KONA_fluxCo2_20260101.tif'),
     PosixPath('KONA/KONA_fluxCo2_20260101_qf.tif'))
    """
    measurement = Path(measurement_path)
    if not measurement.is_file():
        raise FileNotFoundError(
            f"Measurement raster does not exist: {measurement}"
        )

    record = parse_raster_path(measurement)
    if record is None:
        raise ValueError(
            f"Could not parse site, flux type, and date from {measurement.name}"
        )
    if record.is_quality:
        raise ValueError(
            f"Expected a measurement raster, received quality raster: "
            f"{measurement}"
        )

    if quality_path is not None:
        quality = Path(quality_path)
        if not quality.is_file():
            raise FileNotFoundError(f"Quality raster does not exist: {quality}")
        return measurement, quality

    matches: list[Path] = []
    for candidate in measurement.parent.iterdir():
        if (
            not candidate.is_file()
            or candidate.suffix.lower() not in {".tif", ".tiff"}
        ):
            continue
        candidate_record = parse_raster_path(candidate)
        if candidate_record is None or not candidate_record.is_quality:
            continue
        if (
            candidate_record.site.casefold() == record.site.casefold()
            and candidate_record.flux_type.casefold()
            == record.flux_type.casefold()
            and candidate_record.date == record.date
        ):
            matches.append(candidate)

    if not matches:
        raise FileNotFoundError(
            f"No matching _qa or _qf raster was found for {measurement}"
        )
    if len(matches) > 1:
        paths = "\n  ".join(str(path) for path in sorted(matches))
        raise ValueError(
            "More than one matching quality raster was found; pass "
            f"quality_path explicitly:\n  {paths}"
        )
    return measurement, matches[0]
