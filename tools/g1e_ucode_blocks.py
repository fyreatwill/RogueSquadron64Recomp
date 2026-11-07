# s6939: split factor5_ucode host CPU by RSP label block and source line, from an xctrace Time Profiler capture.
# recipe: xctrace record --template "Time Profiler" --attach PID --time-limit 30s --output T.trace
#         vmmap PID | grep -m1 "__TEXT.*RogueSquadron64Recomp" > base.txt   (while the game is alive)
#         xctrace export --input T.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="time-profile"]' > T.xml
#         python3 tools/g1e_xt_leaves.py T.xml > leaves.txt
#         dsymutil build/RogueSquadron64Recomp -o X.dSYM     (atos gives no lines without it)
#         python3 tools/g1e_ucode_blocks.py leaves.txt base.txt X.dSYM/Contents/Resources/DWARF/RogueSquadron64Recomp build/factor5_ucode/factor5_ucode_recompiled.c
# /usr/bin/sample is NOT usable for this: it merges leaf PCs into "+ a,b,..." nodes and drops most of them.
# Once a dSYM sits on disk, xctrace names inlined RS64_RSP_GFX:: vector ops as leaves: they are counted as ucode too.
# usage: python3 xblk.py leaves.txt base.txt binary ucode.c  -> ucode leaf split by RSP label block and line
import re, sys, subprocess, collections
lv, basef, binp, src = sys.argv[1:5]
base = int(re.search(r'([0-9a-f]{9,})-', open(basef).read()).group(1), 16)
rows = []
for ln in open(lv):
    p = ln.split(None, 2)
    if len(p) == 3: rows.append((int(p[0]), int(p[1], 16), p[2].strip()))
tot = sum(r[0] for r in rows)
fn = collections.Counter()
for c, a, n in rows: fn[n.split('(')[0]] += c
print('all leaf samples', tot)
for n, c in fn.most_common(20): print(f'{c:7d} {100*c/tot:5.1f}% {n[:80]}')
uc = [(c, a) for c, a, n in rows if n.startswith('factor5_ucode(') or 'RS64_RSP_GFX::' in n or n.startswith('_mm_')]
ut = sum(c for c, a in uc)
print(f'\nfactor5_ucode leaf {ut} ({100*ut/tot:.1f}%), {len(uc)} distinct PCs')
addrs = [hex(a - base + 0x100000000) for c, a in uc]
out = []
for i in range(0, len(addrs), 400):
    r = subprocess.run(['atos', '-o', binp, '-arch', 'arm64', '-i'] + addrs[i:i+400], capture_output=True, text=True).stdout
    out += r.strip('\n').split('\n\n')
labels = [(i, m.group(1)) for i, t in enumerate(open(src, errors='replace'), 1) for m in [re.match(r'^(L_[0-9A-F]+|RS64_UCODE_ENTRY):', t)] if m]
srcl = open(src, errors='replace').read().split('\n')
def lab(l):
    r = '(pre)'
    for i, n in labels:
        if i <= l: r = n
        else: break
    return r
blk = collections.Counter(); byl = collections.Counter(); inner = collections.Counter(); bad = 0
for (c, a), ch in zip(uc, out):
    ls = [x for x in ch.split('\n') if x.strip()]
    m = None
    for x in ls:
        mm = re.search(r'factor5_ucode_recompiled\.c:(\d+)', x)
        if mm: m = mm
    if not m: bad += c; continue
    l = int(m.group(1)); blk[lab(l)] += c; byl[l] += c
    inner[re.sub(r'\(.*', '', ls[0])[:60] if 'factor5_ucode_recompiled.c' not in ls[0] else '(ucode body)'] += c
print('unmapped', bad)
print('innermost inline frame:'); [print(f'  {c:6d} {100*c/ut:5.1f}% {n}') for n, c in inner.most_common(12)]
print('blocks:'); [print(f'  {c:6d} {100*c/ut:5.1f}% {n}') for n, c in blk.most_common(30)]
print('lines:'); [print(f'  {c:6d} {100*c/ut:5.1f}% {l}: {srcl[l-1].strip()[:110]}') for l, c in byl.most_common(25)]
