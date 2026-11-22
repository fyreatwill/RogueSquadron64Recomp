#!/usr/bin/env python3
"""s7210 field-mode census over a ROGUESQ_G5B_FRAME stream (.cap): which swaps draw with the RDP Set Scissor field bit.
usage: s7210_field_census.py cap [--pos-control]
Per swap: scissor ops total / with field bit (w1 bit 25) / odd (bit 24), widest 16-bit colour image + width, scissor rect.
Prints runs of consecutive field-mode swaps grouped by (cimg, width, field/odd pattern) plus whole-stream totals.
Times: mach_absolute_time ticks (24 MHz on Apple silicon) from the first swap.
Positive control: all scissor ops are counted too (must be > 0 on every drawing swap), and field swaps are reported per run."""
import struct, sys, collections
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from rs64_zopen import zopen, zbytes  # s7805: zst-only retained inputs
import io; f = io.BytesIO(zbytes(sys.argv[1])); rd = f.read
sw = -1; t0 = None; per = {}
def cur():
    return per.setdefault(sw, {'sc': 0, 'fld': 0, 'odd': 0, 'cimg': {}, 'rect': collections.Counter(), 't': 0})
CH = 1 << 22
while True:
    h = rd(4)
    if len(h) < 4: break
    tag = struct.unpack('<I', h)[0]
    if tag == 0x50415753:
        t, s = struct.unpack('<QI', rd(12)); sw = s
        if t0 is None: t0 = t
        cur()['t'] = t; continue
    if tag == 0x204D4152: f.seek(0x1000000, 1); continue
    if tag != 0x20474E52: print('bad tag %08X at %d' % (tag, f.tell())); break
    lo, n = struct.unpack('<II', rd(8))
    if n > 0x200000: f.seek(n, 1); continue
    b = rd(n); d = cur(); a = 0
    while a + 8 <= n:
        w0, w1 = struct.unpack_from('<II', b, a); op = (w0 >> 24) & 0x3F; l = 8
        if 8 <= op <= 15: l = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
        elif op in (0x24, 0x25): l = 16
        elif op == 0x3F and ((w0 >> 19) & 3) == 2:
            w = (w0 & 0x3FF) + 1; c = w1 & 0xFFFFFF; d['cimg'][c] = w
        elif op == 0x2D:
            d['sc'] += 1
            if w1 & 0x02000000:
                d['fld'] += 1
                if w1 & 0x01000000: d['odd'] += 1
            d['rect'][((w0 >> 12) & 0xFFF) // 4, (w0 & 0xFFF) // 4, ((w1 >> 12) & 0xFFF) // 4, (w1 & 0xFFF) // 4, bool(w1 & 0x02000000)] += 1
        a += l
tot = collections.Counter(); runs = []
for s in sorted(per):
    d = per[s]; tot['swaps'] += 1; tot['sc'] += d['sc']; tot['fld'] += d['fld']; tot['drawing'] += d['sc'] > 0
    if d['fld']:
        tot['fswaps'] += 1
        cw = max(d['cimg'].items(), key=lambda kv: kv[1]) if d['cimg'] else (0, 0)
        key = (cw[0], cw[1], 'odd' if d['odd'] == d['fld'] else ('even' if d['odd'] == 0 else 'mix'))
        if runs and runs[-1]['key'] == key and s - runs[-1]['last'] <= 30:
            r = runs[-1]; r['last'] = s; r['n'] += 1; r['fld'] += d['fld']; r['sc'] += d['sc']; r['rect'].update(d['rect']); r['t1'] = d['t']
        else:
            runs.append({'key': key, 'first': s, 'last': s, 'n': 1, 'fld': d['fld'], 'sc': d['sc'], 'rect': collections.Counter(d['rect']), 't0': d['t'], 't1': d['t']})
print('swaps %d drawing(scissor>0) %d scissors %d field-scissors %d field-swaps %d' % (tot['swaps'], tot['drawing'], tot['sc'], tot['fld'], tot['fswaps']))
for r in runs:
    rc = ' '.join('%d,%d-%d,%d%s x%d' % (k[0], k[1], k[2], k[3], 'F' if k[4] else '', v) for k, v in r['rect'].most_common(3))
    print('run swaps %d-%d (%d) t %.1f-%.1f s cimg %06X w %d %s field %d/%d scissors | %s' % (
        r['first'], r['last'], r['n'], (r["t0"] - t0) / 24e6 if t0 else 0, (r["t1"] - t0) / 24e6 if t0 else 0, r['key'][0], r['key'][1], r['key'][2], r['fld'], r['sc'], rc))
# context: screen widths over the whole stream, to place field runs on the route
ctx = []; last = None
for s in sorted(per):
    d = per[s]
    if not d['cimg']: continue
    cw = max(d['cimg'].items(), key=lambda kv: kv[1])
    k = (cw[0], cw[1])
    if k != last: ctx.append((s, k)); last = k
print('cimg segments %d (all):' % len(ctx))
print('  ' + ' '.join('%d:%06X/%d' % (s, k[0], k[1]) for s, k in ctx))
