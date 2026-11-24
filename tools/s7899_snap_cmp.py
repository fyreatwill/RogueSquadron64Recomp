#!/usr/bin/env python3
"""s7899 G3 island B, H-rsp vs H-input: for every s7751 gfx-task snapshot (k900_s*.bin, ROGUESQ_S7751_EVERY) replay the task
on the independent cxd4 RSP (tools/s7751_cxd4_task/replay), then compare three triangle multisets for that task:
  port  = our LLE ucode output (snap tail), cxd4 = cxd4 on the same RDRAM/DMEM, retail = the retail frame paired with the port
  frame whose tris equal the snap's (port frame found in PORT.bin by exact multiset, paired at offset OFF).
Outcomes: cxd4 == port != retail on drift frames -> H-input (the guest data fed to the RSP differs; our RSP is faithful);
          cxd4 == retail != port              -> H-rsp (our LLE RSP computes the drifting vertices differently).
Control (same run): a copy of the first snap's port stream with one tri's XH +1 px must count 1/1 vs port (detector live).
usage: s7899_snap_cmp.py TASKDIR RETAIL.bin PORT.bin OFF [--j0 6073 --j1 6300]
"""
import sys, os, glob, struct, subprocess, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
a = sys.argv[1:]
if len(a) < 4: print(__doc__); sys.exit(2)
TD, RB, PB, OFF = a[0], a[1], a[2], int(a[3])
opt = lambda n, d: int(a[a.index(n) + 1]) if n in a else d
J0, J1 = opt('--j0', 6073), opt('--j1', 6300)
sys.argv = [sys.argv[0], '--tri-geom']
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)

def snap_rdp(path):
    b = open(path, 'rb').read(); ram = struct.unpack_from('<I', b, 16)[0]; off = 20 + 4096 + ram
    n = struct.unpack_from('<I', b, off)[0]; return b[off + 4: off + 4 + n], struct.unpack_from('<I', b, 8)[0]

def tris_be(b):
    c = collections.Counter(); i = 0; prim = None
    while i + 8 <= len(b):
        w0, w1 = struct.unpack_from('>II', b, i); op = (w0 >> 24) & 0x3F; n = 8
        if 0x08 <= op <= 0x0F:
            if i + 32 > len(b): break
            n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
            c[('tri', prim) + struct.unpack_from('>8I', b, i) + (w0 & 0x3FFF,)] += 1
        elif op in (0x24, 0x25): n = 16
        elif op == 0x3A: prim = '%08X' % w1
        i += n
    return c
tri = lambda c: collections.Counter({k: v for k, v in c.items() if k[0] == 'tri'})
d = lambda x, y: (sum((x - y).values()), sum((y - x).values()))

R = [tri(c) for c, _ in m.frames(RB, True)]; P = [tri(c) for c, _ in m.frames(PB, False)]
idx = collections.defaultdict(list)
for j, c in enumerate(P): idx[hash(frozenset(c.items()))].append(j)
snaps = sorted(f for f in glob.glob(os.path.join(TD, 'k900_s*.bin')) if not f.endswith('_end.bin'))
print(f'snaps {len(snaps)}; retail frames {len(R)} port frames {len(P)} OFF {OFF}')
ok = None; rows = []
for f in snaps:
    rdp, serial = snap_rdp(f); pt = tris_be(rdp)
    out = f[:-4] + '.cxd4.rdp'
    if not os.path.exists(out):
        r = subprocess.run([os.path.join(HERE, 's7751_cxd4_task', 'replay'), f, out], capture_output=True, text=True)
        if r.returncode != 0: print(f'  s{serial}: replay rc {r.returncode} {r.stderr[-200:]}'); continue
    ct = tris_be(open(out, 'rb').read())
    if ok is None:   # control: plant XH +1 px on one tri
        k = sorted(pt, key=repr)[0]; g = list(k); g[6] = (g[6] + 65536) & 0xFFFFFFFF; pl = pt.copy(); pl[k] -= 1; pl[tuple(g)] += 1; pl += collections.Counter()
        ok = d(pl, pt) == (1, 1); print(f'control: planted XH+1 vs port {d(pl, pt)} -> {"PASS" if ok else "FAIL"}')
    js = idx.get(hash(frozenset(pt.items())), [])
    j = next((x for x in js if J0 - 400 <= x < J1 + 400), js[0] if js else None)
    if j is None or not 0 <= j + OFF < len(R):
        print(f'  s{serial}: tris {sum(pt.values())} port-vs-cxd4 {d(pt, ct)} (no port frame match)'); continue
    rr = R[j + OFF]
    rows.append((serial, j, d(pt, ct), d(pt, rr), d(ct, rr)))
    print(f'  s{serial} p{j} r{j + OFF} tris {sum(pt.values())}: port-vs-cxd4 {d(pt, ct)}  port-vs-retail {d(pt, rr)}  cxd4-vs-retail {d(ct, rr)}'
          f'{"  [drift window]" if J0 <= j < J1 else ""}')
dr = [r for r in rows if r[3] != (0, 0)]
print(f'tasks matched {len(rows)}; with port-vs-retail diffs {len(dr)}; of those cxd4==port {sum(r[2] == (0, 0) for r in dr)} cxd4==retail {sum(r[4] == (0, 0) for r in dr)}')
sys.exit(0 if ok else 3)
