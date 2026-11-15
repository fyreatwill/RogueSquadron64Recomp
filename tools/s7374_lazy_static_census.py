#!/usr/bin/env python3
"""s7374 class AR census: non-atomic lazy-init statics.

Shape: a plain (non-atomic, non-const, non-thread_local) static scalar or pointer initialised to a sentinel and filled
on first use behind a test of that sentinel:
    static int en = -1;          if (en < 0) { en = getenv(..) ? 1 : 0; }
    static bool inited = false;  if (!inited) { inited = true; lim = ...; }
    static FILE* f = nullptr;    if (!f) f = fopen(...);
A plain-int sentinel reached from two threads is a C++ data race (UB) even when the value is idempotent; on arm64 it is
a real ordering defect when the guarded block ALSO publishes other state (companion statics, a pointer to a freshly
built object): another thread can observe the sentinel set and the companions stale.

Scope: src + librecomp + ultramodern + rt64 src/hle, src/render, src/gbi (the s7366 scope minus rt64 contrib).
Rows (one per sentinel with a lazy guard):
  SIMPLE     the guarded block assigns only the sentinel, from a pure expression (getenv / literal / arithmetic):
             idempotent value; formally racy if two threads, harmless in practice (single-copy-atomic aligned store)
  COMPANION  the block assigns the sentinel AND at least one other static (or the sentinel is a bool/flag guard whose
             block writes other statics): publication-order hazard if the function runs on >1 thread
  PTR        the sentinel is a pointer filled by fopen/new/malloc/an object: publication hazard if >1 thread
  LOCKED     a lock_guard/unique_lock/scoped_lock/.lock() is held at the guard (or the guard is std::call_once)
Rows COMPANION/PTR need a hand verdict in s7374_lazy_static_reviewed.tsv: SINGLE (one calling thread, named),
FIXED (converted to a magic static / locked), BENIGN-ORDER (companions written before the sentinel AND only read after
the sentinel by the same thread, or only diagnostic counters).
--selftest: planted file with one SIMPLE, COMPANION, PTR, LOCKED row, plus an atomic, a const and a thread_local
decl that must produce NO row.  --check: exit 1 on an unreviewed COMPANION/PTR row."""
import re, sys, os, glob
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7363_hostarr_census as an
import s7365_invalidation_census as ap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ['src', 'lib/N64ModernRuntime/librecomp', 'lib/N64ModernRuntime/ultramodern',
        'lib/rt64/src/hle', 'lib/rt64/src/render', 'lib/rt64/src/gbi']
SCALAR = (r'(?:unsigned\s+int|unsigned\s+long|unsigned|int|bool|long|long\s+long|float|double|size_t|uint8_t|uint16_t|'
          r'uint32_t|int32_t|uint64_t|int64_t|int8_t|int16_t|u32|s32|char)')
# a static declaration statement (may declare several names)
DECLSTMT = re.compile(r'(?<![\w])static\s+(?!const\b|constexpr\b|thread_local\b|std::atomic|volatile\b)'
                      r'((?:' + SCALAR + r')|(?:[A-Za-z_][\w:]*\s*\*+))\s*([^;(){}]*);')
LOCK = re.compile(r'\b(?:std::)?(?:lock_guard|unique_lock|scoped_lock)\b|\.\s*lock\s*\(\s*\)|\bcall_once\b')
PTRSRC = re.compile(r'\b(?:fopen|new|malloc|calloc|SDL_\w+|dlopen|dlsym|getenv)\b')

def decls(t):
    """yield (name, typ, sentinel_text, pos) for each static declarator with an initialiser"""
    for m in DECLSTMT.finditer(t):
        typ = m.group(1).strip()
        body = m.group(2)
        # split declarators at top-level commas
        depth, cur, parts = 0, '', []
        for ch in body:
            if ch in '{[(':
                depth += 1
            elif ch in '}])':
                depth -= 1
            if ch == ',' and depth == 0:
                parts.append(cur); cur = ''
            else:
                cur += ch
        parts.append(cur)
        ptr = typ.endswith('*')
        for p in parts:
            p = p.strip()
            mm = re.match(r'(\*?)\s*([A-Za-z_]\w*)\s*(?:=\s*(.+))?$', p, re.S)
            if not mm or '[' in p.split('=')[0]:
                continue
            yield mm.group(2), ('ptr' if (ptr or mm.group(1)) else typ), (mm.group(3) or '').strip(), m.start()

def guard_re(name, typ, sent):
    n = re.escape(name)
    if typ == 'ptr':
        return re.compile(r'\bif\s*\(\s*(?:!\s*%s|%s\s*==\s*(?:nullptr|NULL|0))\s*\)' % (n, n))
    if sent in ('-1', '-1.0', '-1.0f', '(-1)') or sent.startswith('-'):
        return re.compile(r'\bif\s*\(\s*%s\s*(?:<\s*0|==\s*-\s*1|<=\s*-\s*1|<\s*0\.0f?)\s*\)' % n)
    if sent in ('false', '0'):
        return re.compile(r'\bif\s*\(\s*(?:!\s*%s|%s\s*==\s*(?:0|false))\s*\)' % (n, n))
    return None

def guarded_block(t, pos):
    """text of the statement/block governed by the if at pos (pos = end of the if(...) match)"""
    i = pos
    while i < len(t) and t[i] in ' \t\n':
        i += 1
    if i < len(t) and t[i] == '{':
        return t[i + 1:an.block_end(t, i + 1)]
    j = t.find(';', i)
    return t[i:j + 1]

def assigned(block):
    return set(re.findall(r'(?<![\w.>:])([A-Za-z_]\w*)\s*(?:\[[^\]]*\]\s*)?(?<![=!<>])=(?!=)', block))

def scan(path, t):
    t = an.strip_comments(t)
    funcs = ap.functions(t)
    statics_fn, statics_file = {}, set()
    allds = list(decls(t))
    for (name, typ, sent, pos) in allds:
        f = ap.enclosing(funcs, pos)
        if f is None:
            statics_file.add(name)
        else:
            statics_fn.setdefault(f, set()).add(name)
    rows = []
    for (name, typ, sent, pos) in allds:
        g = guard_re(name, typ, sent)
        if g is None:
            continue
        f = ap.enclosing(funcs, pos)
        lo, hi = (f[1], f[2]) if f else (0, len(t))
        hits = []
        for m in g.finditer(t, pos if f else 0, hi):
            ff = ap.enclosing(funcs, m.start())
            if f is not None and ff != f:
                continue
            hits.append((m, ff))
        if not hits:
            continue
        m, ff = hits[0]
        blk = guarded_block(t, m.end())
        asg = assigned(blk)
        if name not in asg and typ != 'ptr':
            # a flag guard whose block sets the flag through a call, or a test-only use: not a lazy init
            if not re.search(r'\b%s\s*=' % re.escape(name), blk):
                continue
        scope = (statics_fn.get(ff, set()) | statics_fn.get(f, set()) | statics_file) if ff else statics_file
        comp = sorted((asg & scope) - {name})
        fs = ff[1] if ff else 0
        locked = bool(LOCK.search(t, fs, m.start()))
        if locked:
            cls = 'LOCKED'
        elif typ == 'ptr' and (PTRSRC.search(blk) or not comp):
            cls = 'PTR'
        elif comp:
            cls = 'COMPANION'
        else:
            cls = 'SIMPLE'
        line = t.count('\n', 0, pos) + 1
        rows.append(dict(file=path, line=line, name=name, typ=typ, cls=cls, fn=(ff[0] if ff else '<file>'),
                         comp=comp, env=bool(re.search(r'getenv|rs64_env|env_cached|ENV', blk))))
    return rows

def files():
    out = []
    for d in DIRS:
        for ext in ('c', 'cpp', 'h', 'hpp', 'mm'):
            out += glob.glob(os.path.join(ROOT, d, '**', '*.' + ext), recursive=True)
    return sorted(set(out))

def load_reviewed():
    p = os.path.join(ROOT, 'tools', 's7374_lazy_static_reviewed.tsv')
    rev = {}
    if os.path.exists(p):
        for ln in open(p):
            if ln.startswith('#') or not ln.strip():
                continue
            f = ln.rstrip('\n').split('\t')
            rev[(f[0], f[1], f[2])] = (f[3], f[4] if len(f) > 4 else '')
    return rev

SELF = r'''
#include <atomic>
static std::atomic<int> a_en{-1};
static const int c_en = -1;
static thread_local int tl_en = -1;
int f_simple() { static int s_en = -1; if (s_en < 0) { s_en = getenv("X") ? 1 : 0; } return s_en; }
int f_comp() { static int c_init = 0; static int c_lim = 0; if (!c_init) { c_init = 1; c_lim = atoi(getenv("Y")); } return c_lim; }
FILE* f_ptr() { static FILE* p_f = nullptr; if (!p_f) p_f = fopen("z", "w"); return p_f; }
int f_lock() { static std::mutex mu; std::lock_guard<std::mutex> lk(mu); static int l_en = -1; if (l_en < 0) l_en = 3; return l_en; }
int f_atomic() { if (a_en < 0) a_en = 1; if (tl_en < 0) tl_en = 2; return c_en; }
'''

def selftest():
    rows = scan('<self>', SELF)
    got = {r['name']: r['cls'] for r in rows}
    want = {'s_en': 'SIMPLE', 'c_init': 'COMPANION', 'p_f': 'PTR', 'l_en': 'LOCKED'}
    ok = got == want
    print('selftest', 'PASS' if ok else 'FAIL', got)
    return 0 if ok else 1

def main():
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    rows = []
    for p in files():
        try:
            t = open(p, errors='replace').read()
        except OSError:
            continue
        rows += scan(os.path.relpath(p, ROOT), t)
    rev = load_reviewed()
    c = Counter(r['cls'] for r in rows)
    print('rows', len(rows), dict(c))
    unrev = 0
    for r in rows:
        if r['cls'] in ('COMPANION', 'PTR'):
            v = rev.get((r['file'], r['fn'], r['name']))
            tag = v[0] if v else 'UNREVIEWED'
            if not v:
                unrev += 1
            if '--all' in sys.argv or not v or '--rows' in sys.argv:
                print('%-10s %-11s %s:%d %s() %s %s comp=%s' % (r['cls'], tag, r['file'], r['line'], r['fn'], r['name'],
                                                               r['typ'], ','.join(r['comp'][:6])))
        elif '--all' in sys.argv:
            print('%-10s %-11s %s:%d %s() %s' % (r['cls'], '-', r['file'], r['line'], r['fn'], r['name']))
    print('unreviewed', unrev)
    if '--check' in sys.argv and (unrev or selftest()):
        sys.exit(1)

if __name__ == '__main__':
    main()
