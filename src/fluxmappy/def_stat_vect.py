"""Reading of polygon vector layers used to clip FluxMaps."""

from pathlib import Path

import fiona

from .modl_geof import VectorFeature, VectorLayer

# Reads vector layer and returns error if incorrect. 
def read_vector_layer(
    vector_path: Path,
    id_field: str | None = None,
) -> VectorLayer:
    """Read polygon features, preserving a unique ID for each.

    Parameters
    ----------
    vector_path : pathlib.Path
        Vector file to read, in any format Fiona can open.
    id_field : str, optional
        Attribute to use as each feature's identifier. When ``None``
        (default) the feature index is used.

    Returns
    -------
    VectorLayer
        Carrying the layer ``crs`` and a tuple of ``features``, each with
        its ``feature_id``, ``geometry`` and ``properties``.

    Raises
    ------
    FileNotFoundError
        If ``vector_path`` does not exist.
    ValueError
        If the file holds no features, if ``id_field`` is absent from the
        schema, or if its values are not unique.

    Examples
    --------
    Requires a vector file on disk, so this is shown rather than
    executed:

    >>> from pathlib import Path
    >>> layer = read_vector_layer(Path("sites.shp"), id_field="name")  # doctest: +SKIP
    >>> len(layer.features)  # doctest: +SKIP
    3
    """
    if not vector_path.is_file():
        raise FileNotFoundError(f"Vector file does not exist: {vector_path}")

    with fiona.open(vector_path) as vector_src:
        vector_crs = vector_src.crs_wkt or vector_src.crs
        available_fields = tuple(vector_src.schema.get("properties", {}))
        if id_field is not None and id_field not in available_fields:
            raise ValueError(
                f"ID field {id_field!r} is not in {vector_path}. "
                f"Available fields: {available_fields}"
            )

        features: list[VectorFeature] = []
        seen_ids: set[object] = set()
        for feature_number, feature in enumerate(vector_src, start=1):
            geometry = feature["geometry"]
            if geometry is None:
                raise ValueError(
                    f"Feature {feature_number} in {vector_path} has no geometry"
                )

            geometry_mapping = geometry.__geo_interface__
            geometry_type = geometry_mapping.get("type")
            if geometry_type not in {"Polygon", "MultiPolygon"}:
                raise ValueError(
                    f"Feature {feature_number} has geometry type "
                    f"{geometry_type!r}; expected Polygon or MultiPolygon"
                )

            properties = dict(feature["properties"])
            feature_id = (
                properties[id_field] if id_field is not None else feature_number
            )
            if feature_id is None:
                raise ValueError(
                    f"Feature {feature_number} has no value for {id_field!r}"
                )
            if feature_id in seen_ids:
                raise ValueError(
                    f"Vector feature ID {feature_id!r} is not unique"
                )
            seen_ids.add(feature_id)
            features.append(
                VectorFeature(
                    feature_id=feature_id,
                    properties=properties,
                    geometry=geometry_mapping,
                )
            )

    if not vector_crs:
        raise ValueError(f"Vector has no CRS: {vector_path}")
    if not features:
        raise ValueError(f"Vector contains no polygon features: {vector_path}")

    return VectorLayer(
        path=vector_path,
        crs=vector_crs,
        features=tuple(features),
        id_field=id_field,
    )
