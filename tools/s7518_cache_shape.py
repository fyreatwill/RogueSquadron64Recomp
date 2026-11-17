#!/usr/bin/env python3
"""s7518 class FO: D-cache maintenance contract vs VR4300 semantics, scored from ROGUESQ_LOG_CACHE_SHAPE=1 logs.

The host memory is coherent, so the port can only differ from hardware where hardware would see a stale or discarded line.
Model per 16-byte line (conservative: any line not provably uncached may be resident):
  osInvalDCache(a,n): n >= 8192 -> index writeback-invalidate of the whole cache (ROM 0x8002C308, cache op 0x01): every line N.
                      else edge lines hit-writeback-invalidate (op 0x15), interior hit-invalidate (op 0x11, DISCARDS dirty data).
  osWritebackDCache(a,n): lines clean but still resident (W). osWritebackDCacheAll: every line W.
  PI DMA cart->RDRAM: a line in state N is safe (the CPU refetches). A line in state W/C may hold a stale copy -> STALE row.
                      After the DMA the line is C again (the CPU will read it).
  SP task start: the RSP reads data_ptr from RAM; a line the CPU may still hold dirty (C) -> UNFLUSHED row. data_size 0 (gfx DL)
                 -> first 8 bytes checked; a wball since the previous task covers everything.
Rows: stale_first (first DMA ever into a line: boot / never-cached state unknown), stale_repeat (line DMA'd before, no inv since),
unflushed, discard (hit-invalidate interior line whose following event is not a DMA covering it).
stale_repeat/stale_first are POTENTIAL only (a DMA over a line not invalidated since its previous DMA): they matter only if the CPU
then loads the line before an invalidate, which the runtime watch (ROGUESQ_S7518_STALEWATCH=1, [s7518-load] STALE rows) decides.
Exit: 0 no runtime stale_load outside the planted ctl and no unflushed task; 1 rows; 3 ctl not proven (--ctl: some arm's STALE row
must fall in its dropped-invalidate range); 4 no rows; 5 controls fail."""
import re, sys, collections
L = 16
RX = re.compile(r'\[cache\] op=(\w+) a=([0-9A-F]+) n=([0-9A-F]+)')
STALE = re.compile(r'\[s7518-load\] STALE pc=([0-9A-F]+) fn=\S+ a=([0-9A-F]+)')
SUM = re.compile(r'\[s7518-sum\] (.*)')
CTL = re.compile(r'\[cache-ctl\] dropped inv k=(\d+) a=([0-9A-F]+) n=([0-9A-F]+)')

def score(lines):
    st = {}            # line -> 'N' | 'W' | 'C'   (missing = unknown, treated as C, first)
    gen = 'C'          # state of lines not in st after a whole-cache op
    dmaed = set()
    sp_wball = {}      # type -> wball seen since previous task of that type
    out = collections.Counter(); ex = collections.defaultdict(list)
    ctl = None; ctl_hit = 0; pend_discard = {}; flushed = {'all': False, 'rng': False}; sp_next = []
    def S(l): return st.get(l, gen)
    def row(k, a, n, extra=''):
        out[k] += 1
        if len(ex[k]) < 8: ex[k].append('%08X+%X%s' % (a, n, extra))
    for ln in lines:
        m = STALE.search(ln)
        if m:
            sa = int(m.group(2), 16) & 0x1FFFFFFF
            if ctl and ctl[0] <= sa < ctl[0] + ctl[1]: out['stale_load_ctl'] += 1; ctl_hit += 1
            else: row('stale_load', sa, 1, ' pc=%s' % m.group(1))
            continue
        m = SUM.search(ln)
        if m: out['watch_sum'] = m.group(1); continue
        m = CTL.search(ln)
        if m: ctl = (int(m.group(2), 16) & 0x1FFFFFFF, int(m.group(3), 16)); continue
        m = RX.search(ln)
        if not m: continue
        op, a, n = m.group(1), int(m.group(2), 16) & 0x1FFFFFFF, int(m.group(3), 16)
        out['ev_' + op] += 1
        lo, hi = a // L, (a + max(n, 1) - 1) // L
        if op == 'inv':
            if n <= 0: continue
            if n >= 8192:
                st.clear(); gen = 'N'; out['inv_index'] += 1; pend_discard.clear(); continue
            for l in range(lo, hi + 1): st[l] = 'N'
            interior = [l for l in range(lo, hi + 1) if not ((l == lo and a % L) or (l == hi and (a + n) % L))]
            for l in interior: pend_discard[l] = (a, n)
        elif op == 'wb':
            sp_next.append((a, n))
            for l in range(lo, hi + 1):
                if S(l) != 'N': st[l] = 'W'
                pend_discard.pop(l, None)
        elif op == 'wball':
            for l in list(st):
                if st[l] == 'C': st[l] = 'W'
            if gen == 'C': gen = 'W'
            pend_discard.clear()
        elif op == 'iinv':
            pass
        elif op == 'dma0':
            bad = [l for l in range(lo, hi + 1) if S(l) != 'N']
            first = [l for l in bad if l not in dmaed]; rep = [l for l in bad if l in dmaed]
            if ctl and a <= ctl[0] < a + n: out['ctl_dma'] += 1
            if rep: row('stale_repeat', a, n, ' lines=%d/%d' % (len(rep), hi - lo + 1))
            elif first: row('stale_first', a, n, ' lines=%d/%d' % (len(first), hi - lo + 1))
            else: out['dma_ok'] += 1
            for l in range(lo, hi + 1):
                st[l] = 'C'; dmaed.add(l); pend_discard.pop(l, None)
        elif op == 'dma1':
            out['dma_out'] += 1
        elif op.startswith('sp'):
            # RSP input contract: since the previous task boundary, a wball or a wb covering data_ptr (CPU writes happen
            # between boundaries; DMA and invalidate events add no CPU-dirty data).
            flushed['rng'] = any(w <= a < w + wn for w, wn in sp_next); sp_next.clear()
            if flushed['all'] or flushed['rng']: out['sp_ok'] += 1
            else: row('unflushed', a, n, ' type=%s' % op[2:])
            flushed['all'] = False; flushed['rng'] = False; sp_a = None
            continue
        if op == 'wball': flushed['all'] = True
    out['discard'] = len(pend_discard)
    return out, ex, ctl, ctl_hit

def verdict(o, ch):
    return (1 if o['stale_repeat'] else 0, 1 if o['unflushed'] else 0, 1 if o['stale_load'] else 0, 1 if ch else 0)

def controls():
    D = lambda a, n: '[cache] op=dma0 a=%08X n=%X ra=0' % (a, n)
    I = lambda a, n: '[cache] op=inv a=%08X n=%X ra=0' % (a, n)
    W = lambda a, n: '[cache] op=wb a=%08X n=%X ra=0' % (a, n)
    A = '[cache] op=wball a=0 n=0 ra=0'
    SP = lambda t, a: '[cache] op=sp%d a=%08X n=1 ra=0' % (t, a)
    ST = lambda a: '[s7518-load] STALE pc=8002871C fn=inflate_codes_recomp a=%08X w=1 k=1' % a
    CT = lambda a, n: '[cache-ctl] dropped inv k=1 a=%08X n=%X ra=0' % (a, n)
    # want = (offline dma-over-resident, unflushed task, runtime stale load outside ctl, ctl proven)
    cases = {
        'clean':        ([W(0x80100000, 0x100), D(0x80100000, 0x100), I(0x80100000, 0x100), W(0x80100000, 0x100), D(0x80100000, 0x100),
                          I(0x80100000, 0x100), W(0x80200000, 0x40), SP(2, 0x80200000), A, SP(1, 0x80300000), A, SP(1, 0x80300000)], (0, 0, 0, 0)),
        'no_inv':       ([I(0x80100000, 0x100), D(0x80100000, 0x100), D(0x80100000, 0x100)], (1, 0, 0, 0)),
        'index_inv':    ([D(0x80100000, 0x100), I(0x80000000, 0x2000), D(0x80100000, 0x100)], (0, 0, 0, 0)),
        'partial_inv':  ([D(0x80100000, 0x100), I(0x80100000, 0x80), D(0x80100000, 0x100)], (1, 0, 0, 0)),
        'sp_unflushed': ([A, SP(1, 0x80300000), D(0x80300000, 0x10), SP(1, 0x80300000)], (0, 1, 0, 0)),
        'sp_wb_other':  ([A, SP(2, 0x80300000), W(0x80400000, 0x40), SP(2, 0x80300000)], (0, 1, 0, 0)),
        'stale_load':   ([D(0x80100000, 0x100), I(0x80100000, 0x100), ST(0x80100040)], (0, 0, 1, 0)),
        'ctl_stale':    ([D(0x80100000, 0x100), CT(0x80100000, 0x100), ST(0x80100040)], (0, 0, 0, 1)),
    }
    ok = True
    for k, (ls, want) in cases.items():
        o, ex, ctl, ch = score(ls)
        got = verdict(o, ch); p = got == want; ok &= p
        print('control %-13s got=%s want=%s %s' % (k, got, want, 'PASS' if p else 'FAIL'))
    return ok

def main():
    a = sys.argv[1:]; rc = 0
    if '--controls' in a:
        a.remove('--controls')
        if not controls(): return 5
    want_ctl = '--ctl' in a
    if want_ctl: a.remove('--ctl')
    anyrows = False; ctl_seen = False
    for f in a:
        o, ex, ctl, ch = score(open(f, errors='replace'))
        n = sum(v for k, v in o.items() if k.startswith('ev_'))
        anyrows |= n > 0
        print('%s events=%d %s' % (f, n, dict(sorted(o.items()))))
        for k, v in ex.items(): print('   %s e.g. %s' % (k, ' '.join(v)))
        print('   ctl=%s ctl_flagged=%d' % ('%08X+%X' % ctl if ctl else 'none', ch))
        ctl_seen |= bool(ch)
        if o['stale_load'] or o['unflushed']: rc = 1
        if 'watch_sum' not in o: print('   NOTE no [s7518-sum]: runtime stale watch not armed in this log')
    if not anyrows: return 4
    if rc == 0 and want_ctl and not ctl_seen: return 3
    return rc

if __name__ == '__main__':
    sys.exit(main())
