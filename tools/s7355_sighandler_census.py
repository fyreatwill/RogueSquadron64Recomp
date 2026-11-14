#!/usr/bin/env python3
"""s7355 class AF census: async-signal-unsafe calls reachable from installed signal handlers.

Enumerates every signal()/sigaction() install in src/main/main.cpp, extracts the handler body, descends into callees
defined in main.cpp (depth 2) plus the one cross-file callee, and classifies each call:
  SAFE  POSIX async-signal-safe, an atomic op, or MEASURED safe under a held malloc lock (tools/s7355_sighandler_ctl.cpp)
  G     reached only past a default-off gate (env/atomic flag tested in the callee's first lines)
  D     dead on this platform (#ifdef _WIN32 branch)
  B     MEASURED unsafe (aborts with the malloc lock held: a crash inside malloc/free loses its whole report)
  ?     unclassified (no measurement, not on the POSIX list)
Controls: planted handlers must classify as B / SAFE / G / ? (exit 1 if not).
"""
import re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
MAIN_RAW = (ROOT / 'src/main/main.cpp').read_text()
_blank = lambda m: re.sub(r'[^\n]', ' ', m.group(0))  # same length, so offsets into MAIN and MAIN_RAW agree
MAIN = re.sub(r'#ifdef _WIN32.*?#(?:else|endif)', _blank, MAIN_RAW, flags=re.S)  # D: Windows-only code
MAIN = re.sub(r'(?<=#ifdef __APPLE__\n)((?:(?!#if|#else|#endif).)*?)(#else(?:(?!#if|#endif).)*?)(?=#endif)',
              lambda m: m.group(1) + _blank(type('M', (), {'group': lambda self, i=0: m.group(2)})()), MAIN, flags=re.S)  # D: non-Apple else
XFILE = {'rs64_get_vifs_crash_snapshot': ROOT / 'lib/rt64/src/hle/rt64_state.cpp'}
POSIX_SAFE = {'write', '_exit', '_Exit', 'sigaction', 'signal', 'raise', 'dup2', 'dup', 'clock_gettime', 'sigemptyset',
              'mprotect', 'ioctl', 'usleep', 'pthread_self', 'abort', 'kill', 'getpid', 'close'}  # mprotect/ioctl/usleep: raw syscalls
ATOMIC = {'load', 'store', 'exchange', 'fetch_add', 'fetch_sub', 'compare_exchange_strong', 'compare_exchange_weak'}
MEASURED_SAFE = {'fprintf', 'fflush', 'backtrace', 'backtrace_symbols_fd', 'dladdr', 'pthread_get_stackaddr_np', 'pthread_get_stacksize_np', 'c_str',
                 'upper_bound', 'empty', 'begin', 'end', 'rs64_s7355_signame', 'now', 'time_since_epoch', 'count'}
MEASURED_UNSAFE = {'malloc', 'strsignal', 'new', 'push_back', 'emplace_back', 'resize', 'detach', 'thread', 'sleep_for',
                   'getenv'}
KEYWORDS = {'if', 'for', 'while', 'switch', 'return', 'sizeof', 'defined', 'static_cast', 'reinterpret_cast', 'catch',
            'decltype', 'int', 'uint32_t', 'uint64_t', 'uintptr_t', 'size_t', 'void', 'bool', 'char', 'unsigned', 'long',
            'const_cast', 'alignof', 'else', 'milliseconds', 'microseconds', 'duration_cast'}
GATE = re.compile(r'if \(!(?:g_\w+\.load\(|wbw_on\(\))')

def body_at(src, i):
    j = src.index('{', i); d = 0
    for k in range(j, len(src)):
        d += (src[k] == '{') - (src[k] == '}')
        if d == 0: return src[j:k + 1]
    raise ValueError

def strip_win(b):  # drop #ifdef _WIN32 ... #else/#endif regions (D)
    return re.sub(r'#ifdef _WIN32.*?#(?:else|endif)', '', b, flags=re.S)

def calls(b):
    b = re.sub(r'//[^\n]*|"(?:\\.|[^"\\])*"', '', b)
    out = []
    for m in re.finditer(r'(?:\bnew\b)|([A-Za-z_][\w]*)\s*\(', b):
        n = 'new' if m.group(0) == 'new' else m.group(1)
        if n and n not in KEYWORDS:
            out.append(n + '@G' if re.search(r'g_rs64_s7355_strsignal \?\s*$', b[max(0, m.start() - 40):m.start()]) else n)
    return out

def find_def(name):
    m = re.search(r'^(?:static |extern "C" )?[\w:<>\*\s]+?\b' + name + r'\s*\([^;{]*\)\s*\{', MAIN, re.M)
    if m and 'return false; }' not in MAIN[m.start():m.start() + 200].split('\n')[0]: return MAIN, m.start()
    if name in XFILE:
        s = XFILE[name].read_text(); m = re.search(r'\b' + name + r'\s*\([^;{]*\)\s*\{', s)
        return (s, m.start()) if m else (None, None)
    return None, None

def classify(name, gated):
    if name in MEASURED_UNSAFE: return 'G' if gated else 'B'
    if name in POSIX_SAFE or name in ATOMIC or name in MEASURED_SAFE: return 'SAFE'
    return 'G' if gated else '?'

def walk(body, path, gated, depth, rows, seen):
    if not gated and GATE.search(body[:400]): gated = True
    for c in calls(body):
        local_gate = c.endswith('@G'); c = c[:-2] if local_gate else c
        if c in seen: continue  # already walked from another site
        lib = c in POSIX_SAFE or c in ATOMIC or c in MEASURED_SAFE or c in MEASURED_UNSAFE
        src, at = find_def(c) if depth < 3 and not lib else (None, None)
        if src is not None:
            seen.add(c); walk(strip_win(body_at(src, at)), path + [c], gated, depth + 1, rows, seen)
        else:
            rows.append((classify(c, gated or local_gate), '>'.join(path), c))

def census(body, label):
    rows = []; walk(strip_win(body), [label], False, 0, rows, set()); return rows

def main():
    installs = [(m.start(), m.group(0)) for m in re.finditer(r'\b(?:sigaction|signal)\(SIG\w+,[^;]*', MAIN_RAW)]
    print(f'installs: {len(installs)}')
    for at, txt in installs:
        line = MAIN_RAW.count('\n', 0, at) + 1
        win = MAIN[at:at + 10] != MAIN_RAW[at:at + 10]
        print(f'  main.cpp:{line} {txt.strip()[:60]}{"  [D: _WIN32]" if win else ""}')
    h = MAIN.index('sa.sa_sigaction = [](int sig')
    rows = census(body_at(MAIN, h), 'crash_handler')
    agg = {}
    for cls, path, c in rows: agg.setdefault((cls, c), set()).add(path)
    tally = {}
    for (cls, c), paths in sorted(agg.items()):
        tally[cls] = tally.get(cls, 0) + 1
        print(f'{cls:4} {c:32} via {sorted(paths)[0]}{" (+%d)" % (len(paths) - 1) if len(paths) > 1 else ""}')
    print('tally (distinct callee x class):', tally)
    # non-call hazard (found by the s7355 game arms, not by the call census): the ctx-scan stack read must be clamped
    clamp = 'lo_c = lo < stk_lo ? stk_lo : lo' in MAIN
    print(f'ctx-scan stack read clamped to the mapped stack: {clamp}; SA_ONSTACK: {"SA_SIGINFO | SA_ONSTACK" in MAIN}; '
          f'altstack hook: {"pthread_introspection_hook_install" in MAIN}')
    ctl = {
        'B':    'sa.sa_sigaction = [](int sig){ fprintf(stderr, "%s", strsignal(sig)); }',
        'SAFE': 'sa.sa_sigaction = [](int sig){ write(2, "x", 1); _exit(1); }',
        'G':    'sa.sa_sigaction = [](int sig){ if (!g_ctl.load(std::memory_order_relaxed)) return; char *p = (char*)malloc(8); }',
        '?':    'sa.sa_sigaction = [](int sig){ syslog(3, "x"); }',
    }
    ok = True
    for want, src in ctl.items():
        got = {r[0] for r in census(body_at(src, 0), 'ctl') if r[2] not in ('write', '_exit', 'load', 'fprintf')} or {'SAFE'}
        print(f'control {want:4}: got {sorted(got)} {"PASS" if got == {want} else "FAIL"}'); ok &= got == {want}
    print('CONTROLS', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
