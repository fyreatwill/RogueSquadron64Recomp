#!/usr/bin/env python3
"""s7383 class AY: census of every host std::atomic op with an explicit memory_order, plus every plain `volatile`
scalar declared at namespace/static scope (a candidate cross-thread flag with no ordering on arm64).

Scope: src/main, src/rsp, lib/rt64/src/{hle,render,common,rhi,apple,gui,shared},
lib/N64ModernRuntime/{ultramodern,librecomp} (thirdparty / contrib excluded: concurrentqueue is upstream-audited).

Per atomic (file-group key = variable name, ops collected across ALL files) the class is automatic:
  COUNTER          only RMW (fetch_*, ++/--, exchange) + loads, no plain store of a value -> relaxed is fine
  ORDERED          every store is release/seq_cst and every load acquire/seq_cst (or RMW acq_rel) -> fine
  TUPLE-RELAXED    a relaxed store sits within 4 lines of a relaxed store to ANOTHER atomic in the same function, and the
                   same two atomics are loaded within 6 lines of each other somewhere -> the reader can pair fields from
                   two different writes (torn tuple); needs a verdict
  MIXED            some stores relaxed and some loads acquire (or release store + relaxed load used as a gate) -> verdict
  VALUE-RELAXED    relaxed store + relaxed load of a single value -> verdict: VALUE (the atomic is the datum) or PUBLISH
  VOLATILE         namespace/static `volatile` scalar (not a cast, not an rdram pointer) -> verdict
Verdicts (tools/s7383_atomic_reviewed.tsv, key `var|class`): VALUE <why> | SAMETHREAD <why> | DIAG <why> (env-gated
diagnostic, default off, value is only printed) | LOCKED <why> (a mutex covers both sides) | FIXED <how> | PUBLISH (open).
--check  exit 1 on an unreviewed non-auto row, a stale review, a PUBLISH verdict, or a control failure.
Controls (always run): planted relaxed field pair read together -> TUPLE-RELAXED; planted fetch_add counter -> COUNTER;
planted release/acquire flag -> ORDERED; planted `static volatile int flag;` -> VOLATILE; planted relaxed single flag ->
VALUE-RELAXED; the real g_rs64_last_drawn_fb must classify TUPLE-RELAXED (verdict FIXED via the s7383 packed snapshot).
"""
import argparse, glob, os, re, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ['src/main', 'src/rsp', 'lib/rt64/src/hle', 'lib/rt64/src/render', 'lib/rt64/src/common', 'lib/rt64/src/rhi',
        'lib/rt64/src/apple', 'lib/rt64/src/gui', 'lib/rt64/src/shared', 'lib/N64ModernRuntime/ultramodern',
        'lib/N64ModernRuntime/librecomp']
TSV = os.path.join(ROOT, 'tools', 's7383_atomic_reviewed.tsv')
EXT = ('.cpp', '.c', '.mm', '.h', '.hpp')
OP_RE = re.compile(r'([A-Za-z_]\w*)(?:\[[^\]]*\])?\s*(?:\.|->)\s*(load|store|fetch_add|fetch_sub|fetch_or|fetch_and|fetch_xor|'
                   r'exchange|compare_exchange_weak|compare_exchange_strong)\s*\(([^;]*?)std::memory_order(?:_|::)'
                   r'(relaxed|acquire|release|acq_rel|consume|seq_cst)')
VOL_RE = re.compile(r'^(?:extern\s+"C"\s*\{?\s*|static\s+|extern\s+)?(?:__thread\s+)?volatile\s+(?!uint8_t\s*\*)'
                    r'(?:unsigned|int|LONG|uint\d+_t|int\d+_t|uintptr_t|bool|float)\s+([A-Za-z_]\w*)\s*(?:=|;|,|\[)')
FUNC_RE = re.compile(r'^[A-Za-z_][\w:<>,\*&\s~]*\b([\w:~]+)\s*\([^;]*\)\s*(?:const\s*)?(?:noexcept\s*)?\{?\s*$')
RMW = {'fetch_add', 'fetch_sub', 'fetch_or', 'fetch_and', 'fetch_xor', 'exchange', 'compare_exchange_weak',
       'compare_exchange_strong'}


def files():
    out = []
    for d in DIRS:
        for f in glob.glob(os.path.join(ROOT, d, '**', '*'), recursive=True):
            if f.endswith(EXT) and '/thirdparty/' not in f and '/contrib/' not in f and '/N64Recomp/' not in f:
                out.append(f)
    return sorted(out)


def scan(named_texts):
    """named_texts: [(rel, text)] -> (ops, vols). ops: var -> list of (rel, line, func, op, order)."""
    ops, vols = defaultdict(list), {}
    for rel, text in named_texts:
        func = '?'
        for i, raw in enumerate(text.split('\n'), 1):
            line = raw.split('//')[0]
            if not raw.startswith((' ', '\t')):
                m = FUNC_RE.match(line)
                if m: func = m.group(1)
            for m in OP_RE.finditer(line):
                ops[m.group(1)].append((rel, i, func, m.group(2), m.group(4)))
            if not raw.startswith((' ', '\t')) or raw.lstrip().startswith('static volatile'):
                for m in VOL_RE.finditer(line.strip()):
                    vols.setdefault(m.group(1), (rel, i))
    return ops, vols


def classify(ops):
    cls = {}
    # tuple detection: relaxed stores within 4 lines, same file+func, different vars
    stores = [(rel, ln, fn, v) for v, L in ops.items() for (rel, ln, fn, op, o) in L
              if op in ('store', 'exchange') and o == 'relaxed']
    loads = [(rel, ln, fn, v) for v, L in ops.items() for (rel, ln, fn, op, o) in L if op == 'load' and o == 'relaxed']
    pairs = set()
    for a in stores:
        for b in stores:
            # s7720: was 4 lines; the s7569/s7384 witness blocks pushed the last-drawn width/siz stores 21 lines below the
            # address exchange, so the real-site control read COUNTER. 24 adds only that pair (window 4..16 -> 26 tuples, 24 -> 27).
            if a[3] != b[3] and a[0] == b[0] and a[2] == b[2] and abs(a[1] - b[1]) <= 24:
                pairs.add(frozenset((a[3], b[3])))
    loaded_pairs = set()
    for a in loads:
        for b in loads:
            if a[3] != b[3] and a[0] == b[0] and abs(a[1] - b[1]) <= 6:
                loaded_pairs.add(frozenset((a[3], b[3])))
    tuple_vars = defaultdict(set)
    for p in pairs & loaded_pairs:
        x, y = tuple(p)
        tuple_vars[x].add(y); tuple_vars[y].add(x)
    for v, L in ops.items():
        st = [o for (_, _, _, op, o) in L if op == 'store']
        ld = [o for (_, _, _, op, o) in L if op == 'load']
        rmw = [o for (_, _, _, op, o) in L if op in RMW]
        if v in tuple_vars:
            cls[v] = ('TUPLE-RELAXED', sorted(tuple_vars[v]))
        elif not st:
            cls[v] = ('COUNTER', [])
        elif all(o in ('release', 'seq_cst', 'acq_rel') for o in st) and all(o in ('acquire', 'seq_cst') for o in ld) \
                and all(o in ('acq_rel', 'seq_cst', 'release', 'acquire') for o in rmw):
            cls[v] = ('ORDERED', [])
        elif any(o == 'relaxed' for o in st) and any(o in ('acquire', 'seq_cst') for o in ld) or \
                any(o in ('release', 'seq_cst') for o in st) and any(o == 'relaxed' for o in ld):
            cls[v] = ('MIXED', [])
        else:
            cls[v] = ('VALUE-RELAXED', [])
    return cls


CONTROL_SRC = '''
static std::atomic<uint32_t> ctl_fa{0}, ctl_fb{0}, ctl_cnt{0}, ctl_flag{0}, ctl_one{0};
static volatile int ctl_vflag = 0;
void ctl_writer() {
    ctl_fa.store(1, std::memory_order_relaxed);
    ctl_fb.store(2, std::memory_order_relaxed);
    ctl_cnt.fetch_add(1, std::memory_order_relaxed);
    ctl_flag.store(1, std::memory_order_release);
}
void ctl_writer2() {
    ctl_one.store(3, std::memory_order_relaxed);
}
void ctl_reader() {
    const uint32_t a = ctl_fa.load(std::memory_order_relaxed);
    const uint32_t b = ctl_fb.load(std::memory_order_relaxed);
    if (ctl_flag.load(std::memory_order_acquire)) {}
    const uint32_t c = ctl_cnt.load(std::memory_order_relaxed);
}
void ctl_reader2() {
    const uint32_t d = ctl_one.load(std::memory_order_relaxed);
}
'''


def controls(real_cls):
    ops, vols = scan([('CONTROL', CONTROL_SRC)])
    c = classify(ops)
    want = {'ctl_fa': 'TUPLE-RELAXED', 'ctl_fb': 'TUPLE-RELAXED', 'ctl_cnt': 'COUNTER', 'ctl_flag': 'ORDERED',
            'ctl_one': 'VALUE-RELAXED'}
    bad = [f'{k}: got {c.get(k, ("absent",))[0]} want {w}' for k, w in want.items() if c.get(k, ('absent',))[0] != w]
    if 'ctl_vflag' not in vols: bad.append('ctl_vflag: VOLATILE not detected')
    if real_cls.get('g_rs64_last_drawn_fb', ('absent',))[0] != 'TUPLE-RELAXED':
        bad.append(f'real g_rs64_last_drawn_fb: got {real_cls.get("g_rs64_last_drawn_fb", ("absent",))[0]}')
    return bad


def load_tsv():
    rev = {}
    if os.path.exists(TSV):
        for ln in open(TSV):
            if ln.strip() and not ln.startswith('#'):
                k, v = ln.rstrip('\n').split('\t', 1)
                rev[k] = v
    return rev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--list', action='store_true', help='print every row needing a verdict')
    ap.add_argument('--all', action='store_true', help='print every atomic incl. auto classes')
    a = ap.parse_args()
    texts = [(os.path.relpath(f, ROOT), open(f, errors='ignore').read()) for f in files()]
    ops, vols = scan(texts)
    cls = classify(ops)
    rev = load_tsv()
    rows = {}
    for v, (c, extra) in cls.items():
        site = ops[v][0]
        rows[f'{v}|{c}'] = (c, f'{site[0]}:{site[1]}', len(ops[v]), extra)
    for v, (rel, ln) in vols.items():
        if v not in cls: rows[f'{v}|VOLATILE'] = ('VOLATILE', f'{rel}:{ln}', 1, [])
    tally = defaultdict(int); unrev, publish = [], []
    for k, (c, site, n, extra) in sorted(rows.items()):
        tally[c] += 1
        auto = c in ('COUNTER', 'ORDERED')
        verdict = rev.get(k, 'AUTO' if auto else None)
        if verdict is None: unrev.append(k)
        elif verdict.startswith('PUBLISH'): publish.append(k)
        if a.all or (a.list and not auto):
            print(f'{k}\t{site}\tn={n}\t{",".join(extra)}\t{verdict}')
    stale = [k for k in rev if k not in rows]
    bad = controls(cls)
    nops = sum(len(L) for L in ops.values())
    print(f'[s7383] {nops} explicit-order ops on {len(cls)} atomics, {len(vols)} static volatiles; classes ' +
          ' '.join(f'{c}={n}' for c, n in sorted(tally.items())))
    print(f'[s7383] unreviewed={len(unrev)} stale={len(stale)} publish={len(publish)} controls={"PASS" if not bad else "FAIL"}')
    for x in unrev[:40]: print('  UNREVIEWED', x)
    for x in stale: print('  STALE', x)
    for x in publish: print('  PUBLISH', x)
    for x in bad: print('  CONTROL-FAIL', x)
    if a.check and (unrev or stale or publish or bad): sys.exit(1)


if __name__ == '__main__':
    main()
