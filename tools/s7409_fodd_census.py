#!/usr/bin/env python3
"""s7409 class BS census: odd-FPR access views per recompiled function.
Generator (N64Recomp cgenerator.cpp): float/double arithmetic operands -> ctx->fN.fl / ctx->fN.d (own slot, FR=1 view);
mtc1/mfc1/lwc1/swc1 operands -> ctx->f_odd[(N-1)*2] for odd N (runtime view: FR=0 -> f(N-1).u32h, FR=1 -> fN.u32l).
Rows: per function, odd accesses split by static FR region (between cop0_status_write after OR and after AND).
MIXED = FR=0 region touching an odd reg through the own-slot view (fODD.fl/.d/.u32l/.u64) -- under FR=0 that slot is
not where f_odd writes go. Also lists calls made inside FR=1 regions (callees run with FR=1).
Usage: s7409_fodd_census.py <RecompiledFuncs dir> [--plant]   (--plant injects a synthetic FR0-called MIXED row: positive control)"""
import os, re, sys
src = sys.argv[1]; plant = '--plant' in sys.argv
fn_re = re.compile(r'^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC void (\w+)\(')
fodd_re = re.compile(r'ctx->f_odd\[\((\d+) - 1\) \* 2\](\s*=(?!=))?')
own_re = re.compile(r'ctx->f(\d+)\.(fl|d|u32l|u32h|fh|u64)')
call_re = re.compile(r'^\s*(\w+)\(rdram, ctx\);')
rows = {}
def row(f):
    return rows.setdefault(f, dict(fodd=[0,0], own_odd={0:0,1:0}, fodd_regs=set(), own_regs={0:set(),1:set()},
                                   even_hi=0, fr1_calls=set(), fr0_calls=set(), status_writes=0, fr1_lines=0, ex={}))
for name in sorted(os.listdir(src)):
    if not name.endswith('.c'): continue
    cur = None; fr = 0
    lines = open(os.path.join(src, name), errors='replace').read().split('\n')
    if plant and name == sorted(n for n in os.listdir(src) if n.endswith('.c'))[0]:
        lines += ['RECOMP_FUNC void PLANT_mixed(uint8_t* rdram, recomp_context* ctx) {',
                  '    ctx->f_odd[(7 - 1) * 2] = MEM_W(ctx->r4, 0);', '    ctx->r2 = CVT_W_S(ctx->f7.fl);', '}',
                  'RECOMP_FUNC void PLANT_caller(uint8_t* rdram, recomp_context* ctx) {', '    PLANT_mixed(rdram, ctx);', '}']
    prev = ''
    for ln in lines:
        m = fn_re.match(ln)
        if m: cur = m.group(1); fr = 0; continue
        if cur is None: continue
        r = row(cur)
        if 'cop0_status_write' in ln:
            r['status_writes'] += 1
            fr = 1 if ' | ' in prev else 0 if ' & ' in prev else fr
        if fr: r['fr1_lines'] += 1
        code = ln.split('//')[0]
        for mm in fodd_re.finditer(code):
            r['fodd'][fr] += 1; r['fodd_regs'].add(int(mm.group(1)))
        for mm in own_re.finditer(code):
            n = int(mm.group(1)); v = mm.group(2)
            if n & 1:
                r['own_odd'][fr] += 1; r['own_regs'][fr].add(n)
                r['ex'].setdefault((fr, n), ln.strip()[:110])
            elif v in ('u32h', 'fh'): r['even_hi'] += 1
        c = call_re.match(code)
        if c and c.group(1) != 'cop0_status_write': r['fr1_calls' if fr else 'fr0_calls'].add(c.group(1))
        if code.strip(): prev = code
tot = dict(fodd=0, own_odd=0)
mixed = []; fr1 = []
for f, r in rows.items():
    if r['status_writes']: fr1.append(f)
    if r['own_odd'][0]: mixed.append(f)
nf = sum(1 for r in rows.values() if sum(r['fodd']))
print(f"functions={len(rows)} with_f_odd={nf} f_odd_uses={sum(sum(r['fodd']) for r in rows.values())} "
      f"even_hi_uses={sum(r['even_hi'] for r in rows.values())} status_write_funcs={len(fr1)} mixed_fr0={len(mixed)}")
for f in sorted(fr1):
    r = rows[f]
    print(f"FR1FN {f} status_writes={r['status_writes']} fr1_lines={r['fr1_lines']} f_odd(fr0/fr1)={r['fodd']} "
          f"own_odd(fr0/fr1)={r['own_odd'][0]}/{r['own_odd'][1]} fr1_calls={sorted(r['fr1_calls'])}")
for f in sorted(rows):
    r = rows[f]
    if sum(r['fodd']) and f not in fr1:
        print(f"FODD {f} f_odd={sum(r['fodd'])} regs={sorted(r['fodd_regs'])} own_odd={r['own_odd'][0]}")
callers0 = {}; callers1 = {}
for g, r in rows.items():
    for c in r['fr0_calls']: callers0.setdefault(c, set()).add(g)
    for c in r['fr1_calls']: callers1.setdefault(c, set()).add(g)
live_mixed = []
for f in sorted(mixed):
    r = rows[f]
    k = ('FR1-ONLY-CALLEE' if callers1.get(f) and not callers0.get(f) else
         'NO-DIRECT-CALLER' if not callers1.get(f) and not callers0.get(f) else 'FR0-CALLED')
    if k == 'FR0-CALLED': live_mixed.append(f)
    print(f"MIXED {f} kind={k} fr1_callers={sorted(callers1.get(f, ()))} fr0_callers={sorted(callers0.get(f, ()))[:4]}")
    print(f"      {f} own_odd_fr0={r['own_odd'][0]} regs={sorted(r['own_regs'][0])} f_odd_regs={sorted(r['fodd_regs'])} "
          f"ex={[v for (k, n), v in r['ex'].items() if k == 0][:2]}")
# FR1-ONLY-CALLEE rows are consistent (they only run with FR=1, where the own slot IS the odd register); NO-DIRECT-CALLER
# rows need the live probe (indirect calls) -- tools/build_fodd.sh. Only FR0-CALLED rows are static defects.
print("VERDICT", "H-mixed-live" if live_mixed else "H-consistent-static", f"mixed_rows={len(mixed)} fr0_called={live_mixed}", ("CONTROL " + ("PASS" if 'PLANT_mixed' in live_mixed else "FAIL")) if plant else "")
