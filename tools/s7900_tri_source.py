#!/usr/bin/env python3
"""s7900 G3 island B: name the guest RDRAM that feeds the drifting (port-only vs retail) triangles of one gfx task.
Inputs: the task snapshot's cxd4 replay stream with its DMA log (tools/s7900_dma_trace/replay_dma, S7900_DMA_LOG), the
retail RDP bin + port RDP bin + port frame P (task's port frame) + OFF (retail = P + OFF), as in tools/s7899_snap_cmp.py.
For each tri in the replay stream: byte offset, PRIM, screen bbox, and the SP DMA reads before it, grouped by SP destination
(0x0590/0x05D0 = 64-byte matrices, 0x0280/0x0B70 = vertex blocks, 0x0170 = DL chunks). Port-only tris (in the task AND in
port frame P but not in retail frame P+OFF) are summarised by the source RDRAM ranges they were drawn after.
Control (same run): --poke-check OUT.rdp: a second replay with one poked word; prints which tris moved (feed it back to show
that the named buffer moves exactly the drifting tris).
usage: s7900_tri_source.py TASK.rdp TASK.dma RETAIL.bin PORT.bin P OFF [--moved OTHER.rdp]
"""
import sys, os, struct, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
a = sys.argv[1:]
if len(a) < 6: print(__doc__); sys.exit(2)
RDP, DMA, RB, PB, P, OFF = a[0], a[1], a[2], a[3], int(a[4]), int(a[5])
MOVED = a[a.index('--moved') + 1] if '--moved' in a else None
from rs64_zopen import zbytes, zopen
sys.argv = [sys.argv[0], '--tri-geom']
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)

def s11_2(v): v &= 0xFFFF; return (v - 0x10000 if v & 0x8000 else v) / 4.0
def tris_pos(b):
    out = []; i = 0; prim = None
    while i + 8 <= len(b):
        w0, w1 = struct.unpack_from('>II', b, i); op = (w0 >> 24) & 0x3F; n = 8
        if 0x08 <= op <= 0x0F:
            if i + 32 > len(b): break
            n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
            w = struct.unpack_from('>8I', b, i)
            key = ('tri', prim) + w + (w0 & 0x3FFF,)
            yl, ym, yh = s11_2(w0 >> 0) if False else s11_2(w0 & 0x3FFF), s11_2(w1 >> 16), s11_2(w1)
            xs = [struct.unpack('>i', struct.pack('>I', w[k]))[0] / 65536.0 for k in (2, 4, 6)]
            out.append((i, key, (min(xs), yh, max(xs), yl)))
        elif op in (0x24, 0x25): n = 16
        elif op == 0x3A: prim = '%08X' % w1
        i += n
    return out

T = tris_pos(bytes(zbytes(RDP)))
dmas = [l.split() for l in zopen(DMA) if l.startswith('dma ')]
dmas = [(int(x[1]), int(x[2], 16), int(x[3], 16), int(x[4], 16) & 0xFFF) for x in dmas]
R = m.frames(RB, True); Pf = m.frames(PB, False)
tri = lambda c: collections.Counter({k: v for k, v in c.items() if k[0] == 'tri'})
rr, pp = tri(R[P + OFF][0]), tri(Pf[P][0])
st = collections.Counter(k for _, k, _ in T)
ponly = (st & pp) - rr; ronly = rr - (st & pp)
print(f'task tris {len(T)}; port frame p{P} tris {sum(pp.values())}; retail r{P+OFF} {sum(rr.values())}; '
      f'task&port {sum((st & pp).values())}; port-only {sum(ponly.values())} retail-only {sum(ronly.values())}')

def src_before(off):   # last DMA per SP dest whose rdp offset <= off (DMA issued before the tri was flushed)
    last = {}
    for (o, dram, spa, ln) in dmas:
        if o > off: break
        last[spa] = (dram, ln + 1)
    return last
groups = collections.Counter(); rows = []
left = ponly.copy()
for (off, k, bb) in T:
    if left[k] > 0:
        left[k] -= 1; s = src_before(off)
        mtx = s.get(0x05D0); vtx = s.get(0x0280); vtc = s.get(0x0B70); mt2 = s.get(0x0590)
        g = (f'mtxA {mtx[0]:06X}' if mtx else 'mtxA -') + (f' mtxB {mt2[0]:06X}' if mt2 else ' mtxB -') + \
            (f' vtx {vtx[0]:06X}+{vtx[1]:X}' if vtx else ' vtx -') + (f' vtc {vtc[0]:06X}+{vtc[1]:X}' if vtc else ' vtc -')
        groups[g] += 1; rows.append((off, k[1], bb, g))
for off, prim, bb, g in rows[:60]:
    print(f'  @{off:6d} prim {prim} bbox x{bb[0]:.1f}-{bb[2]:.1f} y{bb[1]:.2f}-{bb[3]:.2f}  {g}')
print('port-only tris by source:')
for g, n in groups.most_common(): print(f'  {n:3d}  {g}')
# all tris by source, to see whether the drifting group is a whole buffer or part of one
allg = collections.Counter()
for (off, k, bb) in T:
    s = src_before(off); vtx = s.get(0x0280); allg[f'vtx {vtx[0]:06X}' if vtx else 'vtx -'] += 1
dv = collections.Counter(g.split(' vtx ')[1].split('+')[0] for g in groups.elements())
print('drift vtx blocks: ' + ', '.join(f'{v}: {n}/{allg["vtx " + v]} tris' for v, n in dv.most_common()))
if MOVED:
    M = collections.Counter(k for _, k, _ in tris_pos(bytes(zbytes(MOVED))))
    gone = st - M; new = M - st
    print(f'--moved: tris changed {sum(gone.values())} -> {sum(new.values())}; of the changed, port-only {sum((gone & ponly).values())}')
# per (matrix, mesh) instance: drifting / total tris. A mesh whose instances all drift but under different matrices, with
# one clean instance, says the shared mesh bytes are equal and the per-instance matrix differs (H-matrix); every instance
# drifting with identical deltas would point at the mesh (H-vtx).
inst = collections.Counter(); instd = collections.Counter(); left2 = ponly.copy()
for (off, k, bb) in T:
    s = src_before(off); mtx = s.get(0x05D0); vtx = s.get(0x0280)
    key = (f'{mtx[0]:06X}' if mtx else '-', f'{vtx[0]:06X}' if vtx else '-')
    inst[key] += 1
    if left2[k] > 0: left2[k] -= 1; instd[key] += 1
print('instances of drifting meshes (matrix, mesh): drift/total')
for key in sorted(inst):
    if key[1] in dv: print(f'  mtx {key[0]} mesh {key[1]}: {instd[key]}/{inst[key]}')
