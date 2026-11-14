#!/usr/bin/env python3
"""s7356 class AG census: host allocation / mapping / file-open results used without a failure check.

Scope: every line of src/** and lib/N64ModernRuntime/{librecomp,ultramodern}/src/*.cpp, plus the lines WE added to
lib/rt64 (git diff -U0 '+' lines; upstream RT64 code is out of scope).
Sites: malloc/calloc/realloc/strdup/mmap/fopen/popen/fdopen/opendir/dup/SDL_Create*/new(std::nothrow).
For each site, find the variable the result lands in and scan forward (same function, up to the closing brace of the
enclosing block or 80 lines) for the first CHECK of that variable vs the first USE of it:
  CHECKED  a check (if (x) / !x / x == nullptr / x != nullptr / x == MAP_FAILED / x < 0 / x && / x ?) precedes every use,
           or the result is bound in the condition itself (if (FILE *f = fopen(...)))
  STATIC   a static/global sink (log FILE*): every use in the file must sit on a line, or under a line within 3 above,
           that tests the variable; otherwise B/G as below
  G        unchecked, but the site is inside an env-gated diagnostic (getenv/env flag within 25 lines above)
  B        unchecked on a default-on path
  D        _WIN32-only or a comment
  ?        result not captured in a recognisable variable
Controls: planted snippets must classify B / CHECKED / G (exit 1 if not).
"""
import re, sys, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
CALL = re.compile(r'(?<![\w.>])(?:std::)?(malloc|calloc|realloc|strdup|mmap|fopen|popen|fdopen|opendir|dup|SDL_Create\w+)\s*\(|new\s*\(\s*std::nothrow\s*\)')
GATE = re.compile(r'getenv|env_on|env_flag|rs64_env|ROGUESQ_|g_\w*(?:on|enabled|dump|log)\w*\b|_on\(\)')

def check_re(v):
    v = re.escape(v)
    return re.compile(rf'if\s*\(\s*!?\s*\(?\s*{v}\s*[\)&|]|!\s*{v}\b|\b{v}\s*[!=]=\s*(?:nullptr|NULL|0|MAP_FAILED|-1)'
                      rf'|\b{v}\s*<\s*0|\b{v}\s*>=?\s*0|\b{v}\s*&&|\b{v}\s*\?|\(\s*{v}\s*\)\s*\{{|\bif\s*\(\s*{v}\s*\)'
                      rf'|(?:nullptr|NULL|MAP_FAILED)\s*[!=]=\s*{v}\b|\|\|\s*{v}\s*[!=]=|while\s*\(\s*{v}\s*\)')

def use_re(v):
    return re.compile(rf'(?<![\w.])(?<!->){re.escape(v)}\b(?!\s*=[^=])')

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

def guarded(lines, k, var, chk):
    """A use at line k is guarded if its own line tests var, an enclosing block header tests it, or an earlier line of the
    same function bails out on it (if (!var ...) return/continue/break)."""
    if chk.search(lines[k]): return True
    bail = re.compile(r'if\s*\(\s*!\s*' + re.escape(var) + r'\b[^;]*\)\s*(?:\{\s*)?(?:[^;]*;\s*)?(?:return|continue|break|goto|throw|abort|exit|_exit|std::abort)')
    bail2 = re.compile(r'if\s*\([^;]*\b' + re.escape(var) + r'\s*==\s*(?:nullptr|NULL|MAP_FAILED)[^;]*\)\s*(?:\{\s*)?(?:[^;]*;\s*)?(?:return|continue|break|throw|abort|exit|_exit|std::abort)')
    depth = 0
    for j in range(k - 1, max(-1, k - 400), -1):
        ln = re.sub(r'"(?:\\.|[^"\\])*"|//.*', '', lines[j])
        depth += ln.count('}') - ln.count('{')
        if depth < 0:
            if chk.search(lines[j]): return True
            depth = 0
        if bail.search(lines[j]) or bail2.search(lines[j]): return True
        if re.match(r'^\S', lines[j]) and not lines[j].startswith(('#', '//', '}')) and '(' in lines[j]: break  # function header
    return False

def classify(lines, i):
    """lines: list of source lines; i: index of the site line. Returns (cls, var, why)."""
    L = lines[i]; s = L.strip()
    if s.startswith('//') or s.startswith('*'): return 'D', '', 'comment'
    pre = '\n'.join(lines[max(0, i - 40):i])
    if pre.rfind('#ifdef _WIN32') > max(pre.rfind('#endif'), pre.rfind('#else')): return 'D', '', '_WIN32'
    m = CALL.search(L); head = L[:m.start()]
    mc = re.search(r'\b(?:if|while)\s*\(\s*(?:[\w:]+\s*\*?\s*)?(\w+)\s*=\s*(?:\([^)]*\)\s*)?$', head)
    if mc: return 'CHECKED', mc.group(1), 'bound in condition'
    win = '\n'.join(lines[max(0, i - 2):i + 1])
    ms = re.search(r'static\s+[\w:]+\s*\*\s*(\w+)\s*=\s*\[', win)
    mv = re.search(r'([A-Za-z_]\w*(?:(?:\.|->)[A-Za-z_]\w*|\[[^\]]*\])*)\s*=\s*(?:\([^()]*\)\s*|(?:static|reinterpret)_cast<[^>]*>\s*\()?\s*(?:[^;?]*\?\s*)?$', head)
    if ms: var = ms.group(1)
    elif mv: var = mv.group(1)
    else: return ('?', '', 'returned to caller') if re.search(r'\breturn\b', head) else ('?', '', 'not captured')
    local = bool(re.search(r'(?:\b(?:auto|FILE|char|void|int|uint\w*|size_t|SDL_\w+|\w+_t)\b\s*\**\s*)' + re.escape(var) + r'\s*=', head)) and not re.search(r'\bstatic\b', head) and not ms
    gated = bool(GATE.search('\n'.join(lines[max(0, i - 25):i + 1])))
    key = re.split(r'\.|->', var)[-1]
    chk = check_re(key); use = re.compile(rf'(?<![\w])(?<!\.)(?<!->){re.escape(key)}\b(?!\s*=[^=])' if key == var else rf'{re.escape(key)}\b(?!\s*=[^=])')
    # same line after the call: `x = fopen(..); if (!x) return;`
    if chk.search(L[m.end():]): return 'CHECKED', var, 'check on site line'
    end = len(lines)
    if local:
        depth = 0
        for k in range(i, len(lines)):
            depth += lines[k].count('{') - lines[k].count('}')
            if depth < 0: end = k + 1; break
        rng = range(i + 1, end)
    else:
        rng = [k for k in range(len(lines)) if k != i]
    bad = [k for k in rng if use.search(re.sub(r'//.*', '', lines[k])) and not re.search(rf'\b{re.escape(key)}\s*=[^=]', lines[k])
           and not guarded(lines, k, key, chk)]
    if not bad: return 'CHECKED', var, ('local' if local else 'static/global') + ': every use tested'
    return ('G' if gated else 'B'), var, f'untested use at line {bad[0] + 1}: {lines[bad[0]].strip()[:80]}'

# Hand-verified dispositions (s7356) for rows the line heuristic cannot settle (short static names like `f` collide across a
# file; checks sit in a caller or an enclosing helper). Keyed by (path suffix, var); reclassified as CHECKED-M / G-M / D-M.
MANUAL = {
    ('mod_manifest.cpp', 'file_handle'): ('CHECKED-M', 'if (!file_handle) on the next line (#else branch; heuristic saw the _WIN32 use)'),
    ('recomp.cpp', 'rdram'): ('CHECKED-M', 'alloc_failed = rdram == MAP_FAILED -> message_box + return'),
    ('rt64_framebuffer_renderer.cpp', 'log.fp'): ('CHECKED-M', 'copyRamOpen returns log.fp != nullptr; callers bail on false'),
    ('rt64_framebuffer_renderer.cpp', 'log.rd'): ('CHECKED-M', 'rdramOpen returns log.rd != nullptr; callers bail on false'),
    ('rt64_framebuffer_renderer.cpp', 'g_depthJson'): ('CHECKED-M', 'depthWriteEvent: if (g_depthJson == nullptr) return after ensure'),
    ('main.cpp', 'p'): ('CHECKED-M', 'popen(nm): if (!p) { fprintf; return; } on the next line'),
    ('main.cpp', 'g_s5229_pc'): ('CHECKED-M', 's7356 FIX: fail-fast after the three calloc (env-gated ROGUESQ_LOG_S5223_ENTRY_JOIN)'),
    ('main.cpp', 'g_s5229_val'): ('CHECKED-M', 's7356 FIX (same block)'),
    ('main.cpp', 'g_s5229_w'): ('CHECKED-M', 's7356 FIX (same block)'),
    ('main.cpp', 'g_s4457_tab'): ('CHECKED-M', 's7356 FIX: fail-fast after calloc (env-gated rs64_s4457_on)'),
    ('main.cpp', 'pcm'): ('CHECKED-M', 'only use: if (pcm && ...) fwrite'),
    ('main.cpp', 'fr'): ('CHECKED-M', 'if (fr) { fwrite } / if (fr) fclose'),
    ('main.cpp', 'sdl_window'): ('CHECKED-M', 'if (!sdl_window) error path 7 lines below'),
    ('rt64_render_context.cpp', 'f'): ('CHECKED-M', 'f = fopen(dpath); if (f) {...}'),
    ('upstream_compat.cpp', 's'): ('CHECKED-M', 'x->fo: put()/flush() test !fo; s7064() only reached under g_rs64_s7064 (env)'),
    ('events.cpp', 'f'): ('CHECKED-M', 'g1eg::put callers (r_row/g_row) are only called under if (g1eg::f)'),
    ('dpc_bridge.cpp', 'f'): ('CHECKED-M', 'g5b_frame: if (!f ...) return; census/g3e files: callers use if (FILE *f = ...())'),
    ('dpc_bridge.cpp', 's_fg'): ('CHECKED-M', 'every use under if (s_fg && ...) / (s_sh || killsheet || s_fg) is a test'),
    ('overlays.cpp', 'section_addresses'): ('CHECKED-M', 's7356 FIX: was B (default-on null write at boot); now named FATAL + abort'),
}
MANUAL_Q = {  # rows the regex could not bind to a variable
    ('main.cpp', 'popen(nm) failed'): 'the error message line inside the popen check, not a call site',
    ('rs64_env_cache.cpp', 'strdup(name)'): 'null key leaves the slot empty: next lookup retries (designed null tolerance)',
    ('dpc_bridge.cpp', 'g5b_tg_open'): 'returns to g_g5b_tg; every use tests rs64_g5b_tg_on / g_g5b_tg',
}

def apply_manual(rows):
    out = []
    for cls, path, line, var, why, src in rows:
        if cls in ('B', 'G'):
            for (suf, v), (nc, r) in MANUAL.items():
                if path.endswith(suf) and var == v: cls, why = nc, r; break
        elif cls == '?':
            for (suf, frag), r in MANUAL_Q.items():
                if path.endswith(suf) and frag in src: cls, why = 'D-M', r; break
        out.append((cls, path, line, var, why, src))
    return out

def run(paths):
    rows = []
    for p, only in paths:
        try: lines = p.read_text(errors='replace').splitlines()
        except Exception: continue
        for i, ln in enumerate(lines):
            if only is not None and (i + 1) not in only: continue
            if not CALL.search(re.sub(r'"(?:\\.|[^"\\])*"', '""', ln)) or re.search(r'\b(?:extern|typedef)\b|#define|\bfprintf\b.*"[^"]*fopen', ln): continue
            if re.search(r'^\s*(?:static\s+)?[\w:*\s]+\b(?:fopen|malloc|mmap)\s*\([^)]*\)\s*;', ln) and '=' not in ln: continue
            cls, var, why = classify(lines, i)
            rows.append((cls, str(p.relative_to(ROOT)), i + 1, var, why, ln.strip()[:110]))
    return rows

def main():
    rows = run(files()) if '--raw' in sys.argv else apply_manual(run(files()))
    tally = {}
    for r in rows: tally[r[0]] = tally.get(r[0], 0) + 1
    for r in sorted(rows, key=lambda r: ('B?GCD'.find(r[0][0]), r[1], r[2])):
        if r[0] in ('B', '?', 'G') or r[0].endswith('-M') or '-v' in sys.argv: print(f'{r[0]:7} {r[1]}:{r[2]} [{r[3]}] {r[4]} | {r[5]}')
    print('sites:', len(rows), 'tally:', dict(sorted(tally.items())))
    ctl = {
        'B':       ['void f() {', '  char *p = (char *)malloc(64);', '  p[0] = 1;', '}'],
        'CHECKED': ['void f() {', '  char *p = (char *)malloc(64);', '  if (!p) return;', '  p[0] = 1;', '}'],
        'G':       ['void f() {', '  if (!getenv("X")) return;', '  FILE *fp = fopen("a", "w");', '  fprintf(fp, "x");', '}'],
    }
    ok = True
    for want, src in ctl.items():
        i = next(k for k, l in enumerate(src) if CALL.search(l))
        got = classify(src, i)[0]
        print(f'control {want:7}: got {got:7} {"PASS" if got == want else "FAIL"}'); ok &= got == want
    print('CONTROLS', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
