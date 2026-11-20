#!/usr/bin/env python3
"""s7399 class BI report: last complete [s7399-ev]/[s7399-rv] table of a ROGUESQ_S7399_EVP=1 run.

Expected event bindings (static, tools/s7399_evpayload_census.py): every host delivery from an event source onto its
bound queue must carry the bound msg; any other (mq, msg) for a Vi/Si/Sp/Dp/Ai source is a payload MISMATCH.
usage: tools/s7399_evp_report.py <run.log>
exit 0 = control PASS (or not armed) and 0 mismatch; 2 = control armed but its planted row missing/unflagged;
     3 = a mismatch outside the control."""
import re, sys
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from rs64_zopen import zopen  # s7723
SRC = {-1: 'host-thread', 0: 'Timer', 1: 'Sp', 2: 'Si', 3: 'Ai', 4: 'Vi', 5: 'Pi', 6: 'Dp'}
BOUND = {'Vi': {0x80114388: 0}, 'Si': {0x80110770: 0}, 'Sp': {0x8011A420: 0x80128C70}, 'Dp': {0x8011A408: 0},
         'Ai': {0x80149670: 0x801496A0}}
QN = {0x80114388: 'VI', 0x80110770: 'SI', 0x8011A420: 'SP', 0x8011A408: 'DP', 0x80149670: 'AI'}
EV = re.compile(r'^\[s7399-ev\] mq=(\w+) src=(-?\d+) msg=(\w+) n=(\d+) unsent=(\d+)')
RV = re.compile(r'^\[s7399-rv\] mq=(\w+) msg=(\w+) tb=(-?\d+) n=(\d+)')


def main():
    blocks, cur, ctlq, ctlline = [], None, None, None
    for ln in zopen(sys.argv[1], errors='replace'):
        if ln.startswith('[s7399-begin]'):
            m = re.search(r'ctl_q=(\w+)', ln)
            cur = {'ev': [], 'rv': [], 'ctl': int(m.group(1), 16)}
            blocks.append(cur)
        elif ln.startswith('[s7399-ctl]'):
            ctlline = ln.strip()
        elif cur is not None:
            m = EV.match(ln)
            if m:
                cur['ev'].append((int(m.group(1), 16), int(m.group(2)), int(m.group(3), 16), int(m.group(4)), int(m.group(5))))
            m = RV.match(ln)
            if m:
                cur['rv'].append((int(m.group(1), 16), int(m.group(2), 16), int(m.group(3)), int(m.group(4))))
    if not blocks:
        print('NO s7399 TABLE'); sys.exit(2)
    b = blocks[-1]; ctlq = b['ctl'] or None
    print('tables=%d ctl=%s' % (len(blocks), ctlline or 'not-armed'))
    mism, ctl_hit = 0, False
    print('== deliveries by source (event sources checked against the bound msg)')
    for mq, src, msg, n, uns in sorted(b['ev'], key=lambda r: (r[1], r[0], r[2])):
        s = SRC.get(src, str(src))
        verdict = ''
        if s in BOUND:
            exp = BOUND[s].get(mq)
            if exp is None or exp != msg:
                if ctlq and mq == ctlq and msg == 0xBADC0DE0:
                    verdict = 'MISMATCH(CONTROL)'; ctl_hit = True
                else:
                    verdict = 'MISMATCH expected=%s' % ('unbound-mq' if exp is None else '%08X' % exp); mism += 1
            else:
                verdict = 'bound'
        if s in BOUND or verdict:
            print('  src=%-5s mq=%08X(%s) msg=%08X n=%-7d unsent=%-5d %s' % (s, mq, QN.get(mq, 'ctl' if mq == ctlq else '?'), msg, n, uns, verdict))
    other = {}
    for mq, src, msg, n, uns in b['ev']:
        s = SRC.get(src, str(src))
        if s not in BOUND:
            other[s] = other.get(s, 0) + n
    print('  other sources (not event-bound, listed only):', other)
    print('== receives on event queues: (msg, type byte) histogram')
    for mq, msg, tb, n in sorted(b['rv']):
        print('  %s mq=%08X msg=%08X tb=%s n=%d' % (QN.get(mq, 'ctl' if mq == ctlq else '?'), mq, msg, ('0x%02X' % tb) if tb >= 0 else '-', n))
    ctl_rv = any(mq == ctlq and msg == 0xBADC0DE0 for mq, msg, tb, n in b['rv']) if ctlq else False
    if ctlline:
        ok = ctl_hit and ctl_rv
        print('CONTROL %s (delivery flagged=%d, received=%d)' % ('PASS' if ok else 'FAIL', ctl_hit, ctl_rv))
        if not ok:
            sys.exit(2)
    print('VERDICT %s mismatches=%d' % ('H-none' if mism == 0 else 'H-payload', mism))
    sys.exit(3 if mism else 0)


if __name__ == '__main__':
    main()
