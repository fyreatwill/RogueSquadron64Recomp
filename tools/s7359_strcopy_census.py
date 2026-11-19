#!/usr/bin/env python3
"""s7359 class AJ census: unbounded string copies into fixed buffers in host code we own.

Scope (as s7356-s7358): src/**, lib/N64ModernRuntime/{librecomp,ultramodern}/src/*.cpp, the lines WE added to lib/rt64 (git diff
'+'), plus C text injected by tools/fixup_game_funcs_vendored.py (the only fixup that injects string formatting; the
apply_s5786/s5798/s5866/s5867/s6992 watch scripts are not wired into the regen pipeline -> D).
Row types and classes:
  CPY   strcpy/strcat/stpcpy/sprintf/vsprintf/gets   CONST (literal source / fixed-width format) | B (default-on) | G (env-gated)
  NCPY  strncpy/strncat                              BOUNDED (n <= dst-1 and terminated) | ? (hand)
  SCAN  sscanf/fscanf %s / %[                        BOUNDED (width given, checked by hand vs dst) | B (no width)
  MEMS  memcpy(.., strlen(..))                       ? (hand)
  ACC   o += snprintf(b + o, cap - o, ..)            GUARDED (an `o < N` test gates the write; width proof in MANUAL) |
        (snprintf returns the untruncated length;     UNGUARDED (nothing stops o passing cap -> cap - o wraps -> overflow) |
         once o > cap the next write overflows)      FIXED (rs64_apf, src/main/rs64_apf.h, s7359)
Controls: planted snippets, one per class (exit 1 on a miss). usage: python3 tools/s7359_strcopy_census.py [--all]
"""
import re, sys, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
CPY = re.compile(r'(?<![\w.:])(?:std::)?(strcpy|strcat|stpcpy|sprintf|vsprintf|gets)\s*\(')
NCPY = re.compile(r'(?<![\w.])(?:std::)?(strncpy|strncat)\s*\(')
SCAN = re.compile(r'(?<![\w.])(?:std::)?(sscanf|fscanf|scanf)\s*\((.*)')
MEMS = re.compile(r'memcpy\s*\([^;]*strlen')
ACC = re.compile(r'(\w+)\s*\+=\s*(?:static_cast<size_t>\(\s*)?(?:std::)?snprintf\s*\(\s*(\w+)\s*\+\s*\1')
APF = re.compile(r'(\w+)\s*=\s*rs64_apf\s*\(')
GUARD = lambda v: re.compile(rf'\b{re.escape(v)}\s*(?:\+\s*\d+\s*)?<\s*(?:\(int\)\s*)?[\w(]')

def files():
    out = [(p, None) for p in sorted((ROOT / 'src').rglob('*')) if p.suffix in ('.cpp', '.c', '.mm', '.h')]
    for d in ('librecomp', 'ultramodern'):
        out += [(p, None) for p in sorted((ROOT / f'lib/N64ModernRuntime/{d}/src').glob('*.cpp'))]
    rt = ROOT / 'lib/rt64'
    diff = subprocess.run(['git', '-C', str(rt), 'diff', '-U0', '--', 'src'], capture_output=True, text=True).stdout
    cur, added = None, {}
    for ln in diff.splitlines():
        if ln.startswith('+++ b/'): cur = ln[6:]; added.setdefault(cur, set())
        elif ln.startswith('@@') and cur:
            m = re.search(r'\+(\d+)(?:,(\d+))?', ln); s, n = int(m.group(1)), int(m.group(2) or 1); added[cur].update(range(s, s + n))
    out += [(rt / f, l) for f, l in sorted(added.items()) if l and f.endswith(('.cpp', '.h', '.mm', '.c'))]
    out.append((ROOT / 'tools/fixup_game_funcs_vendored.py', None))
    return out

def gated(lines, i):
    """env-gated: a getenv/env flag test in the enclosing 40 lines (diagnostic) -> G; else default-on -> B."""
    return bool(re.search(r'getenv\s*\(|static (?:const )?(?:bool|int) \w*(?:on|en|dbg|log)\w* = ', '\n'.join(lines[max(0, i - 40):i + 1])))

def classify(lines, i):
    raw = lines[i]; s = raw.strip()
    if s.startswith(('//', '*', '/*')): return []
    L = re.sub(r'//.*', '', raw); rows = []
    for m in CPY.finditer(L):
        a = L[m.end():]
        if m.group(1) in ('strcpy', 'strcat', 'stpcpy'):
            src = a.split(',', 1)[1].strip() if ',' in a else ''
            rows.append(('CPY', 'CONST' if src.startswith('"') else ('G' if gated(lines, i) else 'B'), m.group(1)))
        elif m.group(1) == 'gets': rows.append(('CPY', 'B', 'gets'))
        else:
            fmt = re.search(r'"((?:\\.|[^"\\])*)"', a); f = fmt.group(1) if fmt else '%s'
            rows.append(('CPY', 'CONST' if not re.search(r'%[-+ #0]*\d*(?:\.\d+)?[sfge]', f) else ('G' if gated(lines, i) else 'B'), m.group(1)))
    for m in NCPY.finditer(L):
        term = any(re.search(r'\[[^\]]*\]\s*=\s*(?:0|\'\\0\')', lines[k]) for k in range(i, min(len(lines), i + 3)))
        rows.append(('NCPY', 'BOUNDED' if term or re.search(r'sizeof\s*\(?\s*\w+\s*\)?\s*-\s*1', L) else '?', m.group(1)))
    for m in SCAN.finditer(L):
        fmt = re.search(r'"((?:\\.|[^"\\])*)"', m.group(2))
        if not fmt: continue
        specs = re.findall(r'%(\*?)(\d*)(s|\[)', fmt.group(1))
        if specs: rows.append(('SCAN', 'BOUNDED' if all(w or st for st, w, _ in specs) else 'B', m.group(1)))
    if MEMS.search(L): rows.append(('MEMS', '?', 'memcpy'))
    J = L + (re.sub(r'//.*', '', lines[i + 1]) if i + 1 < len(lines) else '')   # multi-line `used += static_cast<size_t>(snprintf(\n b + used`
    for m in ACC.finditer(J if 'snprintf' not in L or ACC.search(L) is None else L):
        if m.start() >= len(L): continue
        v = m.group(1)
        hdr = L[:m.start()] + ''.join(lines[k] for k in range(max(0, i - 1), i))
        rows.append(('ACC', 'GUARDED' if GUARD(v).search(hdr) else ('G' if gated(lines, i) else 'UNGUARDED'), v))
    for m in APF.finditer(L): rows.append(('ACC', 'FIXED', m.group(1)))
    return rows

# s7652: keys were 'file:LINE' (prefix-matched on the line number, so 'dpc_bridge.cpp:39' silently covered 39xx and the rest
# went stale as files grew). Now a key is a bare file (file-wide note) or (file, anchor): the anchor must occur in the row's
# line or the next line (multi-line snprintf). An anchor that matches no row is reported as ORPHAN (exit 1).
# MANUAL width proofs for every GUARDED / G accumulator: (file, line-substring) -> note. A GUARDED row is only safe if the
# largest single write fits under (cap - guard) AND the offset is not reused after the loop beyond cap.
MANUAL = {
    'scheduling.cpp': 'o<440 of 512; "%d/%d/s%d " <= 37 chars (three ints) -> max o 476; G (s4583 trace, inflight/k<=20)',
    ('events.cpp', '"%d:%u,", i, cs_hist[i]'): 'n<512-16; "%d:%u," <= 14 chars (i<64, uint) -> type-bounded. G',
    ('dpc_bridge.cpp', '"%03X ", o'): 'k+6<n; "%03X " with o<0x1000 = 4 chars -> type-bounded. G (spike dmem log)',
    'fixup_game_funcs_vendored.py': 'n<(int)sizeof line gate + final n<sizeof-1 test before line[n++]; "%s%lu"/"%s%08X:%lu" (<=29 chars) into 8192 -> bounded. G (s5224/s5225 hist)',
    'rt64_state.cpp': 'rcn<440 of 512; one [wbval] rect row <=115 chars may truncate (snprintf terminates) and stops further writes; rc only used as %s -> safe. G (wbval)',
    'rt64_workload_queue.cpp': 'W row: n<140 loop then wk/lk/pid/rs %.3f ms of unbounded doubles; truncation left n>240 and the final "\\n" append wrapped -> FIXED s7359 (clamp n to sizeof-2). G (rs64_pring_on)',
    ('events.cpp', 'strncpy((char *)nr + 16, xi.pth_name, 63)'): 'strncpy 63 into a 64-byte slot of nr[80] = {2} (zero-filled) -> terminated. G (G1E thread names)',
    ('upstream_compat.cpp', 'spans + used, sizeof(spans) - used, "%s%06X-%06X"'): 'used+20<512; "%s%06X-%06X" of uint32 <= 18 chars -> type-bounded. G (fill-span log)',
    ('dpc_bridge.cpp', 'words + n, sizeof(words) - n, "%s%08X"'): '8 x "%s%08X" (<=9) = 72 < char[96] -> type-bounded. G (g1d chunk words)',
    ('dpc_bridge.cpp', 'pre + pn, sizeof(pre) - pn, "%s%08X"'): '8 x "%s%08X" (<=9) = 72 < char[96] (pre) -> type-bounded. G (g1d-win)',
    ('dpc_bridge.cpp', 'post + qn, sizeof(post) - qn, "%s%08X"'): '8 x "%s%08X" (<=9) = 72 < char[96] (post) -> type-bounded. G (g1d-win)',
    ('events.cpp', 'o += snprintf(b + o, sizeof(b) - o, " %08X", v[i])'): '20 x " %08X" (9 chars) = 180 < char[400] -> type-bounded. G (rs64_vi_shape_log, s7652)',
    ('dpc_bridge.cpp', 'sig_offs + sig_len, sizeof(sig_offs) - sig_len'): 'sig_len+8<96; "%s0x%X" off<0x200 <= 6 chars -> type-bounded. G (sig scan)',
    'rt64_render_context.cpp': 'above<=8 x "%s0x%06X" (<=9 chars) = 72 < 96 -> type-bounded, unguarded by design. G (ROGUESQ_G1D_TI)',
    ('main.cpp', 'k += snprintf(h + k, sizeof h - k, " %s=%llu"'): 'k<512-64 tested before every write; one " %s=%llu" row <= 70 chars '
        '(tag e<48) may truncate: k then exceeds the gate, the loop stops and the final k<sizeof-1 test drops the line -> no wrapped size. (stderr-cap writer, s7652)',
    ('timer.cpp', 'ol += std::snprintf(order + ol, sizeof order - ol, "%X,"'): 'ol<160-8 gate; "%X," of (p-lo)/0x20 <= 8 chars + NUL fits the 9 B left -> bounded. (s7397 CheckTimerAction, s7652)',
}
DEAD = ['apply_s5786_hudbit4_dump.py', 'apply_s5798_recwatch.py', 'apply_s5866_plwatch.py', 'apply_s5867_callers.py', 'apply_s6992_matwatch.py']

USED = set()

def census():
    rows = []
    for p, only in files():
        lines = p.read_text(errors='replace').splitlines(); rel = str(p.relative_to(ROOT))
        for i in range(len(lines)):
            if only is not None and (i + 1) not in only: continue
            for t, c, what in classify(lines, i):
                J = lines[i] + (lines[i + 1] if i + 1 < len(lines) else '')
                key = next((k for k in MANUAL if (k in rel if isinstance(k, str) else (k[0] in rel and k[1] in J))), None)
                if key is not None and not isinstance(key, str): USED.add(key)
                note = MANUAL[key] if key is not None else ''
                rows.append((t, c, f'{rel}:{i + 1}', what, note))
    return rows

def controls():
    snips = [('CPY', 'B', ['char b[8];', 'strcpy(b, getpath());']), ('CPY', 'CONST', ['char b[8];', 'std::strcpy(b, "-");']),
             ('SCAN', 'B', ['char n[16];', 'sscanf(line, "%llx %s", &a, n);']), ('SCAN', 'BOUNDED', ['char n[16];', 'sscanf(line, "%llx %15s", &a, n);']),
             ('ACC', 'UNGUARDED', ['char b[64]; int o = 0;', 'for (int i = 0; i < 20; i++) o += snprintf(b + o, sizeof b - o, "%.1f,", v[i]);']),
             ('ACC', 'GUARDED', ['char b[64]; int o = 0;', 'for (int i = 0; i < 20 && o < 40; i++) o += snprintf(b + o, sizeof b - o, "%d,", v[i]);']),
             ('ACC', 'FIXED', ['char b[64]; int o = 0;', 'for (int i = 0; i < 20; i++) o = rs64_apf(b, sizeof b, o, "%.1f,", v[i]);'])]
    ok = True
    for t, want, ls in snips:
        got = [c for tt, c, _ in classify(ls, 1) if tt == t]
        r = got == [want]; ok &= r; print(f'control {t:4s} {want:9s} -> {got} {"PASS" if r else "FAIL"}')
    return ok

if __name__ == '__main__':
    ok = controls(); rows = census()
    from collections import Counter
    print(f'{len(rows)} sites:', ' '.join(f'{t}/{c} {n}' for (t, c), n in sorted(Counter((r[0], r[1]) for r in rows).items())))
    show = ('B', 'UNGUARDED', '?', 'G', 'GUARDED') if '--all' not in sys.argv else None
    for r in rows:
        if show is None or r[1] in show: print(f'{r[0]:4s} {r[1]:9s} {r[2]} {r[3]} | {r[4] or "(no MANUAL note)"}')
    print('DEAD (not in the regen pipeline):', ', '.join(DEAD))
    bad = [r for r in rows if r[1] == 'B' or (r[1] in ('G', 'GUARDED', 'UNGUARDED', '?') and not r[4])]  # every non-FIXED/CONST/BOUNDED row needs a hand proof
    orphan = [k for k in MANUAL if not isinstance(k, str) and k not in USED]
    for k in orphan: print(f'ORPHAN MANUAL anchor (matches no row): {k}')
    print(f'unresolved {len(bad)} orphan {len(orphan)}'); sys.exit(0 if ok and not bad and not orphan else 1)
