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