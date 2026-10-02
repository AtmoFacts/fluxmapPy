"""""""""""""""""""""
 @title test function: Test function that confirms working path for public facing API wrapper functions
 
 @author
 Allen Kaplan email{akaplan@atmofacts.com} 

@test group

 @description wrapper defintion. Confirms wrapper functions are working upon installation

 @keywords test, wrap

 changelog and author contributions / copyrights
   Allen Kaplan (2026-08-10)
     original creation
   Allen Kaplan (2026-08-15)
    Reduction in order to reduce lines of code and break apart into smaller functions. 
   Allen Kaplan (2026-08-21)
     adjust function name to eddy4R terms. Now called test_wrap.py

"""""""""""""""""""""


from pathlib import Path
from types import SimpleNamespace
import importlib
import inspect
import unittest

import numpy as np
from rasterio.transform import from_origin

import fluxmappy
from fluxmappy.def_filt_qf_mask import quality_pass_mask

# Each public function shares its module name (the function wrap_diu shadows the
# module wrap_diu on the package), so `import fluxmappy.wrap_diu as x` would bind
# the function. Fetch the defining modules explicitly instead.
diurnal_api = importlib.import_module("fluxmappy.wrap_diu")
filtering_facade = importlib.import_module("fluxmappy.wrap_filt_qf")
opening_api = importlib.import_module("fluxmappy.wrap_open_fm")
statistics_api = importlib.import_module("fluxmappy.wrap_stat")


def _raster(values: np.ndarray):
    return SimpleNamespace(
        record=SimpleNamespace(
            site="test-site",
            flux_type="test-flux",
            date="20260101",
            path=Path("test.tif"),
        ),
        filtered_bands=np.ma.array(values),
        profile={
            "crs": "EPSG:4326",
            "transform": from_origin(0, 2, 1, 1),
            "height": 2,
            "width": 2,
        },
    )


class PublicApiTests(unittest.TestCase):
    def test_top_level_reexports_defining_modules(self):
        self.assertIs(
            fluxmappy.wrap_filt_qf,
            filtering_facade.wrap_filt_qf,
        )
        self.assertIs(
            fluxmappy.wrap_stat,
            statistics_api.wrap_stat,
        )
        self.assertIs(
            fluxmappy.wrap_diu,
            diurnal_api.wrap_diu,
        )
        self.assertIs(
            fluxmappy.wrap_open_fm,
            opening_api.wrap_open_fm,
        )

    def test_filtering_requires_a_user_supplied_data_directory(self):
        parameter = inspect.signature(
            fluxmappy.wrap_filt_qf
        ).parameters["data"]

        self.assertIs(parameter.default, inspect.Parameter.empty)

    def test_quality_mask_applies_threshold_and_broadcasts(self):
        quality = np.ma.array([[[0, 1], [2, 3]]])
        result = quality_pass_mask(
            quality,
            measurement_shape=(48, 2, 2),
            qf_threshold=1,
            qf_keep="lte",
        )

        self.assertEqual(result.shape, (48, 2, 2))
        np.testing.assert_array_equal(
            result[0],
            np.array([[True, True], [False, False]]),
        )

    def test_polygon_mask_and_statistics_still_work(self):
        raster = _raster(np.ones((48, 2, 2), dtype=np.float32))
        feature = fluxmappy.VectorFeature(
            feature_id="top-left",
            properties={"name": "top-left"},
            geometry={
                "type": "Polygon",
                "coordinates": [
                    [(0, 1), (0, 2), (1, 2), (1, 1), (0, 1)]
                ],
            },
        )
        layer = fluxmappy.VectorLayer(
            path=Path("regions.shp"),
            crs="EPSG:4326",
            features=(feature,),
            id_field="name",
        )

        region = next(fluxmappy.geofence_raster(raster, layer))
        statistics = region.statistics()

        self.assertEqual(region.polygon_pixel_count, 1)
        np.testing.assert_array_equal(
            statistics.count,
            np.ones(48, dtype=int),
        )


if __name__ == "__main__":
    unittest.main()
