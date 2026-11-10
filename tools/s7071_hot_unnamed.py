#!/usr/bin/env python3
"""s7071: rank guest functions by host CPU samples (self and inclusive) over tools/s7065_sample_loop.zsh `sample`
dumps, across all threads, and flag the ones still carrying generated placeholder names (func_/fake_func_/static_N_).
The renaming sweep then names the hot placeholders first.
usage: s7071_hot_unnamed.py [--top N] [--all] <dir> [<dir>...]   (--all also lists named functions)"""
import re, glob, sys, os, collections
PLACE = re.compile(r'^(func_|fake_func_|static_\d+_)(0x)?[0-9A-Fa-f]{8}')
BLOCK = re.compile(r'^(__psynch_|mach_msg|__semwait_signal|nanosleep|kevent|__workq_kernreturn|__ulock_wait|semaphore_)')
LINE = re.compile(r'^([\s+!:|]*)(\d+)\s+(.*?)\s+\(in ([^)]+)\)')
args = sys.argv[1:]; top = 30; showall = False
while args and args[0].startswith('--'):
    if args[0] == '--top': top = int(args[1]); args = args[2:]
    elif args[0] == '--all': showall = True; args = args[1:]
# guest = every RECOMP_FUNC defined in the generated sources (N64Recomp/RecompiledFuncs), so libSystem/RT64 leaves
# with C-identifier names (read, getenv) are not counted as guest.
GEN = os.environ.get('RS64_GEN_DIR', os.path.expanduser('~/Documents/Tools/N64Recomp/RecompiledFuncs'))
DEFS = set()
for f in glob.glob(GEN + '/*.c'):
    for l in open(f, errors='replace'):
        if l.startswith('RECOMP_FUNC void '): DEFS.add(l[17:].split('(')[0].strip())
if not DEFS: sys.exit(f'no RECOMP_FUNC definitions under {GEN} (set RS64_GEN_DIR)')
def guestish(sym): return sym in DEFS
selfc = collections.Counter(); incl = collections.Counter(); nfiles = 0
for d in args:
    for fn in sorted(glob.glob(d + '/smp_*.txt')):
        nfiles += 1; stack = []
        def flush(upto):
            while stack and stack[-1][0] >= upto:
                dep, c, sym, cs, onpath = stack.pop()
                s = c - cs
                if s > 0 and not BLOCK.match(sym): selfc[sym] += s
        for l in open(fn, errors='replace'):
            if re.match(r'^\s+\d+ Thread_\d+', l) or l.startswith(('Total number', 'Sort by top', 'Binary Images')):
                flush(0); continue
            m = LINE.match(l)
            if not m or 'RogueSquadron64Recomp' not in m.group(4): 
                if m:  # foreign frame still counts against parent's child sum
                    dep = len(m.group(1)); flush(dep)
                    if stack: p = stack[-1]; stack[-1] = (p[0], p[1], p[2], p[3] + int(m.group(2)), p[4])
                    stack.append((dep, int(m.group(2)), m.group(3).split(' + ')[0], 0, None))
                continue
            dep = len(m.group(1)); c = int(m.group(2)); sym = m.group(3).split(' + ')[0]
            flush(dep)
            if stack: p = stack[-1]; stack[-1] = (p[0], p[1], p[2], p[3] + c, p[4])
            # inclusive: count once per distinct path node (recursion may double count; fine for ranking)
            if guestish(sym) and not any(x[2] == sym for x in stack): incl[sym] += c
            stack.append((dep, c, sym, 0, None))
        flush(0)
cands = [s for s in set(selfc) | set(incl) if guestish(s) and (showall or PLACE.match(s))]
print(f'files={nfiles} generated defs={len(DEFS)} (placeholder-named defs={sum(1 for d in DEFS if PLACE.match(d))}) placeholder-named guest symbols seen={sum(1 for s in set(selfc)|set(incl) if PLACE.match(s))}')
print('   self   incl  symbol')
for s in sorted(cands, key=lambda s: (-selfc[s], -incl[s]))[:top]:
    print(f'{selfc[s]:7d} {incl[s]:6d}  {s}')
print('-- by inclusive')
for s in sorted(cands, key=lambda s: -incl[s])[:top]:
    print(f'{selfc[s]:7d} {incl[s]:6d}  {s}')
