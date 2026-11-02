#!/usr/bin/env python3
"""Bucket xctrace self samples under factor5_ucode by the RSP op template that inlined them (s6775).
Input: --dump-addrs file from tools/xctrace_tp.py ("<n> <addr> self|callsite") and the runtime load slide
(--slide hex: runtime addr - slide = file addr, e.g. 0x2AE0000). Runs one batched lldb `image lookup -a` over every self
address, parses the inline chain, and prints samples by (outermost RSP:: op), by (op, leaf source line) and by leaf line."""
import argparse, collections, re, subprocess, tempfile, os
ap = argparse.ArgumentParser(); ap.add_argument('addrs'); ap.add_argument('--slide', required=True)
ap.add_argument('--bin', default='build/RogueSquadron64Recomp'); ap.add_argument('--top', type=int, default=30)
a = ap.parse_args(); slide = int(a.slide, 16)
rows = []
for ln in open(a.addrs):
    n, ad, kind = ln.split()
    if kind == 'self': rows.append((int(n), int(ad, 16) - slide))
with tempfile.NamedTemporaryFile('w', suffix='.cmds', delete=False) as f:
    for _, ad in rows: f.write(f'image lookup -a {ad:#x}\n')
out = subprocess.run(['lldb', '-b', '-o', f'target create {a.bin}', '-o', f'command source -s 0 {f.name}'],
                     capture_output=True, text=True).stdout
os.unlink(f.name)
chains = {}; cur = None
for ln in out.splitlines():
    m = re.search(r'Address: \S+\[(0x[0-9a-f]+)\]', ln)
    if m: cur = int(m.group(1), 16); chains[cur] = []; continue
    if cur is not None and '`' in ln: chains[cur].append(ln.split('`', 1)[1].strip())
op_re = re.compile(r'\[inlined\] (?:void |\S+ )?RSP::(\w+)(<[^>]*>)?\(')
line_re = re.compile(r' at ([\w.]+:\d+)')
byop = collections.Counter(); byopline = collections.Counter(); byline = collections.Counter(); tot = 0; miss = 0
for n, ad in rows:
    ch = chains.get(ad)
    if not ch: miss += n; continue
    tot += n
    leaf = line_re.search(ch[0]); leaf = leaf.group(1) if leaf else '?'
    ops = [op_re.search(c) for c in ch]; ops = [m.group(1) + (m.group(2) or '') for m in ops if m]
    op = ops[-1] if ops else '(ucode .c / other)'
    byop[op] += n; byopline[(op, leaf)] += n; byline[leaf] += n
print(f'self samples {tot} (unresolved {miss})')
fam = collections.Counter()
for k, n in byop.items(): fam[k.split('<')[0]] += n
print('-- by op family'); [print(f'{n:6d} {100*n/tot:5.1f}% {k}') for k, n in fam.most_common(a.top)]
print('-- by op<e>'); [print(f'{n:6d} {100*n/tot:5.1f}% {k}') for k, n in byop.most_common(a.top)]
print('-- by leaf line'); [print(f'{n:6d} {100*n/tot:5.1f}% {k}') for k, n in byline.most_common(a.top)]
print('-- by (op, leaf line)'); [print(f'{n:6d} {100*n/tot:5.1f}% {k[0]} @ {k[1]}') for k, n in byopline.most_common(a.top)]
print('-- rsp_vu.hpp leaf lines by op')
acc = collections.Counter({k: n for k, n in byopline.items() if k[1].startswith('rsp_vu.hpp')})
[print(f'{n:6d} {k[0]} @ {k[1]}') for k, n in acc.most_common(a.top)]
