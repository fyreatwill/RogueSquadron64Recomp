#!/usr/bin/env python3
"""s7463 class DS: host C/C++ uninitialized reads + missing returns.

Two independent lines per in-scope TU (re-using its exact compile_commands.json command):
  A  clang flow warnings: -Wuninitialized -Wsometimes-uninitialized -Wconditional-uninitialized
     -Wreturn-type -Wreturn-stack-address -Wdangling (+ -Wuninitialized-const-reference)
  B  clang static analyzer (path-sensitive): uninitialized / garbage / undefined findings
Positive control (--controls): a planted TU compiled with main.cpp's command must be flagged by both
lines (sometimes-uninit branch, uninit arg by value, missing return); exit 1 if either line misses it.
Usage: s7463_uninit_census.py [--controls] [--no-analyzer] [--jobs N] [--out DIR]
Exit: 0 clean (every finding is in tools/s7463_uninit_reviewed.tsv), 1 survivor or failed control.
"""
import json, os, re, shlex, subprocess, sys, concurrent.futures as cf
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CC = os.path.join(ROOT, 'build', 'compile_commands.json')
REVIEWED = os.path.join(ROOT, 'tools', 's7463_uninit_reviewed.tsv')
SCOPE = ('src/main/', 'src/rsp/', 'RecompiledPatches/', 'build/factor5_ucode/',
         'lib/N64ModernRuntime/ultramodern/src/', 'lib/N64ModernRuntime/librecomp/src/',
         'lib/rt64/src/common/', 'lib/rt64/src/gbi/', 'lib/rt64/src/hle/', 'lib/rt64/src/render/',
         'lib/rt64/src/rhi/', 'lib/rt64/src/apple/', 'lib/rt64/src/preset/', 'lib/rt64/src/shared/',
         'lib/rt64/src/contrib/plume/plume_metal.cpp', 'lib/rt64/src/contrib/plume/plume_apple.mm')
WFLAGS = ['-Wuninitialized', '-Wsometimes-uninitialized', '-Wconditional-uninitialized',
          '-Wreturn-type', '-Wreturn-stack-address', '-Wdangling', '-Wuninitialized-const-reference']
A_RE = re.compile(r'^(?P<f>[^:\s][^:]*):(?P<l>\d+):\d+: (?:warning|error): (?P<m>.*\[(?P<w>-W(?:uninitialized|sometimes-uninitialized|conditional-uninitialized|return-type|return-stack-address|dangling[\w-]*|uninitialized-const-reference))[\],].*)$')
B_RE = re.compile(r'^(?P<f>[^:\s][^:]*):(?P<l>\d+):\d+: warning: (?P<m>.*(?:uninitiali[sz]ed|garbage|[Uu]ndefined|undef).*)$')
ANALYZER_MAX_BYTES = 1_500_000   # generated ucode TUs: line A only

def rel(p):
    p = os.path.realpath(p)
    r = os.path.realpath(ROOT) + '/'
    return p[len(r):] if p.startswith(r) else p

def base_args(e):
    a = e['arguments'][:] if 'arguments' in e else shlex.split(e['command'])
    out, skip = [], False
    for i, x in enumerate(a):
        if skip: skip = False; continue
        if x == '-o': skip = True; continue
        if x in ('-c',) or x.startswith('-W') and x not in ('-Wno-unused-parameter',) or x == '-w': continue
        if x.startswith('-O'): continue
        out.append(x)
    return out

def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors='replace')
    return p.returncode, p.stderr

def line_a(e, src=None):
    a = base_args(e)
    if src: a = [x if os.path.realpath(os.path.join(e['directory'], x)) != os.path.realpath(e['file']) else src for x in a]
    rc, err = run(a + ['-O1', '-fsyntax-only', '-Wno-everything'] + WFLAGS, e['directory'])
    hits = []
    for ln in err.splitlines():
        m = A_RE.match(ln)
        if m: hits.append(('A', rel(os.path.join(e['directory'], m['f'])), int(m['l']), m['w'], m['m']))
    return rc, hits, err

def line_b(e, src=None):
    a = base_args(e)
    if src: a = [x if os.path.realpath(os.path.join(e['directory'], x)) != os.path.realpath(e['file']) else src for x in a]
    rc, err = run(a + ['--analyze', '--analyzer-output', 'text', '-Wno-everything', '-o', '/dev/null'], e['directory'])
    hits = []
    for ln in err.splitlines():
        m = B_RE.match(ln)
        if m and 'note:' not in ln: hits.append(('B', rel(os.path.join(e['directory'], m['f'])), int(m['l']), 'analyzer', m['m']))
    return rc, hits, err

CONTROL_SRC = r'''
static int pick(int k) { int v; if (k > 3) v = 7; return v; }          /* sometimes-uninit */
static int use(int x) { return x + 1; }
static int pass(void) { int q; return use(q); }                        /* uninit by value */
static int noret(int k) { if (k) return 1; }                           /* missing return */
int s7463_control(int k) { return pick(k) + pass() + noret(k); }
'''

_SRC = {}
def src_line(f, l):
    """Stripped text of line l of repo file f ('' if unreadable): the s7652 review anchor."""
    if f not in _SRC:
        try: _SRC[f] = open(os.path.join(ROOT, f), errors='replace').read().split('\n')
        except OSError: _SRC[f] = []
    ls = _SRC[f]
    return ls[l - 1].strip() if 0 < l <= len(ls) else ''

def load_reviewed(path):
    """s7652: reviewed rows were keyed (file, line) only and went stale as files grew (s7465/s7466 12 survivors were all
    reviewed sites shifted +25..+92 lines). A row may carry a 5th column = the stripped source line at review time; it then
    matches by (file, text) wherever the line moved. A row whose anchor no longer occurs in its file is STALE (exit 1),
    never silently dropped. Rows without an anchor keep the old (file, line) match."""
    rev, anch, stale = {}, {}, []
    if not os.path.exists(path): return rev, anch, stale
    for ln in open(path):
        if ln.startswith('#') or not ln.strip(): continue
        cols = ln.rstrip('\n').split('\t')
        f, l, verdict = cols[0], int(cols[1]), cols[2]
        a = cols[4].strip() if len(cols) > 4 and cols[4].strip() else None
        if a is None: rev[(f, l)] = verdict; continue
        anch[(f, a)] = verdict
        src_line(f, 1)
        if not any(x.strip() == a for x in _SRC[f]): stale.append((f, l, a))
    return rev, anch, stale

def main():
    args = sys.argv[1:]
    out = 'scratch/s7463'
    if '--out' in args: out = args[args.index('--out') + 1]
    jobs = int(args[args.index('--jobs') + 1]) if '--jobs' in args else 8
    os.makedirs(os.path.join(ROOT, out), exist_ok=True)
    cc = json.load(open(CC)); seen = set(); tus = []
    for e in cc:
        r = rel(e['file'])
        if r in seen or not r.startswith(SCOPE): continue
        seen.add(r); tus.append(e)
    print(f'tus_in_scope={len(tus)}')
    bad = 0
    if '--controls' in args:
        mainc = next(e for e in tus if rel(e['file']) == 'src/main/main.cpp')
        csrc = os.path.join(ROOT, out, 's7463_control.cpp'); open(csrc, 'w').write(CONTROL_SRC)
        _, ha, _ = line_a(mainc, csrc); _, hb, _ = line_b(mainc, csrc)
        la = {h[2] for h in ha}; lb = {h[2] for h in hb}
        need_a = {2, 4, 5}; need_b = {2, 4}
        okA = need_a <= la; okB = need_b <= lb
        print(f'control lineA lines={sorted(la)} need={sorted(need_a)} {"PASS" if okA else "FAIL"}')
        print(f'control lineB lines={sorted(lb)} need={sorted(need_b)} {"PASS" if okB else "FAIL"}')
        if not (okA and okB): bad = 1
    def work(e):
        r = rel(e['file']); res = []
        rcA, ha, errA = line_a(e); res += ha
        if rcA != 0 and not ha: res.append(('A', r, 0, 'compile-fail', errA.strip().splitlines()[-1][:200] if errA.strip() else 'rc'))
        if '--no-analyzer' not in args and os.path.getsize(e['file']) <= ANALYZER_MAX_BYTES:
            _, hb, _ = line_b(e); res += hb
        return r, res
    allhits = []
    with cf.ThreadPoolExecutor(jobs) as ex:
        for r, res in ex.map(work, tus):
            allhits += res
    uniq = sorted(set(allhits), key=lambda h: (h[1], h[2], h[0]))
    rev, anch, stale = load_reviewed(REVIEWED)
    def verdict(h):
        a = anch.get((h[1], src_line(h[1], h[2])))
        return a if a is not None else rev.get((h[1], h[2]))
    with open(os.path.join(ROOT, out, 'findings.tsv'), 'w') as fo:
        for h in uniq:
            fo.write('\t'.join([h[0], h[1], str(h[2]), h[3], verdict(h) or 'UNREVIEWED', h[4]]) + '\n')
    surv = [h for h in uniq if verdict(h) is None]
    for f, l, a in stale: print(f'STALE-ANCHOR {f}:{l} anchor not found in the file: {a[:120]}')
    if stale: bad = 1
    ca = sum(1 for h in uniq if h[0] == 'A'); cb = sum(1 for h in uniq if h[0] == 'B')
    print(f'findings lineA={ca} lineB={cb} unique_sites={len({(h[1],h[2]) for h in uniq})} survivors={len(surv)}')
    for h in surv[:80]: print('SURVIVOR', h[0], f'{h[1]}:{h[2]}', h[3], h[4][:160])
    sys.exit(1 if (bad or surv) else 0)

if __name__ == '__main__': main()
