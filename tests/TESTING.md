# Pytest Test Suite Documentation

Comprehensive test suite for the Heating Fuel Analysis toolkit.

---

## Table of Contents
1. [Overview](#overview)
2. [Test Suite Structure](#test-suite-structure)
3. [Running the Tests](#running-the-tests)
   - [Basic Usage](#basic-usage)
   - [Verbose Output](#verbose-output)
   - [Coverage Report](#coverage-report)
   - [Running Individual Test Files](#running-individual-test-files)
   - [Running a Single Test Class or Function](#running-a-single-test-class-or-function)
4. [Test File Descriptions](#test-file-descriptions)
   - [conftest.py — Shared Fixtures](#conftestpy--shared-fixtures)
   - [test_process_data.py — Data Processing Tests](#test_process_datapy--data-processing-tests)
   - [test_visualize_geospatial.py — Visualization Tests](#test_visualize_geospatialpy--visualization-tests)
   - [test_config.py — Configuration Tests](#test_configpy--configuration-tests)
5. [Synthetic Test Data Design](#synthetic-test-data-design)
   - [NHGIS Column Prefixes by Year](#nhgis-column-prefixes-by-year)
   - [Scenario Coverage](#scenario-coverage)
6. [Adding New Tests](#adding-new-tests)
7. [Troubleshooting](#troubleshooting)

---

## Overview

This test suite validates all public functions and constants in the Heating Fuel Analysis toolkit using **synthetic test data only** — no real NHGIS CSV files or shapefiles are required. The suite is built with [pytest](https://docs.pytest.org/) and covers three modules:

| Module                              | Description                              |
|-------------------------------------|------------------------------------------|
| `scripts/process_data.py`           | Data processing, CV calculation, flagging |
| `scripts/visualize_geospatial_data.py` | Map creation and figure export          |
| `config.py`                         | File path constants and project structure |

**Current status:** 110 tests, all passing (~5 seconds on a typical machine).

| Test File                      | Tests | What It Covers                                                            |
|--------------------------------|------:|---------------------------------------------------------------------------|
| `test_config.py`               |    14 | Path constants, directory separators, file extensions                      |
| `test_process_data.py`         |    76 | Column renaming, percentages, dominant fuel, CV, flagging, geodataframes  |
| `test_visualize_geospatial.py` |    20 | Map creation, grid layout, file export, helper functions                   |

---

## Test Suite Structure

```
tests/
├── __init__.py                    # Package marker
├── conftest.py                    # Shared pytest fixtures (synthetic data)
├── test_process_data.py           # Tests for scripts/process_data.py
├── test_visualize_geospatial.py   # Tests for scripts/visualize_geospatial_data.py
└── test_config.py                 # Tests for config.py
```

---

## Running the Tests

### Prerequisites

Ensure the conda environment is active and pytest is installed:

```bash
conda activate joseph-heating-fuel-env
pip install pytest pytest-cov
```

All commands below assume you are in the project root directory (`joseph-heating-fuel-analysis/`).

### Basic Usage

```bash
python -m pytest tests/
```

### Verbose Output

Shows each test name and its pass/fail status:

```bash
python -m pytest tests/ -v --tb=short
```

### Coverage Report

Shows which lines in the source modules are exercised by the test suite:

```bash
python -m pytest tests/ --cov=scripts --cov=config --cov-report=term-missing
```

### Running Individual Test Files

```bash
# Only data processing tests
python -m pytest tests/test_process_data.py -v

# Only visualization tests
python -m pytest tests/test_visualize_geospatial.py -v

# Only configuration tests
python -m pytest tests/test_config.py -v
```

### Running a Single Test Class or Function

```bash
# All tests in a specific class
python -m pytest tests/test_process_data.py::TestCalculateCV -v

# A single test function
python -m pytest tests/test_process_data.py::TestProcessHeatingFuelData::test_percentages_sum_to_approximately_100 -v
```

---

## Test File Descriptions

### `conftest.py` — Shared Fixtures

This file defines reusable pytest fixtures that build small, controlled DataFrames and GeoDataFrames matching the NHGIS data format. Fixtures are automatically discovered by pytest and available to all test files in the `tests/` directory.

#### Fixtures Provided

| Fixture                      | Type              | Description                                                                                  |
|------------------------------|-------------------|----------------------------------------------------------------------------------------------|
| `raw_nhgis_dataframe_2015`   | `pd.DataFrame`    | 12-row synthetic NHGIS DataFrame with `ADQYE`/`ADQYM` column prefix (2015 data)             |
| `raw_nhgis_dataframe_2020`   | `pd.DataFrame`    | 12-row synthetic NHGIS DataFrame with `AMVDE`/`AMVDM` column prefix (2020 data)             |
| `raw_nhgis_dataframe_2023`   | `pd.DataFrame`    | 12-row synthetic NHGIS DataFrame with `ASUPE`/`ASUPM` column prefix (2023 data)             |
| `processed_dataframe`        | `pd.DataFrame`    | Result of `process_heating_fuel_data()` on 2020 raw data (all 45 columns, MOE included)     |
| `flagged_dataframe`          | `pd.DataFrame`    | Result of `flag_unreliable_tracts()` on the processed data (includes CV and flag columns)    |
| `mock_geodataframe`          | `gpd.GeoDataFrame` | 12 simple square polygons with `GISJOIN` column, CRS EPSG:5070                              |
| `mock_states_gdf`            | `gpd.GeoDataFrame` | 12 state boundaries with `STUSPS` column matching the synthetic tracts                      |
| `processed_geodataframe`     | `dict`            | Result of `prepare_geodataframe()` — keys: `'filtered'`, `'conus'`, `'alaska'`             |

Each raw NHGIS fixture contains 12 rows covering diverse analysis scenarios (see [Scenario Coverage](#scenario-coverage) below).

---

### `test_process_data.py` — Data Processing Tests

Contains 76 tests organized into 6 test classes covering every public function and constant in `scripts/process_data.py`.

#### `TestProcessHeatingFuelData` (22 tests)

Tests the main `process_heating_fuel_data(df, year, include_moe=True)` function.

| Test | What It Verifies |
|------|-----------------|
| `test_returns_dataframe` | Return type is `pd.DataFrame` |
| `test_column_renaming` (×3) | Estimate columns renamed correctly for 2015, 2020, and 2023 |
| `test_all_expected_columns_present` | All 45 expected columns are present when `include_moe=True` |
| `test_moe_columns_present_by_default` | MOE columns included when `include_moe` not specified |
| `test_moe_columns_absent_when_disabled` | MOE columns excluded when `include_moe=False` |
| `test_backward_compatibility_no_moe_arg` | Function works without explicitly passing `include_moe` |
| `test_percentage_calculation_correctness` | `Pct_Natural_Gas` = `round((Natural_Gas / Total) × 100, 1)` |
| `test_percentages_sum_to_approximately_100` | All fuel percentages sum to ~100% for valid tracts |
| `test_dominant_fuel_identification` | `Dom_Fuel_Type` matches the fuel with the highest count |
| `test_dominant_fuel_tie_handling` | Tied fuels produce `Dom_Fuel_Type='Tie'` and `Has_Dom_Tie=True` |
| `test_dominant_fuel_count_and_pct` | `Dom_Fuel_Count` and `Dom_Fuel_Pct` match the dominant fuel |
| `test_dominant_fuel_count_nan_for_tie` | Ties produce NaN for `Dom_Fuel_Count` and `Dom_Fuel_Pct` |
| `test_data_quality_flag_valid_tract` | `Data_Quality_Check='Valid_Data'` for tracts with Total > 0 |
| `test_data_quality_flag_zero_total` | `Data_Quality_Check='Insufficient_Data'` for Total == 0 |
| `test_data_quality_flag_nan_total` | `Data_Quality_Check='Insufficient_Data'` for NaN Total |
| `test_fips_code_extraction` | `FIPS_Code` is the last 11 characters of GEOID |
| `test_invalid_year_raises_error` | Unsupported year (e.g., 2010) raises `KeyError` |
| `test_preserves_row_count` | Output row count matches input |
| `test_year_column_set_correctly` | `YEAR` column reflects the input data |
| `test_all_three_years_process_successfully` (×3) | All three years process without error |
| `test_rare_fuel_dominant` | Coal and Solar correctly identified as dominant when highest |
| `test_no_data_dom_fuel_for_zero_total` | Zero-total tracts get `Dom_Fuel_Type='No_Data'` |
| `test_no_data_dom_fuel_for_nan_total` | NaN-total tracts get `Dom_Fuel_Type='No_Data'` |

#### `TestCalculateCV` (11 tests)

Tests the `calculate_cv(estimate, moe)` function (CV = (MOE / 1.645) / estimate).

| Test | What It Verifies |
|------|-----------------|
| `test_basic_calculation` | CV = 0.1 when estimate=1000, MOE=164.5 |
| `test_returns_series` | Return type is `pd.Series` |
| `test_zero_estimate_returns_nan` | Division by zero → NaN |
| `test_nan_estimate_returns_nan` | NaN propagation from estimate |
| `test_nan_moe_returns_nan` | NaN propagation from MOE |
| `test_zero_moe_positive_estimate_returns_zero` | Perfect reliability → CV=0.0 |
| `test_both_zero_returns_nan` | Both zero → NaN |
| `test_high_moe_relative_to_estimate` | Small estimate + large MOE → CV > 1.0 |
| `test_vectorized_on_series` | Works on multi-element Series |
| `test_preserves_index` | Output index matches input index |
| `test_negative_moe_handled` | Negative MOE (NHGIS special codes) does not crash |

#### `TestFlagUnreliableTracts` (13 tests)

Tests the `flag_unreliable_tracts(df, cv_threshold=0.30)` function.

| Test | What It Verifies |
|------|-----------------|
| `test_returns_dataframe` | Return type |
| `test_adds_cv_columns` | `CV_Total_Housing_Units` and `CV_Dom_Fuel` added |
| `test_adds_flag_columns` | `Flag_Unreliable_Total` and `Flag_Unreliable_Dom_Fuel` added |
| `test_preserves_existing_columns` | No original columns removed |
| `test_preserves_row_count` | Row count unchanged |
| `test_default_threshold_is_030` | Default matches explicit `cv_threshold=0.30` |
| `test_custom_threshold` | Different thresholds produce different flagging results |
| `test_flag_true_when_cv_exceeds_threshold` | High-CV tract (NY, small counts) flagged |
| `test_flag_false_when_cv_below_threshold` | Low-CV tract (IL, large counts) not flagged |
| `test_flag_nan_cv_not_flagged` | NaN CV tracts not flagged as unreliable |
| `test_dominant_fuel_cv_uses_correct_moe` | CV_Dom_Fuel uses the MOE matching Dom_Fuel_Type |
| `test_raises_error_without_moe_columns` | `ValueError` if MOE columns are missing |
| `test_stricter_threshold_flags_more` | Stricter threshold flags ≥ lenient count |

#### `TestPrintCVSummary` (7 tests)

Tests the `print_cv_summary(df, thresholds)` function.

| Test | What It Verifies |
|------|-----------------|
| `test_returns_dataframe` | Returns a summary DataFrame |
| `test_output_has_expected_thresholds` | Default 4 thresholds → 4 rows |
| `test_custom_thresholds` | Custom thresholds reflected in output |
| `test_flagged_counts_are_nonnegative` | All counts ≥ 0 |
| `test_flagged_counts_increase_with_stricter_threshold` | Stricter → more flagged |
| `test_prints_output` | Prints "CV Reliability Summary" to stdout (captured with `capsys`) |
| `test_raises_error_without_cv_columns` | `ValueError` if CV columns missing |

#### `TestPrepareGeodataframe` (14 tests)

Tests the `prepare_geodataframe(gdf_tracts, df_processed, exclude_states)` function and the `simplify_fuel_categories()` helper.

| Test | What It Verifies |
|------|-----------------|
| `test_returns_three_element_tuple` | Returns `(gdf_filtered, gdf_conus, gdf_alaska)` |
| `test_gdf_filtered_excludes_hawaii` | Hawaii removed from filtered output |
| `test_gdf_conus_excludes_alaska` | Alaska removed from CONUS output |
| `test_gdf_alaska_only_contains_alaska` | Alaska output contains only AK tracts |
| `test_dom_fuel_simple_column_added` | `Dom_Fuel_Simple` column present |
| `test_color_column_added` | `color` column present |
| `test_dom_fuel_simple_categories` | Only 7 valid simplified categories used |
| `test_coal_mapped_to_other` | Coal → Other |
| `test_solar_mapped_to_other` | Solar → Other |
| `test_tie_mapped_to_other` | Tie → Other |
| `test_no_data_mapped_to_no_fuel_missing` | No_Data → No_Fuel_Missing |
| `test_no_fuel_mapped_to_no_fuel_missing` | No_Fuel → No_Fuel_Missing |
| `test_colors_match_fuel_colors_dict` | Every color comes from `FUEL_COLORS` dictionary |
| `test_merge_on_gisjoin` | Merge on GISJOIN brings processed columns into GeoDataFrame |
| `test_exclude_states_parameter` | Custom `exclude_states` list removes specified states |

#### `TestFuelColors` (3 tests)

Tests the `FUEL_COLORS` constant dictionary.

| Test | What It Verifies |
|------|-----------------|
| `test_fuel_colors_is_dict` | Type is `dict` |
| `test_contains_all_simplified_fuel_types` | All 7 simplified fuel category keys present |
| `test_values_are_valid_colors` | All values pass `matplotlib.colors.is_color_like()` |

---

### `test_visualize_geospatial.py` — Visualization Tests

Contains 20 tests organized into 6 test classes. All tests mock `plt.show()` to prevent display during runs, and an `autouse` fixture calls `plt.close('all')` after every test to prevent memory leaks.

#### `TestDetectStateColumn` (3 tests)

| Test | What It Verifies |
|------|-----------------|
| `test_detects_stusps` | Finds `STUSPS` column |
| `test_detects_stusab` | Finds `STUSAB` column |
| `test_raises_when_no_state_column` | `ValueError` when no recognized column exists |

#### `TestSplitStateBoundaries` (2 tests)

| Test | What It Verifies |
|------|-----------------|
| `test_conus_excludes_ak_hi_pr` | CONUS result excludes AK |
| `test_alaska_only_contains_ak` | Alaska result contains only AK |

#### `TestCreateLegendElements` (2 tests)

| Test | What It Verifies |
|------|-----------------|
| `test_returns_list_of_patches` | Returns list of 7 Patch elements |
| `test_labels_present` | All fuel type labels represented |

#### `TestCreateHeatingFuelMap` (6 tests)

Tests the `create_heating_fuel_map()` function. Uses `tmp_path` for file output.

| Test | What It Verifies |
|------|-----------------|
| `test_returns_two_paths` | Returns `(png_path, pdf_path)` tuple |
| `test_creates_png_file` | PNG file exists on disk |
| `test_creates_pdf_file` | PDF file exists on disk |
| `test_filename_contains_year` | Year appears in output filename |
| `test_show_plot_false_no_display` | `plt.show()` not called when `show_plot=False` |
| `test_handles_empty_alaska` | Works when Alaska GeoDataFrame is empty |

#### `TestCreateHeatingFuelGrid` (5 tests)

Tests the `create_heating_fuel_grid()` function for multi-year grid maps.

| Test | What It Verifies |
|------|-----------------|
| `test_returns_two_paths` | Returns `(png_path, pdf_path)` tuple |
| `test_creates_files` | PNG and PDF files exist on disk |
| `test_three_panel_layout` | 3-year grid produces filename with year range |
| `test_custom_years_subset` | Works with 2-year subset `[2015, 2023]` |
| `test_grid_missing_year_raises_error` | `ValueError` for year not in `gdf_dict` |

#### `TestSaveFigure` (2 tests)

Tests the `save_figure()` utility function.

| Test | What It Verifies |
|------|-----------------|
| `test_saves_png_and_pdf` | Creates both PNG and PDF files |
| `test_show_plot_calls_plt_show` | `plt.show()` called when `show_plot=True` |

---

### `test_config.py` — Configuration Tests

Contains 14 tests in a single test class validating all path constants defined in `config.py`.

#### `TestConfig` (14 tests)

| Test | What It Verifies |
|------|-----------------|
| `test_project_root_is_absolute` | `PROJECT_ROOT` is an absolute path |
| `test_project_root_exists` | `PROJECT_ROOT` directory exists on disk |
| `test_raw_data_dir_defined` | `RAW_DATA_DIR` is a non-empty string |
| `test_all_csv_paths_are_strings` (×3) | `RAW_CSV_2015`, `RAW_CSV_2020`, `RAW_CSV_2023` are strings |
| `test_all_shapefile_paths_are_strings` (×4) | All shapefile path constants are strings |
| `test_paths_use_os_path_join` | Paths contain the correct OS directory separator |
| `test_csv_paths_end_with_csv` | CSV paths have `.csv` extension |
| `test_shapefile_paths_end_with_shp` | Shapefile paths have `.shp` extension |
| `test_output_dirs_are_under_project_root` | `MAPS_DIR` and `LAYOUTS_DIR` are under `PROJECT_ROOT` |

---

## Synthetic Test Data Design

All test data is generated programmatically in `conftest.py`. No real NHGIS data files or shapefiles are needed to run the test suite.

### NHGIS Column Prefixes by Year

The NHGIS assigns year-specific column prefixes to ACS Table B25040 data. The test fixtures use the exact prefixes from `scripts/process_data.py`:

| Year | Estimate Prefix | MOE Prefix | GEOID Column | Example Estimate Column |
|------|----------------|------------|--------------|------------------------|
| 2015 | `ADQYE`        | `ADQYM`    | `GEOID`      | `ADQYE001` (Total Housing Units) |
| 2020 | `AMVDE`        | `AMVDM`    | `GEOID`      | `AMVDE001` (Total Housing Units) |
| 2023 | `ASUPE`        | `ASUPM`    | `GEO_ID`     | `ASUPE001` (Total Housing Units) |

Column numbering follows ACS Table B25040:

| Suffix | Fuel Type            |
|--------|---------------------|
| `001`  | Total Housing Units  |
| `002`  | Natural Gas          |
| `003`  | Propane (LP Gas)     |
| `004`  | Electricity          |
| `005`  | Fuel Oil / Kerosene  |
| `006`  | Coal or Coke         |
| `007`  | Wood                 |
| `008`  | Solar Energy         |
| `009`  | Other Fuel           |
| `010`  | No Fuel Used         |

### Scenario Coverage

Each raw NHGIS fixture contains 12 rows representing diverse analysis scenarios:

| Row | State | Scenario                          | Key Characteristics                                      |
|-----|-------|-----------------------------------|----------------------------------------------------------|
| 0   | PA    | Natural gas dominant              | 700/1000 = 70% natural gas, low CV                       |
| 1   | AL    | Electricity dominant              | 1074/1408 = 76.3% electricity (matches real example tract)|
| 2   | OH    | Two-fuel tie                      | Natural_Gas=400, Electricity=400 → `Dom_Fuel_Type='Tie'` |
| 3   | TX    | Zero total housing units          | All values = 0 → `Data_Quality_Check='Insufficient_Data'`|
| 4   | CA    | NaN total housing units           | All values = NaN → `Data_Quality_Check='Insufficient_Data'`|
| 5   | NY    | Very small counts (high CV)       | Total=10, MOE=50 → CV > 0.30, flagged as unreliable     |
| 6   | IL    | Large counts (low CV)             | Total=5000, MOE=100 → CV < 0.30, reliable               |
| 7   | AK    | Alaska tract                      | Kept in `gdf_alaska`, excluded from `gdf_conus`          |
| 8   | HI    | Hawaii tract                      | Excluded by `prepare_geodataframe(exclude_states=['HI'])` |
| 9   | WV    | Coal dominant (rare fuel)         | Coal=60 is highest → `Dom_Fuel_Simple='Other'`           |
| 10  | AZ    | Solar dominant (rare fuel)        | Solar=50 is highest → `Dom_Fuel_Simple='Other'`          |
| 11  | ME    | Fuel oil dominant                 | Fuel_Oil=500/800 = 62.5%                                 |

GeoDataFrame fixtures use simple square polygons created with `shapely.geometry.box()` and CRS EPSG:5070 (Conus Albers Equal Area).

---

## Adding New Tests

### Adding a Test to an Existing File

1. Identify the appropriate test file and class for the function being tested.
2. Add a new `test_` method following the existing patterns.
3. Use fixtures from `conftest.py` where possible.
4. Run the full suite to confirm no regressions:
   ```bash
   python -m pytest tests/ -v --tb=short
   ```

### Adding a New Fixture

1. Add the fixture function to `tests/conftest.py` with the `@pytest.fixture` decorator.
2. Include a docstring describing what the fixture provides.
3. Use the fixture by name as a parameter in any test function.

### Conventions

- **Test functions** are named `test_<behavior_being_tested>`
- **Test classes** are named `Test<FunctionOrComponent>`
- Use `pytest.approx` for floating-point comparisons
- Use `pytest.raises` for expected exceptions
- Use `capsys` to capture and verify printed output
- Use `tmp_path` for any tests that create files
- Use `unittest.mock.patch` to mock `plt.show()` in visualization tests
- Every test function has a Google-style docstring
- Every test function has a return type hint of `-> None`

---

## Troubleshooting

### ISSUE 1: `ModuleNotFoundError: No module named 'pytest'`

**Cause:** pytest is not installed in the active environment.

**Solution:**
```bash
conda activate joseph-heating-fuel-env
pip install pytest pytest-cov
```

---

### ISSUE 2: `ModuleNotFoundError: No module named 'scripts'` or `'config'`

**Cause:** The project package is not installed in editable mode.

**Solution:**
```bash
conda activate joseph-heating-fuel-env
cd /path/to/joseph-heating-fuel-analysis
pip install -e .
```

---

### ISSUE 3: Visualization Tests Hang or Display Windows

**Cause:** `plt.show()` is being called during tests, opening interactive plot windows.

**Solution:** This should not occur — all visualization tests mock `plt.show()`. If it does happen, ensure you are running the latest version of the test files and that `unittest.mock.patch` is correctly intercepting calls.

---

### ISSUE 4: `DeprecationWarning: The 'shapely.geos' module is deprecated`

**Cause:** The installed version of geopandas references a deprecated `shapely.geos` module.

**Impact:** This is a harmless warning that does not affect test results. It will be resolved when the environment is updated to a newer version of geopandas.

---

### ISSUE 5: Tests Pass Locally but Fail in CI

**Possible causes:**
- Missing `pip install -e .` step in CI pipeline
- Different OS path separators (test_config.py assumes the OS it runs on)
- Missing geospatial dependencies (`geopandas`, `fiona`, `shapely`)

**Solution:** Ensure the CI pipeline includes:
```bash
conda env create -f environment.yml
conda activate joseph-heating-fuel-env
pip install -e .
pip install pytest pytest-cov
python -m pytest tests/ -v --tb=short
```

---
