"""Tests that the public API surface matches what ``__all__`` advertises.

These are deliberately cheap and import-only: no rasters, no filesystem,
no platform-specific behaviour. They are the first thing to fail if a
rename, a re-export or an ``__all__`` edit leaves the package
inconsistent.
"""

import importlib
import types

import fluxmappy

CANONICAL_WRAPPERS = ("wrap_diu", "wrap_filt_qf", "wrap_open_fm", "wrap_stat")


def test_every_all_name_resolves_on_the_package():
    missing = [name for name in fluxmappy.__all__ if not hasattr(fluxmappy, name)]
    assert missing == [], f"__all__ advertises names the package lacks: {missing}"


def test_star_import_binds_every_all_name():
    namespace: dict[str, object] = {}
    exec("from fluxmappy import *", namespace)  # noqa: S102
    missing = [name for name in fluxmappy.__all__ if name not in namespace]
    assert missing == [], f"star import did not bind: {missing}"


def test_each_all_name_is_individually_importable():
    for name in fluxmappy.__all__:
        module = importlib.import_module("fluxmappy")
        assert hasattr(module, name), f"cannot import {name} from fluxmappy"


def test_all_is_unique_and_sorted():
    assert len(fluxmappy.__all__) == len(set(fluxmappy.__all__)), "duplicate entries"
    assert list(fluxmappy.__all__) == sorted(
        fluxmappy.__all__, key=lambda name: (name[0].islower(), name)
    ), "__all__ is not in classes-then-functions alphabetical order"


def test_no_public_name_is_shadowed_by_its_module():
    """Guard the module/function naming collision.

    Each wrapper function shares its module's name, so ``fluxmappy.wrap_diu``
    could resolve to the module rather than the function if the re-export in
    ``__init__`` were reordered or removed.
    """
    shadowed = [
        name
        for name in fluxmappy.__all__
        if isinstance(getattr(fluxmappy, name), types.ModuleType)
    ]
    assert shadowed == [], f"resolved to modules, not objects: {shadowed}"


def test_canonical_wrappers_are_callable_and_match_their_modules():
    for name in CANONICAL_WRAPPERS:
        assert name in fluxmappy.__all__, f"{name} missing from __all__"
        function = getattr(fluxmappy, name)
        assert callable(function), f"{name} is not callable"
        defining_module = importlib.import_module(f"fluxmappy.{name}")
        assert function is getattr(defining_module, name), (
            f"fluxmappy.{name} is not the object defined in fluxmappy/{name}.py"
        )


def test_removed_aliases_stay_removed():
    """The descriptive names dropped in favour of one canonical name each."""
    for name in (
        "geofence_diurnal_cycles",
        "geofence_statistics",
        "open_fluxmap",
        "qf_filter_rasters",
        "iter_filtered_rasters",
        "qf_filtered_rasters",
    ):
        assert not hasattr(fluxmappy, name), f"{name} came back"
        assert name not in fluxmappy.__all__, f"{name} came back in __all__"
