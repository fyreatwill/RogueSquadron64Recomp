#!/usr/bin/env python3
"""s7577: whole-TU -O2 UB-exploitation census for the RSP ucode translation units.

For each ucode TU (compile_commands.json entries matching factor5_ucode/boot), compile to asm at its real flags in four arms:
  A  as built
  W  + -fwrapv                          (signed overflow defined)
  S  + -fno-strict-aliasing             (type-based aliasing off)
  N  + -fno-delete-null-pointer-checks  (null-check deletion off)
tools/s7577_ucode_ctl.h is force-included in every arm: its rs64_s7577_ctl_* functions are fold controls that MUST differ
between A and their arm. Every other function must be identical; a differing ucode function = clang used that UB class.
W diffs are EXPECTED (nsw facts on bounded loop counters / s8 immediates let clang drop sign-extends); whether any of them can
be false is decided per source site by tools/s7577_ubsan_sites.py --check. If the build already passes -fno-strict-aliasing
the S arm is a no-op and its control reads PRE-OFF. Usage: [TU_RE=<regex on file path>] tools/s7577_ucode_ub_census.py OUTDIR
rc 0 = W and N controls fired in every TU, S control fired or PRE-OFF, and the N arm changes 0 ucode functions.
"""
import json, os, re, shlex, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'scratch/s7577'))
CTL = os.path.join(ROOT, 'tools/s7577_ucode_ctl.h')
ARMS = {'A': [], 'W': ['-fwrapv'], 'S': ['-fno-strict-aliasing'], 'N': ['-fno-delete-null-pointer-checks']}
CTL_ARM = {'rs64_s7577_ctl_wrapv': 'W', 'rs64_s7577_ctl_u16mul': 'W', 'rs64_s7577_ctl_alias': 'S', 'rs64_s7577_ctl_null': 'N'}
os.makedirs(OUT, exist_ok=True)
cc = json.load(open(os.path.join(ROOT, 'build/compile_commands.json')))
tus = [e for e in cc if re.search(os.environ.get('TU_RE', r'factor5_(ucode|boot)'), e['file'])]  # TU_RE=RecompiledFuncs/ for the game C

def argv_for(e, extra, asm):
    a = e.get('arguments') or shlex.split(e['command'])
    o = []; skip = False
    for x in a:
        if skip: skip = False; continue
        if x in ('-o', '-MF', '-MT', '-MQ'): skip = True; continue
        if x in ('-c', '-MD', '-MMD') or x == e['file']: continue
        if x.startswith('-g'): continue
        o.append(x)
    return o + extra + ['-include', CTL, '-S', '-g0', '-o', asm, e['file']]

def run(job):
    e, arm = job
    asm = os.path.join(OUT, '%s.%s.s' % (os.path.basename(e['file']), arm))
    r = subprocess.run(argv_for(e, ARMS[arm], asm), cwd=e['directory'], capture_output=True, text=True)
    return job, asm, r.returncode, r.stderr[-400:]

def funcs(path):
    """symbol -> normalised body (labels renumbered per function, directives dropped)."""
    out = {}; cur = None; body = []
    for ln in open(path):
        s = ln.rstrip()
        m = re.match(r'^(_[A-Za-z0-9_$.]+):', s)
        if m and not s.startswith('_.'):
            if cur: out[cur] = body
            cur = m.group(1); body = []; continue
        if cur is None: continue
        t = s.strip()
        if not t or t.startswith(';') or t.startswith('.cfi') or t.startswith('.loc') or t.startswith('.p2align') or t.startswith('.loh'): continue
        if t.startswith('.section') or t.startswith('.globl') or t.startswith('.private_extern'):
            if cur: out[cur] = body
            cur = None; body = []; continue
        body.append(t.split(';')[0].rstrip())
    if cur: out[cur] = body
    norm = {}
    for k, b in out.items():
        labs = {}
        def lab(m):
            labs.setdefault(m.group(0), 'L%d' % len(labs)); return labs[m.group(0)]
        norm[k] = [re.sub(r'\b[Ll](?:tmp|BB|CPI|JTI|loh)[0-9_]+\b', lab, x) for x in b]
    return norm

jobs = [(e, a) for e in tus for a in ARMS]
with ThreadPoolExecutor(max_workers=min(12, os.cpu_count() or 4)) as ex:
    res = list(ex.map(run, jobs))
bad = [r for r in res if r[2]]
for (e, a), asm, rc, err in bad: print('COMPILE-FAIL', os.path.basename(e['file']), a, rc, err)
if bad: sys.exit(3)
asms = {(os.path.basename(e['file']), a): asm for (e, a), asm, rc, err in res}
total_diff = 0; ctl_ok = 0; ctl_n = 0; wdiff = 0
for e in tus:
    tu = os.path.basename(e['file'])
    base = funcs(asms[(tu, 'A')])
    nuc = sum(1 for k in base if 'rs64_s7577_ctl' not in k)
    line = [tu, 'funcs=%d' % nuc]
    for a in ('W', 'S', 'N'):
        other = funcs(asms[(tu, a)])
        diff = sorted(k for k in set(base) | set(other) if 'rs64_s7577_ctl' not in k and base.get(k) != other.get(k))
        if a == 'W': wdiff += len(diff)
        else: total_diff += len(diff)
        line.append('%s:diff=%d%s' % (a, len(diff), ('[' + ','.join(diff[:6]) + ']') if diff else ''))
        for c, ca in CTL_ARM.items():
            if ca != a: continue
            ctl_n += 1; k = '_' + c
            fired = k in base and k in other and base[k] != other[k]
            argv = e.get('arguments') or shlex.split(e['command'])
            preoff = (not fired) and a == 'S' and '-fno-strict-aliasing' in argv
            ctl_ok += fired or preoff
            line.append('ctl:%s=%s' % (c[len('rs64_s7577_ctl_'):], 'FIRED' if fired else ('PRE-OFF' if preoff else 'DEAD')))
    print(' '.join(line))
print('SUMMARY tus=%d wrapv_func_diffs=%d (expected; see s7577_ubsan_sites.py --check) S+N_func_diffs=%d controls=%d/%d' % (len(tus), wdiff, total_diff, ctl_ok, ctl_n))
sys.exit(0 if total_diff == 0 and ctl_ok == ctl_n else 1)
