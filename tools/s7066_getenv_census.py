#!/usr/bin/env python3
"""s7066 hot-getenv census: classify every getenv( site as cached vs per-call.
cached  = on a `static ... = ...getenv` line, or inside a block guarded by a
          once-pattern (`< 0`, `== -1`, `!init`, `_init`, `once`, `static int` sentinel)
          within the preceding 6 lines.
percall = everything else. Reports per-call sites by enclosing function.
usage: s7066_getenv_census.py <files...>"""
import sys, re, collections
FUNC = re.compile(r'^(?:RECOMP_FUNC\s+)?[A-Za-z_][\w\s\*:<>,]*?\b([A-Za-z_]\w*)\s*\([^;]*\)\s*\{?\s*$')
ONCE = re.compile(r'(<\s*0|==\s*-1|!\s*\w*init\w*|\w*_init\w*\s*\)|once|inited|s_\w+\s*==\s*-?\d|\bif\s*\(\s*!\s*\w+_?(?:done|checked|read)\b)')
res = collections.defaultdict(list)
tot = collections.Counter()
for fn in sys.argv[1:]:
    try: lines = open(fn, errors='ignore').read().split('\n')
    except Exception: continue
    cur = '?'
    for i, l in enumerate(lines):
        if l and not l[0].isspace() and '(' in l and not l.rstrip().endswith(';'):
            m = FUNC.match(l)
            if m: cur = m.group(1)
        if 'getenv(' not in l or l.lstrip().startswith('//'): continue
        for m in re.finditer(r'getenv\(\s*"?([A-Za-z0-9_]*)', l):
            if re.match(r'\s*static\b', l) or re.search(r'\bstatic\b[^;]*=[^;]*getenv', l):
                k = 'cached'
            elif any(ONCE.search(x) for x in lines[max(0, i-6):i+1]):
                k = 'cached'
            else:
                k = 'percall'
            tot[k] += 1
            if k == 'percall': res[cur].append((fn.split('/')[-1], i+1, m.group(1)))
print('totals', dict(tot))
for f, v in sorted(res.items(), key=lambda x: -len(x[1])):
    print(f'{len(v):4d} {f}: ' + ', '.join(f'{a}:{b}:{c}' for a, b, c in v[:6]))
