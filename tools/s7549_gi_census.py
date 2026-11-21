#!/usr/bin/env python3
"""s7549 class GI census: statics injected into the generated guest functions (RecompiledFuncs/funcs_*.c) by
tools/fixup_*.py / tools/apply_*.py that capture a guest-derived value in one call and use it in a later one.

Class GH (s7548) covered src/main.  The residual is the C the fixup/apply scripts paste INTO RecompiledFuncs: a static there
runs inside a guest function, so a guest heap pointer captured on call N and dereferenced on call N+1 reads whatever the heap
put there in between (the s7545 heap-reuse hazard).

Enumerate (comments/strings blanked, positions preserved):
  statics  every non-const, non-float static (function-local at any depth, incl. ({ ... }) statement exprs) and every
           file-scope variable definition (static or global) in funcs_*.c; all comma-separated declarators.
  capture  an assignment / compound assignment / initializer whose RHS is guest-derived: ctx->rN/fN/hi/lo, MEM_*(, TO_PTR(,
           rdram[, or a local tainted by those (fixpoint over the function).  File-scope statics: any function in the file.
  sinks    for a captured static S and every local derived from it (fixpoint):
             addr   S inside the argument list of MEM_*( / TO_PTR( / RS64_*( or an rdram[ / rdram + index  (guest deref)
             reg    S on the RHS of `ctx->rN =` (handed back to the guest, which may deref it)
             store  S on the RHS of `MEM_*(..) =` (stored into guest memory)
             call   S in the argument list of a host function call (rs64_*, g_*; escapes to src/main -- covered by GH
                    for the callee, recorded here so the callee is named)
Classes: H-diag (captured, no addr/reg/store sink: print/compare/count/cache only, call sinks to callees proven diag/value);
  rule classes for rows with addr/reg/store sinks (RULES below, each with a proof regex on the injecting script):
  H-gated (every sink is under a default-off env gate), H-refresh (re-read from live guest state before every use in the
  same call), H-value (the static holds a scalar -- float bits, count, cutoff -- never an address), H-static-target (the
  captured value is a static-image address < heap base 0x80154690), OPEN (default-on addr sink of a captured heap pointer).
  UNCLASSIFIED = sink row with no rule; DRIFT = rule proof regex missing from the injecting script, or rule naming a row that
  no longer exists.
Rows are grouped by (static name, injecting PATCH tag) because the same block is pasted into many functions.
Exit 0 iff 0 OPEN, 0 UNCLASSIFIED, 0 DRIFT.  --controls runs planted / mutated variants.  --dump prints every row.
"""
import os, re, sys, glob, collections
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RF = os.environ.get('RS64_RECOMPILED', os.path.join(os.path.dirname(REPO), 'N64Recomp', 'RecompiledFuncs'))

STRIP_RE = re.compile(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'', re.S)
def strip(s):
    def r(m):
        t = m.group(0)
        if t[0] in '"\'': return t[0] + ' ' * (len(t) - 2) + t[0]
        return re.sub(r'[^\n]', ' ', t)
    return STRIP_RE.sub(r, s)

TYPES = r'(?:unsigned|signed|long|short|int|char|uint\d+_t|int\d+_t|uintptr_t|size_t|gpr|struct\s+\w+|rs64_\w+|\w+_e|\w+_t)'
SDECL = re.compile(r'\bstatic\s+(?:_Thread_local\s+)?(?:volatile\s+)?(const\s+)?(' + TYPES + r'(?:\s+(?:unsigned|long|int|short|char))*)\b')
GDECL = re.compile(r'(?m)^(?:volatile\s+)?(' + TYPES + r'(?:\s+(?:unsigned|long|int|short|char))*)\s+(?=\*?\s*[A-Za-z_]\w*\s*(?:\[|=|;|,))')
GSRC = re.compile(r'ctx->(?:[rf]\d+|hi|lo)\b|\bMEM_\w+\s*\(|\bTO_PTR\s*\(|\brdram\s*\[')
ASSIGN = re.compile(r'(?<![\w.>])([A-Za-z_]\w*)\s*(?:(?:\[[^\]\n;]*\]|\.\w+)\s*)*(=(?!=)|\+=|-=|\|=|&=|\^=)([^;]*)')
IDENT = re.compile(r'\b[A-Za-z_]\w*\b')
FUNC = re.compile(r'(?m)^RECOMP_FUNC[^\n(]*?\b(\w+)\(uint8_t\* rdram, recomp_context\* ctx\)\s*\{')
HEAP_BASE = 0x80154690

def match_close(s, j, o='(', c=')'):
    d = 1; n = len(s)
    while j < n and d:
        ch = s[j]
        if ch == o: d += 1
        elif ch == c: d -= 1
        j += 1
    return j

def declarators(s, p):
    """declarators of the declaration whose type ends at p: list of (name, is_ptr, start)"""
    j = p; n = len(s); d = 0; out = []; cur = p
    while j < n:
        ch = s[j]
        if ch in '([{': d += 1
        elif ch in ')]}':
            if d == 0: break
            d -= 1
        elif ch == ';' and d == 0: break
        elif ch == ',' and d == 0:
            out.append((cur, j)); cur = j + 1
        j += 1
    out.append((cur, j))
    res = []
    for a, b in out:
        m = re.match(r'\s*(\*?)\s*([A-Za-z_]\w*)', s[a:b])
        if m: res.append((m.group(2), bool(m.group(1)), a))
    return res

def top_blocks(s):
    """every top-level { } block that is a function body: (name, open+1, close)"""
    out = []; d = 0; j = 0; n = len(s); start = None
    for m in re.finditer(r'[{}]', s):
        ch = m.group(0); p = m.start()
        if ch == '{':
            if d == 0: start = p
            d += 1
        else:
            d -= 1
            if d == 0 and start is not None:
                head = s[max(0, start - 400):start]
                fm = re.search(r'\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*$', head)
                if fm and fm.group(1) not in ('if', 'for', 'while', 'switch'): out.append((fm.group(1), start + 1, p))
                start = None
            if d < 0: d = 0
    return out

class Unit:
    """one translation unit (funcs_N.c) or an override text"""
    def __init__(self, name, raw):
        self.name = name; self.raw = raw; self.s = strip(raw)
        self.funcs = top_blocks(self.s)
    def tag_at(self, p, lim=None):
        a = max(0, p - 6000) if lim is None else max(lim, p - 6000)
        win = self.raw[a:self.raw.find('\n', p) if self.raw.find('\n', p) > 0 else len(self.raw)]
        tags = re.findall(r'PATCH:\s*(s?\d+[a-z]?(?:\s+[A-Za-z_][\w-]*)?)', win)
        if tags: return tags[-1]
        m = re.findall(r'/\*\s*(s\d{3,5}[a-z]?)\b', win)
        return m[-1] if m else 'untagged'

def _fstart(self, p):
    for f, a, b in self.funcs:
        if a <= p < b: return a
    return None
Unit.fstart = _fstart

def enclosing_open(s, p, lim):
    d = 0; j = p - 1
    while j >= lim:
        ch = s[j]
        if ch == '}': d += 1
        elif ch == '{':
            if d == 0: return j
            d -= 1
        j -= 1
    return lim - 1

def statics_of(u):
    """yield (scope, fname, a, b, name, is_ptr, pos)"""
    spans = [(a, b) for _, a, b in u.funcs]
    def infunc(p):
        for k, (a, b) in enumerate(spans):
            if a <= p < b: return k
        return None
    for m in SDECL.finditer(u.s):
        if m.group(1): continue
        if re.match(r'\s*[A-Za-z_]\w*\s*\(', u.s[m.end():m.end() + 200]) and not re.match(r'\s*\*?\s*\w+\s*(?:\[|=|;|,)', u.s[m.end():m.end() + 200]):
            continue  # function declaration
        k = infunc(m.start())
        for nm, ptr, pos in declarators(u.s, m.end()):
            if k is None: yield ('FILE', None, 0, len(u.s), nm, ptr, pos)
            else:
                fn, a, b = u.funcs[k]
                ba = enclosing_open(u.s, m.start(), a)
                bb = match_close(u.s, ba + 1, '{', '}')
                yield ('FUNC', fn, ba, bb, nm, ptr, pos)
    for m in GDECL.finditer(u.s):
        if infunc(m.start()) is not None: continue
        line = u.s[m.start():u.s.find('\n', m.start())]
        if line.startswith(('extern', 'typedef', 'return')) or '(' in line.split('=')[0]: continue
        for nm, ptr, pos in declarators(u.s, m.end()):
            yield ('FILE', None, 0, len(u.s), nm, ptr, pos)

class FuncIndex:
    def __init__(self, body):
        self.body = body
        self.asg = [(m.group(1), m.start(), m.group(3), set(IDENT.findall(m.group(3))), bool(GSRC.search(m.group(3))))
                    for m in ASSIGN.finditer(body)]
        for m in re.finditer(r'\bmemcpy\s*\(\s*&?\s*(\w+)[^,]*,([^,]*),', body):
            self.asg.append((m.group(1), m.start(), m.group(2), set(IDENT.findall(m.group(2))), bool(GSRC.search(m.group(2)))))
        self._spans = None
        self._taint = None
    def taint(self):
        if self._taint is None:
            T = set()
            for _ in range(8):
                g = False
                for lhs, _, _, ids, gs in self.asg:
                    if lhs not in T and (gs or ids & T): T.add(lhs); g = True
                if not g: break
            self._taint = T
        return self._taint
    def derived(self, seed):
        S = set(seed)
        for _ in range(8):
            g = False
            for lhs, _, _, ids, _ in self.asg:
                if lhs not in S and ids & S: S.add(lhs); g = True
            if not g: break
        return S
    def spans(self):
        if self._spans is None:
            b = self.body; sp = []
            for m in re.finditer(r'\b(MEM_\w+|TO_PTR|RS64_\w+|rs64_\w+|g_\w+)\s*\(', b):
                e = match_close(b, m.end())
                k = 'addr' if not m.group(1).startswith(('rs64_', 'g_')) else 'call:' + m.group(1)
                sp.append((m.end(), e - 1, k, m.start()))
            for m in re.finditer(r'(?<![\w.>])rdram\s*\[', b):
                sp.append((m.end(), match_close(b, m.end(), '[', ']') - 1, 'addr', m.start()))
            for m in re.finditer(r'(?<![\w.>])rdram\s*\+', b):
                e = re.match(r'[^;,)]*', b[m.end():]).end()
                sp.append((m.end(), m.end() + e, 'addr', m.start()))
            self._spans = sp
        return self._spans

def stmt_lhs(body, p):
    a = max(body.rfind(';', 0, p), body.rfind('{', 0, p), body.rfind('}', 0, p)) + 1
    return body[a:p]

def census(units):
    rows = collections.OrderedDict()
    nstat = 0
    for u in units:
        bidx = {}
        def BI(a, b):
            if (a, b) not in bidx: bidx[(a, b)] = FuncIndex(u.s[a:b])
            return bidx[(a, b)]
        stats = list(statics_of(u))
        nstat += len(stats)
        seen = set()
        for st in stats:
            scope, fn, ba, bb, nm, ptr, pos = st
            if scope == 'FILE':
                regs = [(f, a, b) for (f, a, b) in u.funcs if re.search(r'\b' + re.escape(nm) + r'\b', u.s[a:b])]
            else:
                if (nm, ba) in seen: continue
                seen.add((nm, ba)); regs = [(fn, ba, bb)]
            cap = []; sinks = set(); where = []
            for f, a, b in regs:
                X = BI(a, b)
                for lhs, p, rhs, ids, gs in X.asg:
                    if lhs != nm: continue
                    if gs or (ids & X.taint()):
                        cap.append((f, rhs.strip()[:100])); break
            if not cap: continue
            for f, a, b in regs:
                X = BI(a, b); body = X.body
                D = X.derived({nm})
                pat = re.compile(r'(?<![\w.>])(' + '|'.join(map(re.escape, sorted(D))) + r')\b(?!\s*(?:=(?!=)|\+=|-=|\|=|&=|\^=))')
                sp = X.spans()
                for m in pat.finditer(body):
                    p = m.start(); kinds = set()
                    for sa, sb, kd, s0 in sp:
                        if sa <= p < sb: kinds.add(kd)
                    ctxt = body[max(0, p - 70):p + 50]
                    if 'addr' in kinds: sinks.add('addr'); where.append((f, 'addr', ctxt))
                    else:
                        lh = stmt_lhs(body, p)
                        if re.search(r'ctx->[rf]\d+\s*=\s*', lh) and '==' not in lh:
                            sinks.add('reg'); where.append((f, 'reg', ctxt))
                        elif re.search(r'\bMEM_\w+\s*\([^;]*\)\s*=(?!=)', lh):
                            sinks.add('store'); where.append((f, 'store', ctxt))
                    for kd in kinds:
                        if kd.startswith('call:'): sinks.add(kd)
            tag = u.tag_at(pos, None if scope == 'FILE' else u.fstart(pos))
            key = (nm, tag)
            r = rows.setdefault(key, dict(name=nm, tag=tag, ptr=ptr, scope=scope, units=set(), funcs=set(), cap=cap[0],
                                          sinks=set(), where=[], derived=set()))
            r['units'].add(u.name); r['funcs'].add(fn or 'FILE'); r['sinks'] |= sinks; r['where'] += where[:6]
            r['derived'] |= D
    return rows, nstat

# ---------------------------------------------------------------------------------------------------------------- rules
# (name, tag-prefix, class, script, proof regex, reason)
RULES = [
    ('rs64_s7482_b', 's7482', 'H-inflight', 'tools/apply_s6031_far.py', r'rs64_s7482_pend = 1; rs64_s7482_b = base;.*rs64_s7482_pend = 0; \}',
     'set in partitionFramebufferMemory and consumed at L_80001060 of the SAME call; pend cleared unconditionally at the consume block; value is the fb-partition carve, not a heap object'),
    ('s7108_s2', 's7108', 'H-inflight', 'tools/apply_s7108_camwide.py', r'(?=.*s7108_s2 = \(uint32_t\)ctx->r18;)(?=.*uint32_t s2 = s7108_s2)',
     'assigned from live $s2 at 0x8004CE58; the only reader s7108_x is called at 0x8004CF.. later in the same function with no label between (guest itself loads $s2+0x2C next)'),
    ('rs5839_obj', 's5905', 'H-inflight', 'tools/apply_s5835_sphere_probe.py', r'rs5839_obj = \(uint32_t\)ctx->r4;.*if \(rs7441_on\) rs5835_probe',
     'assigned from a0 at intersectSegmentWithObjectSphere entry, read by rs5835_probe called right after in the same call, and only under ROGUESQ_LOG_HITS/TELE_BOLT/G1E_TRIM=0 (default off)'),
    ('og6112', 's6112', 'H-value', 'tools/apply_s6031_far.py', r'getenv\("ROGUESQ_VPW_SCALE"\); kv = \(e && \*e\) \? atof\(e\) : 0\.0;',
     'holds the camera viewport w/h ints (scalars); stores go to live ctx->r17, the cam key sp6112 is compare-only; whole block gated by ROGUESQ_VPW_SCALE (kv 0 = off)'),
    ('s6496_a0', 's6497', 'H-refresh', 'tools/apply_s6496_bin_inputs.py',  # s7739: adopted replay keeps one copy, in the s6497 block
     r's6496_a0 = \(uint32_t\)ctx->r4; for \(int i = 0; i < 15; i\+\+\) \{ uint32_t w = \(uint32_t\)MEM_W\(0, \(int64_t\)\(int32_t\)\(s6496_a0',
     're-assigned from live a0 in the same statement before every deref; later uses are fprintf only'),
    ('org6418', 's6418', 'H-value', 'tools/apply_s6418_farclip.py', r'org6418 = \(uint32_t\)MEM_W\(0, \(int64_t\)\(int32_t\)0x8009DEB4\)',
     'float bits of the far-cutoff constant read from the static image 0x8009DEB4 (< heap base) and written back to the same constant address'),
    ('org6421', 's6421', 'H-value', 'tools/apply_s6418_farclip.py', r'org6421\[i\] = \(uint32_t\)MEM_W\(0, \(int64_t\)\(int32_t\)\(0x8009DE94 \+ 4 \* i\)\)',
     'float bits of the LOD tier table at static 0x8009DE94..A0, written back to the same constant addresses; opt-in ROGUESQ_DD_LODSCALE'),
    ('org7011', 's7011', 'H-value', 'tools/apply_s7011_lodmul.py', r'org7011\[i\] = \(uint32_t\)MEM_W\(0, \(int64_t\)\(int32_t\)\(0x8009DE94 \+ 4 \* i\)\)',
     'float bits of the LOD tier table at static 0x8009DE94..A0, written back to the same constant addresses; gated rs64_s7011_en'),
]

def script_texts():
    T = {}
    for p in glob.glob(os.path.join(REPO, 'tools', 'fixup_*.py')) + glob.glob(os.path.join(REPO, 'tools', 'apply_*.py')):
        T[os.path.relpath(p, REPO)] = open(p, errors='replace').read()
    return T

def classify(rows, rules=None, texts=None):
    rules = RULES if rules is None else rules
    texts = script_texts() if texts is None else texts
    out = []; used = set(); drift = []
    for key, r in rows.items():
        hard = {s for s in r['sinks'] if s in ('addr', 'reg', 'store')}
        if not hard:
            r['cls'] = 'H-diag'; out.append(r); continue
        hit = None
        for i, (nm, tp, cls, scr, rx, why) in enumerate(rules):
            if nm == r['name'] and r['tag'].startswith(tp):
                hit = i; break
        if hit is None:
            r['cls'] = 'UNCLASSIFIED'
        else:
            used.add(hit); nm, tp, cls, scr, rx, why = rules[hit]
            if scr not in texts or not re.search(rx, texts[scr], re.S):
                r['cls'] = 'DRIFT'; r['why'] = 'proof regex missing in ' + scr
            else:
                r['cls'] = cls; r['why'] = why
        out.append(r)
    for i, ru in enumerate(rules):
        if i not in used: drift.append('rule names no row: %s@%s' % (ru[0], ru[1]))
    return out, drift

def load_units(overrides=None):
    us = []
    for p in sorted(glob.glob(os.path.join(RF, 'funcs_*.c'))):
        nm = os.path.basename(p)
        txt = overrides.get(nm) if overrides and nm in overrides else open(p, errors='replace').read()
        us.append(Unit(nm, txt))
    if overrides:
        for nm, txt in overrides.items():
            if not nm.startswith('funcs_'): us.append(Unit(nm, txt))
    return us

def report(out, drift, verbose=False):
    c = collections.Counter(r['cls'] for r in out)
    bad = [r for r in out if r['cls'] in ('OPEN', 'UNCLASSIFIED', 'DRIFT')]
    return c, bad, drift

def main():
    a = sys.argv[1:]
    if '--controls' in a: sys.exit(run_controls())
    units = load_units()
    rows, nstat = census(units)
    out, drift = classify(rows)
    c, bad, drift = report(out, drift)
    print('s7549 GI census: %d static declarators in %d units, %d captured-guest rows (grouped by name+tag)' % (nstat, len(units), len(out)))
    print('classes:', dict(c))
    for r in out:
        if '--dump' in a or r['cls'] not in ('H-diag',):
            print('  %-13s %-28s %-24s sinks=%s funcs=%d cap=%s' % (r['cls'], r['name'], r['tag'], ','.join(sorted(r['sinks'])) or '-',
                                                                 len(r['funcs']), r['cap'][1][:70]))
            if '--where' in a:
                for w in r['where'][:3]: print('        %s %s: %s' % (w[0], w[1], ' '.join(w[2].split())[:150]))
    for d in drift: print('  DRIFT', d)
    rc = 0 if not bad and not drift else 1
    print('rc', rc)
    return rc

CONTROLS = [
    ('planted cross-call heap ptr deref', 'UNCLASSIFIED'),
    ('planted cross-call ptr handed to guest reg', 'UNCLASSIFIED'),
    ('planted 2nd declarator of file-scope static', 'UNCLASSIFIED'),
    ('planted print-only capture', 'H-diag'),
    ('capture inside a comment', 'no-row'),
    ('deleted rule', 'UNCLASSIFIED'),
    ('proof text removed from script', 'DRIFT'),
    ('rule for a vanished row', 'drift-list'),
    ('real tree', 'rc0'),
]
PLANT = {
 'planted cross-call heap ptr deref': ('keep9a', """RECOMP_FUNC void plantA(uint8_t* rdram, recomp_context* ctx) {
    { static uint32_t keep9a; if (ctx->r5 == 1) keep9a = (uint32_t)ctx->r4; else ctx->r2 = MEM_W(0x10, (int64_t)(int32_t)keep9a); }
}
"""),
 'planted cross-call ptr handed to guest reg': ('keep9b', """RECOMP_FUNC void plantB(uint8_t* rdram, recomp_context* ctx) {
    { static uint32_t keep9b; if (ctx->r5) keep9b = (uint32_t)MEM_W(0, ctx->r4); ctx->r2 = (gpr)(int32_t)keep9b; }
}
"""),
 'planted 2nd declarator of file-scope static': ('keep9d', """static uint32_t keep9c, keep9d; /* PATCH: s9999 plant */
RECOMP_FUNC void plantC(uint8_t* rdram, recomp_context* ctx) {
    keep9d = (uint32_t)ctx->r6;
    ctx->r3 = MEM_W(4, keep9d);
}
"""),
 'planted print-only capture': ('keep9e', """RECOMP_FUNC void plantD(uint8_t* rdram, recomp_context* ctx) {
    { static uint32_t keep9e; keep9e = (uint32_t)ctx->r4; fprintf(stderr, "%08x", keep9e); }
}
"""),
 'capture inside a comment': ('keep9f', """RECOMP_FUNC void plantE(uint8_t* rdram, recomp_context* ctx) {
    { static uint32_t keep9f; /* keep9f = (uint32_t)ctx->r4; */ ctx->r2 = MEM_W(0, keep9f); }
}
"""),
}
def run_controls():
    units = load_units(); rows, _ = census(units); texts = script_texts()
    ok = 0; n = 0
    def res(label, got, want):
        nonlocal ok, n
        n += 1; good = got == want; ok += good
        print('  control %-46s want=%-12s got=%-12s %s' % (label, want, got, 'ok' if good else 'FAIL'))
    for label, want in CONTROLS:
        if label in PLANT:
            nm, txt = PLANT[label]
            prow, _ = census([Unit('plant.c', txt)])
            out, _ = classify(prow, rules=[], texts=texts)
            hit = [r for r in out if r['name'] == nm]
            res(label, hit[0]['cls'] if hit else 'no-row', want)
        elif label == 'deleted rule':
            out, _ = classify(rows, rules=RULES[1:], texts=texts)
            hit = [r for r in out if r['name'] == RULES[0][0]]
            res(label, hit[0]['cls'] if hit else 'no-row', want)
        elif label == 'proof text removed from script':
            t2 = dict(texts); t2[RULES[0][3]] = t2[RULES[0][3]].replace('rs64_s7482_pend = 0; }', 'rs64_s7482_pend = 0;')
            out, _ = classify(rows, texts=t2)
            hit = [r for r in out if r['name'] == RULES[0][0]]
            res(label, hit[0]['cls'] if hit else 'no-row', want)
        elif label == 'rule for a vanished row':
            out, drift = classify(rows, rules=RULES + [('gone9z', 's9999', 'H-value', RULES[0][3], 'x', 'stale')], texts=texts)
            res(label, 'drift-list' if any('gone9z' in d for d in drift) else 'none', want)
        elif label == 'real tree':
            out, drift = classify(rows, texts=texts)
            bad = [r for r in out if r['cls'] in ('OPEN', 'UNCLASSIFIED', 'DRIFT')]
            res(label, 'rc0' if not bad and not drift else 'rc1', want)
    print('controls %d/%d' % (ok, n))
    return 0 if ok == n else 1

if __name__ == '__main__':
    sys.exit(main())
