# config.py
import os

# Force the path to be relative to this specific file's location
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

print(f"Project root directory: {PROJECT_ROOT}")

"""
========== IMPORTANT NOTES BELOW! ==========
If you download the data yourself, the download number and/or dataset codes
may need to be updated here accordingly.

Make sure that matching shapefiles are also downloaded for the same datasets!

For example:
'nhgis0011' refers to the specific NHGIS download (11th download)
'ds215_20155', 'ds249_20205', and 'ds267_20235' are different NHGIS datasets 
'20155', '20205', and '20235' indicate 5 year datasets: 2011-2015, 2016-2020, and 2019-2023
'tract' indicates census tract level data
"""

# Raw NHGIS data (this is our starting point)
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw_data_and_codebook', 'nhgis0011_csv')

# Shapefile boundaries
BOUNDARIES_DIR = os.path.join(PROJECT_ROOT, 'data', 'boundaries', 'nhgis0011_shape')

# Output directories
MAPS_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'maps')
LAYOUTS_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'print_layouts')

# ============================================================================
# RAW INPUT FILES (Starting point - raw NHGIS data)
# ============================================================================

RAW_CSV_2015 = os.path.join(RAW_DATA_DIR, 'nhgis0011_ds215_20155_tract.csv')
RAW_CSV_2020 = os.path.join(RAW_DATA_DIR, 'nhgis0011_ds249_20205_tract.csv')
RAW_CSV_2023 = os.path.join(RAW_DATA_DIR, 'nhgis0011_ds267_20235_tract.csv')

# ============================================================================
# SHAPEFILES
# ============================================================================

TRACT_SHAPEFILE_2015 = os.path.join(BOUNDARIES_DIR, 'nhgis0011_shapefile_tl2015_us_tract_2015', 'US_tract_2015.shp')
TRACT_SHAPEFILE_2020 = os.path.join(BOUNDARIES_DIR, 'nhgis0011_shapefile_tl2020_us_tract_2020', 'US_tract_2020.shp')
TRACT_SHAPEFILE_2023 = os.path.join(BOUNDARIES_DIR, 'nhgis0011_shapefile_tl2023_us_tract_2023', 'US_tract_2023.shp')

# State boundaries (optional - for map context)
STATE_SHAPEFILE_2015 = os.path.join(BOUNDARIES_DIR, 'nhgis0011_shapefile_tl2015_us_state_2015', 'US_state_2015.shp')

# ============================================================================
# COUNTY-LEVEL DATA (Census Bureau direct downloads, not NHGIS)
# ============================================================================
"""
The county-level analysis sources data directly from the Census Bureau instead
of NHGIS:
  - Attribute data: Table B25040 (House Heating Fuel) 5-year ACS estimates,
    downloaded per-county from data.census.gov. Unlike the NHGIS tract
    extracts, the B25040_0XXE/B25040_0XXM variable codes are the same across
    every ACS vintage, so a single county processing function handles all
    years (see process_heating_fuel_data_county() in scripts/process_data.py).
  - Boundaries: Census cartographic boundary (cb) shapefiles, not TIGER/Line
    (tl) files -- cb files clip out large water areas that make tl-based
    county maps render with distracting slivers along coastlines/rivers.
"""

RAW_DATA_DIR_COUNTY = os.path.join(PROJECT_ROOT, 'data', 'raw_data_and_codebook', 'census_b25040_county')
BOUNDARIES_DIR_COUNTY = os.path.join(PROJECT_ROOT, 'data', 'boundaries', 'census_cb_shapefiles')

RAW_CSV_COUNTY_2015 = os.path.join(RAW_DATA_DIR_COUNTY, 'ACSDT5Y2015.B25040-Data.csv')
RAW_CSV_COUNTY_2020 = os.path.join(RAW_DATA_DIR_COUNTY, 'ACSDT5Y2020.B25040-Data.csv')
RAW_CSV_COUNTY_2023 = os.path.join(RAW_DATA_DIR_COUNTY, 'ACSDT5Y2023.B25040-Data.csv')
RAW_CSV_COUNTY_2024 = os.path.join(RAW_DATA_DIR_COUNTY, 'ACSDT5Y2024.B25040-Data.csv')

COUNTY_SHAPEFILE_2015 = os.path.join(BOUNDARIES_DIR_COUNTY, 'cb_2015_us_county_500k', 'cb_2015_us_county_500k.shp')
COUNTY_SHAPEFILE_2020 = os.path.join(BOUNDARIES_DIR_COUNTY, 'cb_2020_us_county_500k', 'cb_2020_us_county_500k.shp')
COUNTY_SHAPEFILE_2023 = os.path.join(BOUNDARIES_DIR_COUNTY, 'cb_2023_us_county_500k', 'cb_2023_us_county_500k.shp')
COUNTY_SHAPEFILE_2024 = os.path.join(BOUNDARIES_DIR_COUNTY, 'cb_2024_us_county_500k', 'cb_2024_us_county_500k.shp')

# State cb boundaries -- matching vintage per year, since (unlike the county
# files) they're small and there's no reason not to keep them in sync.
STATE_CB_SHAPEFILE_2015 = os.path.join(BOUNDARIES_DIR_COUNTY, 'cb_2015_us_state_500k', 'cb_2015_us_state_500k.shp')
STATE_CB_SHAPEFILE_2020 = os.path.join(BOUNDARIES_DIR_COUNTY, 'cb_2020_us_state_500k', 'cb_2020_us_state_500k.shp')
STATE_CB_SHAPEFILE_2023 = os.path.join(BOUNDARIES_DIR_COUNTY, 'cb_2023_us_state_500k', 'cb_2023_us_state_500k.shp')
STATE_CB_SHAPEFILE_2024 = os.path.join(BOUNDARIES_DIR_COUNTY, 'cb_2024_us_state_500k', 'cb_2024_us_state_500k.shp')
