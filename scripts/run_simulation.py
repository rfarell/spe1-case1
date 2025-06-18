#!/usr/bin/env python3
"""
Run OPM Flow inside Docker and stream logs.

Example:
    python run_simulation.py patched/SPE1CASE1_patched.DATA outputs/
"""
import subprocess, argparse, pathlib, shutil, os

def run(deck_path: pathlib.Path, output_dir: pathlib.Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    # mount containing folder read‑only, outputs writable
    mount_in  = deck_path.resolve().parent
    mount_out = output_dir.resolve()
    cmd = [
        'docker', 'run',
        '--platform', 'linux/amd64',
        '--rm',
        '-v', f'{mount_in}:/deck:ro',
        '-v', f'{mount_out}:/run',
        'openporousmedia/opmreleases:latest',
        '/usr/bin/flow', '/deck/' + deck_path.name,
        '--output-dir=/run'
    ]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('deck', type=pathlib.Path)
    p.add_argument('out',  type=pathlib.Path)
    args = p.parse_args()
    run(args.deck, args.out)