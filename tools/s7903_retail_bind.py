#!/usr/bin/env python3
"""s7903 G3 island B: which (instance matrix, flame vertex block) does RETAIL draw on the crawl-tail odd frames?
For each port task snapshot: overlay every retail oracle task n in a VI window onto it (tools/s7903_retail_overlay.py), replay
through cxd4 with the SP DMA log (tools/s7900_dma_trace/replay_dma), and pick the n whose replay reproduces a retail RDP frame
EXACTLY (positive control: an overlay missing retail state cannot reproduce retail's frame; reported per snapshot).
Then, per flame instance (SP DMA to 0x05D0 = instance matrix in MTXS, 0x0280 = vertex block), compare port vs retail:
  same matrix address, same vertex-block bytes?  If not, where do the port's block bytes sit in retail (which n / address / which
  retail instance draws them):
  H-bind : retail draws the port's bytes under ANOTHER instance matrix in the same task -> instance->mesh binding differs.
  H-alloc: retail's task holds the port's bytes at another address but no instance draws them on this frame.
  H-time : the port's bytes appear in retail only at a LATER n (retail writes them after this task loaded) / earlier n.
usage: s7903_retail_bind.py ORACLE.log RETAIL.bin PORT.bin OFF VI0:VI1 SNAP.bin[:S] ... [--flame 700100,700140] [--keep DIR]
  SNAP name must carry _s<serial> (k900_s5681.bin.zst); port frame P = serial - 42 (s7902 pairing), retail frame = P + OFF.
"""
import sys, os, re, struct, subprocess, tempfile, collections, importlib.util, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from rs64_zopen import zbytes, zopen
import s7903_retail_overlay as ov
a = sys.argv[1:]
if len(a) < 6: print(__doc__); sys.exit(2)
LOG, RB, PB, OFF = a[0], a[1], a[2], int(a[3]); VI0, VI1 = map(int, a[4].split(':'))
opt = lambda k, d: a[a.index(k) + 1] if k in a else d
FLAME = {int(x, 16) for x in opt('--flame', '700100,700140').split(',')}
KEEP = opt('--keep', None)
snaps = [x for i, x in enumerate(a[5:], 5) if not x.startswith('--') and a[i - 1] not in ('--flame', '--keep')]
REPLAY = os.path.join(HERE, 's7900_dma_trace', 'replay_dma')
sys.argv = [sys.argv[0], '--tri-geom']
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
def s11_2(v): v &= 0xFFFF; return (v - 0x10000 if v & 0x8000 else v) / 4.0
def tris_pos(b):   # same parser as tools/s7900_tri_source.py
    out = []; i = 0; prim = None
    while i + 8 <= len(b):
        w0, w1 = struct.unpack_from('>II', b, i); op = (w0 >> 24) & 0x3F; n = 8
        if 0x08 <= op <= 0x0F:
            if i + 32 > len(b): break
            n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
            w = struct.unpack_from('>8I', b, i); out.append((i, ('tri', prim) + w + (w0 & 0x3FFF,)))
        elif op in (0x24, 0x25): n = 16
        elif op == 0x3A: prim = '%08X' % w1
        i += n
    return out

R = ov.load(LOG)
cands = [(n, vi) for n, vi in ov.task_vis(R) if VI0 <= vi <= VI1]
print(f'retail tasks in vi {VI0}:{VI1}: {len(cands)}; ranges {len(R)}: ' + ' '.join(f'{k:06X}' for k in sorted(R)))
RF = m.frames(RB, True); PF = m.frames(PB, False)
# key without PRIM: a replayed task starts with no SETPRIMCOLOR while the captured frame inherits the previous task's (FFFFFFFF),
# which made 100 tris per task differ in s7903's first pass (port replay vs its own frame too).
np_ = lambda k: k[:1] + k[2:]
tri = lambda c: collections.Counter({np_(k): v for k, v in c.items() if k[0] == 'tri'})
tmp = KEEP or tempfile.mkdtemp(prefix='s7903_'); os.makedirs(tmp, exist_ok=True)

def replay(snapbytes, tag):
    sb = os.path.join(tmp, tag + '.bin'); rd = os.path.join(tmp, tag + '.rdp'); dm = os.path.join(tmp, tag + '.dma')
    open(sb, 'wb').write(snapbytes)
    subprocess.run([REPLAY, sb, rd], env=dict(os.environ, S7900_DMA_LOG=dm), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not KEEP: os.remove(sb)
    T = tris_pos(open(rd, 'rb').read()) if os.path.exists(rd) else []
    D = [l.split() for l in open(dm)] if os.path.exists(dm) else []
    D = [(int(x[1]), int(x[2], 16), int(x[3], 16), int(x[4], 16) & 0xFFF) for x in D if x and x[0] == 'dma']
    return T, D

def instances(T, D, mem):
    """[(first tri off, mtxA addr, vtx addr, vtx bytes hash, ntris)] grouped by consecutive (mtxA, vtx) source"""
    out = []; last = {}; di = 0
    for off, k in T:
        while di < len(D) and D[di][0] <= off: last[D[di][2]] = (D[di][1], D[di][3] + 1); di += 1
        mt = last.get(0x05D0); vx = last.get(0x0280)
        key = (mt[0] if mt else None, vx[0] if vx else None)
        if out and out[-1][1:3] == key: out[-1][4] += 1; continue
        h = hashlib.md5(mem(vx[0], vx[1])).hexdigest()[:8] if vx else '-'
        out.append([off, key[0], key[1], h, 1])
    return out

def snapmem(b):
    H = 20 + 4096
    return lambda ad, n: b''.join(struct.pack('>I', struct.unpack_from('<I', b, H + ad + 4 * i)[0]) for i in range(n // 4))
def retmem(st, fallback):
    def g(ad, n):
        for a0, w in st.items():
            if a0 <= ad and ad + n <= a0 + len(w): return w[ad - a0:ad - a0 + n]
        return fallback(ad, n)
    return g

ctl_ok = 0
for sn in snaps:
    S = int(re.search(r'_s(\d+)', sn).group(1)); P = S - 42; F0 = P + OFF
    pb = bytes(zbytes(sn)); pmem = snapmem(pb)
    Tp, Dp = replay(pb, f'port_s{S}')
    pc = collections.Counter(np_(k) for _, k in Tp); pp = tri(PF[P][0]) if P < len(PF) else collections.Counter()
    print(f'\n== s{S} port P={P} replay tris {len(Tp)} == port frame: {pc == pp}')
    best = None; exacts = []
    for n, vi in cands:
        st = ov.state(R, n); T, D = replay(ov.overlay(pb, st), f'ret_s{S}_n{n}')
        c = collections.Counter(np_(k) for _, k in T)
        for F in (F0,):
            if F < 0 or F >= len(RF): continue
            rf = tri(RF[F][0]); inter = sum((c & rf).values()); tot = max(sum(c.values()), sum(rf.values()))
            sc = (c == rf, inter / tot if tot else 0)
            if c == rf: exacts.append(n)
            if best is None or sc > best[0]: best = (sc, n, vi, F, T, D, st)
    (exact, frac), n, vi, F, Tr, Dr, st = best
    ctl_ok += exact
    print(f'  retail tasks reproducing frame {F0}: {[x for x in exacts]}')
    print(f'  best retail n={n} vi={vi} reproduces retail frame {F} (F0{F - F0:+d}): exact={exact} match={frac:.3f}')
    rmem = retmem(st, pmem)
    Ip = instances(Tp, Dp, pmem); Ir = instances(Tr, Dr, rmem)
    # every 64-byte block hash in retail's task state (any address) -> addresses, and retail instances by hash
    rh = collections.defaultdict(list)
    for a0, w in st.items():
        for i in range(0, len(w) - 63, 8): rh[hashlib.md5(w[i:i + 64]).hexdigest()[:8]].append(a0 + i)
    rinst = collections.defaultdict(list)
    for off, mt, vx, h, nt in Ir: rinst[h].append((mt, vx))
    # the same hash in other retail tasks (time)
    def when(h, ad_hint):
        hits = []
        for n2, vi2 in ov.task_vis(R):
            if abs(vi2 - vi) > 12: continue
            for a0, w in ov.state(R, n2).items():
                for i in range(0, len(w) - 63, 8):
                    if hashlib.md5(w[i:i + 64]).hexdigest()[:8] == h: hits.append((vi2 - vi, a0 + i)); break
        return hits
    pf = [x for x in Ip if x[1] in FLAME]; rfl = [x for x in Ir if x[1] in FLAME]
    print(f'  flame instances: port {len(pf)} retail {len(rfl)}')
    for k in range(max(len(pf), len(rfl))):
        p = pf[k] if k < len(pf) else None; r = rfl[k] if k < len(rfl) else None
        ps = f'port mtx {p[1]:06X} vtx {p[2]:06X} h{p[3]} t{p[4]}' if p else 'port -'
        rs = f'retail mtx {r[1]:06X} vtx {r[2]:06X} h{r[3]} t{r[4]}' if r else 'retail -'
        tag = ''
        if p and r and p[3] != r[3]:
            bind = [x for x in rinst.get(p[3], [])]
            tag = (f' | port bytes: retail instance(s) {[(f"{x[0]:06X}" if x[0] else "-", f"{x[1]:06X}") for x in bind]}' if bind else
                   f' | port bytes in retail task at {[f"{x:06X}" for x in rh.get(p[3], [])][:4]}' if p[3] in rh else
                   f' | port bytes not in retail task; other retail tasks (dvi, addr) {when(p[3], p[2])[:6]}')
        print(f'  [{k:2d}] {ps:44s} {rs:44s} {"SAME" if p and r and p[3] == r[3] else "DIFF"}{tag}')
print(f'\ncontrol: {ctl_ok}/{len(snaps)} snapshots have a retail task whose overlaid replay reproduces a retail frame exactly')
