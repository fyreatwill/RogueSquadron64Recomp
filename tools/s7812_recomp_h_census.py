#!/usr/bin/env python3
"""s7812: recomp.h helper-semantics class census + memory-layer differential test.

Class: every static-inline helper and function-like macro in the LIVE recomp.h
(lib/N64ModernRuntime/N64Recomp/include/recomp.h, which carries our s7085 / diag patches) is code that the
generated game calls in place of a MIPS instruction. A live helper (>=1 call in ../N64Recomp/RecompiledFuncs or
RecompiledPatches) needs evidence that it computes what the R4300 computes:
  TEST   a differential test source that exercises the name (the name must appear in that source), or
  CENSUS a closed session census (the session header must exist in PORTING-STATE.md).
Verdicts per helper: COVERED / DEAD (0 live calls) / PASSTHRU (pure cast or diag plumbing, named here) /
OPEN (live, no evidence -> RED). A new helper the generator starts emitting reads OPEN until it gets a row.

The memory-layer test (tools/s7812_mem_test/mem_test.c) is run here: MEM_B/BU/H/HU/W, LD, SD, do_lwl/lwr/swl/swr,
do_ldl/ldr/sdl/sdr and get/set_cop1_cs vs an independent big-endian byte model; 3 mutants must fail.

  --controls   also run the census controls (planted live helper with no row -> OPEN; planted dead -> DEAD;
               planted row whose session header is missing -> OPEN) and the 3 mutant builds.
Exit 0 iff CLASS VERDICT GREEN (and, with --controls, every control PASS)."""
import glob, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
HDR = os.path.join(ROOT, 'lib/N64ModernRuntime/N64Recomp/include/recomp.h')
GEN = glob.glob(os.path.join(ROOT, '../N64Recomp/RecompiledFuncs/*.c')) + glob.glob(os.path.join(ROOT, 'RecompiledPatches/*.c'))
OUT = os.path.join(ROOT, 'scratch', 's7812')

T85 = 'tools/s7085_int_test/int_test.c'
T84 = 'tools/s7084_fpu_test/fpu_test.c'
T12 = 'tools/s7812_mem_test/mem_test.c'
# name -> evidence list: ('TEST', path) or ('CENSUS', 'Session N')
EVID = {
    'ADD32': [('TEST', T85)], 'SUB32': [('TEST', T85)], 'S32': [('TEST', T85)], 'U32': [('TEST', T85)],
    'S64': [('TEST', T85)], 'U64': [('TEST', T85)], 'SIGNED': [('TEST', T85)],
    'DDIV': [('TEST', T85)], 'DDIVU': [('TEST', T85)], 'DMULT': [('TEST', T85)], 'DMULTU': [('TEST', T85)],
    'do_lwl': [('TEST', T85), ('TEST', T12)], 'do_lwr': [('TEST', T85), ('TEST', T12)],
    'do_swl': [('TEST', T85), ('TEST', T12)], 'do_swr': [('TEST', T85), ('TEST', T12)],
    'do_ldl': [('TEST', T12)], 'do_ldr': [('TEST', T12)], 'do_sdl': [('TEST', T12)], 'do_sdr': [('TEST', T12)],
    'MEM_B': [('TEST', T12)], 'MEM_BU': [('TEST', T12)], 'MEM_H': [('TEST', T12)], 'MEM_HU': [('TEST', T12)],
    'MEM_W': [('TEST', T12)], 'LD': [('TEST', T12)], 'SD': [('TEST', T12)], 'load_doubleword': [('TEST', T12)],
    'get_cop1_cs': [('TEST', T12), ('CENSUS', 'Session 4816'), ('CENSUS', 'Session 7405')],
    'set_cop1_cs': [('TEST', T12), ('CENSUS', 'Session 4816'), ('CENSUS', 'Session 7405')],
    # FPU lowering: s7084 differential (rounding modes) + s7415 exact-rational IEEE model + s7576 trunc UB
    **{n: [('CENSUS', 'Session 7084'), ('CENSUS', 'Session 7415')] for n in
       ('MUL_S', 'MUL_D', 'DIV_S', 'DIV_D', 'CVT_S_W', 'CVT_D_W', 'CVT_D_S', 'CVT_S_D', 'CVT_D_L', 'CVT_S_L',
        'CVT_L_D', 'CVT_L_S', 'CVT_W_D', 'CVT_W_S', 'do_cvt_w_s', 'do_cvt_w_d', 'do_cvt_l_s', 'do_cvt_l_d')},
    **{n: [('CENSUS', 'Session 7576'), ('CENSUS', 'Session 7084')] for n in ('TRUNC_W_S', 'TRUNC_W_D', 'TRUNC_L_S', 'TRUNC_L_D')},
    'NAN_CHECK': [('CENSUS', 'Session 7415')], 'CHECK_FR': [('CENSUS', 'Session 7415'), ('CENSUS', 'Session 7405')],
    'LOOKUP_FUNC': [('CENSUS', 'Session 7771')],
}
PASSTHRU = {  # no guest-visible computation: relocation helpers for mods, and our default-off diag plumbing
    'HI16', 'LO16', 'RELOC_HI16', 'RELOC_LO16', 'rs64_bwatch', 'rs64_g1d_blk_maybe',
}

def helpers(text):
    return sorted(set(re.findall(r'^static inline [\w \*]+?\b(\w+)\(', text, re.M) + re.findall(r'^#define (\w+)\(', text, re.M)))

def classify(names, src, evid, ps_heads, srcs):
    rows = []
    for n in names:
        live = len(re.findall(r'\b' + re.escape(n) + r'\(', src))
        ok = []
        for kind, ref in evid.get(n, []):
            if kind == 'TEST' and re.search(r'\b' + re.escape(n) + r'\b', srcs.get(ref, '')): ok.append(ref)
            if kind == 'CENSUS' and ref in ps_heads: ok.append(ref)
        v = 'COVERED' if ok else 'PASSTHRU' if n in PASSTHRU else 'DEAD' if live == 0 else 'OPEN'
        rows.append((n, live, v, ok))
    return rows

def run_mem(defs, tag, trials=200000):
    os.makedirs(OUT, exist_ok=True)
    exe = os.path.join(OUT, 'mem_test' + tag)
    inc = [os.path.join(ROOT, p) for p in ('include', 'lib/N64ModernRuntime/ultramodern/include',
           'lib/N64ModernRuntime/librecomp/include', 'lib/N64ModernRuntime/N64Recomp/include')]
    cmd = ['cc', '-g', '-std=gnu17', '-arch', 'arm64', '-O2', '-fno-strict-aliasing', '-w'] + defs + \
          sum((['-I', i] for i in inc), []) + [os.path.join(ROOT, T12), '-o', exe]
    subprocess.check_call(cmd)
    out = subprocess.run([exe, str(trials)], capture_output=True, text=True, check=True).stdout
    bad = int(re.search(r'TOTAL_BAD (\d+)', out).group(1))
    ops = {m.group(1): (int(m.group(2)), int(m.group(3))) for m in re.finditer(r'op (\S+)\s+n=(\d+) bad=(\d+)', out)}
    return bad, ops, out

def main():
    controls = '--controls' in sys.argv
    text = open(HDR).read()
    src = ''.join(open(f, errors='replace').read() for f in GEN)
    ps = open(os.path.join(ROOT, 'PORTING-STATE.md'), errors='replace').read()
    ps_heads = set(re.findall(r'^## (Session \d+) ', ps, re.M))
    srcs = {p: open(os.path.join(ROOT, p)).read() for p in (T85, T84, T12)}
    names = helpers(text)
    rows = classify(names, src, EVID, ps_heads, srcs)
    cnt = {}
    for n, live, v, ok in rows:
        cnt[v] = cnt.get(v, 0) + 1
        print(f"{n:20s} live={live:7d} {v:8s} {','.join(ok)}")
    print(f"helpers {len(names)} gen_files {len(GEN)} " + ' '.join(f"{k}={cnt[k]}" for k in sorted(cnt)))
    green = cnt.get('OPEN', 0) == 0 and len(GEN) > 0 and len(names) >= 40

    bad, ops, out = run_mem([], '')
    hollow = [k for k, (n, b) in ops.items() if n == 0]
    print(out.rstrip())
    print(f"MEM TEST {'PASS' if bad == 0 and not hollow else 'FAIL'} total_bad={bad} hollow_ops={hollow}")
    green = green and bad == 0 and not hollow

    allc = True
    if controls:
        live_names = [n for n, l, v, o in rows if l > 0]
        c1 = classify(['RS64_PLANTED'], src + ' RS64_PLANTED(x) ', EVID, ps_heads, srcs)[0][2] == 'OPEN'
        c2 = classify(['RS64_PLANTED'], src, EVID, ps_heads, srcs)[0][2] == 'DEAD'
        ev = dict(EVID); ev['MUL_S'] = [('CENSUS', 'Session 99999999')]
        c3 = classify(['MUL_S'], src, ev, ps_heads, srcs)[0][2] == 'OPEN'
        ev = dict(EVID); ev['MEM_H'] = [('TEST', T84)]  # a test source that never names MEM_H
        c4 = classify(['MEM_H'], src, ev, ps_heads, srcs)[0][2] == 'OPEN'
        for nm, ok in (('planted live helper without row -> OPEN', c1), ('planted dead helper -> DEAD', c2),
                       ('row citing a missing session -> OPEN', c3), ('TEST row whose source lacks the name -> OPEN', c4)):
            print(f"CENSUS CONTROL {'PASS' if ok else 'FAIL'} {nm}"); allc &= ok
        for d, want in (('-DMUT_H', ('lh', 'lhu')), ('-DMUT_SD', ('sd',)), ('-DMUT_LDR', ('ldr',))):
            mb, mops, _ = run_mem([d], d[2:].lower(), 20000)
            hit = [k for k in want if mops[k][1] > 0] or (mb > 0 and d == '-DMUT_SD')
            ok = mb > 0 and bool(hit)
            print(f"MUTANT CONTROL {'PASS' if ok else 'FAIL'} {d} total_bad={mb} " + ' '.join(f"{k}={mops[k][1]}" for k in want))
            allc &= ok
        print(f"CONTROLS {'PASS' if allc else 'FAIL'}")
    print(f"CLASS VERDICT {'GREEN' if green else 'RED'} open={cnt.get('OPEN', 0)}")
    sys.exit(0 if green and allc else 1)

if __name__ == '__main__':
    main()
