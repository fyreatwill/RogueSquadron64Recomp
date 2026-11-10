#!/usr/bin/env python3
"""s7070: for host `sample` dumps (tools/s7065_sample_loop.zsh), attribute the on-CPU SELF samples of target leaf
symbols to their caller chains (parent frames with call offsets), per thread.
usage: s7070_parents.py [--thread SUBSTR] [--depth N] [--target REGEX]... <dir> [<dir>...]
Default targets: XXH3_hashLong, _platform_memmove. Default thread 'Gfx'. Prints, per target, the top immediate
callers (sym+offset) and the top depth-N chains; also total target self vs thread on-CPU self."""
import re, glob, sys, collections
LINE = re.compile(r'^([\s+!:|]*)(\d+)\s+(.*?)\s+\(in ([^)]+)\)\s*\+?\s*([\d,\.]*)')
BLOCK = re.compile(r'^(__psynch_|mach_msg|__semwait_signal|nanosleep|kevent|__workq_kernreturn|__ulock_wait|semaphore_|'
                   r'__select|read$|write$|__read_nocancel|__write_nocancel|__pthread_kill|swtch_pri|thread_switch|__sigwait)')
args = sys.argv[1:]; thsel = 'Gfx'; depth = 4; targets = []
while args and args[0].startswith('--'):
    if args[0] == '--thread': thsel = args[1]
    elif args[0] == '--depth': depth = int(args[1])
    elif args[0] == '--target': targets.append(args[1])
    args = args[2:]
targets = [re.compile(t) for t in (targets or [r'^XXH3_hashLong', r'^_platform_memmove'])]
def short(sym): 
    s = sym.split('(')[0].strip(); return s[-70:]
for d in args:
    imm = [collections.Counter() for _ in targets]; chain = [collections.Counter() for _ in targets]
    tot = [0] * len(targets); onself = 0; files = 0
    for fn in sorted(glob.glob(d + '/smp_*.txt')):
        files += 1; inth = False; stack = []  # (depth, count, label, childsum)
        def flush(upto):
            global onself
            while stack and stack[-1][0] >= upto:
                dep, c, lab, cs = stack.pop(); s = c - cs
                if s <= 0 or not inth: continue
                leaf = lab[0]
                if BLOCK.match(leaf): continue
                onself += s
                for i, t in enumerate(targets):
                    if t.search(leaf):
                        tot[i] += s
                        anc = [x[2] for x in stack][::-1]
                        # skip wrapper frames of the same family (XXH64/XXH3_64bits etc.)
                        anc2 = [a for a in anc if not re.match(r'^(XXH|_platform_mem|memcpy|memmove)', a[0])]
                        if anc2: imm[i][f'{short(anc2[0][0])} +{anc2[0][1]}'] += s
                        chain[i][' <- '.join(short(a[0]) + '+' + a[1] for a in anc2[:depth])] += s
                        break
        for l in open(fn, errors='replace'):
            m = re.match(r'^\s+(\d+) Thread_\d+\s*(.*)', l)
            if m: flush(0); stack.clear(); inth = thsel in m.group(2); continue
            if l.startswith(('Total number', 'Sort by top', 'Binary Images')): flush(0); inth = False; continue
            m = LINE.match(l)
            if not m or not inth: continue
            dep = len(m.group(1)); c = int(m.group(2)); sym = m.group(3)
            flush(dep)
            if stack: p = stack[-1]; stack[-1] = (p[0], p[1], p[2], p[3] + c)
            off = re.search(r'\+ ([\d,\.]+)\s+\[', l); off = off.group(1) if off else '?'
            stack.append((dep, c, (sym.split(' + ')[0].strip(), off), 0))
        flush(0)
    print(f'== {d}: files={files} thread~{thsel!r} on-CPU self={onself}')
    for i, t in enumerate(targets):
        print(f'-- target {t.pattern}: self {tot[i]} ({100*tot[i]/max(onself,1):.1f}%)')
        for k, n in imm[i].most_common(10): print(f'   {n:6d} {100*n/max(tot[i],1):5.1f}%  {k}')
        print('   chains:')
        for k, n in chain[i].most_common(8): print(f'   {n:6d} {100*n/max(tot[i],1):5.1f}%  {k}')
