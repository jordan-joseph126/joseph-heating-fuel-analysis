# joseph-heating-fuel-analysis
Mapping Analysis of Primary Residential Heating Fuels Across U.S. Census Tracts

---

# Table of Contents
## Table of Contents
1. [Section 1: Installation and Setup](#section-1-installation-and-setup)
  1. [1.0 Prerequisites and Check Conda](#10-prerequisites-and-check-conda)
  2. [1.1 Software Installation](#11-software-installation)   
    - [Git for Windows](#git-for-windows)   
    - [Anaconda Navigator](#anaconda-navigator)   
    - [Visual Studio Code](#visual-studio-code)   
    - [Fix PATH Integration (Critical Step)](#fix-path-integration-critical-step)   
    - [Install VS Code Extensions](#install-vs-code-extensions)
  3. [1.2 Repository Access](#12-repository-access)
  4. [1.3 Repository Structure](#13-repository-structure)
  5. [1.4 Data Download](#14-data-download)
  6. [1.5 Environment Setup](#15-environment-setup)   
    - [First-Time Setup](#first-time-setup)   
    - [Register Jupyter Kernel](#register-jupyter-kernel)
  7. [1.6 Daily Usage](#16-daily-usage)
  8. [1.7 Troubleshooting](#17-troubleshooting)
  9. [1.8 Environment Maintenance](#18-environment-maintenance)

2. [Section 2: Version Information and Attribution](#section-2-version-information-and-attribution)
  1. [2.1 Version Information](#21-version-information)
  2. [2.2 Licensing and Attribution](#22-licensing-and-attribution)

---

# Project Overview

This project analyzes and visualizes the dominant residential heating fuel types (natural gas, electricity, fuel oil, propane, wood, etc.) across US census tracts for three time periods based on American Community Survey (ACS) 5-year estimates:
- **2011-2015** (referred to as "2015")
- **2016-2020** (referred to as "2020")
- **2019-2023** (referred to as "2023")

The analysis processes raw NHGIS (National Historical Geographic Information System) census data, calculates heating fuel percentages by census tract, identifies dominant fuel types, and generates publication-quality choropleth maps showing geographic patterns across the continental United States and Alaska.

**Author:** Jordan M. Joseph, PhD   
**Affiliation:** Carnegie Mellon University  
**Contact for Support and Questions:** jordanjo@alumni.cmu.edu, jordanjoseph53@gmail.com  
**For Repository Issues:** GitHub Issues page (for bug reports, feature requests)

**Acknowledgement:** 

This README and the codebase supports the Dataset Article submitted to Environmental Research Energy (ERE): "Determining U.S. residential primary heating fuels for energy analysis and planning"

Co-authors on this article are:

- **Constantine Samaras, PhD:** Writing – review & editing, Conceptualization, Project administration, Methodology

- **Destenie Nock, PhD:** Writing – review & editing

The authors acknowledge funding from Carnegie Mellon University’s Department of Civil and Environmental Engineering and Wilton E. Scott Institute for Energy Innovation. Claude AI and GitHub Copilot were used to improve documentation throughout this codebase, including explanatory comments and function documentation (type hints, Google-style docstrings). 

**Data Availability**
The raw data used in this study are publicly available from NHGIS under their data use agreement. Registration is required but is free for research and educational purposes. 

The data used in the data analysis workflow is publicly available on Zenodo under the GNU GPLv3 license. Zenodo repository: https://doi.org/10.5281/zenodo.17706631

**Code Availability**
The analysis code and visualization tools are publicly available in the GitHub repository under the GNU GPLv3 license. GitHub repository: https://github.com/jordan-joseph126/joseph-heating-fuel-analysis.git


**An important note about setting up and running the codebase on different OS:**
- Setup and troubleshooting steps were created using a Windows PC. There may be slight differences for users on other OS. If this causes issues, consider using Claude, GitHub copilot, or another tool to debug the OS specific issue. If issues persist, please reach out using this contact information: jordanjo@alumni.cmu.edu, jordanjoseph53@gmail.com  
- Collaborators are welcomed to contribute the issue (and the resolution steps) on the issues page so that the code base can be updated to ensure accessibility to all users.

---

# Section 1: Installation and Setup

## 1.0 Prerequisites and Check Conda

**IMPORTANT:** Before proceeding with software installation or environment setup, verify that you have a working Anaconda/Miniconda installation and that conda's package resolver is functioning correctly.

### Why This Matters

Conda uses a "solver" to figure out which package versions can coexist when creating environments. If the solver has version conflicts (common after Anaconda Navigator updates), environment creation may fail or produce errors. Fixing this BEFORE setup saves significant troubleshooting time.

### Check Conda

If you already have Anaconda or Miniconda installed, run this test:

```bash
# Open Anaconda Prompt (Windows) or Terminal (Mac/Linux)
conda --version
```

** Good Output (Working):**
```
conda 25.9.1
```
Just the version number with no errors.

** Problem Output (Needs Fixed):**
```
Error while loading conda entry point: conda-libmamba-solver
(module 'libmambapy' has no attribute 'QueryFormat')
conda 24.11.3
```
If you see error messages before the version number, continue to the fix below.

#### Fixing Conda Solver Errors

If you saw errors in the Conda check, fix them now:

**Step 1: Ensure base environment is active**
```bash
conda activate base
```

**Step 2: Update solver components together**
```bash
conda update -n base conda conda-libmamba-solver libmambapy
```

This downloads and installs compatible versions of all three components. Takes 2-5 minutes.

**Step 3: Verify the fix**
```bash
conda --version
```

Should now display only the version number with **NO error messages**.

**If the update fails or you prefer maximum stability:**

Switch to the classic (older, slower but rock-solid) solver:
```bash
conda config --set solver classic
```

You can always switch back to the faster libmamba solver later:
```bash
conda config --set solver libmamba
```

#### Understanding the Issue

**What's happening:** Anaconda Navigator updates can cause version mismatches between:
- `conda` itself (the package manager)
- `conda-libmamba-solver` (the fast dependency resolver plugin)
- `libmambapy` (the underlying library)

**Why it matters for this project:** When you run `conda env create -f environment.yml`, conda needs a working solver to figure out which versions of geospatial packages (geopandas, fiona, shapely, pyproj) can work together. A broken solver means:
-  Environment creation fails
-  Confusing error messages
-  Wasted setup time

**How the fix works:** The `conda update` command forces conda to find compatible versions of all three components at once, resolving the mismatch.

### If You Don't Have Anaconda Yet

Skip the Conda check steps for now and proceed to Section 1.1 to install Anaconda. After installation, return here and then check before attempting environment creation.

---

## 1.1 Software Installation

Install the following software in order before setting up the project environment:

### Git for Windows
**Download:** https://git-scm.com/download/win

**Installation settings:**
- Destination: Keep default (`C:\Program Files\Git`)
- Components: Enable Git LFS, associate .git* files, associate .sh files
- Default editor: **Visual Studio Code** (or Nano or another preferred program)
- Initial branch name: **Override to `main`**
- PATH environment: **Git from the command line and also from 3rd-party software** (Option 2)
- SSH executable: Use bundled OpenSSH
- HTTPS transport: Use OpenSSL library
- Line endings: **Checkout Windows-style, commit Unix-style** (Option 1)
- Terminal emulator: Use MinTTY
- `git pull` behavior: Default (fast-forward or merge)
- Credential helper: Git Credential Manager
- Extra options: Enable file system caching only (disable symbolic links)
- Experimental options: Leave all unchecked

**Configure Git identity: USE THE NAME AND EMAIL ASSOCIATED WITH YOUR GITHUB ACCOUNT**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Verify:**
```bash
git --version
git config --global --list
```

### Anaconda Navigator
**Download:** https://www.anaconda.com/download

**Installation settings:**
- Install type: **Just Me (recommended)**
- Destination: Keep default (`C:\Users\YourName\anaconda3`)
- Advanced options:
  -  **DO NOT** check "Add Anaconda3 to my PATH environment variable"
  -  **CHECK** "Register Anaconda3 as my default Python"

**Why not add to PATH?** Keeps Anaconda isolated, prevents conflicts with other software, and follows Anaconda's recommended best practice.

**Verify:**
```bash
# In regular Command Prompt - should fail
conda --version  # Expected: 'conda' is not recognized

# In Anaconda Prompt - should work
conda --version  # Expected: conda 25.X.X (with no errors)
python --version # Expected: Python 3.12.X or 3.13.X (base environment)
```

**IMPORTANT: After installation, go back to [Section 1.0](#10-prerequisites-and-check-conda) and run the conda check before proceeding.**

### Visual Studio Code
**Download:** https://code.visualstudio.com/download

**Installation settings:**
- Install type: User Installer (recommended)
- Destination: Keep default
- Additional tasks:
  -  Add "Open with Code" action to file context menu
  -  Add "Open with Code" action to directory context menu
  -  Register Code as an editor for supported file types
  -  **Add to PATH (requires shell restart)** ← CRITICAL for `code .` command

**Verify:**
```bash
# In new Command Prompt
code --version
```

### Fix PATH Integration (Critical Step)

After installing VS Code, Anaconda Prompt may not recognize the `code` command. Fix this:

```bash
# In Anaconda Prompt, run:
conda init powershell
```

Close and reopen Anaconda Prompt, then verify:
```bash
code --version  # Should now work
git --version   # Should also work
```

**Why this fix is needed:** Anaconda Prompt needs proper PowerShell initialization to preserve system PATH entries (including VS Code and Git) while adding conda directories.

### Install VS Code Extensions

Open Anaconda Prompt and run:
```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.debugpy
code --install-extension ms-toolsai.jupyter
code --install-extension ms-toolsai.jupyter-renderers
code --install-extension ms-toolsai.vscode-jupyter-cell-tags
code --install-extension ms-toolsai.jupyter-keymap
code --install-extension mechatroner.rainbow-csv
```

Or install via VS Code GUI: Extensions sidebar (`Ctrl+Shift+X`) → Search for each extension → Install.

## 1.2 Repository Access

**Repository Location:** https://github.com/jordan-joseph126/joseph-heating-fuel-analysis
**Status:** Public repository

**Access Options:**

**Option 1 - Git Clone (recommended):**
```bash
# Navigate to where you want the project folder
cd C:\Users\YourName\Documents\Research

# Clone repository (creates 'joseph-heating-fuel-analysis' folder)
git clone https://github.com/jordan-joseph126/joseph-heating-fuel-analysis.git
cd joseph-heating-fuel-analysis
```

**Advantages:** Easy updates (`git pull`), track changes, version history, simplified collaboration

**Option 2 - Download ZIP:**
1. Navigate to repository URL
2. Click "Code" → "Download ZIP"
3. Extract to your preferred location

Best for: One-time use or if you don't have Git installed

## 1.3 Repository Structure

```
joseph-heating-fuel-analysis/
├── scripts/                                   # Main Python package
│   ├── __init__.py
│   ├── process_data.py                        # Data processing functions
│   └── visualize_geospatial_data.py           # Mapping and visualization functions
├── data/                                      # Input data (download separately from NHGIS)
│   ├── raw_data_and_codebook/                 # NHGIS census data
│   │   └── nhgis0011_csv/                     # Raw CSV files
│   │       ├── nhgis0011_ds215_20155_tract.csv  # 2011-2015 data
│   │       ├── nhgis0011_ds249_20205_tract.csv  # 2016-2020 data
│   │       └── nhgis0011_ds267_20235_tract.csv  # 2019-2023 data
│   ├── boundaries/                            # Shapefiles
│   │   └── nhgis0011_shape/
│   │       ├── nhgis0011_shapefile_tl2015_us_state_2015/
│   │       ├── nhgis0011_shapefile_tl2015_us_tract_2015/
│   │       ├── nhgis0011_shapefile_tl2020_us_tract_2020/
│   │       └── nhgis0011_shapefile_tl2023_us_tract_2023/
│   └── __init__.py
├── outputs/                                   # Generated outputs (created on run)
│   └── maps/                                  # Generated maps
├── visualize_us_primary_heating_fuels.ipynb   # MAIN ENTRY POINT
├── environment.yml                            # Conda environment specification
├── requirements.txt                           # Pip requirements
├── setup.py                                   # Package installation script
├── config.py                                  # Project paths configuration
├── __init__.py                                # Package initialization
└── README.md                                  # This file
```

**Key Entry Points:**
- **Main Analysis:** `visualize_us_primary_heating_fuels.ipynb` - Start here for the primary mapping analysis
- **Additional Analysis:** `energy_consumption_chart.ipynb` - Supplementary energy consumption visualizations
- **Functions/Modules:**
  - `scripts/process_data.py` - Data processing, fuel percentage calculations, dominant fuel identification
  - `scripts/visualize_geospatial_data.py` - Choropleth mapping functions with Alaska inset

## 1.4 Data Download

The raw data used in this study are publicly available from NHGIS under their data use agreement. Registration is required but is free for research and educational purposes. 

The data used in the data analysis workflow is publicly available on Zenodo under the GNU GPLv3 license. The data directory, organized in the appropriate file path structure, is available here: https://doi.org/10.5281/zenodo.17706631

The Zenodo data folder contains the data required to run the joseph-heating-fuel-analysis GitHub repo code (not included in the Github repository).  
1. Download the data from this page  
2. Extract all files from the zipped folder  
3. Copy and paste the folder contents in the empty folder at the following path: [YOUR_PATH]/joseph-heating-fuel-analysis

**OPTIONAL:** 
If you choose to download the files (e.g., for a different 5-year dataset), be sure to read the note in the config.py file about updating the file paths. The data acquisition process is outlined below:

1. Register for a free account at NHGIS (https://www.nhgis.org).   
2. Use the Data Finder to select:
    -	Geographic level: Census Tract, State
    -	Years: 2015 (2011-2015), 2020 (2016-2020), 2023 (2019-2023)
    -	Topic: Heating, Cooling, and Fuels
3. In the “SOURCE TABLES” tab under “SELECT DATA”:
    -	Find the rows with Table: B25040 (House Heating Fuel) under Table Name and the listed “Year – Dataset” options of interest.
      -	Click the green plus sign to the left of those rows.
4. Then click the “GIS FILES” tab under “SELECT DATA” to add the 2015, 2020, and 2023 Census Tract shapefiles (TIGER/Line + under “BASIS”). Also, select one of the State options (we chose 2015).
5. Click the “CONTINUE” button in the top right corner. Review the selections and click “CONTINUE” again. 
6. Check the descriptive header row box and hit submit.


**Expected directory structure after extraction:**
```
data/
├── raw_data_and_codebook/
│   └── nhgis0011_csv/
│       ├── nhgis0011_ds215_20155_tract.csv
│       ├── nhgis0011_ds249_20205_tract.csv
│       └── nhgis0011_ds267_20235_tract.csv
├── boundaries/
│   └── nhgis0011_shape/
│       ├── nhgis0011_shapefile_tl2015_us_state_2015/
│       ├── nhgis0011_shapefile_tl2015_us_tract_2015/
│       ├── nhgis0011_shapefile_tl2020_us_tract_2020/
│       └── nhgis0011_shapefile_tl2023_us_tract_2023/
└── __init__.py
```

**Note:** The exact file paths in `config.py` may need adjustment based on your NHGIS extract filenames.

## 1.5 Environment Setup

**PREREQUISITE:** Before proceeding, ensure you completed the [conda check steps in Section 1.0](#10-prerequisites-and-check-conda). If `conda --version` shows errors, fix them first.

### First-Time Setup

**Step 1: Create the Conda Environment**

```bash
# Navigate to project directory
cd /path/to/joseph-heating-fuel-analysis

# Create environment from .yml file
conda env create -f environment.yml
```

**What this does:** Creates an isolated Python 3.10-3.12 environment with all required packages including:
- **Core data processing:** pandas, numpy
- **Geospatial stack:** geopandas, fiona, shapely, pyproj, rtree
- **Visualization:** matplotlib, seaborn, contextily
- **Notebook environment:** jupyter, jupyterlab, ipykernel

**Expected behavior:**
- Downloads and installs 50+ packages
- Takes 5-10 minutes
- Should complete with **no error messages**

**If you see errors during creation:** Your conda solver may still have issues. Return to [Section 1.0](#10-prerequisites-and-check-conda) and verify the fix worked.

**Step 2: Activate the Environment**

```bash
conda activate joseph-heating-fuel-env
```

Your prompt should now show `(joseph-heating-fuel-env)`.

**Step 3: Install Project Package**

```bash
pip install -e .
```

**What this does:** Installs your project as a Python package so you can import modules like `config` and functions from `scripts` from any notebook.

### Register Jupyter Kernel

```bash
python -m ipykernel install --user --name=joseph-heating-fuel-env --display-name "Python (Heating Fuel Analysis)"
```

**What this does:** Makes this environment available in VS Code's kernel selector.

**You only need to do this once** unless you recreate the environment.

### Verify Installation

```bash
# Check Python version
python --version  # Should output: Python 3.10.X, 3.11.X, or 3.12.X

# Test core packages
python -c "import pandas; import numpy; import geopandas; import matplotlib; print('Core packages OK!')"

# Test project imports
python -c "from config import PROJECT_ROOT; print(f'PROJECT_ROOT: {PROJECT_ROOT}')"
python -c "from scripts.process_data import process_heating_fuel_data; print('Project package OK!')"
```

**Success indicators:** All commands complete without errors and display the expected output.

## 1.6 Daily Usage

### Launching the Project

**Recommended method** (ensures proper environment detection):

```bash
# 1. Open Anaconda Prompt
# 2. Activate environment
conda activate joseph-heating-fuel-env

# 3. Navigate to project
cd /path/to/joseph-heating-fuel-analysis

# 4. Launch VS Code
code .
```


### Running Notebooks

1. Open `visualize_us_primary_heating_fuels.ipynb`
2. Click kernel selector (top-right corner)
3. Select **"Python (Heating Fuel Analysis)"**
4. Verify `(joseph-heating-fuel-env)` appears in kernel indicator
5. Run cells sequentially from top to bottom

**What the main notebook does:**
- Loads raw NHGIS heating fuel data for all three time periods
- Processes data to calculate fuel percentages by census tract
- Identifies dominant fuel type (handles ties and missing data)
- Loads census tract shapefiles and merges with processed data
- Generates choropleth maps showing geographic patterns
- Creates multi-year comparison grids
- Exports maps to `outputs/maps/` in both PNG and PDF formats

## 1.7 Troubleshooting

### ISSUE 1: Conda Issues (Solver Errors)

**Symptoms:**
- `conda env create` fails or shows warnings
- Messages about "conda entry point" or "libmambapy"
- Package resolution takes extremely long

**Solution:** See [Section 1.0: Prerequisites and Check Conda](#10-prerequisites-and-check-conda)

This issue affects conda itself (base environment), not your project environment. Fix it in the base environment before creating project environments.

---

### ISSUE 2: `code` Command Not Working in Anaconda Prompt

**Symptoms:** `code --version` works in Command Prompt but fails in Anaconda Prompt with "'code' is not recognized"

**Solution:**
```bash
# In Anaconda Prompt:
conda init powershell
```

Close and reopen Anaconda Prompt. The `code` command should now work.

**Why this happens:** Anaconda Prompt's initialization may not preserve system PATH entries. Running `conda init powershell` creates a proper PowerShell profile that preserves VS Code's PATH entry while adding conda directories.

---

### ISSUE 3: `ModuleNotFoundError: No module named 'config'` or `'scripts'`

**Cause:** Project package not installed in editable mode.

**Solution:**
```bash
conda activate joseph-heating-fuel-env
cd /path/to/joseph-heating-fuel-analysis
pip install -e .
```

Then **restart the Jupyter kernel** in VS Code: Click kernel indicator → Restart Kernel

**Why this happens:** Python needs to know where to find your project modules. `pip install -e .` tells Python "this directory contains importable packages."

---

### ISSUE 4: Wrong Python Version

**Cause:** Environment wasn't created correctly or wrong environment is active.

**Check which environment is active:**
```bash
conda env list
# Look for the * symbol showing active environment
```

**Solution:** Recreate the environment
```bash
conda deactivate
conda env remove -n joseph-heating-fuel-env
conda env create -f environment.yml
```

Then repeat Steps 2-4 from Section 1.5.

---

### ISSUE 5: Jupyter Kernel Not Available in VS Code

**Solution:** Re-register the kernel
```bash
conda activate joseph-heating-fuel-env
python -m ipykernel install --user --name=joseph-heating-fuel-env --display-name "Python (Heating Fuel Analysis)"
```

Then refresh VS Code's kernel list:
- Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
- Run: **"Jupyter: Select Interpreter to Start Jupyter Server"**
- Choose the joseph-heating-fuel-env environment

---

### ISSUE 6: Kernel Crashes or Keeps Restarting

**Solutions:**
1. Clear all kernels: `Ctrl+Shift+P` → "Jupyter: Clear All Kernels"
2. Close all notebooks in VS Code
3. Restart VS Code
4. Reopen notebook and select kernel

---

### ISSUE 7: VS Code Doesn't Detect Conda Environment

**Primary solution:** Launch VS Code from Anaconda Prompt (see Section 1.6)

**Alternative:**
1. Press `Ctrl+Shift+P`
2. Run: **"Python: Select Interpreter"**
3. Manually select: `[path-to-anaconda]/envs/joseph-heating-fuel-env/python.exe`

**Typical paths:**
- Windows: `C:\Users\YourName\anaconda3\envs\joseph-heating-fuel-env\python.exe`
- Mac: `/Users/YourName/anaconda3/envs/joseph-heating-fuel-env/bin/python`
- Linux: `/home/YourName/anaconda3/envs/joseph-heating-fuel-env/bin/python`

---

### ISSUE 8: Environment Creation Hangs or Takes Very Long

**Cause:** Conda solver is working but struggling with dependency resolution (common with geospatial packages).

**Solutions:**

1. **Switch to classic solver** (slower but more reliable):
   ```bash
   conda config --set solver classic
   conda env create -f environment.yml
   ```

2. **Use mamba** (faster alternative):
   ```bash
   conda install -n base mamba
   mamba env create -f environment.yml
   ```

3. **Create with explicit channels**:
   ```bash
   conda env create -f environment.yml --channel conda-forge
   ```

---

### ISSUE 9: GeoPandas / Fiona Installation Errors

**Cause:** Geospatial packages require compiled C libraries that can be difficult to build on Windows.

**Solution:** Always use conda (NOT pip) for geospatial packages:
```bash
conda install -c conda-forge geopandas fiona shapely pyproj rtree
```

The `conda-forge` channel provides pre-compiled binaries for Windows, avoiding compilation issues.

---

### ISSUE 10: Data File Path Errors

**Symptoms:** `FileNotFoundError` when running the notebook

**Solution:** Check `config.py` paths match your actual data structure:
```bash
# Edit config.py if your NHGIS extract has different filenames
# Update RAW_CSV_2015, RAW_CSV_2020, RAW_CSV_2023 paths
# Update TRACT_SHAPEFILE_2015, TRACT_SHAPEFILE_2020, TRACT_SHAPEFILE_2023 paths
```

**Common issue:** NHGIS extract numbers (e.g., `nhgis0011`) vary by download. Update `config.py` to match your actual filenames.

## 1.8 Environment Maintenance

### Adding New Packages

```bash
conda activate joseph-heating-fuel-env
conda install package-name
# Or: pip install package-name
```

To update the environment file:
```bash
conda env export --no-builds > environment.yml
```

**Best practice:** Use `conda install` for packages available through conda channels (faster, better dependency resolution). Use `pip install` only for packages not available through conda.

**For geospatial packages:** Always use `conda install -c conda-forge` to avoid compilation issues.

### Updating All Packages

```bash
conda activate joseph-heating-fuel-env
conda update --all
```

**Warning:** May cause version conflicts or break compatibility with notebooks. Always test thoroughly after updating.

**Safer approach:** Update specific packages individually and test between updates.

### Recreating Environment from Scratch

If your environment becomes corrupted or you want a clean slate:

```bash
# Remove old environment
conda env remove -n joseph-heating-fuel-env

# Recreate from .yml file
conda env create -f environment.yml

# Reinstall project package
conda activate joseph-heating-fuel-env
pip install -e .

# Re-register kernel
python -m ipykernel install --user --name=joseph-heating-fuel-env --display-name "Python (Heating Fuel Analysis)"
```

---

# Section 2: Version Information and Attribution

## 2.1 Version Information

**Version History:**
- **v1.0.0** (Current): Initial public release with comprehensive documentation

**Checking for Updates:**
```bash
git fetch origin
git pull origin main
python setup.py --version
```

## 2.2 Licensing and Attribution

**License:** GNU GPLv3 license

**Author:** Jordan M. Joseph, PhD   
**Affiliation:** Carnegie Mellon University   
**Contact:** jordanjo@alumni.cmu.edu, jordanjoseph53@gmail.com

**Citation (Suggested):**
```
Joseph, J.M. (2025). Heating Fuel Analysis: Mapping Primary Residential Heating Fuels Across U.S. Census Tracts. Carnegie Mellon University.
https://github.com/jordan-joseph126/joseph-heating-fuel-analysis
```

**Data Availability:**   
The raw data used in this study are publicly available from NHGIS under their data use agreement. Registration is required but is free for research and educational purposes. 

The data used in the data analysis workflow is publicly available on Zenodo under the GNU GPLv3 license. Zenodo repository: https://doi.org/10.5281/zenodo.17706631

**Code Availability:**   
The analysis code and visualization tools are publicly available in the GitHub repository under the GNU GPLv3 license. 

GitHub repository: https://github.com/jordan-joseph126/joseph-heating-fuel-analysis.git


**Intended Usage:**
- Research and academic use
- Modification and extension for research purposes
- Integration into other research projects
- Educational and teaching applications

**Attribution Requirements:**
- Cite this analysis in publications using the data or maps
- Reference the GitHub repository in code documentation
- Acknowledge Carnegie Mellon University as institutional affiliation
- Properly cite NHGIS data source (see below)

**Data Sources and Acknowledgments:**

This analysis uses publicly available data from IPUMS NHGIS:

```
Jonathan Schroeder, David Van Riper, Steven Manson, Katherine Knowles, Tracy Kugler, Finn Roberts, and Steven Ruggles. IPUMS National Historical Geographic Information System: Version 20.0 [dataset]. Minneapolis, MN:
IPUMS. 2025. http://doi.org/10.18128/D050.V20.0
```

**Primary Data Sources:**
```
[1]	 U.S. Census Bureau 2025 TIGER/Line Shapefiles (State and Census Tract Boundaries)
[2]	 U.S. Census Bureau 2016 Table B25040 (House Heating Fuel), American Community Survey 5-Year Estimates (2011-2015)
[3]	 U.S. Census Bureau 2021 Table B25040 (House Heating Fuel), American Community Survey 5-Year Estimates (2016-2020)
[4]	 U.S. Census Bureau 2024 Table B25040 (House Heating Fuel), American Community Survey 5-Year Estimates (2019-2023)
```

**Tools and Software:**
- Python geospatial stack (GeoPandas, Shapely, Fiona, PyProj)
- Matplotlib for visualization
- Jupyter for interactive analysis
- Claude AI and GitHub Copilot assisted with code documentation

---
