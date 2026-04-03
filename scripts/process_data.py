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
    year: int,
    include_moe: bool = True
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
    8. Optionally extracts margin of error (MOE) columns
    
    Args:
        df: DataFrame containing raw NHGIS data.
        year: Year identifier (2015, 2020, or 2023).
        include_moe: If True, extract and rename MOE columns alongside estimate
            columns. MOE columns are named MOE_{readable_name} (e.g.,
            MOE_Natural_Gas). Defaults to True.
    
    Returns:
        Processed DataFrame with geographic identifiers, fuel counts,
        percentages, dominant fuel analysis, and (if include_moe=True)
        MOE columns for each fuel type.
        
    Raises:
        KeyError: If year is not 2015, 2020, or 2023.
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
    
    if include_moe:
        moe_prefix = fuel_prefix[:-1] + 'M'  # Replace trailing E with M
        # Derive MOE mapping programmatically from estimate mapping so they stay in sync
        fuel_estimate_cols = {k: v for k, v in columns_to_keep.items()
                              if k.startswith(fuel_prefix)}
        moe_columns_to_keep = {
            k.replace(fuel_prefix, moe_prefix): f'MOE_{v}'
            for k, v in fuel_estimate_cols.items()
        }
        all_columns = {**columns_to_keep, **moe_columns_to_keep}
    else:
        all_columns = columns_to_keep

    df = df[list(all_columns.keys())].rename(columns=all_columns)
    
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
# FUNCTIONS: Margin of Error and Reliability Analysis
# ============================================================================

def calculate_cv(estimate: pd.Series, moe: pd.Series) -> pd.Series:
    """Calculate the coefficient of variation from ACS estimates and margins of error.

    The CV measures relative reliability of an ACS estimate. It is calculated as:
        CV = (MOE / 1.645) / Estimate
    where 1.645 converts the 90% confidence MOE to a standard error.

    Following U.S. Census Bureau guidance, estimates with CV > 0.30 are considered
    potentially unreliable.

    Args:
        estimate: ACS point estimate values (counts of housing units).
        moe: ACS margin of error values at the 90% confidence level.

    Returns:
        Series of CV values. Returns NaN where estimate is 0 or where
        either input is NaN.

    References:
        U.S. Census Bureau. (2022). "Increased Margins of Error in the 5-Year
        Estimates Containing Data Collected in 2020." Census.gov.
        https://www.census.gov/programs-surveys/acs/technical-documentation/user-notes/2022-04.html
    """
    se = moe / 1.645
    # CV is undefined when estimate is zero; NaN propagates for missing inputs
    valid = (estimate > 0) & estimate.notna() & moe.notna()
    cv = np.where(valid, se / estimate, np.nan)
    return pd.Series(cv, index=estimate.index, dtype=float)


def flag_unreliable_tracts(
    df: pd.DataFrame,
    cv_threshold: float = 0.30,
    flag_total: bool = True,
    flag_dominant: bool = True
) -> pd.DataFrame:
    """Flag census tracts with potentially unreliable ACS estimates based on CV.

    Calculates the coefficient of variation (CV) for Total Housing Units and
    for the dominant fuel count in each tract. Adds flag columns indicating
    whether each tract exceeds the specified CV threshold.

    Args:
        df: DataFrame with processed heating fuel data. Must contain estimate
            columns and their corresponding MOE columns (MOE_ prefix).
        cv_threshold: CV value above which estimates are flagged as unreliable.
            Default is 0.30, following Census Bureau guidance. Users may adjust
            this for their specific applications.
        flag_total: If True, calculate CV on Total_Housing_Units.
        flag_dominant: If True, calculate CV on the dominant fuel count.

    Returns:
        DataFrame with additional columns:
            - CV_Total_Housing_Units: CV for total housing unit count
            - CV_Dom_Fuel: CV for the dominant fuel count
            - Flag_Unreliable_Total: True if CV_Total > threshold
            - Flag_Unreliable_Dom_Fuel: True if CV_Dom_Fuel > threshold

    Raises:
        ValueError: If MOE columns are not present in the DataFrame.
    """
    # Mapping from Dom_Fuel_Type values to their corresponding MOE columns
    FUEL_TO_MOE: Dict[str, str] = {
        'Natural_Gas': 'MOE_Natural_Gas',
        'Propane': 'MOE_Propane',
        'Electricity': 'MOE_Electricity',
        'Fuel_Oil': 'MOE_Fuel_Oil',
        'Coal': 'MOE_Coal',
        'Wood': 'MOE_Wood',
        'Solar': 'MOE_Solar',
        'Other': 'MOE_Other',
        'No_Fuel': 'MOE_No_Fuel',
    }

    result = df.copy()

    if flag_total:
        if 'MOE_Total_Housing_Units' not in result.columns:
            raise ValueError(
                "MOE_Total_Housing_Units column not found. "
                "Run process_heating_fuel_data(df, year, include_moe=True) first."
            )
        result['CV_Total_Housing_Units'] = calculate_cv(
            result['Total_Housing_Units'], result['MOE_Total_Housing_Units']
        )
        result['Flag_Unreliable_Total'] = result['CV_Total_Housing_Units'] > cv_threshold

    if flag_dominant:
        missing_moe = [col for col in FUEL_TO_MOE.values() if col not in result.columns]
        if missing_moe:
            raise ValueError(
                f"MOE columns not found: {missing_moe}. "
                "Run process_heating_fuel_data(df, year, include_moe=True) first."
            )
        # Vectorized lookup: select the MOE column matching each tract's dominant fuel
        conditions = [result['Dom_Fuel_Type'] == fuel for fuel in FUEL_TO_MOE]
        choices = [result[moe_col] for moe_col in FUEL_TO_MOE.values()]
        dom_fuel_moe = pd.Series(
            np.select(conditions, choices, default=np.nan),
            index=result.index,
            dtype=float
        )
        result['CV_Dom_Fuel'] = calculate_cv(result['Dom_Fuel_Count'], dom_fuel_moe)
        result['Flag_Unreliable_Dom_Fuel'] = result['CV_Dom_Fuel'] > cv_threshold

    return result


def print_cv_summary(
    df: pd.DataFrame,
    thresholds: List[float] = [0.15, 0.20, 0.30, 0.40]
) -> pd.DataFrame:
    """Print and return a summary of tract reliability at various CV thresholds.

    Shows how many tracts would be flagged as unreliable at each threshold,
    for both Total Housing Units and Dominant Fuel CV.

    Args:
        df: DataFrame that has been processed by flag_unreliable_tracts().
            Must contain CV_Total_Housing_Units and CV_Dom_Fuel columns.
        thresholds: List of CV thresholds to evaluate.

    Returns:
        DataFrame summarizing flagged tract counts and percentages at each threshold.
    """
    required_cols = ['CV_Total_Housing_Units', 'CV_Dom_Fuel']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Required columns not found: {missing}. "
            "Run flag_unreliable_tracts() first."
        )

    total_tracts = len(df)

    rows = []
    for threshold in thresholds:
        total_flagged = int((df['CV_Total_Housing_Units'] > threshold).sum())
        dom_flagged = int((df['CV_Dom_Fuel'] > threshold).sum())
        rows.append({
            'Threshold': f'CV > {threshold:.2f}',
            'Total_Flagged': total_flagged,
            'Total_Pct': total_flagged / total_tracts * 100,
            'Dom_Flagged': dom_flagged,
            'Dom_Pct': dom_flagged / total_tracts * 100,
        })

    summary_df = pd.DataFrame(rows)

    print("\nCV Reliability Summary")
    print("=" * 54)
    print(f"{'':12} {'Total Housing Units':>22}    {'Dominant Fuel':>13}")
    print(f"{'Threshold':<12} {'Flagged':>8}    {'(%)':>6}  {'Flagged':>10}    {'(%)':>6}")
    print("-" * 54)
    for _, row in summary_df.iterrows():
        print(
            f"{row['Threshold']:<12} {int(row['Total_Flagged']):>8,}   {row['Total_Pct']:>5.1f}%"
            f"  {int(row['Dom_Flagged']):>10,}   {row['Dom_Pct']:>5.1f}%"
        )
    print("=" * 54)
    print(f"Total tracts: {total_tracts:,}")

    return summary_df


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
