#!/usr/bin/env python3
"""s7547 class GG census: guest pointers the HOST retains past the guest call that handed them over.

The guest frees and reuses heap objects (s7545: destroyed thread nodes reused within ~2 s), so a host-retained pointer to a
heap object that the guest frees while still registered would deliver messages into / read from whatever now lives there.

Part A (host side): every host-lifetime store of a guest pointer in ultramodern / librecomp / src/main.  Each RETAIN row is
located by regex in the source (missing = DRIFT, a failure) and names the guest API + argument it retains, or a non-retention
reason (copied at call, synchronous, derived from another row, diagnostic).
Part B (guest side): every jal site of each retaining API in the canonical listing (tools/s7419_canon_dis.py); the retained
argument is resolved backwards (tools/s7392_mesg_census.resolve) and classified against the main heap, whose base is derived
from the listing (thread3_video_handle -> initMainHeap a2 = lui/addiu v0 + lui/addiu a2):
  H-static   constant address in the static image (< heap base) or in the top-of-RAM framebuffer carve -- never rs_free'd.
  H-loaded   value loaded from a static global; the rule names what writes that global (must be a static object or the carve).
  H-stack    sp-relative object; allowed only when the same function blocks on that queue (osRecvMesg BLOCK) before return.
  H-dead     the calling function is replaced by librecomp/the port (never runs) or the call is unreachable.
  H-stale    a heap object (>= heap base, below the carve) that is retained -> needs an unregister-before-free proof.
  OPEN       a stack object with no blocking receive, or a heap object; UNCLASSIFIED: no rule resolves the value.
Exit 0 iff 0 OPEN, 0 UNCLASSIFIED, 0 DRIFT.  --controls: (1) planted heap-address retention site -> OPEN; (2) planted stack
queue with no recv -> OPEN; (3) deleted H-loaded rule -> UNCLASSIFIED; (4) host regex removed from source text -> DRIFT;
(5) the real tree -> rc 0; (6) fb slot-table writer set short by one PC -> OPEN (both osViSwapBuffer rows).
"""
import os, re, sys, collections, importlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
c7392 = importlib.import_module('s7392_mesg_census')
c7397 = importlib.import_module('s7397_timer_census')
c7398 = importlib.import_module('s7398_iomesg_census')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UM = 'lib/N64ModernRuntime/ultramodern/src/'
LR = 'lib/N64ModernRuntime/librecomp/src/'

# ---- Part A: host retention sites. (file, regex, kind, api/argspec or reason)
# kind RETAIN = pointer outlives the call (argspec: api:arg, arg = a0..a3 or sp+N); other kinds say why it is not retained.
HOST = [
    (UM + 'events.cpp', r'events_context\.sp\.mq = mq_', 'RETAIN', 'osSetEventMesg:a1'),
    (UM + 'events.cpp', r'events_context\.dp\.mq = mq_', 'RETAIN', 'osSetEventMesg:a1'),
    (UM + 'events.cpp', r'events_context\.ai\.mq = mq_', 'RETAIN', 'osSetEventMesg:a1'),
    (UM + 'events.cpp', r'events_context\.si\.mq = mq_', 'RETAIN', 'osSetEventMesg:a1'),
    (UM + 'events.cpp', r'next_state->mq = mq_', 'RETAIN', 'osViSetEvent:a0'),
    (UM + 'events.cpp', r'next_state->mode_guest = mode_', 'RETAIN', 'osViSetMode:a0'),
    (UM + 'events.cpp', r'next_state->framebuffer = ', 'RETAIN', 'osViSwapBuffer:a0'),
    (UM + 'timer.cpp', r'active_timers\.insert', 'RETAIN', 'osSetTimer:a0'),
    (UM + 'timer.cpp', r'a\.mq = mq', 'RETAIN', 'osSetTimer:sp+24'),
    (LR + 'pi.cpp', r'enqueue_external_message_src\(mq, s7398_msg', 'RETAIN', 'osPiStartDma:sp+24'),
    (LR + 'pi.cpp', r'PTR\(OSMesgQueue\) mq = mb->hdr\.retQueue', 'RETAIN', 'osEPiStartDma:a1'),
    (UM + 'mesgqueue.cpp', r'g_audio_sp_deliveries\.push_back\(\{queued\.mq', 'DERIVED',
     'mq comes from events_context.sp (osSetEventMesg row); queue drains on the guest thread'),
    (UM + 'mesgqueue.cpp', r'struct QueuedMessage \{', 'DERIVED',
     'external-message queue: every producer passes an mq from a RETAIN row above (event/VI/timer/PI) or a host test arm'),
    (UM + 'extensions.cpp', r'pending_events\.emplace_back', 'RETAIN', 'osExQueueDisplaylistEvent:a0'),
    (UM + 'input.cpp', r'extern "C" s32 osContStartReadData', 'NOTRET',
     'mq argument unused by the host; completion goes to events_context.si (osSetEventMesg row)'),
    (LR + 'ai.cpp', r'osAiSetNextBuffer', 'NOTRET', 'PCM copied (byte-swapped) into a host vector at the call (class GB/GC)'),
    (UM + 'input.cpp', r'pfs->queue = mq', 'NOTRET', 'store INTO the guest OSPfs (guest-owned field), not host state'),
    ('src/main/main.cpp', r's_pending_task_guest_ptr\.store\(guest_ptr', 'DIAG',
     'read back only by the [m5-task-handoff] print (main.cpp, env-gated); never dereferenced'),
    (UM + 'events.cpp', r'action_queue\.enqueue\(SpTaskAction\{ \*task \}\)', 'NOTRET',
     'osSpTaskStartGo -> submit_rsp_task copies the OSTask by value; its data pointers in flight are class GA (s7535)'),
]
# APIs whose task / payload in flight is a different class (GA: SP-done ordering).  Not double-counted here.

# ---- Part B rules for values the resolver cannot reduce to a constant.  (api, caller fn, resolved-value regex) -> (class, why)
RULES = [
    ('osViSwapBuffer', None, r'^ld(arr)?:80128E98$', 'H-loaded',
     'fb slot table 0x80128E98..A0, written only by initVideoSubsystem 0x8001A140/160/16C from its cfg arg = the '
     'partitionFramebufferMemory table (&0x801163D8, thread3_video_handle 0x80001250, s7335): fbs sit at/above the heap '
     'hi *0x801163E4 (ensureHeapInitialized size = hi - base), never rs_malloc'),
]

# H-loaded globals whose writer set is verified against the listing: global range -> exact set of storing PCs
LOADED_WRITERS = {(0x80128E98, 0x80128EA4): {0x8001A140, 0x8001A160, 0x8001A16C}}


def writers(insns, lo, hi):
    out = set()
    for j, (a, mn, ops, fn) in enumerate(insns):
        if mn in ('sw', 'sd', 'sh', 'sb') and len(ops) == 2:
            m = re.match(r'(-?\d+)\((\w+)\)', ops[1])
            if not m or m.group(2) == 'sp':
                continue
            b = before(insns, j, m.group(2), -1)
            off = int(m.group(1))
            x = b if isinstance(b, int) else (int(b[4:], 16) if isinstance(b, str) and b.startswith('arr:') else None)
            if x is not None and lo <= ((x + off) & 0xFFFFFFFF) < hi:
                out.add(a)
    return out


CARVE_LO = 0x80700000   # framebuffer/pool carve at the top of the 8 MB (s6127); only used to label constants, not a pass


def heap_base(insns):
    """initMainHeap(mode, ?, base, hi): base = a2 at the thread3_video_handle call (lui/addiu v0 + lui/addiu a2, addu in delay)."""
    for i, (a, mn, ops, fn) in enumerate(insns):
        if mn == 'jal' and ops and '<initMainHeap>' in ops[0]:
            d = insns[i + 1]
            if d[1] == 'addu' and d[2][0] == 'a2':
                x = c7392.resolve_from(insns, i, d[2][1], 0)
                y = c7392.resolve_from(insns, i, d[2][2], 0)
                if isinstance(x, int) and isinstance(y, int):
                    return (x + y) & 0xFFFFFFFF
    return None


SAVED = {'s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 'fp', 'sp', 'gp'}


def before(insns, k, reg, own, depth=0):
    """Value of reg just before insns[k] executes (linear backward scan inside the function).  Callee-saved registers survive
    an intervening jal; others become '?'.  Returns int, 'stk:N' (sp+N), 'ld:ADDR' (load from constant ADDR), 'arr:BASE'
    (BASE + an unresolved index), 'arg:REG' (live-in) or '?'."""
    if reg == 'zero':
        return 0
    if reg == 'sp':
        return 'stk:0'
    if depth > 12:
        return '?'
    fn = insns[k][3] if k < len(insns) else None
    for j in range(k - 1, max(-1, k - 400), -1):
        a, mn, ops, f = insns[j]
        if f != fn:
            return 'arg:' + reg
        if j >= 1 and insns[j - 1][1] in ('jal', 'jalr') and j - 1 != own and reg not in SAVED:
            if dest(mn, ops) == reg:
                pass  # the delay slot itself defines it; callee ran after -> still clobbered
            return '?'
        if dest(mn, ops) != reg:
            continue
        r = lambda x: before(insns, j, x, own, depth + 1)
        if mn == 'li':
            return int(ops[1], 0) & 0xFFFFFFFF
        if mn == 'lui':
            return (int(ops[1], 0) << 16) & 0xFFFFFFFF
        if mn == 'move':
            return r(ops[1])
        if mn in ('addiu', 'daddiu', 'ori'):
            b = r(ops[1]); imm = int(ops[2], 0)
            if isinstance(b, int):
                return (b | imm) if mn == 'ori' else (b + imm) & 0xFFFFFFFF
            if isinstance(b, str) and b.startswith('stk:'):
                return 'stk:%d' % (int(b[4:]) + imm)
            if isinstance(b, str) and b.startswith('arr:'):
                return 'arr:%08X' % ((int(b[4:], 16) + imm) & 0xFFFFFFFF)
            return '?'
        if mn in ('addu', 'daddu', 'or'):
            x, y = r(ops[1]), r(ops[2])
            if isinstance(x, int) and isinstance(y, int):
                return (x + y) & 0xFFFFFFFF if mn != 'or' else x | y
            for c in (x, y):
                if isinstance(c, int) and c >= 0x80000000:
                    return 'arr:%08X' % c
            return '?'
        if mn in ('lw', 'lwu', 'ld'):
            m = re.match(r'(-?\d+)\((\w+)\)', ops[1])
            if m:
                b = r(m.group(2))
                if isinstance(b, int):
                    return 'ld:%08X' % ((b + int(m.group(1))) & 0xFFFFFFFF)
                if isinstance(b, str) and b.startswith('stk:') and b == 'stk:0':
                    off = int(m.group(1))   # reload of a spill slot: resolve the last store to it in this function
                    for q in range(j - 1, max(-1, j - 400), -1):
                        if insns[q][3] != fn:
                            break
                        if insns[q][1] == 'sw' and len(insns[q][2]) == 2 and insns[q][2][1] == '%d(sp)' % off:
                            v = before(insns, q, insns[q][2][0], own, depth + 1)
                            return v if not isinstance(v, str) or v != '?' else 'ldstk:%d' % off
                    return 'ldstk:%d' % off
                if isinstance(b, str) and b.startswith('arr:'):
                    return 'ldarr:%08X' % ((int(b[4:], 16) + int(m.group(1))) & 0xFFFFFFFF)
            return '?'
        return '?'
    return '?'


def dest(mn, ops):
    if not ops or mn.startswith('s') and mn in ('sw', 'sh', 'sb', 'sd', 'swc1', 'sdc1', 'swl', 'swr'):
        return None
    if mn.startswith('b') or mn in ('j', 'jr', 'jal', 'jalr', 'nop', 'mtc1', 'dmtc1', 'mthi', 'mtlo', 'mult', 'multu', 'div', 'divu',
                                    'dmult', 'dmultu', 'ddiv', 'ddivu', 'teq', 'cache', 'sync'):
        return None
    return ops[0]


def fmtv(v):
    return '0x%08X' % v if isinstance(v, int) else v


def argval(insns, i, spec):
    if spec.startswith('sp+'):
        off = int(spec[3:])
        for j in (i + 1,) + tuple(range(i - 1, max(i - 60, -1), -1)):
            a, mn, ops, fn = insns[j]
            if mn == 'sw' and len(ops) == 2 and ops[1] == '%d(sp)' % off:
                return fmtv(before(insns, j, ops[0], i))
        return '?'
    return fmtv(before(insns, i + 2, spec, i))


WRITER_CACHE = {}


def classify(api, fn, v, insns, i, rep, base):
    if fn in rep:
        return 'H-dead', 'caller %s replaced by librecomp (never runs)' % fn
    if api in rep and api not in ('osSetEventMesg', 'osViSetEvent', 'osSetTimer', 'osPiStartDma', 'osViSetMode',
                                  'osViSwapBuffer', 'osEPiStartDma', 'osSpTaskStartGo'):
        pass
    s = str(v)
    def region(x):
        if x == 0:
            return 'H-static', 'NULL (unregister)'
        if x < base:
            return 'H-static', 'static image (< heap base 0x%08X)' % base
        if x >= CARVE_LO:
            return 'H-static', 'top-of-RAM carve'
        return 'OPEN', 'heap object 0x%08X retained (H-stale candidate)' % x
    m = re.match(r'^0x([0-9A-Fa-f]{8})$', s)
    if m:
        return region(int(m.group(1), 16))
    m = re.match(r'^arr:([0-9A-F]{8})$', s)
    if m:
        c, w = region(int(m.group(1), 16))
        return c, 'element of static array 0x%s: %s' % (m.group(1), w) if c != 'OPEN' else w
    if s.startswith('stk:'):
        r = c7398.next_recv(insns, i, fn)
        if 'recv@' in r and re.search(r'flag=(0x0*)?1\b', r):
            return 'H-stack', 'stack object, blocking recv in the same activation: ' + r
        return 'OPEN', 'stack object retained with no blocking recv (%s)' % r
    for api_r, fn_r, vre, cls, why in RULES:
        if api_r == api and (fn_r is None or fn_r == fn) and re.search(vre, s):
            if cls == 'H-loaded':
                g = int(s.split(':')[1], 16)
                for (lo, hi), want in LOADED_WRITERS.items():
                    if lo <= g < hi:
                        got = WRITER_CACHE.setdefault((lo, hi), writers(insns, lo, hi))
                        if got != want:
                            return 'OPEN', 'writer set of 0x%08X changed: %s' % (g, sorted('%08X' % x for x in got))
                        return cls, why + ' [writers verified: %s]' % ','.join('%08X' % x for x in sorted(got))
                return 'UNCLASSIFIED', 'H-loaded global 0x%08X has no verified writer set' % g
            return cls, why
    return 'UNCLASSIFIED', 'no rule for value %s' % v


def run(insns, srcs, rules_override=None, extra_sites=()):
    global RULES
    saved = RULES
    if rules_override is not None:
        RULES = rules_override
    try:
        rep = c7397.replaced()
        base = heap_base(insns)
        out = collections.Counter()
        rows = []
        retained = collections.defaultdict(list)
        for f, rx, kind, spec in HOST:
            txt = srcs.get(f)
            if txt is None:
                txt = srcs[f] = open(os.path.join(REPO, f), errors='replace').read()
            hit = re.search(rx, txt)
            if not hit:
                rows.append(('A', 'DRIFT', '%s /%s/ not found' % (f, rx)))
                out['DRIFT'] += 1
                continue
            ln = txt.count('\n', 0, hit.start()) + 1
            rows.append(('A', kind, '%s:%d %s' % (f, ln, spec)))
            out['A-' + kind] += 1
            if kind == 'RETAIN':
                api, arg = spec.split(':')
                if arg not in retained[api]:
                    retained[api].append(arg)
        if base is None:
            rows.append(('B', 'UNCLASSIFIED', 'heap base not derivable from listing'))
            out['UNCLASSIFIED'] += 1
            base = 0
        sites = []
        for i, (a, mn, ops, fn) in enumerate(insns):
            if mn != 'jal' or not ops:
                continue
            t = re.search(r'<([^>+]+)>', ops[0])
            if t and t.group(1) in retained:
                for arg in retained[t.group(1)]:
                    sites.append((i, a, t.group(1), fn, arg, argval(insns, i, arg)))
        for (a, api, fn, arg, v) in extra_sites:
            sites.append((None, a, api, fn, arg, v))
        seen_api = collections.Counter(s[2] for s in sites)
        for api in retained:
            if seen_api[api] == 0:
                rows.append(('B', 'H-dead', '%s: 0 guest jal sites (host-only API or never linked)' % api))
                out['H-dead'] += 1
        for i, a, api, fn, arg, v in sites:
            cls, why = classify(api, fn, v, insns, i if i is not None else 0, rep, base)
            rows.append(('B', cls, '%08X %-18s %-28s %s=%s  %s' % (a, api, fn, arg, v, why)))
            out[cls] += 1
        return rows, out, base
    finally:
        RULES = saved


def report(rows, out, base, quiet=False):
    if not quiet:
        print('heap base (initMainHeap a2) = 0x%08X' % base)
        for part, cls, txt in rows:
            print('%s %-12s %s' % (part, cls, txt))
        print('--- totals:', dict(out))
    bad = out['OPEN'] + out['UNCLASSIFIED'] + out['DRIFT']
    return 1 if bad else 0


def main():
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    dis = args[0] if args else c7392.DIS
    insns = c7392.parse(dis)
    if '--controls' in sys.argv:
        ok = 0
        # 1 planted heap pointer retained
        r, o, b = run(insns, {}, extra_sites=[(0x80FFFFF0, 'osSetEventMesg', 'plantedHeap', 'a1', '0x80200000')])
        c1 = o['OPEN'] == 1; ok += c1
        # 2 planted stack queue without recv (index 0 = no recv in fn)
        r, o, b = run(insns, {}, extra_sites=[(0x80FFFFF4, 'osPiStartDma', 'plantedStack', 'sp+24', 'stk:64')])
        c2 = o['OPEN'] == 1; ok += c2
        # 3 deleted rule
        r, o, b = run(insns, {}, rules_override=[x for x in RULES if x[0] != 'osViSwapBuffer'])
        c3 = o['UNCLASSIFIED'] >= 1; ok += c3
        # 4 drift: host regex absent
        src = {UM + 'events.cpp': open(os.path.join(REPO, UM + 'events.cpp')).read().replace('next_state->mq = mq_', 'next_state->mq_ = mq_')}
        r, o, b = run(insns, src)
        c4 = o['DRIFT'] == 1; ok += c4
        # 6 writer-set drift: expect one writer fewer than the listing has -> OPEN
        saved_w = dict(LOADED_WRITERS); WRITER_CACHE.clear()
        LOADED_WRITERS[(0x80128E98, 0x80128EA4)] = {0x8001A140, 0x8001A160}
        r, o, b = run(insns, {})
        c6 = o['OPEN'] == 2; ok += c6
        LOADED_WRITERS.clear(); LOADED_WRITERS.update(saved_w); WRITER_CACHE.clear()
        # 5 real tree
        r, o, b = run(insns, {})
        c5 = report(r, o, b, quiet=True) == 0; ok += c5
        print('controls: heap-plant=%s stack-plant=%s rule-del=%s drift=%s writer-drift=%s real=%s -> %d/6' % (c1, c2, c3, c4, c6, c5, ok))
        return 0 if ok == 6 else 1
    rows, out, base = run(insns, {})
    return report(rows, out, base)


if __name__ == '__main__':
    sys.exit(main())
