#!/usr/bin/env python3
"""s7067: per-thread host on-CPU SELF samples by leaf symbol over tools/s7065_sample_loop.zsh `sample` dumps,
bucketed guest / ucode / ours / patches / runtime / rt64 / libsys. Blocking leaves are excluded (off-CPU).
usage: s7067_selftime.py [--top N] [--thread SUBSTR] <dir> [<dir>...]
Symbol sets come from nm over build/CMakeFiles object groups (guest = RecompiledFuncs, ours = src/main+src/rsp,
ucode = factor5_ucode, patches = PatchesLib). Image symbols in none of these: RT64::/rt64 -> rt64,
ultramodern::/recomp:: -> runtime, else 'image-other' (printed so nothing hides)."""
import re, glob, sys, os, subprocess, collections
BLOCK = re.compile(r'^(__psynch_|mach_msg|__semwait_signal|nanosleep|kevent|__workq_kernreturn|__ulock_wait|semaphore_|'
                   r'__select|read$|write$|__read_nocancel|__write_nocancel|__pthread_kill|swtch_pri|thread_switch|__sigwait)')
def nm_set(dirs):
    s = set()
    for d in dirs:
        objs = glob.glob(d + '/**/*.o', recursive=True)
        if not objs: continue
        out = subprocess.run(['nm', '-C', '--defined-only'] + objs, capture_output=True, text=True).stdout
        for l in out.splitlines():
            p = l.split(' ', 2)
            if len(p) == 3 and p[1] in 'tT':
                n = p[2].lstrip('_') if not p[2].startswith('__Z') else p[2]
                s.add(p[2].split('(')[0].strip()); s.add(n.split('(')[0].strip())
    return s
B = 'build/CMakeFiles'
SETS = [('guest', nm_set([B + '/RecompiledFuncs.dir'])), ('ucode', nm_set([B + '/RogueSquadron64Recomp.dir/factor5_ucode'])),
        ('ours', nm_set([B + '/RogueSquadron64Recomp.dir/src'])), ('patches', nm_set([B + '/PatchesLib.dir']))]
DIAG = re.compile(r'^(rs64|RT64::rs64Log|.*::rs64Log|s\d{4}_|.*_s\d{4})|printf|fwrite|fputs|fflush')
def bucket(sym, binary):
    base = sym.split('(')[0].strip()
    if DIAG.search(base) and 'rs64LoadBlock' not in base: return 'diag'
    if 'RogueSquadron64Recomp' not in binary: return 'libsys'
    for name, st in SETS:
        if base in st or base.lstrip('_') in st: return name
    if 'RT64' in base or 'rt64' in base or 'plume' in base.lower() or 'hlslpp' in base: return 'rt64'
    if base.startswith(('ultramodern', 'recomp', 'Multilibultra', 'ultra')) or 'recomp' in base.lower(): return 'runtime'
    return 'image-other'
args = sys.argv[1:]; top = 25; thsel = None
while args and args[0].startswith('--'):
    if args[0] == '--top': top = int(args[1]); args = args[2:]
    elif args[0] == '--thread': thsel = args[1]; args = args[2:]
LINE = re.compile(r'^([\s+!:|]*)(\d+)\s+(.*?)\s+\(in ([^)]+)\)')
for d in args:
    selfs = collections.defaultdict(collections.Counter); bk = collections.defaultdict(collections.Counter)
    blocked = collections.Counter(); total = collections.Counter(); files = 0
    for fn in sorted(glob.glob(d + '/smp_*.txt')):
        files += 1; th = None; stack = []  # (depth, count, sym, bin, childsum)
        def flush(upto):
            while stack and stack[-1][0] >= upto:
                dep, c, sym, bn, cs = stack.pop()
                s = c - cs
                if s > 0 and th:
                    leaf = sym.split(' + ')[0]
                    if BLOCK.match(leaf): blocked[th] += s
                    else: selfs[th][(leaf, bn)] += s; bk[th][bucket(leaf, bn)] += s
        for l in open(fn, errors='replace'):
            m = re.match(r'^\s+(\d+) Thread_\d+\s*(.*)', l)
            if m:
                flush(0); nm = m.group(2)
                th = 'MAIN' if '[Game] MAIN' in nm else re.sub(r'\s+\(serial\)|DispatchQueue_\d+: |^: ', '', nm)[:34] or 'unnamed'
                total[th] += int(m.group(1)); continue
            if l.startswith(('Total number', 'Sort by top', 'Binary Images')): flush(0); th = None; continue
            m = LINE.match(l)
            if not m or th is None: continue
            dep = len(m.group(1)); c = int(m.group(2)); sym = m.group(3); bn = m.group(4)
            flush(dep)
            if stack: p = stack[-1]; stack[-1] = (p[0], p[1], p[2], p[3], p[4] + c)
            stack.append((dep, c, sym, bn, 0))
        flush(0)
    print(f'== {d}: files={files}')
    ths = sorted(bk, key=lambda t: -sum(bk[t].values()))
    for th in ths:
        if thsel and thsel not in th: continue
        on = sum(bk[th].values())
        if on < 200 and not thsel: continue
        print(f'-- {th}: on-CPU self {on} of {total[th]} samples (blocked {blocked[th]})  ' +
              '  '.join(f'{b}={n} ({100*n/on:.1f}%)' for b, n in bk[th].most_common()))
        if thsel or th in ('MAIN',) or th.startswith(('Gfx', 'SP Task')):
            for (sym, bn), n in selfs[th].most_common(top):
                print(f'     {n:6d} {100*n/on:5.1f}% {bucket(sym, bn):11s} {sym[:90]}')
