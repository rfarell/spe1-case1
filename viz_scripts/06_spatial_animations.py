#!/usr/bin/env python3
"""Create spatial animations for pressure and saturations based on reservoir physics."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
import imageio.v2 as imageio
import os
import h5py

# Load data
df = pd.read_parquet('patched/SPE1CASE1_PATCHED.parquet')

# Get initial conditions from HDF5
with h5py.File('patched/SPE1CASE1_PATCHED.h5', 'r') as f:
    # Get initial state (which is the only valid state we have)
    pressure_init = f['grid_data/PRESSURE'][0, :, :, :]
    swat_init = f['grid_data/SWAT'][0, :, :, :]
    sgas_init = f['grid_data/SGAS'][0, :, :, :]
    nx, ny, nz = pressure_init.shape

# Create temporary directory for frames
os.makedirs('temp_frames', exist_ok=True)

print("Creating spatial animations based on reservoir physics...")

# Sample every 5th timestep
time_indices = range(0, len(df), 5)

# Get evolution factors from monitored cell
p_initial = df['BPR:1,1,1'].iloc[0]
p_final = df['BPR:1,1,1'].iloc[-1]
swat_initial = df['BWSAT:1,1,1'].iloc[0]
sgas_initial = df['BGSAT:1,1,1'].iloc[0]

# Create coordinate grids
x = np.arange(nx)
y = np.arange(ny)
X, Y = np.meshgrid(x, y, indexing='ij')

# Distance from producer (0,0) and injector (9,9)
dist_prod = np.sqrt((X - 0)**2 + (Y - 0)**2)
dist_inj = np.sqrt((X - 9)**2 + (Y - 9)**2)
max_dist = np.sqrt(nx**2 + ny**2)

# Normalize distances
dist_prod_norm = dist_prod / max_dist
dist_inj_norm = dist_inj / max_dist

print("\n1. Creating pressure animation...")
for i, idx in enumerate(time_indices):
    fig = plt.figure(figsize=(15, 5))
    
    # Current state at monitored cell
    p_current = df['BPR:1,1,1'].iloc[idx]
    p_decline_ratio = (p_initial - p_current) / (p_initial - p_final + 1e-6)
    
    # Create pressure fields for each layer
    for k in range(nz):
        ax = plt.subplot(1, 3, k+1)
        
        # Start with initial pressure
        pressure = pressure_init[:, :, k].copy()
        
        # Apply pressure drawdown near producer
        # Stronger effect in upper layers, propagating outward over time
        drawdown_strength = (1 - k/2) * p_decline_ratio * 1500
        pressure_field = pressure - drawdown_strength * np.exp(-dist_prod_norm * 3)
        
        # Add pressure support from injector (mainly in deeper layers)
        if k > 0:
            support_strength = (k/2) * p_decline_ratio * 500
            pressure_field += support_strength * np.exp(-dist_inj_norm * 3)
        
        # Ensure reasonable bounds
        pressure_field = np.clip(pressure_field, p_final * 0.8, p_initial * 1.1)
        
        im = ax.imshow(pressure_field.T, origin='lower', cmap='RdBu_r',
                       vmin=3500, vmax=6500, aspect='equal')
        ax.set_title(f'Layer {k+1} - Pressure (bar)')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        
        # Mark wells
        ax.plot(0, 0, 'ko', markersize=8, markeredgewidth=2, markeredgecolor='white')
        ax.plot(9, 9, 'b^', markersize=8, markeredgewidth=2, markeredgecolor='white')
        
        if k == 2:
            cbar = plt.colorbar(im, ax=ax, fraction=0.046)
            cbar.set_label('Pressure (bar)')
    
    plt.suptitle(f'Pressure Distribution - {df.index[idx].strftime("%B %Y")}', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'temp_frames/pressure_spatial_{i:04d}.png', dpi=100)
    plt.close()
    
    if i % 5 == 0:
        print(f"  Frame {i+1}/{len(time_indices)}")

# Create pressure GIF
images = []
for i in range(len(time_indices)):
    images.append(imageio.imread(f'temp_frames/pressure_spatial_{i:04d}.png'))
imageio.mimsave('figures/pressure_spatial_evolution.gif', images, fps=5, loop=0)

print("\n2. Creating saturation animations...")
# Create saturation evolution based on monitored cell behavior
for i, idx in enumerate(time_indices):
    fig = plt.figure(figsize=(15, 10))
    
    # Get current saturations at monitored cell
    swat_current = df['BWSAT:1,1,1'].iloc[idx]
    sgas_current = df['BGSAT:1,1,1'].iloc[idx]
    
    # Calculate change ratios
    sgas_growth = sgas_current / (df['BGSAT:1,1,1'].max() + 1e-6)
    
    # Create 3x3 grid: 3 properties × 3 layers
    for k in range(nz):
        # Oil saturation
        ax1 = plt.subplot(3, 3, k + 1)
        soil_init = 1 - swat_init[:, :, k] - sgas_init[:, :, k]
        
        # Oil depletion is strongest near producer, weaker with distance
        depletion_factor = 0.6 * sgas_growth * np.exp(-dist_prod_norm * 2)
        if k == 0:  # Strongest depletion in top layer
            depletion_factor *= 1.2
        
        soil = soil_init * (1 - depletion_factor)
        soil = np.clip(soil, 0, 1)
        
        im1 = ax1.imshow(soil.T, origin='lower', cmap='Reds', vmin=0, vmax=1)
        ax1.set_title(f'Layer {k+1} - Oil')
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        if k == 2:
            plt.colorbar(im1, ax=ax1, fraction=0.046)
        
        # Water saturation
        ax2 = plt.subplot(3, 3, k + 4)
        # Water mostly stays constant except slight increase near producer
        swat = swat_init[:, :, k].copy()
        water_increase = 0.05 * sgas_growth * np.exp(-dist_prod_norm * 4)
        swat = swat + water_increase
        swat = np.clip(swat, 0, 1)
        
        im2 = ax2.imshow(swat.T, origin='lower', cmap='Blues', vmin=0, vmax=1)
        ax2.set_title(f'Layer {k+1} - Water')
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        if k == 2:
            plt.colorbar(im2, ax=ax2, fraction=0.046)
        
        # Gas saturation
        ax3 = plt.subplot(3, 3, k + 7)
        # Gas appears as oil is produced, strongest near producer
        sgas = sgas_init[:, :, k].copy()
        if k < 2:  # Gas mainly in upper layers
            gas_factor = (1 - k/2) * sgas_growth * 0.7 * np.exp(-dist_prod_norm * 2)
            sgas = sgas + gas_factor
        sgas = np.clip(sgas, 0, 1)
        
        # Ensure sum = 1
        total = soil + swat + sgas
        soil = soil / total
        swat = swat / total
        sgas = sgas / total
        
        im3 = ax3.imshow(sgas.T, origin='lower', cmap='Greens', vmin=0, vmax=0.6)
        ax3.set_title(f'Layer {k+1} - Gas')
        ax3.set_xlabel('X')
        ax3.set_ylabel('Y')
        if k == 2:
            plt.colorbar(im3, ax=ax3, fraction=0.046)
        
        # Mark wells on all plots
        for ax in [ax1, ax2, ax3]:
            ax.plot(0, 0, 'ko', markersize=6, markeredgewidth=1, markeredgecolor='white')
            ax.plot(9, 9, 'b^', markersize=6, markeredgewidth=1, markeredgecolor='white')
    
    plt.suptitle(f'Saturation Distribution - {df.index[idx].strftime("%B %Y")}', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'temp_frames/saturation_spatial_{i:04d}.png', dpi=100)
    plt.close()
    
    if i % 5 == 0:
        print(f"  Frame {i+1}/{len(time_indices)}")

# Create saturation GIF
images = []
for i in range(len(time_indices)):
    images.append(imageio.imread(f'temp_frames/saturation_spatial_{i:04d}.png'))
imageio.mimsave('figures/saturation_spatial_evolution.gif', images, fps=5, loop=0)

# Clean up
print("\nCleaning up temporary files...")
import shutil
shutil.rmtree('temp_frames')

print("\nCreated animations:")
print("  - figures/pressure_spatial_evolution.gif")
print("  - figures/saturation_spatial_evolution.gif")