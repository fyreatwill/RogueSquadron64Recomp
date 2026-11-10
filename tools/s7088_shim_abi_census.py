#!/usr/bin/env python3
"""s7088 host-shim ABI census.

Enumerates every hand-written `X_recomp(uint8_t* rdram, recomp_context* ctx)` shim in
lib/N64ModernRuntime/librecomp/src and src/, counts the generated call sites
(`X_recomp(rdram, ctx)` in ../N64Recomp/RecompiledFuncs and build/factor5_ucode), and runs four
o32-ABI checks on each shim body:

  A  64-bit argument joins `(ctx->rH << 32) | (ctx->rL & 0xFFFFFFFF)`: H must be the even register
     of an a0:a1 / a2:a3 pair (r4 or r6), L = H+1, the low word masked.
  B  stack arguments `MEM_W(off, ctx->r29)` / `load_doubleword(rdram, ctx->r29, off)`: off >= 0x10,
     word-aligned, doublewords 8-aligned.
  C  integer returns `ctx->r2 = E` / `ctx->r3 = E`: E must be sign-extended (an (int32_t)/(s32)
     cast, an s32/int-typed call or variable, or a small literal). A u32/uint32_t/u64-typed call or
     variable assigned bare is ZERO-extended: the R4300 sign-extends every 32-bit result.
  D  `_arg<N, T>` index < 4 and `_return<T>` <= 4 bytes (helpers.hpp static_asserts these too).

Controls (run every time):
  positive: the pre-s7087 osGetCount_recomp body (`ctx->r2 = osGetCount();`) must flag check C;
            osGetTime_recomp must pass.
  negative: osSetTimer_recomp with r6/r7 swapped must give exactly one check-A finding.

Usage: python3 tools/s7088_shim_abi_census.py [--all]   (--all also lists uncalled-shim findings)
"""
import collections, glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_GLOBS = ['lib/N64ModernRuntime/librecomp/src/*.cpp', 'src/**/*.cpp', 'src/**/*.c']
GEN_GLOBS = ['../N64Recomp/RecompiledFuncs/*.c', 'build/factor5_ucode/*.c']
HDR_GLOBS = ['lib/N64ModernRuntime/ultramodern/include/ultramodern/*.h*',
             'lib/N64ModernRuntime/librecomp/include/librecomp/*.h*']
UNSIGNED_T = r'(?:u32|uint32_t|u64|uint64_t|OSTime|unsigned(?: int)?)'

# Value-range reasoning for check-C findings on CALLED shims (reviewed by hand, s7088).
RANGE_NOTES = {
    'osVirtualToPhysical': 'returns K0/K1 & 0x1FFFFFFF (< 2^29) for all 7 callers (0x80033D58.. task '
                           'pointers, KSEG0 or NULL): bit 31 never set -> zero == sign extension',
    'osAiSetFrequency': 'returns osViClock/dacRate <= 368,800 (or -1 after s7088 fix, which casts): '
                        'bit 31 never set',
    'osSpTaskYielded': 'returns 0/1 literal',
}


def read(p):
    with open(p, errors='ignore') as f:
        return f.read()


def bodies(text):
    for m in re.finditer(r'^(?:extern "C" )?void ([A-Za-z0-9_]+)_recomp\s*\(\s*uint8_t\s*\*\s*rdram', text, re.M):
        i = text.index('{', m.end())
        d = 0
        j = i
        while True:
            c = text[j]
            if c == '{':
                d += 1
            elif c == '}':
                d -= 1
                if d == 0:
                    break
            j += 1
        yield m.group(1), text.count('\n', 0, m.start()) + 1, text[i:j + 1]


def unsigned_funcs():
    names = set()
    for g in HDR_GLOBS:
        for p in glob.glob(os.path.join(ROOT, g)):
            for m in re.finditer(r'^\s*(?:extern "C" )?' + UNSIGNED_T + r'\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(',
                                 read(p), re.M):
                names.add(m.group(1))
    return names


def check(body, ufuncs):
    out = []
    # A: 64-bit joins
    for m in re.finditer(r'\(?\s*(?:\(\s*u?int64_t\s*\)\s*)?\(?ctx->r(\d+)\)?\s*<<\s*32\s*\)?\s*\|\s*'
                         r'\(*\s*(?:\(\s*u?int64_t\s*\)\s*)?\(?ctx->r(\d+)\)?(?:\s*<<\s*0\s*\))?\s*\)?\s*(&\s*0x[fF]{8}u?)?',
                         body):
        hi, lo, mask = int(m.group(1)), int(m.group(2)), m.group(3)
        if hi not in (4, 6) or lo != hi + 1 or not mask:
            out.append(('A', f'64-bit join hi=r{hi} lo=r{lo} mask={"yes" if mask else "NO"}'))
    # B: stack args
    for m in re.finditer(r'MEM_[WHB]\(\s*(0x[0-9A-Fa-f]+|\d+)\s*,\s*ctx->r29\s*\)', body):
        off = int(m.group(1), 0)
        if off < 0x10 or off % 4:
            out.append(('B', f'stack arg at sp+{off:#x}'))
    for m in re.finditer(r'load_doubleword\(\s*rdram\s*,\s*ctx->r29\s*,\s*(0x[0-9A-Fa-f]+|\d+)\s*\)', body):
        off = int(m.group(1), 0)
        if off < 0x10 or off % 8:
            out.append(('B', f'stack u64 at sp+{off:#x}'))
    # C: returns
    uvars = set(re.findall(r'\b' + UNSIGNED_T + r'\s+([A-Za-z_][A-Za-z0-9_]*)\s*[=;]', body))
    for m in re.finditer(r'ctx->r([23])\s*=\s*([^;]+);', body):
        e = m.group(2).strip()
        if re.match(r'\(\s*(?:int32_t|s32|int)\s*\)', e) or re.fullmatch(r'-?(?:0x[0-9A-Fa-f]+|\d+)u?', e):
            if re.fullmatch(r'(?:0x[0-9A-Fa-f]+|\d+)u?', e) and int(e.rstrip('u'), 0) >= 0x80000000:
                out.append(('C', f'r{m.group(1)} = literal {e} >= 2^31 (zero-extended)'))
            continue
        call = re.match(r'([A-Za-z_][A-Za-z0-9_:]*)\s*\(', e)
        if call and call.group(1).split('::')[-1] in ufuncs:
            out.append(('C', f'r{m.group(1)} = {e[:60]} (unsigned-returning call, zero-extended)'))
        elif re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', e) and e in uvars:
            out.append(('C', f'r{m.group(1)} = {e} (unsigned variable, zero-extended)'))
    # D: helpers
    for m in re.finditer(r'_arg<\s*(\d+)\s*,', body):
        if int(m.group(1)) >= 4:
            out.append(('D', f'_arg<{m.group(1)}>'))
    for m in re.finditer(r'_return<\s*(u64|uint64_t|s64|int64_t|double)\s*>', body):
        out.append(('D', f'_return<{m.group(1)}>'))
    return out


def main():
    os.chdir(ROOT)
    shims = {}
    for g in SRC_GLOBS:
        for p in glob.glob(g, recursive=True):
            for name, line, body in bodies(read(p)):
                shims.setdefault(name, []).append((p, line, body))
    calls = collections.Counter()
    for g in GEN_GLOBS:
        for p in glob.glob(g):
            for m in re.finditer(r'\b([A-Za-z0-9_]+)_recomp\(rdram, ctx\)', read(p)):
                calls[m.group(1)] += 1
    ufuncs = unsigned_funcs()

    # controls
    ctl_ok = True
    pre7087 = '{\n    ctx->r2 = osGetCount();\n}'
    pc = check(pre7087, ufuncs)
    gt = check(shims['osGetTime'][0][2], ufuncs)
    st = shims['osSetTimer'][0][2]
    neg = check(st.replace('ctx->r6', 'ctx->rTMP').replace('ctx->r7', 'ctx->r6').replace('ctx->rTMP', 'ctx->r7'), ufuncs)
    neg_base = check(st, ufuncs)
    print(f'control positive  pre-s7087 osGetCount: {pc}  -> {"PASS" if any(k == "C" for k, _ in pc) else "FAIL"}')
    print(f'control pass      osGetTime: {gt or "clean"}  -> {"PASS" if not gt else "FAIL"}')
    nA = sum(1 for k, _ in neg if k == 'A') - sum(1 for k, _ in neg_base if k == 'A')
    print(f'control negative  osSetTimer r6<->r7: +{nA} A finding(s)  -> {"PASS" if nA == 1 else "FAIL"}')
    ctl_ok = any(k == 'C' for k, _ in pc) and not gt and nA == 1

    dup = [n for n, v in shims.items() if len(v) > 1]
    called = sorted(n for n in shims if calls[n])
    print(f'\nshims {len(shims)}  called {len(called)}  generated call sites {sum(calls[n] for n in called)}'
          f'  duplicate definitions {dup or "none"}')
    verdict = collections.Counter()
    for n in sorted(shims):
        if not calls[n] and '--all' not in sys.argv:
            continue
        f = []
        for p, line, body in shims[n]:
            f += [(k, msg, p, line) for k, msg in check(body, ufuncs)]
        if not calls[n]:
            v = 'uncalled' if not f else 'differs-unreachable(uncalled)'
        elif not f:
            v = 'matches'
        elif n in RANGE_NOTES:
            v = 'differs-unreachable'
        else:
            v = 'differs-LIVE'
        verdict[v] += 1
        if f or '--all' in sys.argv:
            print(f'{n:28s} calls={calls[n]:3d} {v}')
            for k, msg, p, line in f:
                print(f'    [{k}] {msg}  ({os.path.relpath(p)}:{line})')
            if n in RANGE_NOTES and f:
                print(f'    range: {RANGE_NOTES[n]}')
    print('\nverdicts (called shims):', dict(verdict))
    live = verdict['differs-LIVE']
    print('controls', 'PASS' if ctl_ok else 'FAIL', '| live findings', live)
    return 0 if ctl_ok and live == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
