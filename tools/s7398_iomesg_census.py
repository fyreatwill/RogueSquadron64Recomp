#!/usr/bin/env python3
"""s7398 class BH: static census of guest PI/SI I/O-message start sites (osPiStartDma / osEPiStartDma / osPiRawStartDma /
osEPiRawStartDma / osPiRawReadIo / osPiReadIo / osEPiReadIo / osContStartReadData). Per site: caller fn, REPLACED when
librecomp defines <caller>_recomp (guest body never runs), callee REPLACED (librecomp owns the start), the OSIoMesg (a0
for osPiStartDma, a1 for osEPi*), completion mq (24(sp) / a0 for SI), the NEXT osRecvMesg in the same function
(mq, msg slot, flag) and whether the received msg slot is ever loaded back (msg-consumed), IN-LOOP, callers=N.
Usage: tools/s7398_iomesg_census.py [disasm=/tmp/s7392.dis]"""
import re, sys, os, collections, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
c7392 = importlib.import_module('s7392_mesg_census')
c7395 = importlib.import_module('s7395_event_census')
c7397 = importlib.import_module('s7397_timer_census')
FN = ('osPiStartDma', 'osEPiStartDma', 'osPiRawStartDma', 'osEPiRawStartDma', 'osPiRawReadIo', 'osPiReadIo',
      'osEPiReadIo', 'osContStartReadData')


def next_recv(insns, i, fn):
    for j in range(i + 2, min(i + 400, len(insns))):
        a, mn, ops, f = insns[j]
        if f != fn:
            break
        if mn == 'jal' and ops and '<osRecvMesg>' in ops[0]:
            slot = c7392.fmt(c7392.resolve(insns, j, 'a1'))
            consumed = 'n/a'
            m = re.match(r'sp\+0x([0-9a-f]+)|sp\+(\d+)', slot.lower()) if isinstance(slot, str) else None
            if slot != 'zero':
                consumed = 'no'
                for k in range(j + 2, min(j + 200, len(insns))):
                    if insns[k][3] != fn:
                        break
                    if insns[k][1] in ('lw', 'ld') and m and len(insns[k][2]) == 2:
                        off = int(m.group(1), 16) if m.group(1) else int(m.group(2))
                        if insns[k][2][1] == '%d(sp)' % off:
                            consumed = 'yes@%08X' % insns[k][0]
                            break
            return 'recv@%08X mq=%s slot=%s flag=%s consumed=%s' % (a, c7392.fmt(c7392.resolve(insns, j, 'a0')), slot,
                                                                   c7392.fmt(c7392.resolve(insns, j, 'a2')), consumed)
    return 'recv=none-in-fn'


def main():
    dis = sys.argv[1] if len(sys.argv) > 1 else c7392.DIS
    insns = c7392.parse(dis)
    rep = c7397.replaced()
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
        if call == 'osPiStartDma':
            arg = 'mb=%s dir=%s dev=%s dram=%s size=%s mq=%s' % (c7392.fmt(c7392.resolve(insns, i, 'a0')), c7392.fmt(c7392.resolve(insns, i, 'a2')),
                  c7392.fmt(c7392.resolve(insns, i, 'a3')), c7397.stack_store(insns, i, 16), c7397.stack_store(insns, i, 20), c7397.stack_store(insns, i, 24))
        elif call.startswith('osEPi'):
            arg = 'h=%s mb/dev=%s a2=%s' % (c7392.fmt(c7392.resolve(insns, i, 'a0')), c7392.fmt(c7392.resolve(insns, i, 'a1')), c7392.fmt(c7392.resolve(insns, i, 'a2')))
        elif call == 'osContStartReadData':
            arg = 'mq=%s' % c7392.fmt(c7392.resolve(insns, i, 'a0'))
        else:
            arg = 'a0=%s a1=%s' % (c7392.fmt(c7392.resolve(insns, i, 'a0')), c7392.fmt(c7392.resolve(insns, i, 'a1')))
        r = fn in rep
        live += not r
        per[call] += 1
        print('%08X %-19s %-26s callee=%-8s %-70s %s callers=%d %-8s %s' % (a, call, fn, 'REPLACED' if call in rep else 'GUEST', arg,
              next_recv(insns, i, fn), jal_to[fn], 'IN-LOOP' if c7395.in_loop(insns, i, fn) else 'straight', 'REPLACED' if r else 'LIVE'))
    print('--- per call:', dict(per), 'live_sites=%d' % live)


if __name__ == '__main__':
    main()
