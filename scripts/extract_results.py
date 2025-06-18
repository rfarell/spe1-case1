#!/usr/bin/env python3
"""
Quick demo of loading the UNSMRY file with resdata.

    python extract_results.py outputs/SPE1CASE1_patched.UNSMRY
"""
import pathlib, pandas as pd
from resdata.summary import Summary

def load(path: pathlib.Path):
    r = Summary(str(path.with_suffix('')))  # Remove .UNSMRY extension
    wanted = [
        'FOPR', 'FGPR', 'FWPR',          # rates
        'FOPT', 'FGPT', 'FWPT',          # cum
        'WBHP:INJ', 'WBHP:PROD',         # BHP per well
        'BPR:1,1,1', 'BWSAT:1,1,1', 'BGSAT:1,1,1'
    ]
    # Get all available keys and filter for wanted ones that exist
    available_keys = [k for k in r.keys() if any(w in k for w in wanted)]
    
    # Build dataframe
    data = {}
    for key in available_keys:
        data[key] = r.numpy_vector(key)
    
    # Get time steps
    time_points = r.numpy_dates
    df = pd.DataFrame(data, index=pd.to_datetime(time_points))
    out = path.with_suffix('.parquet')
    df.to_parquet(out)
    print(f'→ saved to {out}')
    print(df.head())

if __name__ == "__main__":
    import sys
    load(pathlib.Path(sys.argv[1]))