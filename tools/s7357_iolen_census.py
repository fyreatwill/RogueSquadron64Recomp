#!/usr/bin/env python3
"""s7357 class AH census: host I/O length results (fread/read/pread/fgets/fwrite/write/pwrite/fseek/ftell/lseek and
iostream .read/.write/.tellg/.seekg) used unchecked, so a short read is treated as full data, a failed write as a good save,
or ftell/tellg's -1 becomes a huge size.

Scope: src/** + lib/N64ModernRuntime/{librecomp,ultramodern}/src/*.cpp + the lines WE added to lib/rt64 (git diff '+').
Classes:
  CHECKED  the result is tested: the call sits in an if/while condition or a comparison (== != < <= > >=), or is
           assigned to a variable tested within 3 lines, or (iostream) the stream's gcount()/good()/fail()/!s is tested
           within 8 lines after the call
  W        unchecked write to an output-only diagnostic sink (dump/log opened for write); short write = truncated dump
  G        unchecked, inside an env-gated diagnostic (getenv/ROGUESQ_/env flag within 30 lines above)
  B        unchecked on a default-on path
  D        comment / _WIN32 / stdout|stderr console print (a short console write loses only console text)
Then MANUAL (hand-verified) dispositions. Controls: planted snippets must classify B / CHECKED / G (exit 1 if not).
"""
import re, sys, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
CALL = re.compile(r'(?:(?<![\w.>:])|(?<=std::)|(?<=[^\w]::))(fread|read|pread|fseek|fseeko|ftell|ftello|fgets|fwrite|write|pwrite|lseek)\s*\(|'
                  r'(\w+)\s*(?:\.|->)\s*(read|write|tellg|seekg|tellp)\s*\(')
GATE = re.compile(r'getenv|env_on|env_flag|rs64_env|ROGUESQ_|g_\w*(?:on|enabled|dump|log)\w*\b|_on\(\)|\bs_\w*(?:on|dump|log)\b')
CMP = r'(?:==|!=|<=?|>=?)'

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

def classify(lines, i, m):
    L = strip(lines[i]); s = lines[i].strip()
    if s.startswith(('//', '*', '/*')): return 'D', 'comment'
    pre = '\n'.join(lines[max(0, i - 40):i])
    if pre.rfind('#ifdef _WIN32') > max(pre.rfind('#endif'), pre.rfind('#else')): return 'D', '_WIN32'
    fn = m.group(1) or m.group(3); obj = m.group(2)
    if fn in ('fwrite', 'write') and re.search(r'\b(?:stdout|stderr)\s*\)|write\s*\(\s*[12]\s*,', L[m.start():m.start() + 200]):
        return 'D', 'console write'
    if fn == 'read' and re.match(r'\s*ram\b', L[m.end():]): return 'D', 'rt64 RDRAM accessor, not I/O'
    head = L[:m.start()]
    # in a condition or comparison
    if re.search(r'\b(?:if|while)\s*\([^;]*$', head) or re.search(CMP + r'\s*\(?\s*$', head) or \
       re.match(r'[^;]*\)\s*' + CMP, L[m.end():] if fn else '') or re.search(r'\breturn\b[^;]*$', head) and fn in ('fread', 'read', 'fgets'):
        return 'CHECKED', 'in condition/comparison'
    # balance to find the end of the call, then look for a comparison directly after it
    depth, k = 1, m.end()
    while k < len(L) and depth: depth += {'(': 1, ')': -1}.get(L[k], 0); k += 1
    if re.match(r'\s*\)*\s*' + CMP, L[k:]): return 'CHECKED', 'result compared'
    mv = re.search(r'([A-Za-z_]\w*)\s*=\s*(?:\([^()]*\)\s*|static_cast<[^>]*>\s*\()?\s*$', head)
    if mv:
        v = mv.group(1); win = '\n'.join(strip(x) for x in lines[i:i + 4])
        if re.search(rf'\b{v}\b\s*{CMP}|{CMP}\s*{v}\b|if\s*\(\s*!?\s*{v}\b', win.replace(L[:m.end()], '', 1)): return 'CHECKED', f'{v} tested'
    if obj:
        win = '\n'.join(strip(x) for x in lines[i:i + 9])
        if re.search(rf'\b{obj}\s*\.\s*(?:gcount|good|fail|bad)\s*\(|!\s*{obj}\b|if\s*\(\s*{obj}\s*\)', win): return 'CHECKED', 'stream state tested'
    if obj and fn in ('seekg',) : pass
    gated = bool(GATE.search('\n'.join(lines[max(0, i - 30):i + 1])))
    PERSIST = ('save_file', 'out_file', 'output_file')  # files the program reads back: never 'W'
    if fn in ('fwrite', 'write', 'pwrite') and obj not in PERSIST:
        # output-only diagnostic sink: opened for writing nearby (fopen "w"/"a", ofstream) or a static/global log FILE*.
        # A short write only truncates that dump; nothing in-process reads it back. Persisted files (save, stored ROM,
        # mod config) are NOT in this class: they are listed in MANUAL with their fix.
        sink = re.search(r'(\w+)\s*\)\s*;?', L[m.end():].split(';')[0][::-1][::-1])
        args = L[m.end():]; d2, e = 1, 0
        while e < len(args) and d2: d2 += {'(': 1, ')': -1}.get(args[e], 0); e += 1
        last = re.split(r',', args[:e - 1])[-1].strip()
        near = '\n'.join(lines[max(0, i - 60):i + 1])
        if re.search(r'fopen\s*\([^;]*"(?:[wa]b?|[wa]\+?b?)"|std::ofstream', near) or re.match(r'(?:s_|g_)\w+$', last):
            return 'W', f'diagnostic output sink {last}'
    return ('G' if gated else 'B'), 'result unused'

# Hand-verified dispositions (s7357). Key: (path suffix, fragment of the site line) -> (class, reason).
MANUAL = {
    ('librecomp/src/recomp.cpp', 'file.seekg(0, std::ios::end)'): ('CHECKED-M', 's7357 FIX: read_file checks tellg<0, read gcount; short -> empty (FailedToOpen)'),
    ('librecomp/src/recomp.cpp', 'ret.resize(file.tellg())'): ('CHECKED-M', 's7357 FIX (same block)'),
    ('librecomp/src/recomp.cpp', 'file.seekg(0, std::ios::beg)'): ('CHECKED-M', 's7357 FIX (same block)'),
    ('librecomp/src/recomp.cpp', 'out_file.write('): ('CHECKED-M', 's7357 FIX: write_file flushes and returns out_file.good(); caller logs failure'),
    ('librecomp/src/pi.cpp', 'save_file.write('): ('CHECKED-M', 's7357 FIX: flush+good() after write; failure skips finalize (no truncated save over the real one)'),
    ('librecomp/src/pi.cpp', 'save_file.read('): ('CHECKED-M', 's7357 FIX: gcount short -> zero-fill tail (no previous-profile bytes) + named warning'),
    ('librecomp/src/mod_manifest.cpp', 'file.seekg(0, std::ios::end)'): ('CHECKED-M', 's7357 FIX: tellg<0 / short read -> exists=false'),
    ('librecomp/src/mod_manifest.cpp', 'file.seekg(0, std::ios::beg)'): ('CHECKED-M', 's7357 FIX (same block)'),
    ('librecomp/src/sp.cpp', 'dump_file.write('): ('G-M', 'dump_frame debug ramdump (compile-time false); truncated dump only'),
    ('ultramodern/src/events.cpp', 'std::fwrite(buf.data(), 1, buf.size(), f)'): ('W-M', 'g1e thread sampler run(f): f fopen("wb") in started lambda, only under ROGUESQ_G1E_THREADS'),
    ('ultramodern/src/events.cpp', 'std::fwrite(r5, 1, 16, f)'): ('W-M', 'same sampler (header record)'),
    ('librecomp/src/print.cpp', 'fwrite(to_print.get()'): ('D-M', 'guest osSyncPrintf to stdout'),
}

def apply_manual(rows):
    out = []
    for cls, path, line, why, src in rows:
        if cls in ('B', 'G'):
            for (suf, frag), (nc, r) in MANUAL.items():
                if path.endswith(suf) and frag in src: cls, why = nc, r; break
        out.append((cls, path, line, why, src))
    return out

def run(paths):
    rows = []
    for p, only in paths:
        try: lines = p.read_text(errors='replace').splitlines()
        except Exception: continue
        for i, ln in enumerate(lines):
            if only is not None and (i + 1) not in only: continue
            for m in CALL.finditer(strip(ln)):
                if re.search(r'\b(?:extern|typedef)\b|#define', ln): continue
                cls, why = classify(lines, i, m)
                rows.append((cls, str(p.relative_to(ROOT)), i + 1, why, ln.strip()[:120]))
    return rows

def main():
    rows = run(files()) if '--raw' in sys.argv else apply_manual(run(files()))
    tally = {}
    for r in rows: tally[r[0]] = tally.get(r[0], 0) + 1
    for r in sorted(rows, key=lambda r: ('BGWCD'.find(r[0][0]), r[1], r[2])):
        if r[0] in ('B', 'G') or r[0].endswith('-M') or '-v' in sys.argv: print(f'{r[0]:9} {r[1]}:{r[2]} {r[3]} | {r[4]}')
    print('sites:', len(rows), 'tally:', dict(sorted(tally.items())))
    ctl = {
        'B':       ['void f(FILE *fp, char *b) {', '  fread(b, 1, 64, fp);', '  use(b);', '}'],
        'CHECKED': ['void f(FILE *fp, char *b) {', '  if (fread(b, 1, 64, fp) != 64) return;', '  use(b);', '}'],
        'G':       ['void f(FILE *fp, char *b) {', '  if (!getenv("X")) return;', '  fread(b, 1, 64, fp);', '}'],
        'W':       ['void f(char *b) {', '  FILE *d = fopen("dump.bin", "wb");', '  fwrite(b, 1, 64, d);', '}'],
        'B ':      ['void f(char *b) {', '  std::ofstream save_file{p};', '  save_file.write(b, 64);', '}'],
        'CHECKED ':['void f(char *b) {', '  std::ifstream s{p};', '  s.read(b, 64);', '  if (s.gcount() != 64) return;', '}'],
    }
    ok = True
    for want, src in ctl.items():
        i = next(k for k, l in enumerate(src) if CALL.search(l))
        got = classify(src, i, CALL.search(src[i]))[0]; want = want.strip()
        print(f'control {want:7}: got {got:7} {"PASS" if got == want else "FAIL"}'); ok &= got == want
    print('CONTROLS', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
