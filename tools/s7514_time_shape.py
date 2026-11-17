#!/usr/bin/env python3
"""s7514 class FK: score [s7514-time] rows (ROGUESQ_LOG_TIME_SHAPE=1, src/main/upstream_compat.cpp) against the hardware rule.

Hardware: CP0 Count ticks at 46.875 MHz (93.75 MHz / 2) -> osGetTime advances 46,875 ticks per ms, monotone, 64-bit.
Checks per log:
  rate     d(osGetTime)/d(host ms) within 0.2% of 46875 (whole run and every 30-swap step within 2%)
  mono     osGetTime strictly increasing; the game's VI-retrace stamp 0x80128ED8 non-decreasing mod 2^32
  vi       ticks per VI ordinal from the VI stamp (median); reported, hardware NTSC ~779.7k-781.3k (59.94-60.1 Hz)
  clk      osClockRate lo == 46875000 (s7402 CLOCKFIX) on every row after boot
  gate     profiler-bar gate 0x80038CE0 == 0 on every row outside the ctl window once mainGameLoop ran, == 1 inside it
           (ctl rows must exist: the poke is the positive control that the row reads live guest RAM)
rc 0 = all pass, 1 = live rate/mono/clk/gate defect, 3 = ctl window missing or not seen, 4 = no rows.
--controls runs 1 synthetic-good + 4 mutants (rate 62500/ms, backwards step, gate leak, clk unscaled) first; each must flip.
"""
import re, sys, statistics

ROW = re.compile(r'\[s7514-time\] n=(\d+) vi=(\d+) ns=(-?\d+) ostime=(\d+) vit=(\d+) fint=(\d+) gfxd=(\d+) clk=(\d+) gate=(\d+) ctl=(\d+)')


def parse(lines):
    out = []
    for l in lines:
        m = ROW.search(l)
        if m:
            n, vi, ns, ot, vit, fint, gfxd, clk, gate, ctl = (int(x) for x in m.groups())
            out.append(dict(n=n, vi=vi, ns=ns, ot=ot, vit=vit, fint=fint, gfxd=gfxd, clk=clk, gate=gate, ctl=ctl))
    return out


def score(rows):
    if len(rows) < 4:
        return 4, {'rows': len(rows)}
    r = {'rows': len(rows)}
    d_ms = (rows[-1]['ns'] - rows[0]['ns']) / 1e6
    r['rate'] = (rows[-1]['ot'] - rows[0]['ot']) / d_ms if d_ms > 0 else 0
    steps = []
    back = 0
    vitback = 0
    tpv = []
    for a, b in zip(rows, rows[1:]):
        dm = (b['ns'] - a['ns']) / 1e6
        if dm > 5:
            steps.append((b['ot'] - a['ot']) / dm)
        if b['ot'] <= a['ot']:
            back += 1
        dv = (b['vit'] - a['vit']) & 0xFFFFFFFF
        if dv > 0x80000000:
            vitback += 1
        dvi = b['vi'] - a['vi']
        if dvi > 0 and a['vit'] and dv and dv < 0x80000000:
            tpv.append(dv / dvi)
    r['step_bad'] = sum(1 for s in steps if abs(s / 46875 - 1) > 0.02)
    r['back'] = back
    r['vitback'] = vitback
    r['ticks_per_vi'] = round(statistics.median(tpv)) if tpv else 0
    post = [x for x in rows if x['clk'] != 62500000 or x['n'] > 60]
    r['clk_bad'] = sum(1 for x in post if x['n'] > 60 and x['clk'] != 46875000)
    # gate: first row with gate 0 marks mainGameLoop; after it, ctl rows must be 1 and the rest 0
    first0 = next((i for i, x in enumerate(rows) if x['gate'] == 0), None)
    after = rows[first0:] if first0 is not None else []
    r['gate_leak'] = sum(1 for x in after if not x['ctl'] and x['gate'] != 0)
    ctl_rows = [x for x in after if x['ctl']]
    r['ctl_rows'] = len(ctl_rows)
    r['ctl_seen'] = sum(1 for x in ctl_rows if x['gate'] == 1)
    r['gfxd_max_ms'] = round(max(x['gfxd'] for x in rows) / 46875, 2)
    r['fint_med_ms'] = round(statistics.median([x['fint'] for x in rows if x['fint']] or [0]) / 46875, 2)
    live_bad = abs(r['rate'] / 46875 - 1) > 0.002 or r['step_bad'] or back or vitback or r['clk_bad'] or r['gate_leak']
    if live_bad:
        return 1, r
    if not ctl_rows or r['ctl_seen'] != len(ctl_rows):
        return 3, r
    return 0, r


def synth(mut=None):
    rows = []
    for i in range(1, 60):
        n = i * 30
        ns = 10_000_000_000 + n * 33_333_333
        rate = 0.0625 if mut == 'rate' else 0.046875
        ot = int((ns - 10_000_000_000) * rate) + 1000
        if mut == 'back' and i == 30:
            ot -= 5_000_000
        vi = n * 2
        vit = (vi * 781_250) & 0xFFFFFFFF
        ctl = 1 if 600 <= n < 720 else 0
        gate = 1 if (ctl or n < 60) else 0
        if mut == 'gate' and n == 1200:
            gate = 1
        clk = 62500000 if (mut == 'clk' and n > 300) else 46875000
        rows.append(f"[s7514-time] n={n} vi={vi} ns={ns} ostime={ot} vit={vit} fint=1562500 gfxd=400000 clk={clk} gate={gate} ctl={ctl}")
    return parse(rows)


def main():
    a = sys.argv[1:]
    worst = 0
    if a and a[0] == '--controls':
        a = a[1:]
        ok = score(synth())[0] == 0
        for m in ('rate', 'back', 'gate', 'clk'):
            ok &= score(synth(m))[0] == 1
        print(f"controls synthetic+4 mutants: {'PASS' if ok else 'FAIL'}")
        if not ok:
            worst = 3
    for p in a:
        rc, r = score(parse(open(p, errors='replace')))
        print(p, f"rc={rc}", ' '.join(f"{k}={v:.1f}" if isinstance(v, float) else f"{k}={v}" for k, v in r.items()))
        worst = max(worst, rc)
    return worst


if __name__ == '__main__':
    sys.exit(main())
