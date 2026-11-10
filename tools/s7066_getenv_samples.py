#!/usr/bin/env python3
"""s7066: count inclusive host samples of libSystem getenv vs the image's cached getenv, per thread, over a
directory of tools/s7065_sample_loop.zsh files. usage: s7066_getenv_samples.py <dir> [<dir>...]"""
import re, glob, sys, collections
for d in sys.argv[1:]:
    lib = collections.Counter(); img = collections.Counter(); tot = collections.Counter(); files = 0
    for fn in glob.glob(d + '/smp_*.txt'):
        files += 1; th = '?'
        for l in open(fn, errors='replace'):
            m = re.match(r'^\s+(\d+) Thread_\d+\s*(.*)', l)
            if m: th = ('MAIN' if '[Game] MAIN' in m.group(2) else re.sub(r'\s+\(serial\)|DispatchQueue_\d+: ', '', m.group(2))[:40] or 'unnamed'); tot[th] += int(m.group(1)); continue
            m = re.match(r'^[\s+!:|]*(\d+)\s+getenv\s+\(in (\S+)\)', l)
            if m: (lib if 'libsystem' in m.group(2) else img)[th] += int(m.group(1))
    print(f'{d}: files={files} libsystem_getenv={sum(lib.values())} image_getenv={sum(img.values())} all_samples={sum(tot.values())}')
    for th in sorted(set(lib) | set(img), key=lambda t: -(lib[t] + img[t]))[:8]:
        print(f'   {th:42s} lib={lib[th]:5d} img={img[th]:5d} of {tot[th]}')
