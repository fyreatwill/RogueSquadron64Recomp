#!/usr/bin/env python3
"""s7365 class AP census: references / pointers / iterators / indices captured from a runtime-sized host container
(std::vector / deque / string, the s7364 collect() set) and used after a mutation of the SAME container that can
invalidate them.

Capture kinds (inside one function):
  REF   T &x = C[i] / C.back() / C.front() / C.at(i)
  PTR   T *p = C.data() / &C[i] / &C.back()        (declaration or plain assignment)
  ITER  auto it = C.begin() / end() / find() / std::find(C.begin() ...)
  IDX   i = C.size()                               (only shrinking mutations invalidate an index)
  RFOR  for (x : C) { ... C.mutate ... }           (the range-for's hidden iterator)
Mutation of C: C.push_back/emplace_back/resize/clear/erase/insert/assign/pop_back/swap/reserve/shrink_to_fit/emplace/append,
`C = ...`, std::swap(C, ..), or a call to a same-file function whose body mutates a container of that name (one level).

Row classes:
  NOMUT      no mutation of C between the capture and the last use of the captured name in its scope
  DEADAFTER  a mutation exists but the name is never used after it (nor inside a loop that re-runs the use)
  REFRESHED  the name is re-assigned between the mutation and its next use (incl. it = C.erase(it))
  GROWONLY   IDX capture and every mutation before the use only appends (push_back/emplace_back/append/resize-up/insert at end)
  RESERVED   a dominating C.reserve(...) earlier in the function (needs a capacity verdict, so it is a B-class row)
  B / B-LOOP / B-CALL   used after an invalidating mutation (B-LOOP: mutation and use share a loop that began after the
             capture; B-CALL: the mutation is a call to a same-file mutator). Every B* / RESERVED row needs a hand verdict
             in s7365_invalidation_reviewed.tsv.
Part 2 (--members): member index fields used as C[obj.fieldIndex] where C is cleared/resized in some function F of the
scope set and the field is not assigned in F: MEMBER-B rows (the s7364 FULLSYNC drawCall.tileIndex shape); MEMBER-RESET
when F also assigns the field.
`--check` exits 1 on an unreviewed B. `--selftest` runs planted rows of every class.
"""
import re, sys, os, glob
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7363_hostarr_census as an
import s7364_heapbuf_census as ao

MUTS = ('push_back', 'emplace_back', 'resize', 'clear', 'erase', 'insert', 'assign', 'pop_back', 'swap', 'reserve',
        'shrink_to_fit', 'emplace', 'append', 'pop_front', 'push_front', 'emplace_front')
GROW = ('push_back', 'emplace_back', 'append', 'reserve', 'emplace', 'push_front', 'emplace_front')
KW = {'if', 'for', 'while', 'switch', 'return', 'sizeof', 'catch', 'defined', 'static_assert', 'decltype', 'alignof'}
FUNC = re.compile(r'\b([A-Za-z_]\w*)\s*\(([^;{}()]*(?:\([^;{}()]*\)[^;{}()]*)*)\)\s*(?:const\s*)?(?:noexcept\s*)?(?:override\s*)?'
                  r'(?::[^;{]*)?\{')

def functions(t):
    """list of (name, body_start, body_end) for function-like bodies"""
    out = []
    for m in FUNC.finditer(t):
        if m.group(1) in KW or m.group(1) in an.NOTTYPE:
            continue
        b = m.end()
        out.append((m.group(1), b, an.block_end(t, b)))
    return out

def enclosing(funcs, pos):
    best = None
    for (n, s, e) in funcs:
        if s <= pos <= e and (best is None or s > best[1]):
            best = (n, s, e)
    return best

def cont_re(name):
    return r'(?<![\w])(?:(?:[A-Za-z_]\w*|\])\s*(?:\.|->)\s*)*%s' % re.escape(name)

def mut_sites(t, name, lo, hi, mutfuncs):
    """[(pos, stmt_end, op)] mutations of container `name` in t[lo:hi]"""
    out = []
    n = re.escape(name)
    for m in re.finditer(r'(?<![\w])%s\s*(?:\.|->)\s*(%s)\s*\(' % (n, '|'.join(MUTS)), t[lo:hi]):
        p = lo + m.start(); out.append((p, an.stmt_end(t, p), m.group(1)))
    for m in re.finditer(r'(?<![\w.>])%s\s*=(?!=)' % n, t[lo:hi]):
        p = lo + m.start(); out.append((p, an.stmt_end(t, p), 'assign='))
    for m in re.finditer(r'(?<![\w.>])(?:(?:[A-Za-z_]\w*)\s*(?:\.|->)\s*)+%s\s*=(?!=)' % n, t[lo:hi]):
        p = lo + m.start(); out.append((p, an.stmt_end(t, p), 'assign='))
    for m in re.finditer(r'\bstd::swap\s*\(\s*[^;]*\b%s\b' % n, t[lo:hi]):
        p = lo + m.start(); out.append((p, an.stmt_end(t, p), 'swap'))
    for fn, cs in mutfuncs.items():
        if name not in cs:
            continue
        for m in re.finditer(r'(?<![\w.>:~])%s\s*\(' % re.escape(fn), t[lo:hi]):
            p = lo + m.start(); out.append((p, an.stmt_end(t, p), 'call:' + fn))
    return sorted(set(out))

def body_end(t, k):
    """end of the statement at k, treating a brace-less if/for/while body as one statement"""
    while k < len(t) and t[k] in ' \t\n':
        k += 1
    if t[k:k + 1] == '{':
        return an.block_end(t, k + 1)
    m = re.match(r'(if|for|while|switch)\s*\(', t[k:k + 12])
    if m:
        _, j = an.take_br(t, k + m.end())
        e = body_end(t, j + 1)
        em = re.match(r'\s*\}?\s*else\b', t[e + 1:e + 20]) if m.group(1) == 'if' else None
        if em:
            return body_end(t, e + 1 + em.end())
        return e
    return an.stmt_end(t, k)

LOOPHDR = re.compile(r'\b(for|while)\s*\(|\bdo\s*\{')

def loops_in(t, lo, hi):
    out = []
    for m in LOOPHDR.finditer(t, lo, hi):
        if m.group(0).startswith('do'):
            b = m.end(); out.append((m.start(), b, an.block_end(t, b))); continue
        _, j = an.take_br(t, m.end())
        k = j + 1
        while k < len(t) and t[k] in ' \t\n':
            k += 1
        if k < len(t) and t[k] == '{':
            out.append((m.start(), k + 1, an.block_end(t, k + 1)))
        else:
            out.append((m.start(), k, an.stmt_end(t, k)))
    return out

CAPS = None
def capture_res(name):
    c = cont_re(name)
    return [
        ('RFOR', re.compile(r'\bfor\s*\(\s*[^;()]*?[\w&*>\]]\s*:\s*\*?(%s)\s*\)' % c)),
        ('REF', re.compile(r'(?:\bauto|[\w:>]+)\s*(?:const\s*)?&\s*([A-Za-z_]\w*)\s*=\s*(%s)\s*(?:\[|(?:\.|->)\s*(?:back|front|at)\s*\()' % c)),
        ('PTR', re.compile(r'(?:\bauto|[\w:>]+)\s*(?:const\s*)?\*\s*(?:const\s*)?([A-Za-z_]\w*)\s*=\s*(?:\([^()]*\)\s*|(?:reinterpret|static)_cast\s*<[^<>]*>\s*\(\s*)?&?\s*(%s)\s*(?:(?:\.|->)\s*(?:data|back|front)\s*\(|\[)' % c)),
        ('PTR', re.compile(r'(?:^|[;{}(,]\s*)([A-Za-z_]\w*)\s*=(?!=)\s*(?:\([^()]*\)\s*|(?:reinterpret|static)_cast\s*<[^<>]*>\s*\(\s*)?(?:&\s*(%s)\s*\[|(%s)\s*(?:\.|->)\s*data\s*\()' % (c, c), re.M)),
        ('ITER', re.compile(r'(?:\bauto|[\w:>]*iterator)\s+([A-Za-z_]\w*)\s*=\s*(?:std::(?:find|find_if|lower_bound|upper_bound|remove_if)\s*\(\s*)?(%s)\s*(?:\.|->)\s*(?:c?begin|c?end|r?begin|find|lower_bound|upper_bound)\s*\(' % c)),
        ('IDX', re.compile(r'(?:\b(?:auto|size_t|u?int\d*_t|int|unsigned|uint)\s+)?([A-Za-z_]\w*)\s*=(?!=)\s*(?:\([\w\s]+\)\s*|static_cast\s*<[^<>]*>\s*\(\s*)?(%s)\s*(?:\.|->)\s*size\s*\(\s*\)\s*[;)]' % c)),
    ]

def mutator_funcs(t, funcs, names):
    """same-file function name -> set of container names it mutates directly"""
    out = defaultdict(set)
    ns = set(names)
    rx = re.compile(r'(?<![\w])([A-Za-z_]\w*)\s*(?:(?:\.|->)\s*(?:%s)\s*\(|=(?!=))' % '|'.join(MUTS))
    for (fn, s, e) in funcs:
        for m in rx.finditer(t, s, e):
            if m.group(1) in ns:
                out[fn].add(m.group(1))
    return out

def classify(t, kind, var, name, cpos, cend, scope_end, fbody, mutfuncs):
    fs, fe = fbody
    lo = cend; hi = scope_end
    uses = [m.start() for m in re.finditer(r'(?<![\w.>])%s\b' % re.escape(var), t[lo:hi])] if var else []
    uses = [lo + u for u in uses]
    if kind == 'RFOR':
        muts = mut_sites(t, name, lo, hi, mutfuncs)
        muts = [x for x in muts if not x[2].startswith('call:') or True]
        if not muts:
            return 'NOMUT', ''
        p, se, op = muts[0]
        # a mutation followed at once by break/return leaves the loop before the iterator is used again
        tail = t[se + 1:se + 60].lstrip()
        if re.match(r'(?:break|return|goto|throw)\b', tail):
            return 'DEADAFTER', op + '+exit'
        return ('B-CALL' if op.startswith('call:') else 'B'), op
    muts = mut_sites(t, name, lo, hi, mutfuncs)
    if kind == 'IDX':
        shrink = [x for x in muts if x[2] not in GROW and not (x[2] == 'resize')]
    else:
        shrink = muts
    if not uses:
        return 'NOMUT', 'unused'
    last = max(uses)
    loops = loops_in(t, fs, fe)
    def inloop(x):
        return any(ls > cpos and bs <= x[0] <= be and any(bs <= u <= be for u in uses) for (ls, bs, be) in loops)
    rel = [x for x in shrink if x[0] < last or inloop(x)]
    if not rel:
        if kind == 'IDX' and [x for x in muts if x[0] < last]:
            return 'GROWONLY', ','.join(sorted({x[2] for x in muts}))
        return 'NOMUT', ''
    refreshed = False
    for (p, se, op) in rel:
        after = [u for u in uses if u > se]
        # a use inside the mutating statement (e.g. it = C.erase(it)) that also re-assigns var refreshes it
        stmt = t[p:se]
        if re.search(r'(?<![\w.>])%s\s*=(?!=)' % re.escape(var), t[t.rfind(';', 0, p) + 1:se]) and kind != 'REF':
            refreshed = True
            continue
        for (ls, bs, be) in loops:
            if ls > cpos and bs <= p <= be and any(bs <= u <= be for u in uses):
                return ('B-CALL' if op.startswith('call:') else 'B-LOOP'), op
        if not after:
            continue
        nxt = min(after)
        if kind != 'REF' and re.search(r'(?<![\w.>])%s\s*=(?!=)' % re.escape(var), t[se:nxt + len(var) + 3]):
            # only a refresh if the assignment comes at/ before the next use
            am = re.search(r'(?<![\w.>])%s\s*=(?!=)' % re.escape(var), t[se:nxt + len(var) + 3])
            if se + am.start() <= nxt:
                refreshed = True
                continue
        if kind in ('PTR', 'REF', 'ITER') and op in GROW and op != 'reserve' and re.search(r'\b%s\s*(?:\.|->)\s*reserve\s*\(' % re.escape(name), t[fs:cpos]):
            return 'RESERVED', op
        return ('B-CALL' if op.startswith('call:') else 'B'), op
    if refreshed or any(re.search(r'(?<![\w.>])%s\s*=(?!=)' % re.escape(var), t[x[1]:last + 1]) for x in rel):
        return 'REFRESHED', ''
    return 'DEADAFTER', ','.join(sorted({x[2] for x in rel}))

GMEM = set()   # container member names declared in any header of the scope set
def scan(path, text, base_consts):
    t = an.strip_comments(text)
    consts = an.consts_of(t, base_consts)
    bufs = {k: v for k, v in ao.collect(t, consts).items() if any(kd == 'VEC' for (_, _, kd, _, _) in v)}
    words = set(re.findall(r'[A-Za-z_]\w*', t))
    for nm in GMEM & words:
        bufs.setdefault(nm, [(0, len(t), 'VEC', None, True)])
    bufs = {k: v for k, v in bufs.items() if k in words}
    rows = []
    if not bufs:
        return rows
    funcs = functions(t)
    mutf = mutator_funcs(t, funcs, list(bufs))
    for name in sorted(bufs):
        if not re.search(r'(?<![\w])%s\s*(?:\[|(?:\.|->)\s*(?:data|back|front|at|begin|end|cbegin|rbegin|find|lower_bound|upper_bound|size)\s*\(|\))' % re.escape(name), t):
            continue
        for kind, rx in capture_res(name):
            for m in rx.finditer(t):
                f = enclosing(funcs, m.start())
                if f is None:
                    continue
                if kind == 'RFOR':
                    var = None
                    _, j = an.take_br(t, t.find('(', m.start()) + 1)
                    k = j + 1
                    while k < len(t) and t[k] in ' \t\n':
                        k += 1
                    cend = k + 1 if t[k:k + 1] == '{' else k
                    se = body_end(t, k)
                    others = {fn: cs for fn, cs in mutf.items() if fn != f[0]}
                    cls, why = classify(t, kind, None, name, m.start(), cend, se, (f[1], f[2]), others)
                else:
                    var = m.group(1)
                    if var in KW or var in ('auto', 'const', name):
                        continue
                    cend = an.stmt_end(t, m.start())
                    se = an.block_end(t, m.start() + m.group(0).find(var))
                    if kind in ('PTR', 'ITER', 'IDX') and not re.match(r'\s*(?:\bauto|[\w:>]+)\s*(?:const\s*)?[*&]?\s*(?:const\s*)?\s*' + re.escape(var), m.group(0).lstrip(';{}(, \t\n')):
                        se = f[2]   # plain assignment to an outer variable: its life is the rest of the function
                    if re.search(r'\bfor\s*\(\s*$', t[max(0, m.start() - 40):m.start()]):
                        _, j = an.take_br(t, t.rfind('(', 0, m.start()) + 1)
                        se = an.stmt_end(t, j + 1)   # a for-init capture lives for the loop
                    if se > f[2]:
                        se = f[2]
                    others = {fn: cs for fn, cs in mutf.items() if fn != f[0]}
                    cls, why = classify(t, kind, var, name, m.start(), cend, se, (f[1], f[2]), others)
                line = t.count('\n', 0, m.start()) + 1
                rows.append((path, line, name, kind, var or '-', f[0], cls, why))
    # dedupe (two PTR regexes can hit the same statement)
    seen = set(); out = []
    for r in rows:
        k = (r[1], r[2], r[4])
        if k in seen:
            continue
        seen.add(k); out.append(r)
    return out

# ---------------- part 2: member index fields into containers cleared elsewhere ----------------
IDXFIELD = r'(?:[A-Za-z_]\w*(?:Index|Idx|Cursor|Start|Offset|Count|Base|Pos|index|start|cursor))'
def members(files):
    texts = {f: an.strip_comments(open(f, errors='replace').read()) for f in files}
    clears = defaultdict(list)   # container -> [(file, func, body text)]
    for f, t in texts.items():
        for (fn, s, e) in functions(t):
            for m in re.finditer(r'(?<![\w])([A-Za-z_]\w*)\s*(?:\.|->)\s*(clear|resize|assign|erase)\s*\(', t[s:e]):
                clears[m.group(1)].append((f, fn, s, e))
    rows = []
    sub = re.compile(r'(?<![\w])([A-Za-z_]\w*)\s*\[\s*((?:[A-Za-z_]\w*(?:\.|->))+(%s))\s*(?:[+-]\s*\w+\s*)?\]' % IDXFIELD)
    for f, t in texts.items():
        for m in sub.finditer(t):
            c, expr, fld = m.group(1), m.group(2), m.group(3)
            if c not in clears or len(c) < 3:
                continue
            reset = []; noreset = []
            for (cf, cfn, s, e) in clears[c]:
                body = texts[cf][s:e]
                if re.search(r'\b%s\s*=(?!=)' % re.escape(fld), body):
                    reset.append(cfn)
                else:
                    noreset.append('%s:%s' % (os.path.basename(cf), cfn))
            line = t.count('\n', 0, m.start()) + 1
            cls = 'MEMBER-RESET' if not noreset else 'MEMBER-B'
            rows.append((f, line, c, 'MEMBER', expr, ','.join(sorted(set(noreset)))[:90] or '-', cls, ','.join(sorted(set(reset)))[:60]))
    seen = set(); out = []
    for r in rows:
        k = (r[0], r[2], r[4])
        if k in seen:
            continue
        seen.add(k); out.append(r)
    return out

SELFTEST = r'''
#include <vector>
struct W { std::vector<int> v; std::vector<int> calls; void grow(); };
void W::grow() { calls.push_back(1); }
void a(std::vector<int> &unused) {
    std::vector<int> v;
    int &r = v[0];
    v.push_back(1);
    use(r);
}
void b() {
    std::vector<int> v;
    v.reserve(16);
    int *p = v.data();
    v.push_back(2);
    use(p);
}
void c() {
    std::vector<int> v;
    for (auto it = v.begin(); it != v.end(); ) {
        if (*it) it = v.erase(it); else ++it;
    }
}
void d() {
    std::vector<int> v;
    auto it = v.begin();
    v.erase(it);
    use(*it);
}
void e() {
    std::vector<int> v;
    size_t idx = v.size();
    v.push_back(3);
    use(v[idx]);
}
void f() {
    std::vector<int> v;
    size_t idx = v.size();
    v.clear();
    use(v[idx]);
}
void g() {
    std::vector<int> v;
    int &r = v[0];
    use(r);
    v.clear();
}
void h() {
    std::vector<int> v;
    for (int x : v) { v.push_back(x); }
}
void i2() {
    std::vector<int> v;
    for (int x : v) { if (x) { v.erase(v.begin()); break; } }
}
void j(W &w) {
    std::vector<int> calls;
    int *p = calls.data();
    for (int k = 0; k < 4; k++) { use(p[k]); calls.push_back(k); }
}
void k2() {
    std::vector<int> v;
    int *p = v.data();
    v.resize(8);
    p = v.data();
    use(p);
}
void W2() {
    std::vector<int> calls;
    int &r = calls[0];
    grow();
    use(r);
}
'''
EXPECT = ['B', 'RESERVED', 'REFRESHED', 'B', 'GROWONLY', 'B', 'NOMUT', 'B', 'DEADAFTER', 'B-LOOP', 'REFRESHED', 'NOMUT', 'B-CALL']

REVIEWED = {}
_rv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7365_invalidation_reviewed.tsv')
if os.path.exists(_rv):
    for _l in open(_rv):
        if _l.startswith('#') or not _l.strip():
            continue
        _f = _l.rstrip('\n').split('\t')
        if len(_f) >= 5:
            REVIEWED[(_f[0], _f[1], _f[2], _f[3])] = _f[4]

def key(r):
    return (r[0], r[2], r[4], r[5] if r[3] != 'MEMBER' else 'MEMBER')

def is_open(r):
    return r[6].startswith('B') or r[6] in ('RESERVED', 'MEMBER-B')

def main():
    if '--selftest' in sys.argv:
        rows = scan('selftest', SELFTEST, {})
        order = sorted(rows, key=lambda r: r[1])
        got = [r[6] for r in order]
        ok = got == EXPECT
        print('selftest', 'PASS' if ok else 'FAIL', got)
        if not ok:
            for r in order:
                print('  ', r)
        sys.exit(0 if ok else 1)
    files = an.scope(True)
    if '--files' in sys.argv:
        files = sys.argv[sys.argv.index('--files') + 1].split(',')
    for h in files:
        if h.endswith(('.h', '.hpp')):
            ht = an.strip_comments(open(h, errors='replace').read())
            for k, v in ao.collect(ht, {}).items():
                if any(kd == 'VEC' and mem for (_, _, kd, _, mem) in v) and len(k) > 2:
                    GMEM.add(k)
    rows = []
    for f in files:
        rows += scan(f, open(f, errors='replace').read(), {})
    mrows = members([f for f in files if '/rt64/src/hle/' in f or f.startswith('src/') or '/librecomp/' in f
                     or '/ultramodern/' in f or '/rt64/src/' in f])
    allr = rows + mrows
    c = Counter(r[6] for r in allr)
    print('TOTAL', len(rows), 'captures +', len(mrows), 'member rows', dict(sorted(c.items())))
    bad = 0; keys = set()
    for r in allr:
        if is_open(r):
            v = REVIEWED.get(key(r))
            if v is None:
                bad += 1; keys.add(key(r))
            if (v is None and '-q' not in sys.argv) or '-v' in sys.argv:
                print('%s:%d %s %s %s fn=%s %s %s %s' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], v or ''))
    print('OPEN', bad, 'keys', len(keys))
    if '--emit-open' in sys.argv:
        with open(sys.argv[sys.argv.index('--emit-open') + 1], 'w') as o:
            seen = set()
            for r in allr:
                k = key(r)
                if is_open(r) and REVIEWED.get(k) is None and k not in seen:
                    seen.add(k)
                    o.write('%s\t%s\t%s\t%s\t%s:%d %s %s %s\n' % (k + (r[6], r[1], r[3], r[7], r[5] if r[3] == 'MEMBER' else '')))
    if '--check' in sys.argv:
        sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
