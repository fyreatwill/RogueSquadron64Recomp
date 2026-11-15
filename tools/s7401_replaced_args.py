#!/usr/bin/env python3
"""s7401 class BK: replaced-libultra INPUT/argument contract census.
For every live guest jal to a replaced libultra function with a special-value contract, resolve the guest arg value
(tools/s7399 val(): backward scan, one caller level when the value is a pass-through argument) and classify it against
(a) what retail libultra does with that value and (b) what the port's replacement does with it.
  OK       value handled identically
  H-arg    the guest passes a value the replacement mishandles (rc 1)
  H-ignored  the guest passes a value libultra honours but the replacement drops (rc 1)
  INERT    libultra honours it but no host event source exists (PRENMI)
  DEAD-caller  site in a libultra internal whose only callers/address refs are replaced bodies
  UNRES    value not static (listed; decided by the runtime arm ROGUESQ_S7401_ARGS)
Usage: tools/s7401_replaced_args.py [disasm=/tmp/s7392.dis] [--rows]"""
import re, sys, os, importlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
c7392 = importlib.import_module('s7392_mesg_census')
c7399 = importlib.import_module('s7399_evpayload_census')
c7400 = importlib.import_module('s7400_replaced_contract')
AREG = {0: 'a0', 1: 'a1', 2: 'a2', 3: 'a3'}

# retail libultra: osRecvMesg/osSendMesg/osJamMesg block for ANY flags != OS_MESG_NOBLOCK(0); the port blocks only on ==1.
def k_flags(v):
    if v in (0, 1): return 'OK'
    return 'H-arg' if isinstance(v, int) else 'UNRES'
# port osSetEventMesg (ultramodern events.cpp) stores only SP(4) SI(5) AI(6) DP(9); retail stores every event id
def k_event(v):
    if not isinstance(v, int): return 'UNRES'
    if v == 14: return 'INERT'   # PRENMI: no host reset source exists, retail and port both never deliver it
    return 'OK' if v in (4, 5, 6, 9) else 'H-ignored'
def k_v2p(v):   # port: KSEG0/KSEG1 masked, anything else returned as-is (no TLB walk)
    if not isinstance(v, int): return 'UNRES'
    return 'OK' if 0x80000000 <= v < 0xC0000000 else 'H-arg'
def k_pri(v):
    if not isinstance(v, int): return 'UNRES'
    return 'OK' if 0 <= v <= 255 else 'H-arg'
def k_nonnull(v):
    if not isinstance(v, int): return 'UNRES'
    return 'OK' if v else 'H-arg'
def k_any(v): return 'OK' if isinstance(v, int) else 'UNRES'

SPEC = {
    'osRecvMesg': [(2, 'flags', k_flags)], 'osSendMesg': [(2, 'flags', k_flags)], 'osJamMesg': [(2, 'flags', k_flags)],
    'osSetEventMesg': [(0, 'event', k_event)], 'osVirtualToPhysical': [(0, 'vaddr', k_v2p)],
    'osSetThreadPri': [(1, 'pri', k_pri)], 'osStartThread': [(0, 'thread', k_nonnull)],
    'osDestroyThread': [(0, 'thread', k_any)], 'osStopThread': [(0, 'thread', k_any)],
    'osViSetEvent': [(2, 'retrace', k_any)], 'osViSetSpecialFeatures': [(0, 'feat', k_any)],
    'osPiStartDma': [(2, 'dir', k_any)], 'osSetTimer': [(2, 'cnt_hi', k_any), (3, 'cnt_lo', k_any)],
}


def callers(insns, fn):
    return [i for i, (a, mn, ops, f) in enumerate(insns) if mn == 'jal' and ops and ('<%s>' % fn) in ops[0]]


def value(insns, i, reg, depth=0):
    a, mn, ops, f = insns[i + 1]
    if mn == 'andi' and ops[0] == reg and int(ops[2], 0) == 0xff:
        return [0, 255]   # masked to a byte: bounds only
    if mn == 'move' and ops and ops[0] == reg and ops[1] != reg:   # delay-slot copy: resolve the source before the jal
        return value(insns, i, ops[1], depth) if ops[1] != 'zero' else 0
    v = c7399.val(insns, i, reg)
    if isinstance(v, str) and v.startswith('arg:') and depth < 2:
        outs = [value(insns, j, v[4:], depth + 1) for j in callers(insns, insns[i][3])]
        if outs and all(isinstance(o, int) for o in outs):
            return sorted(set(outs))
        return v + ('(callers %d)' % len(outs))
    return v


def addr_refs(insns, fn):
    """functions that materialise fn's address with lui+addiu (pointer-called thread entries, callbacks)"""
    ent = [a for a, mn, ops, f in insns if f == fn]
    if not ent:
        return []
    e = ent[0]; hi = ((e + 0x8000) >> 16) & 0xFFFF; lo = e & 0xFFFF
    out = []
    for k, (a, mn, ops, f) in enumerate(insns):
        if mn == 'addiu' and len(ops) == 3 and (int(ops[2], 0) & 0xFFFF) == lo:
            for j in range(max(0, k - 12), k):
                if insns[j][1] == 'lui' and insns[j][2][0] == ops[1] and int(insns[j][2][1], 0) == hi:
                    out.append(f); break
    return out


def live(insns, fn, allb, seen=()):
    """False when every caller of fn is a replaced body (never runs) or itself dead; functions with no jal callers
    (thread entries, pointer-called) count as live."""
    cs = [insns[j][3] for j in callers(insns, fn)]
    if not cs:
        refs = addr_refs(insns, fn)   # conservative: no found ref = live; dead only if every ref sits in a replaced body
        return not refs or any(r not in allb for r in refs)
    return any(c not in allb and c not in seen and live(insns, c, allb, seen + (fn,)) for c in cs)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    insns = c7392.parse(args[0] if args else c7392.DIS)
    allb = c7400.bodies()
    bad, tally = 0, collections.Counter()
    for fn, specs in SPEC.items():
        for i in callers(insns, fn):
            if insns[i][3] in allb:
                continue
            if not live(insns, insns[i][3], allb):
                tally[(fn, '-', 'DEAD-caller')] += 1
                continue
            for n, nm, k in specs:
                v = value(insns, i, AREG[n])
                vs = v if isinstance(v, list) else [v]
                cls = sorted(set(k(x) for x in vs))
                c = 'H-arg' if 'H-arg' in cls else 'H-ignored' if 'H-ignored' in cls else 'UNRES' if 'UNRES' in cls else 'INERT' if 'INERT' in cls else 'OK'
                tally[(fn, nm, c)] += 1
                bad += c in ('H-arg', 'H-ignored')
                if c != 'OK' or '--rows' in sys.argv:
                    sv = ','.join(c7399.fmt(x) for x in vs)
                    print('%-8s %-20s %-7s %08X %-36s %s' % (c, fn, nm, insns[i][0], insns[i][3], sv))
    print('---')
    for (fn, nm, c), n in sorted(tally.items()):
        print('%-22s %-8s %-9s %d' % (fn, nm, c, n))
    print('--- deviations=%d' % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
