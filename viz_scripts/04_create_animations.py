#!/usr/bin/env python3
"""Create animated visualizations of reservoir evolution."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
import imageio.v2 as imageio
import os

# Load summary data
df = pd.read_parquet('patched/SPE1CASE1_PATCHED.parquet')

# Calculate oil saturation
soil = 1.0 - df['BWSAT:1,1,1'] - df['BGSAT:1,1,1']

# Create a temporary directory for frames
os.makedirs('temp_frames', exist_ok=True)

print("Creating saturation animation frames...")

# Animation 1: Saturation evolution at cell (1,1,1)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Sample every 5th timestep for reasonable GIF size
time_indices = range(0, len(df), 5)

for i, idx in enumerate(time_indices):
    ax1.clear()
    ax2.clear()
    
    # Pie chart of saturations
    sizes = [df['BWSAT:1,1,1'].iloc[idx], 
             soil.iloc[idx], 
             df['BGSAT:1,1,1'].iloc[idx]]
    colors = ['blue', 'red', 'green']
    labels = ['Water', 'Oil', 'Gas']
    
    wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, 
                                        autopct='%1.1f%%', startangle=90)
    ax1.set_title(f'Saturations at Cell (1,1,1)\n{df.index[idx].strftime("%Y-%m")}')
    
    # Time series up to current point
    ax2.plot(df.index[:idx+1], soil[:idx+1], 'r-', label='Oil', linewidth=2)
    ax2.plot(df.index[:idx+1], df['BWSAT:1,1,1'][:idx+1], 'b-', label='Water', linewidth=2)
    ax2.plot(df.index[:idx+1], df['BGSAT:1,1,1'][:idx+1], 'g-', label='Gas', linewidth=2)
    ax2.set_xlim(df.index[0], df.index[-1])
    ax2.set_ylim(0, 1)
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Saturation')
    ax2.set_title('Saturation Evolution')
    ax2.legend(loc='right')
    ax2.grid(True, alpha=0.3)
    
    # Add vertical line for current time
    ax2.axvline(df.index[idx], color='k', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(f'temp_frames/sat_frame_{i:04d}.png', dpi=100)
    
    if i % 10 == 0:
        print(f"  Created frame {i+1}/{len(time_indices)}")

plt.close()

# Create GIF from frames
print("\nCreating saturation GIF...")
images = []
for i in range(len(time_indices)):
    images.append(imageio.imread(f'temp_frames/sat_frame_{i:04d}.png'))

imageio.mimsave('figures/saturation_evolution.gif', images, fps=5, loop=0)

# Animation 2: Combined view with pressure
print("\nCreating combined animation frames...")

fig = plt.figure(figsize=(14, 8))
gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

for i, idx in enumerate(time_indices):
    # Clear all
    fig.clear()
    
    # Recreate subplots
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])
    
    # Pressure evolution
    ax1.plot(df.index[:idx+1], df['BPR:1,1,1'][:idx+1], 'purple', linewidth=2)
    ax1.set_xlim(df.index[0], df.index[-1])
    ax1.set_ylim(df['BPR:1,1,1'].min() * 0.95, df['BPR:1,1,1'].max() * 1.05)
    ax1.set_ylabel('Pressure (bar)')
    ax1.set_title(f'Pressure at Cell (1,1,1)')
    ax1.grid(True, alpha=0.3)
    ax1.axvline(df.index[idx], color='k', linestyle='--', alpha=0.5)
    
    # Current saturations bar chart
    ax2.bar(['Water', 'Oil', 'Gas'], 
            [df['BWSAT:1,1,1'].iloc[idx], soil.iloc[idx], df['BGSAT:1,1,1'].iloc[idx]],
            color=['blue', 'red', 'green'])
    ax2.set_ylim(0, 1)
    ax2.set_ylabel('Saturation')
    ax2.set_title(f'Current Saturations\n{df.index[idx].strftime("%Y-%m")}')
    
    # Production rate
    ax3.plot(df.index[:idx+1], df['FOPR'][:idx+1], 'green', linewidth=2)
    ax3.set_xlim(df.index[0], df.index[-1])
    ax3.set_ylim(0, df['FOPR'].max() * 1.1)
    ax3.set_xlabel('Time')
    ax3.set_ylabel('Oil Production Rate (SM³/day)')
    ax3.set_title('Field Oil Production Rate')
    ax3.grid(True, alpha=0.3)
    ax3.axvline(df.index[idx], color='k', linestyle='--', alpha=0.5)
    
    fig.suptitle(f'SPE1 Reservoir Evolution - {df.index[idx].strftime("%B %Y")}', fontsize=16)
    plt.tight_layout()
    plt.savefig(f'temp_frames/combined_frame_{i:04d}.png', dpi=100)
    
    if i % 10 == 0:
        print(f"  Created frame {i+1}/{len(time_indices)}")

plt.close()

# Create combined GIF
print("\nCreating combined GIF...")
images = []
for i in range(len(time_indices)):
    images.append(imageio.imread(f'temp_frames/combined_frame_{i:04d}.png'))

imageio.mimsave('figures/reservoir_evolution.gif', images, fps=5, loop=0)

# Clean up temporary frames
print("\nCleaning up temporary files...")
import shutil
shutil.rmtree('temp_frames')

print("\nCreated animations:")
print("  - figures/saturation_evolution.gif")
print("  - figures/reservoir_evolution.gif")