#!/usr/bin/env python3
"""s7751: compare two RDP command byte streams (plain big-endian bytes): the port's raw ucode output captured by
ROGUESQ_S7751_SNAP (the tail of a snap .bin) and an independent RSP's output for the same task (tools/s7751_cxd4_task/replay).
Prints command counts, the first divergence, the per-opcode diff census, and every textured triangle whose start W is
within +-WTOL (the s7309/s7310 'pinned' signature: a clip vertex at w~0 collapsed onto fb x=0).
usage: s7751_rdp_compare.py <port.snap.bin | port.rdp> <ref.rdp> [--wtol 0.01]
exit 0 = streams identical, 1 = they differ (diff census printed), 2 = usage/format error."""
import struct, sys, collections

def load(path):
    b = open(path, 'rb').read()
    if b[:4] == b'S751'[::-1] or b[:4] == struct.pack('<I', 0x31353753):
        ram = struct.unpack_from('<I', b, 16)[0]
        off = 20 + 4096 + ram
        n = struct.unpack_from('<I', b, off)[0]
        return b[off + 4: off + 4 + n]
    return b

def cmd_len(op):
    if 0x08 <= op <= 0x0F:
        return 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
    if op in (0x24, 0x25):
        return 16
    return 8

def split(b):
    out, i = [], 0
    while i + 8 <= len(b):
        op = b[i] & 0x3F
        n = cmd_len(op)
        out.append((op, b[i:i + n]))
        i += n
    return out

def s32(b, o): return struct.unpack_from('>i', b, o)[0]
def s16(b, o): return struct.unpack_from('>h', b, o)[0]
def u16(b, o): return struct.unpack_from('>H', b, o)[0]

def tri_info(op, c):
    xl, xh, xm = s32(c, 8) / 65536.0, s32(c, 16) / 65536.0, s32(c, 24) / 65536.0
    yl = (((struct.unpack_from('>I', c, 0)[0] & 0x3FFF) ^ 0x2000) - 0x2000) / 4.0
    w1 = struct.unpack_from('>I', c, 4)[0]
    ym = ((((w1 >> 16) & 0x3FFF) ^ 0x2000) - 0x2000) / 4.0
    yh = (((w1 & 0x3FFF) ^ 0x2000) - 0x2000) / 4.0
    w = None
    if op & 2:
        t = 32 + (64 if op & 4 else 0)
        w = ((s16(c, t + 4) << 16) | u16(c, t + 20)) / 65536.0
    return dict(xl=xl, xh=xh, xm=xm, yh=yh, ym=ym, yl=yl, w=w)

def pinned(cmds, wtol):
    res = []
    for k, (op, c) in enumerate(cmds):
        if 0x08 <= op <= 0x0F and op & 2 and len(c) == cmd_len(op):
            ti = tri_info(op, c)
            if abs(ti['w']) <= wtol:
                res.append((k, op, ti))
    return res

def main():
    import argparse
    ap = argparse.ArgumentParser(description='s7751 RDP stream compare')
    ap.add_argument('port'); ap.add_argument('ref'); ap.add_argument('--wtol', type=float, default=0.01)
    o = ap.parse_args(); a = [o.port, o.ref]; wtol = o.wtol
    A, B = split(load(a[0])), split(load(a[1]))
    print(f'port cmds={len(A)} ref cmds={len(B)}')
    for name, cm in (('port', A), ('ref', B)):
        tris = sum(1 for op, _ in cm if 0x08 <= op <= 0x0F)
        print(f'{name}: tris={tris} textured={sum(1 for op, _ in cm if 0x08 <= op <= 0x0F and op & 2)}')
        for k, op, ti in pinned(cm, wtol):
            print(f'  {name} |W|<={wtol} cmd#{k} op={op:02X} W={ti["w"]:+.5f} xh={ti["xh"]:.2f} xm={ti["xm"]:.2f} xl={ti["xl"]:.2f} '
                  f'y={ti["yh"]:.2f}/{ti["ym"]:.2f}/{ti["yl"]:.2f}')
    n = min(len(A), len(B))
    first = next((i for i in range(n) if A[i][1] != B[i][1]), None)
    diff = collections.Counter(A[i][0] for i in range(n) if A[i][1] != B[i][1])
    same = n - sum(diff.values())
    print(f'aligned compare: {same}/{n} commands byte-identical; first divergence at cmd#{first}; length delta {len(A) - len(B)}')
    if diff:
        print('differing commands by opcode: ' + ' '.join(f'{op:02X}:{c}' for op, c in sorted(diff.items())))
        if first is not None:
            for j in range(first, min(first + 3, n)):
                print(f'  #{j} port {A[j][1][:16].hex()}  ref {B[j][1][:16].hex()}')
    return 0 if (len(A) == len(B) and not diff) else 1

if __name__ == '__main__':
    sys.exit(main())
