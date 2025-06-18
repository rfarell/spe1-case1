#!/usr/bin/env python3
"""
Inject a canonical SUMMARY section into an Eclipse/Flow deck.

Usage:
    python patch_summary.py data/SPE1CASE1.DATA patched/SPE1CASE1_patched.DATA
"""
import sys, pathlib, textwrap, re

BLOCK = textwrap.dedent("""\
    SUMMARY
    -- === automatically inserted by patch_summary.py ===
    -- grid‑state core
    BPR
    1 1 1 /
    10 10 3 /
    /
    BWSAT
    1 1 1 /
    10 10 3 /
    /
    BGSAT
    1 1 1 /
    10 10 3 /
    /
    -- field vectors
    FOPR FGPR FWPR
    FOPT FGPT FWPT
    FGOR FWCT
    -- well vectors
    WBHP WTHP
    WOPR WGPR WWPR
    WOPT WGPT WWPT
    WGIR WWIR WGIT WWIT
    -- solver diagnostics
    PERFORMA
    -- file layout
    RUNSUM
    SEPARATE
    RPTONLY
    /
""")

def main(src, dst):
    deck = pathlib.Path(src).read_text().splitlines(keepends=False)
    # remove existing SUMMARY section if present
    cleaned = []
    skipping = False
    for line in deck:
        if line.strip().upper().startswith('SUMMARY'):
            skipping = True
            continue
        if skipping and line.strip().upper().startswith('SCHEDULE'):
            skipping = False
            cleaned.append(line)               # keep SCHEDULE
            continue
        if not skipping:
            cleaned.append(line)
    # inject block *before* SCHEDULE
    txt = '\n'.join(cleaned)
    txt = re.sub(r'\nSCHEDULE', f'\n{BLOCK}\nSCHEDULE', txt, flags=re.I)
    pathlib.Path(dst).write_text(txt)
    print(f'Patched deck written → {dst}')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("patch_summary.py <input.DATA> <output.DATA>")
    main(sys.argv[1], sys.argv[2])