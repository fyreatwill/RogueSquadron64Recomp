#!/usr/bin/env python3
"""s7421 class CD: classify every function whose machine code differs between the live RecompiledFuncs tree and a regen
tree (tools/regen_verify.sh compare.json), so a live-only hand edit that no fixup reproduces (LOST: dies at the next regen)
cannot hide among expected differences.

Per differing / one-sided function the C text of both trees is split at top level (brace-aware, strings/comments skipped),
comments are dropped, whitespace collapsed, and the two statement lists diffed:
  CODEGEN   normalized text identical: the object differs only through file context (a static helper or macro elsewhere in
            the file, inlining) - the cause is reported as the file-level delta, which is classified on its own
  ENVDIAG   every live-only / regen-only statement is diagnostic: gated on an env/diag flag, a logging/print call, a
            rs64 counter/note/watch helper, or a known opt-in chain (docs/REGEN-VERIFY.md "What a regen loses")
  GUEST     the differing statements are generated guest code (N64Recomp output: sizing / data_gap / func_sizes.txt)
  LOST      any other live-only statement: a hand edit with no fixup
  REGENONLY any other regen-only statement (a fixup applies something the live tree lacks: live is stale)
File-level (outside functions) deltas are classified the same way, keyed by file.
usage: s7421_regen_drift.py <live dir> <regen dir> <compare.json> [--baseline old.json] [--json out] [--control] [--no-accept]
Reviewed env-gated LOST/REORDER rows are listed in tools/s7421_regen_accept.tsv (exit code ignores them).
--control plants a one-line non-diag statement into a copy of one live function and requires LOST for it (exit 3 if not).
  SLOTPERM  (s7559) the only differences are the counter-slot index of s7487 lwl/lwr wraps (RS64_S7487_LWX(pc, idx, ...)):
            same sites, same pcs, numbered in a different order (apply_s7487 continues the index for sites a later step adds,
            so live numbers them in apply order and a replay in file order). The host keys every report on the pc it stores
            with the slot (upstream_compat.cpp s_s7487_site), so the permutation changes no behaviour and no report.
--control also renumbers one RS64_S7487_LWX slot (must be SLOTPERM) and changes one wrap's pc (must not be).
Exit: 0 no LOST, 1 LOST present, 3 control failed."""
import difflib, json, os, re, shutil, sys, tempfile

HDR = re.compile(r'^(?:__attribute__\(\(weak\)\) )?(?:static |extern )?(?:inline )?(?:RECOMP_FUNC )?[\w\s\*]*?\b(\w+)\s*\(')

def strip(src):
    """drop comments, keep strings as '"S"' (lines preserved)."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if src.startswith('/*', i):
            j = src.find('*/', i + 2); j = n if j < 0 else j + 2
            out.append('\n' * src.count('\n', i, j)); i = j
        elif src.startswith('//', i):
            j = src.find('\n', i); i = n if j < 0 else j
        elif c in '"\'':
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == '\\' else 1
            out.append(src[i:j + 1]); i = j + 1
        else:
            out.append(c); i += 1
    return ''.join(out)

def stmts(s):
    """split one source line into ';'-terminated statements (not inside parens / strings)."""
    out, d, q, b = [], 0, None, ''
    for i, ch in enumerate(s):
        b += ch
        if q:
            if ch == q and s[i - 1] != '\\': q = None
        elif ch in '"\'': q = ch
        elif ch == '(': d += 1
        elif ch == ')': d -= 1
        elif ch in ';{}' and d == 0:
            if b.strip() not in ('', ';'): out.append(b.strip())
            b = ''
    if b.strip(): out.append(b.strip())
    return out

def split(path):
    """-> {name: [normalized statement lines]}, plus '<file>' for top-level text outside function bodies."""
    lines = strip(open(path, errors='replace').read()).split('\n')
    funcs, top, depth, cur, body, pend, opened = {}, [], 0, None, [], None, False
    for ln in lines:
        s = ' '.join(ln.split())
        if depth == 0 and cur is None:
            m = HDR.match(s) if s and not s.startswith('#') and not s.startswith(('typedef', 'struct', 'enum', 'union')) and not s.endswith(';') else None
            if m and '{' in s:
                cur, body, opened = m.group(1), stmts(s), False
            elif m:
                pend = m.group(1)
            elif pend and s.startswith('{'):
                cur, body, pend, opened = pend, [], None, False
            elif s:
                top.extend(stmts(s)); pend = None
        elif cur is not None and s:
            body.extend(stmts(s))
        for ch in re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', '', ln):
            if ch == '{': depth += 1; opened = True
            elif ch == '}': depth -= 1
        if cur is not None and opened and depth == 0:
            k = cur
            while k in funcs: k += "'"
            funcs[k] = body; cur = None
    funcs['<file>'] = top
    return funcs

DIAG = re.compile(r'getenv|ROGUESQ_|fprintf|printf|fputs|fflush|stderr|_diag\b|g_rs64_\w*(diag|log|dbg|trace|watch|probe|cnt|count|tally|obs)|'
                  r'rs64_\w*(note|log|cnt|count|tally|watch|probe|dump|trace|obs|_st\b|bwatch|mark|tctr)|rs5904_tally|RS64_S5798_ST|'
                  r'__builtin_expect\(g_rs64_store_diag|static FILE|FILE\s*\*', re.I)
GUEST = re.compile(r'^(ctx->r\d+|MEM_[BHWD]U?\(|ctx->f\d+|S32\(|ADD32|SUB32|SIGNED|goto L_|L_[0-9A-F]+:|if \(|\} else|else|\}|\{|'
                   r'(u)?int\d+_t \w+ = |func_0x|[a-zA-Z_]\w*\(rdram, ctx\);|return;|default:|case |switch|jalr|do \{|while)')

EFFECT = re.compile(r'ctx->\w+(?:\.\w+)?\s*(?:=(?!=)|\+=|-=|\|=|&=)|MEM_\w+\([^;]*\)\s*=(?!=)|\bgoto\b|\b\w+\(rdram,\s*ctx\)|do_break|__builtin_trap|'
                    r'LOOKUP_FUNC|\bmemcpy\(rdram|\bmemset\(rdram|\brdram\[[^\]]*\]\s*=(?!=)|\breturn\b')
CTRL = re.compile(r'^(?:\}\s*)?(?:else\s+)?(?:if|while|for|switch)\s*\((.*)\)\s*\{?$|^(?:\}\s*)?else\s*\{?$')
DECLV = re.compile(r'^(?:static\s+|extern\s+|const\s+|volatile\s+|unsigned\s+|signed\s+)*[A-Za-z_]\w*(?:\s+|\s*\*+\s*)\**(\w+)')
KW = {'if', 'else', 'while', 'for', 'switch', 'return', 'sizeof', 'int', 'unsigned', 'uint32_t', 'int32_t', 'float', 'double',
      'char', 'const', 'static', 'NULL', 'U32', 'S32', 'MEM_W', 'MEM_HU', 'MEM_BU', 'MEM_H', 'MEM_B', 'uint8_t', 'uint16_t',
      'int16_t', 'uint64_t', 'int64_t', 'gpr', 'ctx', 'rdram', 'u32l', 'fl', 'd', 'u32h'}

def untaint(extra, side, fname=''):
    """statements of extra with a guest-visible effect, or control statements whose condition is not purely diagnostic.
    Declarations, prints, local bookkeeping and braces are diagnostic by construction; a variable declared in the extra
    statements stays diagnostic only while no effect statement on that side reads it."""
    eff = [t for t in side if EFFECT.search(t) and not DIAG.search(t)]
    dv = set()
    for t in extra:
        m = DECLV.match(t)
        if m and not EFFECT.search(t): dv.update(re.findall(r'\b([A-Za-z_]\w*)\s*(?:=|\[|;|,|$)', t)); dv.add(m.group(1))
    dv = {v for v in dv if not any(re.search(r'\b%s\b' % re.escape(v), t) for t in eff)} - KW
    diagfn = bool(DIAG.search(fname))
    keep = []
    for t in extra:
        if DIAG.search(t) and not re.search(r'ctx->\w+(?:\.\w+)?\s*=(?!=)|MEM_\w+\([^;]*\)\s*=(?!=)', t): continue
        if EFFECT.search(t):
            if diagfn and not re.search(r'ctx->\w+(?:\.\w+)?\s*=(?!=)|MEM_\w+\([^;]*\)\s*=(?!=)', t): continue
            keep.append(t); continue
        m = CTRL.match(t)
        if m:
            ids = set(re.findall(r'\b([A-Za-z_]\w*)\b', m.group(1) or '')) - KW
            ids = {i for i in ids if not re.fullmatch(r'0[xX][0-9A-Fa-f]+u?|[0-9]+u?', i)}
            if diagfn or not (ids - dv): continue
            keep.append(t); continue
    return keep

SIZED = re.compile(r'^(data_gap_[0-9A-F]{8}|static_\d+_[0-9A-F]{8}|rspbootTextPreamble|fake_func_[0-9A-F]{8})$')

SLOT = re.compile(r'RS64_S7487_LWX\((0x[0-9A-Fa-f]+u), \d+,')
def slotless(x):
    return SLOT.sub(lambda m: 'RS64_S7487_LWX(%s, #,' % m.group(1), x)

def classify(lv, rg, name=''):
    """-> (class, live-only stmts, regen-only stmts, non-diag stmts that decided it)"""
    if lv == rg: return 'CODEGEN', [], [], []
    sm = difflib.SequenceMatcher(None, lv, rg, autojunk=False)
    lo, ro = [], []
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op != 'equal': lo += lv[a0:a1]; ro += rg[b0:b1]
    cl = [s for s in lo if s not in rg]; cr = [s for s in ro if s not in lv]
    if not cl and not cr:
        # same statements, different order: harmless only if every moved statement is diagnostic
        nd = [] if name == '<file>' else untaint(lo, lv, name) + untaint(ro, rg, name)
        return ('REORDER-DIAG' if not nd else 'REORDER'), lo, ro, nd
    if cl and sorted(map(slotless, cl)) == sorted(map(slotless, cr)) and all(SLOT.search(x) for x in cl + cr):
        return 'SLOTPERM', cl, cr, []
    nd_l = untaint(cl, lv, name); nd_r = untaint(cr, rg, name)
    if not nd_l and not nd_r: return 'ENVDIAG', cl, cr, []
    if SIZED.match(name) or not lv or not rg and SIZED.match(name): return 'GUEST', cl, cr, nd_l + nd_r
    if nd_l: return 'LOST', cl, cr, nd_l
    return 'REGENONLY', cl, cr, nd_r

def names(cmp):
    s = set()
    for k in ('diff', 'only_a', 'only_b'):
        for obj, v in cmp.get(k, {}).items():
            for n in v:
                s.add((obj.replace('.o', ''), (n[0] if isinstance(n, list) else n).lstrip('_'), k))
    return s

def run(live, regen, cmp, base=None):
    want = names(cmp)
    if base: old = {(o, n) for o, n, _ in names(base)}
    rows, cache = [], {}
    files = sorted({o for o, _, _ in want} | {f for f in os.listdir(live) if f.startswith('funcs_') and f.endswith('.c')})
    for f in files:
        L = split(os.path.join(live, f)) if os.path.exists(os.path.join(live, f)) else {}
        R = split(os.path.join(regen, f)) if os.path.exists(os.path.join(regen, f)) else {}
        cache[f] = (L, R)
        c, cl, cr, nd = classify(L.get('<file>', []), R.get('<file>', []), '<file>')
        if c != 'CODEGEN' or not R:
            rows.append(dict(file=f, func='<file>', kind='file' if R else 'live-file-only', cls=c if R else 'LIVEFILE',
                             live_only=cl[:40] if R else ['%d top-level + %d funcs' % (len(L.get('<file>', [])), len(L) - 1)],
                             regen_only=cr[:40], decided=nd[:40] if R else [], new=None))
    for f, n, k in sorted(want):
        L, R = cache.get(f, ({}, {}))
        if n not in L and n not in R:
            c, cl, cr, nd = 'NOTFOUND', [], [], []
        elif f == 'funcs_50.c' and not R:
            c, cl, cr, nd = 'LIVEFILE', [], [], []
        else:
            c, cl, cr, nd = classify(L.get(n, []), R.get(n, []), n)
        rows.append(dict(file=f, func=n, kind=k, cls=c, live_only=cl[:40], regen_only=cr[:40], decided=nd[:40],
                         new=(None if not base else (f, n) not in old)))
    # CODEGEN rows: name the text-level differences in the same file (the only thing that can change their object)
    for r in rows:
        if r['cls'] == 'CODEGEN' and r['func'] != '<file>':
            L, R = cache[r['file']]
            r['context'] = sorted(n for n in set(L) | set(R) if L.get(n) != R.get(n))
    return rows

def main(a):
    live, regen, cmpf = a[0], a[1], a[2]
    base = json.load(open(a[a.index('--baseline') + 1])) if '--baseline' in a else None
    cmp = json.load(open(cmpf))
    rows = run(live, regen, cmp, base)
    from collections import Counter
    print('class counts:', dict(Counter(r['cls'] for r in rows)))
    if base: print('new vs baseline:', dict(Counter(r['cls'] for r in rows if r['new'])))
    for r in rows:
        if r['cls'] in ('LOST', 'REGENONLY', 'NOTFOUND', 'LIVEFILE', 'REORDER') or (r['func'] == '<file>' and r['cls'] != 'ENVDIAG'):
            print('%-12s %-11s %-40s new=%s' % (r['cls'], r['file'], r['func'], r['new']))
            for s in r['decided'][:6]: print('    ! ' + s[:220])
    ctx = Counter((r['file'], tuple(r.get('context', []))) for r in rows if r['cls'] == 'CODEGEN' and (r['new'] or not base))
    for (f, c), k in sorted(ctx.items()): print('CODEGEN x%d %s context: %s' % (k, f, ', '.join(c) or 'NONE (unexplained)'))
    if '--json' in a: json.dump(rows, open(a[a.index('--json') + 1], 'w'), indent=1)
    acc = {}
    ap = os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7421_regen_accept.tsv')
    for l in open(ap) if os.path.exists(ap) and '--no-accept' not in a else []:
        if l.strip() and not l.startswith('#'): f, n, why = l.rstrip('\n').split('\t'); acc[(f, n)] = why
    bad = [r for r in rows if r['cls'] in ('LOST', 'REORDER') and (r['file'], r['func']) not in acc]
    for r in rows:
        if (r['file'], r['func']) in acc and r['cls'] in ('LOST', 'REORDER'): print('ACCEPTED %s %s %s: %s' % (r['cls'], r['file'], r['func'], acc[(r['file'], r['func'])]))
    for r in bad: print('OPEN %s %s %s' % (r['cls'], r['file'], r['func']))
    rc = 1 if bad else 0
    if '--control' in a:
        # plant: one non-diag statement into a copy of a function that compares equal; it must come back LOST
        f = 'funcs_20.c'; L = split(os.path.join(live, f)); R = split(os.path.join(regen, f))
        tgt = next(n for n in L if n != '<file>' and L[n] == R.get(n) and len(L[n]) > 5 and not DIAG.search(n) and not SIZED.match(n))
        tmp = tempfile.mkdtemp(prefix='s7421ctl'); shutil.copy(os.path.join(live, f), tmp)
        src = open(os.path.join(tmp, f)).read().split('\n')
        i = next(i for i, l in enumerate(src) if HDR.match(' '.join(l.split())) and re.search(r'\b%s\s*\(' % re.escape(tgt), l))
        j = next(j for j in range(i, len(src)) if '{' in src[j])
        src.insert(j + 1, '    ctx->r2 = ctx->r2 ^ 0x7421u; /* PATCH: s7421 planted control */')
        open(os.path.join(tmp, f), 'w').write('\n'.join(src))
        c = classify(split(os.path.join(tmp, f))[tgt], R[tgt], tgt)[0]
        # and a planted diag-only line must come back ENVDIAG (negative control)
        src.insert(j + 1, '    if (getenv("ROGUESQ_S7421_CTL")) fprintf(stderr, "x\\n");')
        src.pop(j + 2); open(os.path.join(tmp, f), 'w').write('\n'.join(src))
        c2 = classify(split(os.path.join(tmp, f))[tgt], R[tgt], tgt)[0]
        shutil.rmtree(tmp)
        # s7559 slot controls on a function carrying s7487 wraps: renumbered slot -> SLOTPERM, changed pc -> not SLOTPERM
        c3 = c4 = 'NONE'
        for f3 in sorted(os.listdir(live)):
            if not (f3.startswith('funcs_') and f3.endswith('.c')): continue
            L3 = split(os.path.join(live, f3))
            t3 = next((n for n in L3 if n != '<file>' and any(SLOT.search(x) for x in L3[n])), None)
            if not t3: continue
            k = next(i for i, x in enumerate(L3[t3]) if SLOT.search(x))
            a3 = list(L3[t3]); a3[k] = SLOT.sub(lambda m: 'RS64_S7487_LWX(%s, 1023,' % m.group(1), a3[k], 1)
            c3 = classify(L3[t3], a3, t3)[0]
            a4 = list(L3[t3]); a4[k] = SLOT.sub(lambda m: 'RS64_S7487_LWX(0x80000000u, 1023,', a4[k], 1)
            c4 = classify(L3[t3], a4, t3)[0]
            break
        ok = c == 'LOST' and c2 == 'ENVDIAG' and c3 == 'SLOTPERM' and c4 not in ('SLOTPERM', 'CODEGEN')
        print('CONTROL plant-hand-edit %s -> %s ; plant-diag -> %s ; slot-renumber -> %s ; pc-change -> %s : %s' % (tgt, c, c2, c3, c4, 'PASS' if ok else 'FAIL'))
        if not ok: return 3
    print('VERDICT', 'H-lost' if rc else 'H-mirrored')
    return rc

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
