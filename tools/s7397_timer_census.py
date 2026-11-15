#!/usr/bin/env python3
"""s7397 class BG: static census of guest timer call sites (osSetTimer / osStopTimer). Per site: caller fn, OSTimer (a0),
countdown (a2:a3), interval (16/20(sp)), mq (24(sp)), msg (28(sp)), callers=N, IN-LOOP, and REPLACED when librecomp defines
<caller>_recomp (that guest body never runs). Runtime half: ROGUESQ_S7397_TM=1 [+ _CTL=1], tools/s7397_timer_report.py.
Usage: tools/s7397_timer_census.py [disasm=/tmp/s7392.dis]"""
import re, sys, os, glob, collections, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
c7392 = importlib.import_module('s7392_mesg_census')
c7395 = importlib.import_module('s7395_event_census')
FN = ('osSetTimer', 'osStopTimer')
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def replaced():
    out = set()
    for f in glob.glob(os.path.join(ROOT, 'lib/N64ModernRuntime/librecomp/src/*.cpp')):
        out |= set(re.findall(r'void\s+(\w+)_recomp\s*\(', open(f, errors='replace').read()))
    return out


def stack_store(insns, i, off):
    """last 'sw reg,off(sp)' before the jal (or in its delay slot) -> resolved reg value"""
    for j in (i + 1,) + tuple(range(i - 1, max(i - 40, -1), -1)):
        a, mn, ops, fn = insns[j]
        if mn == 'sw' and len(ops) == 2 and ops[1] == '%d(sp)' % off:
            return 'zero' if ops[0] == 'zero' else c7392.fmt(c7392.resolve(insns, j, ops[0]))
    return '?'


def main():
    dis = sys.argv[1] if len(sys.argv) > 1 else c7392.DIS
    insns = c7392.parse(dis)
    rep = replaced()
    jal_to = collections.Counter()
    for a, mn, ops, fn in insns:
        if mn == 'jal' and ops:
            t = re.search(r'<([^>+]+)>', ops[0])
            if t:
                jal_to[t.group(1)] += 1
    per = collections.Counter(); live = 0
    for i, (a, mn, ops, fn) in enumerate(insns):
        if mn != 'jal' or not ops:
            continue
        m = re.search(r'<(%s)>' % '|'.join(FN), ops[0])
        if not m:
            continue
        call = m.group(1)
        a0 = c7392.fmt(c7392.resolve(insns, i, 'a0'))
        extra = ''
        if call == 'osSetTimer':
            extra = 'cd=%s:%s iv=%s:%s mq=%s msg=%s' % (c7392.fmt(c7392.resolve(insns, i, 'a2')), c7392.fmt(c7392.resolve(insns, i, 'a3')),
                                                    stack_store(insns, i, 16), stack_store(insns, i, 20), stack_store(insns, i, 24), stack_store(insns, i, 28))
        r = fn in rep
        live += not r
        per[call] += 1
        print('%08X %-11s %-24s t=%-12s %-60s callers=%d %-8s %s' % (a, call, fn, a0, extra, jal_to[fn],
              'IN-LOOP' if c7395.in_loop(insns, i, fn) else 'straight', 'REPLACED' if r else 'LIVE'))
    print('--- per call:', dict(per), 'live_sites=%d' % live)


if __name__ == '__main__':
    main()
