#!/usr/bin/env python3
"""s7392 class BB report: last complete [s7392-mq] table of a ROGUESQ_S7392_MQ=1 run, joined with the static census
(tools/s7392_mesg_census.py) by call site (ra - 8).

usage: tools/s7392_mq_report.py <run.log> [disasm=/tmp/s7392.dis] [--known]  (--known: classified families -> KNWN, not DROP)
exit 0 = control PASS (or not armed) and no failing non-control row; 2 = control armed but FAILED;
     3 = a guest send failed / an external message was dropped outside the control (the rows marked DROP).
"""
import re, sys, bisect, subprocess, os

# s7392 classified drop families (tools/s7392_mesg_reviewed.tsv + PORTING-STATE s7392): with --known these do not count.
KNOWN = {('E', '80114388'), ('E', '80149670'), ('S', '8010FEE0'), ('S', '8011A800'), ('S', '80128CF0')}
SRC = {-1: 'host-thread', 0: 'Timer', 1: 'Sp', 2: 'Si', 3: 'Ai', 4: 'Vi', 5: 'Pi', 6: 'Dp'}
ROW = re.compile(r'^\[s7392-mq\] t=([\d.]+) kind=(\w) mq=(\w+) key=(\S+) flags=(-?\d+) calls=(\d+) fails=(\d+) rq=(\d+) hiv=(-?\d+) cnt=(-?\d+) tff=(-?[\d.]+)')


def funcs(dis):
    st, nm = [], []
    for ln in open(dis):
        m = re.match(r'^([0-9a-f]{8}) <([^>]+)>:$', ln)
        if m:
            st.append(int(m.group(1), 16)); nm.append(m.group(2))
    return st, nm


def main():
    av = [a for a in sys.argv[1:] if not a.startswith('--')]
    log = av[0]
    dis = av[1] if len(av) > 1 else '/tmp/s7392.dis'
    census = {}
    try:
        out = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7392_mesg_census.py'), dis],
                             capture_output=True, text=True).stdout
        for ln in out.splitlines():
            p = ln.split('\t')
            if len(p) >= 6 and re.match(r'^[0-9A-F]{8}$', p[0]):
                census[int(p[0], 16)] = (p[4].replace('flags=', ''), p[5].replace('v0=', ''), p[3].replace('mq=', ''), p[1].strip())
    except Exception:
        pass
    blocks, cur, ctl = [], None, None
    for ln in open(log, errors='replace'):
        if ln.startswith('[s7392-mq-begin]'):
            if cur is not None:
                blocks.append(cur)
            cur = []
        elif cur is not None and ln.startswith('[s7392-mq]'):
            m = ROW.match(ln)
            if m:
                cur.append(m.groups())
        elif ln.startswith('[s7392-ctl]'):
            ctl = ln.strip()
    if cur:
        blocks.append(cur)
    if not blocks:
        print('NO-TABLE'); sys.exit(2)
    rows = blocks[-1]
    print('TABLE t=%s rows=%d blocks=%d' % (rows[0][0] if rows else '?', len(rows), len(blocks)))
    ctl_q = None
    if ctl:
        print(ctl)
        ctl_q = re.search(r'q=(\w+)', ctl).group(1)
    ctl_s = ctl_e = False
    drops = 0
    out = []
    for t, kind, mq, key, flags, calls, fails, rq, hiv, cnt, tff in rows:
        calls, fails, rq, hiv, cnt = int(calls), int(fails), int(rq), int(hiv), int(cnt)
        if kind == 'E':
            src = int(key[3:])
            who = 'ext:' + SRC.get(src, str(src))
            site = ''
        else:
            who = key
            fn = key.split('+')[0]
            cs = [(a, c) for a, c in census.items() if c[3] == fn and c[2] == mq]
            cs = cs or [(a, c) for a, c in census.items() if c[3] == fn]
            site = ' '.join('site=%08X/fl=%s/v0=%s' % (a, c[0], c[1]) for a, c in sorted(cs)) or '(no census row)'
        isctl = mq == ctl_q
        if isctl and kind == 'S' and calls == 2 and fails == 1:
            ctl_s = True
        if isctl and kind == 'E' and fails >= 1:
            ctl_e = True
        tag = ''
        if fails and not isctl:
            if '--known' in sys.argv and (kind, mq) in KNOWN:
                tag = 'KNWN'
            else:
                tag = 'DROP'; drops += 1
        out.append((tag == 'DROP', '%-4s %s mq=%s %-40s flags=%s calls=%d fails=%d rq=%d hiwater=%d/%d tff=%s %s' % (
            tag, kind, mq, who[:40], flags, calls, fails, rq, hiv, cnt, tff, site)))
    for _, s in sorted(out, key=lambda x: (not x[0], x[1])):
        print(s)
    armed = ctl is not None
    print('CONTROL %s (guest=%d ext=%d)' % (('PASS' if (ctl_s and ctl_e) else 'FAIL') if armed else 'not-armed', ctl_s, ctl_e))
    print('VERDICT %s drops=%d' % ('H-none-on-route' if drops == 0 else 'drops-present', drops))
    if armed and not (ctl_s and ctl_e):
        sys.exit(2)
    sys.exit(3 if drops else 0)


if __name__ == '__main__':
    main()
