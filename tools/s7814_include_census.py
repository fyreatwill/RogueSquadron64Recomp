#!/usr/bin/env python3
"""s7814: generated-C INCLUDE-RESOLUTION census (sibling of s7812 recomp.h helpers / s7813 host callees).

s7813 found s7812 scanned recomp.h only while CMake force-includes include/rsp_dpc_macros.h. The class: a header the
generated C really compiles against that no census reads, or a census reading a different copy than the compiler.
Ask the compiler, not the CMake text. Two independent sources of the resolved header set per (build dir, target):
  A  the compiler's own dependency files (CMakeFiles/<target>.dir/**/*.o.d) for EVERY generated TU
  B  a fresh `-M` run of the real compile command (`make -n -B` on one object per target), today's sources
Targets: RecompiledFuncs (game C), PatchesLib (RecompiledPatches host compile), factor5_ucode TUs (LLE RSP C).
Build dirs: build (shipped) + build_fbld / build_spwm / build_asan when present.
Rows per resolved header:
  SYSTEM   SDK / toolchain path
  SCANNED  basename named by a census or harness tool (SCANNERS)
  DECL     project header with no function-like macro and no function body (prototypes / types only)
  OPEN     project header with >=1 helper (function-like macro / inline body) called in the TUs and no scanner
  SHADOW   same basename resolving to different paths across builds; OPEN if the shipped build resolves a copy no
           scanner reads, or a scanner reads a path the shipped build does not resolve (SHADOW-MISS)
Per-helper map for the ucode TUs: every rsp.<op> and RSP_*/DMA macro the generated LLE C calls -> evidence session.
--controls: planted -include of a scratch header carrying a live-named macro -> OPEN; scanner path redirected to
include/fbld/recomp.h -> SHADOW-MISS; rsp_dpc_macros.h dropped from SCANNERS -> OPEN; VMOV evidence dropped -> OPEN.
Exit 0 iff 0 OPEN, A == B on every pair, and (with --controls) every control fires."""
import glob, os, re, shlex, subprocess, sys, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BUILDS = ['build', 'build_fbld', 'build_spwm', 'build_asan']
SYS_MARK = ('/Applications/Xcode', '/Library/Developer', '/usr/include', 'SDKs/', '/usr/lib/clang', '/opt/homebrew/Cellar/llvm')
# tool file -> session. A header is SCANNED by a tool when the tool text names its basename.
SCANNERS = {
    'tools/s7812_recomp_h_census.py': 'Session 7812',      # recomp.h helper semantics
    'tools/s7813_callee_census.py': 'Session 7813',        # rsp_dpc_macros.h force-included helpers
    'tools/s7092_vu_mem_test/run.sh': 'Session 7092',      # rsp_vu.hpp, rsp_vu_impl.hpp, rsp.hpp DMEM block
    'tools/s7093_su_census.py': 'Session 7093',            # rsp.hpp scalar macros vs Python model
    'tools/rsp_vu_diff/run.sh': 'Session 6301',            # rsp_vu_impl.hpp SIMD vs SISD
    'tools/s7814_vmov_vsar/run.sh': 'Session 7814',        # VMOV/VSAR vs cxd4
}
EXTRA_NAMED = {  # headers a harness compiles against by -I without naming the file
    'sse2neon.h': [('tools/s7092_vu_mem_test/run.sh', 'Session 7092 (-I thirdparty/sse2neon, harness built on it)')],
}

def is_sys(p): return any(m in p for m in SYS_MARK)
def rel(p): p = os.path.realpath(p); return p[len(ROOT) + 1:] if p.startswith(ROOT + '/') else p

def dep_headers(txt):
    txt = txt.replace('\\\n', ' ')
    body = txt.split(':', 1)[1] if ':' in txt else ''
    return {rel(t) for t in body.split() if t.endswith(('.h', '.hpp', '.inc', '.inl'))}

def objs(b, t):
    fs = glob.glob(f'{ROOT}/{b}/CMakeFiles/{t}.dir/**/*.o.d', recursive=True)
    if t == 'RogueSquadron64Recomp': fs = [f for f in fs if '/factor5_ucode/' in f]
    return sorted(fs)

def source_a(b, t):
    s = collections.Counter(); fs = objs(b, t)
    for f in fs: s.update(dep_headers(open(f, errors='replace').read()))
    return len(fs), s

def compile_cmd(b, t, od):
    o = od[:-2]; obj = os.path.relpath(o, f'{ROOT}/{b}')
    r = subprocess.run(['make', '-n', '-B', '-f', f'CMakeFiles/{t}.dir/build.make', obj], cwd=f'{ROOT}/{b}',
                       capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if re.match(r'^\s*(cd \S+ && )?/\S*(cc|c\+\+|clang\+\+|clang)\s', line) and ' -c ' in line:
            return line.split('&&', 1)[1].strip() if line.lstrip().startswith('cd ') else line.strip()
    return None

def source_b(b, t, od, extra=None):
    cmd = compile_cmd(b, t, od)
    if not cmd: return None, None
    a = shlex.split(cmd); out = []; i = 0
    while i < len(a):
        x = a[i]
        if x in ('-o', '-MT', '-MF'): i += 2; continue
        if x in ('-MD', '-MMD', '-c'): i += 1; continue
        out.append(x); i += 1
    if extra: out[1:1] = extra
    r = subprocess.run(out + ['-M'], cwd=f'{ROOT}/{b}', capture_output=True, text=True)
    if r.returncode: return cmd, ('ERR', r.stderr[-400:])
    return cmd, dep_headers(r.stdout)

def strip_c(s):
    s = re.sub(r'/\*.*?\*/', ' ', s, flags=re.S); s = re.sub(r'//[^\n]*', ' ', s)
    return re.sub(r'"(\\.|[^"\\\n])*"', '""', s)

def helpers(path):
    s = strip_c(open(path, errors='replace').read()); h = set()
    h |= set(re.findall(r'^\s*#\s*define\s+([A-Za-z_]\w*)\(', s, re.M))
    for m in re.finditer(r'^[^\n#;{}]*?\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*(const\s*)?(->\s*[\w:<> ]+)?\s*\{', s, re.M):
        if m.group(1) not in ('if', 'while', 'for', 'switch', 'return', 'sizeof'): h.add(m.group(1))
    return h

def tu_sources(t):
    if t == 'RecompiledFuncs': return glob.glob(f'{ROOT}/../N64Recomp/RecompiledFuncs/*.c')
    if t == 'PatchesLib': return glob.glob(f'{ROOT}/RecompiledPatches/*.c')
    return glob.glob(f'{ROOT}/build/factor5_ucode/*.c')

_calls = {}
def call_counts(t):
    if t not in _calls:
        c = collections.Counter()
        for f in tu_sources(t):
            for m in re.finditer(r'\b([A-Za-z_]\w*)\s*(<[^<>()]*>)?\s*\(', strip_c(open(f, errors='replace').read())):
                c[m.group(1)] += 1
        _calls[t] = c
    return _calls[t]

def scanner_hits(h, scanners, ambiguous):
    # basename match only when the basename is unique among resolved headers; otherwise the tool must name dir/base
    base = os.path.basename(h); key = base if base not in ambiguous else '/'.join(h.split('/')[-2:])
    hits = [(tp, ss) for tp, ss in scanners.items() if os.path.exists(f'{ROOT}/{tp}') and key in open(f'{ROOT}/{tp}', errors='replace').read()]
    return hits + EXTRA_NAMED.get(base, [])

# ---- ucode per-helper evidence ----
def vu_diff_ops():
    return set(re.findall(r'OP\((V[A-Z]+)', open(f'{ROOT}/tools/rsp_vu_diff/harness.cpp').read()))
def s7092_ops():
    txt = open(f'{ROOT}/tools/s7092_vu_mem_test/README.md').read()
    return set(re.findall(r'\b([LS][BSLDQRPUHFW]V|VRCP[HL]?|VRSQ[HL]?)\b', txt))
def ucode_evidence(drop=()):
    ev = {}
    for o in vu_diff_ops(): ev[o] = 'Session 6301 (ares SIMD vs SISD, self-consistency) + Session 7751 (cxd4 whole-task)'
    for o in s7092_ops(): ev[o] = 'Session 7092 (fast path vs ares loop; divide vs cxd4 ROM)'
    for o in ('MFC2', 'MTC2', 'CFC2', 'CTC2'): ev[o] = 'Session 7093 E (cop2 moves vs cxd4 su.c)'
    for o in ('VMOV', 'VSAR'): ev[o] = 'Session 7814 (vs cxd4, whole vpu state)'
    for o in ('RSP_ADD32', 'RSP_SUB32', 'RSP_SIGNED', 'S32', 'U32', 'RSP_MEM_B', 'RSP_MEM_BU', 'RSP_MEM_H_LOAD',
              'RSP_MEM_HU_LOAD', 'RSP_MEM_W_LOAD', 'RSP_MEM_H_STORE', 'RSP_MEM_W_STORE'):
        ev[o] = 'Session 7093 D (scalar lowering vs Python model, live rsp.hpp block) + Session 7092 (2)'
    for o in ('SET_DMA_MEM', 'SET_DMA_DRAM', 'DO_DMA_READ', 'DO_DMA_WRITE'):
        ev[o] = 'Session 7094 (DMA host differential vs ares) + 7327 mask + 7344 length'
    for o in ('RSP_DPC_START', 'RSP_DPC_END', 'RSP_DPC_END_READ', 'RSP_DPC_CURRENT_READ', 'RSP_DPC_STATUS_READ',
              'RSP_DPC_STATUS_WRITE'):
        ev[o] = 'Session 7095 (RSP-side DPC register model vs hardware, 15/15 ROM sites)'
    for d in drop: ev.pop(d, None)
    return ev

def ucode_map(drop=()):
    ev = ucode_evidence(drop); rows = []; c = collections.Counter()
    for f in tu_sources('ucode'):
        s = strip_c(open(f, errors='replace').read())
        for m in re.finditer(r'\brsp\.([A-Z][A-Z0-9]+)\s*(<[^>]*>)?\s*\(', s): c[m.group(1)] += 1
        for m in re.finditer(r'\b(RSP_[A-Z0-9_]+|S32|U32|SET_DMA_\w+|DO_DMA_\w+)\s*\(', s): c[m.group(1)] += 1
    for k, n in sorted(c.items()): rows.append((k, n, ev.get(k, 'OPEN')))
    return rows

def all_resolved():
    seen = collections.defaultdict(set)
    for b in BUILDS:
        for t in ('RecompiledFuncs', 'PatchesLib', 'RogueSquadron64Recomp'):
            for f in objs(b, t):
                for h in dep_headers(open(f, errors='replace').read()):
                    if not is_sys(h): seen[os.path.basename(h)].add(h)
    return {b for b, ps in seen.items() if len(ps) > 1}

# Diagnostic shadows: pass-through differential (tools/s7814_shadow_passthru.c), shipped force-include in every arm.
SHADOW_ARMS = {'up': [], 'fbld': ['-I{d}/fbld', '-DRS64_FB_LDWATCH'], 'spwm': ['-I{d}/spwm', '-DRS64_SP_WATCH']}
def shadow_passthru(mutant=None):
    import shutil
    d = f'{ROOT}/include'
    if mutant:
        d = f'{ROOT}/scratch/s7814/inc_{mutant}'; shutil.rmtree(d, ignore_errors=True)
        shutil.copytree(f'{ROOT}/include/fbld', f'{d}/fbld'); shutil.copytree(f'{ROOT}/include/spwm', f'{d}/spwm')
        f, a, b = {'fbld_h': ('fbld/recomp.h', '(((reg) + (offset)) ^ 2) - 0xFFFFFFFF80000000), __FILE__, __LINE__, 2))\n#define MEM_HU',
                              '(((reg) + (offset)) ^ 0) - 0xFFFFFFFF80000000), __FILE__, __LINE__, 2))\n#define MEM_HU'),
                   'spwm_r29': ('spwm/recomp.h', '    return r;\n}', '    return r + 1;\n}')}[mutant]
        t = open(f'{d}/{f}').read(); assert a in t, f'mutant {mutant} did not apply'; open(f'{d}/{f}', 'w').write(t.replace(a, b, 1))
    out = {}
    for arm, x in SHADOW_ARMS.items():
        exe = f'{ROOT}/scratch/s7814/pt_{arm}_{mutant or "live"}'; os.makedirs(os.path.dirname(exe), exist_ok=True)
        cmd = ['cc', '-std=gnu17', '-O2', '-fno-strict-aliasing', '-w', '-include', f'{ROOT}/include/rsp_dpc_macros.h'] + \
              [y.format(d=d) for y in x] + [f'-I{ROOT}/include', f'-I{ROOT}/lib/N64ModernRuntime/N64Recomp/include',
              f'{ROOT}/tools/s7814_shadow_passthru.c', '-o', exe]
        r = subprocess.run(cmd, capture_output=True, text=True)
        out[arm] = subprocess.run([exe], capture_output=True, text=True).stdout.strip() if not r.returncode else 'BUILD-ERR ' + r.stderr[-300:]
    return out

def run(scanners=SCANNERS, extra=None, drop=(), shadow_redirect=None, quiet=False):
    P = (lambda *a: None) if quiet else print
    ambiguous = all_resolved()
    opens, mism = [], []; resolved = collections.defaultdict(set)  # basename -> {(path, build)}
    for b in BUILDS:
        if not os.path.isdir(f'{ROOT}/{b}'): continue
        for t in ('RecompiledFuncs', 'PatchesLib', 'RogueSquadron64Recomp'):
            n, A = source_a(b, t)
            if not n: P(f'{b:11s} {t:22s} no .o.d (target not built here)'); continue
            od = objs(b, t)[0]; cmd, B = source_b(b, t, od, extra)
            if isinstance(B, tuple): P(f'{b} {t} -M failed: {B[1]}'); mism.append((b, t, 'ERR')); continue
            Aset = set(A)
            proj = sorted(h for h in Aset | (B or set()) if not is_sys(h))
            agree = B is not None and {h for h in B if not is_sys(h)} <= Aset | set(proj) and \
                {h for h in dep_headers(open(od).read()) if not is_sys(h)} == {h for h in B if not is_sys(h)}
            if not agree: mism.append((b, t, sorted({h for h in B if not is_sys(h)} ^ {h for h in dep_headers(open(od).read()) if not is_sys(h)})))
            tk = 'ucode' if t == 'RogueSquadron64Recomp' else t
            P(f'{b:11s} {t:22s} TUs={n:3d} sys={sum(1 for h in Aset if is_sys(h)):3d} A==B(sample)={agree}')
            for h in proj:
                path = h if h.startswith('/') else f'{ROOT}/{h}'; base = os.path.basename(h)
                resolved[base].add((h, b))
                hits = scanner_hits(h, scanners, ambiguous)
                hs = helpers(path) if os.path.exists(path) else set()
                live = {k: v for k, v in call_counts(tk).items() if k in hs}
                if not hits and base in ambiguous and b != 'build' and h.startswith('include/') and h.split('/')[1] in SHADOW_PT:
                    cls = f'SHADOW-DIAG pass-through {SHADOW_PT[h.split("/")[1]]}'
                    if not SHADOW_PT[h.split('/')[1]].startswith('EQUAL'): opens.append((b, t, h, 'pass-through differs'))
                elif hits: cls = 'SCANNED ' + ','.join(sorted({s for _, s in hits}))
                elif not hs: cls = 'DECL'
                elif not live: cls = f'DEAD-IN-TU ({len(hs)} helpers, 0 calls)'
                else: cls = 'OPEN'; opens.append((b, t, h, sorted(live.items())[:8]))
                P(f'    {h:70s} {cls}  live_helpers={len(live)}')
    # shadow: same basename, different resolved paths
    P('SHADOW')
    rh_paths = {}
    for tp in scanners:
        fp = f'{ROOT}/{tp}'
        if os.path.exists(fp):
            for m in re.finditer(r"'([\w./-]*recomp\.h)'", open(fp).read()): rh_paths[tp] = m.group(1)
    if shadow_redirect: rh_paths['tools/s7812_recomp_h_census.py'] = shadow_redirect
    for base, ps in sorted(resolved.items()):
        paths = {p for p, _ in ps}
        if len(paths) < 2: continue
        shipped = {p for p, bb in ps if bb == 'build'}
        for p in sorted(paths):
            blds = sorted(bb for pp, bb in ps if pp == p)
            P(f'    {base:16s} {p:62s} builds={",".join(blds)}' + ('' if 'build' in blds else '  (diagnostic-only build)'))
        if base == 'recomp.h':
            for tp, rp in rh_paths.items():
                if not any(s.endswith(rp) for s in shipped):
                    P(f'    SHADOW-MISS: {tp} reads {rp}, shipped build resolves {sorted(shipped)}'); opens.append(('SHADOW', tp, rp, []))
    P('UCODE helper map (generated LLE C call -> evidence)')
    for k, n, e in ucode_map(drop):
        if e == 'OPEN': opens.append(('ucode', 'helper', k, n))
        P(f'    {k:22s} {n:6d}  {e}')
    return opens, mism

def controls():
    ok = True; d = f'{ROOT}/scratch/s7814'; os.makedirs(d, exist_ok=True)
    hp = f'{d}/planted.h'; open(hp, 'w').write('#define MEM_W_PLANT(a,b) ((a)+(b))\nstatic inline int RSP_ADD32_PLANT(int a){return a;}\n')
    _calls.setdefault('RecompiledFuncs', call_counts('RecompiledFuncs'))['MEM_W_PLANT'] += 5
    o, _ = run(extra=['-include', hp], quiet=True)
    f1 = any(h.endswith('planted.h') for _, _, h, _ in o); print('CONTROL planted-include ->', 'PASS' if f1 else 'FAIL'); ok &= f1
    _calls['RecompiledFuncs'].pop('MEM_W_PLANT', None)
    o, _ = run(shadow_redirect='include/fbld/recomp.h', quiet=True)
    f2 = any(b == 'SHADOW' for b, *_ in o); print('CONTROL shadow-redirect ->', 'PASS' if f2 else 'FAIL'); ok &= f2
    sc = {k: v for k, v in SCANNERS.items() if 's7813' not in k}
    o, _ = run(scanners=sc, quiet=True)
    f3 = any(h.endswith('rsp_dpc_macros.h') for _, _, h, _ in o); print('CONTROL drop-rsp_dpc_macros ->', 'PASS' if f3 else 'FAIL'); ok &= f3
    for m in ('fbld_h', 'spwm_r29'):
        set_pt(m); o, _ = run(quiet=True)
        arm = m.split('_')[0]; f5 = any(isinstance(x[3], str) and x[2].startswith(f'include/{arm}/') for x in o)
        print(f'CONTROL shadow-mutant {m} ->', 'PASS' if f5 else 'FAIL'); ok &= f5
    set_pt()
    o, _ = run(drop=('VMOV',), quiet=True)
    f4 = any(b == 'ucode' and h == 'VMOV' for b, _, h, _ in o); print('CONTROL drop-VMOV-evidence ->', 'PASS' if f4 else 'FAIL'); ok &= f4
    return ok

SHADOW_PT = {}
def set_pt(mutant=None):
    r = shadow_passthru(mutant); up = r['up']
    for arm in ('fbld', 'spwm'): SHADOW_PT[arm] = ('EQUAL ' if r[arm] == up and up.startswith('hash=') else 'DIFFER ') + f'{arm}:{r[arm]} up:{up}'
    return r

if __name__ == '__main__':
    print('PASSTHRU', set_pt())
    opens, mism = run()
    print(f'OPEN={len(opens)} A!=B={len(mism)}')
    for x in opens: print('  OPEN', x)
    for x in mism: print('  MISMATCH', x)
    cok = True
    if '--controls' in sys.argv:
        cok = controls(); print('CONTROLS', 'PASS' if cok else 'FAIL')
    green = not opens and not mism and cok
    print('CLASS VERDICT', 'GREEN' if green else 'RED', f'open={len(opens)} mismatch={len(mism)}')
    sys.exit(0 if green else 1)
