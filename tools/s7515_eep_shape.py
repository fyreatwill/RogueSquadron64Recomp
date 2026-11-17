#!/usr/bin/env python3
"""s7515 class FL: score [s7515-eep] rows (ROGUESQ_LOG_EEP_SHAPE=1, lib/N64ModernRuntime/librecomp/src/eep.cpp) against the
libultra EEPROM rules, re-derived here independently of the logged hw_ret:
  osEepromLongRead/LongWrite: address > MAXBLOCKS -> -1 before any transfer; then one 8-byte block per step, block >= MAXBLOCKS
  -> -1 (earlier blocks already transferred); nbytes must be a multiple of 8 (hardware loops while nbytes > 0, so a remainder
  over-transfers a whole block). osEepromRead/Write: block >= MAXBLOCKS -> -1. Probe: RS64 cart = EEPROM_TYPE_4K (1), 64 blocks.
Also checks the game's own capacity math: record count * record size + 0x20 header <= capacity <= MAXBLOCKS * 8.
Divergence = host return != hardware return, a hardware-successful op the host skipped, a host transfer hardware refuses,
a remainder, a probe type != 1, or a capacity outside the probed size.
Usage: s7515_eep_shape.py [--controls] LOG...   rc 0 clean + ctl row flagged, 1 live divergence, 3 ctl missing/unflagged, 4 no rows."""
import re, sys

ROW = re.compile(r'\[s7515-eep\] (.*)')

def parse(lines):
    out = []
    for ln in lines:
        m = ROW.search(ln)
        if not m:
            continue
        d = dict(kv.split('=', 1) for kv in m.group(1).split() if '=' in kv)
        out.append(d)
    return out

def hw_ret(fn, addr, nbytes, maxb):
    if fn.startswith('osEepromLong'):
        if addr > maxb:
            return -1
        n = nbytes
        while n > 0:
            if addr >= maxb:
                return -1
            n -= 8; addr += 1
        return 0
    if fn in ('osEepromRead', 'osEepromWrite'):
        return -1 if addr >= maxb else 0
    return None

def issues(r):
    fn = r['fn']; maxb = int(r['maxb']); bad = []
    if fn == 'osEepromProbe':
        if int(r['host_ret']) != 1:
            bad.append('probe_type=%s' % r['host_ret'])
        return bad
    addr = int(r['addr']); nb = int(r['nbytes']); hr = int(r['host_ret']); x = int(r['xfer'])
    h = hw_ret(fn, addr, nb, maxb)
    if int(r['hw_ret']) != h:
        bad.append('model_mismatch logged=%s rederived=%d' % (r['hw_ret'], h))
    if hr != h:
        bad.append('ret host=%d hw=%d' % (hr, h))
    if h == 0 and not x:
        bad.append('host_skipped_valid_op')
    if h != 0 and x:
        bad.append('host_xfer_hw_refuses')
    if fn.startswith('osEepromLong') and nb % 8:
        bad.append('nbytes_remainder=%d' % nb)
    cap = int(r['cap'], 16); cnt = int(r['cnt']); rsz = int(r['rsz'], 16)
    if cap and (cap > maxb * 8 or (rsz and cnt * rsz + 0x20 > cap)):
        bad.append('capacity cap=0x%X cnt=%d rsz=0x%X maxb=%d' % (cap, cnt, rsz, maxb))
    return bad

def score(rows, label, quiet=False):
    if not rows:
        if not quiet: print('%s rows=0' % label)
        return 4
    live = [(r, issues(r)) for r in rows if r.get('ctl') == '0']
    ctl = [(r, issues(r)) for r in rows if r.get('ctl') == '1']
    livebad = [(r, b) for r, b in live if b]
    ctl_ok = bool(ctl) and all(b for _, b in ctl)
    if not quiet:
        fns = {}
        for r, _ in live:
            fns[r['fn']] = fns.get(r['fn'], 0) + 1
        shapes = sorted({(r['fn'], r['addr'], r['nbytes'], r['host_ret'], r['xfer']) for r, _ in live})
        print('%s rows=%d fns=%s ctl_rows=%d ctl_flagged=%d live_bad=%d' % (label, len(live), fns, len(ctl), int(ctl_ok), len(livebad)))
        for s in shapes:
            print('  shape fn=%s addr=%s nbytes=%s host_ret=%s xfer=%s' % s)
        glb = sorted({(r['cap'], r['cnt'], r['rsz'], r['flag']) for r, _ in live if r['fn'] != 'osEepromProbe'})
        print('  globals cap,cnt,rsz,flag: %s' % glb)
        for r, b in livebad[:10]:
            print('  BAD seq=%s fn=%s addr=%s nbytes=%s: %s' % (r['seq'], r['fn'], r['addr'], r['nbytes'], '; '.join(b)))
        for r, b in ctl:
            print('  ctl fn=%s addr=%s nbytes=%s flagged: %s' % (r['fn'], r['addr'], r['nbytes'], '; '.join(b) or 'NO'))
    if livebad:
        return 1
    if not ctl_ok:
        return 3
    return 0

def row(fn, addr, nb, host_ret, xfer, hw=None, cap='0x200', cnt='8', rsz='0x3C', ctl=0, maxb=64):
    if hw is None:
        hw = hw_ret(fn, addr, nb, maxb)
        hw = 0 if hw is None else hw
    return ('[s7515-eep] seq=0 t=0 fn=%s addr=%d nbytes=%d buf=0x80112700 host_ret=%d hw_ret=%d xfer=%d maxb=%d b8=- '
            'cap=%s cnt=%s rsz=%s flag=1 ctl=%d' % (fn, addr, nb, host_ret, hw, xfer, maxb, cap, cnt, rsz, ctl))

def controls():
    good = [row('osEepromProbe', 0, 0, 1, 0), row('osEepromLongRead', 0, 32, 0, 1), row('osEepromLongRead', 4, 480, 0, 1),
            row('osEepromLongWrite', 0, 512, 0, 1), row('osEepromLongRead', 70, 16, 0, 0, hw=-1, ctl=1)]
    ok = score(parse(good), 'synthetic', True) == 0
    mutants = {
        'past_end': good + [row('osEepromLongRead', 63, 16, 0, 0)],      # host skips + returns 0; hw reads block 63 then -1
        'remainder': good + [row('osEepromLongWrite', 0, 12, 0, 1)],
        'probe16k': good + [row('osEepromProbe', 0, 0, 2, 0)],
        'capacity': good + [row('osEepromLongRead', 0, 32, 0, 1, cap='0x800')],
        'no_ctl': good[:-1],
    }
    want = {'past_end': 1, 'remainder': 1, 'probe16k': 1, 'capacity': 1, 'no_ctl': 3}
    for k, v in mutants.items():
        got = score(parse(v), k, True)
        if got != want[k]:
            ok = False
            print('control %s: rc %d want %d' % (k, got, want[k]))
    print('controls synthetic+%d mutants: %s' % (len(mutants), 'PASS' if ok else 'FAIL'))
    return ok

def main(a):
    rc_ctl = 0
    if a and a[0] == '--controls':
        a = a[1:]
        if not controls():
            rc_ctl = 2
    rcs = []
    for p in a:
        try:
            rows = parse(open(p, errors='replace'))
        except OSError:
            rows = []
        rc = score(rows, p)
        print('%s rc=%d' % (p, rc))
        rcs.append(rc)
    worst = next((k for k in (1, 3, 4) if k in rcs), 0)
    return rc_ctl or worst

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
