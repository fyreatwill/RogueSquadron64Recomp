#!/usr/bin/env python3
"""s7428 class CK: config-FILE vs ROGUESQ_* env precedence audit (offline).

Enumerates every file-open site (fopen / ifstream / ofstream / open_*_file_with_backup / read_file / write_file) in the
host code the game links (src/, librecomp, ultramodern, rt64 hle) and classifies it:
  ENVPATH  the path comes from a getenv (test/diagnostic file the caller names explicitly) -> no precedence question
  WRITE    output-only to a non-env path (dumps, logs)                                    -> no precedence question
  FIXED    a READ of a fixed path (cwd / exe dir / config dir)                             -> must be in REVIEWED with a check
Then for each REVIEWED fixed-path file it runs a code check:
  rt64.json      RT64::Application loads/saves its user config only if appConfig.useConfigurationFile; our
                 rt64_render_context.cpp must set it false and detectDataPath false (then userPaths is empty).
  audio_device   audio_route_load_pref must test ROGUESQ_AUDIO_DEVICE BEFORE opening the file (env wins), and the F9
                 persist write must be gated by ROGUESQ_NO_SAVE_WRITE (a probe run cannot change the next default).
  save           update_save_file gated by ROGUESQ_NO_SAVE_WRITE (s5721).
Positive control: two planted snippets (file read before env; ungated persist write) must both be flagged.
Runtime half: tools/s7428_audio_route_arms.sh (copied game folder, planted audio_device.txt).
Exit: 0 = H-env-wins, 1 = drift, 3 = control failed.
"""
import os, re, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ROOTS = ['src', 'lib/N64ModernRuntime/librecomp/src', 'lib/N64ModernRuntime/ultramodern/src', 'lib/rt64/src/hle']
OPEN = re.compile(r'\b(?:std::)?(fopen|ifstream|ofstream|open_input_file_with_backup|open_output_file_with_backup|read_file|write_file)\b\s*[({]?\s*([^;]*)')
REVIEWED = {  # (file, function-ish marker) -> name of the check that covers it
    'audio_route_file_path().c_str(), "r"': 'audio_device',
    'audio_route_file_path(), std::ios::binary': 'audio_device',  # s7959 reader via rs64_audio_pref_from_text
    'audio_route_file_path().c_str(), "w"': 'audio_device',
    'userPaths.configurationPath': 'rt64',
    'save_file_path': 'save', 'get_save_file_path': 'save',
    'stored_filename': 'rom',        # librecomp stored ROM copy; no env key selects a ROM
    'mod_path': 'mods', 'full_path': 'mods', 'std::ifstream{ path }': 'mods', 'ifstream file{ path': 'rom',
    'fopen(null_dev': 'write', 'fopen(ipath': 'envpath', 'fopen(dpath': 'envpath',
    'manifest.file_handle->read_file': 'mods',   # files inside a mod archive (mod.json, thumbnails, patches); mods/ is empty
    'read_file(rom_path)': 'rom',                  # select_rom: import of rogue_squadron.z64 etc. from cwd
    'static bool read_json(std::ifstream': 'helper', 'recomp::open_input_backup_file(': 'helper',
    'recomp::open_input_file_with_backup(': 'helper', 'return std::ifstream{backup_path': 'helper',
    'std::ifstream ret{filepath': 'helper',
    # s7718: S7430Rotate (upstream_compat.cpp) opens our own default-on diagnostic log only to size it for rotation: not a
    # config file, no setting is read from it (ROGUESQ_S7430_NO_ROTATE / _CAP tested above it)
    'fopen("rs64_s6892.log", "r")': 'logsize',
}

def code_part(ln):  # s7718: drop a trailing // comment outside string literals (s7106_rsptri.cpp:184 "keep fopen(NULL)")
    q = False
    for j, ch in enumerate(ln):
        if ch == '"' and (j == 0 or ln[j - 1] != '\\'): q = not q
        elif not q and ln.startswith('//', j): return ln[:j]
    return ln

def files():
    for r in ROOTS:
        for d, _, fs in os.walk(r):
            for f in fs:
                if f.endswith(('.cpp', '.c', '.h', '.hpp', '.mm')):
                    yield os.path.join(d, f)

def classify(lines, i, call, arg):
    ctx = '\n'.join(lines[max(0, i - 25):i + 1])
    var = re.match(r'\s*\(?\s*([A-Za-z_][\w.>-]*(?:\(\))?)', arg)
    v = var.group(1) if var else ''
    for k, c in REVIEWED.items():
        if k in lines[i]:
            return 'REVIEWED:' + c
    if call in ('ofstream', 'open_output_file_with_backup', 'write_file') or re.search(r'"[wa]b?\+?"', arg):
        return 'WRITE'
    if v and re.search(r'\b' + re.escape(v.split('.')[0].split('(')[0]) + r'\b[^;\n]*getenv', ctx):
        return 'ENVPATH'
    if re.search(r'getenv\(\s*"(ROGUESQ|RS64)_\w+"', ctx) and v and v.split('.')[0] in ctx.split('getenv')[-2][-200:] if 'getenv' in ctx else False:
        return 'ENVPATH'
    return 'FIXED'

def scan(text_by_file):
    rows = []
    for fn, t in text_by_file.items():
        L = t.split('\n')
        for i, ln in enumerate(L):
            s = ln.strip()
            if s.startswith('//') or s.startswith('*') or re.match(r'(std::)?f?printf\(|fprintf\(', s):
                continue
            for m in OPEN.finditer(code_part(ln)):
                call, arg = m.group(1), m.group(2)
                if call in ('read_file', 'write_file') and ('std::vector' in ln and '(' in ln and 'const' in ln):
                    continue  # definitions
                rows.append((fn, i + 1, call, classify(L, i, call, arg), s[:110]))
    return rows

def fn_body(t, name):
    m = re.search(r'\n[^\n;]*\b' + name + r'\s*\([^;{]*\)\s*\{', t)
    if not m: return ''
    i, d = t.index('{', m.end() - 1), 0
    for j in range(i, len(t)):
        d += t[j] == '{'; d -= t[j] == '}'
        if d == 0: return t[i:j + 1]
    return ''

def check_env_first(body, env, fileop):
    e, f = body.find('getenv("%s")' % env), body.find(fileop)
    return e >= 0 and f >= 0 and e < f

def check_gated_write(body, fileop, gate='ROGUESQ_NO_SAVE_WRITE'):
    f = body.find(fileop)
    return f >= 0 and 0 <= body.find(gate) < f

def checks(main_t, rc_t, pi_t):
    out = []
    ok = 'appConfig.useConfigurationFile = false' in rc_t and 'appConfig.detectDataPath = false' in rc_t and 'appConfig.dataPath' not in rc_t
    out.append(('rt64', ok, 'useConfigurationFile=false, detectDataPath=false, no dataPath -> RT64 reads/writes no config file'))
    lp = fn_body(main_t, 'audio_route_load_pref')
    out.append(('audio_device:env-first', check_env_first(lp, 'ROGUESQ_AUDIO_DEVICE', 'std::ifstream f(audio_route_file_path()'),
                'ROGUESQ_AUDIO_DEVICE tested before audio_device.txt is opened'))
    ac = fn_body(main_t, 'audio_route_apply_cycle')
    out.append(('audio_device:persist-gated', check_gated_write(ac, 'rs64_write_file_atomic(audio_route_file_path()'),
                'F9 persist write gated by ROGUESQ_NO_SAVE_WRITE'))
    us = fn_body(pi_t, 'update_save_file')
    out.append(('save:write-gated', check_gated_write(us, 'open_output_file_with_backup'), 'save write gated by ROGUESQ_NO_SAVE_WRITE'))
    return out

def main():
    T = {f: open(f, errors='replace').read() for f in files()}
    rows = scan(T)
    from collections import Counter
    print('open sites:', len(rows), dict(Counter(r[3] for r in rows)))
    fixed = [r for r in rows if r[3] == 'FIXED']
    for r in rows:
        if r[3].startswith('REVIEWED') or r[3] == 'FIXED':
            print('  %-10s %s:%d %s' % (r[3], r[0], r[1], r[4]))
    main_t, rc_t = T['src/main/main.cpp'], T['src/main/rt64_render_context.cpp']
    pi_t = T['lib/N64ModernRuntime/librecomp/src/pi.cpp']
    res = checks(main_t, rc_t, pi_t)
    for n, ok, d in res:
        print('CHECK %-28s %s  %s' % (n, 'PASS' if ok else 'FAIL', d))
    # positive control: planted drift must be flagged by the same checks and the scanner
    plant = ('static void audio_route_load_pref() {\n if (FILE* f = fopen(audio_route_file_path().c_str(), "r")) {}\n'
             ' else if (const char* env = std::getenv("ROGUESQ_AUDIO_DEVICE")) {}\n}\n'
             'static void audio_route_apply_cycle() {\n if (FILE* f = fopen(audio_route_file_path().c_str(), "w")) {}\n}\n'
             'static void x() { std::ifstream cfg("rs64_planted.json"); }\n')
    pres = checks(plant, rc_t.replace('appConfig.useConfigurationFile = false', 'appConfig.useConfigurationFile = true'), 'void update_save_file() { open_output_file_with_backup(p); }')
    prow = [r for r in scan({'<plant>': plant}) if r[3] == 'FIXED']
    ctl = all(not ok for _, ok, _ in pres) and len(prow) == 1
    print('CONTROL', 'PASS' if ctl else 'FAIL', '(planted: %d/4 checks flagged, %d planted fixed read)' % (sum(not ok for _, ok, _ in pres), len(prow)))
    if not ctl: sys.exit(3)
    drift = fixed or not all(ok for _, ok, _ in res)
    print('VERDICT', 'drift' if drift else 'H-env-wins')
    sys.exit(1 if drift else 0)

if __name__ == '__main__':
    main()
