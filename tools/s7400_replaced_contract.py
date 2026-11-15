#!/usr/bin/env python3
"""s7400 class BJ: replaced-libultra output contract census. For every <name>_recomp defined in librecomp/src or src/,
extract its body and classify: R2 (sets ctx->r2 / _return<>), writes (MEM_*/TO_PTR/memcpy targets), then join every guest
jal to <name> (callers not themselves replaced) with the s7392 v0_fate classifier (TESTED/USED/IGNORED/RETURNED).
FLAG = a live caller consumes v0 of a replacement that never sets r2 (H-ret, stale v0).
Usage: tools/s7400_replaced_contract.py [disasm=/tmp/s7392.dis] [--rows]"""
import re, sys, os, glob, collections, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
c7392 = importlib.import_module('s7392_mesg_census')
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
# libultra prototypes returning void (os.h / ultra64): consuming v0 after these is a tail/void artefact, not H-ret
VOID = set('''osStartThread osStopThread osDestroyThread osYieldThread osSetThreadPri osCreateThread osCreateMesgQueue
osSetEventMesg osViSetEvent osViSetMode osViSetSpecialFeatures osViSwapBuffer osViBlack osViRepeatLine osViSetXScale
osViSetYScale osWritebackDCache osWritebackDCacheAll osInvalDCache osInvalICache osSpTaskLoad osSpTaskStartGo osSpTaskYield
osCreatePiManager osCreateViManager osInitialize osSetTime osSetCount osDpSetStatus osDpGetCounters osUnmapTLBAll
osContGetReadData osContGetQuery osEPiReadIo bzero __osRestoreInt __osSetFpcCsr osMotorInit __osInitialize_common
osExQueueDisplaylistEvent'''.split())
SRC = glob.glob(os.path.join(ROOT, 'lib/N64ModernRuntime/librecomp/src/*.cpp')) + \
    glob.glob(os.path.join(ROOT, 'src/**/*.cpp'), recursive=True)


def bodies():
    out = {}
    for f in SRC:
        t = open(f, errors='replace').read()
        for m in re.finditer(r'void\s+(\w+)_recomp\s*\([^)]*\)\s*\{', t):
            d, k = 1, m.end()
            while d and k < len(t):
                d += {'{': 1, '}': -1}.get(t[k], 0); k += 1
            out[m.group(1)] = (os.path.relpath(f, ROOT), t[m.end():k])
    return out


def r2_kind(name, body, allb, seen=()):
    if re.search(r'ctx->r2\s*=|_return\s*<', body):
        return 'R2'
    for callee in re.findall(r'(\w+)_recomp\s*\(\s*rdram', body):   # delegation to another replacement
        if callee in allb and callee not in seen and callee != name:
            if r2_kind(callee, allb[callee][1], allb, seen + (name,)) == 'R2':
                return 'R2(via %s)' % callee
    return 'NO-R2'


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dis = args[0] if args else c7392.DIS
    allb = bodies()
    insns = c7392.parse(dis)
    rows = collections.defaultdict(list)
    for i, (a, mn, ops, fn) in enumerate(insns):
        if mn != 'jal' or not ops:
            continue
        m = re.search(r'<([^>+]+)>', ops[0])
        if not m or m.group(1) not in allb:
            continue
        if fn in allb:
            continue    # caller body replaced: never runs
        rows[m.group(1)].append((a, fn, c7392.v0_fate(insns, i)))
    flags = 0
    for name in sorted(allb):
        f, body = allb[name]
        k = r2_kind(name, body, allb)
        r = rows.get(name, [])
        fates = collections.Counter(x[2].split(':')[0] for x in r)
        consumed = fates['TESTED'] + fates['USED'] + fates['RETURNED']
        flag = 'FLAG' if (k == 'NO-R2' and consumed and name not in VOID) else ('void' if k == 'NO-R2' and consumed else '')
        flags += flag == 'FLAG'
        if r or '--all' in sys.argv:
            print('%-28s %-22s %-16s live_sites=%-3d %s %s' % (name, f.split('/')[-1], k, len(r), dict(fates), flag))
            if '--rows' in sys.argv and (flag or consumed):
                for a, fn, fate in r:
                    if not fate.startswith('IGNORED'):
                        print('    %08X %-36s %s' % (a, fn, fate))
    print('--- replaced=%d called_live=%d FLAG=%d' % (len(allb), len(rows), flags))
    return 1 if flags else 0


if __name__ == '__main__':
    sys.exit(main())
