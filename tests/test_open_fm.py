"""Tests for opening and quality-masking a single FluxMap band.

Every raster used here is generated at test time from a synthetic numpy
array. No binary fixtures are committed to the repository.

The rasters are written to pytest's ``tmp_path`` rather than to a
``TemporaryDirectory``. ``tmp_path`` cleans up lazily and tolerates
failure, which matters on Windows, where a file cannot be unlinked while
any handle to it is still open.
"""

from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from fluxmappy import OpenedFluxMap, wrap_open_fm


def _write_raster(path: Path, data: np.ndarray) -> None:
    """Write a synthetic array to a GeoTIFF with per-band metadata."""
    profile = {
        "driver": "GTiff",
        "height": data.shape[1],
        "width": data.shape[2],
        "count": data.shape[0],
        "dtype": data.dtype,
        "crs": "EPSG:4326",
        "transform": from_origin(0, 2, 1, 1),
    }
    with rasterio.open(path, "w", **profile) as destination:
        destination.write(data)
        for band in range(1, data.shape[0] + 1):
            destination.set_band_description(band, f"Band {band}")
            destination.update_tags(band, time_index=str(band))


def test_opens_only_requested_band_and_applies_matching_qf_band(tmp_path):
    measurement_path = tmp_path / "siteA_fluxCo2_20260101.tif"
    quality_path = tmp_path / "siteA_fluxCo2_20260101_qf.tif"

    measurement = np.stack(
        [np.full((2, 2), band, dtype=np.float32) for band in range(1, 4)]
    )
    quality = np.array(
        [
            [[0, 0], [0, 0]],
            [[0, 1], [2, 3]],
            [[3, 3], [3, 3]],
        ],
        dtype=np.uint8,
    )
    _write_raster(measurement_path, measurement)
    _write_raster(quality_path, quality)

    result = wrap_open_fm(measurement_path, band=2, qf_thsh=1)

    assert isinstance(result, OpenedFluxMap)
    assert result.band == 2
    assert result.quality_path == quality_path
    assert result.description == "Band 2"
    assert result.tags["time_index"] == "2"
    assert result.profile["count"] == 1
    np.testing.assert_array_equal(
        np.ma.getmaskarray(result.data),
        np.array([[False, False], [True, True]]),
    )
    np.testing.assert_array_equal(
        result.data.compressed(),
        np.array([2, 2], dtype=np.float32),
    )


def test_single_quality_band_is_applied_to_selected_band(tmp_path):
    measurement_path = tmp_path / "siteA_fluxCo2_20260101.tif"
    quality_path = tmp_path / "custom-quality.tif"
    _write_raster(measurement_path, np.ones((3, 2, 2), dtype=np.float32))
    _write_raster(
        quality_path,
        np.array([[[0, 2], [1, 3]]], dtype=np.uint8),
    )

    result = wrap_open_fm(
        measurement_path,
        band=3,
        qf_path=quality_path,
        qf_thsh=1,
    )

    np.testing.assert_array_equal(
        np.ma.getmaskarray(result.data),
        np.array([[False, True], [False, True]]),
    )


def test_rejects_out_of_range_band(tmp_path):
    measurement_path = tmp_path / "siteA_fluxCo2_20260101.tif"
    quality_path = tmp_path / "siteA_fluxCo2_20260101_qf.tif"
    _write_raster(measurement_path, np.ones((2, 1, 1), dtype=np.float32))
    _write_raster(quality_path, np.zeros((1, 1, 1), dtype=np.uint8))

    with pytest.raises(ValueError, match="available bands are 1-2"):
        wrap_open_fm(measurement_path, band=3)


def test_rejects_zero_and_negative_bands(tmp_path):
    measurement_path = tmp_path / "siteA_fluxCo2_20260101.tif"

    for band in (0, -1):
        with pytest.raises(ValueError, match="positive 1-based integer"):
            wrap_open_fm(measurement_path, band=band)
