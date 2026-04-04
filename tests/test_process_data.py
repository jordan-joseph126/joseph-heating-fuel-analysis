"""Tests for scripts/process_data.py.

Covers process_heating_fuel_data, calculate_cv, flag_unreliable_tracts,
print_cv_summary, prepare_geodataframe, and FUEL_COLORS.
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import pytest
from typing import Dict

from scripts.process_data import (
    calculate_cv,
    flag_unreliable_tracts,
    FUEL_COLORS,
    prepare_geodataframe,
    print_cv_summary,
    process_heating_fuel_data,
    simplify_fuel_categories,
)


# ============================================================================
# Expected column lists (derived from the source code)
# ============================================================================

FUEL_COLUMNS = [
    "Natural_Gas", "Propane", "Electricity", "Fuel_Oil",
    "Coal", "Wood", "Solar", "Other", "No_Fuel",
]

METADATA_COLUMNS = [
    "GISJOIN", "YEAR", "STUSAB", "STATE", "STATEA",
    "COUNTY", "COUNTYA", "TRACTA", "GEOID", "County_Name",
]

ESTIMATE_COLUMNS = ["Total_Housing_Units"] + FUEL_COLUMNS

MOE_COLUMNS = [f"MOE_{c}" for c in ESTIMATE_COLUMNS]

PCT_COLUMNS = [f"Pct_{c}" for c in FUEL_COLUMNS]

DERIVED_COLUMNS = [
    "FIPS_Code", "Data_Quality_Check",
    *PCT_COLUMNS,
    "Has_Dom_Tie", "Dom_Fuel_Type", "Dom_Fuel_Count", "Dom_Fuel_Pct",
]

ALL_45_COLUMNS = METADATA_COLUMNS + ESTIMATE_COLUMNS + MOE_COLUMNS + DERIVED_COLUMNS


# ============================================================================
# TestProcessHeatingFuelData
# ============================================================================


class TestProcessHeatingFuelData:
    """Tests for the main data processing function."""

    def test_returns_dataframe(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Function should return a pandas DataFrame."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        assert isinstance(result, pd.DataFrame)

    @pytest.mark.parametrize("year,fixture_name", [
        (2015, "raw_nhgis_dataframe_2015"),
        (2020, "raw_nhgis_dataframe_2020"),
        (2023, "raw_nhgis_dataframe_2023"),
    ])
    def test_column_renaming(self, year: int, fixture_name: str, request: pytest.FixtureRequest) -> None:
        """Estimate columns should be renamed to human-readable names for each year."""
        df = request.getfixturevalue(fixture_name)
        result = process_heating_fuel_data(df, year, include_moe=True)
        for col in ESTIMATE_COLUMNS:
            assert col in result.columns, f"Missing column {col} for year {year}"

    def test_all_expected_columns_present(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Output should contain all 45 expected columns when include_moe=True."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020, include_moe=True)
        for col in ALL_45_COLUMNS:
            assert col in result.columns, f"Missing column: {col}"
        assert len(result.columns) == 45

    def test_moe_columns_present_by_default(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """MOE columns should be included by default (include_moe=True)."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        for col in MOE_COLUMNS:
            assert col in result.columns, f"Missing MOE column: {col}"

    def test_moe_columns_absent_when_disabled(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """MOE columns should NOT be present when include_moe=False."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020, include_moe=False)
        for col in MOE_COLUMNS:
            assert col not in result.columns, f"Unexpected MOE column: {col}"

    def test_backward_compatibility_no_moe_arg(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Calling without include_moe argument should work (default True)."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        assert "MOE_Total_Housing_Units" in result.columns

    def test_percentage_calculation_correctness(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Pct_{FUEL} should equal round((FUEL / Total_Housing_Units) * 100, 1)."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        # Row 0: PA — Natural_Gas=700, Total=1000 → 70.0%
        row = result.iloc[0]
        assert row["Pct_Natural_Gas"] == pytest.approx(70.0, abs=0.1)

    def test_percentages_sum_to_approximately_100(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """All fuel percentages should sum to ~100% for valid tracts."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        valid = result[result["Data_Quality_Check"] == "Valid_Data"]
        pct_sum = valid[PCT_COLUMNS].sum(axis=1)
        for idx, val in pct_sum.items():
            assert val == pytest.approx(100.0, abs=1.0), (
                f"Row {idx}: percentages sum to {val}"
            )

    def test_dominant_fuel_identification(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Dom_Fuel_Type should be the fuel with the highest count."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        # Row 0: Natural_Gas=700 is highest
        assert result.iloc[0]["Dom_Fuel_Type"] == "Natural_Gas"
        # Row 1: Electricity=1074 is highest
        assert result.iloc[1]["Dom_Fuel_Type"] == "Electricity"
        # Row 11: Fuel_Oil=500 is highest
        assert result.iloc[11]["Dom_Fuel_Type"] == "Fuel_Oil"

    def test_dominant_fuel_tie_handling(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """When two fuels tie, Dom_Fuel_Type should be 'Tie' and Has_Dom_Tie True."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        # Row 2: Natural_Gas=400, Electricity=400 — tie
        row = result.iloc[2]
        assert row["Dom_Fuel_Type"] == "Tie"
        assert bool(row["Has_Dom_Tie"]) is True

    def test_dominant_fuel_count_and_pct(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Dom_Fuel_Count and Dom_Fuel_Pct should match the dominant fuel."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        # Row 0: Natural_Gas=700, Total=1000 → count=700, pct=70.0
        row = result.iloc[0]
        assert row["Dom_Fuel_Count"] == pytest.approx(700.0)
        assert row["Dom_Fuel_Pct"] == pytest.approx(70.0, abs=0.1)

    def test_dominant_fuel_count_nan_for_tie(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Dom_Fuel_Count and Dom_Fuel_Pct should be NaN for ties."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        row = result.iloc[2]  # tie row
        assert pd.isna(row["Dom_Fuel_Count"])
        assert pd.isna(row["Dom_Fuel_Pct"])

    def test_data_quality_flag_valid_tract(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Data_Quality_Check should be 'Valid_Data' for tracts with Total > 0."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        assert result.iloc[0]["Data_Quality_Check"] == "Valid_Data"

    def test_data_quality_flag_zero_total(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Data_Quality_Check should be 'Insufficient_Data' for Total == 0."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        assert result.iloc[3]["Data_Quality_Check"] == "Insufficient_Data"

    def test_data_quality_flag_nan_total(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Data_Quality_Check should be 'Insufficient_Data' for NaN Total."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        assert result.iloc[4]["Data_Quality_Check"] == "Insufficient_Data"

    def test_fips_code_extraction(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """FIPS_Code should be the last 11 characters of GEOID."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        # Row 0: GEOID=14000US42001010100 → FIPS=42001010100
        assert result.iloc[0]["FIPS_Code"] == "42001010100"
        assert len(result.iloc[0]["FIPS_Code"]) == 11

    def test_invalid_year_raises_error(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Passing an unsupported year should raise KeyError."""
        with pytest.raises(KeyError, match="2010"):
            process_heating_fuel_data(raw_nhgis_dataframe_2020, 2010)

    def test_preserves_row_count(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Output should have the same number of rows as input."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        assert len(result) == len(raw_nhgis_dataframe_2020)

    def test_year_column_set_correctly(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """The YEAR column in output should reflect the raw data."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        assert (result["YEAR"] == 2020).all()

    @pytest.mark.parametrize("year,fixture_name", [
        (2015, "raw_nhgis_dataframe_2015"),
        (2020, "raw_nhgis_dataframe_2020"),
        (2023, "raw_nhgis_dataframe_2023"),
    ])
    def test_all_three_years_process_successfully(
        self, year: int, fixture_name: str, request: pytest.FixtureRequest
    ) -> None:
        """All three years should process without error."""
        df = request.getfixturevalue(fixture_name)
        result = process_heating_fuel_data(df, year, include_moe=True)
        assert len(result) > 0

    def test_rare_fuel_dominant(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Rare fuels (Coal, Solar) should be correctly identified as dominant."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        # Row 9: Coal=60 is highest
        assert result.iloc[9]["Dom_Fuel_Type"] == "Coal"
        # Row 10: Solar=50 is highest
        assert result.iloc[10]["Dom_Fuel_Type"] == "Solar"

    def test_no_data_dom_fuel_for_zero_total(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Tracts with 0 total housing units get Dom_Fuel_Type='No_Data'."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        assert result.iloc[3]["Dom_Fuel_Type"] == "No_Data"

    def test_no_data_dom_fuel_for_nan_total(self, raw_nhgis_dataframe_2020: pd.DataFrame) -> None:
        """Tracts with NaN total housing units get Dom_Fuel_Type='No_Data'."""
        result = process_heating_fuel_data(raw_nhgis_dataframe_2020, 2020)
        assert result.iloc[4]["Dom_Fuel_Type"] == "No_Data"


# ============================================================================
# TestCalculateCV
# ============================================================================


class TestCalculateCV:
    """Tests for the coefficient of variation calculation."""

    def test_basic_calculation(self) -> None:
        """CV should equal (MOE / 1.645) / estimate."""
        est = pd.Series([1000.0])
        moe = pd.Series([164.5])
        result = calculate_cv(est, moe)
        assert result.iloc[0] == pytest.approx(0.1, abs=1e-6)

    def test_returns_series(self) -> None:
        """Should return a pandas Series."""
        result = calculate_cv(pd.Series([100.0]), pd.Series([50.0]))
        assert isinstance(result, pd.Series)

    def test_zero_estimate_returns_nan(self) -> None:
        """CV should be NaN when estimate is 0."""
        result = calculate_cv(pd.Series([0.0]), pd.Series([50.0]))
        assert pd.isna(result.iloc[0])

    def test_nan_estimate_returns_nan(self) -> None:
        """CV should be NaN when estimate is NaN."""
        result = calculate_cv(pd.Series([np.nan]), pd.Series([50.0]))
        assert pd.isna(result.iloc[0])

    def test_nan_moe_returns_nan(self) -> None:
        """CV should be NaN when MOE is NaN."""
        result = calculate_cv(pd.Series([100.0]), pd.Series([np.nan]))
        assert pd.isna(result.iloc[0])

    def test_zero_moe_positive_estimate_returns_zero(self) -> None:
        """CV should be 0.0 when MOE=0 and estimate>0."""
        result = calculate_cv(pd.Series([500.0]), pd.Series([0.0]))
        assert result.iloc[0] == pytest.approx(0.0)

    def test_both_zero_returns_nan(self) -> None:
        """CV should be NaN when both estimate and MOE are 0."""
        result = calculate_cv(pd.Series([0.0]), pd.Series([0.0]))
        assert pd.isna(result.iloc[0])

    def test_high_moe_relative_to_estimate(self) -> None:
        """Small estimate with large MOE should produce CV > 1.0."""
        result = calculate_cv(pd.Series([10.0]), pd.Series([50.0]))
        expected = (50.0 / 1.645) / 10.0  # ≈ 3.04
        assert result.iloc[0] == pytest.approx(expected, rel=1e-3)
        assert result.iloc[0] > 1.0

    def test_vectorized_on_series(self) -> None:
        """Should work on pandas Series with multiple values."""
        est = pd.Series([1000.0, 500.0, 200.0, 0.0, 100.0])
        moe = pd.Series([164.5, 82.25, 100.0, 50.0, 0.0])

        result = calculate_cv(est, moe)
        assert len(result) == 5
        assert result.iloc[0] == pytest.approx(0.1, abs=1e-4)
        assert pd.isna(result.iloc[3])  # zero estimate
        assert result.iloc[4] == pytest.approx(0.0)  # zero MOE

    def test_preserves_index(self) -> None:
        """Output Series should have the same index as input."""
        idx = pd.Index([10, 20, 30])
        est = pd.Series([100.0, 200.0, 300.0], index=idx)
        moe = pd.Series([10.0, 20.0, 30.0], index=idx)
        result = calculate_cv(est, moe)
        assert list(result.index) == [10, 20, 30]

    def test_negative_moe_handled(self) -> None:
        """Negative MOE values should compute without crashing."""
        result = calculate_cv(pd.Series([100.0]), pd.Series([-50.0]))
        # Should produce a numeric result (negative CV) — not crash
        assert isinstance(result.iloc[0], (float, np.floating))


# ============================================================================
# TestFlagUnreliableTracts
# ============================================================================


class TestFlagUnreliableTracts:
    """Tests for the reliability flagging function."""

    def test_returns_dataframe(self, processed_dataframe: pd.DataFrame) -> None:
        """Should return a DataFrame."""
        result = flag_unreliable_tracts(processed_dataframe)
        assert isinstance(result, pd.DataFrame)

    def test_adds_cv_columns(self, processed_dataframe: pd.DataFrame) -> None:
        """Should add CV_Total_Housing_Units and CV_Dom_Fuel columns."""
        result = flag_unreliable_tracts(processed_dataframe)
        assert "CV_Total_Housing_Units" in result.columns
        assert "CV_Dom_Fuel" in result.columns

    def test_adds_flag_columns(self, processed_dataframe: pd.DataFrame) -> None:
        """Should add Flag_Unreliable_Total and Flag_Unreliable_Dom_Fuel columns."""
        result = flag_unreliable_tracts(processed_dataframe)
        assert "Flag_Unreliable_Total" in result.columns
        assert "Flag_Unreliable_Dom_Fuel" in result.columns

    def test_preserves_existing_columns(self, processed_dataframe: pd.DataFrame) -> None:
        """Should not remove any existing columns from the input."""
        original_cols = set(processed_dataframe.columns)
        result = flag_unreliable_tracts(processed_dataframe)
        assert original_cols.issubset(set(result.columns))

    def test_preserves_row_count(self, processed_dataframe: pd.DataFrame) -> None:
        """Output should have the same number of rows as input."""
        result = flag_unreliable_tracts(processed_dataframe)
        assert len(result) == len(processed_dataframe)

    def test_default_threshold_is_030(self, processed_dataframe: pd.DataFrame) -> None:
        """Default cv_threshold should be 0.30."""
        result_default = flag_unreliable_tracts(processed_dataframe)
        result_explicit = flag_unreliable_tracts(processed_dataframe, cv_threshold=0.30)
        pd.testing.assert_frame_equal(result_default, result_explicit)

    def test_custom_threshold(self, processed_dataframe: pd.DataFrame) -> None:
        """Changing cv_threshold should change which tracts are flagged."""
        strict = flag_unreliable_tracts(processed_dataframe, cv_threshold=0.01)
        lenient = flag_unreliable_tracts(processed_dataframe, cv_threshold=10.0)
        assert strict["Flag_Unreliable_Total"].sum() >= lenient["Flag_Unreliable_Total"].sum()

    def test_flag_true_when_cv_exceeds_threshold(self, processed_dataframe: pd.DataFrame) -> None:
        """Flag should be True when CV > threshold."""
        result = flag_unreliable_tracts(processed_dataframe, cv_threshold=0.30)
        # Row 5 (NY): very small counts, high CV → should be flagged
        ny_row = result.iloc[5]
        if not pd.isna(ny_row["CV_Total_Housing_Units"]):
            assert ny_row["CV_Total_Housing_Units"] > 0.30
            assert ny_row["Flag_Unreliable_Total"] is True or ny_row["Flag_Unreliable_Total"] == True

    def test_flag_false_when_cv_below_threshold(self, processed_dataframe: pd.DataFrame) -> None:
        """Flag should be False when CV <= threshold."""
        result = flag_unreliable_tracts(processed_dataframe, cv_threshold=0.30)
        # Row 6 (IL): large counts, low CV → should NOT be flagged
        il_row = result.iloc[6]
        assert il_row["CV_Total_Housing_Units"] < 0.30
        assert bool(il_row["Flag_Unreliable_Total"]) is False

    def test_flag_nan_cv_not_flagged(self, processed_dataframe: pd.DataFrame) -> None:
        """Tracts with NaN CV should NOT be flagged as unreliable."""
        result = flag_unreliable_tracts(processed_dataframe, cv_threshold=0.30)
        # Rows with NaN Total (row 4) should have NaN CV
        nan_cv = result[result["CV_Total_Housing_Units"].isna()]
        if len(nan_cv) > 0:
            # NaN > threshold evaluates to False in numpy
            assert not nan_cv["Flag_Unreliable_Total"].any()

    def test_dominant_fuel_cv_uses_correct_moe(self, processed_dataframe: pd.DataFrame) -> None:
        """CV_Dom_Fuel should use MOE corresponding to each tract's Dom_Fuel_Type."""
        result = flag_unreliable_tracts(processed_dataframe)
        # Row 0: Dom_Fuel_Type = Natural_Gas → should use MOE_Natural_Gas
        row_0 = result.iloc[0]
        if row_0["Dom_Fuel_Type"] == "Natural_Gas" and not pd.isna(row_0["Dom_Fuel_Count"]):
            expected_cv = calculate_cv(
                pd.Series([row_0["Dom_Fuel_Count"]]),
                pd.Series([row_0["MOE_Natural_Gas"]]),
            ).iloc[0]
            assert row_0["CV_Dom_Fuel"] == pytest.approx(expected_cv, rel=1e-6)

    def test_raises_error_without_moe_columns(self) -> None:
        """Should raise ValueError if MOE columns are missing."""
        df_no_moe = pd.DataFrame({
            "Total_Housing_Units": [100],
            "Dom_Fuel_Type": ["Natural_Gas"],
            "Dom_Fuel_Count": [70],
        })
        with pytest.raises(ValueError, match="MOE"):
            flag_unreliable_tracts(df_no_moe)

    def test_stricter_threshold_flags_more(self, processed_dataframe: pd.DataFrame) -> None:
        """A stricter threshold should flag more tracts than a lenient one."""
        strict = flag_unreliable_tracts(processed_dataframe, cv_threshold=0.05)
        lenient = flag_unreliable_tracts(processed_dataframe, cv_threshold=0.50)
        assert strict["Flag_Unreliable_Total"].sum() >= lenient["Flag_Unreliable_Total"].sum()


# ============================================================================
# TestPrintCVSummary
# ============================================================================


class TestPrintCVSummary:
    """Tests for the CV summary display function."""

    def test_returns_dataframe(self, flagged_dataframe: pd.DataFrame) -> None:
        """Should return a summary DataFrame."""
        result = print_cv_summary(flagged_dataframe)
        assert isinstance(result, pd.DataFrame)

    def test_output_has_expected_thresholds(self, flagged_dataframe: pd.DataFrame) -> None:
        """Summary should include a row for each default threshold."""
        result = print_cv_summary(flagged_dataframe)
        assert len(result) == 4  # default [0.15, 0.20, 0.30, 0.40]

    def test_custom_thresholds(self, flagged_dataframe: pd.DataFrame) -> None:
        """Passing custom thresholds should be reflected in output."""
        result = print_cv_summary(flagged_dataframe, thresholds=[0.10, 0.50])
        assert len(result) == 2
        assert "CV > 0.10" in result["Threshold"].values
        assert "CV > 0.50" in result["Threshold"].values

    def test_flagged_counts_are_nonnegative(self, flagged_dataframe: pd.DataFrame) -> None:
        """Flagged counts should be >= 0."""
        result = print_cv_summary(flagged_dataframe)
        assert (result["Total_Flagged"] >= 0).all()
        assert (result["Dom_Flagged"] >= 0).all()

    def test_flagged_counts_increase_with_stricter_threshold(
        self, flagged_dataframe: pd.DataFrame
    ) -> None:
        """More tracts should be flagged at CV>0.15 than at CV>0.40."""
        result = print_cv_summary(flagged_dataframe, thresholds=[0.15, 0.40])
        strict = result[result["Threshold"] == "CV > 0.15"]["Total_Flagged"].iloc[0]
        lenient = result[result["Threshold"] == "CV > 0.40"]["Total_Flagged"].iloc[0]
        assert strict >= lenient

    def test_prints_output(self, flagged_dataframe: pd.DataFrame, capsys: pytest.CaptureFixture) -> None:
        """Function should print to stdout."""
        print_cv_summary(flagged_dataframe)
        captured = capsys.readouterr()
        assert "CV Reliability Summary" in captured.out
        assert "Total tracts:" in captured.out

    def test_raises_error_without_cv_columns(self) -> None:
        """Should raise ValueError if CV columns are not present."""
        df = pd.DataFrame({"Total_Housing_Units": [100]})
        with pytest.raises(ValueError, match="not found"):
            print_cv_summary(df)


# ============================================================================
# TestPrepareGeodataframe
# ============================================================================


class TestPrepareGeodataframe:
    """Tests for geodataframe preparation."""

    def test_returns_three_element_tuple(
        self, mock_geodataframe: gpd.GeoDataFrame, processed_dataframe: pd.DataFrame
    ) -> None:
        """Should return (gdf_filtered, gdf_conus, gdf_alaska) tuple."""
        result = prepare_geodataframe(mock_geodataframe, processed_dataframe)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_gdf_filtered_excludes_hawaii(
        self, mock_geodataframe: gpd.GeoDataFrame, processed_dataframe: pd.DataFrame
    ) -> None:
        """gdf_filtered should not contain Hawaii tracts."""
        gdf_filtered, _, _ = prepare_geodataframe(mock_geodataframe, processed_dataframe)
        if "STUSAB" in gdf_filtered.columns:
            assert "HI" not in gdf_filtered["STUSAB"].values

    def test_gdf_conus_excludes_alaska(
        self, mock_geodataframe: gpd.GeoDataFrame, processed_dataframe: pd.DataFrame
    ) -> None:
        """gdf_conus should not contain Alaska tracts."""
        _, gdf_conus, _ = prepare_geodataframe(mock_geodataframe, processed_dataframe)
        if "STUSAB" in gdf_conus.columns:
            assert "AK" not in gdf_conus["STUSAB"].values

    def test_gdf_alaska_only_contains_alaska(
        self, mock_geodataframe: gpd.GeoDataFrame, processed_dataframe: pd.DataFrame
    ) -> None:
        """gdf_alaska should only contain Alaska tracts."""
        _, _, gdf_alaska = prepare_geodataframe(mock_geodataframe, processed_dataframe)
        if len(gdf_alaska) > 0:
            assert (gdf_alaska["STUSAB"] == "AK").all()

    def test_dom_fuel_simple_column_added(
        self, mock_geodataframe: gpd.GeoDataFrame, processed_dataframe: pd.DataFrame
    ) -> None:
        """Output should include a Dom_Fuel_Simple column."""
        gdf_filtered, _, _ = prepare_geodataframe(mock_geodataframe, processed_dataframe)
        assert "Dom_Fuel_Simple" in gdf_filtered.columns

    def test_color_column_added(
        self, mock_geodataframe: gpd.GeoDataFrame, processed_dataframe: pd.DataFrame
    ) -> None:
        """Output should include a color column."""
        gdf_filtered, _, _ = prepare_geodataframe(mock_geodataframe, processed_dataframe)
        assert "color" in gdf_filtered.columns

    def test_dom_fuel_simple_categories(
        self, mock_geodataframe: gpd.GeoDataFrame, processed_dataframe: pd.DataFrame
    ) -> None:
        """Dom_Fuel_Simple should only contain the 7 simplified categories."""
        valid_categories = {
            "Natural_Gas", "Electricity", "Fuel_Oil", "Propane",
            "Wood", "Other", "No_Fuel_Missing",
        }
        gdf_filtered, _, _ = prepare_geodataframe(mock_geodataframe, processed_dataframe)
        actual = set(gdf_filtered["Dom_Fuel_Simple"].dropna().unique())
        assert actual.issubset(valid_categories), f"Unexpected categories: {actual - valid_categories}"

    def test_coal_mapped_to_other(self) -> None:
        """Coal in Dom_Fuel_Type should become Other in Dom_Fuel_Simple."""
        assert simplify_fuel_categories("Coal") == "Other"

    def test_solar_mapped_to_other(self) -> None:
        """Solar in Dom_Fuel_Type should become Other in Dom_Fuel_Simple."""
        assert simplify_fuel_categories("Solar") == "Other"

    def test_tie_mapped_to_other(self) -> None:
        """Tie in Dom_Fuel_Type should become Other in Dom_Fuel_Simple."""
        assert simplify_fuel_categories("Tie") == "Other"

    def test_no_data_mapped_to_no_fuel_missing(self) -> None:
        """No_Data in Dom_Fuel_Type should become No_Fuel_Missing."""
        assert simplify_fuel_categories("No_Data") == "No_Fuel_Missing"

    def test_no_fuel_mapped_to_no_fuel_missing(self) -> None:
        """No_Fuel in Dom_Fuel_Type should become No_Fuel_Missing."""
        assert simplify_fuel_categories("No_Fuel") == "No_Fuel_Missing"

    def test_colors_match_fuel_colors_dict(
        self, mock_geodataframe: gpd.GeoDataFrame, processed_dataframe: pd.DataFrame
    ) -> None:
        """Each tract's color should come from the FUEL_COLORS dictionary."""
        gdf_filtered, _, _ = prepare_geodataframe(mock_geodataframe, processed_dataframe)
        valid_colors = set(FUEL_COLORS.values())
        non_null = gdf_filtered["color"].dropna()
        for color in non_null:
            assert color in valid_colors, f"Unexpected color: {color}"

    def test_merge_on_gisjoin(
        self, mock_geodataframe: gpd.GeoDataFrame, processed_dataframe: pd.DataFrame
    ) -> None:
        """Data should be merged using the GISJOIN column."""
        gdf_filtered, _, _ = prepare_geodataframe(mock_geodataframe, processed_dataframe)
        # If merge worked, processed columns should be in the result
        assert "Dom_Fuel_Type" in gdf_filtered.columns

    def test_exclude_states_parameter(
        self, mock_geodataframe: gpd.GeoDataFrame, processed_dataframe: pd.DataFrame
    ) -> None:
        """Passing exclude_states should remove those states."""
        gdf_filtered, _, _ = prepare_geodataframe(
            mock_geodataframe, processed_dataframe, exclude_states=["HI", "PR", "CA"]
        )
        if "STUSAB" in gdf_filtered.columns:
            assert "CA" not in gdf_filtered["STUSAB"].values


# ============================================================================
# TestFuelColors
# ============================================================================


class TestFuelColors:
    """Tests for the FUEL_COLORS constant."""

    def test_fuel_colors_is_dict(self) -> None:
        """FUEL_COLORS should be a dictionary."""
        assert isinstance(FUEL_COLORS, dict)

    def test_contains_all_simplified_fuel_types(self) -> None:
        """Should have keys for all 7 simplified fuel categories."""
        expected_keys = {
            "Natural_Gas", "Electricity", "Fuel_Oil", "Propane",
            "Wood", "Other", "No_Fuel_Missing",
        }
        assert set(FUEL_COLORS.keys()) == expected_keys

    def test_values_are_valid_colors(self) -> None:
        """All values should be valid matplotlib color specifications."""
        from matplotlib.colors import is_color_like

        for fuel, color in FUEL_COLORS.items():
            assert is_color_like(color), f"Invalid color for {fuel}: {color}"
