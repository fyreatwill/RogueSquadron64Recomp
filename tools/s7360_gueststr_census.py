#!/usr/bin/env python3
"""s7360 class AK census: host code that reads a GUEST string (rdram bytes) with an unbounded scan.

Scope (as s7356-s7359): src/**, lib/N64ModernRuntime/{librecomp,ultramodern}/src/*.cpp, the '+' lines of lib/rt64 (git diff),
plus C text injected by tools/fixup_game_funcs_vendored.py. A row is any line where a string primitive or %s/byte loop touches a
guest-memory expression (rdram / MEM_B / TO_PTR / _arg< / g2h / g_rdram*).
Row kinds: STR  strlen/strnlen/strcmp/strncmp/strchr/strstr/std::string(/string_view(/fputs/puts on a guest expr
           FMT  %s in a printf-family call whose arg list names a guest expr
           LOOP while/for scanning MEM_B/rdram[] for a terminator (!= 0 / != '\\0')
           GSTUB a *_recomp host export that copies guest bytes in a size-driven loop (MEM_B(i, buf))
Classes: CAPPED (explicit index cap and/or range check; MANUAL note) | D (no caller in the generated game/patch code) |
         G (env-gated diagnostic) | B (default-on unbounded) | ? (unreviewed -> exit 1).
Controls: planted snippets, one per kind, must be detected (exit 1 on a miss). usage: python3 tools/s7360_gueststr_census.py [--all]
"""
import re, sys, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
GEN = [ROOT.parent / 'N64Recomp/RecompiledFuncs', ROOT / 'RecompiledPatches']
GX = r'(?:rdram|MEM_BU?\s*\(|TO_PTR|_arg\s*<|g2h|g_rdram\w*)'
STR = re.compile(r'(?<![\w.])(?:std::)?(strlen|strnlen|strcmp|strncmp|strchr|strstr|fputs|puts|string|string_view)\s*\(([^;]*)')
FMT = re.compile(r'printf\s*\(\s*(?:[\w>.-]+\s*,\s*)?(?:[\w]+\s*,\s*)?(?:sizeof\s*\(?\w*\)?\s*,\s*)?"((?:\\.|[^"\\])*)"(.*)')
TERM = re.compile(GX + r'[^;]*(?:!=\s*0\b|!=\s*\'\\\\0\')|^\s*\(?\s*(?:unsigned\s+)?\(?\s*' + GX + r'[^;]*\)?\s*$')
GSTUB = re.compile(r'extern\s+"C"\s+void\s+(\w+_recomp)\s*\(')
SLOOP = re.compile(r'MEM_BU?\s*\(\s*i\s*,\s*\w+\s*\)')
STUBNAME = re.compile(r'(?i)print|rdb|puts|prout|str|name')   # only text-shaped exports; size-driven DMA copies are class AH
LIT = re.compile(r'"(?:\\.|[^"\\])*"')
def loop_cond(L):
    m = re.search(r'\bwhile\s*\((.*)', L)
    if m: return m.group(1).split('{')[0]
    m = re.search(r'\bfor\s*\(([^;]*);([^;]*);', L)
    return m.group(2) if m else None

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
    return bool(re.search(r'getenv\s*\(|static (?:const )?(?:bool|int) \w*(?:on|en|dbg|log)\w* = ', '\n'.join(lines[max(0, i - 40):i + 1])))

_callers = {}
def callers(fn):
    if fn not in _callers:
        n = 0
        for d in GEN:
            if d.is_dir():
                r = subprocess.run(['grep', '-rlF', '--include=*.c', fn + '(rdram', str(d)], capture_output=True, text=True).stdout
                n += len([x for x in r.splitlines() if x])
        _callers[fn] = n
    return _callers[fn]

def scan(lines, only=None):
    rows, stub = [], None
    for i, raw in enumerate(lines):
        if only is not None and (i + 1) not in only: continue
        s = raw.strip()
        m = GSTUB.search(raw)
        if m: stub = m.group(1)
        if s.startswith(('//', '*', '/*')): continue
        L = LIT.sub('""', re.sub(r'//.*', '', raw)); Lf = re.sub(r'//.*', '', raw)
        for m in STR.finditer(L):
            if re.search(GX, m.group(2)): rows.append((i, 'STR', m.group(1)))
        for m in FMT.finditer(Lf):
            if re.search(r'%[-0-9.]*s', m.group(1)):
                # a guest expr only counts if it is a %s argument candidate, i.e. a char* cast or pointer, not a %02X byte
                args = m.group(2)
                if re.search(r'\((?:const\s+)?(?:unsigned\s+)?char\s*\*\)\s*\(?\s*' + GX, args) or re.search(r'TO_PTR\s*\(\s*(?:const\s+)?char', args):
                    rows.append((i, 'FMT', '%s'))
        c = loop_cond(L)
        if c is not None and TERM.search(c.strip()): rows.append((i, 'LOOP', 'scan'))
        if stub and STUBNAME.search(stub) and SLOOP.search(L): rows.append((i, 'GSTUB', stub))
    return rows

# MANUAL: (file-substring, line-substring) -> (class, note). Every row must land here or in an automatic class.
MANUAL = {
    ('librecomp/src/print.cpp', 'MEM_B(i, buf)'): ('D', '__osRdbSend: size<=0x800000 but buf unchecked; 0 callers in RecompiledFuncs+Patches; '
                                                       's7360 adds a [buf, buf+size) < rs64-style 8 MB KSEG0 range check'),
    # s7652: G6c stand-ins (opt-in ROGUESQ_STANDINS=1 at dd>1, mode() in rs64_standins.cpp), read by hand.
    ('src/main/rs64_standins.cpp', 'i < 64 && rb(rdram, name + i) != 0'): ('CAPPED', 'find_model name byte-sum: i < 64 cap; name passed guest() '
                                                       '(< 0x81700000) and the 512 MB host map covers +64'),
    ('src/main/rs64_standins.cpp', 'while (rw(rdram, lists) != 0) {'): ('CAPPED', 'build_instance leaf lists: every pass advances leaf by 0x5C and '
                                                       'returns at leaf + 0x5C > leaf_end (leaves from the model table), so <= leaves+nodes reads'),
}

def classify(path, i, kind, what, lines):
    rel = str(path.relative_to(ROOT)) if str(path).startswith(str(ROOT)) else str(path)
    for (f, sub), v in MANUAL.items():
        if f in rel and sub in lines[i]: return v
    if kind == 'GSTUB' and callers(what) == 0: return ('D', f'{what}: 0 callers in generated code')
    ctx = '\n'.join(lines[max(0, i - 8):i + 1])
    if re.search(r'\bi\s*<\s*(?:\d+|\w+)u?\b', ctx) and re.search(r'<=\s*0x80800000u|<\s*rs64_ram_top|_ok\b', ctx): return ('CAPPED', 'index cap + range check')
    if gated(lines, i): return ('G', 'env-gated diagnostic')
    return ('B', 'default-on unbounded guest string read')

CONTROLS = [
    ('STR', 'size_t n = strlen((const char*)(rdram + off));'),
    ('FMT', 'fprintf(stderr, "name=%s\\n", (const char*)(rdram + off));'),
    ('LOOP', 'while (MEM_BU(n, p) != 0) ++n;'),
    ('LOOP', 'for (n = 0; MEM_BU(n, p); n++) {}'),
    ('GSTUB', 'extern "C" void fakePrintf_recomp(uint8_t* rdram, recomp_context* ctx) {\n for (size_t i = 0; i < size; i++) b[i] = MEM_B(i, buf);'),
]

def main():
    bad = 0
    for kind, snip in CONTROLS:
        got = [r[1] for r in scan(snip.splitlines())]
        ok = kind in got; bad += not ok
        print(f'CTL {kind:5} {"PASS" if ok else "MISS"}')
    tot, cls = 0, {}
    for p, only in files():
        if not p.exists(): continue
        lines = p.read_text(errors='replace').splitlines()
        for i, kind, what in scan(lines, only):
            c, note = classify(p, i, kind, what, lines); tot += 1; cls[c] = cls.get(c, 0) + 1
            if c in ('B', '?') or '--all' in sys.argv:
                print(f'{c:6} {kind:5} {p.relative_to(ROOT.parent)}:{i + 1}  {note}  | {lines[i].strip()[:110]}')
    print(f'TOTAL {tot} ' + ' '.join(f'{k}={v}' for k, v in sorted(cls.items())))
    return 1 if bad or cls.get('B') or cls.get('?') else 0

if __name__ == '__main__': sys.exit(main())
