#!/usr/bin/env python3
"""s7425 class CH: build-option drift audit (offline).

Are the options the shipped build/ was compiled with the intended ones?
 1. CMakeLists option()/CACHE defaults vs build/CMakeCache.txt values in force.
 2. Per compile_commands entry: -O level, diagnostic defines, -fsanitize, grouped by target.
    Hot targets (game code) must be -O2; diagnostic defines must be absent.
 3. Stale flags: every object newer than its target's flags.make.
 4. Linked image: no __tsan_/__asan_ symbols; rs64_bwatch symbols present iff RS64_BYTE_WATCH is compiled in.
 5. --control: a planted librecomp entry with -DRS64_BYTE_WATCH -O0 and a planted cache value != default must be flagged.
Exit 0 = H-intended, 1 = H-drift, 3 = control failed.
"""
import json, os, re, shlex, subprocess, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, 'build')
DIAG_DEFINES = ('RS64_BYTE_WATCH', 'RS64_FB_LDWATCH', 'RS64_SP_WATCH', 'D3D12_DEBUG_LAYER_ENABLED')
HOT = {'RecompiledFuncs', 'PatchesLib', 'RogueSquadron64Recomp', 'librecomp', 'ultramodern', 'rt64', 'plume'}
# Linked into the game at the Debug -O0 default, by design: cold paths (mod loading, zip, texture-pack zstd, fmt).
COLD_OK = {'LiveRecomp', 'N64Recomp', 'rabbitizer', 'SymbolLists', 'fmt', 'miniz', 'nfd', 're-spirv', 'zstd',
           'libzstd_static', 'zstd-frugal'}
# zstd's own CMake adds -DDEBUGLEVEL=1 under Debug (AddZstdCompilationFlags.cmake:75): upstream default, asserts only.
DEFINE_OK = {('zstd', '-DDEBUGLEVEL=1'), ('libzstd_static', '-DDEBUGLEVEL=1'), ('zstd-frugal', '-DDEBUGLEVEL=1')}
# Cache values that differ from the CMakeLists default for a documented reason (host paths).
CACHE_OK = {'MIPS_TOOLCHAIN_DIR', 'MIPS_GCC', 'MIPS_LD', 'N64RECOMP_EXE'}


def cmake_defaults():
    src = open(os.path.join(ROOT, 'CMakeLists.txt')).read()
    d = {}
    for m in re.finditer(r'option\(\s*(\w+)\s+"[^"]*"\s+(ON|OFF)\s*\)', src):
        d[m.group(1)] = m.group(2)
    for m in re.finditer(r'set\(\s*(\w+)\s+"([^"]*)"\s+CACHE\s+\w+', src):
        d[m.group(1)] = m.group(2)
    return d


def cache_values(path):
    v = {}
    for ln in open(path):
        m = re.match(r'^([A-Za-z_0-9]+):(\w+)=(.*)$', ln.rstrip('\n'))
        if m:
            v[m.group(1)] = m.group(3)
    return v


def target_of(out):
    return re.sub(r'.*CMakeFiles/', '', out).split('.dir')[0]


def audit_entries(entries, defaults, cache, findings, info):
    groups = collections.Counter()
    for e in entries:
        a = shlex.split(e['command']) if 'command' in e else e['arguments']
        out = a[a.index('-o') + 1] if '-o' in a else e.get('output', '?')
        t = target_of(out)
        opts = [x for x in a if re.fullmatch(r'-O[0-3sz]?', x)]
        olev = opts[-1] if opts else '-O0'
        defs = [x for x in a if x.startswith('-D')]
        san = [x for x in a if x.startswith('-fsanitize')]
        groups[(t, olev)] += 1
        for dd in defs:
            name = dd[2:].split('=')[0]
            if name in DIAG_DEFINES:
                findings.append(f'DIAG-DEFINE {t}: {dd} in {os.path.basename(e["file"])}')
            elif name == 'DEBUGLEVEL' and (t, dd) not in DEFINE_OK:
                findings.append(f'DEBUG-DEFINE {t}: {dd} in {os.path.basename(e["file"])}')
        for s in san:
            findings.append(f'SANITIZER {t}: {s} in {os.path.basename(e["file"])}')
        if t in HOT and olev != '-O2':
            want = {'rt64': 'ROGUESQ_RT64_OPT', 'plume': 'ROGUESQ_PLUME_OPT', 'RecompiledFuncs': 'ROGUESQ_FUNCS_OPT',
                    'PatchesLib': 'ROGUESQ_FUNCS_OPT'}.get(t, 'ROGUESQ_SRC_OPT')
            if cache.get(want, defaults.get(want)) == 'ON':
                findings.append(f'OPT {t}: {olev} but {want}=ON in {os.path.basename(e["file"])}')
        if os.path.basename(e['file']) == 'factor5_ucode_recompiled.c' and \
                cache.get('ROGUESQ_UCODE_INLINE_THRESHOLD', '4000') != '0' and \
                not any(x.startswith('-inline-threshold=') for x in a):
            findings.append('UCODE gfx TU missing -inline-threshold')
    for (t, o), n in sorted(groups.items()):
        tag = 'HOT' if t in HOT else ('cold' if t in COLD_OK else 'tool')
        info.append(f'  {tag:4} {t:24} {o:4} x{n}')
    return groups


def audit_cache(defaults, cache, findings):
    for k, dv in sorted(defaults.items()):
        if k not in cache:
            continue
        cv = cache[k]
        if cv != dv and k not in CACHE_OK:
            findings.append(f'CACHE {k}={cv} (CMakeLists default {dv})')
    if cache.get('CMAKE_C_FLAGS', '') or cache.get('CMAKE_CXX_FLAGS', ''):
        findings.append(f'CACHE global flags C="{cache.get("CMAKE_C_FLAGS")}" CXX="{cache.get("CMAKE_CXX_FLAGS")}"')
    for k in ('CMAKE_C_FLAGS_DEBUG', 'CMAKE_CXX_FLAGS_DEBUG'):
        if cache.get(k, '-g') != '-g':
            findings.append(f'CACHE {k}="{cache[k]}" (CMake default -g)')


def audit_stale_flags(entries, findings):
    n = 0
    for e in entries:
        a = shlex.split(e['command']) if 'command' in e else e['arguments']
        if '-o' not in a:
            continue
        out = os.path.join(e['directory'], a[a.index('-o') + 1])
        fm = os.path.join(out.split('.dir/')[0] + '.dir', 'flags.make')
        if os.path.exists(out) and os.path.exists(fm):
            n += 1
            if os.path.getmtime(out) < os.path.getmtime(fm):
                findings.append(f'STALE-FLAGS {os.path.relpath(out, BUILD)} older than its flags.make')
    return n


def audit_binary(entries, findings, info):
    exe = os.path.join(BUILD, 'RogueSquadron64Recomp')
    syms = subprocess.run(['nm', exe], capture_output=True, text=True).stdout
    tsan = len(re.findall(r'__tsan_', syms)); asan = len(re.findall(r'__asan_', syms))
    bw = len(re.findall(r'_rs64_bwatch\b', syms))
    info.append(f'  nm: __tsan_ {tsan}, __asan_ {asan}, rs64_bwatch {bw}')
    if tsan or asan:
        findings.append(f'BINARY sanitizer symbols tsan={tsan} asan={asan}')
    compiled = any('-DRS64_BYTE_WATCH' in (e.get('command') or ' '.join(e.get('arguments', []))) for e in entries)
    if bool(bw) != compiled:
        findings.append(f'BINARY rs64_bwatch symbols={bw} but RS64_BYTE_WATCH compiled-in={compiled} (relink pending?)')


def main():
    control = '--control' in sys.argv
    defaults = cmake_defaults()
    cache = cache_values(os.path.join(BUILD, 'CMakeCache.txt'))
    entries = json.load(open(os.path.join(BUILD, 'compile_commands.json')))
    findings, info = [], []
    print(f'options/cache vars in CMakeLists: {len(defaults)}; build type {cache.get("CMAKE_BUILD_TYPE")}')
    audit_cache(defaults, cache, findings)
    audit_entries(entries, defaults, cache, findings, info)
    nst = audit_stale_flags(entries, findings)
    audit_binary(entries, findings, info)
    print('\n'.join(info)); print(f'  flags.make freshness checked on {nst} objects')
    rc_ctl = 0
    if control:
        lr = [e for e in entries if target_of(shlex.split(e['command'])[shlex.split(e['command']).index('-o') + 1])
              == 'librecomp'][0]
        plant = dict(lr); plant['command'] = lr['command'].replace(' -O2', ' -O0') + ' -DRS64_BYTE_WATCH'
        f2 = []; audit_entries([plant], defaults, cache, f2, [])
        c2 = dict(cache); c2['ROGUESQ_SP_WATCH'] = 'ON'; f3 = []; audit_cache(defaults, c2, f3)
        ok1 = any('DIAG-DEFINE librecomp' in f for f in f2) and any('OPT librecomp' in f for f in f2)
        ok2 = any('ROGUESQ_SP_WATCH=ON' in f for f in f3)
        print(f'CONTROL planted -O0 -DRS64_BYTE_WATCH librecomp entry: {"PASS" if ok1 else "FAIL"} {f2}')
        print(f'CONTROL planted cache ROGUESQ_SP_WATCH=ON: {"PASS" if ok2 else "FAIL"} {f3}')
        if not (ok1 and ok2):
            rc_ctl = 3
    agg = collections.Counter(re.sub(r' in \S+$', '', f) for f in findings)
    for f, n in sorted(agg.items()):
        print(f'FINDING x{n}: {f}')
    if rc_ctl:
        print('VERDICT control-failed'); return 3
    print('VERDICT ' + ('H-drift' if findings else 'H-intended'))
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
