#!/usr/bin/env python3
"""Quick check that everything is set up correctly."""
import os
import sys

print("SPE1 Case 1 - Setup Check")
print("=" * 40)

# Check directories
dirs = ['data', 'patched', 'scripts', 'viz_scripts', 'figures']
for d in dirs:
    exists = os.path.exists(d)
    print(f"Directory {d:12} {'✓' if exists else '✗'}")

# Check figures
print("\nGenerated figures:")
if os.path.exists('figures'):
    figures = [f for f in os.listdir('figures') if f.endswith('.png')]
    for fig in sorted(figures):
        size = os.path.getsize(f'figures/{fig}') / 1024
        print(f"  {fig:30} {size:6.1f} KB")
else:
    print("  No figures found")

# Check for data file
print("\nData file:")
data_file = 'data/SPE1CASE1.DATA'
if os.path.exists(data_file):
    print(f"  {data_file} ✓")
else:
    print(f"  {data_file} ✗ (You need to provide this)")

# Check Python packages
print("\nPython packages:")
packages = ['resdata', 'pandas', 'h5py', 'matplotlib']
for pkg in packages:
    try:
        __import__(pkg)
        print(f"  {pkg:12} ✓")
    except ImportError:
        print(f"  {pkg:12} ✗")

print("\nTo run the full pipeline:")
print("  1. Place SPE1CASE1.DATA in data/")
print("  2. Run: python scripts/patch_summary.py ...")
print("  3. Run: python scripts/run_simulation.py ...")
print("  4. Run: python scripts/extract_results.py ...")