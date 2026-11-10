#!/usr/bin/env python3
"""s7089 host-shim RESULT census: which shim results does retail code actually consume?

For every called `X_recomp` shim (same enumeration as tools/s7088_shim_abi_census.py), find each
`jal X` in the retail ELF (../rogue_squadron64/build/roguesquadron.elf, all code sections incl.
overlays) and run a forward liveness walk over the MIPS code after the call:

  * a read of $v0 / $v1 before a write on some path  -> CONSUMED (records the reading insn)
  * a `jr ra` with the register still unwritten       -> RETURNED: the containing function hands
    the value to ITS callers; the walk recurses into those call sites (depth <= 4)
  * a jal/jalr/bal (after its delay slot)             -> killed (callee clobbers v0/v1)
  * branch delay slots are honoured; branch-likely slots execute on the taken path only.

Per shim the verdict is {result-unread, consumed}. Consumed shims are then compared with the ROM
routine by hand (table in docs/N64RECOMP-WARNING-CENSUS.md, s7089 section).

Controls (run every time):
  positive: the call at 0x80003874 (osRecvMesg, then `beq v0,v1`) must come out CONSUMED v0.
  negative: a synthetic sequence `jal X; nop; addiu v0,zero,1; jr ra` must come out unread.
  count:    total ELF jal sites to called shims, compared with the 286 generated call sites.

Usage: python3 tools/s7089_shim_result_census.py [-v]
"""
import collections, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
ELF = os.path.join(ROOT, '..', 'rogue_squadron64', 'build', 'roguesquadron.elf')
OBJDUMP = 'mips64-elf-objdump'

GPR = {'zero', 'at', 'v0', 'v1', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7',
       's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 't8', 't9', 'k0', 'k1', 'gp', 'sp', 's8', 'fp', 'ra'}
NODEST = re.compile(r'^(s[bhwd]|s[wd][lr]|sc|scd|s[wd]c1|b|beq|bne|beql|bnel|beqz|bnez|beqzl|bnezl|blez|bgtz|bltz|bgez|'
                    r'blezl|bgtzl|bltzl|bgezl|bltzal|bgezal|bal|jr|j|jal|jalr|d?multu?|d?divu?|mt(hi|lo|c0|c1|c2)|'
                    r'dmtc1|ctc1|t(eq|ne|ge|lt|geu|ltu)i?|sync|cache|break|syscall|nop|eret|bc1[tf]l?)$')
BRANCH = re.compile(r'^(b|beq|bne|beql|bnel|beqz|bnez|beqzl|bnezl|blez|bgtz|bltz|bgez|blezl|bgtzl|bltzl|bgezl|'
                    r'bc1[tf]l?)$')
CALL = re.compile(r'^(jal|jalr|bal|bltzal|bgezal)$')


def regs(ops):
    return [r for r in re.findall(r'\b([a-z][a-z0-9]{1,3})\b', ops) if r in GPR]


def disasm():
    out = subprocess.run([OBJDUMP, '-d', '-z', ELF], capture_output=True, text=True).stdout
    sections = {}          # name -> {addr: (mn, ops)}
    funcs = {}             # (sec, addr) -> name
    sec = None
    for line in out.splitlines():
        m = re.match(r'^Disassembly of section (\S+):', line)
        if m:
            sec = m.group(1)
            sections[sec] = {}
            continue
        m = re.match(r'^([0-9a-f]{8}) <([^>]+)>:', line)
        if m and sec:
            funcs[(sec, int(m.group(1), 16))] = m.group(2)
            continue
        m = re.match(r'^\s*([0-9a-f]{8}):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)$', line)
        if m and sec:
            sections[sec][int(m.group(1), 16)] = (m.group(2), m.group(3).split('#')[0].strip())
    return sections, funcs


def target(ops):
    m = re.search(r'\b([0-9a-f]{8})\b(?: <[^>]*>)?\s*$', ops)
    return int(m.group(1), 16) if m else None


def walk(code, start, want):
    """Forward walk from `start` (first insn after the call's delay slot). Returns
    (reads, returned): reads = [(addr, reg, insn)], returned = set of regs live at a jr ra."""
    reads, returned = [], set()
    seen = set()
    work = [(start, frozenset(want))]
    while work:
        pc, live = work.pop()
        while live:
            if (pc, live) in seen or pc not in code:
                break
            seen.add((pc, live))
            mn, ops = code[pc]
            rs = regs(ops)

            def step(a, live):
                m2, o2 = code.get(a, ('nop', ''))
                r2 = regs(o2)
                dst = r2[0] if (r2 and not NODEST.match(m2)) else None
                srcs = r2[1:] if dst else r2
                for r in srcs:
                    if r in live:
                        reads.append((a, r, f'{m2} {o2}'))
                live = live - {r for r in srcs if r in live}  # first read is enough per path
                if dst in live:
                    live = live - {dst}
                return live

            if BRANCH.match(mn) or mn in ('j', 'jr') or CALL.match(mn):
                # the branch/jump itself reads its source regs
                srcs = [r for r in rs if r != 'ra'] if mn != 'jr' else ([] if rs == ['ra'] else rs)
                for r in srcs:
                    if r in live:
                        reads.append((pc, r, f'{mn} {ops}'))
                live = live - set(srcs)
                likely = mn.endswith('l') and BRANCH.match(mn) and mn != 'bal'
                slot_live = step(pc + 4, live)
                if CALL.match(mn):
                    break                     # callee clobbers v0/v1 (after the slot)
                if mn == 'jr':
                    if rs == ['ra']:
                        returned |= set(slot_live)
                    break                     # other jr = jump table / tail: stop (reported below)
                t = target(ops)
                if mn in ('j', 'b'):
                    if t is not None:
                        work.append((t, frozenset(slot_live)))
                    break
                if t is not None:
                    work.append((t, frozenset(slot_live)))
                live = live if likely else slot_live   # not-taken path
                pc += 8
                continue
            live = step(pc, live)
            pc += 4
    return reads, returned


def main():
    os.chdir(ROOT)
    import s7088_shim_abi_census as c88
    import glob
    shims, calls = set(), collections.Counter()
    for g in c88.SRC_GLOBS:
        for p in glob.glob(g, recursive=True):
            for name, _l, _b in c88.bodies(c88.read(p)):
                shims.add(name)
    for g in c88.GEN_GLOBS:
        for p in glob.glob(g):
            for m in re.finditer(r'\b([A-Za-z0-9_]+)_recomp\(rdram, ctx\)', c88.read(p)):
                calls[m.group(1)] += 1
    called = sorted(n for n in shims if calls[n])

    sections, funcs = disasm()
    # function bounds per section
    fstarts = collections.defaultdict(list)
    for (sec, a), n in funcs.items():
        fstarts[sec].append((a, n))
    for s in fstarts:
        fstarts[s].sort()

    def owner(sec, a):
        best = None
        for fa, n in fstarts[sec]:
            if fa <= a:
                best = (fa, n)
            else:
                break
        return best

    # call sites the recompiled tree actually contains (generated `// 0xADDR:` instruction comments);
    # ELF jal sites inside libultra routines that are themselves replaced by shims are not live.
    gen = set()
    for g in c88.GEN_GLOBS:
        for p in glob.glob(g):
            for m in re.finditer(r'// 0x([0-9A-F]{8}): ', c88.read(p)):
                gen.add(int(m.group(1), 16))
    callsites = collections.defaultdict(list)   # callee name -> [(sec, addr)]  (generated sites only)
    dropped = collections.Counter()
    for sec, code in sections.items():
        for a, (mn, ops) in code.items():
            if mn == 'jal':
                m = re.search(r'<([^>+]+)>', ops)
                if m:
                    if a in gen or a + 4 in gen:     # jal comment, or its delay slot (some patches strip the jal line)
                        callsites[m.group(1)].append((sec, a))
                    else:
                        dropped[m.group(1)] += 1

    memo = {}

    def consumers(sec, site, want, depth, path):
        reads, ret = walk(sections[sec], site + 8, want)
        res = [(f'{sec}:{a:08X}', r, i, path) for a, r, i in reads]
        if ret:
            o = owner(sec, site)
            fn = o[1] if o else '?'
            if depth >= 4 or fn in path:
                res.append((f'{sec}:{site:08X}', ','.join(sorted(ret)), f'RETURNED from {fn} (depth cap)', path))
            else:
                for s2, a2 in callsites.get(fn, []):
                    res += consumers(s2, a2, ret, depth + 1, path + (fn,))
        return res

    # controls
    ok = True
    r, _ = walk(sections['.text'], 0x80003874, {'v0', 'v1'})
    pos = any(rr == 'v0' and a == 0x80003878 for a, rr, _i in r)
    print(f'control positive  0x80003874 osRecvMesg -> beq v0,v1: {"CONSUMED" if pos else "unread"}  -> '
          f'{"PASS" if pos else "FAIL"}')
    ok &= pos
    syn = {0x100: ('addiu', 'v0,zero,1'), 0x104: ('jr', 'ra'), 0x108: ('nop', '')}
    r, ret = walk(syn, 0x100, {'v0'})
    neg = not r and not ret
    print(f'control negative  synthetic overwrite: reads={len(r)} returned={sorted(ret)}  -> '
          f'{"PASS" if neg else "FAIL"}')
    ok &= neg
    syn2 = {0x100: ('jr', 'ra'), 0x104: ('nop', '')}
    _r, ret2 = walk(syn2, 0x100, {'v0'})
    print(f'control return    synthetic jr ra: returned={sorted(ret2)}  -> {"PASS" if ret2 == {"v0"} else "FAIL"}')
    ok &= ret2 == {'v0'}

    nelf = sum(len(callsites.get(n, [])) for n in called)
    ngen = sum(calls[n] for n in called)
    nd = sum(dropped[n] for n in called)
    # duplicate-call detector: a retail jal address whose comment appears twice inside ONE generated function
    # (s7089: the s3531 fixup pasted reapplyAudioConfig's initFactor5Mutex/osAiSetFrequency blocks twice).
    dups = []
    for g in c88.GEN_GLOBS:
        for p in glob.glob(g):
            fn, seen = None, collections.Counter()
            for line in c88.read(p).split('\n') + ['RECOMP_FUNC void __end__(']:
                m = re.match(r'RECOMP_FUNC void (\w+)\(', line)
                if m:
                    dups += [(fn, a) for a, k in seen.items() if k > 1]
                    fn, seen = m.group(1), collections.Counter()
                    continue
                m = re.match(r'\s*// 0x([0-9A-F]{8}): jalr?\s', line)
                if m:
                    seen[m.group(1)] += 1
    print(f'count             ELF jal sites in generated code {nelf} (+{nd} inside replaced libultra code, dropped)'
          f' vs generated shim call sites {ngen}  -> {"PASS" if nelf == ngen else "MISMATCH"}')
    print(f'duplicate calls   {len(dups)} {dups}  -> {"PASS" if not dups else "DEFECT"}')
    ok &= nelf == ngen and not dups

    verdict = {}
    for n in called:
        sites = callsites.get(n, [])
        allc = []
        for sec, a in sites:
            for loc, r, i, path in consumers(sec, a, {'v0', 'v1'}, 0, ()):
                allc.append((f'{sec}:{a:08X}', loc, r, i, path))
        regs_used = sorted({c[2] for c in allc})
        v = 'consumed ' + '+'.join(regs_used) if allc else 'result-unread'
        verdict[n] = v
        print(f'{n:26s} elf={len(sites):3d} gen={calls[n]:3d}  {v}  (consuming sites '
              f'{len({c[0] for c in allc})}/{len(sites)})')
        if '-v' in sys.argv:
            for site, loc, r, i, path in allc[:12]:
                via = (' via ' + '>'.join(path)) if path else ''
                print(f'      {site} -> {loc} {r}: {i}{via}')
    print('\nsummary', collections.Counter(v.split()[0] for v in verdict.values()))
    print('controls', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
