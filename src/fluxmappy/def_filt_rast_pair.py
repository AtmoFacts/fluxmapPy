"""Discovery and pairing of measurement and quality FluxMap files."""

from pathlib import Path

from .modl_filt import RasterPair, RasterRecord
from .def_filt_rast_name import parse_raster_path

# Discovers raster pairs between measurement rasters and qf rasters. Will skip over mismatching names or problem files. 
def find_raster_pairs(
    data_dir: Path,
    flux_type: str,
) -> list[RasterPair]:
    """Recursively find and pair measurement and quality TIFFs.

    Walks ``data_dir``, parses every filename, and matches each
    measurement raster to the quality raster sharing its site, flux type
    and date.

    Parameters
    ----------
    data_dir : pathlib.Path
        Directory to search, including subdirectories.
    flux_type : str
        Flux type to keep, e.g. ``"fluxCo2"``.

    Returns
    -------
    list of RasterPair
        One entry per matched measurement/quality pair, ordered by date.

    Raises
    ------
    FileNotFoundError
        If ``data_dir`` is not a directory.
    ValueError
        If no measurement rasters of ``flux_type`` are found, or a
        measurement raster has no matching quality raster.

    Examples
    --------
    Requires rasters on disk, so this is shown rather than executed:

    >>> from pathlib import Path
    >>> pairs = find_raster_pairs(Path("KONA"), "fluxCo2")  # doctest: +SKIP
    >>> len(pairs)  # doctest: +SKIP
    12
    """
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")

    records: list[RasterRecord] = []
    for path in sorted(data_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".tif", ".tiff"}:
            continue
        record = parse_raster_path(path)
        if (
            record is not None
            and record.flux_type.casefold() == flux_type.casefold()
        ):
            records.append(record)

    quality_by_key = {
        (
            record.path.parent,
            record.site.casefold(),
            record.flux_type.casefold(),
            record.date,
        ): record.path
        for record in records
        if record.is_quality
    }

    pairs: list[RasterPair] = []
    missing_quality: list[Path] = []
    for record in records:
        if record.is_quality:
            continue
        key = (
            record.path.parent,
            record.site.casefold(),
            record.flux_type.casefold(),
            record.date,
        )
        quality_path = quality_by_key.get(key)
        if quality_path is None:
            missing_quality.append(record.path)
        else:
            pairs.append(
                RasterPair(
                    measurement=record,
                    quality_path=quality_path,
                )
            )

    if missing_quality:
        missing = "\n  ".join(str(path) for path in missing_quality)
        raise FileNotFoundError(
            "No matching _qa or _qf raster was found for:\n"
            f"  {missing}"
        )
    if not pairs:
        raise FileNotFoundError(
            f"No measurement/quality pairs for {flux_type} were found "
            f"below {data_dir}"
        )
    return pairs
