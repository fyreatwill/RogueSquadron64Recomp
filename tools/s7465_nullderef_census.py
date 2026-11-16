#!/usr/bin/env python3
"""s7465 class DT: host C/C++ null-pointer dereferences / calls through null (clang static analyzer).

Re-uses s7463_uninit_census.py's TU scope and analyzer runner (line B), with the finding regex widened to the
core.NullDereference / core.CallAndMessage null family, and its own reviewed list.
Positive control (--controls): a planted TU compiled with main.cpp's command must be flagged on every planted line
(null deref through a sometimes-null pointer, null member call, null field store). Exit 1 if missed.
Usage: s7465_nullderef_census.py [--controls] [--jobs N] [--out DIR]
Exit: 0 clean (every finding is in tools/s7465_nullderef_reviewed.tsv), 1 survivor or failed control.
"""
import os, re, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('s7463', os.path.join(HERE, 's7463_uninit_census.py'))
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
c.B_RE = re.compile(r'^(?P<f>[^:\s][^:]*):(?P<l>\d+):\d+: warning: (?P<m>.*(?:[Nn]ull pointer|null|nullptr).*)$')
c.REVIEWED = os.path.join(HERE, 's7465_nullderef_reviewed.tsv')
c.CONTROL_SRC = r'''
struct S { int v; int get() const { return v; } };
int s7465_a(S *p, int k) { if (k) p = nullptr; return p->v; }          /* null deref */
int s7465_b(int k) { S *q = k ? new S{1} : nullptr; return q->get(); }  /* null member call */
void s7465_c(int k) { int *r = nullptr; if (k > 2) r = new int(0); *r = k; }  /* null store */
'''
_line_a = c.line_a
c.line_a = lambda e, src=None: (0, [], '')   # analyzer-only class
_main = c.main
def main():
    # control lines: 3, 4, 5 must be flagged by line B; line A is disabled for this class
    orig_args = sys.argv[1:]
    if '--controls' in orig_args:
        out = orig_args[orig_args.index('--out') + 1] if '--out' in orig_args else 'scratch/s7465'
        os.makedirs(os.path.join(c.ROOT, out), exist_ok=True)
        import json
        cc = json.load(open(c.CC))
        mainc = next(e for e in cc if c.rel(e['file']) == 'src/main/main.cpp')
        csrc = os.path.join(c.ROOT, out, 's7465_control.cpp'); open(csrc, 'w').write(c.CONTROL_SRC)
        _, hb, err = c.line_b(mainc, csrc)
        lb = {h[2] for h in hb}; need = {3, 4, 5}
        ok = need <= lb
        print(f'control lineB lines={sorted(lb)} need={sorted(need)} {"PASS" if ok else "FAIL"}')
        if not ok:
            print(err[-800:]); sys.exit(1)
        sys.argv = [sys.argv[0]] + [a for a in orig_args if a != '--controls']
    if '--out' not in sys.argv: sys.argv += ['--out', 'scratch/s7465']
    _main()
if __name__ == '__main__': main()
