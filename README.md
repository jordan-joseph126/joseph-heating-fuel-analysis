# Heating Fuel Analysis: US Census Tracts

Analysis of residential heating fuel usage patterns across US census tracts using American Community Survey (ACS) 5-year estimates from NHGIS.

## Project Overview

This project analyzes and visualizes the dominant residential heating fuel types (natural gas, electricity, fuel oil, etc.) across US census tracts for three time periods: 2011-2015, 2016-2020, and 2019-2023.

**Author:** Jordan M. Joseph, PhD  
**Contact:** jordanjo@alumni.cmu.edu

## Project Structure
```
joseph-heating-fuel-analysis/
├── data/                                       # FOUND ON ZENODO
│   ├── raw_data_and_codebook/                  # NHGIS census data
│   ├── boundaries/                             # Shapefiles
│   └── tables/                                 # Processed data tableS
├── outputs/
│   ├── maps/                                   # Generated maps (empty directory)
│   └── print_layouts/                          # Print-ready outputs (empty directory)
├── scripts/                                    # Main Python package
│   ├── __init__.py
│   ├── process_data.py                         # Data processing functions
│   └── visualize_geospatial_data.py            # Mapping and visualization functions
├── environment.yml                             # Conda environment specification
├── requirements.txt                            # Pip requirements
├── setup.py                                    # Package installation configuration
├── config.py                                   # Project paths configuration
├── visualize_us_primary_heating_fuels.ipynb    # Main notebook
└── README.md                      # This file
```

## Getting Started

### Prerequisites

- [Anaconda](https://www.anaconda.com/products/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- Git

### Installation

1. **Clone the repository:**
```bash
   git clone https://github.com/YOUR_USERNAME/joseph-heating-fuel-analysis.git
   cd joseph-heating-fuel-analysis
```

2. **Create conda environment:**
```bash
   conda env create -f environment.yml
   conda activate heating-fuel-analysis
```

3. **Install package in development mode:**
```bash
   pip install -e .
```

4. **Verify installation:**
```bash
   python -c "import heating_fuel_analysis; print('✓ Installation successful!')"
```

### Data Acquisition

**Note:** Data files are not included in this repository due to size constraints.

DATA SOURCES
------------
1. Housing Unit Heating Fuel Data:
   - Source: NHGIS (National Historical Geographic Information System)
   - URL: https://www.nhgis.org
   - Dataset: American Community Survey (ACS) 5-Year Estimates
   - Tables: B25040 (House Heating Fuel)
   - Years: 2011-2015, 2016-2020, 2019-2023
   - Downloaded: [Date you downloaded]

2. Census Tract Boundaries:
   - Source: NHGIS
   - Year: 2015 TIGER/Line Shapefiles
   - Note: 2015 boundaries used for all three time periods

3. State Boundaries:
   - Source: NHGIS
   - Year: 2015 TIGER/Line Shapefiles

## Usage

### Running the Analysis

1. **Launch Jupyter Lab:**
```bash
   jupyter lab
```

2. **Open the main notebook:**
   - Navigate to `visualize_us_primary_heating_fuels.ipynb`

3. **Run all cells** to:
   - Process raw census data
   - Calculate heating fuel percentages
   - Identify dominant fuel types by tract
   - Generate maps and visualizations

### Output Files

Maps and visualizations will be saved to:
- `outputs/maps/` - Individual year maps and comparison grids
- Format: Both PNG (for viewing) and PDF (for publication)

## Dependencies

### Core Packages
- Python ≥3.10, <3.13
- pandas ≥1.3.0
- numpy ≥1.20.0
- geopandas ≥0.10.0
- matplotlib ≥3.4.0

See `environment.yml` for complete list.

## Documentation

### Key Functions

- `process_heating_fuel_data()`: Processes raw NHGIS data and calculates fuel percentages
- `create_heating_fuel_map()`: Generates individual year maps
- `create_heating_fuel_grid()`: Creates multi-year comparison grids

See function docstrings for detailed parameter descriptions.

## Contributing

This is a research project. For questions or collaboration inquiries, please contact the author.

## License

[Choose a license - MIT, Apache 2.0, GPL, etc.]

## Acknowledgments

- **Data Source:** IPUMS NHGIS, University of Minnesota (www.nhgis.org)
- **Citation:** 
```
  Jonathan Schroeder, David Van Riper, Steven Manson, Katherine Knowles, 
  Tracy Kugler, Finn Roberts, and Steven Ruggles. IPUMS National Historical 
  Geographic Information System: Version 20.0 [dataset]. Minneapolis, MN: 
  IPUMS. 2025. http://doi.org/10.18128/D050.V20.0
```
- **Tools:** Claude AI and GitHub Copilot assisted with code documentation

## Contact

**Jordan M. Joseph, PhD**  
Email: jordanjo@alumni.cmu.edu

---

*This project was created to replicate and extend analysis originally performed in Excel and QGIS.*