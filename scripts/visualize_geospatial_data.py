"""
Heating Fuel Choropleth Mapping Functions

Creates census tract-level maps showing primary heating fuel usage across the US.
Handles standard layout with Alaska inset and customizable positioning.
"""
import os
from typing import List, Tuple, Optional, Dict
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

FUEL_COLORS = {
    'Natural_Gas': '#3182bd',      # Darker blue (more contrast)
    'Electricity': '#31a354',      # Medium green
    'Fuel_Oil': '#de2d26',         # Bright red
    'Propane': '#fd8d3c',          # Orange (better than yellow for print)
    'Wood': '#8c6d31',             # Darker brown (better contrast)
    'Other': '#969696',            # Gray
    'No_Fuel_Missing': '#f0f0f0'   # Light gray (better than pure white)
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def detect_state_column(gdf: gpd.GeoDataFrame) -> str:
    """
    Find state abbreviation column in GeoDataFrame.
    
    Args:
        gdf: GeoDataFrame to search
        
    Returns:
        Name of state abbreviation column
        
    Raises:
        ValueError: If no recognized column found
    """
    candidates = ['STUSAB', 'STUSPS', 'STATE_ABBR', 'STATEABBR']
    
    for col in candidates:
        if col in gdf.columns:
            return col
    
    raise ValueError(
        f"No state abbreviation column found. Tried: {candidates}. "
        f"Available: {list(gdf.columns)}"
    )


def create_legend_elements() -> List[Patch]:
    """Create legend patches for heating fuel types."""
    return [
        Patch(facecolor=FUEL_COLORS['Electricity'], label='Electricity'),
        Patch(facecolor=FUEL_COLORS['Natural_Gas'], label='Natural Gas'),
        Patch(facecolor=FUEL_COLORS['Propane'], label='Propane'),
        Patch(facecolor=FUEL_COLORS['Fuel_Oil'], label='Fuel Oil'),
        Patch(facecolor=FUEL_COLORS['Wood'], label='Wood'),
        Patch(facecolor=FUEL_COLORS['Other'], label='Other'),
        Patch(facecolor=FUEL_COLORS['No_Fuel_Missing'], label='No Fuel/Missing')
    ]


# ============================================================================
# CORE PLOTTING FUNCTION
# ============================================================================

def plot_heating_fuel_map(
    gdf_conus: gpd.GeoDataFrame,
    gdf_alaska: gpd.GeoDataFrame,
    gdf_states: gpd.GeoDataFrame,
    year: int,
    ax_main: plt.Axes,
    ax_alaska: Optional[plt.Axes] = None,
    show_title: bool = True,
    verbose: bool = False
) -> None:
    """
    Render heating fuel choropleth on provided axes.
    
    Args:
        gdf_conus: Contiguous US tracts with 'color' column
        gdf_alaska: Alaska tracts with 'color' column
        gdf_states: State boundaries (matching CRS)
        year: Data year for title
        ax_main: Main map axes
        ax_alaska: Optional Alaska inset axes
        show_title: Whether to add title
        verbose: Print rendering progress
        
    Raises:
        ValueError: If CRS doesn't match between inputs
    """
    # Verify consistent CRS
    if gdf_conus.crs != gdf_states.crs:
        raise ValueError(
            f"CRS mismatch: tracts={gdf_conus.crs}, states={gdf_states.crs}"
        )
    
    # Split state boundaries by region
    state_col = detect_state_column(gdf_states)
    state_ak = gdf_states[gdf_states[state_col] == 'AK']
    state_conus = gdf_states[~gdf_states[state_col].isin(['AK', 'HI', 'PR'])]
    
    # Plot contiguous US
    if verbose:
        print(f"  Rendering CONUS: {len(gdf_conus):,} tracts")
    
    gdf_conus.plot(
        ax=ax_main,
        color=gdf_conus['color'],
        edgecolor='none',
        linewidth=0,
        rasterized=True
    )
    
    state_conus.boundary.plot(
        ax=ax_main,
        linewidth=0.6,
        edgecolor='black',
        rasterized=False
    )
    
    ax_main.set_axis_off()
    
    # Add title if requested
    if show_title:
        ax_main.text(
            0.5, 0.97,
            f'Primary Heating Fuel by Census Tract, {year}',
            transform=ax_main.transAxes,
            ha='center',
            fontsize=24,
            fontweight='bold'
        )
    
    # Plot Alaska inset if provided
    if ax_alaska is not None:
        if verbose:
            print(f"  Rendering Alaska: {len(gdf_alaska):,} tracts")
        
        gdf_alaska.plot(
            ax=ax_alaska,
            color=gdf_alaska['color'],
            edgecolor='none',
            linewidth=0,
            rasterized=True
        )
        
        state_ak.boundary.plot(
            ax=ax_alaska,
            linewidth=0.8,
            edgecolor='black',
            rasterized=False
        )
        
        ax_alaska.set_axis_off()
        ax_alaska.text(
            0.5, -0.05,
            'Alaska',
            transform=ax_alaska.transAxes,
            ha='center',
            fontsize=11
        )


# ============================================================================
# COMPLETE MAP CREATION
# ============================================================================

def create_heating_fuel_map(
    gdf_conus: gpd.GeoDataFrame,
    gdf_alaska: gpd.GeoDataFrame,
    gdf_states: gpd.GeoDataFrame,
    year: int,
    output_dir: str,
    show_plot: bool = True,
    dpi: int = 600,
    verbose: bool = False
) -> Tuple[str, str]:
    """
    Create and save complete heating fuel map with standard layout.
    
    Args:
        gdf_conus: Contiguous US tracts with 'color' column
        gdf_alaska: Alaska tracts with 'color' column
        gdf_states: State boundaries
        year: Data year
        output_dir: Directory for output files
        show_plot: Display plot after creation
        dpi: PNG resolution
        verbose: Print progress messages
        
    Returns:
        Tuple of (png_path, pdf_path)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Create figure with standard layout
    fig = plt.figure(figsize=(20, 11), facecolor='white')
    
    # Main map: 2% left margin, 75% width, 80% height
    ax_main = plt.axes([0.02, 0.15, 0.75, 0.80])
    
    # Alaska inset: bottom-left corner
    ax_alaska = plt.axes([0.02, 0.15, 0.22, 0.25])
    
    # Render map layers
    plot_heating_fuel_map(
        gdf_conus=gdf_conus,
        gdf_alaska=gdf_alaska,
        gdf_states=gdf_states,
        year=year,
        ax_main=ax_main,
        ax_alaska=ax_alaska,
        show_title=True,
        verbose=verbose
    )
    
    # Add legend (positioned in figure coordinates for precision)
    fig.legend(
        handles=create_legend_elements(),
        title='Primary Heating Fuel\n(by census tract)',
        loc='center right',
        bbox_to_anchor=(0.80, 0.55),
        bbox_transform=fig.transFigure,
        fontsize=11,
        frameon=True,
        edgecolor='black'
    )
    
    # Save outputs
    png_path = os.path.join(output_dir, f'heating_fuel_map_{year}.png')
    pdf_path = os.path.join(output_dir, f'heating_fuel_map_{year}.pdf')
    
    if verbose:
        print(f"  Saving to: {output_dir}")
    
    fig.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    fig.savefig(pdf_path, bbox_inches='tight', facecolor='white')
    
    if show_plot:
        plt.show()
    else:
        plt.close(fig)
    
    return png_path, pdf_path


# ===========================================================================
# USAGE EXAMPLE
# ============================================================================

def create_heating_fuel_grid(
    gdf_dict: Dict[int, Dict[str, gpd.GeoDataFrame]],
    gdf_states: gpd.GeoDataFrame,
    output_dir: str,
    years: Optional[List[int]] = None,
    include_alaska: bool = True,
    figsize: Tuple[int, int] = (30, 10),
    dpi: int = 600,
    verbose: bool = False
) -> Tuple[str, str]:
    """
    Create horizontal grid of heating fuel maps for multiple years.
    
    Args:
        gdf_dict: Nested dict like {2015: {'conus': gdf, 'alaska': gdf}, ...}
        gdf_states: GeoDataFrame with state boundaries
        output_dir: Directory for saving outputs
        years: List of years to plot. If None, uses all years in gdf_dict
        include_alaska: Whether to add Alaska insets
        figsize: Figure size (width, height) in inches
        dpi: Resolution for PNG output
        verbose: Print progress messages
        
    Returns:
        Tuple of (png_path, pdf_path) for saved files
        
    Raises:
        ValueError: If years not found in gdf_dict or required data missing
    """
    # ============================================================
    # INPUT VALIDATION
    # ============================================================
    if years is None:
        years = sorted(gdf_dict.keys())
    
    for year in years:
        if year not in gdf_dict:
            raise ValueError(f"Year {year} not found in gdf_dict")
        if 'conus' not in gdf_dict[year]:
            raise ValueError(f"Missing 'conus' data for year {year}")
        if include_alaska and 'alaska' not in gdf_dict[year]:
            raise ValueError(f"Missing 'alaska' data for year {year}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # ============================================================
    # CALCULATE LAYOUT GEOMETRY
    # ============================================================
    num_plots = len(years)
    
    # Subplot dimensions (as fraction of figure)
    subplot_width = 0.28      # 28% width per subplot
    subplot_height = 0.70     # 70% height
    top_margin = 0.08         # Space for overall title
    bottom_margin = 0.15      # Space below maps
    left_margin = 0.02        # Left edge buffer
    spacing = 0.03            # Gap between subplots
    
    # Alaska inset dimensions (relative to each subplot)
    alaska_width_ratio = 0.35   # 35% of subplot width
    alaska_height_ratio = 0.35  # 35% of subplot height
    
    if verbose:
        print(f"\nCreating {num_plots}-panel grid...")
        print(f"  Subplot dimensions: {subplot_width:.2%} × {subplot_height:.2%}")
    
    # ============================================================
    # CREATE FIGURE AND AXES
    # ============================================================
    fig = plt.figure(figsize=figsize, facecolor='white')
    
    axes_main = []
    axes_alaska = []
    
    for i, year in enumerate(years):
        # Calculate left position for this subplot
        left = left_margin + i * (subplot_width + spacing)
        
        # Create main map axes
        ax_main = fig.add_axes([
            left, 
            bottom_margin, 
            subplot_width, 
            subplot_height
        ])
        axes_main.append(ax_main)
        
        # Create Alaska inset if requested
        if include_alaska:
            alaska_width = subplot_width * alaska_width_ratio
            alaska_height = subplot_height * alaska_height_ratio
            
            ax_alaska = fig.add_axes([
                left,
                bottom_margin,
                alaska_width,
                alaska_height
            ])
            axes_alaska.append(ax_alaska)
        else:
            axes_alaska.append(None)
    
    # ============================================================
    # PLOT EACH YEAR
    # ============================================================
    if verbose:
        print(f"\nRendering {num_plots} maps...")
    
    for i, year in enumerate(years):
        if verbose:
            print(f"\n  [{i+1}/{num_plots}] Year {year}")
        
        # Use existing plot_heating_fuel_map() function
        plot_heating_fuel_map(
            gdf_conus=gdf_dict[year]['conus'],
            gdf_alaska=gdf_dict[year].get('alaska'),
            gdf_states=gdf_states,
            year=year,
            ax_main=axes_main[i],
            ax_alaska=axes_alaska[i],
            show_title=True,
            verbose=verbose
        )
    
    # ============================================================
    # ADD SHARED LEGEND (Figure-level)
    # ============================================================
    # Position legend to the right of the last subplot
    legend_x = left_margin + num_plots * (subplot_width + spacing) - spacing + 0.02
    legend_y = 0.50  # Vertically centered
    
    fig.legend(
        handles=create_legend_elements(),
        title='Primary Heating Fuel\n(by census tract)',
        loc='center',
        bbox_to_anchor=(legend_x, legend_y),
        bbox_transform=fig.transFigure,
        fontsize=11,
        title_fontsize=12,
        frameon=True,
        edgecolor='black',
        fancybox=False
    )
    
    # ============================================================
    # ADD OVERALL TITLE
    # ============================================================
    year_range = f"{min(years)}–{max(years)}"
    fig.text(
        0.5, 0.96,
        f'Evolution of Primary Heating Fuels, {year_range}',
        ha='center',
        va='top',
        fontsize=26,
        fontweight='bold',
        transform=fig.transFigure
    )
    
    # ============================================================
    # SAVE OUTPUTS
    # ============================================================
    filename_base = f"heating_fuel_grid_{min(years)}_{max(years)}"
    png_path = os.path.join(output_dir, f'{filename_base}.png')
    pdf_path = os.path.join(output_dir, f'{filename_base}.pdf')
    
    if verbose:
        print(f"\n  Saving to: {output_dir}")
    
    fig.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    fig.savefig(pdf_path, bbox_inches='tight', facecolor='white')
    
    if verbose:
        print(f"  ✓ Grid complete!")
    
    plt.show()
    plt.close(fig)
    
    return png_path, pdf_path

