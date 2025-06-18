#!/usr/bin/env python3
"""Visualize time evolution of reservoir properties."""
import h5py
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Load data
with h5py.File('patched/SPE1CASE1_PATCHED.h5', 'r') as f:
    time_strings = f['time/dates'][:]
    dates = pd.to_datetime([t.decode() for t in time_strings])
    
    # Get interesting cell evolution (0,0,0) - near producer well
    cx, cy, cz = 0, 0, 0
    pressure_center = f['grid_data/PRESSURE'][:, cx, cy, cz]
    swat_center = f['grid_data/SWAT'][:, cx, cy, cz]
    sgas_center = f['grid_data/SGAS'][:, cx, cy, cz]
    soil_center = 1.0 - swat_center - sgas_center
    
    # Get layer averages over time
    pressure_all = f['grid_data/PRESSURE'][:]
    swat_all = f['grid_data/SWAT'][:]
    sgas_all = f['grid_data/SGAS'][:]

# Calculate layer averages
pressure_avg = np.mean(pressure_all, axis=(1, 2))  # Average over X,Y for each layer
swat_avg = np.mean(swat_all, axis=(1, 2))
sgas_avg = np.mean(sgas_all, axis=(1, 2))
soil_avg = 1.0 - swat_avg - sgas_avg

# Create figure
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 9))

# Plot 1: Pressure evolution at producer cell
ax1.plot(dates, pressure_center, 'b-', linewidth=2)
ax1.set_xlabel('Time')
ax1.set_ylabel('Pressure (bar)')
ax1.set_title(f'Pressure Evolution at Cell ({cx},{cy},{cz}) - Near Producer')
ax1.grid(True, alpha=0.3)

# Plot 2: Saturation evolution at producer cell
ax2.plot(dates, soil_center, 'r-', label='Oil', linewidth=2)
ax2.plot(dates, swat_center, 'b-', label='Water', linewidth=2)
ax2.plot(dates, sgas_center, 'g-', label='Gas', linewidth=2)
ax2.set_xlabel('Time')
ax2.set_ylabel('Saturation')
ax2.set_title(f'Saturation Evolution at Cell ({cx},{cy},{cz}) - Near Producer')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 1)

# Plot 3: Average pressure by layer
for k in range(3):
    ax3.plot(dates, pressure_avg[:, k], label=f'Layer {k+1}', linewidth=2)
ax3.set_xlabel('Time')
ax3.set_ylabel('Average Pressure (bar)')
ax3.set_title('Layer-Average Pressure Evolution')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: Average oil saturation by layer
for k in range(3):
    ax4.plot(dates, soil_avg[:, k], label=f'Layer {k+1}', linewidth=2)
ax4.set_xlabel('Time')
ax4.set_ylabel('Average Oil Saturation')
ax4.set_title('Layer-Average Oil Saturation Evolution')
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.set_ylim(0, 1)

plt.tight_layout()
plt.savefig('figures/time_evolution.png', dpi=150, bbox_inches='tight')
plt.close()

# Create snapshots at different times
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
time_indices = [0, 24, 48, 72, 96, 120]  # Every 2 years
layer = 1  # Middle layer

for i, (ax, t_idx) in enumerate(zip(axes.flat, time_indices)):
    soil = 1.0 - swat_all[t_idx, :, :, layer] - sgas_all[t_idx, :, :, layer]
    im = ax.imshow(soil.T, origin='lower', cmap='Reds', vmin=0, vmax=1)
    ax.set_title(f'{dates[t_idx].strftime("%Y-%m")}')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    if i == len(time_indices)-1:
        plt.colorbar(im, ax=ax, fraction=0.046, label='Oil Saturation')

fig.suptitle('Oil Saturation Evolution - Layer 2', fontsize=14)
plt.tight_layout()
plt.savefig('figures/oil_depletion_snapshots.png', dpi=150, bbox_inches='tight')
plt.close()

# Create gas saturation snapshots
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
layer = 0  # Top layer where gas appears most

for i, (ax, t_idx) in enumerate(zip(axes.flat, time_indices)):
    gas = sgas_all[t_idx, :, :, layer]
    im = ax.imshow(gas.T, origin='lower', cmap='Greens', vmin=0, vmax=0.3)
    ax.set_title(f'{dates[t_idx].strftime("%Y-%m")}')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    # Mark producer location
    ax.plot(0, 0, 'k*', markersize=8)
    if i == len(time_indices)-1:
        plt.colorbar(im, ax=ax, fraction=0.046, label='Gas Saturation')

fig.suptitle('Gas Saturation Evolution - Layer 1 (Top)', fontsize=14)
plt.tight_layout()
plt.savefig('figures/gas_evolution_snapshots.png', dpi=150, bbox_inches='tight')
plt.close()

print("Created: time_evolution.png, oil_depletion_snapshots.png, gas_evolution_snapshots.png")