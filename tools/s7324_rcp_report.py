#!/usr/bin/env python3
"""s7324 class G report: reads build/rs64_s7324.log (ROGUESQ_S7324_RCPREF=ctl + ROGUESQ_S7317_ALLOCMAP=1, src/rsp/s7324_rcp_spill.cpp).
Exit 1 if any RCP address is direct-spill / direct-other, the control failed, or an alias-only hit carries a tag other than 0x80
(or 0x00 inside the static image), i.e. something that could be a masked spill pointer. Alias-only hits are triaged into static
(below the first live heap block) and heap-gap (no live block; audio stream reads seen at s7324)."""
import re, sys, collections
path = sys.argv[1] if len(sys.argv) > 1 else 'build/rs64_s7324.log'
txt = open(path).read().splitlines()
rc = 0
hdr = txt[0]; print(hdr)
m = dict(re.findall(r'(\w+)=(\d+)', hdr))
if int(m.get('ctl_direct_ok', 0)) == 0 or m.get('ctl_direct_ok') != m.get('ctl_alias_ok'):
    print('CONTROL FAIL'); rc = 1
for l in txt:
    if l.startswith('SRC '):
        print(l[:120]); d = dict(re.findall(r'(\w+)=(\d+)', l))
        if int(d['direct_spill']) or int(d['direct_other']): print('  DIRECT HIT'); rc = 1
        tags = l.split('tag00/80/other:')[1].split()
        if tags[2].split('/')[2] != '0': print('  alias_only with foreign tag'); rc = 1
cat = collections.Counter(); n = collections.Counter(); ex = {}
for l in txt:
    if not l.startswith('DI '): continue
    d = dict(re.findall(r'(\w+)=([0-9A-Fa-f.]+)', l)); src, cls = l.split()[1:3]
    lo = int(d['near_lo'].split('..')[0], 16)
    raw = int(d['raw0'], 16) >> 24
    k = (src, cls, 'static' if lo == 0 else 'heap-gap', 'tag%02X' % raw)
    if raw not in (0, 0x80) or (raw == 0 and lo != 0): rc = 1
    cat[k] += 1; n[k] += int(d['n']); ex.setdefault(k, l[:150])
for k in sorted(cat): print(k, 'distinct', cat[k], 'n', n[k], '\n   ', ex[k])
print('DI_OVERFLOW', [l for l in txt if l.startswith('DI_OVERFLOW')])
print('VERDICT', 'FAIL' if rc else 'class G clean: no RCP address is a spill block (direct 0, aliases all static/heap-tag)')
sys.exit(rc)
