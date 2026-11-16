#!/usr/bin/env python3
"""s7466 class DV: the clang static-analyzer crash families DS (uninit) and DT (null) did not cover.

Same 150-TU scope and analyzer runner as s7463_uninit_census.py (line B), analyzer-only. Families scored (by the
checker tag clang prints in brackets): unix.Malloc / cplusplus.NewDelete use-after-free and double free,
unix.MismatchedDeallocator, core.DivideZero, core.BitwiseShift / core.UndefinedBinaryOperatorResult,
core.StackAddressEscape, cplusplus.InnerPointer, plus anything else core./unix./cplusplus. that is not a leak.
Leaks, deadcode.*, security.insecureAPI.*, optin.*, nullability.* are COUNTED (count printed) but not reviewed:
they are not crash classes. DS/DT families (uninit/undefined/garbage, null) are excluded (their own censuses).
Positive control (--controls): planted TU with main.cpp's command; lines 3,4,5,6,7,8 must all be flagged.
Exit 0 clean (every scored finding in tools/s7466_analyzer_rest_reviewed.tsv), 1 survivor or failed control.
"""
import os, re, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('s7463', os.path.join(HERE, 's7463_uninit_census.py'))
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
ANY = re.compile(r'^(?P<f>[^:\s][^:]*):(?P<l>\d+):\d+: warning: (?P<m>.*)\[(?P<k>[A-Za-z0-9_.]+)\]\s*$')
DS_DT = re.compile(r'uninitiali[sz]ed|garbage|[Uu]ndefined|undef|[Nn]ull pointer|\bnull\b|nullptr')
UNSCORED = re.compile(r'^(deadcode\.|security\.insecureAPI|optin\.|nullability\.|osx\.|alpha\.)')
c.REVIEWED = os.path.join(HERE, 's7466_analyzer_rest_reviewed.tsv')
counted = {}
def scored(m):
    k, msg = m['k'], m['m']
    if 'leak' in msg.lower() or UNSCORED.match(k):
        counted[k] = counted.get(k, 0) + 1; return False
    if DS_DT.search(msg) and k not in ('core.BitwiseShift', 'core.DivideZero'): return False
    return True
def line_b(e, src=None):
    a = c.base_args(e)
    if src: a = [x if os.path.realpath(os.path.join(e['directory'], x)) != os.path.realpath(e['file']) else src for x in a]
    rc, err = c.run(a + ['--analyze', '--analyzer-output', 'text', '-Wno-everything', '-o', '/dev/null'], e['directory'])
    hits = []
    for ln in err.splitlines():
        m = ANY.match(ln)
        if m and scored(m):
            hits.append(('B', c.rel(os.path.join(e['directory'], m['f'])), int(m['l']), m['k'], m['m'].strip()))
    return rc, hits, err
c.line_b = line_b
c.line_a = lambda e, src=None: (0, [], '')   # analyzer-only class
CONTROL_SRC = r'''#include <cstdlib>
struct S { int v; };
int s7466_a(int k) { int *p = (int*)malloc(4); free(p); return *p + k; }   /* UAF */
void s7466_b(int k) { int *p = (int*)malloc(4); free(p); if (k) free(p); } /* double free */
int s7466_c(int k) { S *s = new S{1}; delete s; return s->v + k; }       /* new/delete UAF */
int s7466_d(int k) { int z = 0; if (k > 1) z = 0; return k / z; }        /* div zero */
int s7466_f(int k) { int *p = new int[4]; delete p; return k; }          /* mismatched dealloc */
int s7466_g(int k) { return 1 << 40 | k; }                               /* shift overflow */
'''
def main():
    args = sys.argv[1:]
    out = args[args.index('--out') + 1] if '--out' in args else 'scratch/s7466'
    if '--controls' in args:
        import json
        os.makedirs(os.path.join(c.ROOT, out), exist_ok=True)
        cc = json.load(open(c.CC))
        mainc = next(e for e in cc if c.rel(e['file']) == 'src/main/main.cpp')
        csrc = os.path.join(c.ROOT, out, 's7466_control.cpp'); open(csrc, 'w').write(CONTROL_SRC)
        _, hb, err = line_b(mainc, csrc)
        lb = {h[2] for h in hb}; need = {3, 4, 5, 6, 7, 8}
        ok = need <= lb
        print(f'control lineB lines={sorted(lb)} need={sorted(need)} {"PASS" if ok else "FAIL"}')
        if not ok: print(err[-800:]); sys.exit(1)
        counted.clear()
        args = [a for a in args if a != '--controls']
    if '--out' not in args: args += ['--out', out]
    sys.argv = [sys.argv[0]] + args
    try:
        c.main()
    finally:
        print('counted_unscored ' + ' '.join(f'{k}={v}' for k, v in sorted(counted.items())))
if __name__ == '__main__': main()
