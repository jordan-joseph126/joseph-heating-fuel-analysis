"""Shared pytest fixtures for heating fuel analysis tests.

Provides synthetic test data that mimics NHGIS format without requiring real
data files. Fixtures cover all three ACS survey periods (2015, 2020, 2023).
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import pytest
from shapely.geometry import box
from typing import Dict

from scripts.process_data import (
    process_heating_fuel_data,
    flag_unreliable_tracts,
    FUEL_COLORS,
)


# ============================================================================
# HELPERS
# ============================================================================

# Year-specific column prefixes extracted from scripts/process_data.py
_YEAR_CONFIG: Dict[int, Dict[str, str]] = {
    2015: {"est_prefix": "ADQYE", "moe_prefix": "ADQYM", "geoid_col": "GEOID"},
    2020: {"est_prefix": "AMVDE", "moe_prefix": "AMVDM", "geoid_col": "GEOID"},
    2023: {"est_prefix": "ASUPE", "moe_prefix": "ASUPM", "geoid_col": "GEO_ID"},
}


def _build_raw_nhgis(year: int) -> pd.DataFrame:
    """Build a synthetic raw NHGIS DataFrame for *year*.

    Creates 12 rows covering diverse analysis scenarios:
        0  - Natural gas dominant (PA)
        1  - Electricity dominant (AL)
        2  - Two-fuel tie (OH)
        3  - Zero total housing units (TX)
        4  - NaN total housing units (CA)
        5  - Very small counts / high CV (NY)
        6  - Large counts / low CV (IL)
        7  - Alaska tract (AK)
        8  - Hawaii tract (HI)
        9  - Coal dominant / rare fuel (WV)
        10 - Solar dominant / rare fuel (AZ)
        11 - Fuel oil dominant (ME)
    """
    cfg = _YEAR_CONFIG[year]
    est = cfg["est_prefix"]
    moe = cfg["moe_prefix"]
    geoid_col = cfg["geoid_col"]

    # fmt: off
    rows = [
        # GISJOIN             YEAR  STUSAB STATE            STATEA COUNTY              COUNTYA TRACTA   GEOID                      NAME_E                                            Tot  NG   Prop  Elec FO   Coal Wood Solar Oth  NF   mTot mNG  mPr  mEl  mFO  mCo  mWo  mSo  mOt  mNF
        ("G4200010010100",     year, "PA",  "Pennsylvania",  "42", "Adams County",      "001", "010100","14000US42001010100",       "Tract 101, Adams County, PA",                    1000, 700,  50,  150,  30,   5,  40,   5,  10,  10,  50,  40,  20,  30,  15,  10,  20,  10,  10,  10),
        ("G0101010031000",     year, "AL",  "Alabama",       "01", "Russell County",    "101", "031000","14000US01101031000",       "Tract 310, Russell County, AL",                  1408,  30, 258, 1074,   0,   0,  46,   0,   0,   0,  60,  15,  40,  70,   0,   0,  25,   0,   0,   0),
        ("G3900010010200",     year, "OH",  "Ohio",          "39", "Adams County",      "001", "010200","14000US39001010200",       "Tract 102, Adams County, OH",                    1000, 400,  50,  400,  50,  10,  40,  10,  20,  20,  55,  45,  25,  45,  25,  12,  22,  12,  15,  15),
        ("G4800010010100",     year, "TX",  "Texas",         "48", "Anderson County",   "001", "010100","14000US48001010100",       "Tract 101, Anderson County, TX",                    0,   0,   0,    0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0),
        ("G0600010010100",     year, "CA",  "California",    "06", "Alameda County",    "001", "010100","14000US06001010100",       "Tract 101, Alameda County, CA",              np.nan, np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan),
        ("G3600010010100",     year, "NY",  "New York",      "36", "Albany County",     "001", "010100","14000US36001010100",       "Tract 101, Albany County, NY",                     10,   5,   1,    2,   1,   0,   1,   0,   0,   0,  50,  40,  20,  30,  20,   0,  20,   0,   0,   0),
        ("G1700010010100",     year, "IL",  "Illinois",      "17", "Adams County",      "001", "010100","14000US17001010100",       "Tract 101, Adams County, IL",                    5000,3500, 200,  800, 100,  50, 200,  50,  50,  50, 100,  80,  40,  60,  30,  25,  45,  25,  25,  25),
        ("G0200010010100",     year, "AK",  "Alaska",        "02", "Aleutians East",    "013", "010100","14000US02013010100",       "Tract 101, Aleutians East, AK",                   500, 200,  50,  150,  50,   0,  40,   0,   5,   5,  70,  50,  30,  40,  30,   0,  25,   0,  10,  10),
        ("G1500010010100",     year, "HI",  "Hawaii",        "15", "Hawaii County",     "001", "010100","14000US15001010100",       "Tract 101, Hawaii County, HI",                    300,  10,  20,  250,   0,   0,  10,   5,   3,   2,  45,  15,  20,  50,   0,   0,  15,  10,   8,   8),
        ("G5400010010100",     year, "WV",  "West Virginia", "54", "Barbour County",    "001", "010100","14000US54001010100",       "Tract 101, Barbour County, WV",                   200,  30,  20,   50,  10,  60,  15,   0,  10,   5,  40,  20,  18,  30,  15,  35,  18,   0,  15,  10),
        ("G0400010010100",     year, "AZ",  "Arizona",       "04", "Apache County",     "001", "010100","14000US04001010100",       "Tract 101, Apache County, AZ",                    100,  10,   5,   20,   0,   0,   5,  50,   5,   5,  30,  15,  12,  20,   0,   0,  12,  30,  12,  12),
        ("G2300010010100",     year, "ME",  "Maine",         "23", "Androscoggin County","001","010100","14000US23001010100",       "Tract 101, Androscoggin County, ME",              800,  50,  30,  100, 500,   0,  80,   0,  20,  20,  55,  30,  22,  40,  60,   0,  35,   0,  18,  18),
    ]
    # fmt: on

    meta_cols = [
        "GISJOIN", "YEAR", "STUSAB", "STATE", "STATEA",
        "COUNTY", "COUNTYA", "TRACTA", geoid_col, "NAME_E",
    ]
    est_cols = [f"{est}{i:03d}" for i in range(1, 11)]
    moe_cols = [f"{moe}{i:03d}" for i in range(1, 11)]
    all_cols = meta_cols + est_cols + moe_cols

    df = pd.DataFrame(rows, columns=all_cols)
    return df


def _build_mock_tract_gdf(geoid_col: str = "GEOID") -> gpd.GeoDataFrame:
    """Build a small GeoDataFrame with square geometries matching GISJOIN values.

    Creates one polygon per synthetic tract row.  Alaska and Hawaii rows use
    shifted positions purely for distinguishability; CRS is EPSG:5070.
    """
    gisjoins = [
        "G4200010010100", "G0101010031000", "G3900010010200",
        "G4800010010100", "G0600010010100", "G3600010010100",
        "G1700010010100", "G0200010010100", "G1500010010100",
        "G5400010010100", "G0400010010100", "G2300010010100",
    ]
    geometries = [box(i, 0, i + 1, 1) for i in range(len(gisjoins))]

    gdf = gpd.GeoDataFrame(
        {"GISJOIN": gisjoins},
        geometry=geometries,
        crs="EPSG:5070",
    )
    return gdf


def _build_mock_states_gdf() -> gpd.GeoDataFrame:
    """Build a small states GeoDataFrame with a STUSPS column."""
    states = ["PA", "AL", "OH", "TX", "CA", "NY", "IL", "AK", "HI", "WV", "AZ", "ME"]
    geometries = [box(i * 2, 2, i * 2 + 2, 4) for i in range(len(states))]
    gdf = gpd.GeoDataFrame(
        {"STUSPS": states},
        geometry=geometries,
        crs="EPSG:5070",
    )
    return gdf


# ============================================================================
# RAW NHGIS FIXTURES (one per year)
# ============================================================================

@pytest.fixture
def raw_nhgis_dataframe_2015() -> pd.DataFrame:
    """Synthetic raw NHGIS DataFrame using 2015 column prefix ADQYE/ADQYM."""
    return _build_raw_nhgis(2015)


@pytest.fixture
def raw_nhgis_dataframe_2020() -> pd.DataFrame:
    """Synthetic raw NHGIS DataFrame using 2020 column prefix AMVDE/AMVDM."""
    return _build_raw_nhgis(2020)


@pytest.fixture
def raw_nhgis_dataframe_2023() -> pd.DataFrame:
    """Synthetic raw NHGIS DataFrame using 2023 column prefix ASUPE/ASUPM."""
    return _build_raw_nhgis(2023)


# ============================================================================
# PROCESSED DATA FIXTURES
# ============================================================================

@pytest.fixture
def processed_dataframe() -> pd.DataFrame:
    """DataFrame after process_heating_fuel_data() with MOE columns (45 cols)."""
    raw = _build_raw_nhgis(2020)
    return process_heating_fuel_data(raw, year=2020, include_moe=True)


@pytest.fixture
def flagged_dataframe(processed_dataframe: pd.DataFrame) -> pd.DataFrame:
    """DataFrame after flag_unreliable_tracts() — includes CV and flag columns."""
    return flag_unreliable_tracts(processed_dataframe)


# ============================================================================
# GEODATAFRAME FIXTURES
# ============================================================================

@pytest.fixture
def mock_geodataframe() -> gpd.GeoDataFrame:
    """Tract GeoDataFrame with GISJOIN column and simple square geometries."""
    return _build_mock_tract_gdf()


@pytest.fixture
def mock_states_gdf() -> gpd.GeoDataFrame:
    """State boundaries GeoDataFrame with STUSPS column."""
    return _build_mock_states_gdf()


@pytest.fixture
def processed_geodataframe(
    mock_geodataframe: gpd.GeoDataFrame,
    processed_dataframe: pd.DataFrame,
) -> Dict[str, gpd.GeoDataFrame]:
    """Result of prepare_geodataframe() — dict with 'filtered', 'conus', 'alaska'."""
    from scripts.process_data import prepare_geodataframe

    gdf_filtered, gdf_conus, gdf_alaska = prepare_geodataframe(
        mock_geodataframe, processed_dataframe
    )
    return {"filtered": gdf_filtered, "conus": gdf_conus, "alaska": gdf_alaska}
