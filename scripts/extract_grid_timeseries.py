#!/usr/bin/env python3
"""
Extract full grid timeseries data from OPM Flow output and save to HDF5.

Usage:
    python extract_grid_timeseries.py patched/SPE1CASE1_PATCHED
"""
import pathlib
import numpy as np
import pandas as pd
import h5py
from resdata.summary import Summary
from resdata.grid import Grid
from resdata.resfile import ResdataFile
from resdata import FileType
import sys

def extract_grid_timeseries(base_path: pathlib.Path):
    """Extract full grid timeseries data and save to HDF5."""
    
    # Remove any extension from base path
    base_str = str(base_path).split('.')[0]
    
    print("Loading grid geometry...")
    grid = Grid(f"{base_str}.EGRID")
    nx, ny, nz = grid.nx, grid.ny, grid.nz
    n_active = grid.get_num_active()
    
    print(f"Grid dimensions: {nx} x {ny} x {nz} = {nx*ny*nz} cells")
    print(f"Active cells: {n_active}")
    
    # Load summary data to get time information
    print("\nLoading summary data...")
    summary = Summary(base_str)
    time_points = summary.numpy_dates
    n_steps = len(time_points)
    print(f"Number of timesteps: {n_steps}")
    print(f"Time range: {time_points[0]} to {time_points[-1]}")
    
    # Define parameters to extract from restart files
    grid_params = {
        'PRESSURE': 'Pressure (bar)',
        'SWAT': 'Water saturation',
        'SGAS': 'Gas saturation',
        'SOIL': 'Oil saturation',
        'RS': 'Dissolved gas-oil ratio',
        'PBUB': 'Bubble point pressure (bar)'
    }
    
    # Initialize data storage
    data = {param: np.zeros((n_steps, nx, ny, nz)) for param in grid_params}
    
    # Check which restart files exist
    print("\nScanning for restart files...")
    restart_files = []
    unrst_path = pathlib.Path(f"{base_str}.UNRST")
    
    if unrst_path.exists():
        # Unified restart file
        print(f"Found unified restart file: {unrst_path}")
        rst_file = ResdataFile(str(unrst_path), FileType.UNIFIED_RESTART)
        n_reports = rst_file.num_report_steps()
        print(f"Contains {n_reports} report steps")
        
        for report_step in range(n_reports):
            restart_files.append((report_step, rst_file))
    else:
        # Look for individual restart files
        for i in range(n_steps):
            rst_path = pathlib.Path(f"{base_str}.X{i:04d}")
            if rst_path.exists():
                restart_files.append((i, str(rst_path)))
    
    print(f"Found {len(restart_files)} restart files")
    
    # Extract data from restart files
    print("\nExtracting grid data...")
    available_params = set()
    
    for idx, (report_step, rst_source) in enumerate(restart_files):
        if isinstance(rst_source, ResdataFile):
            # Unified restart file
            rst = rst_source
            report_idx = report_step
        else:
            # Individual restart file
            rst = ResdataFile(rst_source, FileType.RESTART)
            report_idx = report_step
        
        # Check which parameters are available
        for param in grid_params:
            if rst.has_kw(param):
                available_params.add(param)
                kw = rst.iget_named_kw(param, 0)
                values = np.array(kw)
                
                # Reshape to grid dimensions
                if len(values) == nx * ny * nz:
                    data[param][report_idx] = values.reshape(nx, ny, nz, order='F')
                else:
                    print(f"Warning: {param} has unexpected size {len(values)}")
        
        if idx % 10 == 0:
            print(f"  Processed {idx+1}/{len(restart_files)} restart files...")
    
    print(f"\nAvailable parameters: {sorted(available_params)}")
    
    # Save to HDF5
    output_path = base_path.with_suffix('.h5')
    print(f"\nSaving to {output_path}...")
    
    with h5py.File(output_path, 'w') as f:
        # Store metadata
        f.attrs['nx'] = nx
        f.attrs['ny'] = ny
        f.attrs['nz'] = nz
        f.attrs['n_active'] = n_active
        f.attrs['n_timesteps'] = n_steps
        
        # Store time information
        time_group = f.create_group('time')
        # Convert datetime to strings for HDF5 compatibility
        time_strings = [pd.Timestamp(t).strftime('%Y-%m-%d %H:%M:%S') for t in time_points]
        time_group.create_dataset('dates', data=np.array(time_strings, dtype='S19'))
        # Also store as timestamps
        time_group.create_dataset('timestamps', data=pd.to_datetime(time_points).astype(np.int64))
        
        # Store grid data
        grid_group = f.create_group('grid_data')
        for param in available_params:
            dset = grid_group.create_dataset(
                param, 
                data=data[param],
                compression='gzip',
                compression_opts=4
            )
            dset.attrs['description'] = grid_params.get(param, param)
            dset.attrs['shape_info'] = 'Shape is (timesteps, nx, ny, nz)'
        
        # Note: Grid coordinates could be added here if needed
        # For now, focusing on the grid property data
    
    # Print summary
    print("\n" + "="*60)
    print("HDF5 FILE SUMMARY")
    print("="*60)
    print(f"Output file: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024**2:.2f} MB")
    print(f"\nReservoir dimensions:")
    print(f"  Grid: {nx} x {ny} x {nz} = {nx*ny*nz} total cells")
    print(f"  Active cells: {n_active}")
    print(f"\nTime information:")
    print(f"  Number of timesteps: {n_steps}")
    print(f"  Time range: {pd.Timestamp(time_points[0])} to {pd.Timestamp(time_points[-1])}")
    duration_days = (pd.Timestamp(time_points[-1]) - pd.Timestamp(time_points[0])).days
    print(f"  Duration: {duration_days} days")
    print(f"\nStored parameters:")
    for param in sorted(available_params):
        print(f"  - {param}: {grid_params.get(param, 'Unknown')}")
    print(f"\nData structure:")
    print(f"  /time/dates: Time stamps for each step")
    print(f"  /grid_data/{param}: 4D array (timesteps, nx, ny, nz)")
    print(f"\nTo access data:")
    print(f"  import h5py")
    print(f"  f = h5py.File('{output_path.name}', 'r')")
    print(f"  pressure = f['grid_data/PRESSURE'][:]  # All timesteps")
    print(f"  pressure_t0 = f['grid_data/PRESSURE'][0, :, :, :]  # First timestep")
    print(f"  pressure_cell = f['grid_data/PRESSURE'][:, 5, 5, 1]  # Time series at cell (5,5,1)")
    print("="*60)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_grid_timeseries.py patched/SPE1CASE1_PATCHED")
        sys.exit(1)
    
    base_path = pathlib.Path(sys.argv[1])
    extract_grid_timeseries(base_path)