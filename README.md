# SPE1 Case 1 - OPM Flow Simulation

This repository contains scripts to run the SPE1 Case 1 benchmark using OPM Flow simulator with automated summary data extraction.

## Prerequisites

1. **Python 3.8+** with pip
2. **Docker** installed and running
3. **SPE1CASE1.DATA** file (original Eclipse deck)

## Installation

### Option 1: Using Conda (Recommended)
```bash
# Clone this repository
git clone <repo-url> spe1-case1
cd spe1-case1

# Run the setup script to create a conda environment
./setup.sh

# Activate the environment
conda activate spe1-case1
```

### Option 2: Using pip
```bash
# Clone this repository
git clone <repo-url> spe1-case1
cd spe1-case1

# Install Python dependencies
pip install -r requirements.txt
```

### Verify Installation
```bash
# Verify Docker is running
docker --version

# Test Python dependencies
python -c "import resdata, pandas, pyarrow; print('✅ All dependencies installed')"
```

## How to Run

### Step 1: Prepare the Data
Place your original SPE1CASE1.DATA file in the `data/` directory:
```bash
cp /path/to/SPE1CASE1.DATA data/
```

### Step 2: Patch the Deck
Add a comprehensive SUMMARY section to capture simulation outputs:
```bash
python scripts/patch_summary.py data/SPE1CASE1.DATA patched/SPE1CASE1_patched.DATA
```
This creates a new deck file with monitoring for:
- Grid state (pressure, saturations)
- Field production/injection rates
- Well performance metrics
- Solver diagnostics

### Step 3: Run the Simulation
Execute OPM Flow using Docker:
```bash
python scripts/run_simulation.py patched/SPE1CASE1_patched.DATA patched/
```
This will:
- Pull the OPM Flow Docker image (first run only)
- Mount your deck as read-only
- Run the simulation
- Save outputs to `patched/` directory

### Step 4: Extract Results
Convert binary UNSMRY data to Parquet format:
```bash
python scripts/extract_results.py patched/SPE1CASE1_patched.UNSMRY
```
This creates `SPE1CASE1_patched.parquet` with time-series data.

## Complete Workflow Example

```bash
# From the repository root
cd spe1-case1

# Install dependencies
pip install -r requirements.txt

# Assume SPE1CASE1.DATA is in ~/Downloads
cp ~/Downloads/SPE1CASE1.DATA data/

# Run the complete pipeline
python scripts/patch_summary.py data/SPE1CASE1.DATA patched/SPE1CASE1_patched.DATA
python scripts/run_simulation.py patched/SPE1CASE1_patched.DATA patched/
python scripts/extract_results.py patched/SPE1CASE1_patched.UNSMRY

# View results
ls -la patched/
# Should see: *.UNSMRY, *.SMSPEC, *.RSM, *.INIT, *.parquet, etc.
```

## Repository Structure

```
spe1-case1/
├── data/                       # Original decks (untouched)
│   └── SPE1CASE1.DATA         
├── patched/                    # Auto-generated, ignored by git
├── scripts/
│   ├── patch_summary.py        # Injects/updates SUMMARY section
│   ├── run_simulation.py       # Wraps docker run … /usr/bin/flow
│   └── extract_results.py      # Reads *.UNSMRY with resdata
├── requirements.txt            # Python dependencies
├── .gitignore                 
└── README.md                  
```

## Variable Glossary

### Grid State Variables
- **BPR**: Block pressure [barsa]
- **BWSAT**: Block water saturation [fraction]
- **BGSAT**: Block gas saturation [fraction]

### Field Rates & Totals
- **FOPR/FOPT**: Field oil production rate/total [SM³/day, SM³]
- **FGPR/FGPT**: Field gas production rate/total [SM³/day, SM³]
- **FWPR/FWPT**: Field water production rate/total [SM³/day, SM³]
- **FGOR**: Field gas-oil ratio [SM³/SM³]
- **FWCT**: Field water cut [fraction]

### Well Variables
- **WBHP/WTHP**: Well bottom/tubing head pressure [barsa]
- **WOPR/WOPT**: Well oil production rate/total [SM³/day, SM³]
- **WGPR/WGPT**: Well gas production rate/total [SM³/day, SM³]
- **WWPR/WWPT**: Well water production rate/total [SM³/day, SM³]
- **WGIR/WGIT**: Well gas injection rate/total [SM³/day, SM³]
- **WWIR/WWIT**: Well water injection rate/total [SM³/day, SM³]

### Numerical Performance
- **PERFORMA**: Solver performance statistics (iterations, timesteps, etc.)

## Troubleshooting

### Docker Issues
- **Permission denied**: Run `docker` commands with `sudo` or add your user to the docker group
- **Platform warning on Mac**: The `--platform linux/amd64` flag ensures compatibility on Apple Silicon

### Common Errors
- **FileNotFoundError**: Ensure SPE1CASE1.DATA exists in `data/` directory
- **resdata import error**: Install with `pip install resdata pandas pyarrow`
- **Docker not found**: Install Docker Desktop from https://www.docker.com/

### Output Files
After successful run, `patched/` will contain:
- `*.UNSMRY` - Binary summary data
- `*.SMSPEC` - Summary specification
- `*.RSM` - Column-format summary (human-readable)
- `*.INIT` - Initial grid state
- `*.EGRID` - Grid geometry
- `*.parquet` - Extracted time-series data

## Notes

- The `patched/` directory is auto-generated and ignored by git
- Summary data is configured to output only at report steps (`RPTONLY`)
- Results are saved in Parquet format for efficient storage and analysis
- The Docker image is ~2GB on first download

## Understanding the SPE1 Dataset

### What is SPE1 Case 1?

SPE1 Case 1 is a standard benchmark problem defined by the Society of Petroleum Engineers for comparing reservoir simulators. It represents a simple oil reservoir with:

- **Grid**: 10×10×3 cells (300 total cells)
- **Physics**: Three-phase flow (oil, water, gas) with dissolved gas
- **Wells**: One producer (PROD) and one gas injector (INJ)
- **Duration**: 10-year production period

### Dataset Overview

![Key Statistics](figures/key_statistics.png)

The simulation tracks the evolution of pressure and fluid saturations in every grid cell over time, creating a rich 4D dataset (3D space + time).

### Initial Reservoir Conditions

![Reservoir Overview](figures/reservoir_overview.png)

The reservoir starts with:
- **High oil saturation** (~88%) throughout most of the reservoir
- **Pressure gradient** increasing with depth (typical hydrostatic conditions)
- **Water saturation** only at the bottom (water-oil contact)

![Cross Section](figures/reservoir_cross_section.png)

The cross-section view shows the three-layer structure with pressure increasing with depth and high initial oil saturation.

### Production Evolution

![Time Evolution](figures/time_evolution.png)

Over the 10-year production period:
- **Pressure declines** as fluids are produced
- **Water saturation increases** as water moves in to replace produced oil
- **Gas saturation increases** as pressure drops below bubble point
- **Oil saturation decreases** as oil is produced

![Oil Depletion](figures/oil_depletion_snapshots.png)

These snapshots show how oil (red) is gradually displaced by water and gas over the production period. The depletion pattern is influenced by well locations and reservoir properties.

### Production Performance

![Production Analysis](figures/production_analysis.png)

Key production metrics:
- **Oil production rate** maintained at target until reservoir pressure can no longer sustain it
- **Cumulative production** reaches over 3 million SM³
- **Recovery factor** approaches 30% of original oil in place
- **Average pressure** declines from ~380 to ~340 bar

## Accessing the Full Dataset

### HDF5 Format

The complete grid timeseries data is stored in `patched/SPE1CASE1_PATCHED.h5`:

```python
import h5py
import numpy as np

# Open the dataset
with h5py.File('patched/SPE1CASE1_PATCHED.h5', 'r') as f:
    # Get dimensions
    nx, ny, nz = f.attrs['nx'], f.attrs['ny'], f.attrs['nz']
    n_timesteps = f.attrs['n_timesteps']
    
    # Access pressure data (4D array: time × x × y × z)
    pressure = f['grid_data/PRESSURE'][:]
    
    # Get pressure evolution at specific cell
    cell_pressure = pressure[:, 5, 5, 1]  # Cell (5,5,1) over time
    
    # Get pressure distribution at specific time
    pressure_t50 = pressure[50, :, :, :]  # 3D grid at timestep 50
```

### Available Properties

1. **PRESSURE** - Reservoir pressure in bars
2. **SWAT** - Water saturation (fraction, 0-1)
3. **SGAS** - Gas saturation (fraction, 0-1)
4. **RS** - Dissolved gas-oil ratio

Note: Oil saturation can be calculated as: `SOIL = 1.0 - SWAT - SGAS`

### Data Structure

- **Shape**: (123 timesteps, 10 x-cells, 10 y-cells, 3 layers)
- **Time span**: Monthly data from 2015-01-01 to 2024-12-31
- **File size**: ~6 MB (compressed HDF5)

## Visualization Scripts

Generate these visualizations yourself:

```bash
# Create all figures
python viz_scripts/01_reservoir_overview.py
python viz_scripts/02_time_evolution.py
python viz_scripts/03_production_analysis.py
```

## Applications

This dataset is useful for:
- Testing reservoir simulation post-processing tools
- Machine learning on reservoir data (production forecasting, history matching)
- Visualization technique development
- Educational purposes in petroleum engineering
- Benchmarking data compression and storage methods