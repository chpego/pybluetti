"""Placeholder test so CI has something to run before code is migrated in."""

import pybluetti


def test_package_is_importable_and_versioned() -> None:
    assert pybluetti.__version__ == "0.1.1"
