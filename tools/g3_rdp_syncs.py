#!/usr/bin/env python3
"""s6805 G3: every FULL_SYNC of an RDP stream, INCLUDING empty ones, as (vi, rects, tris), and run-length segments
over them. g3_rdp_segments.all_frames drops a sync with no tri/texrect (`if cur:`), so its frame index is not the
sync index: s6804's port frame->VI join (one VI per sync) was shifted by every empty frame before it, and inside the
lvl9 death camera ~50 of the ticks render empty frames in both arms. Port records carry the VI (RS64_RDP_BIN_PORT_VI=1);
retail records do not (vi = -1), but retail swaps once per sim tick, so retail sync index - offset = tick.
usage: g3_rdp_syncs.py BIN retail|port [FROM_SYNC TO_SYNC]   (segments of (rects, tri bucket of 100, empty))
"""
import os, pickle, struct, sys


def syncs(path, retail):
    pk = path + '.syncs.pkl'
    if os.path.exists(pk) and os.path.getmtime(pk) > os.path.getmtime(path):
        return pickle.load(open(pk, 'rb'))
    H, out, rects, tris = (20 if retail else 16), [], 0, 0
    with open(path, 'rb') as f:
        while True:
            h = f.read(H)
            if len(h) < H:
                break
            if retail:
                ln, vi = struct.unpack_from('<I', h, 12)[0], -1
            else:
                ln, vi = struct.unpack_from('<I', h, 8)[0], struct.unpack_from('<I', h, 12)[0]
            b = f.read(ln); a = 0
            while a + 8 <= len(b):
                op = b[a + 3] & 0x3F; n = 8
                if 0x08 <= op <= 0x0F:
                    n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0); tris += 1
                elif op in (0x24, 0x25):
                    n = 16; rects += 1
                elif op == 0x29:
                    out.append((vi, rects, tris)); rects = tris = 0
                a += n
    pickle.dump(out, open(pk, 'wb'))
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    S = syncs(sys.argv[1], sys.argv[2] == 'retail')
    lo, hi = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, len(S))
    ne = sum(1 for _, r, t in S if r or t)
    print(f"syncs {len(S)}  non-empty {ne} (= g3_rdp_segments frame count)  empty {len(S) - ne}")
    key = lambda s: (s[1], s[2] // 100, not (s[1] or s[2]))
    i, cum_ne = lo, sum(1 for _, r, t in S[:lo] if r or t)
    while i < hi:
        j = i
        while j < hi and key(S[j]) == key(S[i]):
            j += 1
        k = key(S[i]); nne = 0 if k[2] else j - i
        print(f"  sync {i:6d}-{j:6d} n={j - i:4d} vi {S[i][0]}-{S[j - 1][0]}  nonempty-idx {cum_ne}  rects={k[0]:3d} tris~{k[1] * 100:5d}{'  EMPTY' if k[2] else ''}")
        cum_ne += nne; i = j


main()
