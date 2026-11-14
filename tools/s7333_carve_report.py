#!/usr/bin/env python3
"""s7333 item 24: per-run FIFO host-live table + carve-key erase paths from a run log ([s7332] fifo / [s7333] lines).
usage: s7333_carve_report.py <run.log> [...]. rc 0 when every in-carve (guest=2 fl=6) FIFO transition reads host-live (host=0)."""
import re, sys, collections
rc = 0
for path in sys.argv[1:]:
    fifo = collections.Counter(); ev = collections.Counter(); above = collections.Counter(); bad_above = 0
    for ln in open(path, 'rb'):
        ln = ln.decode('latin1')
        m = re.match(r'\[s7332\] fifo .* guest=(\d):([0-9A-F]+):\S+ host=(\d+) ', ln)
        if m: fifo[(m.group(1), m.group(2), m.group(3))] += 1; continue
        m = re.match(r'\[s7333\] carve-key (\S+) key=(\S+) old=(\S+) .* guest fl=(\S+) sz=\S+ carve_ok=(\d)', ln)
        if m: ev[(m.group(1), 'guest_fl=' + m.group(4), 'carve_ok=' + m.group(5))] += 1; continue
        m = re.match(r'\[s7333\] fifo out=\S+ guest=0 host=(\d+) top=(\S+) dist=(\S+) .* topw=(\S+)', ln)
        if m: above[('sentinel' if int(m.group(4), 16) >> 16 & 8 else 'nonsentinel', 'host=' + m.group(1))] += 1
    inc = sum(v for k, v in fifo.items() if k[0] == '2' and int(k[1], 16) & 6 == 6)
    live = sum(v for k, v in fifo.items() if k[0] == '2' and int(k[1], 16) & 6 == 6 and k[2] == '0')
    print(f'{path}: in-carve FIFO transitions host-live {live}/{inc}')
    for k, v in sorted(fifo.items()): print(f'  fifo guest={k[0]} fl={k[1]} host={k[2]}: {v}')
    for k, v in sorted(ev.items()): print(f'  erase {k}: {v}')
    for k, v in sorted(above.items()): print(f'  above-heap {k}: {v}')
    if inc == 0 or live != inc: rc = 1
sys.exit(rc)
