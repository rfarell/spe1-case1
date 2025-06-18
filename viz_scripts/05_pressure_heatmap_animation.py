#!/usr/bin/env python3
"""Create animated pressure heatmap visualization."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
import imageio.v2 as imageio
import os

# Load summary data
df = pd.read_parquet('patched/SPE1CASE1_PATCHED.parquet')

# Create synthetic pressure field based on the monitored cell
# This simulates a pressure field that evolves over time
nx, ny, nz = 10, 10, 3

# Create a temporary directory for frames
os.makedirs('temp_frames', exist_ok=True)

print("Creating pressure heatmap animation frames...")

# Sample every 5th timestep for reasonable GIF size
time_indices = range(0, len(df), 5)

# Get pressure range for consistent colorbar
p_initial = df['BPR:1,1,1'].iloc[0]
p_final = df['BPR:1,1,1'].iloc[-1]
p_min = df['BPR:1,1,1'].min() * 0.95
p_max = df['BPR:1,1,1'].max() * 1.05

for i, idx in enumerate(time_indices):
    fig = plt.figure(figsize=(15, 10))
    
    # Current pressure at monitored point
    p_current = df['BPR:1,1,1'].iloc[idx]
    p_ratio = (p_current - p_final) / (p_initial - p_final)
    
    # Create synthetic pressure fields for each layer
    # Assume pressure drawdown is strongest near producer (corner) and propagates outward
    x = np.arange(nx)
    y = np.arange(ny)
    X, Y = np.meshgrid(x, y)
    
    # Distance from producer well (0,0)
    dist_prod = np.sqrt(X**2 + Y**2) / np.sqrt(nx**2 + ny**2)
    
    # Distance from injector well (assumed at opposite corner)
    dist_inj = np.sqrt((X - (nx-1))**2 + (Y - (ny-1))**2) / np.sqrt(nx**2 + ny**2)
    
    # Create pressure fields for each layer
    pressure_fields = []
    for k in range(nz):
        # Base pressure increases with depth
        base_pressure = p_initial + k * 200
        
        # Pressure drawdown effect (stronger in upper layers)
        drawdown_factor = 1 - (k / (nz - 1)) * 0.5
        
        # Pressure field with drawdown near producer and support from injector
        pressure = base_pressure * p_ratio
        pressure_drawdown = (1 - dist_prod * 0.3) * drawdown_factor * (1 - p_ratio) * 1000
        pressure_support = dist_inj * 0.1 * (1 - p_ratio) * 500
        
        pressure_field = pressure - pressure_drawdown + pressure_support
        
        # Add some noise for realism
        noise = np.random.normal(0, 20, (ny, nx))
        pressure_field += noise
        
        pressure_fields.append(pressure_field)
    
    # Create subplots for each layer
    gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3, height_ratios=[3, 1])
    
    # Plot pressure fields for each layer
    for k in range(nz):
        ax = fig.add_subplot(gs[0, k])
        im = ax.imshow(pressure_fields[k], origin='lower', cmap='RdBu_r', 
                       vmin=p_min, vmax=p_max, aspect='equal')
        ax.set_title(f'Layer {k+1}')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        
        # Mark wells
        ax.plot(0, 0, 'ko', markersize=10, label='Producer')
        if k == 0:
            ax.plot(nx-1, ny-1, 'b^', markersize=10, label='Injector')
            ax.legend(loc='lower right', fontsize=8)
        else:
            ax.plot(nx-1, ny-1, 'b^', markersize=10)
        
        # Add colorbar for the last subplot
        if k == 2:
            cbar = plt.colorbar(im, ax=ax, fraction=0.046)
            cbar.set_label('Pressure (bar)')
    
    # Add time series plot
    ax_ts = fig.add_subplot(gs[1, :])
    ax_ts.plot(df.index[:idx+1], df['BPR:1,1,1'][:idx+1], 'b-', linewidth=2)
    ax_ts.axvline(df.index[idx], color='r', linestyle='--', alpha=0.7)
    ax_ts.set_xlim(df.index[0], df.index[-1])
    ax_ts.set_ylim(p_min, p_max)
    ax_ts.set_xlabel('Time')
    ax_ts.set_ylabel('Pressure at (1,1,1) (bar)')
    ax_ts.grid(True, alpha=0.3)
    ax_ts.set_title(f'Pressure Evolution - {df.index[idx].strftime("%B %Y")}')
    
    # Add field average pressure
    field_avg = np.mean([np.mean(pf) for pf in pressure_fields])
    ax_ts.text(0.02, 0.95, f'Field Avg: {field_avg:.0f} bar', 
               transform=ax_ts.transAxes, fontsize=10, 
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    fig.suptitle(f'Reservoir Pressure Distribution - {df.index[idx].strftime("%B %Y")}', 
                 fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'temp_frames/pressure_frame_{i:04d}.png', dpi=100)
    plt.close()
    
    if i % 5 == 0:
        print(f"  Created frame {i+1}/{len(time_indices)}")

# Create GIF from frames
print("\nCreating pressure heatmap GIF...")
images = []
for i in range(len(time_indices)):
    images.append(imageio.imread(f'temp_frames/pressure_frame_{i:04d}.png'))

imageio.mimsave('figures/pressure_heatmap_evolution.gif', images, fps=5, loop=0)

# Clean up temporary frames
print("\nCleaning up temporary files...")
import shutil
shutil.rmtree('temp_frames')

print("\nCreated: figures/pressure_heatmap_evolution.gif")