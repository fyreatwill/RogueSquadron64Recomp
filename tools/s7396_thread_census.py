#!/usr/bin/env python3
"""s7396 class BF: static census of guest thread-lifecycle call sites (osCreateThread/osStartThread/osStopThread/
osDestroyThread/osSetThreadPri). Per site: caller fn, target thread (a0; 0 = self), extra arg (pri / entry),
callers=N, IN-LOOP. A non-self stop/destroy/setpri reaches ultramodern::thread_queue_remove, whose pre-s7396 walk
never advanced past the queue head (non-head target in a >=2 queue = infinite loop). Runtime half:
ROGUESQ_S7396_TQ=1 [+ _CTL=1], tools/s7396_tq_report.py.
Usage: tools/s7396_thread_census.py [disasm=/tmp/s7392.dis]"""
import re, sys, os, collections, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
c7392 = importlib.import_module('s7392_mesg_census')
c7395 = importlib.import_module('s7395_event_census')
FN = ('osCreateThread', 'osStartThread', 'osStopThread', 'osDestroyThread', 'osSetThreadPri')


def main():
    dis = sys.argv[1] if len(sys.argv) > 1 else c7392.DIS
    insns = c7392.parse(dis)
    jal_to = collections.Counter()
    for a, mn, ops, fn in insns:
        if mn == 'jal' and ops:
            t = re.search(r'<([^>+]+)>', ops[0])
            if t:
                jal_to[t.group(1)] += 1
    per = collections.Counter(); nonself = 0
    for i, (a, mn, ops, fn) in enumerate(insns):
        if mn != 'jal' or not ops:
            continue
        m = re.search(r'<(%s)>' % '|'.join(FN), ops[0])
        if not m:
            continue
        call = m.group(1)
        a0 = c7392.fmt(c7392.resolve(insns, i, 'a0'))
        extra = ''
        if call == 'osSetThreadPri':
            extra = 'pri=%s' % c7392.fmt(c7392.resolve(insns, i, 'a1'))
        elif call == 'osCreateThread':
            extra = 'id=%s entry=%s pri=%s' % (c7392.fmt(c7392.resolve(insns, i, 'a1')),
                                               c7392.fmt(c7392.resolve(insns, i, 'a2')), 'stack')
        selfc = a0 in ('0', '0x0', '00000000', 'zero') or a0 == '0'
        tgt = 'SELF' if selfc else 'other'
        if call in ('osStopThread', 'osDestroyThread', 'osSetThreadPri') and not selfc:
            nonself += 1
        per[call] += 1
        print('%08X %-15s %-28s a0=%-12s %-5s %-40s callers=%d %s' % (a, call, fn, a0, tgt, extra, jal_to[fn],
              'IN-LOOP' if c7395.in_loop(insns, i, fn) else 'straight'))
    print('--- per call:', dict(per))
    print('nonself_stop_destroy_setpri=%d (each reaches thread_queue_remove when the target is not STOPPED)' % nonself)


if __name__ == '__main__':
    main()
