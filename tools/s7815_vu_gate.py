#!/usr/bin/env python3
"""s7815 gate: every elementwise VU op the LLE gfx ucode compiles (25 live + 6 dead siblings), our ares bodies from the LIVE
librecomp headers vs two independent RSPs: cxd4 (rs64-oracle, with its five s7815 VU defects fixed by
tools/s7815_vu_ops/patch_cxd4.sh) on every op, and CEN64 (vendored headers) on the six ops stock cxd4 gets wrong.
Both shipped flavours (RS64_RSP_NEON_MAC=0/1). Controls: stock cxd4 must show exactly the known six-op defect signature
(the harness sees real differences), and a VMADN clamp mutant must fire both references.
usage: python3 tools/s7815_vu_gate.py [--reps N]   rc 0 = VERDICT GREEN + CONTROLS PASS"""
import subprocess, sys, re, os, tempfile, argparse, shutil
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7815_vu_ops')
KNOWN = {'VMADL', 'VMADN', 'VABS', 'VCH', 'VCR', 'VMRG'}   # stock cxd4 live-op defects (s7815)

def run(mut, reps, nm, cxd4=None):
    env = dict(os.environ); env.pop('CXD4', None)
    if cxd4: env['CXD4'] = cxd4
    p = subprocess.run(['zsh', os.path.join(H, 'run.sh'), mut, str(reps), str(nm), '0'], env=env, capture_output=True, text=True)
    out = p.stdout + p.stderr
    live_bad = {m.group(1) for m in re.finditer(r'^(V\w+)\s+live\s+([1-9]\d*)/', out, re.M)}
    cen = re.search(r'\[s7815\] cen64-vs-ares bad=(\d+)', out)
    cen_ops = {m.group(1) for m in re.finditer(r'^cen64-vs-ares (\w+)\s+([1-9]\d*)/', out, re.M)}
    tot = re.search(r'compares=(\d+) bad_live=(\d+)', out)
    if not tot or not cen: print(out[-1500:]); sys.exit(f'harness failed: mutant={mut} nm={nm}')
    return live_bad, int(cen.group(1)), cen_ops, int(tot.group(1))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--reps', type=int, default=200); o = ap.parse_args()
    d = tempfile.mkdtemp(prefix='s7815_cxd4p_')
    r = subprocess.run(['zsh', os.path.join(H, 'patch_cxd4.sh'), d], capture_output=True, text=True)
    if r.returncode: print(r.stdout, r.stderr); sys.exit('patch_cxd4 failed')
    green = True; ctl = True
    for nm in (0, 1):
        lb, cb, _, n = run('none', o.reps, nm, d)
        ok = not lb and cb == 0
        print(f'neon_mac={nm} ours-vs-cxd4(patched) live_bad_ops={sorted(lb)} ours-vs-cen64 bad={cb} compares={n} -> {"OK" if ok else "RED"}')
        green &= ok
    lb, _, _, _ = run('none', o.reps // 2, 0)
    ok = lb == KNOWN; ctl &= ok
    print(f'STOCK-CXD4 CONTROL {"PASS" if ok else "FAIL"} live_bad_ops={sorted(lb)} expected={sorted(KNOWN)}')
    for nm in (0, 1):
        lb, cb, cops, _ = run('madn_clamp', o.reps // 2, nm, d)
        ok = 'VMADN' in lb and 'VMADN' in cops; ctl &= ok
        print(f'MUTANT madn_clamp neon_mac={nm} {"PASS" if ok else "FAIL"} cxd4_ops={sorted(lb)} cen64_ops={sorted(cops)}')
    shutil.rmtree(d, ignore_errors=True)
    print('CONTROLS PASS' if ctl else 'CONTROLS FAIL')
    print(f'VU VERDICT {"GREEN" if green else "RED"}')
    return 0 if (green and ctl) else 1

if __name__ == '__main__': sys.exit(main())
