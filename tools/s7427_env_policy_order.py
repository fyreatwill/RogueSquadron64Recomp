#!/usr/bin/env python3
"""s7427 class CJ: env-policy ORDER audit (offline, plus a runtime trace fold).

main() applies the env policy as a sequence of steps (QOS_ALL block, rs64_s7358_sanitize_env, rs64_g1d_apply_aspect_policy,
rs64_g1c_apply_dd_policy, rs64_m5_apply_drain_tick_policy). s7426 (class CI) only checked FILE-SCOPE latches of policy vars.
This audit checks the rest of the ordering contract:

  PRE     a function reachable from main()'s pre-policy calls or from a file-scope initializer / constructor reads a policy
          var (the value it sees is the pre-policy one). LATCH = the read sits in a `static` initializer (kept for the run).
  STEP    policy step i (or anything it calls) reads a var that a LATER step j sets.
  OW      setenv(V, x, 1) / unsetenv(V) in a policy step that is neither the sanitiser, nor guarded by !getenv(V), nor a
          reviewed normalisation of the user's own V (ACCEPT_OW below). Overwrites a user value.
  DUP     two steps default the same var (overwrite=0) to different values: the earlier step silently wins.

Call graph: crude, name based (definitions at brace depth 0 or inside namespace/class/extern "C"; calls = identifier + "(").
It over-approximates (name collisions), so every reached reader is printed with its call path for review.

--trace <log>  folds the runtime half: ROGUESQ_S7427_ENVTRACE=1 makes rs64_env_cache.cpp record every ROGUESQ_* getenv made
               before main() finishes the policy ("[s7427] pre name=<V> n=<k> ra=<offset>" rows). Policy vars in that list
               = real pre-policy reads. ROGUESQ_S7427_PLANT=1 plants a function-local static latch of ROGUESQ_OSMEM_MB before the
               policy: it must show up (runtime positive control).
Exit: 0 = H-ordered, 1 = drift, 3 = control failed.
"""
import collections, os, re, subprocess, sys
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from rs64_zopen import zopen, zbytes  # s7805: zst-only retained inputs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7426_env_defaults as E  # noqa: E402  (chdirs to the repo root)

MAIN = 'src/main/main.cpp'
STEPS = ['@qos_all', 'rs64_s7358_sanitize_env', 'rs64_g1d_apply_aspect_policy', 'rs64_g1c_apply_dd_policy',
         'rs64_m5_apply_drain_tick_policy']
KW = set('if for while switch return sizeof catch defined decltype alignof static_assert new delete case do else'.split())
GET = re.compile(r'(?:std::)?getenv\(\s*"((?:ROGUESQ|RS64)_[A-Z0-9_]+)"\s*\)')
SET = re.compile(r'\bsetenv\(\s*"((?:ROGUESQ|RS64)_[A-Z0-9_]+)"\s*,\s*([^,]+?)\s*,\s*([01])\s*\)')
UNSET = re.compile(r'\bunsetenv\(\s*"((?:ROGUESQ|RS64)_[A-Z0-9_]+)"\s*\)')
# Reviewed overwrites: (function, var) -> why it is not a clobber of a user value.
ACCEPT_OW = {
    ('rs64_g1d_apply_aspect_policy', 'ROGUESQ_ASPECT'):
        'normalises the user\'s own ASPECT: auto -> "<r>:1" of the display, odd width -> multiple of 4 (s7188), >1024 -> '
        '1024:448 (s6142 clamp, s6688 RT64 output aspect must match); each rewrite is derived from the value read above it',
}
# Reviewed pre-policy / step reads: (function, var) -> why the early value is the intended one.
ACCEPT_READ = {
    ('rs64_s7358_sanitize_env', 'ROGUESQ_FB_WIDTH'): 'the sanitiser must see the USER value; aspect then defaults it only if unset (overwrite=0)',
    # s7717: added by s7713 ([s7713-osmem]); the sanitiser clamps only a USER-set value (e && *e) to 8; the later aspect / dd steps
    # default OSMEM_MB to the in-range 12 with overwrite=0, i.e. only when the user left it unset, so no step undoes the other.
    ('rs64_s7358_sanitize_env', 'ROGUESQ_OSMEM_MB'): 'the sanitiser must see the USER value; aspect/dd then default 12 only if unset (overwrite=0)',
}
# Pre-policy readers whose value main() re-arms after the policy: reader fn -> call that must follow the last policy step in main().
REARM = {
    'g5b_tg_fix_init': 'rs64_s7427_tg_fix_reinit',   # s7427 fix: rs64_g5b_tg_fix latched the raw DRAW_DISTANCE at static init
    'S7239Init': 'rs64_s7258_merge_reinit',          # dd policy re-runs both ctors after it sets MERGE / MERGE_E (s7258)
    'S7246Init': 'rs64_s7258_merge_reinit',
}
# recomp.cpp `init` (osMemSize/ram_top) is reached only through the name collision rt64 Metal checkActiveRenderEncoder -> init;
# its real caller is recomp::start, after the policy: the s7427 runtime trace has no pre-policy OSMEM/RAMTOP read from it.
ACCEPT_READ[('init', 'ROGUESQ_OSMEM_MB')] = 'name-collision path; runtime trace: read after the policy (recomp::start)'
ACCEPT_READ[('init', 'ROGUESQ_RAMTOP_MB')] = 'name-collision path; runtime trace: read after the policy (recomp::start)'
# Runtime pre-policy readers (atos symbol substring) whose early value is handled: (var, symbol substring) -> how.
TRACE_ACCEPT = {
    ('ROGUESQ_DD_OFFMAPCULL', 'upstream_compat'): 'g_rs64_s7030, set to 1 by the dd policy when it arms the cull',
    ('ROGUESQ_DD_WIDEWIN_MERGE', 'S7239Init'): 're-run by rs64_s7258_merge_reinit() in the dd policy',
    ('ROGUESQ_DD_WIDEWIN_MERGE_E', 'upstream_compat'): 'S7246Init (inlined), re-run by rs64_s7258_merge_reinit()',
    ('ROGUESQ_GFX_QOS', 'events.cpp'): 's6975_gfx_qos reads QOS_ALL itself',
    ('ROGUESQ_DRAW_DISTANCE', 'dpc_bridge'): 'rs64_g5b_tg_fix, re-armed by rs64_s7427_tg_fix_reinit() after the policy (s7427 fix)',
}
# s7732: the launch validator (rs64_settings_apply, before the policy; it re-execs) must see the USER value; it only unsets a
# value that is not auto/expand/W:H, so the aspect policy then reads a valid value or unset, as before s7732.
ACCEPT_READ[('rs64_s7732_aspect', 'ROGUESQ_ASPECT')] = 'launch validator of the USER value (s7732): unsets only non-aspect values; policy reads after'
TRACE_ACCEPT[('ROGUESQ_ASPECT', 'rs64_s7732_aspect')] = 'launch validator (s7732), before the re-exec; the policy reads the validated value'
ACCEPT_READ[('s7427_plant_latch', 'ROGUESQ_OSMEM_MB')] = 'runtime positive-control plant, runs only under ROGUESQ_S7427_PLANT=1'
# Reviewed file-scope latches of policy vars: (file basename, var) -> how the post-policy value reaches them.
ACCEPT_FILE = {
    ('upstream_compat.cpp', 'ROGUESQ_DD_OFFMAPCULL'): 'g_rs64_s7030: dd policy sets g_rs64_s7030 = 1 itself when it arms the cull (s7037)',
    ('upstream_compat.cpp', 'ROGUESQ_DD_FOGCULL'): 'g_rs64_s7030 (not a policy var)',
    ('events.cpp', 'ROGUESQ_GFX_QOS'): 's6975_gfx_qos: reads ROGUESQ_QOS_ALL itself when GFX_QOS is unset, = the QOS_ALL block\'s overwrite=0 default',
}
ACCEPT_DUP = {
    'ROGUESQ_DD_WIDEWIN_R': 'dd policy: 128 (s7293 px8 auto, dd>=8) is set before the generic 88 (s7266) on purpose',
    'ROGUESQ_RAMTOP_MB': 'dd policy: 24 when OSMEM>8 (s7326 8 MB spill arena) is set FIRST on purpose, 16 is the fallback',
    'ROGUESQ_OSMEM_MB': 'aspect (fbw>796) and dd (dd>1) both default 12: same value',
}


def functions(files, extra=None):
    """name -> list of (file, body_start, body_end, text, stripped). Also returns per-file stripped text for file-scope scans."""
    idx = collections.defaultdict(list); fs = {}
    defre = re.compile(r'([A-Za-z_]\w*(?:::[A-Za-z_~]\w*)*)\s*\(([^;{}()]*(?:\([^;{}()]*\)[^;{}()]*)*)\)\s*'
                       r'(?:const\s*)?(?:noexcept\s*)?(?:override\s*)?(?:->\s*[\w:<>*& ]+)?\s*(?::[^;{}]*)?$')
    items = [(f, None) for f in files] + list(extra or [])
    for f, text in items:
        if '/RecompiledFuncs/' in f or '/factor5_ucode/' in f: continue   # guest code cannot run before main()
        try: t = text if text is not None else open(f, errors='replace').read()
        except OSError: continue
        s = E.strip(t); marks = E.scope_map(t, s); fs[f] = (t, s, marks)
        depth = 0; stack = []
        for m in re.finditer(r'[{}]', s):
            if m.group() == '{':
                d0 = E.depth_at(marks, m.start() + 1)
                pre = s[max(0, m.start() - 400):m.start()]
                k = pre.rstrip()
                if d0 == 1 and E.depth_at(marks, m.start()) == 0:
                    dm = defre.search(k)
                    if dm and dm.group(1).split('::')[-1] not in KW:
                        stack.append((dm.group(1), m.start()))
                        continue
                stack.append(None)
            else:
                if stack:
                    top = stack.pop()
                    if top:
                        name, b = top
                        idx[name.split('::')[-1]].append((f, b, m.end(), t[b:m.end()], s[b:m.end()]))
    return idx, fs


def calls(stripped):
    out = set()
    for q in re.findall(r'((?:[A-Za-z_]\w*\s*::\s*)*[A-Za-z_]\w*)\s*\(', stripped):
        if q.startswith('std') and '::' in q: continue
        c = re.split(r'\s*::\s*', q)[-1]
        if c not in KW and not re.fullmatch(r'(?:f|s|sn|v|vsn)?printf|fputs|fopen|fclose|fflush|fwrite|strlen|strcmp|strncmp|strchr|atoi|atof|strtod|strtol|strtoul|memcpy|memset|getenv|setenv|unsetenv', c):
            out.add(c)
    return out


def reads(fn_text):
    out = []
    for m in GET.finditer(fn_text):
        ls = fn_text.rfind('\n', 0, m.start()) + 1; le = fn_text.find('\n', m.end()); le = len(fn_text) if le < 0 else le
        stmt_lo = max(fn_text.rfind(';', 0, m.start()), fn_text.rfind('{', 0, m.start())) + 1
        latch = bool(re.search(r'\bstatic\b', fn_text[stmt_lo:m.start()]))
        out.append((m.group(1), m.start(), latch, fn_text[ls:le].strip()[:160]))
    return out


def bfs(idx, roots, stop=()):
    """roots: list of (label, set_of_callee_names). Returns name -> path (list)."""
    seen = {}; q = collections.deque()
    def defs(c, f):
        d = [i for i, x in enumerate(idx.get(c, [])) if f and x[0] == f]
        return d if d else list(range(len(idx.get(c, []))))
    for lab, cs, *rf in roots:
        for c in cs:
            for i in defs(c, rf[0] if rf else None):
                if (c, i) not in seen and c not in stop:
                    seen[(c, i)] = [lab, c]; q.append((c, i))
    while q:
        n, i = q.popleft()
        f, _, _, _, s = idx[n][i]
        for c in calls(s):
            for j in defs(c, f):
                if (c, j) not in seen and c not in stop:
                    seen[(c, j)] = seen[(n, i)] + [c]; q.append((c, j))
    return seen


def main_body(idx):
    for (f, b, e, t, s) in idx.get('main', []):
        if f.endswith(MAIN): return t, s
    raise SystemExit('main() not found')


def step_ranges(mt, ms):
    """Return (pre_text_stripped, {step: stripped text of the inline step or None}) from main()'s body."""
    q = ms.find('ROGUESQ_QOS_ALL'.replace('ROGUESQ_QOS_ALL', ''))  # placeholder (literals are blanked in ms)
    qa = mt.find('"ROGUESQ_QOS_ALL"')
    first = min([qa] + [ms.find(n + '(') for n in STEPS[1:] if ms.find(n + '(') >= 0])
    blk_lo = ms.rfind('{', 0, qa); d = 0; blk_hi = blk_lo
    for i in range(blk_lo, len(ms)):
        if ms[i] == '{': d += 1
        elif ms[i] == '}':
            d -= 1
            if d == 0: blk_hi = i + 1; break
    return ms[:first], mt[blk_lo:blk_hi], ms[blk_lo:blk_hi]


def filescope_roots(fs, fnend, ctor_names=frozenset()):
    """Calls made by file-scope initializers (`= f(...)`, `= [..]{...}()`, `{ f() }`) and __attribute__((constructor)) fns."""
    roots = []; direct = []
    for f, (t, s, marks) in fs.items():
        for m in re.finditer(r'__attribute__\s*\(\(\s*constructor[^)]*\)\)\s*(?:static\s+)?(?:void|int)\s+(\w+)', t):
            roots.append((f'ctor {os.path.basename(f)}', {m.group(1)}))
        # s7717: `struct T { T() {...} } name;` (definition + declarator) runs T's constructor before main() too; the statement
        # split below sees only `} name` there, so match the class head, its closing brace and a trailing declarator here.
        for m in re.finditer(r'\b(?:struct|class)\s+([A-Za-z_]\w*)\s*(?::[^{;()]*)?\{', s):
            if m.group(1) not in ctor_names or E.depth_at(marks, m.start()) != 0: continue
            d = 0; j = m.end() - 1
            for j in range(m.end() - 1, len(s)):
                if s[j] == '{': d += 1
                elif s[j] == '}':
                    d -= 1
                    if d == 0: break
            dm = re.match(r'\s*([A-Za-z_]\w*)\s*(?:\{\s*\})?\s*;', s[j + 1:j + 200])
            if dm:
                roots.append((f'global {os.path.basename(f)}:{t.count(chr(10), 0, m.start()) + 1} {m.group(1)} {dm.group(1)}',
                              {m.group(1)}, f))
        # depth-0 statements: split on ';' where depth==0
        ends = sorted(fnend.get(f, []))
        bounds = sorted([m.end() for m in re.finditer(r';', s) if E.depth_at(marks, m.start()) == 0] + ends)
        bset = set(ends); last = 0
        for e_ in bounds:
            st_lo = last; last = e_
            if e_ in bset: continue          # a function body, not a declaration
            st = s[st_lo:e_ - 1]
            st = re.sub(r'(?m)^[ \t]*#.*$', lambda m: ' ' * len(m.group()), st)
            st = re.sub(r'^\s*(?:namespace\s*\w*\s*\{|extern\s+"?C?"?\s*\{|\}|\s)*', '', st)
            st_lo = e_ - 1 - len(st)
            if '=' not in st:
                # class-type global: `[static] T name;` / `namespace { T name; }` runs T's constructor before main()
                gm = re.match(r'\s*(?:static\s+)?([A-Za-z_]\w*)\s+[A-Za-z_]\w*\s*(?:\{\s*\})?\s*$', st)
                if gm and gm.group(1) in ctor_names:
                    roots.append((f'global {os.path.basename(f)}:{t.count(chr(10), 0, st_lo) + 1} {gm.group(1)}', {gm.group(1)}, f))
                continue
            if re.match(r'\s*(?:typedef|using)', st): continue
            init = st[st.index('=') + 1:]
            cs = calls(init)
            # skip pure type-construction / casts of literals
            if cs:
                roots.append((f'init {os.path.relpath(f, E.ROOT) if f.startswith("/") else f}:{t.count(chr(10), 0, st_lo) + 1}', cs, f))
            for g in GET.finditer(t[st_lo:st_lo + len(st)]):
                direct.append((f, t.count('\n', 0, st_lo) + 1, g.group(1)))
    return roots, direct


def audit(files, extra_main=None, extra=None):
    idx, fs = functions(files, extra)
    if extra_main is not None:   # control: re-index a patched main.cpp
        idx2, fs2 = functions([], [(os.path.join(E.ROOT, MAIN), extra_main)])
        for k in list(idx):
            idx[k] = [x for x in idx[k] if not x[0].endswith(MAIN)]
        for k, v in idx2.items(): idx[k] += v
        fs = {f: v for f, v in fs.items() if not f.endswith(MAIN)}; fs.update(fs2)
    mt, ms = main_body(idx)
    pre_s, qos_t, qos_s = step_ranges(mt, ms)
    mtext = extra_main if extra_main is not None else open(MAIN, errors='replace').read()
    pv = E.policy_vars([os.path.join(E.ROOT, MAIN)]) if extra_main is None else {}
    if extra_main is not None:
        for m in re.finditer(r'\bsetenv\(\s*"((?:ROGUESQ|RS64)_[A-Z0-9_]+)"', mtext): pv.setdefault(m.group(1), mtext.count('\n', 0, m.start()) + 1)
        for m in re.finditer(r'for\s*\(\s*const\s+char\s*\*\s*(\w+)\s*:\s*\{([^}]*)\}\s*\)\s*setenv\(\s*\1\b', mtext):
            for n in re.findall(r'"((?:ROGUESQ|RS64)_[A-Z0-9_]+)"', m.group(2)): pv.setdefault(n, 0)
    flags = []; stats = collections.Counter()
    stats['policy_vars'] = len(pv); stats['functions'] = sum(len(v) for v in idx.values())
    stepnames = STEPS[1:]
    # ---- PRE: pre-policy roots + file-scope initializers -------------------------------------------------------------
    MF = os.path.join(E.ROOT, MAIN)
    roots = [('main<pre-policy>', calls(pre_s), MF)]
    fnend = collections.defaultdict(list)
    for v in idx.values():
        for (f, b, e, t, s_) in v: fnend[f].append(e)
    fr, direct = filescope_roots(fs, fnend, set(idx))
    roots += fr
    stats['pre_roots'] = len(calls(pre_s)); stats['init_roots'] = len(fr)
    reach = bfs(idx, roots, stop=set(stepnames))
    stats['pre_reached'] = len(reach)
    pre_hits = []
    for (n, i), path in reach.items():
        for (f, b, e, t, s) in [idx[n][i]]:
            for v, off, latch, line in reads(t):
                if v not in pv: continue
                ln = open(f, errors='replace').read().count('\n', 0, b + off) + 1 if not f.endswith(MAIN) or extra_main is None \
                    else mtext.count('\n', 0, mtext.find(t) + off) + 1
                pre_hits.append((n, v, latch, f, ln, path, line))
    last_step = max(ms.find(n + '(') for n in stepnames)
    for (n, v, latch, f, ln, path, line) in pre_hits:
        if (n, v) in ACCEPT_READ: continue
        if n in REARM and (ms.find(REARM[n] + '(', last_step) > 0 or any(REARM[n] + '(' in x[4] for st in stepnames for x in idx.get(st, []))):
            stats['pre_rearmed'] += 1; continue
        flags.append(('PRE-LATCH' if latch else 'PRE-READ', f'{os.path.relpath(f, E.ROOT) if f.startswith("/") else f}:{ln}',
                      f'{n} reads {v} before the policy (path {" -> ".join(path)}): {line}'))
    stats['filescope_policy_reads'] = sum(1 for (_, _, v) in direct if v in pv)
    for (f, ln, v) in direct:
        if v in pv and (os.path.basename(f), v) not in ACCEPT_FILE:
            flags.append(('PRE-FILE', f'{os.path.relpath(f, E.ROOT) if f.startswith("/") else f}:{ln}', f'file-scope initializer latches {v} before the policy'))
    # ---- STEP order -------------------------------------------------------------------------------------------------
    sreads = {}; swrites = collections.defaultdict(dict)
    for i, st in enumerate(STEPS):
        if st == '@qos_all':
            texts = [(MAIN, qos_t, qos_s)]; sub = bfs(idx, [(st, calls(qos_s), MF)])
        else:
            texts = [(f, t, s) for (f, b, e, t, s) in idx.get(st, []) if f.endswith(MAIN)]
            sub = bfs(idx, [(st, calls(''.join(s for _, _, s in texts)), MF)])
        rr = []
        for f, t, s in texts: rr += [(st, v, line) for v, _, _, line in reads(t)]
        for (n, j) in sub:
            for (f, b, e, t, s) in [idx[n][j]]: rr += [(n, v, line) for v, _, _, line in reads(t)]
        sreads[st] = rr
        for f, t, s in texts:
            for m in SET.finditer(t): swrites[st].setdefault(m.group(1), []).append((m.group(2), int(m.group(3)), m.start(), t))
            for m in UNSET.finditer(t): swrites[st].setdefault(m.group(1), []).append(('<unset>', 1, m.start(), t))
            if st == '@qos_all':
                for mm in re.finditer(r'\{([^}]*)\}\s*\)\s*setenv\(\s*\w+\s*,\s*("[^"]*")\s*,\s*([01])', t):
                    for nn in re.findall(r'"((?:ROGUESQ|RS64)_[A-Z0-9_]+)"', mm.group(1)):
                        swrites[st].setdefault(nn, []).append((mm.group(2), int(mm.group(3)), mm.start(), t))
    stats['step_reads'] = sum(len(v) for v in sreads.values())
    stats['step_writes'] = sum(len(w) for v in swrites.values() for w in v.values())
    for i, st in enumerate(STEPS):
        for fn, v, line in sreads[st]:
            later = [STEPS[j] for j in range(i + 1, len(STEPS)) if v in swrites[STEPS[j]]]
            if later and (fn, v) not in ACCEPT_READ:
                flags.append(('STEP', st, f'{fn} reads {v} but later step(s) {later} set it: {line}'))
    # ---- OW: overwrites -----------------------------------------------------------------------------------------------
    for st in STEPS:
        for v, ws in swrites[st].items():
            for val, ow, off, t in ws:
                if not ow: continue
                stats['overwrites'] += 1
                if st == 'rs64_s7358_sanitize_env': stats['ow_sanitise'] += 1; continue
                ctx = t[max(0, off - 300):off]
                if re.search(r'!\s*(?:std::)?getenv\(\s*"' + v + r'"\s*\)', ctx): stats['ow_guarded'] += 1; continue
                if (st, v) in ACCEPT_OW and GET.search(t[:off]) and v in [g.group(1) for g in GET.finditer(t[:off])]:
                    stats['ow_normalise'] += 1; continue
                flags.append(('OW', st, f'setenv({v}, {val}, 1) overwrites a user value unguarded'))
    # ---- DUP: conflicting defaults ------------------------------------------------------------------------------------
    dflt = collections.defaultdict(set)
    for st in STEPS:
        for v, ws in swrites[st].items():
            for val, ow, _, _ in ws:
                if not ow: dflt[v].add((st, val))
    for v, s in dflt.items():
        vals = {x[1] for x in s}
        if len(s) > 1: stats['multi_default'] += 1
        if len(vals) > 1 and v not in ACCEPT_DUP:
            flags.append(('DUP', v, f'defaulted to {sorted(vals)} by {sorted({x[0] for x in s})}: first step wins'))
    return flags, stats, pre_hits, sreads, swrites


PLANT_FN = ('\nstatic void s7427_plant_pre() { static int v = std::getenv("ROGUESQ_OSMEM_MB") ? 1 : 0; (void)v; }\n'
            'static void s7427_plant_ow() { setenv("ROGUESQ_ASPECT", "16:9", 1); }\n')


def control(files):
    t = open(MAIN, errors='replace').read()
    i = t.index('int main(int argc')
    t2 = t[:i] + PLANT_FN + t[i:]
    t2 = t2.replace('    s7354_race_ctl_start();\n', '    s7354_race_ctl_start();\n    s7427_plant_pre();\n', 1)
    # planted unguarded overwrite inside a policy step, and a planted order inversion (sanitiser reads a var aspect sets later)
    t2 = t2.replace('static void rs64_g1c_apply_dd_policy() {\n', 'static void rs64_g1c_apply_dd_policy() {\n    s7427_plant_ow();\n'
                    '    setenv("ROGUESQ_UCODE_CAP", "1", 1);\n', 1)
    t2 = t2.replace('static void rs64_s7358_sanitize_env() {\n', 'static void rs64_s7358_sanitize_env() {\n'
                    '    (void)std::getenv("ROGUESQ_VPW_SCALE");\n', 1)
    # s7717: drop the dd policy's re-arm of the S7239Init / S7246Init file-scope latches: both must read as un-re-armed again
    rc_ = re.compile(r'(?<!void )\brs64_s7258_merge_reinit\(\);')   # the call, not the extern declaration
    assert len(rc_.findall(t2)) == 1, 'rearm call site moved: update the s7717 control'
    t2 = rc_.sub('/* s7717 control: re-arm dropped */', t2, count=1)
    flags, _, _, _, _ = audit(files, extra_main=t2)
    got = {(k, ('OSMEM' in m) or ('VPW_SCALE' in m) or ('UCODE_CAP' in m)) for k, _, m in flags}
    need = [('PRE-LATCH', 'ROGUESQ_OSMEM_MB'), ('STEP', 'ROGUESQ_VPW_SCALE'), ('OW', 'ROGUESQ_UCODE_CAP'),
            ('PRE-', 'ROGUESQ_DD_WIDEWIN_MERGE '), ('PRE-', 'ROGUESQ_DD_WIDEWIN_MERGE_E ')]   # s7717: both dropped re-arms
    hit = [(k, v.strip()) for k, v in need if any(fk.startswith(k) and v in m for fk, _, m in flags)]
    ok = len(hit) == len(need)
    print(f'[s7427] CONTROL {"PASS" if ok else "FAIL"}: planted pre-policy static latch / step order inversion / unguarded '
          f'overwrite -> {hit}')
    return ok


def fold_trace(path, pv):
    allrows = [l for l in zopen(path, errors='replace') if l.startswith(('[s7427] pre ', '[s7427] in '))]
    rows = [l for l in allrows if l.startswith('[s7427] pre ')]
    print(f'[s7427] trace phase rows: pre={len(rows)} in-policy={len(allrows) - len(rows)}')
    done = [l for l in zopen(path, errors='replace') if l.startswith('[s7427] policy-done')]
    hits = []
    for l in rows:
        m = re.search(r'name=(\S+) n=(\d+) ra=(0x[0-9a-f]+)', l)
        if m: hits.append((m.group(1), int(m.group(2)), m.group(3)))
    exe = os.path.join(E.ROOT, 'build', 'RogueSquadron64Recomp')
    sym = {}
    ras = sorted({h[2] for h in hits})
    if ras:
        try:
            out = subprocess.run(['atos', '-o', exe, '-l', '0x100000000'] + [hex(int(r, 16) + 0x100000000) for r in ras],
                                 capture_output=True, text=True, timeout=120).stdout.splitlines()
            sym = dict(zip(ras, out))
        except Exception as ex:  # noqa: BLE001
            print('[s7427] atos failed', ex)
    print(f'[s7427] trace rows={len(hits)} distinct={len({h[0] for h in hits})} policy-done={len(done)}')
    pol = [(h, sym.get(h[2], h[2])) for h in hits if h[0] in pv]
    for (n, k, ra), s in sorted(pol):
        print(f'  TRACE-PRE {n} n={k} at {s}')
    return hits, pol, len(done)


def main():
    files = E.sources()
    if '--control' in sys.argv and not control(files): return 3
    flags, stats, pre_hits, sreads, swrites = audit(files)
    print('[s7427] ' + ' '.join(f'{k}={v}' for k, v in sorted(stats.items())))
    if '-v' in sys.argv:
        for st in STEPS:
            print(f'  step {st}: reads {sorted({v for _, v, _ in sreads[st]})}')
            print(f'           writes {sorted((v, w[0][1]) for v, w in swrites[st].items())}')
    for k, where, msg in flags: print(f'  {k:9s} {where}  {msg}')
    rc = 1 if flags else 0
    if '--trace' in sys.argv:
        pv = E.policy_vars([os.path.join(E.ROOT, MAIN)])
        hits, pol, nd = fold_trace(sys.argv[sys.argv.index('--trace') + 1], pv)
        plant = [p for p in pol if p[0][0] == 'ROGUESQ_OSMEM_MB' and 's7427_plant' in p[1]]
        if '--trace-control' in sys.argv:
            print(f'[s7427] TRACE CONTROL {"PASS" if plant and nd else "FAIL"}: planted pre-policy OSMEM latch seen={bool(plant)} policy-done={nd}')
            if not (plant and nd):
                tp = __import__('rs64_zopen').resolve(sys.argv[sys.argv.index('--trace') + 1])
                exe = os.path.join(E.ROOT, 'build', 'RogueSquadron64Recomp')
                if nd and tp and os.path.exists(exe) and os.path.getmtime(exe) > os.path.getmtime(tp):
                    # s7805: ra values are symbolized with atos against the CURRENT binary; a trace captured on an older
                    # build (the plant arm compiled in) resolves to unrelated symbols, so this is not a control verdict.
                    print('[s7427] TRACE CONTROL STALE-BINARY: build/RogueSquadron64Recomp is newer than the trace; '
                          'replay needs the binary the trace was captured with')
                    return 4
                return 3
        real = [p for p in pol if 's7427_plant' not in p[1]]
        for (n, k, ra), s in real:
            if not any(n == v and sub in s for (v, sub) in TRACE_ACCEPT):
                flags.append(('TRACE', n, s)); rc = 1
    print(f'[s7427] VERDICT {"H-race" if rc else "H-ordered"} ({len(flags)} findings)')
    return rc


if __name__ == '__main__':
    sys.exit(main())
