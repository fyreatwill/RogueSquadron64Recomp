#!/usr/bin/env python3
"""s7527 class FU: retail side effects skipped by host replacements of libultra.

Enumerates every guest function N64Recomp does not recompile from retail code
(symbol_lists.cpp reimplemented_funcs / ignored_funcs that exist in the game
ELF), and for each one derives offline:
  callers   jal sites in recompiled (non-replaced) game code
  helpers   retail callees that are NOT replaced (recompiled guest helpers whose
            effect the host must reproduce itself: the s7524 osSpTaskLoad ->
            _VirtualToPhysicalTask shape)
  effects   retail stores (sp-relative excluded), cop0/cop1-ctl writes, cache
            ops, KSEG1 hardware-register bases (lui 0xa4xx)
  host      the *_recomp definition (file:line) and whether its body (one level
            of same-file calls) names each helper
Then classifies each row:
  H-dead   no caller in recompiled game code (only reachable from other
           replaced functions or not at all)
  H-gap    a non-replaced retail helper is skipped by the host (needs a
           same-run measurement), unless --credit names a host path for it
  H-canon / H-dead(reader) from the ANNOT table (manual, with the reason)
  REVIEW   game-called, no helper gap, no annotation yet
Positive control: osSpTaskLoad must be H-gap by default and H-canon with
--credit osSpTaskLoad:_VirtualToPhysicalTask=src/main/main.cpp:ROGUESQ_S7524_V2P.
Usage: python3 tools/s7527_host_replace_audit.py [--credit NAME:HELPER=file:pattern ...] [--tsv out]
"""
import re, subprocess, sys, os, collections, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N64R = os.path.join(os.path.dirname(ROOT), 'N64Recomp')
ELF = os.path.join(os.path.dirname(ROOT), 'rogue_squadron64', 'build', 'roguesquadron.elf')
HOST_DIRS = ['src', 'lib/N64ModernRuntime/librecomp', 'lib/N64ModernRuntime/ultramodern']

def lists():
    src = open(os.path.join(N64R, 'src', 'symbol_lists.cpp')).read()
    g = lambda n: set(re.findall(r'"([^"]+)"', re.search(n + r'\s*\{(.*?)\n\};', src, re.S).group(1)))
    return g('reimplemented_funcs'), g('ignored_funcs'), g('renamed_funcs')

def disasm():
    out = subprocess.run(['mips64-elf-objdump', '-d', '--no-show-raw-insn', ELF], capture_output=True, text=True).stdout
    funcs = collections.OrderedDict(); cur = None; sec = None
    for l in out.splitlines():
        m = re.match(r'Disassembly of section (\S+):', l)
        if m: sec = m.group(1); continue
        m = re.match(r'([0-9a-f]+) <([^>]+)>:', l)
        if m:
            cur = (sec, m.group(2)); funcs.setdefault(cur, []); continue
        m = re.match(r'\s*([0-9a-f]+):\s+(\S+)\s*(.*)', l)
        if m and cur: funcs[cur].append((int(m.group(1), 16), m.group(2), m.group(3)))
    return funcs

STORES = ('sw', 'sh', 'sb', 'sd', 'swc1', 'sdc1', 'swl', 'swr')
LOADS = ('lw', 'lh', 'lhu', 'lb', 'lbu', 'ld', 'lwc1', 'ldc1', 'lwl', 'lwr')
NODEST = STORES + ('beq', 'bne', 'beqz', 'bnez', 'blez', 'bgtz', 'bltz', 'bgez', 'j', 'jr', 'jal', 'jalr', 'b', 'nop',
                   'mtc0', 'mtc1', 'ctc1', 'cache', 'sync', 'mult', 'multu', 'div', 'divu', 'dmult', 'dmultu', 'ddiv', 'ddivu',
                   'mthi', 'mtlo', 'break', 'syscall', 'eret', 'tlbwi', 'tlbwr', 'tlbp', 'tlbr', 'c.eq.s', 'c.lt.s', 'c.le.s',
                   'bc1t', 'bc1f', 'bc1tl', 'bc1fl', 'beql', 'bnel', 'beqzl', 'bnezl', 'teq', 'tne')

SAVED = ('s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 'fp', 'sp')

def targets(insns):
    t = set()
    for a, op, args in insns:
        if (op.startswith('b') or op == 'j') and op not in ('break',):
            m = re.search(r'\b([0-9a-f]{8})\b', args)
            if m: t.add(int(m.group(1), 16))
    return t

def mem_refs(insns, kinds):
    """(addr-or-None, base, off, op) for each memory op in kinds, resolving lui-based absolute addresses."""
    lui = {}; out = []; tg = targets(insns); clr = 0
    for a, op, args in insns:
        if a in tg: lui = {}
        if clr:
            clr -= 1
            if not clr: lui = {k: v for k, v in lui.items() if k in SAVED}
        if op in ('jal', 'jalr'): clr = 2
        ar = [x.strip() for x in args.split('#')[0].split(',')]
        if op == 'lui':
            lui[ar[0]] = int(ar[1], 16) << 16; continue
        if op in kinds:
            m = re.match(r'(-?\w+)\((\w+)\)', ar[1] if len(ar) > 1 else '')
            if m:
                b = m.group(2); off = int(m.group(1), 0)
                out.append((((lui[b] + off) & 0xffffffff) if b in lui else None, b, off, op))
        if op in ('j', 'jr', 'b') or op.startswith('b') and op not in ('bnez', 'beqz'):
            pass
        if op in NODEST or op in LOADS and False:
            continue
        d = ar[0] if ar and ar[0] else None
        if op in ('addiu', 'ori') and len(ar) == 3 and ar[1] in lui and d:
            v = int(ar[2], 0); lui[d] = (lui[ar[1]] + v) & 0xffffffff if op == 'addiu' else lui[ar[1]] | v
            continue
        if d in lui: del lui[d]
    return out

def effects(insns):
    st = set(); gw = set(); hw = set(); cop = set(); cache = 0; jal = []
    for ad, b, off, op in mem_refs(insns, STORES):
        if b == 'sp': continue
        if ad is not None:
            gw.add(ad)
            if (ad & 0xfff00000) in (0xa4000000, 0xa4100000, 0xa4300000, 0xa4400000, 0xa4500000, 0xa4600000, 0xa4800000) or (ad >> 24) == 0xa4: hw.add('%08x' % ad)
            else: st.add('G:%08x' % ad)
        else: st.add('P:%s+%d' % (b, off))
    for ad, b, off, op in mem_refs(insns, LOADS):
        if ad is not None and (ad >> 24) == 0xa4: hw.add('r%08x' % ad)
    for a, op, args in insns:
        if op in ('mtc0', 'ctc1', 'tlbwi', 'tlbwr', 'eret'): cop.add(op)
        if op == 'cache': cache += 1
        if op == 'jal':
            m = re.search(r'<([^>+]+)', args)
            if m: jal.append(m.group(1))
    return st, hw, cop, cache, jal, gw

def host_defs():
    defs = {}
    pat = re.compile(r'\b(\w+)_recomp\s*\(\s*(?:uint8_t\s*\*\s*(?:/\*\s*rdram\s*\*/|rdram)?\s*,|RDRAM_ARG)\s*recomp_context\s*\*\s*(?:/\*\s*ctx\s*\*/|ctx)?\s*\)\s*\{')
    for d in HOST_DIRS:
        for dp, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                if not f.endswith(('.cpp', '.c', '.h', '.hpp')): continue
                p = os.path.join(dp, f)
                try: t = open(p, errors='replace').read()
                except OSError: continue
                for m in pat.finditer(t):
                    # body by brace matching
                    i = m.end(); depth = 1
                    while i < len(t) and depth:
                        depth += {'{': 1, '}': -1}.get(t[i], 0); i += 1
                    body = t[m.end():i]
                    line = t.count('\n', 0, m.start()) + 1
                    defs.setdefault(m.group(1), []).append((os.path.relpath(p, ROOT), line, body, t))
    return defs

# Manual classification of game-called rows that have no mechanical helper gap.
# name -> (class, reason). Every reason names the readers or the reproducing host path.
ANNOT = {}; HELPER_OK = {}
exec(open(os.path.join(ROOT, 'tools', 's7527_annot.py')).read()) if os.path.exists(os.path.join(ROOT, 'tools', 's7527_annot.py')) else None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--credit', action='append', default=[]); ap.add_argument('--tsv')
    ap.add_argument('--only'); ap.add_argument('--globals', action='store_true'); ap.add_argument('--objs', action='store_true'); a = ap.parse_args()
    R, I, N = lists(); repl = R | I
    funcs = disasm()
    byname = collections.defaultdict(list)
    for (sec, n), ins in funcs.items(): byname[n].append((sec, ins))
    callers = collections.defaultdict(set)
    for (sec, n), ins in funcs.items():
        if n in repl: continue
        for _, op, args in ins:
            if op == 'jal':
                m = re.search(r'<([^>+]+)', args)
                if m and m.group(1) in repl: callers[m.group(1)].add(n)
    # address-taken replaced functions (function pointers built in recompiled code): an H-dead "no caller" row must have none
    fstart = {}
    for n in repl:
        for sec, il in byname.get(n, []):
            if il: fstart[il[0][0]] = n
    ptrs = collections.defaultdict(set)
    for (sec, fn), ins in funcs.items():
        if fn in repl: continue
        hi = {}
        for ad, op, args in ins:
            ar = [x.strip() for x in args.split('#')[0].split(',')]
            if op == 'lui': hi[ar[0]] = int(ar[1], 16) << 16; continue
            if op in ('addiu', 'ori') and len(ar) == 3 and ar[1] in hi:
                v = (hi[ar[1]] + int(ar[2], 0)) & 0xffffffff if op == 'addiu' else hi[ar[1]] | int(ar[2], 0)
                if v in fstart: ptrs[fstart[v]].add(fn)
    # data words equal to a replaced function address (jump tables / thread entry tables in .data)
    raw = open(ELF, 'rb').read(); words = collections.Counter()
    for l in subprocess.run(['mips64-elf-objdump', '-h', ELF], capture_output=True, text=True).stdout.splitlines():
        q = l.split()
        if len(q) >= 7 and q[1].startswith('.') and not q[1].startswith('.bss'):
            size, off = int(q[2], 16), int(q[5], 16)
            for i in range(off, off + size - 3, 4): words[int.from_bytes(raw[i:i + 4], 'big')] += 1
    for v, n in fstart.items():
        if words[v]: ptrs[n].add('data-word x%d' % words[v])
    defs = host_defs()
    credits = collections.defaultdict(dict)
    for c in a.credit:
        nh, ev = c.split('='); n, h = nh.split(':'); f, p = ev.split(':', 1)
        ok = p in open(os.path.join(ROOT, f)).read()
        credits[n][h] = (ok, ev)
    rows = []; gwrites = {}
    for n in sorted(x for x in repl if x in byname):
        ins = [i for _, il in byname[n] for i in il]
        st, hw, cop, cache, jal, gw = effects(ins)
        gwrites[n] = gw
        helpers = sorted(set(j for j in jal if j not in repl and j != n))
        hd = defs.get(n, [])
        hostloc = ';'.join('%s:%d' % (f, l) for f, l, _, _ in hd) or 'NONE'
        bodies = ' '.join(b for _, _, b, _ in hd)
        # one level of same-file callees
        ext = bodies
        for f, l, b, t in hd:
            for cn in set(re.findall(r'\b([A-Za-z_]\w*)\s*\(', b)):
                m = re.search(r'\b' + re.escape(cn) + r'\s*\([^;{)]*\)\s*\{', t)
                if m: ext += t[m.start():m.start() + 4000]
        gaps = []
        for h in helpers:
            addr = '%08x' % [i for _, il in byname[h] for i in il][0][0] if byname.get(h) else ''
            named = h in ext or (addr and addr in ext.lower())
            cr = credits.get(n, {}).get(h)
            if named: continue
            if cr and cr[0]: continue
            if h in HELPER_OK.get(n, {}): continue
            gaps.append(h)
        gc = sorted(callers.get(n, ()))
        if n in ANNOT and not gaps and (gc or ptrs.get(n)): cls, why = ANNOT[n]
        elif gaps and gc: cls, why = 'H-gap', 'retail helper(s) skipped by host: ' + ','.join(gaps)
        elif not gc and n not in ANNOT and not ptrs.get(n): cls, why = 'H-dead', 'no jal caller and no address taken in recompiled game code'
        elif not gc and ptrs.get(n): cls, why = 'REVIEW', 'address taken: ' + ','.join(sorted(ptrs[n]))
        else: cls, why = 'REVIEW', ''
        rows.append(dict(name=n, kind='R' if n in R else 'I', callers=len(gc), callers_s=','.join(gc[:4]), helpers=','.join(helpers),
                         stores=len(st), stores_s=','.join(sorted(st)[:6]), hw=','.join(sorted(hw)), cop=','.join(sorted(cop)), cache=cache,
                         host=hostloc, cls=cls, why=why))
    # readers: loads of each retail-only global word in recompiled (non-replaced) game code
    symat = {}
    for l in subprocess.run(['mips64-elf-nm', '-n', ELF], capture_output=True, text=True).stdout.splitlines():
        q = l.split()
        if len(q) == 3: symat[int(q[0][-8:], 16)] = q[2]
    allg = {}
    for n, gw in gwrites.items():
        for ad in gw:
            if (ad >> 24) == 0x80: allg.setdefault(ad & ~3, set()).add(n)
    readers = collections.defaultdict(set); replreaders = collections.defaultdict(set)
    for (sec, fn), ins in funcs.items():
        for ad, b, off, op in mem_refs(ins, LOADS):
            if ad is not None and (ad & ~3) in allg:
                (replreaders if fn in repl else readers)[ad & ~3].add(fn)
    def gname(ad):
        best = max((k for k in symat if k <= ad and ad - k < 0x400), default=None)
        return '%08x(%s+0x%x)' % (ad, symat[best], ad - best) if best is not None else '%08x' % ad
    for r in rows:
        gl = sorted(ad for ad in allg if r['name'] in allg[ad])
        rr = ['%s<-%s' % (gname(ad), ','.join(sorted(readers[ad])[:3]) + ('..+%d' % (len(readers[ad]) - 3) if len(readers[ad]) > 3 else '')) for ad in gl if readers[ad]]
        r['greaders'] = ';'.join(rr); r['gcount'] = len(gl); r['gread'] = sum(1 for ad in gl if readers[ad])
    if a.globals:
        for ad in sorted(allg):
            print('G %s writers=%s game_readers=%s repl_readers=%d' % (gname(ad), ','.join(sorted(allg[ad])), ','.join(sorted(readers[ad])) or '-', len(replreaders[ad])))
    # arg objects: resolve a0/a1/a2 at each jal to a replaced function (lui/addiu chain incl. delay slot); then find
    # direct field loads of those objects in recompiled game code (inlined MQ_IS_FULL, task->flags, timer fields ...)
    OBJSZ = {'osCreateMesgQueue': (0, 24), 'osRecvMesg': (0, 24), 'osSendMesg': (0, 24), 'osJamMesg': (0, 24),
             'osSetEventMesg': (1, 24), 'osViSetEvent': (0, 24), 'osCreateThread': (0, 0x1B0), 'osStartThread': (0, 0x1B0),
             'osStopThread': (0, 0x1B0), 'osSetThreadPri': (0, 0x1B0), 'osDestroyThread': (0, 0x1B0), 'osSetTimer': (0, 32),
             'osPiStartDma': (0, 24), 'osEPiRawStartDma': (1, 24), 'osSpTaskLoad': (0, 64), 'osSpTaskStartGo': (0, 64),
             'osSpTaskYielded': (0, 64), 'osContGetReadData': (0, 6 * 4), 'osContGetQuery': (0, 4 * 4), 'osContInit': (0, 24),
             'osPfsInitPak': (1, 0x68), 'osMotorInit': (1, 0x68), 'osCreatePiManager': (2, 24), 'osCreateViManager': (0, 0)}
    objs = collections.defaultdict(set)
    for (sec, fn), ins in funcs.items():
        if fn in repl: continue
        reg = {}; tg = targets(ins); age = {}
        for k, (ad, op, args) in enumerate(ins):
            if ad in tg: reg = {}
            ar = [x.strip() for x in args.split('#')[0].split(',')]
            if op == 'jal':
                m = re.search(r'<([^>+]+)', args); t = m.group(1) if m else None
                if t in OBJSZ and OBJSZ[t][1]:
                    r2 = dict(reg)
                    if k + 1 < len(ins):
                        _, op2, a2 = ins[k + 1]; b2 = [x.strip() for x in a2.split(',')]
                        if op2 == 'addiu' and len(b2) == 3 and b2[1] in r2: r2[b2[0]] = (r2[b2[1]] + int(b2[2], 0)) & 0xffffffff
                        elif op2 == 'lui': r2[b2[0]] = int(b2[1], 16) << 16
                    av = r2.get('a%d' % OBJSZ[t][0])
                    if age.get('a%d' % OBJSZ[t][0], -99) < k - 16 and not (k + 1 < len(ins) and ins[k + 1][2].startswith('a%d,' % OBJSZ[t][0])): av = None
                    if av is not None and (av >> 24) == 0x80: objs[(av, OBJSZ[t][1])].add(t)
                reg = {k: v for k, v in reg.items() if k in SAVED}
                continue
            if op == 'lui': reg[ar[0]] = int(ar[1], 16) << 16; age[ar[0]] = k; continue
            if op in ('addiu', 'ori') and len(ar) == 3 and ar[1] in reg:
                v = int(ar[2], 0); reg[ar[0]] = (reg[ar[1]] + v) & 0xffffffff if op == 'addiu' else reg[ar[1]] | v; age[ar[0]] = k; continue
            if op in NODEST: continue
            if ar and ar[0] in reg: del reg[ar[0]]
    objreads = collections.defaultdict(lambda: collections.defaultdict(set))
    ranges = sorted(objs)
    # address takers: every lui+addiu/ori/mem-offset value landing inside an object (survives indexed loops)
    takers = collections.defaultdict(set); fields = collections.defaultdict(lambda: collections.defaultdict(set))
    for (sec, fn), ins in funcs.items():
        if fn in repl: continue
        hi = {}; tg = targets(ins); clr = 0
        for ad, op, args in ins:
            if ad in tg: hi = {k: v for k, v in hi.items() if k in SAVED}
            if clr:
                clr -= 1
                if not clr: hi = {k: v for k, v in hi.items() if k in SAVED}
            if op in ('jal', 'jalr'): clr = 2
            ar = [x.strip() for x in args.split('#')[0].split(',')]
            vals = []
            if op == 'lui': hi[ar[0]] = int(ar[1], 16) << 16; continue
            if op in ('addiu', 'ori') and len(ar) == 3 and ar[1] in hi:
                v = int(ar[2], 0); vals.append((hi[ar[1]] + v) & 0xffffffff if op == 'addiu' else hi[ar[1]] | v)
            m = re.match(r'(-?\w+)\((\w+)\)', ar[1]) if len(ar) > 1 else None
            if m and op in LOADS + STORES and m.group(2) in hi: vals.append((hi[m.group(2)] + int(m.group(1), 0)) & 0xffffffff)
            for j, v in enumerate(vals):
                kind = ('W' if op in STORES else 'R') if (m and op in LOADS + STORES and j == len(vals) - 1) else 'A'
                for (o, sz) in ranges:
                    if o <= v < o + sz: takers[(o, sz)].add(fn); fields[(o, sz)][(v - o, kind)].add(fn)
            if op not in NODEST and op not in ('addiu', 'ori') and ar and ar[0] in hi: del hi[ar[0]]
            if op in ('addiu', 'ori') and len(ar) == 3:
                if ar[1] in hi and vals: hi[ar[0]] = vals[0]
                elif ar[0] in hi: del hi[ar[0]]
    for (sec, fn), ins in funcs.items():
        if fn in repl: continue
        for ad, b, off, op in mem_refs(ins, LOADS + STORES):
            if ad is None: continue
            for (o, sz) in ranges:
                if o <= ad < o + sz: objreads[(o, sz)][(ad - o, 'W' if op in STORES else 'R')].add(fn)
    for (o, sz) in ranges:
        fl = objreads[(o, sz)]
        if a.objs or fl:
            pass
        for r in rows:
            if r['name'] in objs[(o, sz)]:
                r.setdefault('objs', []).append('%s{%s}' % (gname(o), ' '.join('%s+%d:%s' % (rw, f, ','.join(sorted(fl[(f, rw)])[:2])) for f, rw in sorted(fl))))
    if a.objs:
        for (o, sz) in ranges:
            fl = fields[(o, sz)]
            print('O %s sz=%d via=%s takers=%s fields=%s' % (gname(o), sz, ','.join(sorted(objs[(o, sz)])), ','.join(sorted(takers[(o, sz)])),
                  ' '.join('%s+0x%x<-%s' % (rw, f, ','.join(sorted(fl[(f, rw)])[:3])) for f, rw in sorted(fl) if rw != 'A') or '-'))
    for r in rows: r['objs'] = ';'.join(r.get('objs', []))
    if a.only: rows = [r for r in rows if r['name'] in a.only.split(',')]
    keys = ['name', 'kind', 'cls', 'callers', 'callers_s', 'helpers', 'stores', 'stores_s', 'hw', 'cop', 'cache', 'gcount', 'gread', 'greaders', 'objs', 'host', 'why']
    if a.tsv:
        with open(a.tsv, 'w') as fo:
            fo.write('\t'.join(keys) + '\n')
            for r in rows: fo.write('\t'.join(str(r[k]) for k in keys) + '\n')
    cnt = collections.Counter(r['cls'] for r in rows)
    for r in rows:
        if r['cls'] != 'H-dead' or a.only:
            print('%-26s %s %-7s callers=%-3d helpers=[%s] stores=%d hw=[%s] cop=[%s] cache=%d host=%s | %s' % (
                r['name'], r['kind'], r['cls'], r['callers'], r['helpers'], r['stores'], r['hw'], r['cop'], r['cache'], r['host'][:60], r['why'][:120]))
    print('rows=%d %s' % (len(rows), ' '.join('%s=%d' % kv for kv in sorted(cnt.items()))))

def controls():
    """rc 0 iff every positive control fires: helper-gap default/credit/bogus-credit, G-join, O-join taker, pointer scan."""
    me = [sys.executable, os.path.abspath(__file__)]
    run = lambda *x: subprocess.run(me + list(x), capture_output=True, text=True).stdout
    cred = 'osSpTaskLoad:_VirtualToPhysicalTask=src/main/main.cpp:'
    checks = [
        ('helper gap default', ' H-gap ' in run('--only', 'osSpTaskLoad')),
        ('helper gap credited', ' H-canon ' in run('--only', 'osSpTaskLoad', '--credit', cred + 'ROGUESQ_S7524_V2P')),
        ('helper gap bogus credit', ' H-gap ' in run('--only', 'osSpTaskLoad', '--credit', cred + 'NO_SUCH_PATTERN_S7527')),
    ]
    full = run('--globals', '--objs')
    checks += [
        ('G-join osClockRate game reader', any(l.startswith('G 80039104') and 'timeSnapshotFiller' in l for l in full.splitlines())),
        ('O-join gControllerPads taker', any(l.startswith('O 8010ff30') and 'pollControllerInputs' in l for l in full.splitlines())),
        ('pointer scan rspbootTextStart', any(l.startswith('rspbootTextStart') for l in full.splitlines())),
        ('only H-gap row is osSpTaskLoad', [l.split()[0] for l in full.splitlines() if ' H-gap ' in l] == ['osSpTaskLoad']),
        ('no REVIEW rows', 'REVIEW=' not in full.splitlines()[-1]),
    ]
    for n, ok in checks: print('%-34s %s' % (n, 'PASS' if ok else 'FAIL'))
    return 0 if all(ok for _, ok in checks) else 1

if __name__ == '__main__':
    if '--controls' in sys.argv: sys.exit(controls())
    main()
