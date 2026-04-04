"""Tests for scripts/visualize_geospatial_data.py.

Uses synthetic GeoDataFrames with simple geometries and mocks plt.show()
to prevent display during test runs. All file I/O uses pytest's tmp_path.
"""

import os
from typing import Dict
from unittest.mock import patch

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import pytest
from shapely.geometry import box

from scripts.visualize_geospatial_data import (
    create_heating_fuel_grid,
    create_heating_fuel_map,
    create_legend_elements,
    detect_state_column,
    FUEL_COLORS,
    save_figure,
    split_state_boundaries,
)


# ============================================================================
# HELPER FIXTURES (visualization-specific)
# ============================================================================


@pytest.fixture(autouse=True)
def _close_plots():
    """Close all matplotlib figures after each test to free memory."""
    yield
    plt.close("all")


def _make_tract_gdf(states: list[str], fuel_simples: list[str]) -> gpd.GeoDataFrame:
    """Build a minimal tract GeoDataFrame ready for plotting."""
    n = len(states)
    geometries = [box(i, 0, i + 1, 1) for i in range(n)]
    colors = [FUEL_COLORS.get(f, "#cccccc") for f in fuel_simples]
    return gpd.GeoDataFrame(
        {
            "STUSAB": states,
            "Dom_Fuel_Simple": fuel_simples,
            "color": colors,
        },
        geometry=geometries,
        crs="EPSG:5070",
    )


def _make_states_gdf(states: list[str]) -> gpd.GeoDataFrame:
    """Build a minimal states GeoDataFrame with STUSPS column."""
    geometries = [box(i * 2, 2, i * 2 + 2, 4) for i in range(len(states))]
    return gpd.GeoDataFrame(
        {"STUSPS": states},
        geometry=geometries,
        crs="EPSG:5070",
    )


@pytest.fixture
def viz_conus_gdf() -> gpd.GeoDataFrame:
    """Tract GeoDataFrame for CONUS (no AK/HI)."""
    states = ["PA", "AL", "OH", "TX", "NY", "IL", "WV", "AZ", "ME"]
    fuels = [
        "Natural_Gas", "Electricity", "Other", "No_Fuel_Missing",
        "Natural_Gas", "Natural_Gas", "Other", "Other", "Fuel_Oil",
    ]
    return _make_tract_gdf(states, fuels)


@pytest.fixture
def viz_alaska_gdf() -> gpd.GeoDataFrame:
    """Tract GeoDataFrame for Alaska."""
    return _make_tract_gdf(["AK"], ["Natural_Gas"])


@pytest.fixture
def viz_states_gdf() -> gpd.GeoDataFrame:
    """State boundaries GeoDataFrame for visualization tests."""
    return _make_states_gdf(
        ["PA", "AL", "OH", "TX", "NY", "IL", "WV", "AZ", "ME", "AK"]
    )


# ============================================================================
# TestHelperFunctions
# ============================================================================


class TestDetectStateColumn:
    """Tests for detect_state_column helper."""

    def test_detects_stusps(self) -> None:
        """Should detect STUSPS column."""
        gdf = gpd.GeoDataFrame({"STUSPS": ["PA"]}, geometry=[box(0, 0, 1, 1)])
        assert detect_state_column(gdf) == "STUSPS"

    def test_detects_stusab(self) -> None:
        """Should detect STUSAB column."""
        gdf = gpd.GeoDataFrame({"STUSAB": ["PA"]}, geometry=[box(0, 0, 1, 1)])
        assert detect_state_column(gdf) == "STUSAB"

    def test_raises_when_no_state_column(self) -> None:
        """Should raise ValueError when no recognized state column exists."""
        gdf = gpd.GeoDataFrame({"other": ["PA"]}, geometry=[box(0, 0, 1, 1)])
        with pytest.raises(ValueError, match="No state abbreviation column"):
            detect_state_column(gdf)


class TestSplitStateBoundaries:
    """Tests for split_state_boundaries helper."""

    def test_conus_excludes_ak_hi_pr(self, viz_states_gdf: gpd.GeoDataFrame) -> None:
        """CONUS result should exclude AK, HI, and PR."""
        conus, _ = split_state_boundaries(viz_states_gdf)
        assert "AK" not in conus["STUSPS"].values

    def test_alaska_only_contains_ak(self, viz_states_gdf: gpd.GeoDataFrame) -> None:
        """Alaska result should only contain AK."""
        _, alaska = split_state_boundaries(viz_states_gdf)
        assert (alaska["STUSPS"] == "AK").all()


class TestCreateLegendElements:
    """Tests for legend element creation."""

    def test_returns_list_of_patches(self) -> None:
        """Should return a list of 7 Patch elements."""
        patches = create_legend_elements()
        assert len(patches) == 7

    def test_labels_present(self) -> None:
        """All fuel type labels should be represented."""
        patches = create_legend_elements()
        labels = {p.get_label() for p in patches}
        assert "Natural Gas" in labels
        assert "Electricity" in labels


# ============================================================================
# TestCreateHeatingFuelMap
# ============================================================================


class TestCreateHeatingFuelMap:
    """Tests for single-year map creation."""

    @patch("scripts.visualize_geospatial_data.plt.show")
    def test_returns_two_paths(
        self,
        mock_show,
        viz_conus_gdf: gpd.GeoDataFrame,
        viz_alaska_gdf: gpd.GeoDataFrame,
        viz_states_gdf: gpd.GeoDataFrame,
        tmp_path,
    ) -> None:
        """Should return (png_path, pdf_path) tuple."""
        result = create_heating_fuel_map(
            viz_conus_gdf, viz_alaska_gdf, viz_states_gdf,
            year=2020, output_dir=str(tmp_path), show_plot=True, dpi=72,
        )
        assert isinstance(result, tuple)
        assert len(result) == 2

    @patch("scripts.visualize_geospatial_data.plt.show")
    def test_creates_png_file(
        self,
        mock_show,
        viz_conus_gdf: gpd.GeoDataFrame,
        viz_alaska_gdf: gpd.GeoDataFrame,
        viz_states_gdf: gpd.GeoDataFrame,
        tmp_path,
    ) -> None:
        """Should create a PNG file at the expected path."""
        png_path, _ = create_heating_fuel_map(
            viz_conus_gdf, viz_alaska_gdf, viz_states_gdf,
            year=2020, output_dir=str(tmp_path), show_plot=True, dpi=72,
        )
        assert os.path.isfile(png_path)
        assert png_path.endswith(".png")

    @patch("scripts.visualize_geospatial_data.plt.show")
    def test_creates_pdf_file(
        self,
        mock_show,
        viz_conus_gdf: gpd.GeoDataFrame,
        viz_alaska_gdf: gpd.GeoDataFrame,
        viz_states_gdf: gpd.GeoDataFrame,
        tmp_path,
    ) -> None:
        """Should create a PDF file at the expected path."""
        _, pdf_path = create_heating_fuel_map(
            viz_conus_gdf, viz_alaska_gdf, viz_states_gdf,
            year=2020, output_dir=str(tmp_path), show_plot=True, dpi=72,
        )
        assert os.path.isfile(pdf_path)
        assert pdf_path.endswith(".pdf")

    @patch("scripts.visualize_geospatial_data.plt.show")
    def test_filename_contains_year(
        self,
        mock_show,
        viz_conus_gdf: gpd.GeoDataFrame,
        viz_alaska_gdf: gpd.GeoDataFrame,
        viz_states_gdf: gpd.GeoDataFrame,
        tmp_path,
    ) -> None:
        """Output filename should contain the year parameter."""
        png_path, pdf_path = create_heating_fuel_map(
            viz_conus_gdf, viz_alaska_gdf, viz_states_gdf,
            year=2023, output_dir=str(tmp_path), show_plot=True, dpi=72,
        )
        assert "2023" in os.path.basename(png_path)
        assert "2023" in os.path.basename(pdf_path)

    def test_show_plot_false_no_display(
        self,
        viz_conus_gdf: gpd.GeoDataFrame,
        viz_alaska_gdf: gpd.GeoDataFrame,
        viz_states_gdf: gpd.GeoDataFrame,
        tmp_path,
    ) -> None:
        """Setting show_plot=False should not call plt.show()."""
        with patch("scripts.visualize_geospatial_data.plt.show") as mock_show:
            create_heating_fuel_map(
                viz_conus_gdf, viz_alaska_gdf, viz_states_gdf,
                year=2020, output_dir=str(tmp_path), show_plot=False, dpi=72,
            )
            mock_show.assert_not_called()

    @patch("scripts.visualize_geospatial_data.plt.show")
    def test_handles_empty_alaska(
        self,
        mock_show,
        viz_conus_gdf: gpd.GeoDataFrame,
        viz_states_gdf: gpd.GeoDataFrame,
        tmp_path,
    ) -> None:
        """Should work when Alaska GeoDataFrame is empty."""
        empty_ak = _make_tract_gdf([], [])
        empty_ak = empty_ak.set_crs("EPSG:5070")
        png_path, pdf_path = create_heating_fuel_map(
            viz_conus_gdf, empty_ak, viz_states_gdf,
            year=2020, output_dir=str(tmp_path), show_plot=True, dpi=72,
        )
        assert os.path.isfile(png_path)


# ============================================================================
# TestCreateHeatingFuelGrid
# ============================================================================


class TestCreateHeatingFuelGrid:
    """Tests for multi-year grid creation."""

    def _build_gdf_dict(
        self,
        viz_conus_gdf: gpd.GeoDataFrame,
        viz_alaska_gdf: gpd.GeoDataFrame,
        years: list[int],
    ) -> Dict[int, Dict[str, gpd.GeoDataFrame]]:
        """Build gdf_dict in the expected format."""
        return {
            yr: {"conus": viz_conus_gdf, "alaska": viz_alaska_gdf}
            for yr in years
        }

    @patch("scripts.visualize_geospatial_data.plt.show")
    def test_returns_two_paths(
        self,
        mock_show,
        viz_conus_gdf: gpd.GeoDataFrame,
        viz_alaska_gdf: gpd.GeoDataFrame,
        viz_states_gdf: gpd.GeoDataFrame,
        tmp_path,
    ) -> None:
        """Should return (png_path, pdf_path) tuple."""
        gdf_dict = self._build_gdf_dict(viz_conus_gdf, viz_alaska_gdf, [2015, 2020, 2023])
        result = create_heating_fuel_grid(
            gdf_dict, viz_states_gdf, str(tmp_path),
            years=[2015, 2020, 2023], dpi=72,
        )
        assert isinstance(result, tuple)
        assert len(result) == 2

    @patch("scripts.visualize_geospatial_data.plt.show")
    def test_creates_files(
        self,
        mock_show,
        viz_conus_gdf: gpd.GeoDataFrame,
        viz_alaska_gdf: gpd.GeoDataFrame,
        viz_states_gdf: gpd.GeoDataFrame,
        tmp_path,
    ) -> None:
        """Should create PNG and PDF files."""
        gdf_dict = self._build_gdf_dict(viz_conus_gdf, viz_alaska_gdf, [2015, 2020, 2023])
        png_path, pdf_path = create_heating_fuel_grid(
            gdf_dict, viz_states_gdf, str(tmp_path),
            years=[2015, 2020, 2023], dpi=72,
        )
        assert os.path.isfile(png_path)
        assert os.path.isfile(pdf_path)

    @patch("scripts.visualize_geospatial_data.plt.show")
    def test_three_panel_layout(
        self,
        mock_show,
        viz_conus_gdf: gpd.GeoDataFrame,
        viz_alaska_gdf: gpd.GeoDataFrame,
        viz_states_gdf: gpd.GeoDataFrame,
        tmp_path,
    ) -> None:
        """Grid should create files when years=[2015, 2020, 2023]."""
        gdf_dict = self._build_gdf_dict(viz_conus_gdf, viz_alaska_gdf, [2015, 2020, 2023])
        png_path, _ = create_heating_fuel_grid(
            gdf_dict, viz_states_gdf, str(tmp_path),
            years=[2015, 2020, 2023], dpi=72,
        )
        assert "2015_2023" in os.path.basename(png_path)

    @patch("scripts.visualize_geospatial_data.plt.show")
    def test_custom_years_subset(
        self,
        mock_show,
        viz_conus_gdf: gpd.GeoDataFrame,
        viz_alaska_gdf: gpd.GeoDataFrame,
        viz_states_gdf: gpd.GeoDataFrame,
        tmp_path,
    ) -> None:
        """Should work with a subset of years like [2015, 2023]."""
        gdf_dict = self._build_gdf_dict(viz_conus_gdf, viz_alaska_gdf, [2015, 2023])
        png_path, pdf_path = create_heating_fuel_grid(
            gdf_dict, viz_states_gdf, str(tmp_path),
            years=[2015, 2023], dpi=72,
        )
        assert os.path.isfile(png_path)
        assert "2015_2023" in os.path.basename(png_path)

    @patch("scripts.visualize_geospatial_data.plt.show")
    def test_grid_missing_year_raises_error(
        self,
        mock_show,
        viz_conus_gdf: gpd.GeoDataFrame,
        viz_alaska_gdf: gpd.GeoDataFrame,
        viz_states_gdf: gpd.GeoDataFrame,
        tmp_path,
    ) -> None:
        """Requesting a year not in gdf_dict should raise ValueError."""
        gdf_dict = self._build_gdf_dict(viz_conus_gdf, viz_alaska_gdf, [2020])
        with pytest.raises(ValueError, match="2025"):
            create_heating_fuel_grid(
                gdf_dict, viz_states_gdf, str(tmp_path),
                years=[2025], dpi=72,
            )


# ============================================================================
# TestSaveFigure
# ============================================================================


class TestSaveFigure:
    """Tests for the save_figure utility."""

    def test_saves_png_and_pdf(self, tmp_path) -> None:
        """Should create both PNG and PDF files."""
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        png, pdf = save_figure(fig, str(tmp_path), "test_out", dpi=72, show_plot=False)
        assert os.path.isfile(png)
        assert os.path.isfile(pdf)

    def test_show_plot_calls_plt_show(self, tmp_path) -> None:
        """show_plot=True should call plt.show()."""
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        with patch("scripts.visualize_geospatial_data.plt.show") as mock_show:
            save_figure(fig, str(tmp_path), "test_show", dpi=72, show_plot=True)
            mock_show.assert_called_once()
