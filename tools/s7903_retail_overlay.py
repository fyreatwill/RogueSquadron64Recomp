#!/usr/bin/env python3
"""s7903 G3 island B: rebuild a RETAIL gfx task from oracle RDRAM dumps by overlaying them onto a port s7751 task snapshot,
so the cxd4 replay (tools/s7900_dma_trace/replay_dma) yields retail's own task output + SP DMA log, and
tools/s7900_tri_source.py-style analysis can name the (instance matrix, vertex block) retail draws.
Retail rows: "[ramdump] vi= n= w=" (base range, given by --base START) and "[ramdumpK] vi= n= a= w=" (printed at osSpTaskLoad hit
n, only when the range changed). State of a range at task n = its latest row with row.n <= n.
The task header range 0x377C8 (OSTask, 64 bytes) is copied into the snapshot's DMEM 0xFC0 too (pointer fields as the guest wrote
them; replay.c applies osVirtualToPhysical).
Control: the replay of an overlaid snapshot must reproduce one retail frame of the retail RDP bin exactly (checked by the driver,
tools/s7903_retail_bind.py), otherwise the overlay is missing state and nothing it says counts.
usage: s7903_retail_overlay.py ORACLE.log PORTSNAP.bin N OUT.bin [--base 0x700000] [--list]
  --list : print every n with its vi and which ranges changed, then exit (PORTSNAP/N/OUT ignored).
"""
import sys, re, struct, bisect
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from rs64_zopen import zopen, zbytes

TASK = 0x377C8
rx = re.compile(r'^\[ramdump(\d*)\] vi=(\d+) n=(\d+) (?:a=([0-9A-F]+) )?w=([0-9A-F]+)')

def load(log, base=0x700000):
    """-> {start: [(n, vi, bytes)] sorted by n}"""
    R = {}
    with zopen(log) as f:
        for l in f:
            if not l.startswith('[ramdump'): continue
            m = rx.match(l)
            if not m: continue
            st = int(m.group(4), 16) & 0xFFFFFF if m.group(1) else base
            R.setdefault(st, []).append((int(m.group(3)), int(m.group(2)), bytes.fromhex(m.group(5))))
    for v in R.values(): v.sort(key=lambda r: r[0])
    return R

def state(R, n):
    """{start: bytes} as of task n (None for a range with no row yet)"""
    out = {}
    for st, rows in R.items():
        i = bisect.bisect_right([r[0] for r in rows], n) - 1
        if i >= 0: out[st] = rows[i][2]
    return out

def task_vis(R):
    """[(n, vi)] for every n any range printed a row at"""
    s = {}
    for rows in R.values():
        for n, vi, _ in rows: s[n] = vi
    return sorted(s.items())

def overlay(snap, st):
    b = bytearray(snap); H = 20 + 4096; ram = struct.unpack_from('<5I', b, 0)[4]
    for a0, w in st.items():
        for i in range(0, len(w) - 3, 4):
            ad = a0 + i
            if ad + 4 <= ram: struct.pack_into('<I', b, H + ad, struct.unpack_from('>I', w, i)[0])
        if a0 == TASK:
            for i in range(16): struct.pack_into('<I', b, 20 + 0xFC0 + 4 * i, struct.unpack_from('>I', w, 4 * i)[0])
    return bytes(b)

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    base = int(a[a.index('--base') + 1], 16) if '--base' in a else 0x700000
    R = load(a[0], base)
    if '--list' in a:
        for n, vi in task_vis(R):
            ch = [f'{st:06X}' for st, rows in sorted(R.items()) if any(r[0] == n for r in rows)]
            print(n, vi, ' '.join(ch))
        sys.exit(0)
    snap, n, out = a[1], int(a[2]), a[3]
    st = state(R, n)
    open(out, 'wb').write(overlay(bytes(zbytes(snap)), st))
    t = st.get(TASK)
    print(f'n={n} ranges={len(st)} task data_ptr={struct.unpack_from(">I", t, 0x30)[0]:08X}' if t else f'n={n} ranges={len(st)} (no task row)')
