#!/usr/bin/env python3
"""Find the most interesting grid cell with maximum variation."""
import h5py
import numpy as np

with h5py.File('patched/SPE1CASE1_PATCHED.h5', 'r') as f:
    swat = f['grid_data/SWAT'][:]
    sgas = f['grid_data/SGAS'][:]
    pressure = f['grid_data/PRESSURE'][:]
    
    # Calculate oil saturation
    soil = 1.0 - swat - sgas
    
    # Calculate variation for each cell
    swat_var = np.var(swat, axis=0)
    sgas_var = np.var(sgas, axis=0)
    soil_var = np.var(soil, axis=0)
    pressure_var = np.var(pressure, axis=0)
    
    # Combined variation score
    total_var = swat_var + sgas_var + soil_var + pressure_var/1000
    
    # Find cell with maximum variation
    max_idx = np.unravel_index(np.argmax(total_var), total_var.shape)
    cx, cy, cz = max_idx
    
    print(f"Most interesting cell: ({cx}, {cy}, {cz})")
    print(f"\nVariations at this cell:")
    print(f"  Water sat: {swat_var[cx,cy,cz]:.4f}")
    print(f"  Gas sat: {sgas_var[cx,cy,cz]:.4f}")
    print(f"  Oil sat: {soil_var[cx,cy,cz]:.4f}")
    print(f"  Pressure: {pressure_var[cx,cy,cz]:.1f}")
    
    print(f"\nSaturation ranges at cell ({cx}, {cy}, {cz}):")
    print(f"  Water: {swat[:,cx,cy,cz].min():.3f} to {swat[:,cx,cy,cz].max():.3f}")
    print(f"  Gas: {sgas[:,cx,cy,cz].min():.3f} to {sgas[:,cx,cy,cz].max():.3f}")
    print(f"  Oil: {soil[:,cx,cy,cz].min():.3f} to {soil[:,cx,cy,cz].max():.3f}")
    
    # Also check cells near wells
    print("\n\nCells near wells (corners and center):")
    interesting_cells = [(0,0,0), (9,9,2), (0,9,0), (9,0,2), (5,5,1)]
    
    for x, y, z in interesting_cells:
        oil_change = soil[0,x,y,z] - soil[-1,x,y,z]
        gas_max = sgas[:,x,y,z].max()
        print(f"  Cell ({x},{y},{z}): Oil change={oil_change:.3f}, Max gas={gas_max:.3f}")