#!/usr/bin/env python3
"""s7858 regression: a [vi-poll] line spliced into a 0x800FA738 [hit] line must not shift later dt pins (s7857/v14 r1 lost the
tick-886 hit and every later pin landed one tick early).  Builds a 6-tick synthetic oracle log, splices tick 2's 738 hit, and checks
the tick-4 pin stays at 4.  Control: the same log with a dt hit simply deleted must make the parser exit 2 (missing tick)."""
import subprocess, sys, tempfile, os
def hit(pc, n, f20, f0='3d0b253a'):
    return (f'[hit] x addr=0x00000000 pc=0x{pc} prev_pc=0x0 t=1.0s n={n}', f' v0=0x1 fpr: f0={f0} f4=0 f6=0 f14=0 f20={f20}')
def log(splice_at=None, drop_at=None):
    L = []
    for t in range(6):
        L.append(f'[xtrace] {t} {t} 800fa730 00000000 pc=800fa730 m=80003470:12345678')
        a, b = hit('800fa738', 2 * t, '3d0b253a')
        if t == drop_at: pass
        elif t == splice_at: L += [a + '[vi-poll] t= 1.0s WIDTH 512 => 512 origin=0x00690800', b]
        else: L.append(a + b)
        a, b = hit('800fa7d0', 2 * t + 1, '3d088887' if t == 4 else '3d088888'); L.append(a + b)
    return '\n'.join(L) + '\n'
def run(text):
    with tempfile.NamedTemporaryFile('w', suffix='.log', delete=False) as f: f.write(text)
    r = subprocess.run([sys.executable, 'tools/s7849_det_pins.py', f.name], capture_output=True, text=True); os.unlink(f.name)
    return r.returncode, dict(l.split('=', 1) for l in r.stdout.split('\n') if '=' in l)
ok = True
rc, v = run(log(splice_at=2)); good = rc == 0 and v.get('DT_AT') == '4:3D088887' and v.get('NTICKS') == '6'
print('splice  :', 'PASS' if good else 'FAIL', rc, v); ok &= good
rc, v = run(log(drop_at=2)); good = rc == 2
print('control :', 'PASS' if good else 'FAIL', '(missing tick must exit 2)', rc, v.get('DT_AT')); ok &= good
sys.exit(0 if ok else 1)
