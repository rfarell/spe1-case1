#!/usr/bin/env python3
"""Visualize time evolution using summary data."""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load summary data
df = pd.read_parquet('patched/SPE1CASE1_PATCHED.parquet')

# Create figure
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 9))

# Plot 1: Pressure evolution at monitored cell (1,1,1)
ax1.plot(df.index, df['BPR:1,1,1'], 'b-', linewidth=2)
ax1.set_xlabel('Time')
ax1.set_ylabel('Pressure (bar)')
ax1.set_title('Pressure Evolution at Cell (1,1,1)')
ax1.grid(True, alpha=0.3)

# Plot 2: Saturation evolution at monitored cell
# Calculate oil saturation from water and gas
soil = 1.0 - df['BWSAT:1,1,1'] - df['BGSAT:1,1,1']
ax2.plot(df.index, soil, 'r-', label='Oil', linewidth=2)
ax2.plot(df.index, df['BWSAT:1,1,1'], 'b-', label='Water', linewidth=2)
ax2.plot(df.index, df['BGSAT:1,1,1'], 'g-', label='Gas', linewidth=2)
ax2.set_xlabel('Time')
ax2.set_ylabel('Saturation')
ax2.set_title('Saturation Evolution at Cell (1,1,1)')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 1)

# Plot 3: Field oil production rate
ax3.plot(df.index, df['FOPR'], 'g-', linewidth=2)
ax3.set_xlabel('Time')
ax3.set_ylabel('Oil Rate (SM³/day)')
ax3.set_title('Field Oil Production Rate')
ax3.grid(True, alpha=0.3)
ax3.set_ylim(0, df['FOPR'].max() * 1.1)

# Plot 4: Recovery factor
initial_oil_rate = df['FOPR'].iloc[0]
recovery_factor = (df['FOPT'] / df['FOPT'].iloc[-1]) * 100
ax4.plot(df.index, recovery_factor, 'k-', linewidth=2)
ax4.set_xlabel('Time')
ax4.set_ylabel('Recovery Progress (%)')
ax4.set_title('Cumulative Oil Recovery')
ax4.grid(True, alpha=0.3)
ax4.set_ylim(0, 105)

plt.tight_layout()
plt.savefig('figures/time_evolution.png', dpi=150, bbox_inches='tight')
plt.close()

# Create detailed saturation plot for monitored cell
fig, ax = plt.subplots(figsize=(10, 6))

# Stack plot
ax.fill_between(df.index, 0, df['BWSAT:1,1,1'], color='blue', alpha=0.7, label='Water')
ax.fill_between(df.index, df['BWSAT:1,1,1'], df['BWSAT:1,1,1'] + soil, color='red', alpha=0.7, label='Oil')
ax.fill_between(df.index, df['BWSAT:1,1,1'] + soil, 1, color='green', alpha=0.7, label='Gas')

ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Saturation', fontsize=12)
ax.set_title('Fluid Saturation Evolution at Cell (1,1,1)', fontsize=14)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 1)

plt.tight_layout()
plt.savefig('figures/saturation_stack.png', dpi=150, bbox_inches='tight')
plt.close()

# Print summary statistics
print("Cell (1,1,1) Evolution Summary:")
print(f"  Pressure: {df['BPR:1,1,1'].iloc[0]:.0f} -> {df['BPR:1,1,1'].iloc[-1]:.0f} bar")
print(f"  Oil saturation: {soil.iloc[0]:.3f} -> {soil.iloc[-1]:.3f}")
print(f"  Water saturation: {df['BWSAT:1,1,1'].iloc[0]:.3f} -> {df['BWSAT:1,1,1'].iloc[-1]:.3f}")
print(f"  Gas saturation: {df['BGSAT:1,1,1'].iloc[0]:.3f} -> {df['BGSAT:1,1,1'].iloc[-1]:.3f}")
print(f"  Max gas saturation: {df['BGSAT:1,1,1'].max():.3f}")

print("\nCreated: time_evolution.png, saturation_stack.png")