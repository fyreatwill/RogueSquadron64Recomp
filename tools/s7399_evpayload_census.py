#!/usr/bin/env python3
"""s7399 class BI: event-message payload census.

For every hardware-event binding (osSetEventMesg / osViSetEvent, live guest sites) resolve the bound (mq, msg), then for
EVERY guest osRecvMesg site whose mq is one of those queues (same constant, or same callee-saved register in the binder
function) classify what the consumer does with the received message:
  DISCARD  slot is zero / never loaded back
  CMP      loaded msg compared (beq/bne) against a constant or register -> value-dispatch: sender must pass the exact msg
  DEREF    loaded msg used as a pointer (load off(reg)) -> type-byte dispatch: sender must pass the bound pointer
  PASS     loaded msg handed to a call / stored
The sender side (ultramodern events.cpp / timer.cpp / pi.cpp) is checked textually: every enqueue for an event source
must pass the stored bound msg (events_context.X.msg / cur_state->msg), never a literal.
Usage: tools/s7399_evpayload_census.py [disasm=/tmp/s7392.dis] [--check]  (rc 1 on a CMP/DEREF consumer whose sender
does not pass the bound msg, or on an unresolved bound mq)."""
import re, sys, os, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
c7392 = importlib.import_module('s7392_mesg_census')
c7397 = importlib.import_module('s7397_timer_census')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVED = {'s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 'fp', 'sp', 'gp'}
EV = {4: 'SP', 5: 'SI', 6: 'AI', 7: 'VI', 8: 'PI', 9: 'DP', 14: 'PRENMI', 3: 'COUNTER'}


def val(insns, i, reg, depth=0):
    """backward scan; crosses jal for callee-saved regs; handles li/lui/addiu/ori/move. Returns int, 'arg:REG' or '?'"""
    if reg == 'zero':
        return 0
    fn = insns[i][3]
    hi = None
    for k in [i + 1] + list(range(i - 1, max(-1, i - 200), -1)):
        a, mn, ops, f = insns[k]
        if f != fn:
            return 'arg:' + reg if reg in ('a0', 'a1', 'a2', 'a3') else ('entry:' + reg if reg in SAVED else '?')
        if k < i and mn in ('jal', 'jalr') and reg not in SAVED:
            return '?'
        d = c7392.dest_of(mn, ops)
        if d != reg:
            continue
        if mn == 'li':
            return int(ops[1], 0) & 0xFFFFFFFF
        if mn == 'lui':
            return (int(ops[1], 0) << 16) & 0xFFFFFFFF
        if mn == 'move':
            return val(insns, k, ops[1], depth + 1) if depth < 6 else '?'
        if mn in ('addiu', 'ori') and len(ops) == 3:
            b = val(insns, k, ops[1], depth + 1) if depth < 6 else '?'
            if isinstance(b, int):
                imm = int(ops[2], 0)
                return ((b + imm) if mn == 'addiu' else (b | (imm & 0xFFFF))) & 0xFFFFFFFF
            return '?'
        return '?:%s@%08X' % (mn, a)
    return '?'


def fmt(v):
    return '%08X' % v if isinstance(v, int) else str(v)


def reg_before(insns, i, reg):
    """the source register name feeding reg at call i (follow one 'move')"""
    for k in [i + 1] + list(range(i - 1, max(-1, i - 40), -1)):
        a, mn, ops, f = insns[k]
        if f != insns[i][3]:
            break
        if c7392.dest_of(mn, ops) == reg:
            return ops[1] if mn == 'move' else reg
    return reg


def use_of(insns, j, fn, slot_off):
    """after recv at j: find lw of slot, then the first use of the loaded reg"""
    for k in range(j + 2, min(j + 300, len(insns))):
        a, mn, ops, f = insns[k]
        if f != fn:
            return 'DISCARD', 'fn-end'
        if mn in ('lw', 'ld', 'lbu', 'lhu') and len(ops) == 2 and ops[1] == '%d(sp)' % slot_off:
            r = ops[0]
            for q in range(k + 1, min(k + 80, len(insns))):
                a2, mn2, ops2, f2 = insns[q]
                if f2 != fn:
                    break
                srcs = ops2[1:] if c7392.dest_of(mn2, ops2) else ops2
                hit = [o for o in srcs if re.search(r'\b%s\b' % r, o)]
                if hit:
                    if mn2 in ('beq', 'bne', 'beql', 'bnel', 'slt', 'sltu', 'slti', 'sltiu', 'xor', 'xori', 'subu'):
                        other = [o for o in ops2[:2] if o != r]
                        ov = fmt(val(insns, q, other[0])) if other and other[0] not in ('zero',) else ('0' if other else '?')
                        return 'CMP', '%s@%08X vs %s' % (mn2, a2, ov)
                    if re.search(r'\(%s\)' % r, ' '.join(srcs)) and mn2.startswith('l'):
                        return 'DEREF', '%s %s @%08X' % (mn2, ','.join(ops2), a2)
                    if mn2.startswith('s') and re.search(r'\(%s\)' % r, ' '.join(srcs)):
                        return 'DEREF', 'store-through %s @%08X' % (','.join(ops2), a2)
                    if mn2 == 'jalr':
                        return 'DEREF', 'jalr @%08X' % a2
                    return 'PASS', '%s %s @%08X' % (mn2, ','.join(ops2), a2)
                if c7392.dest_of(mn2, ops2) == r:
                    return 'DISCARD', 'reg overwritten @%08X' % a2
            return 'DISCARD', 'loaded@%08X unused' % a
    return 'DISCARD', 'never loaded'


def recv_sites(insns):
    for j, (a, mn, ops, fn) in enumerate(insns):
        if mn == 'jal' and ops and '<osRecvMesg>' in ops[0]:
            yield j


def senders():
    out = []
    for rel in ('lib/N64ModernRuntime/ultramodern/src/events.cpp', 'lib/N64ModernRuntime/ultramodern/src/timer.cpp',
                'lib/N64ModernRuntime/ultramodern/src/extensions.cpp', 'lib/N64ModernRuntime/librecomp/src/pi.cpp'):
        for n, ln in enumerate(open(os.path.join(ROOT, rel), errors='replace'), 1):
            m = re.search(r'enqueue_external_message_src\(\s*([^,]+),\s*([^,]+),\s*(\w+),\s*ultramodern::EventMessageSource::(\w+)', ln)
            if m:
                out.append((rel.split('/')[-1], n, m.group(4), m.group(1).strip(), m.group(2).strip(), m.group(3)))
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    check = '--check' in sys.argv
    insns = c7392.parse(args[0] if args else c7392.DIS)
    rep = c7397.replaced()
    bind = []
    for i, (a, mn, ops, fn) in enumerate(insns):
        if mn != 'jal' or not ops or not re.search(r'<(osSetEventMesg|osViSetEvent)>', ops[0]):
            continue
        if 'osViSetEvent' in ops[0]:
            ev, mqr, msr = 'VI', 'a0', 'a1'
        else:
            e = val(insns, i, 'a0'); ev = EV.get(e, fmt(e)) if isinstance(e, int) else fmt(e); mqr, msr = 'a1', 'a2'
        bind.append(dict(site=a, fn=fn, ev=ev, mq=val(insns, i, mqr), mqreg=reg_before(insns, i, mqr), msg=val(insns, i, msr),
                         live=fn not in rep))
    bad = 0
    print('== bindings (live guest sites; REPLACED callers never run)')
    for b in bind:
        print('%08X %-24s ev=%-7s mq=%-10s (reg %s) msg=%-10s %s' % (b['site'], b['fn'], b['ev'], fmt(b['mq']), b['mqreg'],
              fmt(b['msg']), 'LIVE' if b['live'] else 'REPLACED'))
    print('== consumers (osRecvMesg on a bound queue)')
    rows = []
    for j in recv_sites(insns):
        a, mn, ops, fn = insns[j]
        mq = val(insns, j, 'a0'); mqreg = reg_before(insns, j, 'a0')
        for b in bind:
            if not b['live']:
                continue
            same = (isinstance(mq, int) and mq == b['mq']) or (fn == b['fn'] and mqreg == b['mqreg'] and mqreg in SAVED)
            if not same:
                continue
            slot = val(insns, j, 'a1')
            slotr = reg_before(insns, j, 'a1')
            off = None
            for k in [j + 1] + list(range(j - 1, max(-1, j - 40), -1)):
                if insns[k][3] != fn:
                    break
                if c7392.dest_of(insns[k][1], insns[k][2]) == 'a1' or (slotr != 'a1' and c7392.dest_of(insns[k][1], insns[k][2]) == slotr):
                    o = insns[k][2]
                    if insns[k][1] == 'addiu' and len(o) == 3 and o[1] == 'sp':
                        off = int(o[2], 0)
                    break
            if slot == 0:
                kind, why = 'DISCARD', 'slot=NULL'
            elif off is None:
                kind, why = 'UNRESOLVED-SLOT', 'slot=%s' % fmt(slot)
            else:
                kind, why = use_of(insns, j, fn, off)
            rows.append((b['ev'], a, fn, kind, why, b['msg']))
            print('%-7s recv@%08X %-26s mq=%-10s %-8s %-50s bound_msg=%s %s' % (b['ev'], a, fn, fmt(mq) if isinstance(mq, int) else mqreg,
                  kind, why, fmt(b['msg']), 'REPLACED' if fn in rep else 'LIVE'))
    print('== senders (host side)')
    exact = {'Vi': 'cur_state->msg', 'Sp': 'events_context.sp.msg', 'Dp': 'events_context.dp.msg', 'Ai': 'events_context.ai.msg',
             'Si': 'events_context.si.msg', 'Timer': 'cur_timer->msg', 'Pi': 's7398_msg'}
    snd_ok = {}
    for f, n, src, mq, msg, jam in senders():
        ok = msg == exact.get(src) or (src == 'Sp' and f == 'extensions.cpp' and msg == 'iter->mesg')
        snd_ok.setdefault(src.upper(), []).append(ok)
        print('%-15s:%-5d src=%-5s mq=%-22s msg=%-24s jam=%-5s %s' % (f, n, src, mq, msg, jam, 'BOUND-MSG' if ok else 'LITERAL/OTHER'))
    print('== verdict per event')
    for ev in sorted({r[0] for r in rows} | {b['ev'] for b in bind if b['live']}):
        r = [x for x in rows if x[0] == ev]
        kinds = sorted({x[3] for x in r})
        sok = snd_ok.get(ev, [])
        need = any(k in ('CMP', 'DEREF', 'PASS') for k in kinds)
        unres = any(not isinstance(b['mq'], int) and b['mqreg'] not in SAVED for b in bind if b['ev'] == ev and b['live'])
        v = 'H-none' if (not need or (sok and all(sok))) and not unres and 'UNRESOLVED-SLOT' not in kinds else 'CHECK'
        if ev == 'PRENMI':
            v = 'H-none (host never raises PRENMI; consumer waits forever, retail-equivalent without a reset)'
        bad += v == 'CHECK'
        print('  %-7s consumers=%d kinds=%s senders_bound=%s -> %s' % (ev, len(r), ','.join(kinds) or '-',
              '%d/%d' % (sum(sok), len(sok)) if sok else 'n/a', v))
    print('CHECK rows=%d' % bad)
    sys.exit(1 if (check and bad) else 0)


if __name__ == '__main__':
    main()
