#!/usr/bin/env python3
"""s7393 class BC: static census of every guest osCreateMesgQueue call site (re-create of a LIVE queue).

Usage: tools/s7393_createmq_census.py [disasm=/tmp/s7419_canon.dis]
  (default built by tools/s7419_canon_dis.py)

Per site: caller function, mq (a0), msg buffer (a1), count (a2) resolved by tools/s7392_mesg_census.py's resolver, and the
number of static jal sites that reach the caller (callers=N; 0 = reached only indirectly / entry). A caller with callers>1,
or one sitting in a loop / a re-init path, can run more than once, so its queue may be live at the re-create; whether it IS
live is the runtime half. post=SEND = the caller posts to the same queue right after (a count-1 mutex re-seeded with
its token: a pending token the re-create discards is replaced at once, so validCount is unchanged) (ROGUESQ_S7393_CQ=1, tools/s7393_cq_report.py).
"""
import re, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
c7392 = importlib.import_module('s7392_mesg_census')


def a0_src(insns, i, lo):
    # the instruction that last set a0 before call i (delay slot first), scanning back to index lo
    for k in [i + 1] + list(range(i - 1, lo - 1, -1)):
        if c7392.dest_of(insns[k][1], insns[k][2]) == 'a0':
            return k
    return None


def same_sreg(insns, i, j):
    # create's a0 and send's a0 both copied from the same callee-saved s-register, unwritten in between (survives the jal)
    ka, kb = a0_src(insns, i, max(0, i - 30)), a0_src(insns, j, i + 2)
    if ka is None or kb is None or insns[ka][1] != 'move' or insns[kb][1] != 'move':
        return False
    r = insns[ka][2][1]
    if r != insns[kb][2][1] or not re.match(r'^s[0-8]$', r):
        return False
    return all(c7392.dest_of(insns[k][1], insns[k][2]) != r for k in range(ka + 1, kb))


def main():
    dis = sys.argv[1] if len(sys.argv) > 1 else c7392.DIS
    insns = c7392.parse(dis)
    start = {}
    for a, mn, ops, fn in insns:
        start.setdefault(fn, a)
    jal_to = collections.Counter()
    for a, mn, ops, fn in insns:
        if mn == 'jal' and ops:
            t = re.search(r'<([^>+]+)>', ops[0])
            if t:
                jal_to[t.group(1)] += 1
    n = 0
    for i, (a, mn, ops, fn) in enumerate(insns):
        if mn != 'jal' or not ops or '<osCreateMesgQueue>' not in ops[0]:
            continue
        n += 1
        mq, buf, cnt = (c7392.fmt(c7392.resolve(insns, i, r)) for r in ('a0', 'a1', 'a2'))
        post = '-'
        for j in range(i + 2, min(i + 10, len(insns))):
            if insns[j][3] != fn:
                break
            if insns[j][1] == 'jal' and insns[j][2]:
                if '<osSendMesg>' in insns[j][2][0] and (c7392.fmt(c7392.resolve(insns, j, 'a0')) == mq
                                                          or same_sreg(insns, i, j)):
                    post = 'SEND'
                break
        print('%08X\t%-34s\tmq=%s\tmsg=%s\tcount=%s\tcallers=%d\tpost=%s' % (a, fn[:34], mq, buf, cnt, jal_to[fn], post))
    print('SUMMARY sites=%d' % n)


if __name__ == '__main__':
    main()
