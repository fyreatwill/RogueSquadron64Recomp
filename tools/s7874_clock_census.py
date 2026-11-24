#!/usr/bin/env python3
"""s7874: census of every raw-clock source the recompiled game code can read.

Enumerates, over ../N64Recomp/RecompiledFuncs/funcs_*.c:
  1. call sites of osGetTime (jal 0x8002BF00) and osGetCount (osGetCount_recomp), with the enclosing function;
  2. inline cop0 reads other than Status (mfc0 Count/Compare comments; N64Recomp traps unhandled cop0 regs);
  3. loads/stores of the derived clock words (stamp 0x80128ED8, prev 0x8011A900, dt 0x8011A904, since-last-frame
     0x8011A914, frame timestamp 0x80128F10, clock 0x80039100/04), resolved by the lui base in the preceding lines
     so same-offset words in other segments (e.g. 0x800A8ED8) are not counted.
Control: the known timeSnapshotFiller osGetTime call (0x8000BC1C) and the viRetraceHandlerThread stamp store
(0x8001993C) must both be found, else rc 2.  usage: python3 tools/s7874_clock_census.py [RecompiledFuncs dir]
"""
import re, sys, glob, os, collections

D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '../../N64Recomp/RecompiledFuncs')
HDR = re.compile(r'^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC void (\w+)\(')
INS = re.compile(r'^\s*// (0x8[0-9A-F]{7}): (\w+(?:\.\w+)?)\s+(.*)$')
WORDS = {0x80128ED8: 'vi_stamp', 0x8011A900: 'prev_stamp', 0x8011A904: 'dt', 0x8011A914: 'since_last_frame',
         0x80128F10: 'frame_ts', 0x80039100: 'clock_hi', 0x80039104: 'clock_word'}
MEM = re.compile(r'^(l[bhwd]u?|lwc1|ldc1|s[bhwd]|swc1|sdc1|addiu)$')

calls, cop0, refs = [], [], []
for f in sorted(glob.glob(os.path.join(D, 'funcs_*.c'))):
    cur = None; lui = {}; seen = set()
    for l in open(f, errors='ignore'):
        m = HDR.match(l)
        if m: cur = m.group(1); lui = {}; continue
        if 'osGetCount_recomp(rdram' in l: calls.append(('osGetCount', cur, f))
        m = INS.match(l)
        if not m or m.group(1) in seen and m.group(2) != 'lui': continue
        pc, op, args = m.groups(); seen.add(pc)
        if op == 'jal' and args.strip() == '0x8002BF00': calls.append(('osGetTime@' + pc, cur, os.path.basename(f)))
        if op == 'mfc0' and 'Status' not in args and '$12' not in args: cop0.append((pc, cur, args.strip()))
        if op == 'lui':
            r, v = [a.strip() for a in args.split(',')]; lui[r] = int(v, 16) << 16; continue
        if MEM.match(op):
            mm = re.search(r'(-?0x[0-9A-F]+)\((\$\w+)\)', args) if op != 'addiu' else None
            if op == 'addiu':
                p = [a.strip() for a in args.split(',')]
                if len(p) == 3 and p[1] in lui and re.match(r'-?0x', p[2]):
                    a = (lui[p[1]] + int(p[2], 16)) & 0xFFFFFFFF
                    if a in WORDS: refs.append((pc, cur, 'addr', WORDS[a]))
                continue
            if mm and mm.group(2) in lui:
                a = (lui[mm.group(2)] + int(mm.group(1), 16)) & 0xFFFFFFFF
                if a in WORDS: refs.append((pc, cur, op, WORDS[a]))

print(f'osGetTime/osGetCount call sites: {len(calls)}')
for c in calls: print('  ', *c)
print(f'inline non-Status cop0 reads: {len(cop0)}')
for c in cop0: print('  ', *c)
print(f'clock-word refs: {len(refs)}')
by = collections.defaultdict(list)
for pc, fn, op, w in refs: by[w].append(f'{fn}:{pc}:{op}')
for w, v in sorted(by.items()): print(f'  {w}: ' + ' '.join(v))
ok = any(c[0] == 'osGetTime@0x8000BC1C' for c in calls) and any(r[0] == '0x8001993C' for r in refs)
print('CONTROL', 'PASS' if ok else 'FAIL', '(timeSnapshotFiller osGetTime 0x8000BC1C + vi stamp store 0x8001993C)')
sys.exit(0 if ok else 2)
