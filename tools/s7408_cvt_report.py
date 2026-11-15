#!/usr/bin/env python3
"""s7408 class BR report: last [s7408-dump] block of a build_cvt run log.
CONTROL PASS = plant>0 and plant_oor == plant (every planted out-of-range input classified UNIMPL) and >=1 site with max>0.
VERDICT H-equal = control PASS, mism=0 (in-range host == VR4300 model on every live call), oor=0 (no live site ever needs
the retail-faulting path). Otherwise H-wrap-live (oor at a CVT_W site: host wraps) / H-oor-trunc (oor at TRUNC: host
saturates) with the site list. Usage: s7408_cvt_report.py <run.log> [--top N]   rc 0 = H-equal + control PASS."""
import re, sys
log = sys.argv[1]; top = int(sys.argv[sys.argv.index('--top') + 1]) if '--top' in sys.argv else 12
blk = None; cur = None; oors = []; mis = []
for ln in open(log, errors='replace'):
    if ln.startswith('[s7408-dump]'): cur = [ln]; blk_hdr = ln
    elif ln.startswith('[s7408-site]') and cur is not None: cur.append(ln)
    elif ln.startswith('[s7408-oor]'): oors.append(ln.strip())
    elif ln.startswith('[s7408-mism]'): mis.append(ln.strip())
    if cur is not None and ln.startswith('[s7408-dump]'): blk = cur
if not blk: print('VERDICT no-data (no [s7408-dump])'); sys.exit(3)
h = dict(kv.split('=') for kv in blk[0].split()[2:] if '=' in kv)
sites = []
for ln in blk[1:]:
    d = dict(kv.split('=', 1) for kv in ln.split()[1:] if '=' in kv); sites.append(d)
print('DUMP', blk[0].strip())
live = [s for s in sites if int(s['calls']) > 0]
bykind = {}
for s in live:
    k = s['kind']; b = bykind.setdefault(k, [0, 0, 0, 0.0]); b[0] += 1; b[1] += int(s['calls']); b[2] += int(s['oor']); b[3] = max(b[3], float(s['max']))
for k, b in sorted(bykind.items()): print('KIND %s live_sites=%d calls=%d oor=%d max=%.6g' % (k, b[0], b[1], b[2], b[3]))
for s in sorted(live, key=lambda s: -float(s['max']))[:top]:
    print('TOPMAX pc=%s fn=%s kind=%s calls=%s max=%s oor=%s rmz=%s' % (s['pc'], s['fn'], s['kind'], s['calls'], s['max'], s['oor'], s['rmz']))
for s in live:
    if s['kind'].startswith('CVT'): print('CVTSITE pc=%s fn=%s calls=%s max=%s oor=%s rmz=%s' % (s['pc'], s['fn'], s['calls'], s['max'], s['oor'], s['rmz']))
for l in oors[:10]: print(l)
for l in mis[:10]: print(l)
pl, po = int(h['plant']), int(h['plant_oor'])
ctl = pl > 0 and po == pl and any(float(s['max']) > 0 for s in live)
print('CONTROL %s plant=%d plant_oor=%d live_sites=%d' % ('PASS' if ctl else 'FAIL', pl, po, len(live)))
oor, mm = int(h['oor']), int(h['mism'])
oorsites = [s for s in live if int(s['oor']) > 0]
if not ctl: v = 'unevaluable (control FAIL)'
elif mm: v = 'H-mismatch (in-range host != model, %d)' % mm
elif not oor: v = 'H-equal (oor=0 mism=0)'
elif any(s['kind'].startswith('CVT') for s in oorsites): v = 'H-wrap-live ' + ','.join(s['pc'] + ':' + s['fn'] for s in oorsites)
else: v = 'H-oor-trunc ' + ','.join(s['pc'] + ':' + s['fn'] for s in oorsites)
print('VERDICT', v)
sys.exit(0 if ctl and v.startswith('H-equal') else 3)
