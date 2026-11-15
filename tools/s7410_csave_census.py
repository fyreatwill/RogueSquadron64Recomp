#!/usr/bin/env python3
"""s7410 class BT census: callee-saved register preservation across the FR=1 hand-asm routines and their FR=1 callees.
Caller contract (GCC o32, FR=0): f20,f22,..,f30 doubles, s0-s7 (r16-r23), s8 (r30), sp (r29), ra-as-return survive a call.
Two models of what the FR=0 caller sees after return, for each even pair N (20..30):
  recomp : ctx->fN.u64 (both halves live in fN's slot; the FR=0 odd single f(N+1) is fN.u32h)
  hardware (VR4300): physical fN.lo32 + physical f(N+1).lo32 (FR=1 writes to fN.hi32 are invisible to FR=0)
A routine is safe in BOTH models for pair N when it saves fN with sdc1 in an FR=0 region and restores it with ldc1 in an
FR=0 region (an FR=0 sdc1/ldc1 moves the whole caller pair). An FR=1 save of fN covers only fN; f(N+1) then needs its own.
Writes are collected transitively through direct callees made inside the FR=1 region.
Rows: PAIR <fn> fN written=<regs> save=<FR> restore=<FR> -> preserved / CLOBBER-recomp / CLOBBER-hw / untouched.
GPR rows: s-reg / s8 written without an sw/lw pair on the stack, sp not balanced.
Usage: s7410_csave_census.py <RecompiledFuncs dir> [--plant]   (--plant drops one ldc1 restore from a copy of
mat3x4Multiply and plants an unsaved s0 write: both must be flagged -> CONTROL PASS)"""
import os, re, sys
src = sys.argv[1]; plant = '--plant' in sys.argv
ROUTINES = ['transformAndEmitFaceVertices', 'evalCubicSplineAtTime', 'mat3x4Multiply', 'transformVec3ByMat34',
            'rotateVec3ByMat3x3', 'quaternionToMat3x4', 'projectPointToScreen']
fn_re = re.compile(r'^RECOMP_FUNC void (\w+)\(')
wr_f = re.compile(r'ctx->f(\d+)\.(fl|d|u32l|u32h|u64)\s*=(?!=)')
wr_odd = re.compile(r'ctx->f_odd\[\((\d+) - 1\) \* 2\]\s*=(?!=)')
wr_r = re.compile(r'ctx->r(\d+)\s*=(?!=)')
sv_f = re.compile(r'SD\(ctx->f(\d+)\.u64, (0X[0-9A-F]+), ctx->r29\)')
rs_f = re.compile(r'ctx->f(\d+)\.u64 = LD\(ctx->r29, (0X[0-9A-F]+)\)')
sv_r = re.compile(r'MEM_W\((0X[0-9A-F]+), ctx->r29\) = ctx->r(\d+);')
rs_r = re.compile(r'ctx->r(\d+) = MEM_W\(ctx->r29, (0X[0-9A-F]+)\);')
sp_re = re.compile(r'ctx->r29 = ADD32\(ctx->r29, (-?0X[0-9A-F]+)\)')
call_re = re.compile(r'^\s*(\w+)\(rdram, ctx\);')
bodies = {}
for name in sorted(os.listdir(src)):
    if not name.endswith('.c'): continue
    cur = None
    for ln in open(os.path.join(src, name), errors='replace').read().split('\n'):
        m = fn_re.match(ln)
        if m: cur = m.group(1); bodies[cur] = []; continue
        if cur: bodies[cur].append(ln)
if plant:
    b = list(bodies['mat3x4Multiply']); out = []; dropped = False
    for ln in b:
        if not dropped and 'ctx->f22.u64 = LD(ctx->r29' in ln: dropped = True; continue
        out.append(ln)
    i = next(k for k, ln in enumerate(out) if 'cop0_status_write' in ln)
    out.insert(i + 1, '    ctx->r16 = ADD32(ctx->r4, 0X4);')
    bodies['PLANT_mat3x4Multiply'] = out; ROUTINES = ROUTINES + ['PLANT_mat3x4Multiply']

def scan(fname, fr_entry, seen):
    """returns dict: fw[N]=set(FR) written, gw set, saves/restores, callees; writes from FR=1 callees merged."""
    r = dict(fw={}, gw={}, fsave={}, frest={}, gsave={}, grest={}, sp=[], calls=set(), status=0)
    fr = fr_entry; prev = ''
    for ln in bodies.get(fname, []):
        code = ln.split('//')[0]
        if 'g_rs64' in code or 'RS64_' in code and not code.strip().startswith('{'):
            pass
        if 'cop0_status_write' in code:
            r['status'] += 1
            fr = 1 if ' | ' in prev else 0 if ' & ' in prev else fr
        for m in wr_f.finditer(code): r['fw'].setdefault(int(m.group(1)), set()).add(fr)
        for m in wr_odd.finditer(code):  # FR=0 -> f(N-1).u32h, FR=1 -> fN.u32l
            n = int(m.group(1)); r['fw'].setdefault(n if fr else n - 1, set()).add(fr)
        for m in sv_f.finditer(code): r['fsave'].setdefault(int(m.group(1)), set()).add(fr)
        for m in rs_f.finditer(code): r['frest'].setdefault(int(m.group(1)), set()).add(fr)
        if 'g_rs64' not in code:
            for m in sv_r.finditer(code): r['gsave'].setdefault(int(m.group(2)), set()).add(fr)
            for m in rs_r.finditer(code): r['grest'].setdefault(int(m.group(1)), set()).add(fr)
            for m in wr_r.finditer(code):
                n = int(m.group(1))
                if not rs_r.search(code) or int(rs_r.search(code).group(1)) != n: r['gw'].setdefault(n, set()).add(fr)
            for m in sp_re.finditer(code): r['sp'].append(int(m.group(1), 16))
        c = call_re.match(code)
        if c and c.group(1) not in ('cop0_status_write', 'cop0_status_read'):
            r['calls'].add((c.group(1), fr))
        if code.strip() and 'g_rs64' not in code: prev = code
    for (cal, cfr) in sorted(r['calls']):
        if cal in seen: continue
        sub = scan(cal, cfr, seen | {cal})
        for n, s in sub['fw'].items():
            # a callee's net effect is its writes minus what it restores itself
            if n in sub['fsave'] and n in sub['frest']: continue
            r['fw'].setdefault(n, set()).update(s)
        for n, s in sub['gw'].items():
            if n in sub['gsave'] and n in sub['grest']: continue
            r['gw'].setdefault(n, set()).update(s)
    return r

flags = {}
for f in ROUTINES:
    if f not in bodies: print(f"MISSING {f}"); continue
    r = scan(f, 0, {f}); bad = []
    for N in range(20, 31, 2):
        wN = r['fw'].get(N, set()); wO = r['fw'].get(N + 1, set())
        if not wN and not wO: continue
        sv = r['fsave'].get(N, set()); rs = r['frest'].get(N, set())
        svO = r['fsave'].get(N + 1, set()); rsO = r['frest'].get(N + 1, set())
        pair_ok = 0 in sv and 0 in rs                      # FR=0 sdc1/ldc1: whole caller pair, both models
        even_ok = pair_ok or (sv and rs)                     # FR=1 save covers fN 64-bit
        odd_ok = pair_ok or (svO and rsO) or not wO
        rec = 'ok' if (not wN or even_ok) else 'CLOBBER'     # recomp caller sees fN.u64; odd own slot invisible
        hw = 'ok' if ((not wN or even_ok) and odd_ok) else 'CLOBBER'
        verdict = 'preserved' if rec == hw == 'ok' else f"recomp={rec} hw={hw}"
        if verdict != 'preserved': bad.append(f"f{N}")
        print(f"PAIR {f} f{N}/f{N+1} wrote_even={sorted(wN)} wrote_odd={sorted(wO)} save={sorted(sv)} restore={sorted(rs)} -> {verdict}")
    for n in list(range(16, 24)) + [30]:
        if n in r['gw']:
            ok = n in r['gsave'] and n in r['grest']
            print(f"GPR  {f} r{n} written fr={sorted(r['gw'][n])} saved={n in r['gsave']} restored={n in r['grest']} -> {'preserved' if ok else 'CLOBBER'}")
            if not ok: bad.append(f"r{n}")
    spsum = sum(r['sp'])
    # an ADD32(-X) prologue and one ADD32(+X) per return path: balanced when the positives equal |negative| each
    neg = [x for x in r['sp'] if x < 0]; pos = [x for x in r['sp'] if x > 0]
    sp_ok = (not neg and not pos) or (len(neg) == 1 and all(p == -neg[0] for p in pos) and pos)
    if not sp_ok: bad.append('sp')
    print(f"SP   {f} adj={r['sp']} -> {'balanced' if sp_ok else 'UNBALANCED'}  ra_written={31 in r['gw'] and 31 not in r['grest']}  callees={sorted(r['calls'])}")
    flags[f] = bad
    print(f"ROW  {f} -> {'H-preserved' if not bad else 'CLOBBERED ' + ','.join(bad)}")
real = {f: b for f, b in flags.items() if not f.startswith('PLANT') and b}
print("VERDICT", "H-preserved-static" if not real else f"H-clobber {real}",
      ("CONTROL " + ("PASS" if set(flags.get('PLANT_mat3x4Multiply', [])) >= {'f22', 'r16'} else "FAIL")) if plant else "")
