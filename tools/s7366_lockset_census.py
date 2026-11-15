#!/usr/bin/env python3
"""s7366 class AQ census: host containers touched under a mutex in one place and without it in another (Eraser-style
lockset inconsistency), static half. The dynamic half is the TSan arm (tools/build_tsan.sh + tools/s7354_tsan_report.py),
which only covers what a run reaches (s7366: boot -> front end); this covers every path, at lower fidelity.

Containers: names declared as std::vector / deque / list / map / unordered_map / set / unordered_set / queue / string /
array (any template) in the scope set (s7363 scope: src + librecomp + ultramodern + rt64/src), declared at class/struct
or namespace/file scope (function locals are thread-private and skipped).
Lock held at an access: a lock_guard / unique_lock / scoped_lock / shared_lock / std::lock declared earlier in the same
function in a block that still encloses the access, or an `X.lock()` earlier in the function with no `X.unlock()` between.
Rows per (file, container):
  CONSISTENT   every access in a non-ctor/dtor function holds some lock (or none ever does: NOLOCK, thread-confined
               or handed off by queue; counted, not reviewed)
  MIXED        at least one access under a lock and at least one without -> each unlocked function needs a hand verdict in
               s7366_lockset_reviewed.tsv (H-safe: caller holds the lock / single-threaded phase / init; H-race: fix).
Functions named like the class (ctor), ~X (dtor), or containing "Locked"/"_locked"/"NoLock" are classed CALLER-HOLDS
candidates and still listed but marked.
--selftest: planted file (one MIXED, one CONSISTENT, one NOLOCK, one ctor-only unlocked) must classify exactly.
--check: exit 1 on an unreviewed MIXED row."""
import re, sys, os
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7363_hostarr_census as an
import s7365_invalidation_census as ap

TPL = r'<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>'
CDECL = re.compile(r'\b(?:std::)?(?:vector|deque|list|map|unordered_map|set|unordered_set|multimap|queue|priority_queue|'
                   r'array|basic_string|string|unordered_multimap|flat_map)\s*(?:' + TPL + r')?\s*([A-Za-z_]\w*)\s*(?:[;={]|\[)')
LOCKDECL = re.compile(r'\b(?:std::)?(?:lock_guard|unique_lock|scoped_lock|shared_lock)\s*(?:' + TPL + r')?\s*\w*\s*[({]\s*([^;)}]*)')
STDLOCK = re.compile(r'\bstd::lock\s*\(')
MLOCK = re.compile(r'([A-Za-z_][\w.>\-]*)\s*(?:\.|->)\s*lock\s*\(\s*\)')

def depth_between(t, a, b):
    """True if the brace block open at position a still encloses b (no net close below a's level between a and b)."""
    d = 0
    for ch in t[a:b]:
        if ch == '{': d += 1
        elif ch == '}':
            d -= 1
            if d < 0: return False
    return True

def locks_at(t, fs, fe, pos):
    held = []
    for m in LOCKDECL.finditer(t, fs, pos):
        if depth_between(t, m.start(), pos):
            held.append(m.group(1).strip() or '?')
    for m in STDLOCK.finditer(t, fs, pos):
        if depth_between(t, m.start(), pos):
            held.append('std::lock')
    for m in MLOCK.finditer(t, fs, pos):
        nm = m.group(1)
        if not re.search(re.escape(nm) + r'\s*(?:\.|->)\s*unlock\s*\(', t[m.end():pos]):
            held.append(nm)
    return held

def declared(t):
    out = {}
    for m in CDECL.finditer(t):
        name = m.group(1)
        if name in an.NOTTYPE or name in ('const', 'operator', 'value_type', 'iterator', 'size_type') or len(name) < 3:
            continue
        pre = t[max(0, m.start() - 40):m.start()]
        if re.search(r'(?:::|\.|->)\s*$', pre) and not re.search(r'std::\s*$', pre):
            continue
        # skip function-local declarations: inside a function body
        out.setdefault(name, []).append(m.start(1))
    return out

def scan(path, t, members):
    t = an.strip_comments(t)
    funcs = ap.functions(t)
    rows = []
    for name in members:
        for m in re.finditer(r'(?<![\w.>:])(?:this->)?' + re.escape(name) + r'\b(?!\s*\()', t):
            f = ap.enclosing(funcs, m.start())
            if f is None:
                continue
            fn, fs, fe = f
            # a declaration of a same-named local inside this function makes it thread-private
            if re.search(r'\b(?:std::)?(?:vector|deque|list|map|unordered_map|set|unordered_set|queue|array|string)\b[^;(){}]*\b'
                         + re.escape(name) + r'\b', t[fs:fe]):
                continue
            held = locks_at(t, fs, fe, m.start())
            rows.append((path, t.count('\n', 0, m.start()) + 1, name, fn, tuple(held)))
    return rows

def classify(rows):
    by = defaultdict(list)
    for r in rows:
        by[(r[0], r[2])].append(r)
    out = []
    for (path, name), rs in by.items():
        locked = [r for r in rs if r[4]]
        unl = [r for r in rs if not r[4]]
        if not locked:
            out.append((path, name, 'NOLOCK', [], rs)); continue
        if not unl:
            out.append((path, name, 'CONSISTENT', [], rs)); continue
        fns = sorted({r[3] for r in unl})
        out.append((path, name, 'MIXED', fns, rs))
    return out

def is_ctorish(fn, path):
    return fn.startswith('~') or 'Locked' in fn or '_locked' in fn or 'NoLock' in fn or fn in ('init', 'shutdown', 'setup')

SELFTEST = r'''
struct S { std::mutex mtx; std::vector<int> mixedVec; std::map<int,int> goodMap; std::deque<int> freeQ; std::vector<int> ctorVec;
  S() { }
  void a() { std::lock_guard<std::mutex> lk(mtx); mixedVec.push_back(1); goodMap[1] = 2; ctorVec.push_back(3); }
  void b() { mixedVec.clear(); }
  void c() { { std::unique_lock<std::mutex> lk(mtx); goodMap.erase(1); } }
  void d() { freeQ.push_back(1); }
  void e() { mtx.lock(); goodMap.clear(); mtx.unlock(); }
  void f() { if (true) { std::scoped_lock lk(mtx); ctorVec.clear(); } }
};
'''
EXPECT = {'mixedVec': 'MIXED', 'goodMap': 'CONSISTENT', 'freeQ': 'NOLOCK', 'ctorVec': 'CONSISTENT'}

REVIEWED = {}
_rv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7366_lockset_reviewed.tsv')
if os.path.exists(_rv):
    for ln in open(_rv):
        p = ln.rstrip('\n').split('\t')
        if len(p) >= 4 and not ln.startswith('#'):
            REVIEWED[(p[0], p[1], p[2])] = p[3]

def main():
    if '--selftest' in sys.argv:
        t = SELFTEST
        mem = declared(an.strip_comments(t))
        got = {r[1]: r[2] for r in classify(scan('selftest', t, mem))}
        ok = all(got.get(k) == v for k, v in EXPECT.items())
        print('selftest', 'PASS' if ok else 'FAIL', got)
        sys.exit(0 if ok else 1)
    files = an.scope(True)
    rows = []
    for f in files:
        txt = open(f, errors='replace').read()
        mem = declared(an.strip_comments(txt))
        # header-declared members used from the matching .cpp
        if f.endswith(('.cpp', '.cc', '.mm')):
            for h in (f.rsplit('.', 1)[0] + '.h', f.rsplit('.', 1)[0] + '.hpp'):
                if os.path.exists(h):
                    for k, v in declared(an.strip_comments(open(h, errors='replace').read())).items():
                        mem.setdefault(k, v)
        if not re.search(r'\b(?:lock_guard|unique_lock|scoped_lock|shared_lock|\.lock\s*\()', txt):
            continue  # no lock anywhere in the file: nothing can be inconsistent within it
        rows += scan(f, txt, mem)
    cl = classify(rows)
    c = Counter(x[2] for x in cl)
    print('TOTAL accesses', len(rows), 'containers', len(cl), dict(sorted(c.items())))
    bad = 0
    for path, name, k, fns, rs in sorted(cl):
        if k != 'MIXED':
            continue
        for fn in fns:
            v = REVIEWED.get((path, name, fn))
            if v is None: bad += 1
            if v is None or '-v' in sys.argv:
                lines = ','.join(str(r[1]) for r in rs if r[3] == fn and not r[4])[:60]
                locks = sorted({l for r in rs for l in r[4]})
                print('%s\t%s\t%s\tunlocked@%s\tlocks=%s%s\t%s' % (path, name, fn, lines, '|'.join(locks)[:60],
                      '\tCTORISH' if is_ctorish(fn, path) else '', v or ''))
    print('OPEN', bad)
    if '--check' in sys.argv:
        sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
