#!/usr/bin/env python3
"""s7430 class CM: unbounded default-on file growth audit (offline half).

Enumerates every WRITE-mode file open (fopen "w"/"a", ofstream, open_output_file_with_backup) in the host code the
game links (src/, librecomp, ultramodern, rt64 hle/render/common/gui) and classifies each:
  OPTIN     the path or the gate comes from a getenv on the same line, or the site sits under an opt-in env gate
            named in REVIEWED -> an owner run (no logging env) never writes it
  DEFAULT   writes on an owner run; must be in REVIEWED with (mode, bound) -> 'a' without a cross-run cap = GROWTH
Every site that is not same-line-getenv must be in REVIEWED or it is UNREVIEWED (drift).
Positive control (--control or always): planted snippets -- an ungated fixed-path "a" fopen and an unreviewed "w"
fopen -- must be flagged GROWTH / UNREVIEWED.
Runtime half: tools/s7430_file_growth.sh (copied folder, owner recipe twice, plus an s6892 planted-line control).
Exit: 0 = H-bounded, 1 = growth or unreviewed, 3 = control failed.
"""
import os, re, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ROOTS = ['src', 'lib/N64ModernRuntime/librecomp/src', 'lib/N64ModernRuntime/ultramodern/src', 'lib/rt64/src/hle',
         'lib/rt64/src/render', 'lib/rt64/src/common', 'lib/rt64/src/gui']
W = re.compile(r'fopen\s*\(([^;]*?),\s*"([wa])b?\+?"\s*\)|std::ofstream\s+\w+\s*[({]|ofstream\s+\w+\s*\(|open_output_file_with_backup\(')
# substring of the line -> (class, note). DEFAULT entries carry mode/bound; 'GROWTH' marks an unbounded append.
REVIEWED = {
    # s7651 drift triage (6 sites added after s7430 closed; each caller read by hand)
    # s7718: swept for the first time; s7702 census dump (dump_locked <- tick_locked <- rs64_s7702_rdp/_dma, both callers
    # dpc_bridge.cpp:6130 / s7094_dma_shape.cpp:102 test rs64_s7702_on first; "w" truncate every 2 s, one file)
    'fopen("rs64_s7702.log"': ('OPTIN', 'ROGUESQ_S7702_FBREAD (callers gated by rs64_s7702_on; w truncate)'),
    # s7751: rs64_s7751_dump returns on !dir(); one ~18 MB file per completed ring slot (3) per POSE_FREEZE entry, "wb"
    'std::fopen(p, "wb")': ('OPTIN', 'ROGUESQ_S7751_SNAP (dump returns on !dir(); <= 3 files per POSE_FREEZE, wb)'),
    'fopen("rs64_s7535.log"': ('OPTIN', 'ROGUESQ_S7535_GA_CHK (dump only while g_open; snap/close gated by rs64_s7535_on in events.cpp)'),
    'fopen("rs64_s7536.log"': ('OPTIN', 'ROGUESQ_S7536_CNT or ROGUESQ_SP_LATE=alt (c_dump only under s_cnt_on)'),
    'g_tf = e ? fopen(e, "wb")': ('OPTIN', 'ROGUESQ_S7112_TRI (s7466 reworded the s7430-reviewed line)'),
    'fopen("rs64_s7526.log"': ('OPTIN', 'ROGUESQ_S7524_V2P=a (task_begin only when rs64_s7526_alt, main.cpp)'),
    'std::fopen(fp, "wb")) { std::fprintf(f, "P6': ('OPTIN', 'ROGUESQ_S7504_DIR (getenv on the line above)'),
    'fopen(tmp.c_str(), "wb")) { ok = fwrite(text.data()': ('DEFAULT', 'controls.json via .tmp+rename, truncate, only on the F6 panel Save press; refused under ROGUESQ_NO_SAVE_WRITE (s7620)'),
    'fopen("rs64_s7095.log"': ('OPTIN', 'ROGUESQ_S7095_DPC'), 'fopen("rs64_s7097.log"': ('OPTIN', 'ROGUESQ_S7097_EDIT'),
    'fopen("rs64_s7096.log"': ('OPTIN', 'ROGUESQ_S7096_FWD'), 'fopen("rs64_s7094.log"': ('OPTIN', 'ROGUESQ_S7094_DMASHAPE'),
    'fopen("rs64_s7330.log"': ('OPTIN', 'ROGUESQ_S7324_RCPREF'), 'fopen("rs64_s7325.log"': ('OPTIN', 'ROGUESQ_S7324_RCPREF'),
    'fopen("rs64_s7324.log"': ('OPTIN', 'ROGUESQ_S7324_RCPREF'), 'fopen("rs64_s7331.log.tmp"': ('OPTIN', 'ROGUESQ_S7331_RESETW'),
    'g_tf = fopen(e, "wb")': ('OPTIN', 'ROGUESQ_S7112_TRI'), 'g_f = fopen(strcmp(e, "1")': ('OPTIN', 'ROGUESQ_S7106_RSPTRI'),
    'FILE* f = fopen(ipath': ('OPTIN', 'ROGUESQ_DUMP_UCODE'), 'f = fopen(dpath': ('OPTIN', 'ROGUESQ_DUMP_UCODE'),
    'snprintf(name, sizeof(name), "ucode_%06X.bin"': ('MARK', ''),
    'FILE* f = fopen(path, "wb");': ('OPTIN', 'render_context: ROGUESQ_DUMP_VTXDATA / main: ROGUESQ_LOG_AUDIO_OBJECTS'),
    's_rand_trace_f = fopen(rt': ('OPTIN', 'ROGUESQ_RAND_TRACE'), 'if (FILE* f = fopen(path, "wb")) {': ('OPTIN', 'ROGUESQ_EDGE_DUMP'),
    'if (FILE* df = std::fopen(fn, "wb"))': ('OPTIN', 'ROGUESQ_LOG_G1D_CMD'),
    'fwrite(s6883_snap': ('OPTIN', 'ROGUESQ_G1D_SPANDUMP'), 'if (FILE* f = fopen(filename, "wb"))': ('OPTIN', 'ROGUESQ_FB_DUMP_VI'),
    'fwrite(rdram, 1, (size_t)(s_bytes': ('OPTIN', 'ROGUESQ_RDRAM_DUMP_DIR'), 'fopen(out.c_str(), "wb")': ('OPTIN', 'ROGUESQ_RDRAM_SNAP_DIR'),
    'if (FILE* f = fopen(path, "w")) {': ('OPTIN', 's7317_on() ROGUESQ_S7317_ALLOCMAP'), 'fopen(g_s7318_path': ('OPTIN', 'ROGUESQ_S7318'),
    'fopen("rs64_s6893_rdram.bin"': ('DEFAULT', 'wb truncate, once per run (static done), only on the first real s6892 repair; 20 MB'),
    'fopen("rs64_s6893_spill.txt"': ('DEFAULT', 'w truncate, once per run with the rdram dump'),
    'std::fopen(path, "wb")) {': ('OPTIN', 'RS64_GFX_DL_DUMP_DIR'), 'std::fopen(cp, "wb")': ('OPTIN', 'RS64_GFX_DL_DUMP_DIR'),
    'std::fopen(dp2, "wb")': ('OPTIN', 'RS64_GFX_DL_DUMP_DIR'), 'if (FILE* f = fopen(name, "wb"))': ('CTX', ''),
    'g_rs64_tr_f = std::fopen(e': ('OPTIN', 'ROGUESQ_G1E_TRING'),
    'rs64_write_file_atomic(audio_route_file_path()': ('DEFAULT', 'audio_device.txt one line, F9 key only, temp+rename (s7958), gated by ROGUESQ_NO_SAVE_WRITE (s7428)'),
    'FILE* f = std::fopen(tmp.c_str(), "wb");': ('HELPER', 's7958 rs64_write_file_atomic temp file'),
    'tr = fopen(e, "w")': ('OPTIN', 'ROGUESQ_AI_TRACE'), 'tp = fopen((std::string(e)': ('OPTIN', 'ROGUESQ_AI_TRACE'),
    's_pcm_raw = fopen(e': ('OPTIN', 'ROGUESQ_PCM_RAW'), 'fr = fopen(s_ref_path': ('OPTIN', 'ROGUESQ_POSE_REF'),
    'fopen(null_dev, "w")': ('DEFAULT', '/dev/null sink for RT64 log, no file'),
    'std::ofstream out_file{ path, std::ios::binary }': ('DEFAULT', 'stored ROM copy, once on ROM import'),
    'std::ofstream recomp::open_output_file_with_backup': ('HELPER', ''), 'std::ofstream temp_file_out{ temp_path': ('HELPER', ''),
    'open_output_file_with_backup(ultramodern::get_save_file_path()': ('DEFAULT', 'save, fixed 16 KB, gated by ROGUESQ_NO_SAVE_WRITE'),
    'ramdump" + std::string': ('OPTIN', 'dump_frame is never set true anywhere (dead debug path)'),
    'std::ofstream output_file = recomp::open_output_file_with_backup(path)': ('OPTIN', 'mod config, only on mod-menu action; mods/ empty'),
    'std::fopen(fn, "wb"); }();': ('OPTIN', 'ROGUESQ_G1E_TL'), 'fwrite(rdram + 0x100000': ('OPTIN', 'ROGUESQ_G1E_DUMP'),
    'fwrite(rdram, 1, 0x800000': ('OPTIN', 'ROGUESQ_RAMSNAP'),
    'cfgStream(userPaths.configurationPath': ('OPTIN', 'useConfigurationFile=false (s7428)'),
    'rt64_rdp.cpp': ('OPTIN', 'ROGUESQ_DUMP_HANGAR_TEX / LOG_LOADS / DUMP_CI_LOAD / BUF dump / DUMP_TMEM_LOAD / DUMP_TMEM_DRAW'),
    'rt64_state.cpp': ('OPTIN', 'ROGUESQ_DUMP_CI / DUMP_TMEM_DRAW / sprite replacement dump (texture-pack tooling)'),
    'rt64_framebuffer.cpp': ('OPTIN', 'fl_snap freelist snapshot (env)'), 'rt64_rdp_tmem.cpp': ('OPTIN', 'dumpingTexturesDirectory empty'),
    'rt64_framebuffer_renderer.cpp': ('OPTIN', 'ROGUESQ_FLOOR_DEPTH_DIR / LOG_CIMG dirs'),
    'databaseNewFile(databaseNewPath)': ('OPTIN', 'texture replacement pack save, none loaded'),
    'FILE *f = std::fopen(e, "wb"); if (!f) return false;': ('OPTIN', 'ROGUESQ_G1E_THREADS (previous line)'),
    'rt64_texture_cache.cpp': ('OPTIN', 'ROGUESQ_DUMP_TMEM_DIR / replacement pack save'),
    'rt64_native_target.cpp': ('OPTIN', 'ROGUESQ_FLOOR_PIPE_DIR'), 'define RT64_LOG_OPEN': ('OPTIN', 'logPath empty: no data path'),
    'rt64_debugger_inspector.cpp': ('OPTIN', 'RT64 debugger UI, not shown'),
}
PLANT = ('src/s7430_plant.cpp', ['static void plant() {', '    if (FILE* f = fopen("rs64_plant.log", "a")) fclose(f);',
                                  '    FILE* g = fopen("rs64_plant2.txt", "w");', '}'])

def sites(files):
    for p, L in files:
        for i, l in enumerate(L):
            if W.search(l):
                yield p, i + 1, l.strip()

CTXGATE = {'rs64_dump_ucode': ('OPTIN', 'ROGUESQ_DUMP_UCODE_BIN (s7430; was DEFAULT, 512 KB/run)'),
           'rs64_audio_source_objects': ('OPTIN', 'ROGUESQ_LOG_AUDIO_OBJECTS')}
def enclosing_legacy(L, n):  # s7430 backward column-0 scan, no brace check (kept for --diff)
    for k in range(n - 1, -1, -1):
        m = re.match(r'(?:static\s+)?(?:void|bool|int|FILE\s*\*)\s+(\w+)\s*\(', L[k])
        if m: return m.group(1), '\n'.join(L[k:n])
    return '', ''
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from census_attr import fn_spans, enclosing_braced  # s7651: brace-aware attribution (s7650 algorithm)
_SPANS, DIFF = {}, []
def enclosing(L, n):
    sp = _SPANS.setdefault(id(L), (L, fn_spans(L)))[1]
    fn, j = enclosing_braced(sp, n - 1)
    old = enclosing_legacy(L, n)[0]
    if old != (fn if j is not None else ''): DIFF.append((n, old, fn))
    return (fn, '\n'.join(L[j:n])) if j is not None else ('', '')
def classify(p, l, L=None, n=0):
    if 'getenv' in l: return ('OPTIN', 'same-line getenv')
    if L is not None and 'fopen(name, "wb")' in l:
        fn, body = enclosing(L, n)
        if fn in CTXGATE and 'getenv("' + CTXGATE[fn][1].split()[0] + '")' in body: return CTXGATE[fn]
        return ('UNREVIEWED', f'enclosing {fn}: no gate')
    if L is not None and 'fopen("rs64_s6892.log", "a")' in l:
        fn, body = enclosing(L, n); whole = '\n'.join(L)
        if 'std::rename("rs64_s6892.log", "rs64_s6892.log.1")' in whole and re.search(r'}\s*}\s*s7430_rotate;', whole):
            return ('DEFAULT', f'append, rotated to .1 above 256 KiB at process start (s7430 S7430Rotate static init, in {fn})')
        return ('GROWTH', f'append, 32 lines/run, no cross-run cap (in {fn})')
    for k, v in REVIEWED.items():
        if k in l or k == os.path.basename(p): return v
    return ('UNREVIEWED', '')

def scan(files):
    FL = dict(files)
    rows = [(p, n, l) + classify(p, l, FL[p], n - 1) for p, n, l in sites(files)]
    return rows

REV = sys.argv[sys.argv.index('--rev') + 1] if '--rev' in sys.argv else None
def load():
    if REV:  # same audit on a committed tree (src/ only; lib/ is submodules) -- HEAD before s7430 must flag 2 defects
        import subprocess
        for p in subprocess.run(['git', 'ls-tree', '-r', '--name-only', REV, 'src'], capture_output=True, text=True).stdout.split():
            if p.endswith(('.cpp', '.c', '.h', '.hpp', '.mm')):
                yield p, subprocess.run(['git', 'show', f'{REV}:{p}'], capture_output=True, text=True, errors='replace').stdout.split('\n')
        return
    for r in ROOTS:
        for d, _, fs in os.walk(r):
            for f in fs:
                if f.endswith(('.cpp', '.c', '.h', '.hpp', '.mm')):
                    p = os.path.join(d, f); yield p, open(p, errors='replace').read().split('\n')

real = scan(list(load()))
ctl = scan([PLANT])
cok = sorted(c for *_, c, _ in ctl) == ['GROWTH', 'UNREVIEWED'] if False else None
cls = [r[3] for r in ctl]
# the planted "a" fopen to a fixed path is unreviewed -> must surface; an unreviewed 'a' counts as GROWTH
def verdict(rows):
    g = [r for r in rows if r[3] == 'GROWTH' or (r[3] == 'UNREVIEWED' and re.search(r'"ab?\+?"', r[2]))]
    u = [r for r in rows if r[3] == 'UNREVIEWED' and r not in g]
    return g, u
cg, cu = verdict(ctl)
cpass = len(cg) == 1 and len(cu) == 1
print(f'CONTROL {"PASS" if cpass else "FAIL"}: planted growth={len(cg)} unreviewed={len(cu)} (want 1/1)')
from collections import Counter
print('sites', len(real), dict(Counter(r[3] for r in real)))
for r in real:
    if r[3] in ('DEFAULT', 'GROWTH', 'UNREVIEWED'):
        print(f'  {r[3]:10s} {r[0]}:{r[1]}  {r[4]}' + ('' if r[4] else '  ' + r[2][:90]))
if '--diff' in sys.argv:
    print('attribution diff (line, legacy, braced):', DIFF or 'none')
g, u = verdict(real)
if not cpass: sys.exit(3)
print('VERDICT', 'H-bounded' if not g and not u else f'H-growth ({len(g)} growth, {len(u)} unreviewed)')
sys.exit(0 if not g and not u else 1)
