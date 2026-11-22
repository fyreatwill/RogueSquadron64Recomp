#!/usr/bin/env python3
"""s7813: generated-C host-callee class census (the last sibling of s7809 gcc patches / s7810 host overrides /
s7558 fixup hunks / s7812 recomp.h helpers).

Every identifier the generated game C calls that is NOT a RECOMP_FUNC of the tree is host code standing in for, or
added to, guest behaviour. It needs evidence. Sources (comments and string literals stripped before scanning):
  PRISTINE = tools/regen_front.sh output (raw N64Recomp emission, no fixups)  -> what the EMITTER calls
  LIVE     = ../N64Recomp/RecompiledFuncs + RecompiledPatches                   -> emitter + fixup chain
Classes, one verdict per distinct callee:
  FHDR    helper/macro of the FORCE-INCLUDED include/rsp_dpc_macros.h (CMake -include; s7812 scanned recomp.h only, so
          MEM_WU / RS64_DIV32 / RS64_TRUNC_W_* were outside its census). Evidence row or DEAD (0 live calls).
  EMIT    callee of the pristine emission (libm, traps, cop0, libultra/IDO replacements). Evidence row:
          ('CENSUS', 'Session N') header must exist; ('S7400', None) name must be a live row of tools/s7400_replaced_contract.py;
          ('DEADFN', fn) the guest function holding every site has 0 direct calls and 0 lui/addiu address refs in LIVE.
  FIXUP   callee only the fixup chain adds (live-only, not defined in the tree). Sub-classes:
          HOOK  rs64_/rogue_/rsN_/sN_ host hook -> class GR (Session 7558; s7719 --strict keeps live == replay)
          DIAG  stdio/env/time/backtrace/string/thread-id plumbing (never stores guest state by itself)
          MATH  libm in our opt-in feature code (FPS60 quanta, hangar cam, dd) -> GR + s7407 (retail never calls host libm)
          RT    runtime/atomics/trap (yield_self_1ms, __builtin_trap, __atomic_*) -> GR
          MEM   memcpy/memset/memcmp: every SITE is checked; an argument naming rdram/MEM_/ctx-> = RAW (word-swapped RDRAM
                byte copy, a byte-order hazard) -> OPEN unless the site is listed in RAW_OK.
  OPEN    anything unrowed -> RED.
H-hollow guard: classified distinct callees must equal the regex enumeration of LIVE U PRISTINE minus defs/keywords.
  --controls  planted controls (each must PASS). Exit 0 iff CLASS VERDICT GREEN (and controls PASS)."""
import glob, os, re, shutil, subprocess, sys, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = os.path.join(ROOT, 'scratch', 's7813')
LIVE = glob.glob(os.path.join(ROOT, '../N64Recomp/RecompiledFuncs/*.c')) + glob.glob(os.path.join(ROOT, 'RecompiledPatches/*.c'))
RHDR = os.path.join(ROOT, 'lib/N64ModernRuntime/N64Recomp/include/recomp.h')
FHDR = os.path.join(ROOT, 'include/rsp_dpc_macros.h')
KW = {'if', 'while', 'for', 'switch', 'return', 'sizeof', 'defined', '__attribute__', '__builtin_expect', '_Static_assert',
      '__typeof__', 'typeof', 'alignof', '_Alignof', 'asm', '__asm__'}

FHDR_EVID = {
    'MEM_WU': [('CENSUS', 'Session 7086')],  # tools/s7086_mem_test/mem_test.c exercises MEM_WU (lwu)
    'RS64_DIV32': [('CENSUS', 'Session 7575')], 'RS64_DIVU32': [('CENSUS', 'Session 7575')],
    'RS64_TRUNC_W_S': [('CENSUS', 'Session 7576')], 'RS64_TRUNC_W_D': [('CENSUS', 'Session 7576')],
    'rs64_trunc_w_s': [('CENSUS', 'Session 7576')], 'rs64_trunc_w_d': [('CENSUS', 'Session 7576')],
    'fprintf': [('CENSUS', 'Session 7432')],  # macro -> rs64_diag_fprintf (class CO: byte-identical default, QUIET drops)
}
FHDR_TEST = {'MEM_WU': 'tools/s7086_mem_test/mem_test.c'}  # the name must appear in that source
EMIT_EVID = {
    'fabsf': [('CENSUS', 'Session 7415')], 'fabs': [('CENSUS', 'Session 7415')], 'sqrtf': [('CENSUS', 'Session 7415')],
    'ceil': [('DEADFN', 'ceilDouble'), ('CENSUS', 'Session 7576')],  # S32(ceil()) = s7576 UB shape, only site dead
    'do_break': [('CENSUS', 'Session 7416'), ('CENSUS', 'Session 7575')],
    'switch_error': [('CENSUS', 'Session 7416')], 'pause_self': [('CENSUS', 'Session 7416')],
    'cop0_status_read': [('CENSUS', 'Session 7405'), ('CENSUS', 'Session 7409')],
    'cop0_status_write': [('CENSUS', 'Session 7405'), ('CENSUS', 'Session 7409')],
}
REPL_SESS = ('Session 7400', 'Session 7401', 'Session 7402', 'Session 7407')  # BJ/BK/BL contracts + BQ IDO math
DIAG = set('''getenv fflush time mach_absolute_time backtrace backtrace_symbols backtrace_symbols_fd atof atoi atol strtol
strtoul strcmp strncmp strchr strncpy snprintf sscanf fputc fputs fwrite fopen setvbuf clock_gettime gettimeofday
pthread_self pthread_threadid_np dladdr raise usleep fprintf pthread_create pthread_detach'''.split())
MATH = set('floorf ceilf powf sinf acosf tan __builtin_tan sqrt __builtin_sqrt fminf fmaxf isnan isinf __builtin_nanf'.split())
RT = set('''yield_self_1ms __builtin_trap __atomic_add_fetch __atomic_sub_fetch __atomic_load_n __atomic_store_n
__atomic_thread_fence'''.split())
MEMF = {'memcpy', 'memset', 'memcmp', 'memmove', '__builtin_memcpy', '__builtin_memset'}
RAW_OK = set()  # (normalised site text) reviewed RAW sites; empty: none exist at s7813
HOOK_RE = re.compile(r'^(rs64_|rogue_|_rogue_|rs\d+_|s\d+[a-z]?_|RS64_)')


def strip(s):
    s = re.sub(r'/\*.*?\*/', ' ', s, flags=re.S)
    s = re.sub(r'//[^\n]*', ' ', s)
    s = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', s)
    return re.sub(r"'(?:\\.|[^'\\])'", '0', s)


def calls(src):
    return collections.Counter(re.findall(r'(?<![\w.>$])([A-Za-z_]\w*)\s*\(', src))


def local_defs(src):
    d = set(re.findall(r'^[ \t]*(?:(?:static|inline|extern|const|unsigned|signed|struct|volatile|__attribute__\(\([^)]*\)\))\s+)*'
                       r'[A-Za-z_]\w*[\s\*]+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{', src, re.M))
    d |= set(re.findall(r'#\s*define\s+(\w+)\(', src))
    d |= set(re.findall(r'\(\s*\*\s*(\w+)\s*\)\s*\(', src))  # function-pointer variables
    return d


def helpers(text):
    return set(re.findall(r'^static inline [\w \*]+?\b(\w+)\(', text, re.M) + re.findall(r'^#define (\w+)\(', text, re.M))


def mem_sites(src):
    out = []
    for m in re.finditer(r'(?<![\w.>$])(memcpy|memset|memcmp|memmove|__builtin_memcpy|__builtin_memset)\s*\(', src):
        i, depth = m.end(), 1
        while i < len(src) and depth:
            depth += {'(': 1, ')': -1}.get(src[i], 0); i += 1
        args = src[m.end():i - 1]
        if re.fullmatch(r'\s*rdram\s*,\s*ctx\s*', args):
            continue  # a guest RECOMP_FUNC call shape, not host libc
        raw = bool(re.search(r'\brdram\b|\bMEM_\w+\(|ctx->', args))
        out.append((m.group(1), re.sub(r'\s+', ' ', args.strip()), raw))
    return out


def deadfn(fn, live):
    direct = len(re.findall(r'(?<![\w.>])' + re.escape(fn) + r'\(rdram', live))
    return direct


def addr_refs(addr, live):
    hi, lo = (addr + 0x8000) >> 16, addr & 0xFFFF
    lo_s = lo - 0x10000 if lo >= 0x8000 else lo
    pat = r'ADD32\(ctx->r\d+, ' + ('-' if lo_s < 0 else '') + '0X%X\)' % abs(lo_s)
    return len(re.findall(pat, live)), hi


def classify(live_src, pr_src, ps_heads, s7400_live, fhdr_text, rhdr_text, srcs, emit_evid=None, fhdr_evid=None):
    emit_evid = EMIT_EVID if emit_evid is None else emit_evid
    fhdr_evid = FHDR_EVID if fhdr_evid is None else fhdr_evid
    defs = set(re.findall(r'^RECOMP_FUNC\s+void\s+(\w+)\(', live_src, re.M)) | \
        set(re.findall(r'^RECOMP_FUNC\s+void\s+(\w+)\(', pr_src, re.M))
    rh, fh = helpers(rhdr_text), helpers(fhdr_text) - helpers(rhdr_text)
    loc = local_defs(live_src)
    lc, pc = calls(live_src), calls(pr_src)
    every = {k for k in set(lc) | set(pc) if k not in defs and k not in KW and k not in rh}
    rows = {}
    for n in sorted(every):
        live_n = lc.get(n, 0)
        if n in fh:
            ok = [r for k, r in fhdr_evid.get(n, []) if k == 'CENSUS' and r in ps_heads]
            if n in FHDR_TEST and not re.search(r'\b' + n + r'\b', srcs.get(FHDR_TEST[n], '')):
                ok = []
            rows[n] = ('FHDR', live_n, 'COVERED' if ok else 'DEAD' if live_n == 0 else 'OPEN', ok)
        elif n in pc:
            ok = []
            if re.fullmatch(r'_*os\w+_recomp|__u?ll_\w+_recomp', n):
                if n[:-7] in s7400_live and all(s in ps_heads for s in REPL_SESS):
                    ok = ['s7400-live-row'] + list(REPL_SESS)
            for k, r in emit_evid.get(n, []):
                if k == 'CENSUS' and r in ps_heads: ok.append(r)
                if k == 'DEADFN':
                    d = deadfn(r, live_src)
                    if d == 0: ok.append(f'DEADFN:{r}(0 calls)')
                    else: ok = [x for x in ok if not x.startswith('Session')]; break
            rows[n] = ('EMIT', live_n, 'COVERED' if ok else 'OPEN', ok)
        elif n in loc:
            continue  # defined inside the tree by a fixup: its body is part of class GR, not a host callee
        elif n in MEMF:
            rows[n] = ('MEM', live_n, 'SITES', [])
        elif HOOK_RE.match(n):
            rows[n] = ('HOOK', live_n, 'COVERED' if 'Session 7558' in ps_heads else 'OPEN', ['Session 7558'])
        elif n in DIAG:
            rows[n] = ('DIAG', live_n, 'COVERED', [])
        elif n in MATH:
            ok = [s for s in ('Session 7558', 'Session 7407') if s in ps_heads]
            rows[n] = ('MATH', live_n, 'COVERED' if len(ok) == 2 else 'OPEN', ok)
        elif n in RT:
            rows[n] = ('RT', live_n, 'COVERED' if 'Session 7558' in ps_heads else 'OPEN', ['Session 7558'])
        else:
            rows[n] = ('UNKNOWN', live_n, 'OPEN', [])
    sites = mem_sites(live_src)
    raw_open = [s for s in sites if s[2] and s[1] not in RAW_OK]
    for n, r in list(rows.items()):
        if r[0] == 'MEM':
            mine = [s for s in sites if s[0] == n]
            bad = [s for s in mine if s[2] and s[1] not in RAW_OK]
            rows[n] = ('MEM', r[1], 'OPEN' if bad else 'COVERED', [f'{len(mine)} sites raw={len(bad)}'])
    return rows, sites, raw_open, token_enum(live_src, pr_src, rh)


def token_enum(live_src, pr_src, rh):
    """Independent enumeration (H-hollow): a token walk, not the call regex. An identifier followed by '(' whose previous
    token is not '.', '->' or '$', minus RECOMP_FUNC names (token after 'void' following RECOMP_FUNC), keywords, recomp.h
    helpers, and identifiers defined in LIVE that neither the emitter calls nor the force header defines."""
    seen, defs, loc = set(), set(), set()
    for src in (live_src, pr_src):
        toks = re.findall(r'[A-Za-z_]\w*|->|\S', src)
        for i in range(1, len(toks) - 1):
            t = toks[i]
            if toks[i + 1] == '(' and (t[0].isalpha() or t[0] == '_') and toks[i - 1] not in ('.', '->', '$'):
                if toks[i - 1] == 'void' and i >= 2 and toks[i - 2] == 'RECOMP_FUNC':
                    defs.add(t)
                else:
                    seen.add(t)
    pc_names = set(re.findall(r'(?<![\w.>$])([A-Za-z_]\w*)\s*\(', pr_src))
    fh = helpers(open(FHDR).read()) - rh
    loc = local_defs(live_src)
    return {k for k in seen - defs - KW - rh if k not in loc or k in fh or k in pc_names}


def main():
    controls = '--controls' in sys.argv
    os.makedirs(OUT, exist_ok=True)
    pr = os.path.join(OUT, 'pristine')
    for p in (pr, pr + '.work'):
        shutil.rmtree(p, ignore_errors=True)
    r = subprocess.run(['zsh', os.path.join(ROOT, 'tools/regen_front.sh'), pr], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode:
        print(r.stderr); print('CLASS VERDICT RED (regen_front failed)'); sys.exit(3)
    pr_src = strip(''.join(open(f, errors='replace').read() for f in glob.glob(os.path.join(pr, '*.c'))))
    live_src = strip(''.join(open(f, errors='replace').read() for f in LIVE))
    shutil.rmtree(pr + '.work', ignore_errors=True)
    ps = open(os.path.join(ROOT, 'PORTING-STATE.md'), errors='replace').read()
    ps_heads = set(re.findall(r'^## (Session \d+) ', ps, re.M))
    s4 = subprocess.run([sys.executable, os.path.join(ROOT, 'tools/s7400_replaced_contract.py')], capture_output=True, text=True)
    s7400_live = set(re.findall(r'^(\w+)\s+\S+\s+\S+\s+live_sites=([1-9]\d*)', s4.stdout, re.M))
    s7400_live = {a for a, b in s7400_live}
    print(f"s7400 live replacements {len(s7400_live)} (rc {s4.returncode})")
    rhdr, fhdr = open(RHDR).read(), open(FHDR).read()
    srcs = {p: open(os.path.join(ROOT, p)).read() for p in set(FHDR_TEST.values())}
    rows, sites, raw_open, enum = classify(live_src, pr_src, ps_heads, s7400_live, fhdr, rhdr, srcs)
    cnt = collections.Counter()
    for n, (cls, live_n, v, ok) in sorted(rows.items(), key=lambda x: (x[1][0], -x[1][1])):
        cnt[(cls, v)] += 1
        if cls in ('FHDR', 'EMIT', 'MEM', 'MATH', 'RT', 'UNKNOWN') or v == 'OPEN':
            print(f"{cls:7s} {n:30s} live={live_n:7d} {v:8s} {','.join(ok)}")
    hooks = sum(1 for r in rows.values() if r[0] == 'HOOK')
    print(f"HOOK rows {hooks} (class GR, s7558 + s7719 --strict), DIAG rows {sum(1 for r in rows.values() if r[0] == 'DIAG')}")
    # latent: dead UB shape kept visible
    nref, _ = addr_refs(0x80093E60, live_src)
    print(f"LATENT ceilDouble 0x80093E60: S32(ceil()) direct_calls={deadfn('ceilDouble', live_src)} lo16_addr_refs={nref}")
    print(f"MEM host sites {len(sites)} raw_open {len(raw_open)}")
    for s in raw_open[:10]: print('  RAW', s)
    opened = [n for n, r in rows.items() if r[2] == 'OPEN']
    hollow = set(rows) != enum
    print(f"distinct callees classified {len(rows)} enumerated {len(enum)} hollow={'YES' if hollow else 'no'}")
    print('counts ' + ' '.join(f"{c}:{v}={k}" for (c, v), k in sorted(cnt.items())))
    green = not opened and not hollow and len(rows) >= 100 and nref == 0
    allc = True
    if controls:
        def one(live_add='', pr_add='', heads=ps_heads, emit=None):
            rr, _, ro, _ = classify(live_src + live_add, pr_src + pr_add, heads, s7400_live, fhdr, rhdr, srcs, emit_evid=emit)
            return rr, ro
        c = []
        rr, _ = one(pr_add=' rs64_planted_emit(1); ', live_add=' rs64_planted_emit(1); ')
        c.append(('planted emitted callee without row -> OPEN', rr['rs64_planted_emit'][2] == 'OPEN'))
        rr, _ = one(live_add=' strfry(x); ')
        c.append(('planted unknown fixup libc callee -> OPEN', rr['strfry'][2] == 'OPEN'))
        rr, ro = one(live_add=' memcpy(rdram + 0x100, buf, 3); ')
        c.append(('planted raw RDRAM memcpy -> MEM OPEN', rr['memcpy'][2] == 'OPEN' and len(ro) == len(raw_open) + 1))
        rr, _ = one(live_add=' getenv(x); ')
        c.append(('planted diag callee -> DIAG COVERED', rr['getenv'][:3:2] == ('DIAG', 'COVERED')))
        e = dict(EMIT_EVID); e['fabsf'] = [('CENSUS', 'Session 99999999')]
        rr, _ = one(emit=e)
        c.append(('row citing a missing session -> OPEN', rr['fabsf'][2] == 'OPEN'))
        rr, _ = one(live_add=' ceilDouble(rdram, ctx); ')
        c.append(('ceilDouble given a caller -> ceil OPEN', rr['ceil'][2] == 'OPEN'))
        rr, _ = one(pr_add=' osPlanted_recomp(rdram, ctx); ')
        c.append(('emitted replacement not in s7400 live table -> OPEN', rr['osPlanted_recomp'][2] == 'OPEN'))
        rr, _ = one(live_add=' RS64_DIV32(a, b); ', heads=ps_heads - {'Session 7575'})
        c.append(('FHDR helper whose session is missing -> OPEN', rr['RS64_DIV32'][2] == 'OPEN'))
        rr, _, _, en = classify(live_src + ' strfry(x); ', pr_src, ps_heads, s7400_live, fhdr, rhdr, srcs)
        rr.pop('strfry', None)
        c.append(('classifier dropping a callee -> hollow detected', set(rr) != en and 'strfry' in en))
        for nm, ok in c:
            print(f"CONTROL {'PASS' if ok else 'FAIL'} {nm}"); allc &= ok
        print(f"CONTROLS {'PASS' if allc else 'FAIL'}")
    print(f"CLASS VERDICT {'GREEN' if green else 'RED'} open={len(opened)} {opened[:12]}")
    sys.exit(0 if green and allc else 1)


if __name__ == '__main__':
    main()
