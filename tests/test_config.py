"""Tests for config.py.

Validates that all path constants are defined, well-formed, and that
PROJECT_ROOT points to an existing directory.
"""

import os

import pytest

from config import (
    BOUNDARIES_DIR,
    LAYOUTS_DIR,
    MAPS_DIR,
    PROJECT_ROOT,
    RAW_CSV_2015,
    RAW_CSV_2020,
    RAW_CSV_2023,
    RAW_DATA_DIR,
    STATE_SHAPEFILE_2015,
    TRACT_SHAPEFILE_2015,
    TRACT_SHAPEFILE_2020,
    TRACT_SHAPEFILE_2023,
)


class TestConfig:
    """Tests for configuration file paths."""

    def test_project_root_is_absolute(self) -> None:
        """PROJECT_ROOT should be an absolute path."""
        assert os.path.isabs(PROJECT_ROOT)

    def test_project_root_exists(self) -> None:
        """PROJECT_ROOT directory should exist."""
        assert os.path.isdir(PROJECT_ROOT)

    def test_raw_data_dir_defined(self) -> None:
        """RAW_DATA_DIR should be defined and non-empty."""
        assert isinstance(RAW_DATA_DIR, str)
        assert len(RAW_DATA_DIR) > 0

    @pytest.mark.parametrize("path_var", [RAW_CSV_2015, RAW_CSV_2020, RAW_CSV_2023])
    def test_all_csv_paths_are_strings(self, path_var: str) -> None:
        """RAW_CSV paths should be strings."""
        assert isinstance(path_var, str)
        assert len(path_var) > 0

    @pytest.mark.parametrize("path_var", [
        TRACT_SHAPEFILE_2015,
        TRACT_SHAPEFILE_2020,
        TRACT_SHAPEFILE_2023,
        STATE_SHAPEFILE_2015,
    ])
    def test_all_shapefile_paths_are_strings(self, path_var: str) -> None:
        """All shapefile path constants should be strings."""
        assert isinstance(path_var, str)
        assert len(path_var) > 0

    def test_paths_use_os_path_join(self) -> None:
        """Paths should use the correct OS directory separator."""
        for path in [
            RAW_DATA_DIR, BOUNDARIES_DIR, MAPS_DIR, LAYOUTS_DIR,
            RAW_CSV_2015, RAW_CSV_2020, RAW_CSV_2023,
            TRACT_SHAPEFILE_2015, TRACT_SHAPEFILE_2020, TRACT_SHAPEFILE_2023,
            STATE_SHAPEFILE_2015,
        ]:
            assert os.sep in path, f"Path missing OS separator: {path}"

    def test_csv_paths_end_with_csv(self) -> None:
        """CSV file paths should have .csv extension."""
        for path in [RAW_CSV_2015, RAW_CSV_2020, RAW_CSV_2023]:
            assert path.endswith(".csv"), f"Expected .csv extension: {path}"

    def test_shapefile_paths_end_with_shp(self) -> None:
        """Shapefile paths should have .shp extension."""
        for path in [
            TRACT_SHAPEFILE_2015, TRACT_SHAPEFILE_2020,
            TRACT_SHAPEFILE_2023, STATE_SHAPEFILE_2015,
        ]:
            assert path.endswith(".shp"), f"Expected .shp extension: {path}"

    def test_output_dirs_are_under_project_root(self) -> None:
        """MAPS_DIR and LAYOUTS_DIR should be under PROJECT_ROOT."""
        assert MAPS_DIR.startswith(PROJECT_ROOT)
        assert LAYOUTS_DIR.startswith(PROJECT_ROOT)
