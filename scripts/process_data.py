# 02_scripts/data_processing.py
"""
Data processing functions for heating fuel analysis.

This module processes raw NHGIS census tract data into analysis-ready format
with fuel percentages and dominant fuel identification.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import geopandas as gpd

# ============================================================================
# FUNCTIONS: Process NHGIS Heating Fuel Data for a Given Year
# ============================================================================

def process_heating_fuel_data(
    df: pd.DataFrame,
    year: int
) -> pd.DataFrame:
    """Process raw NHGIS heating fuel data for a specific year.
    
    Performs the following transformations:
    1. Takes in raw DataFrame and year (2015, 2020, or 2023)
    2. Selects and renames columns to standardized names
    3. Extracts FIPS codes from GEOID
    4. Flags data quality (valid vs insufficient)
    5. Calculates fuel type percentages
    6. Identifies dominant fuel type and handles ties
    7. Calculates dominant fuel statistics
    
    Args:
        df: DataFrame containing raw NHGIS data.
        year: Year identifier (2015, 2020, or 2023).
    
    Returns:
        Processed DataFrame with 35 columns including geographic identifiers,
        fuel counts, percentages, and dominant fuel analysis.
        
    Raises:
        KeyError: If year is not 2015, 2020, or 2023.
        FileNotFoundError: If raw_csv_path does not exist.
    """
    
    # Year-specific column mappings
    column_mappings = {
        2015: {
            'geoid_col': 'GEOID',
            'name_col': 'NAME_E',
            'fuel_prefix': 'ADQYE'
        },
        2020: {
            'geoid_col': 'GEOID',
            'name_col': 'NAME_E', 
            'fuel_prefix': 'AMVDE'
        },
        2023: {
            'geoid_col': 'GEO_ID',  # Different in 2023!
            'name_col': 'NAME_E',
            'fuel_prefix': 'ASUPE'
        }
    }
    
    if year not in column_mappings:
        raise KeyError(f"Year must be 2015, 2020, or 2023. Got: {year}")
    
    mapping = column_mappings[year]
    fuel_prefix = mapping['fuel_prefix']
    geoid_col = mapping['geoid_col']
    
    # # Load raw data (skip row 1 which contains descriptions)
    # df = pd.read_csv(raw_csv_path, skiprows=[1], low_memory=False)
    
    # Select and rename columns to standardized names
    columns_to_keep = {
        'GISJOIN': 'GISJOIN',
        'YEAR': 'YEAR',
        'STUSAB': 'STUSAB',
        'STATE': 'STATE',
        'STATEA': 'STATEA',
        'COUNTY': 'COUNTY',
        'COUNTYA': 'COUNTYA',
        'TRACTA': 'TRACTA',
        geoid_col: 'GEOID',
        mapping['name_col']: 'County_Name',
        f'{fuel_prefix}001': 'Total_Housing_Units',
        f'{fuel_prefix}002': 'Natural_Gas',
        f'{fuel_prefix}003': 'Propane',
        f'{fuel_prefix}004': 'Electricity',
        f'{fuel_prefix}005': 'Fuel_Oil',
        f'{fuel_prefix}006': 'Coal',
        f'{fuel_prefix}007': 'Wood',
        f'{fuel_prefix}008': 'Solar',
        f'{fuel_prefix}009': 'Other',
        f'{fuel_prefix}010': 'No_Fuel'
    }
    
    df = df[list(columns_to_keep.keys())].rename(columns=columns_to_keep)
    
    # Extract FIPS_Code (last 11 characters of GEOID)
    df['FIPS_Code'] = df['GEOID'].str[-11:]
    
    # Create data quality flag
    df['Data_Quality_Check'] = np.where(
        (df['Total_Housing_Units'].notna()) & (df['Total_Housing_Units'] > 0),
        'Valid_Data',
        'Insufficient_Data'
    )
    
    # Calculate percentages for all fuel types
    fuel_columns = ['Natural_Gas', 'Propane', 'Electricity', 'Fuel_Oil', 
                    'Coal', 'Wood', 'Solar', 'Other', 'No_Fuel']
    
    for fuel in fuel_columns:
        pct_col = f'Pct_{fuel}'
        df[pct_col] = np.where(
            df['Data_Quality_Check'] == 'Insufficient_Data',
            np.nan,
            np.round((df[fuel] / df['Total_Housing_Units']) * 100, 1)
        )
    
    # Find max fuel value and detect ties
    fuel_counts = df[fuel_columns]
    df['_max_fuel_value'] = fuel_counts.max(axis=1)
    df['_tie_count'] = (fuel_counts == df['_max_fuel_value'].values[:, np.newaxis]).sum(axis=1)
    
    df['Has_Dom_Tie'] = np.where(
        df['Total_Housing_Units'] == 0,
        False,
        df['_tie_count'] > 1
    )
    
    # Identify dominant fuel type
    df['Dom_Fuel_Type'] = df.apply(
        lambda row: _identify_dominant_fuel(row, fuel_columns), 
        axis=1
    )
    
    # Calculate dominant fuel statistics
    df['Dom_Fuel_Count'] = np.where(
        (df['Data_Quality_Check'] == 'Insufficient_Data') | (df['Has_Dom_Tie']),
        np.nan,
        df['_max_fuel_value']
    )
    
    df['Dom_Fuel_Pct'] = np.where(
        (df['Data_Quality_Check'] == 'Insufficient_Data') | (df['Has_Dom_Tie']),
        np.nan,
        np.round((df['_max_fuel_value'] / df['Total_Housing_Units']) * 100, 1)
    )
    
    # Remove temporary calculation columns
    df = df.drop(columns=['_max_fuel_value', '_tie_count'])
    
    return df


def _identify_dominant_fuel(
    row: pd.Series,
    fuel_columns: List[str]
) -> str:
    """Identify which fuel type is dominant for a census tract.
    
    Checks fuel types in priority order and returns the first one that
    matches the maximum value. Returns 'No_Data' for insufficient data
    or 'Tie' when multiple fuels are tied for maximum.
    
    Args:
        row: DataFrame row containing fuel data and flags.
        fuel_columns: Ordered list of fuel column names to check.
    
    Returns:
        Name of dominant fuel type, 'Tie', 'No_Data', or 'Error'.
    """
    if row['Data_Quality_Check'] == 'Insufficient_Data':
        return 'No_Data'
    if row['Has_Dom_Tie']:
        return 'Tie'
    
    max_value = row['_max_fuel_value']
    for fuel in fuel_columns:
        if row[fuel] == max_value:
            return fuel
    
    return 'Error'  # Should never reach here

# ============================================================================
# FUNCTIONS: Prepare Geodataframe for Mapping
# ============================================================================
FUEL_COLORS = {
    'Natural_Gas': '#3182bd',      # Darker blue (more contrast)
    'Electricity': '#31a354',      # Medium green
    'Fuel_Oil': '#de2d26',         # Bright red
    'Propane': '#fd8d3c',          # Orange (better than yellow for print)
    'Wood': '#8c6d31',             # Darker brown (better contrast)
    'Other': '#969696',            # Gray
    'No_Fuel_Missing': '#f0f0f0'   # Light gray (better than pure white)
}


def simplify_fuel_categories(fuel_type: str) -> str:
    """
    Simplify detailed fuel type categories into broader groups.
    
    Combines rare fuel types and missing data into consolidated categories
    for cleaner visualization.
    
    Args:
        fuel_type: Original fuel type from Dom_Fuel_Type column.
    
    Returns:
        Simplified fuel category name.
    
    Categories:
        - Electricity, Natural_Gas, Propane, Fuel_Oil, Wood: Unchanged
        - Tie, Coal, Solar, Other: Combined into "Other"
        - No_Fuel, No_Data: Combined into "No_Fuel_Missing"
    """
    if fuel_type in ['Electricity', 'Natural_Gas', 'Propane', 'Fuel_Oil', 'Wood']:
        return fuel_type
    elif fuel_type in ['Tie', 'Coal', 'Solar', 'Other']:
        return 'Other'
    else:  # No_Fuel, No_Data
        return 'No_Fuel_Missing'

def prepare_geodataframe(
    gdf_tracts: gpd.GeoDataFrame,
    df_processed: pd.DataFrame,
    exclude_states: Optional[list] = None,
) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Prepare and filter geodataframe for mapping.
    
    Merges processed fuel data with tract geometries, applies simplified
    fuel categories, filters geographic extent, and separates Alaska for
    inset plotting.
    
    Args:
        gdf_tracts: GeoDataFrame containing census tract geometries.
        df_processed: DataFrame with processed heating fuel data.
        exclude_states: List of state abbreviations to exclude (e.g., ['HI', 'PR']).
    
    Returns:
        Tuple of (gdf_full, gdf_conus, gdf_alaska) where:
        - gdf_full: Complete merged geodataframe with filtered states
        - gdf_conus: Contiguous US only (excludes Alaska)
        - gdf_alaska: Alaska only
    """
    if exclude_states is None:
        exclude_states = ['HI', 'PR']
    
    # Merge geometries with processed data
    gdf = gdf_tracts.merge(df_processed, on='GISJOIN', how='left')
    
    # Apply simplified fuel categories
    gdf['Dom_Fuel_Simple'] = gdf['Dom_Fuel_Type'].apply(simplify_fuel_categories)
    
    # Assign colors
    gdf['color'] = gdf['Dom_Fuel_Simple'].map(FUEL_COLORS)
    
    # Filter geographic extent
    gdf_filtered = gdf[~gdf['STUSAB'].isin(exclude_states)].copy()
    
    # Separate Alaska for inset
    gdf_alaska = gdf_filtered[gdf_filtered['STUSAB'] == 'AK'].copy()
    gdf_conus = gdf_filtered[gdf_filtered['STUSAB'] != 'AK'].copy()
    
    return gdf_filtered, gdf_conus, gdf_alaska
