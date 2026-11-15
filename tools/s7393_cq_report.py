#!/usr/bin/env python3
"""s7393 class BC report: last complete [s7393-cq] table of a ROGUESQ_S7393_CQ=1 run, joined with the static census
(tools/s7393_createmq_census.py) by guest call site (gra - 8).

usage: tools/s7393_cq_report.py <run.log> [disasm=/tmp/s7419_canon.dis]
exit 0 = control PASS (or not armed) and no orphan / lost row outside it; 2 = control armed but FAILED or no table;
     3 = a guest re-create orphaned a live waiter or discarded a pending message (rows marked LIVE).
"""
import re, sys, subprocess, os

ROW = re.compile(r'^\[s7393-cq\] mq=(\w+) key=(\S+) gra=(\w+) cnt=(-?\d+) creates=(\d+) recreates=(\d+) lost=(\d+) '
                 r'orphan_r=(\d+) orphan_s=(\d+) raw_r=(\d+) raw_s=(\d+) held=(\d+)')


def main():
    av = [a for a in sys.argv[1:] if not a.startswith('--')]
    log, dis = av[0], (av[1] if len(av) > 1 else '/tmp/s7419_canon.dis')
    census = {}
    out = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7393_createmq_census.py'), dis],
                         capture_output=True, text=True).stdout
    for ln in out.splitlines():
        p = ln.split('\t')
        if len(p) >= 6 and re.match(r'^[0-9A-F]{8}$', p[0]):
            census.setdefault(p[1].strip(), set()).add(p[6].replace('post=', '') if len(p) > 6 else '-')
    blocks, cur, ctl, ev = [], None, False, []
    for ln in open(log, errors='replace'):
        if ln.startswith('[s7393-cq-begin]'):
            if cur is not None:
                blocks.append(cur)
            cur = []
        elif cur is not None and ln.startswith('[s7393-cq]'):
            m = ROW.match(ln)
            if m:
                cur.append(m.groups())
        elif ln.startswith('[s7393-ctl]'):
            ctl = True
        elif ln.startswith('[s7393-ev]'):
            ev.append(ln.strip())
    if cur:
        blocks.append(cur)
    if not blocks:
        print('NO-TABLE'); sys.exit(2)
    rows = blocks[-1]
    print('TABLE rows=%d blocks=%d ev_rows=%d' % (len(rows), len(blocks), len(ev)))
    rc, cpass = 0, None
    for r in rows:
        mq, key, gra, cnt, cr, re_, lost, orr, ors, rr, rs, held = r
        fn = re.sub(r'(_s\d+_inner)?\+0x[0-9a-f]+$', '', key)  # host key -> guest function (s7325-style wrappers folded)
        reseed = census.get(fn) == {'SEND'} and cnt == '1'
        # a lost token on a count-1 queue whose creator re-posts at once is a mutex re-seed, not a loss
        live = (0 if reseed else int(lost)) + int(orr) + int(ors)
        tag = 'CTRL' if key == 'CONTROL' else ('LIVE' if live else ('SEED' if reseed and int(lost) else ('RE  ' if int(re_) else '    ')))
        if key == 'CONTROL':
            cpass = (int(lost) == 1 and int(orr) == 1 and int(ors) == 0 and int(re_) == 1)
        elif live:
            rc = 3
        print('%s mq=%s %-40s cnt=%s creates=%s re=%s lost=%s orphan_r=%s orphan_s=%s raw_r=%s raw_s=%s held=%s' % (
            tag, mq, key[:40], cnt, cr, re_, lost, orr, ors, rr, rs, held))
    for e in ev[:20]:
        print(e)
    if ctl:
        print('CONTROL %s' % ('PASS' if cpass else 'FAIL'))
        if not cpass:
            rc = 2
    print('VERDICT %s' % ('H-none' if rc == 0 else ('H-orphan' if rc == 3 else 'CONTROL-FAIL')))
    sys.exit(rc)


if __name__ == '__main__':
    main()
