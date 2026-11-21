#!/usr/bin/env python3
"""s7423 class CF: live-stale patches. The binary is built from the LIVE RecompiledFuncs tree, so a statement the fixup chain
applies in a regen but the live tree lacks is a patch the shipped build is missing. s7421_regen_drift.py only walked functions
whose OBJECT differed; this walks EVERY function in every file (text level), so a regen-only line hidden by identical codegen
(or an object diff misattributed) cannot escape.
Per function present in both trees: normalised statement lists (s7421 split: comments incl. PATCH labels dropped, whitespace
collapsed); regen-only statements = in regen, not anywhere in live's same function (pure reorder -> ORDER). Each is
  DIAG       s7421 untaint() finds no guest-visible effect / non-diag control (env-gated log, trace, counter, static capture)
  BEHAVIOUR  anything else
Functions only in regen are listed as REGEN-FUNC (BEHAVIOUR unless every statement is DIAG).
usage: s7423_live_stale.py <live> <regen> [--json out] [--control]
--control: (1) the two known funcs_9 lines (s6789b g3e kind 8, s6497 bounds) must be listed; (2) a planted guest store
in a copy of a regen function must come back BEHAVIOUR; (3) a planted env-gated print must come back DIAG.
Reviewed rows: tools/s7423_live_stale_accept.tsv. Exit 0 = no open BEHAVIOUR row, 1 = open BEHAVIOUR rows, 3 = control failed.
--reverse (s7719): same walk with the trees swapped, i.e. statements/functions/files only in LIVE (class H-lost: a hand edit no
fixup reproduces, which dies at the next regen). s7421 only saw functions whose object differed; this sees every function.
Usage keeps the argument order <live> <regen>. Control (1) becomes: the known live-only s6499 funcs_9 store-census loop is
listed; (2)/(3) plant into a copy of the live file. Reviewed rows: tools/s7719_live_only_accept.tsv."""
import json, os, re, shutil, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s7421_regen_drift import split, untaint, HDR, SIZED, DIAG, EFFECT
import difflib

def cmpf(L, R):
    rows = []
    for n, rg in R.items():
        if n == '<file>': continue
        lv = L.get(n)
        if lv is None:
            nd = untaint(rg, rg, n)
            rows.append(dict(func=n, cls='REGEN-FUNC' if nd else 'REGEN-FUNC-DIAG', stmts=rg[:8], decided=nd[:8])); continue
        if lv == rg: continue
        ls = set(lv); ro = [s for s in rg if s not in ls]
        if SIZED.match(n):  # data-gap / boot-preamble sizing (s6871): guest decode of non-code bytes, not a patch
            rows.append(dict(func=n, cls='GUEST', stmts=ro[:20], decided=[])); continue
        if not ro:
            sm = difflib.SequenceMatcher(None, lv, rg, autojunk=False)
            mv = [x for op, a0, a1, b0, b1 in sm.get_opcodes() if op != 'equal' for x in rg[b0:b1]]
            nd = untaint(mv, rg, n) if mv else []
            if mv: rows.append(dict(func=n, cls='ORDER-BEHAVIOUR' if nd else 'ORDER-DIAG', stmts=mv[:20], decided=nd[:20]))
            continue
        nd = untaint(ro, rg, n)
        # a control statement reading only counters declared in a diag-gated static decl of this function is diagnostic
        sv = set()
        for i, t in enumerate(rg):
            if t.startswith('static ') and i and DIAG.search(rg[i - 1]):
                sv.update(re.findall(r'\b([A-Za-z_]\w*)\s*=', t))
        nd = [t for t in nd if EFFECT.search(t) or not (set(re.findall(r'\b([a-z_]\w*\d+\w*)\b', t)) & sv)]
        rows.append(dict(func=n, cls='BEHAVIOUR' if nd else 'DIAG', stmts=ro[:20], decided=nd[:20]))
    ro = [s for s in R.get('<file>', []) if s not in set(L.get('<file>', []))]
    if ro:
        nd = [s for s in untaint(ro, R['<file>'], '<file>') if not re.match(r'^(static|extern|#)', s)]
        rows.append(dict(func='<file>', cls='FILE-BEHAVIOUR' if nd else 'FILE-DIAG', stmts=ro[:20], decided=nd[:20]))
    return rows

def run(live, regen):
    out = []
    for f in sorted(x for x in os.listdir(regen) if x.startswith('funcs_') and x.endswith('.c')):
        lp = os.path.join(live, f)
        if not os.path.exists(lp): out.append(dict(file=f, func='*', cls='REGEN-FILE', stmts=[], decided=[])); continue
        for r in cmpf(split(lp), split(os.path.join(regen, f))): r['file'] = f; out.append(r)
    return out

def control(live, regen, rows, rev=False):
    k9 = [r for r in rows if r['file'] == 'funcs_9.c' and r['cls'] in ('DIAG', 'BEHAVIOUR')]
    s = ' '.join(' '.join(r['stmts'] + r['decided']) for r in k9)
    c1 = ('for (int i = 0; i < 24; i++) {' in s) if rev else ('rs64_g3e_trace(8' in s and 's6497_x0' in s)
    # s7739: once the regen replay is adopted as live, funcs_9 is byte-identical on both sides and the known drift lines no
    # longer exist; (1) is then vacuous ('n/a') and the planted store/diag controls below carry the same-run positive.
    if not c1 and not k9 and open(os.path.join(live, 'funcs_9.c'), 'rb').read() == open(os.path.join(regen, 'funcs_9.c'), 'rb').read():
        c1 = 'n/a'
    f = 'funcs_20.c'; L = split(os.path.join(live, f)); R = split(os.path.join(regen, f))
    tgt = next(n for n in R if n != '<file>' and L.get(n) == R[n] and len(R[n]) > 5)
    tmp = tempfile.mkdtemp(prefix='s7423ctl'); res = []
    for plant in ('    MEM_W(0, ctx->r29) = ctx->r2 ^ 0x7423u;', '    if (getenv("ROGUESQ_S7423_CTL")) fprintf(stderr, "x\\n");'):
        src = open(os.path.join(regen, f)).read().split('\n')
        i = next(i for i, l in enumerate(src) if HDR.match(' '.join(l.split())) and re.search(r'\b%s\s*\(' % re.escape(tgt), l))
        j = next(j for j in range(i, len(src)) if '{' in src[j]); src.insert(j + 1, plant)
        open(os.path.join(tmp, f), 'w').write('\n'.join(src))
        rr = [r for r in cmpf(L, split(os.path.join(tmp, f))) if r['func'] == tgt]
        res.append(rr[0]['cls'] if rr else 'NONE')
    shutil.rmtree(tmp)
    ok = bool(c1) and res == ['BEHAVIOUR', 'DIAG']
    print('CONTROL funcs_9 known lines listed=%s (%s) ; plant-store -> %s ; plant-diag -> %s : %s' %
          (c1, ','.join(r['cls'] for r in k9), res[0], res[1], 'PASS' if ok else 'FAIL'))
    return ok

def main(a):
    live, regen = a[0], a[1]
    rev = '--reverse' in a
    if rev: live, regen = regen, live
    rows = run(live, regen)
    from collections import Counter
    print('class counts:', dict(Counter(r['cls'] for r in rows)))
    for r in rows:
        print('%-15s %-11s %s' % (r['cls'], r['file'], r['func']))
        for s in (r['decided'] or r['stmts'])[:5]: print('    %s %s' % ('!' if r['decided'] else '-', s[:230]))
    if '--json' in a: json.dump(rows, open(a[a.index('--json') + 1], 'w'), indent=1)
    if '--control' in a and not control(live, regen, rows, rev): return 3
    ap = os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7719_live_only_accept.tsv' if rev else 's7423_live_stale_accept.tsv'); acc = {}
    for l in open(ap) if os.path.exists(ap) else []:
        if l.strip() and not l.startswith('#'): f, n, why = l.rstrip('\n').split('\t'); acc[(f, n)] = why
    beh = [r for r in rows if r['cls'] in ('BEHAVIOUR', 'ORDER-BEHAVIOUR', 'REGEN-FUNC', 'FILE-BEHAVIOUR', 'REGEN-FILE')]
    for r in beh:
        if (r['file'], r['func']) in acc: print('ACCEPTED %s %s %s: %s' % (r['cls'], r['file'], r['func'], acc[(r['file'], r['func'])]))
    beh = [r for r in beh if (r['file'], r['func']) not in acc]
    for r in beh: print('OPEN %s %s %s' % (r['cls'], r['file'], r['func']))
    print('VERDICT', 'H-behaviour (%d rows)' % len(beh) if beh else 'H-diag')
    return 1 if beh else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
