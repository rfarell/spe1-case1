#!/usr/bin/env python3
"""Analyze production data and fluid movement."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import h5py

# Load summary data
df = pd.read_parquet('patched/SPE1CASE1_PATCHED.parquet')

# Load grid data for advanced analysis
with h5py.File('patched/SPE1CASE1_PATCHED.h5', 'r') as f:
    swat_all = f['grid_data/SWAT'][:]
    sgas_all = f['grid_data/SGAS'][:]
    pressure_all = f['grid_data/PRESSURE'][:]
    
    # Calculate field-wide averages
    avg_pressure = np.mean(pressure_all, axis=(1, 2, 3))
    avg_swat = np.mean(swat_all, axis=(1, 2, 3))
    avg_sgas = np.mean(sgas_all, axis=(1, 2, 3))
    avg_soil = 1.0 - avg_swat - avg_sgas

# Create production analysis figure
fig = plt.figure(figsize=(14, 10))

# 1. Oil production rate
ax1 = plt.subplot(3, 2, 1)
ax1.plot(df.index, df['FOPR'], 'g-', linewidth=2)
ax1.set_ylabel('Oil Rate (SM³/day)')
ax1.set_title('Field Oil Production Rate')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, df['FOPR'].max() * 1.1)

# 2. Cumulative oil production
ax2 = plt.subplot(3, 2, 2)
ax2.plot(df.index, df['FOPT'] / 1e6, 'g-', linewidth=2)
ax2.set_ylabel('Cumulative Oil (Million SM³)')
ax2.set_title('Cumulative Oil Production')
ax2.grid(True, alpha=0.3)

# 3. Field average pressure
ax3 = plt.subplot(3, 2, 3)
ax3.plot(df.index, avg_pressure, 'b-', linewidth=2)
ax3.set_ylabel('Pressure (bar)')
ax3.set_title('Field Average Pressure')
ax3.grid(True, alpha=0.3)

# 4. Field average saturations
ax4 = plt.subplot(3, 2, 4)
ax4.plot(df.index, avg_soil, 'r-', label='Oil', linewidth=2)
ax4.plot(df.index, avg_swat, 'b-', label='Water', linewidth=2)
ax4.plot(df.index, avg_sgas, 'g-', label='Gas', linewidth=2)
ax4.set_ylabel('Saturation')
ax4.set_title('Field Average Saturations')
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.set_ylim(0, 1)

# 5. Recovery factor
initial_oil = avg_soil[0] * 300  # Initial oil in place (normalized)
current_oil = avg_soil * 300
recovery_factor = (initial_oil - current_oil) / initial_oil * 100

ax5 = plt.subplot(3, 2, 5)
ax5.plot(df.index, recovery_factor, 'k-', linewidth=2)
ax5.set_ylabel('Recovery Factor (%)')
ax5.set_xlabel('Time')
ax5.set_title('Oil Recovery Factor')
ax5.grid(True, alpha=0.3)

# 6. Pressure at monitoring well (1,1,1)
ax6 = plt.subplot(3, 2, 6)
ax6.plot(df.index, df['BPR:1,1,1'], 'purple', linewidth=2)
ax6.set_ylabel('Pressure (bar)')
ax6.set_xlabel('Time')
ax6.set_title('Pressure at Block (1,1,1)')
ax6.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('figures/production_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

# Create a simple infographic
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')

# Title
ax.text(0.5, 0.95, 'SPE1 Case 1 - Key Statistics', 
        fontsize=20, weight='bold', ha='center', transform=ax.transAxes)

# Key numbers
stats_text = f"""
Simulation Period: 10 years (2015-2025)
Grid Size: 10 × 10 × 3 = 300 cells
Active Cells: 300 (100%)

Initial Conditions:
• Average Pressure: {avg_pressure[0]:.1f} bar
• Average Oil Saturation: {avg_soil[0]:.1%}
• Average Water Saturation: {avg_swat[0]:.1%}

Final Results:
• Average Pressure: {avg_pressure[-1]:.1f} bar
• Average Oil Saturation: {avg_soil[-1]:.1%}
• Oil Recovery Factor: {recovery_factor[-1]:.1f}%
• Total Oil Produced: {df['FOPT'].iloc[-1]/1e6:.2f} Million SM³
"""

ax.text(0.1, 0.5, stats_text, fontsize=14, 
        transform=ax.transAxes, verticalalignment='center',
        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.5))

plt.savefig('figures/key_statistics.png', dpi=150, bbox_inches='tight')
plt.close()

print("Created: production_analysis.png, key_statistics.png")