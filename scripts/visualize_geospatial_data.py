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


def split_state_boundaries(
    gdf_states: gpd.GeoDataFrame
) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Split state boundaries into CONUS and Alaska for mapping.
    
    Args:
        gdf_states: GeoDataFrame with all state boundaries
        
    Returns:
        Tuple of (state_conus, state_alaska) GeoDataFrames
        
    Raises:
        ValueError: If state column not found
    """
    state_col = detect_state_column(gdf_states)
    
    state_conus = gdf_states[~gdf_states[state_col].isin(['AK', 'HI', 'PR'])]
    state_alaska = gdf_states[gdf_states[state_col] == 'AK']
    
    return state_conus, state_alaska


def save_figure(
    fig: plt.Figure,
    output_dir: str,
    filename_base: str,
    dpi: int = 600,
    show_plot: bool = True,
    verbose: bool = False
) -> Tuple[str, str]:
    """
    Save matplotlib figure as PNG and PDF.
    
    Args:
        fig: Matplotlib figure to save
        output_dir: Directory for output files
        filename_base: Base filename without extension
        dpi: Resolution for PNG output
        show_plot: Whether to display the plot
        verbose: Print save location
        
    Returns:
        Tuple of (png_path, pdf_path)
    """
    png_path = os.path.join(output_dir, f'{filename_base}.png')
    pdf_path = os.path.join(output_dir, f'{filename_base}.pdf')
    
    if verbose:
        print(f"  Saving to: {output_dir}")
    
    save_kwargs = {'bbox_inches': 'tight', 'facecolor': 'white'}
    
    fig.savefig(png_path, dpi=dpi, **save_kwargs)
    fig.savefig(pdf_path, **save_kwargs)
    
    if show_plot:
        plt.show()
    else:
        plt.close(fig)
    
    return png_path, pdf_path


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
    state_conus, state_alaska = split_state_boundaries(gdf_states)
    
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
        
        state_alaska.boundary.plot(
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
            # Increased from 14 to 20 and made bold for better visibility
            fontsize=20,
            fontweight='bold'
        )


# ============================================================================
# CREATE SINGLE YEAR MAP
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
        # Moved legend lower to allow for larger text and avoid overlap. Originally (0.80, 0.55)
        bbox_to_anchor=(0.78, 0.30),
        bbox_transform=fig.transFigure,
        # Increased from 11 to 16, and title from 12 to 17
        fontsize=16,              
        title_fontsize=17,
        frameon=True,
        edgecolor='black'
    )
    
    # Save outputs (SIMPLIFIED - single function call)
    return save_figure(
        fig=fig,
        output_dir=output_dir,
        filename_base=f'heating_fuel_map_{year}',
        dpi=dpi,
        show_plot=show_plot,
        verbose=verbose
    )


# ===========================================================================
# CREATE MULTI-YEAR GRID MAP
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
    # CREATE FIGURE WITH AUTOMATIC SUBPLOT GRID
    # ============================================================
    num_plots = len(years)
    
    if verbose:
        print(f"\nCreating {num_plots}-panel grid...")
    
    # Use matplotlib's built-in subplot grid (MUCH SIMPLER!)
    fig, axes_main = plt.subplots(
        nrows=1, 
        ncols=num_plots,
        figsize=figsize,
        facecolor='white',
        gridspec_kw={
            'wspace': 0.05,    # Horizontal space between subplots (5%)
            'hspace': 0.0      # No vertical space (single row)
        }
    )
    
    # Adjust margins to minimize white space
    fig.subplots_adjust(
        left=0.01,      # Minimal left margin
        right=0.99,     # Minimal right margin  
        top=0.98,       # Minimal top margin
        bottom=0.08     # Space for legend at bottom
    )
    
    # Convert to list if single subplot (for consistent indexing)
    if num_plots == 1:
        axes_main = [axes_main]
    
    # ============================================================
    # CREATE ALASKA INSETS (positioned relative to each subplot)
    # ============================================================
    axes_alaska = []
    
    if include_alaska:
        for i, ax in enumerate(axes_main):
            # Get subplot position in figure coordinates
            bbox = ax.get_position()
            
            # Alaska inset: bottom-left corner of each subplot
            # Width: 35% of subplot width
            # Height: 35% of subplot height
            ax_alaska = fig.add_axes([
                bbox.x0,                    # Left edge of subplot
                bbox.y0,                    # Bottom edge of subplot
                bbox.width * 0.35,          # 35% of subplot width
                bbox.height * 0.35          # 35% of subplot height
            ])
            axes_alaska.append(ax_alaska)
    else:
        axes_alaska = [None] * num_plots
    
    # ============================================================
    # PLOT EACH YEAR
    # ============================================================
    if verbose:
        print(f"\nRendering {num_plots} maps...")
    
    for i, year in enumerate(years):
        if verbose:
            print(f"\n  [{i+1}/{num_plots}] Year {year}")
        
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
    # ADD SHARED LEGEND (horizontal at bottom)
    # ============================================================
    fig.legend(
        handles=create_legend_elements(),
        title='Primary Heating Fuel (by census tract)',
        loc='lower center',
        bbox_to_anchor=(0.5, -0.01),
        ncol=7,
        fontsize=20,
        title_fontsize=22,
        frameon=True,
        edgecolor='black',
        fancybox=False
    )
    
    # ============================================================
    # SAVE OUTPUTS (SIMPLIFIED - single function call)
    # ============================================================
    filename_base = f"heating_fuel_grid_{min(years)}_{max(years)}"
    
    if verbose:
        print(f"  Grid complete!")
    
    return save_figure(
        fig=fig,
        output_dir=output_dir,
        filename_base=filename_base,
        dpi=dpi,
        show_plot=True,  # Grid always shows
        verbose=verbose
    )
