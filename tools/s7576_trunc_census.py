#!/usr/bin/env python3
"""s7576: does clang -O2 exploit float->int cast UB in the generated C?

TRUNC_W_S/TRUNC_W_D (recomp.h) are bare C casts: (int32_t)float is UB for NaN or out-of-range values,
and clang -O2 provably deletes code on that basis (control snippet below). Census method, two arms per
RecompiledFuncs file, both at the RecompiledFuncs -O2 flags (tools/s7575_ir_flags.txt):
  A = the file as built (bare casts)
  B = TRUNC_W_S/TRUNC_W_D replaced by an opaque, total `fcvtzs` (inline asm: arm64 hardware semantics,
      saturating, NaN -> 0, nothing for the optimiser to reason about)
Per function, count fcvtzs (any form) in A and B. A < B means the optimiser deleted or constant-folded a
conversion that the hardware would have executed -> SUSPECT (listed). A >= B = conversions kept (CSE in A
may only lower B's count, never raise A's).  Controls (--controls): planted functions where clang folds
fptosi poison (must be SUSPECT) and a benign round trip (must be clean).
Suspects get a B2 arm (neon vcvts: defined, optimisable): A >= B2 = MERGED (legal code motion), else FOLDED.
Works on pre- or post-s7576 files (apply_s7576_trunc_total.py rewrites are undone in a temp copy first).
Run from repo root:  python3 tools/s7576_trunc_census.py --controls [-j 6] [--out scratch/s7576/census.txt]
"""
import os, re, subprocess, sys, tempfile, concurrent.futures as cf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUNCS = os.path.join(os.path.dirname(ROOT), 'N64Recomp', 'RecompiledFuncs')
PRELUDE = r'''
#include <stdint.h>
static inline __attribute__((always_inline)) int32_t rs64t_w_s(float v) { int32_t r; __asm__("fcvtzs %w0, %s1" : "=r"(r) : "w"(v)); return r; }
static inline __attribute__((always_inline)) int32_t rs64t_w_d(double v) { int32_t r; __asm__("fcvtzs %w0, %d1" : "=r"(r) : "w"(v)); return r; }
'''
CONTROL = r'''
#include <stdint.h>
#ifndef TRUNC_W_S
#define TRUNC_W_S(v) ((int32_t)(v))
#endif
int32_t ctl_fold_pos(float x) { if (x == 3e9f) return TRUNC_W_S(x); return 5; }
int32_t ctl_fold_neg(float x) { if (x == -3e9f) return TRUNC_W_S(x) > 0; return 5; }
float ctl_benign_roundtrip(float x) { return (float)TRUNC_W_S(x); }
int ctl_benign_cmp(float x) { return TRUNC_W_S(x) < 0; }
'''
# Hand-verified merges where B2 does not reproduce A's code motion (s7576, -O2 asm read):
INSPECTED = {
    '__Ldtob': 'one fcvtzs w10,d0 at loop header LBB31_173 (= L_80036EA8), entered from 0x80036EA4 and the bc1tl back-edge '
               'delay slot 0x80036F54, both trunc.w.d $f8,$f20 with f20 unchanged: legal tail-merge of identical pure ops',
}
FLAGS = open(os.path.join(ROOT, 'tools', 's7575_ir_flags.txt')).read().split()
FCV = re.compile(r'^\s+fcvtzs\b')
LABEL = re.compile(r'^(_[A-Za-z0-9_$.]+):')


def asm(src_path, extra):
    r = subprocess.run(['clang'] + FLAGS + extra + ['-S', '-o', '-', src_path], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f'{src_path}: {r.stderr[-400:]}')
    return r.stdout


def per_func(text):
    out, cur = {}, None
    for ln in text.splitlines():
        m = LABEL.match(ln)
        if m:
            cur = m.group(1); out.setdefault(cur, 0); continue
        if cur and FCV.match(ln):
            out[cur] += 1
    return out


UNPATCH = re.compile(r'RS64_TRUNC_W_([SD])\(([^,;]+), 0x[0-9A-F]+u\); /\* PATCH: s7576 trunc total \*/')
NEON = '#include <arm_neon.h>\n#define rs64n_w_s(v) vcvts_s32_f32(v)\n' \
       '#define rs64n_w_d(v) ((int32_t)vcvtd_s64_f64(v))\n'  # same shape as A (one fcvtzs), defined; only code motion is under test


def arms(path, tmpd):
    src = UNPATCH.sub(lambda m: 'TRUNC_W_%s(%s);' % (m.group(1), m.group(2)), open(path).read())
    inc = ['-I', os.path.dirname(os.path.abspath(path))]
    if src != open(path).read():  # census the raw N64Recomp emission, not the s7576-patched file
        path = os.path.join(tmpd, 'A_' + os.path.basename(path)); open(path, 'w').write(src)
    nsite = len(re.findall(r'(?<!define )TRUNC_W_[SD]\(', src))
    a = per_func(asm(path, inc))
    bsrc = re.sub(r'(?<!define )TRUNC_W_([SD])\(', lambda m: 'rs64t_w_%s(' % m.group(1).lower(), src)
    pre = os.path.join(tmpd, 'prelude.h')
    bp = os.path.join(tmpd, os.path.basename(path))
    open(bp, 'w').write(bsrc)
    # B is compiled from a copy beside the original's include context: -I paths in FLAGS are repo-relative.
    b = per_func(asm(bp, ['-include', pre] + inc))
    sus = [(f, a.get(f, 0), n) for f, n in b.items() if a.get(f, 0) < n]
    if sus:  # B2: well-defined but optimisable total conversion (neon fcvtzs). A >= B2 = a legal merge, not UB folding.
        np_ = os.path.join(tmpd, 'neon.h'); open(np_, 'w').write(NEON)
        b2 = per_func(asm(open_w(os.path.join(tmpd, 'B2_' + os.path.basename(path)),
                                 re.sub(r'(?<!define )TRUNC_W_([SD])\(', lambda m: 'rs64n_w_%s(' % m.group(1).lower(), src)),
                          ['-include', np_] + inc))
        sus = [(f, ca, n, b2.get(f, 0), 'MERGED' if ca >= b2.get(f, 0) else 'FOLDED') for f, ca, n in sus]
    return nsite, sum(a.values()), sum(b.values()), sus


def open_w(p, text):
    open(p, 'w').write(text); return p


def work(path):
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, 'prelude.h'), 'w').write(PRELUDE)
        return os.path.basename(path), arms(path, d)


def main():
    j = int(sys.argv[sys.argv.index('-j') + 1]) if '-j' in sys.argv else 6
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    lines, bad = [], 0
    sus = []
    if '--controls' in sys.argv:
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, 'prelude.h'), 'w').write(PRELUDE)
            cp = os.path.join(d, 'ctl.c'); open(cp, 'w').write(CONTROL)
            _, _, _, sus = arms(cp, d)
        names = {s[0] for s in sus}
        want = {'_ctl_fold_pos', '_ctl_fold_neg'}
        ok = names == want
        lines.append(f'CONTROL suspects={sorted(names)} want={sorted(want)} -> {"PASS" if ok else "FAIL"}')
        if not ok:
            bad = 1
    files = sorted(os.path.join(FUNCS, f) for f in os.listdir(FUNCS) if re.match(r'funcs_\d+\.c$', f))
    tot = [0, 0, 0]; allsus = []
    if '--controls' in sys.argv and not any(len(x) > 4 and x[4] == 'FOLDED' for x in sus):
        lines.append('CONTROL B2 did not classify the fold controls as FOLDED -> FAIL'); bad = 1
    with cf.ProcessPoolExecutor(j) as ex:
        for name, (n, ca, cb, sus) in ex.map(work, files):
            tot[0] += n; tot[1] += ca; tot[2] += cb
            for s in sus:
                allsus.append((name,) + s)
    allsus = [s[:5] + ('MERGED(inspected)',) if s[5] == 'FOLDED' and s[1] in INSPECTED else s for s in allsus]
    lines.append(f'files={len(files)} trunc_sites={tot[0]} fcvtzs_A={tot[1]} fcvtzs_B={tot[2]} suspect_funcs={len(allsus)}')
    for s in allsus:
        lines.append('SUSPECT %s %s A=%d B=%d B2=%d %s' % s)
    folded = sum(1 for s in allsus if s[5] == 'FOLDED')
    lines.append('FOLDED=%d (0 = no conversion deleted on UB grounds)' % folded)
    txt = '\n'.join(lines)
    print(txt)
    if out:
        os.makedirs(os.path.dirname(out), exist_ok=True); open(out, 'w').write(txt + '\n')
    return 1 if bad else (2 if folded else 0)


if __name__ == '__main__':
    sys.exit(main())
