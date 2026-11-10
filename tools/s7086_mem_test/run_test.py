#!/usr/bin/env python3
"""s7086: build mem_test.c with the live RecompiledFuncs flags (-O2, recomp.h from lib/ + include/
rsp_dpc_macros.h), run it, then the -DNEG build (byte swizzle ^2) as a negative control.
Exit 0 iff the real build has 0 bad rows and the NEG build has > 0."""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'scratch', 's7086')
inc = [os.path.join(ROOT, p) for p in ('include', 'lib/N64ModernRuntime/ultramodern/include',
       'lib/N64ModernRuntime/librecomp/include', 'lib/N64ModernRuntime/N64Recomp/include')]
os.makedirs(OUT, exist_ok=True)
res = {}
for arm, extra in (('real', []), ('neg', ['-DNEG'])):
    exe = os.path.join(OUT, 'mem_test_' + arm)
    subprocess.check_call(['cc', '-g', '-std=gnu17', '-arch', 'arm64', '-O2', '-fno-strict-aliasing', '-w'] + extra +
                          sum((['-I', i] for i in inc), []) + [os.path.join(HERE, 'mem_test.c'), '-o', exe])
    p = subprocess.run([exe], capture_output=True, text=True)
    last = p.stdout.strip().split('\n')[-1]
    m = re.match(r'rows (\d+) bad (\d+)', last)
    res[arm] = (int(m.group(1)), int(m.group(2)))
    print(arm, last)
    if arm == 'real' and res[arm][1]:
        print(p.stdout[:2000])
ok = res['real'][1] == 0 and res['neg'][1] > 0
print('RESULT', 'PASS' if ok else 'FAIL', f"real {res['real'][1]}/{res['real'][0]} bad, neg control {res['neg'][1]} bad")
sys.exit(0 if ok else 1)
