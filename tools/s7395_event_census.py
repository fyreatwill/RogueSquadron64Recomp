#!/usr/bin/env python3
"""s7395 class BE: static census of every guest osSetEventMesg / osViSetEvent call site (event re-binding).

Usage: tools/s7395_event_census.py [disasm=/tmp/s7392.dis]
Per site: caller fn, event (a0 for osSetEventMesg), queue, message, callers=N (static jal sites reaching the caller).
An event bound by >1 site, or by a caller with callers>1, can be RE-BOUND; whether a re-bind strands a waiter on the
old queue is the runtime half (ROGUESQ_S7395_EV=1, tools/s7395_ev_report.py).
"""
import re, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
c7392 = importlib.import_module('s7392_mesg_census')
EV = {0: 'SW1', 1: 'SW2', 2: 'CART', 3: 'COUNTER', 4: 'SP', 5: 'SI', 6: 'AI', 7: 'VI', 8: 'PI', 9: 'DP',
      10: 'CPU_BREAK', 11: 'SP_BREAK', 12: 'FAULT', 13: 'THREADSTATUS', 14: 'PRENMI'}


def in_loop(insns, i, fn):
    # a backward branch later in fn whose target is at or before the call site = the call can repeat in one activation
    site = insns[i][0]
    for a, mn, ops, f in insns[i + 1:]:
        if f != fn:
            break
        if (mn.startswith('b') or mn == 'j') and ops:
            m = re.search(r'\b([0-9a-f]{8})\b', ops[-1])
            if m and int(m.group(1), 16) <= site and int(m.group(1), 16) >= insns[0][0]:
                tgt = int(m.group(1), 16)
                # target must lie inside fn
                if any(x[0] == tgt and x[3] == fn for x in insns[max(0, i - 4000):i + 1]):
                    return True
    return False


def main():
    dis = sys.argv[1] if len(sys.argv) > 1 else c7392.DIS
    insns = c7392.parse(dis)
    jal_to = collections.Counter()
    for a, mn, ops, fn in insns:
        if mn == 'jal' and ops:
            t = re.search(r'<([^>+]+)>', ops[0])
            if t:
                jal_to[t.group(1)] += 1
    per_ev = collections.defaultdict(list)
    for i, (a, mn, ops, fn) in enumerate(insns):
        if mn != 'jal' or not ops or not re.search(r'<(osSetEventMesg|osViSetEvent)>', ops[0]):
            continue
        vi = 'osViSetEvent' in ops[0]
        if vi:
            mq, msg, rc = (c7392.fmt(c7392.resolve(insns, i, r)) for r in ('a0', 'a1', 'a2'))
            ev = 'VI'
            extra = 'retrace=%s' % rc
        else:
            evr = c7392.resolve(insns, i, 'a0')
            mq, msg = (c7392.fmt(c7392.resolve(insns, i, r)) for r in ('a1', 'a2'))
            try:
                ev = EV.get(int(c7392.fmt(evr), 16), c7392.fmt(evr))
            except (ValueError, TypeError):
                ev = c7392.fmt(evr)
            extra = ''
        per_ev[ev].append(fn)
        loop = in_loop(insns, i, fn)
        print('%08X %-24s ev=%-8s mq=%-10s msg=%-10s %s callers=%d %s' % (a, fn, ev, mq, msg, extra, jal_to[fn],
              'IN-LOOP' if loop else 'straight'))
    print('--- per event: binding sites')
    for ev, fns in sorted(per_ev.items()):
        print('  %-8s sites=%d fns=%s%s' % (ev, len(fns), ','.join(fns),
              '  RE-BIND-CAPABLE' if len(fns) > 1 or any(jal_to[f] > 1 for f in fns) else ''))
    print('sites=%d' % sum(len(v) for v in per_ev.values()))


if __name__ == '__main__':
    main()
