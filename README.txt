================================================================================
PRIMARY HEATING FUEL BY CENSUS TRACT: 2015, 2020, AND 2023
Mapping Analysis of U.S. Housing Heating Fuel Sources
================================================================================

PROJECT OVERVIEW
----------------
This project maps the dominant primary heating fuel type used in occupied 
housing units across U.S. census tracts for three time periods: 2015, 2020, 
and 2023. The analysis reveals geographic patterns in residential heating 
fuel preference and changes over time.

AUTHOR INFORMATION
------------------
Name: Jordan M. Joseph, PhD
Affiliation: Carnegie Mellon University
Date Created: September 2025
Last Updated: October 2025
Contact: jordanjoseph53@gmail.com



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

FOLDER STRUCTURE
----------------
data/raw/          - Original unmodified data files
02_qgis_projects/     - QGIS project files (.qgz)
03_outputs/           - Final map exports
04_documentation/     - Additional guides and notes
05_supplementary/     - Supporting materials

QUICK START GUIDE
-----------------
1. Extract all files maintaining the folder structure
2. Open QGIS
3. Navigate to 02_qgis_projects/
4. Open any .qgz file (e.g., 2015_heating_fuel_analysis.qgz)
5. If prompted about missing files, browse to data/raw/ to locate them
6. View the map or modify as needed
7. See 04_documentation/replication_guide.pdf for detailed instructions

KEY FINDINGS
------------
[You can add 2-3 sentences about what the maps show]
- Example: Fuel oil heating is heavily concentrated in the Northeast
- Natural gas dominates the Midwest and Mid-Atlantic regions
- Electricity is the primary heating source across the South

CITATION
--------
If you use this work, please cite:
[Your citation format]

LICENSE
-------
[Specify: Public domain, CC-BY, All Rights Reserved, etc.]

NOTES AND LIMITATIONS
---------------------
- Census tract boundaries can change between survey periods; this analysis
  uses 2015 boundaries consistently for temporal comparison
- Alaska is shown as an inset and not to scale
- Hawaii and PR are not shown because most census tracts have no heating fuel (warm, tropical climates)
- Dominant fuel type is defined as the heating fuel used by the plurality
  of housing units in each tract

CONTACT
-------
For questions or issues replicating this analysis:
jordanjo@alumni.cmu.edu

================================================================================
