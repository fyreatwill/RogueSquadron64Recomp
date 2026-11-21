#!/usr/bin/env python3
"""s7744: count stand-in items that were really drawn before the game spawned them.
The s7691 recipe counted `grep -o 'early_s=[0-9.]*'`, which also matches early_s=-1.00 (never added early), so its
early_items always equalled spawn_lines. This reads [standins-spawn] lines and counts early_s > 0 only, plus the first
time any stand-in was added (so a dump window placed before it reads as an artefact, not a null).
Usage: s7744_early_count.py <log[.zst]> [--self-test]"""
import re, subprocess, sys
PAT = re.compile(r'\[standins-spawn\].*?added_first=(-?[0-9.]+).*?early_s=(-?[0-9.]+)')
def read(p):
    if p.endswith('.zst'):
        return subprocess.run(['zstd', '-dc', p], capture_output=True, text=True, errors='replace').stdout
    return open(p, errors='replace').read()
def count(text):
    rows = [(float(a), float(e)) for a, e in PAT.findall(text)]
    early = [e for _, e in rows if e > 0]
    firsts = [a for a, _ in rows if a >= 0]
    return dict(spawn=len(rows), early=len(early), early_max=max(early) if early else -1,
                first_add=min(firsts) if firsts else -1)
def self_test():
    t = ("[standins-spawn] item 1 t=0.00 added_first=-1.00 added_last=-1.00 early_s=-1.00 par=0\n"
         "[standins-spawn] item 2 t=58.61 added_first=21.36 added_last=58.59 early_s=37.25 par=1\n")
    r = count(t); old = len(re.findall(r'early_s=[0-9.]*', t))
    ok = r['spawn'] == 2 and r['early'] == 1 and r['first_add'] == 21.36 and old == 2
    print(f"self-test new early={r['early']} old_grep={old} -> {'PASS' if ok else 'FAIL'}"); return 0 if ok else 1
if __name__ == '__main__':
    if '--self-test' in sys.argv: sys.exit(self_test())
    for p in sys.argv[1:]:
        r = count(read(p)); print(f"{p}: spawn={r['spawn']} early={r['early']} early_max={r['early_max']:.2f} first_add={r['first_add']:.2f}")
