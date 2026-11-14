#!/usr/bin/env python3
"""s7358 class AI census: numeric parses (atoi/atol/atof/strto*/sscanf/sto*) of getenv values or config text whose result
reaches an array index, allocation size, shift amount, divisor or loop bound with no clamp.

Scope: src/** + lib/N64ModernRuntime/{librecomp,ultramodern}/src/*.cpp + the lines WE added to lib/rt64 (git diff '+').
Per parse site:
  knob   ROGUESQ_*/other env name read on the line or up to 6 lines above (None = config/file text)
  owner  the knob appears in docs/OWNER-OPT-INS.md
  var    the variable the result is assigned to (lhs of '=' / static init lambda / sscanf &targets)
  sinks  uses of var in the file (static/global) or the next 60 lines (local) as: [var] index, / var or % var divisor,
         << var / >> var shift, malloc/calloc/new[]/resize/reserve/vector(var) size, for(...; < var) bound
  clamp  a std::min/max/clamp on var, a range test (var < / > / <= / >= literal or name) before the first sink,
         or a ternary range test in the init expression
Classes: NOSINK (no sink use found) / CLAMPED (sink but clamp seen first) / G (sink, unclamped, diagnostic knob) /
         B (sink, unclamped, owner knob or no knob name = default-on config text) / D (comment, _WIN32).
Then MANUAL dispositions (hand-verified reading of each G/B row). Controls: planted snippets (exit 1 on a miss).
usage: python3 tools/s7358_envparse_census.py [--raw] [--rows CLASS]
"""
import re, sys, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
PARSE = re.compile(r'(?<![\w.])(?:std::)?(atoi|atol|atoll|atof|strtol|strtoul|strtoull|strtoll|strtod|strtof|sscanf|stoi|stol|stoul|stof|stod)\s*\(')
ENV = re.compile(r'getenv\s*\(\s*"([A-Za-z0-9_]+)"|env_\w+\s*\(\s*"([A-Za-z0-9_]+)"|"(ROGUESQ_[A-Z0-9_]+)"')
OWNER = set(re.findall(r'ROGUESQ_[A-Z0-9_]+', (ROOT / 'docs/OWNER-OPT-INS.md').read_text()))

def files():
    out = []
    for p in sorted((ROOT / 'src').rglob('*')):
        if p.suffix in ('.cpp', '.c', '.mm', '.h'): out.append((p, None))
    for d in ('librecomp', 'ultramodern'):
        for p in sorted((ROOT / f'lib/N64ModernRuntime/{d}/src').glob('*.cpp')): out.append((p, None))
    rt = ROOT / 'lib/rt64'
    diff = subprocess.run(['git', '-C', str(rt), 'diff', '-U0', '--', 'src'], capture_output=True, text=True).stdout
    cur, added = None, {}
    for ln in diff.splitlines():
        if ln.startswith('+++ b/'): cur = ln[6:]; added.setdefault(cur, set())
        elif ln.startswith('@@') and cur:
            m = re.search(r'\+(\d+)(?:,(\d+))?', ln); s, n = int(m.group(1)), int(m.group(2) or 1)
            added[cur].update(range(s, s + n))
    for f, lines in sorted(added.items()):
        if lines and f.endswith(('.cpp', '.h', '.mm', '.c')): out.append((rt / f, lines))
    return out

def strip(s): return re.sub(r'//.*', '', re.sub(r'"(?:\\.|[^"\\])*"', '""', s))

def sink_re(v):
    v = re.escape(v)
    return re.compile(rf'\[[^\]\[]*\b{v}\b[^\]\[]*\]|[^/*]/\s*\(?\s*{v}\b(?!\s*\.)|%\s*\(?\s*{v}\b|<<\s*\(?\s*{v}\b|>>\s*\(?\s*{v}\b|'
                      rf'(?:malloc|calloc|realloc|resize|reserve|assign)\s*\([^;]*\b{v}\b|new\s+[\w:<>]+\s*\[[^\]]*\b{v}\b|'
                      rf'\bfor\s*\([^;]*;[^;]*<=?\s*\(?\s*{v}\b')

def clamp_re(v):
    v = re.escape(v)
    return re.compile(rf'(?:std::)?(?:min|max|clamp|fmin|fmax|fminf|fmaxf)\s*\([^;]*\b{v}\b|\b{v}\b\s*(?:<|>|<=|>=)\s*[-\w.(]|'
                      rf'[-\w.)]\s*(?:<|>|<=|>=)\s*\b{v}\b|if\s*\(\s*!?\s*\(?\s*{v}\s*\)')

def target(lines, i, m, L):
    fn = m.group(1)
    if fn == 'sscanf':
        tg = re.findall(r'&\s*([A-Za-z_][\w.\[\]]*)', L[m.end():].split(';')[0])
        return [re.sub(r'\[.*', '', t) for t in tg]
    head = L[:m.start()]
    mv = re.search(r'([A-Za-z_][\w.]*)(?:\[[^\]]*\])?\s*=[^=;]*$', head)
    if mv and not re.search(r'return\s*[^;]*$', head[mv.end():]): return [mv.group(1).split('.')[-1]]
    # static init lambda: static const T name = [] { ... return (...) ? atoi(e) : d; }();  -> name may be lines above
    for k in range(i, max(-1, i - 4), -1):
        mm = re.search(r'(?:static\s+)?(?:const\s+)?(?:constexpr\s+)?[\w:<>]+\s+([A-Za-z_]\w*)\s*=\s*\[', strip(lines[k]))
        if mm: return [mm.group(1)]
    if mv: return [mv.group(1).split('.')[-1]]
    return []

def classify(path, lines, i, m):
    raw = lines[i]; L = strip(raw); s = raw.strip()
    if s.startswith(('//', '*', '/*')): return 'D', 'comment', None, [], []
    pre = '\n'.join(lines[max(0, i - 40):i])
    if pre.rfind('#ifdef _WIN32') > max(pre.rfind('#endif'), pre.rfind('#else')): return 'D', '_WIN32', None, [], []
    knob = None
    for k in range(i, max(-1, i - 7), -1):
        e = ENV.findall(lines[k])
        if e: knob = next(x for x in e[-1] if x); break
    tg = [t for t in target(lines, i, m, L) if t not in ('e', 'c', 'q', 'p', 'end', 'endp')]
    if not tg: return 'NOSINK', 'result not stored (inline use)', knob, [], []
    sinks, clamps = [], []
    for v in tg:
        decl = '\n'.join(lines[max(0, i - 3):i + 1])
        static = (bool(re.search(r'\bstatic\b[^;=]*\b' + re.escape(v) + r'\s*=', decl)) and len(v) >= 4) or bool(re.match(r's_|g_|s\d{3,}', v))
        rng = range(0, len(lines)) if static else range(i, min(len(lines), i + 60))
        S, C = sink_re(v), clamp_re(v)
        first_sink = None
        for k in rng:
            t = strip(lines[k])
            if k == i: t = t[m.end():]
            if S.search(t): sinks.append((k + 1, v)); first_sink = first_sink or k
        if first_sink is not None:
            for k in range(min(i, first_sink) if static else i, first_sink + 1):
                t = strip(lines[k])
                if C.search(t): clamps.append((k + 1, v)); break
    if re.search(r'(?:min|max|clamp|fmin|fmax|fminf|fmaxf)\s*\([^;]*' + m.group(1) + r'\s*\(', L) or \
       re.search(m.group(1) + r'\s*\([^;]*\)\s*\)?\s*(?:<|>|<=|>=)\s*[-\w.]', L):
        clamps.append((i + 1, 'inline'))
    if not sinks: return 'NOSINK', 'no index/size/shift/divisor/bound use', knob, tg, []
    if clamps: return 'CLAMPED', f'clamp L{clamps[0][0]}', knob, tg, sinks
    owner = knob is None or knob in OWNER
    return ('B' if owner else 'G'), ('owner/default-on' if owner else 'diagnostic knob'), knob, tg, sinks

# MANUAL: hand-verified dispositions, key = (relpath, var). value = (class, note)
MANUAL = {
    ('src/main/main.cpp', 'dwell'): ('G', 'ROGUESQ_PLPOS_POKE_DWELL autopilot test lever; / and % by 0 on arm64 udiv give 0, no trap'),
    ('src/main/main.cpp', 's_every'): ('G', 'ROGUESQ_PLPOS_EVERY / GRIDSPAWN_EVERY log cadence; % 0 on arm64 = no trap, test lever only'),
    ('src/main/upstream_compat.cpp', 's_fbd_every'): ('G', 'ROGUESQ_FB_DUMP_EVERY dump cadence; % 0 no trap on arm64, env-gated dump'),
    ('src/rsp/dpc_bridge.cpp', 'mask'): ('NOSINK', 'name collision: T[finalAddr & mask] at 4199 is rs64_i4_texel\'s parameter, the env mask is a gate bitmask'),
}
# Rows the heuristic cannot see (result flows through a return expression / another env var / a fixup-injected reader), found by
# reading every owner-knob site by hand (47 owner + 14 config sites). FIXED in s7358, proven by tools/s7358_arms.zsh pre/post.
FIXED = [
    ('src/main/upstream_compat.cpp', 'rs64_s6893_tilepool_size', 'k = ceil(dd)^2*2 unclamped while terrain clamps dd at 8: dd12 k=288, spill arena full, SIGBUS -> px<=8'),
    ('tools/apply_s6036_dd.py', 'm6036', 'v < 0.25 lets NaN through: dd=nan multiplier nan, assert in buildVisibleTerrainGridAroundCamera -> main.cpp rs64_s7358_sanitize_env'),
    ('src/main/upstream_compat.cpp + fixups', 'ROGUESQ_DRAW_DISTANCE (all readers)', 'typo "x4" -> atof 0 -> silent 0.25x terrain -> sanitize: unset + warn'),
    ('src/main/upstream_compat.cpp:1604 + fixups', 'ROGUESQ_FB_WIDTH', 'hand-set value bypasses the 1024 clamp; negative atoi -> huge uint32 VI width -> sanitize clamp'),
]

def census(raw=False):
    rows = []
    for p, only in files():
        lines = p.read_text(errors='replace').splitlines()
        for i, l in enumerate(lines):
            if only is not None and (i + 1) not in only: continue
            for m in PARSE.finditer(l):
                c, why, knob, tg, sinks = classify(p, lines, i, m)
                rel = str(p.relative_to(ROOT))
                for v in tg:
                    if not raw and (rel, v) in MANUAL and c in ('B', 'G', 'CLAMPED'):
                        c, why = MANUAL[(rel, v)][0] + '-M', MANUAL[(rel, v)][1]; break
                rows.append((c, rel, i + 1, m.group(1), knob, ','.join(tg), sinks[:3], why))
    return rows

def controls():
    snips = {
        'B': ['static int tbl[8];', 'static const int s_ctl_ix = [] { const char* e = getenv("ROGUESQ_DRAW_DISTANCE"); return e ? atoi(e) : 0; }();',
              'int f() { return tbl[s_ctl_ix]; }'],
        'CLAMPED': ['static int tbl[8];', 'static const int s_ctl_cx = [] { const char* e = getenv("ROGUESQ_DRAW_DISTANCE"); return e ? std::clamp(atoi(e), 0, 7) : 0; }();',
                    'int f() { return tbl[s_ctl_cx]; }'],
        'NOSINK': ['static const int s_ctl_px = [] { const char* e = getenv("ROGUESQ_DRAW_DISTANCE"); return e ? atoi(e) : 0; }();',
                   'void f() { fprintf(stderr, "%d", s_ctl_px); }'],
        'G': ['static int tbl[8];', 'static const int s_ctl_gx = [] { const char* e = getenv("ROGUESQ_CTL_DIAG_ONLY"); return e ? atoi(e) : 0; }();',
              'int f() { return 100 / s_ctl_gx; }'],
    }
    ok = True
    for want, ls in snips.items():
        i = next(k for k, x in enumerate(ls) if PARSE.search(x))
        c = classify(None, ls, i, PARSE.search(ls[i]))[0]
        print(f'control {want:8s} -> {c:8s} {"PASS" if c == want else "FAIL"}'); ok &= c == want
    return ok

if __name__ == '__main__':
    raw = '--raw' in sys.argv
    show = sys.argv[sys.argv.index('--rows') + 1].split(',') if '--rows' in sys.argv else ['B', 'G', '?']
    ok = controls()
    rows = census(raw)
    from collections import Counter
    cnt = Counter(r[0] for r in rows)
    print(f'{len(rows)} parse sites:', ' '.join(f'{k} {v}' for k, v in sorted(cnt.items())))
    for r in rows:
        if r[0] in show or r[0].rstrip('-M') in show:
            print(f'{r[0]:9s} {r[1]}:{r[2]} {r[3]} knob={r[4]} var={r[5]} sinks={r[6]} | {r[7]}')
    for f in FIXED: print('FIXED     ', ' | '.join(f))
    sys.exit(0 if ok else 1)
