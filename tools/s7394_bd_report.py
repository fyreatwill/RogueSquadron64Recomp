#!/usr/bin/env python3
"""s7394 class BD report: heap-mutex (8010FEE0) re-seed windows from a ROGUESQ_S7394_BD=1 run.

usage: tools/s7394_bd_report.py <run.log> [--fix]
Reads [s7394-win] rows (one per window) and the last [s7394-sum]. Verdict:
  H-none        no window saw a foreign 8010FEE0 recv (intr 0 outside the control window) and no foreign close
  H-race        some window outside the control had intr>0 or a foreign close (a second thread inside the critical section)
  H-port-timing reported alongside: windows where another guest thread ran at all (xcalls>0)
exit 0 = control PASS (CTL armed: control window intr==1, foreground mode reported) and H-none; 2 = control FAILED/missing
or no windows; 3 = H-race.
"""
import re, sys
W = re.compile(r'^\[s7394-win\] n=(\d+) t=(\S+) owner=(-?\d+) open=(\S+) close=(\w) ctid=(-?\d+) cres=(-?\d+) ckey=(\S+) us=(\S+) '
               r'intr=(\d+) xcalls=(\d+) xtids=(\w+) ocalls=(\d+)')
S = re.compile(r'^\[s7394-sum\] .*ctl=(\d+) ctlwin=(-?\d+) ctlmode=(\d+) open=\d+ shadow_x=(\d+) shadow_hitwin=(\d+)')
rows, summ, tidl = [], None, ''
for ln in open([a for a in sys.argv[1:] if not a.startswith('--')][0], errors='replace'):
    m = W.match(ln)
    if m: rows.append(m.groups()); continue
    if ln.startswith('[s7394-tid]'): tidl = ln.strip()
    m = S.match(ln)
    if m: summ = tuple(int(x) for x in m.groups())
armed = any(l.startswith('[s7394-sum]') for l in open([a for a in sys.argv[1:] if not a.startswith('--')][0], errors='replace'))
ctl, ctlwin, mode, shx, shw = summ if summ else (0, -1, 0, 0, 0)
print(f"windows={len(rows)} ctl={ctl} ctlwin={ctlwin} ctlmode={ {0:'off/none',1:'foreign-thread',2:'owner-ctx(CTLF)'}[mode] }")
by = {}
race, xw = [], 0
for r in rows:
    n, intr, xc, kind = int(r[0]), int(r[9]), int(r[10]), r[4]
    by.setdefault((r[3], kind, r[7], r[6]), []).append((float(r[8]), xc, intr))
    if xc: xw += 1
    if n == ctlwin or r[3].startswith('initMainHeap'):
        continue
    if intr or kind == 'F':
        race.append(r)
for k, v in sorted(by.items()):
    us = sorted(x[0] for x in v)
    print(f"  open={k[0]:<28} close={k[1]} ckey={k[2]:<34} cres={k[3]:>3} n={len(v):3d} us_med={us[len(us)//2]:.0f} us_max={us[-1]:.0f} "
          f"xwin={sum(1 for x in v if x[1])} intr={sum(x[2] for x in v)}")
cw = [r for r in rows if int(r[0]) == ctlwin]
ctl_ok = mode != 0 and len(cw) == 1 and int(cw[0][9]) == 1
print(f"windows with another guest thread running (xcalls>0): {xw}/{len(rows)}; xcalls counter control: 20 ms after close "
      f"{shx} foreign calls in {shw} windows -> {'PASS' if shx > 0 else 'FAIL (xcalls=0 is not evidence)'}")
# first-create window (initMainHeap at boot) seeds a fresh queue: not a held re-seed, listed but excluded from the verdict
rows_v = [r for r in rows if not r[3].startswith('initMainHeap')]
for r in race[:20]:
    print('RACE', ' '.join(r))
print('heap-mutex recv by guest thread id (whole run):', tidl)
if not rows:
    print('NO WINDOWS'); sys.exit(2)
FIX = '--fix' in sys.argv  # HOLDFIX arm: the planted take must FIND NO TOKEN inside the window (ctl == 0 after an attempt)
if FIX:
    ctl_ok = mode != 0 and ctl == 0
    print('FIX-ARM CONTROL', 'PASS (planted take found no free token in window)' if ctl_ok else 'FAIL', 'skips:', re.findall(r'holdfix_skips=\d+', tidl))
    if not ctl_ok: sys.exit(2)
elif mode:
    print('CONTROL', 'PASS' if ctl_ok else 'FAIL', cw[0] if cw else '(control window not closed)')
    if not ctl_ok: sys.exit(2)
if shx == 0:
    print('XCALLS CONTROL FAIL'); sys.exit(2)
print('VERDICT', 'H-race' if race else 'H-none')
sys.exit(3 if race else 0)
