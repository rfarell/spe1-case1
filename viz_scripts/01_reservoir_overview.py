#!/usr/bin/env python3
"""Create overview visualizations of the SPE1 reservoir."""
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Load data
with h5py.File('patched/SPE1CASE1_PATCHED.h5', 'r') as f:
    nx, ny, nz = f.attrs['nx'], f.attrs['ny'], f.attrs['nz']
    pressure_init = f['grid_data/PRESSURE'][0, :, :, :]
    swat_init = f['grid_data/SWAT'][0, :, :, :]
    sgas_init = f['grid_data/SGAS'][0, :, :, :]
    soil_init = 1.0 - swat_init - sgas_init

# Create figure with 4 rows instead of 3
fig = plt.figure(figsize=(12, 13))
gs = gridspec.GridSpec(4, 3, figure=fig, hspace=0.3, wspace=0.3)

# Plot initial pressure for each layer
for k in range(nz):
    ax = fig.add_subplot(gs[0, k])
    im = ax.imshow(pressure_init[:, :, k].T, origin='lower', cmap='RdBu_r')
    ax.set_title(f'Layer {k+1} Pressure (bar)')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.colorbar(im, ax=ax, fraction=0.046)
    # Mark the monitored cell (1,1,1) 
    if k == 1:
        ax.plot(0, 0, 'k*', markersize=10)

# Plot initial oil saturation for each layer
for k in range(nz):
    ax = fig.add_subplot(gs[1, k])
    im = ax.imshow(soil_init[:, :, k].T, origin='lower', cmap='Reds', vmin=0, vmax=1)
    ax.set_title(f'Layer {k+1} Oil Saturation')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.colorbar(im, ax=ax, fraction=0.046)

# Plot water saturation for each layer
for k in range(nz):
    ax = fig.add_subplot(gs[2, k])
    im = ax.imshow(swat_init[:, :, k].T, origin='lower', cmap='Blues', vmin=0, vmax=1)
    ax.set_title(f'Layer {k+1} Water Saturation')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.colorbar(im, ax=ax, fraction=0.046)

# Plot gas saturation for each layer
for k in range(nz):
    ax = fig.add_subplot(gs[3, k])
    im = ax.imshow(sgas_init[:, :, k].T, origin='lower', cmap='Greens', vmin=0, vmax=1)
    ax.set_title(f'Layer {k+1} Gas Saturation')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.colorbar(im, ax=ax, fraction=0.046)

fig.suptitle('SPE1 Reservoir Initial Conditions\n10×10×3 Grid (300 cells)', fontsize=14)
plt.tight_layout()
plt.savefig('figures/reservoir_overview.png', dpi=150, bbox_inches='tight')
plt.close()

# Create cross-section view
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Pressure cross-section at Y=5
pressure_xz = pressure_init[:, 5, :]
im1 = ax1.imshow(pressure_xz.T, origin='lower', aspect='auto', cmap='RdBu_r', extent=[0, 10, 0, 3])
ax1.set_xlabel('X')
ax1.set_ylabel('Layer')
ax1.set_title('Pressure Cross-Section (Y=5)')
ax1.set_yticks([0.5, 1.5, 2.5])
ax1.set_yticklabels(['1', '2', '3'])
plt.colorbar(im1, ax=ax1, label='Pressure (bar)')

# Saturation cross-section
soil_xz = soil_init[:, 5, :]
im2 = ax2.imshow(soil_xz.T, origin='lower', aspect='auto', cmap='Reds', vmin=0, vmax=1, extent=[0, 10, 0, 3])
ax2.set_xlabel('X')
ax2.set_ylabel('Layer')
ax2.set_title('Oil Saturation Cross-Section (Y=5)')
ax2.set_yticks([0.5, 1.5, 2.5])
ax2.set_yticklabels(['1', '2', '3'])
plt.colorbar(im2, ax=ax2, label='Oil Saturation')

plt.tight_layout()
plt.savefig('figures/reservoir_cross_section.png', dpi=150, bbox_inches='tight')
plt.close()

print("Created: reservoir_overview.png, reservoir_cross_section.png")