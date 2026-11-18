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

def declared(t, funcs=None):
    """name -> [scope]; scope None = class/namespace/file scope, else (body_start, body_end) of the function that declares it
    (s7561: a function-local container, static or not, is only visible inside its own function, so a same-named variable
    elsewhere is not it)."""
    if funcs is None:
        funcs = ap.functions(t)
    out = {}
    for m in CDECL.finditer(t):
        name = m.group(1)
        if name in an.NOTTYPE or name in ('const', 'operator', 'value_type', 'iterator', 'size_type') or len(name) < 3:
            continue
        pre = t[max(0, m.start() - 40):m.start()]
        if re.search(r'(?:::|\.|->)\s*$', pre) and not re.search(r'std::\s*$', pre):
            continue
        f = ap.enclosing(funcs, m.start(1))
        out.setdefault(name, []).append(None if f is None else (f[1], f[2]))
    return out

NOTDECL = {'return', 'case', 'else', 'delete', 'throw', 'goto', 'new', 'co_return', 'co_yield', 'sizeof', 'typename', 'using',
           'do', 'and', 'or', 'not', 'xor', 'bitand', 'bitor', 'template', 'operator', 'default', 'public', 'private', 'protected'}
TYPEISH = re.compile(r'(?:::|<|_t$|^[A-Z]|^(?:auto|void|bool|char|short|int|long|float|double|unsigned|signed)$)')

def params_of(t, fs):
    """parameter list text of the function whose body starts at fs"""
    for m in ap.FUNC.finditer(t, max(0, fs - 2000), fs):
        if m.end() == fs:
            return m.group(2)
    return ''

def shadowed(t, fs, fe, name):
    """s7561: True if the function's parameter list or body declares a variable called `name` (any type)"""
    n = re.escape(name)
    for prm in re.split(r',(?![^<]*>)', params_of(t, fs)):
        prm = prm.split('=')[0].strip()
        mm = re.search(r'([A-Za-z_]\w*)\s*(?:\[[^\]]*\]\s*)*$', prm)
        if mm and mm.group(1) == name and re.search(r'[\w>*&][\s*&]+(?:const\s+)?' + n + r'\b', prm):
            return True
    body = t[fs - 1:fe]
    for m in re.finditer(r'[;{}(,]\s*(?:(?:const|static|volatile|constexpr|thread_local|register|struct)\s+)*'
                         r'([A-Za-z_][\w:]*(?:\s*<[\w\s:,*]*(?:<[\w\s:,*]*>[\w\s:,*]*)*>)?)(\s*[*&]+\s*|\s+)(?:const\s+)?' + n + r'\s*(?=[=;,\[{(:)])', body):
        ty, sep = m.group(1), m.group(2)
        if ty in NOTDECL:
            continue
        if sep.strip() and not TYPEISH.search(ty):
            continue   # `a * name` / `a & name` is an expression unless `a` looks like a type
        return True
    return False

def scan(path, t, members):
    t = an.strip_comments(t)
    funcs = ap.functions(t)
    rows = []
    for name, scopes in members.items():
        glob_ = None in scopes
        local = [sc for sc in scopes if sc is not None]
        shadow = {}
        for m in re.finditer(r'(?<![\w.>:])(?:this->)?' + re.escape(name) + r'\b(?!\s*\()', t):
            f = ap.enclosing(funcs, m.start())
            if f is None:
                continue
            fn, fs, fe = f
            # inside a function that declares a local container of this name: thread-private, skipped as before s7561
            # (gap kept on purpose: a static local, or a local captured by a thread lambda, is not checked here).
            # Elsewhere it can only be the class/file-scope container, and not even that if this function (or its
            # parameter list) declares its own variable of the name.
            if any(s <= m.start() <= e for s, e in local) or not glob_:
                continue
            if fs not in shadow:
                shadow[fs] = shadowed(t, fs, fe, name)
            if shadow[fs]:
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
// s7561 scope cases: names declared as a container only locally / in another function, parameters and locals that shadow a
// file-scope container, and a real unlocked access beside a same-name local elsewhere.
static std::mutex gm; static std::vector<int> shadowVec; static std::vector<int> realVec; static std::vector<int> trapVec;
void g1() { std::lock_guard<std::mutex> lk(gm); shadowVec.push_back(1); realVec.push_back(1); trapVec.push_back(1); }
void g2(uint32_t shadowVec) { int x = shadowVec + 1; }
void g3() { const uint32_t* shadowVec = nullptr; (void)shadowVec; }
void g4() { std::string realVec = "x"; (void)realVec; }
void g5() { realVec.clear(); }
void g6(int a, int b) { if (a < 0 || b > trapVec[0]) trapVec.clear(); }
void h1() { std::lock_guard<std::mutex> lk(gm); std::vector<int> onlyLocal; onlyLocal.push_back(1); }
void h2(int onlyLocal) { int y = onlyLocal; }
'''
EXPECT = {'mixedVec': 'MIXED', 'goodMap': 'CONSISTENT', 'freeQ': 'NOLOCK', 'ctorVec': 'CONSISTENT',
          'shadowVec': 'CONSISTENT', 'realVec': 'MIXED', 'trapVec': 'MIXED'}
EXPECT_ABSENT = ('onlyLocal',)   # s7561: a function-local container never pairs with a same-name variable elsewhere

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
        ok = all(got.get(k) == v for k, v in EXPECT.items()) and not any(k in got for k in EXPECT_ABSENT)
        fns = {r[3] for r in scan('selftest', t, mem) if r[2] == 'realVec' and not r[4]}
        ok = ok and fns == {'g5'}   # g4's local string is not the global; g5's unlocked clear is
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
                        if None in v and None not in mem.get(k, []):
                            mem.setdefault(k, []).append(None)   # s7561: header locals are not visible in the .cpp
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
