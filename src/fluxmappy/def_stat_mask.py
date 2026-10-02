"""Masking of FluxMaps to vector polygons, or passing them through as a whole raster."""

from collections.abc import Iterable, Iterator
from pathlib import Path

import numpy as np
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom

from .modl_geof import (
    FilteredFluxRasterLike,
    GeofencedRaster,
    VectorLayer,
)
from .def_stat_vect import read_vector_layer

# reads vector and defines area for analysis 
def geofence_raster(
    filtered_raster: FilteredFluxRasterLike,
    vector_layer: VectorLayer,
    all_touched: bool = False,
) -> Iterator[GeofencedRaster]:
    """Yield one independently masked raster per vector feature.

    Parameters
    ----------
    filtered_raster : FilteredFluxRaster
        Raster to clip, which must carry ``crs`` and ``transform`` in its
        profile.
    vector_layer : VectorLayer
        Polygons to clip to, reprojected to the raster CRS as needed.
    all_touched : bool, default False
        Include every pixel touched by a polygon, not only those whose
        centre falls inside it.

    Yields
    ------
    GeofencedRaster
        One per polygon that overlaps the raster. Polygons with no
        overlapping pixels are skipped.

    Raises
    ------
    ValueError
        If the raster lacks the spatial metadata needed to apply a
        vector.
    """
    raster_crs = filtered_raster.profile.get("crs")
    raster_transform = filtered_raster.profile.get("transform")
    height = filtered_raster.profile.get("height")
    width = filtered_raster.profile.get("width")

    if raster_crs is None:
        raise ValueError(
            f"Filtered raster has no CRS: {filtered_raster.record.path}"
        )
    if raster_transform is None or height is None or width is None:
        raise ValueError(
            "Filtered raster has incomplete spatial metadata: "
            f"{filtered_raster.record.path}"
        )

    for feature in vector_layer.features:
        raster_geometry = transform_geom(
            vector_layer.crs,
            raster_crs,
            feature.geometry,
        )
        inside_polygon = geometry_mask(
            [raster_geometry],
            out_shape=(height, width),
            transform=raster_transform,
            invert=True,
            all_touched=all_touched,
        )
        outside_polygon = np.broadcast_to(
            ~inside_polygon[np.newaxis, :, :],
            filtered_raster.filtered_bands.shape,
        )

        yield GeofencedRaster(
            source=filtered_raster,
            feature_id=feature.feature_id,
            properties=feature.properties.copy(),
            masked_bands=np.ma.masked_where(
                outside_polygon,
                filtered_raster.filtered_bands,
            ),
            polygon_pixel_count=int(inside_polygon.sum()),
            vector_path=vector_layer.path,
        )

# Stores polygon areas.  
def iter_geofenced_rasters(
    filtered_rasters: Iterable[FilteredFluxRasterLike],
    vector_path: Path | None = None,
    id_field: str | None = None,
    all_touched: bool = False,
) -> Iterator[GeofencedRaster]:
    """Yield polygon regions, or one whole region per raster.

    Parameters
    ----------
    filtered_rasters : iterable of FilteredFluxRaster
        Rasters to geofence.
    vector_path : pathlib.Path, optional
        Polygon vector file. When ``None`` (default) each raster is
        yielded whole, as a single region with ``feature_id`` 0.
    id_field : str, optional
        Vector attribute identifying each polygon.
    all_touched : bool, default False
        Include every pixel touched by a polygon.

    Yields
    ------
    GeofencedRaster
        One per raster and polygon, or one per raster when no vector is
        given.

    Examples
    --------
    With no vector, each raster passes through as a single whole region:

    >>> rasters = [_example_raster("20260101")]
    >>> regions = list(iter_geofenced_rasters(rasters))
    >>> len(regions)
    1
    >>> regions[0].feature_id
    'whole_raster'
    >>> regions[0].masked_bands.shape
    (48, 1, 1)
    """
    if vector_path is None:
        if id_field is not None:
            raise ValueError("id_field requires a vector_path")
        for filtered_raster in filtered_rasters:
            spatial_shape = filtered_raster.filtered_bands.shape[-2:]
            yield GeofencedRaster(
                source=filtered_raster,
                feature_id="whole_raster",
                properties={},
                masked_bands=filtered_raster.filtered_bands.copy(),
                polygon_pixel_count=int(np.prod(spatial_shape)),
                vector_path=None,
            )
        return

    vector_layer = read_vector_layer(vector_path, id_field=id_field)
    for filtered_raster in filtered_rasters:
        yield from geofence_raster(
            filtered_raster,
            vector_layer,
            all_touched=all_touched,
        )


def _example_raster(date: str) -> object:
    """Build a one-pixel filtered raster for the docstring examples."""
    from types import SimpleNamespace

    return SimpleNamespace(
        record=SimpleNamespace(
            site="KONA",
            flux_type="fluxCo2",
            date=date,
            path=Path(f"{date}.tif"),
        ),
        filtered_bands=np.ma.array(
            np.arange(48, dtype=np.float32)[:, None, None]
        ),
        profile={"height": 1, "width": 1},
    )
