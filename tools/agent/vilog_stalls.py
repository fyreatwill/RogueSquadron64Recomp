#!/usr/bin/env python3
"""s7459 class DO: stall score of a game log's [vi] update_screen rows (m6 harness run.log).

usage: vilog_stalls.py <log> [gap_vi=1800] [--from-vi N]
prints: fs_holds=<n> max_fs_hold_vi=<m> last_fs=<f> vi_rows=<r>      (no fs= rows -> fs_holds=na)

The rows print every 64 VIs whatever the game does (rt64_render_context / librecomp VI path), so their COUNT proves only
that the VI thread ticks. fs= is the game's frame-swap counter: a run of rows with the same fs spanning >= gap_vi VIs
(1800 = 30 s at the real-time 60 Hz VI) is a held frame while VI keeps running (the s6993 boot freeze: fs stuck at 273).
--from-vi: score only rows with update_screen # >= N (skip boot/load).
"""
import re, sys
R = re.compile(r'\[vi\] update_screen #(\d+) .*?\bfs=(\d+)')
def score(path, gap=1800, from_vi=0):
    rows = []
    with open(path, 'rb') as f:
        for b in f:
            if b'update_screen #' not in b: continue
            m = R.search(b.decode('latin-1'))
            if m and int(m.group(1)) >= from_vi: rows.append((int(m.group(1)), int(m.group(2))))
    if not rows: return dict(n='na', mx=0, last='na', rows=0, eps=[])
    eps = []; s_vi, s_fs = rows[0]; mx = 0; prev_vi = s_vi
    for vi, fs in rows[1:] + [(rows[-1][0] + 1, None)]:
        if fs != s_fs:
            last_vi = prev_vi
            h = last_vi - s_vi; mx = max(mx, h)
            if h >= gap: eps.append((s_vi, last_vi, s_fs))
            s_vi, s_fs = vi, fs
        prev_vi = vi
    return dict(n=len(eps), mx=mx, last=rows[-1][1], rows=len(rows), eps=eps)
if __name__ == '__main__':
    a = sys.argv[1:]; fv = 0
    if '--from-vi' in a: i = a.index('--from-vi'); fv = int(a[i+1]); del a[i:i+2]
    r = score(a[0], int(a[1]) if len(a) > 1 else 1800, fv)
    print(f"fs_holds={r['n']} max_fs_hold_vi={r['mx']} last_fs={r['last']} vi_rows={r['rows']}")
    for e in r['eps']: print(f"  hold vi={e[0]}..{e[1]} fs={e[2]}", file=sys.stderr)
