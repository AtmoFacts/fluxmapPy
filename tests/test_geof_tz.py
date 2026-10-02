"""""""""""""""""""""
 @title test function: Test function that confirms working path for geofencing and timezones within package functionality
 
 @author
 Allen Kaplan email{akaplan@atmofacts.com} 

@test group

 @description wrapper defintion. Tests geofencing capabilities and time zones to confirm no errors in code

 @keywords test, tz, geofence, geof

 changelog and author contributions / copyrights
   Allen Kaplan (2026-08-10)
     original creation
   Allen Kaplan (2026-08-15)
    Reduction in order to reduce lines of code and break apart into smaller functions. 
   Allen Kaplan (2026-08-21)
     adjust function name to eddy4R terms. Now called test_geof_tz.py

"""""""""""""""""""""


from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np

from fluxmappy import wrap_diu


def _raster(date: str, values: np.ndarray):
    return SimpleNamespace(
        record=SimpleNamespace(
            site="test-site",
            flux_type="test-flux",
            date=date,
            path=Path(f"{date}.tif"),
        ),
        filtered_bands=np.ma.array(
            np.asarray(values, dtype=np.float32)[:, None, None]
        ),
        profile={"height": 1, "width": 1},
    )


def _cycles_for(dates: list[str], **kwargs):
    rasters = [_raster(date, np.arange(48)) for date in dates]
    return wrap_diu(rasters, **kwargs)[0]


class GeofenceTimezoneTests(unittest.TestCase):
    def test_default_behavior_remains_utc(self):
        result = _cycles_for(["20260101", "20260102"])

        self.assertEqual(result.timezone, "UTC")
        self.assertEqual(result.dates, ("20260101", "20260102"))
        np.testing.assert_allclose(result.mean_cycle, np.arange(48))

    def test_madrid_winter_and_summer_offsets(self):
        winter = _cycles_for(
            ["20260101", "20260102", "20260103"],
            out_tz="Europe/Madrid",
        )
        summer = _cycles_for(
            ["20260701", "20260702", "20260703"],
            out_tz="Europe/Madrid",
        )

        self.assertEqual(winter.timezone, "Europe/Madrid")
        np.testing.assert_allclose(
            winter.mean_cycle,
            np.roll(np.arange(48), 2),
        )
        np.testing.assert_allclose(
            summer.mean_cycle,
            np.roll(np.arange(48), 4),
        )

    def test_spring_dst_gap_is_a_missing_local_slot(self):
        result = _cycles_for(
            ["20260328", "20260329", "20260330"],
            out_tz="Europe/Madrid",
        )

        transition_day = result.daily_cycles[
            result.dates.index("20260329")
        ]
        self.assertTrue(np.isnan(transition_day[4:6]).all())
        np.testing.assert_array_equal(
            result.valid_day_count[4:6],
            np.full(2, len(result.dates) - 1),
        )

    def test_autumn_repeated_slots_are_averaged_within_day(self):
        result = _cycles_for(
            ["20261024", "20261025", "20261026"],
            out_tz="Europe/Madrid",
        )

        transition_day = result.daily_cycles[
            result.dates.index("20261025")
        ]
        self.assertEqual(transition_day[4], 1.0)
        self.assertEqual(transition_day[5], 2.0)

    def test_incomplete_day_policy(self):
        included = _cycles_for(
            ["20260101"],
            out_tz="Europe/Madrid",
            incomplete_local_days="include",
        )
        self.assertEqual(included.dates, ("20260101", "20260102"))

        with self.assertRaisesRegex(ValueError, "No complete local days"):
            _cycles_for(
                ["20260101"],
                out_tz="Europe/Madrid",
            )

    def test_invalid_timezone_has_clear_error(self):
        with self.assertRaisesRegex(ValueError, "Unknown out_tz"):
            _cycles_for(
                ["20260101"],
                out_tz="Mars/Olympus",
            )


if __name__ == "__main__":
    unittest.main()
