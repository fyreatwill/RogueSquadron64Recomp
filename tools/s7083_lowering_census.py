#!/usr/bin/env python3
"""s7083: N64Recomp silent-lowering census (the lowerings it does NOT warn about).

1. Every LOOKUP_FUNC(ctx->rN) site: classify the lowered instruction (jalr = indirect call,
   jr $non-ra = tail call), then the jr ones by how the target register was produced:
   PTR   target loaded from memory off a non-constant base (function pointer: real tail call)
   TABLE target loaded from <constant base> + <scaled index> (a jump table N64Recomp missed)
   CONST target is a constant (lui/addiu) -- direct jump through a register
   DATA  the containing function is decoded data (data_gap_/fake_func_)
   ?     anything the backward evaluator could not resolve (printed with context)
2. Every `switch (jr_addend_X >> 2)` jump table: independently recover the table base (lui/addiu
   chain feeding the addu next to the jr), the bound (nearest preceding sltiu), read the words
   from the ROM through the owning section's rom/ram mapping, and check
   (a) case count == bound, (b) word[i] == case i label, (c) every word lies inside the function.
   A self-test re-runs the checker with the base shifted by +4: it must report mismatches.
Usage: s7083_lowering_census.py <regen dir> <rom.z64> [--check]
--check (s7722): exit 1 unless every LOOKUP_FUNC site is a jalr CALL or the ACCEPTED jr row (which must still be seen: a
stale accept list fails), every jump table is OK/OK-SRIDX, the base+4 negative control mismatches EVERY table, the jr
read control fires on every table, the injected-store control only ever reads READ, and no case target reuses the index reg.
"""
import re, sys, glob, struct, collections

_pos = [x for x in sys.argv[1:] if not x.startswith('-')]
D, ROMP = _pos[0], _pos[1]
rom = open(ROMP, 'rb').read()
ov = open(D + '/recomp_overlays.inl').read()
secs = {}
for m in re.finditer(r'static FuncEntry (section_\d+_\w+?)_funcs\[\] = \{(.*?)\};', ov, re.S):
    secs[m.group(1)] = [(e.group(1), int(e.group(2), 16), int(e.group(3), 16))
                        for e in re.finditer(r'\.func = (\w+), \.offset = 0x([0-9A-F]+), \.rom_size = 0x([0-9A-F]+)', m.group(2))]
smap = {}
for m in re.finditer(r'\.rom_addr = 0x([0-9A-F]+), \.ram_addr = 0x([0-9A-F]+), \.size = 0x([0-9A-F]+), \.funcs = (section_\d+_\w+?)_funcs', ov):
    smap[m.group(4)] = tuple(int(m.group(i), 16) for i in (1, 2, 3))
fsec = {}; fbound = {}
for s, fs in secs.items():
    ra = smap[s][1]
    for n, o, z in fs:
        fsec[n] = s; fbound[n] = (ra + o, ra + o + z)

def rom_word(sec, va):
    ro, ra, sz = smap[sec]
    if not (ra <= va < ra + sz):          # overlay code may index a main-segment table
        ro, ra, sz = smap['section_3_text']
        if not (ra <= va < ra + sz): return None
    off = ro + va - ra
    return struct.unpack('>I', rom[off:off + 4])[0]

sidx = {}
for m in re.finditer(r'\.funcs = (section_\d+_\w+?)_funcs.*?\.index = (\d+)', ov): sidx[int(m.group(2))] = m.group(1)
def secof(name, lo):
    if name in fsec: return fsec[name]
    m = re.match(r'static_(\d+)_', name)
    if m: return sidx[int(m.group(1))]
    return [s for s, (ro, ra, sz) in smap.items() if ra <= lo < ra + sz][0]
INS = re.compile(r'^\s*// 0x([0-9A-F]{8}): (\S+)\s*(.*)$')
FN = re.compile(r'^RECOMP_FUNC void (\w+)\(')
funcs = []   # (name, [(addr, op, args)], [lines])
for f in sorted(glob.glob(D + '/funcs_*.c'), key=lambda p: int(re.search(r'(\d+)\.c$', p).group(1))):
    cur = None
    for ln in open(f):
        m = FN.match(ln)
        if m:
            cur = [m.group(1), {}, []]; funcs.append(cur); continue
        if cur is None: continue
        cur[2].append(ln)
        m = INS.match(ln)
        if m: cur[1].setdefault(int(m.group(1), 16), (m.group(2), m.group(3)))

def parse_args(a): return [x.strip() for x in a.split(',')] if a else []
MEMRE = re.compile(r'^(-?0x[0-9A-Fa-f]+|-?\d+)\((\$\w+)\)$')
def imm(s): return int(s, 0)

def lastdef(ins, addrs, reg, before):
    """most recent instruction (linear order) before `before` that writes `reg`."""
    for a in reversed(addrs):
        if a >= before: continue
        op, ar = ins[a]; p = parse_args(ar)
        if not p: continue
        if op in ('sw', 'sh', 'sb', 'sd', 'swc1', 'sdc1', 'beq', 'bne', 'beql', 'bnel', 'blez', 'bgtz', 'bltz', 'bgez',
                  'jr', 'jalr', 'j', 'jal', 'mtc1', 'bc1t', 'bc1f', 'mult', 'multu', 'div', 'divu', 'nop', 'mthi', 'mtlo',
                  'cache', 'sync', 'ctc1', 'dmtc1', 'mtc0', 'bnez', 'beqz', 'b', 'teq', 'break', 'tne'):
            continue
        if p[0] == reg: return a, op, p
    return None

def evaluate(ins, addrs, reg, before, depth=0):
    """('const', v) | ('load', base_desc, idx_desc) | ('sll', reg) | ('opaque', op) | ('undef',)"""
    if reg == '$zero': return ('const', 0)
    if depth > 8: return ('opaque', 'depth')
    d = lastdef(ins, addrs, reg, before)
    if d is None: return ('undef',)
    a, op, p = d
    if op == 'lui': return ('const', (imm(p[1]) << 16) & 0xFFFFFFFF)
    if op in ('addiu', 'ori', 'daddiu'):
        s = evaluate(ins, addrs, p[1], a, depth + 1)
        if s[0] == 'const':
            v = (s[1] + imm(p[2])) if op != 'ori' else (s[1] | (imm(p[2]) & 0xFFFF))
            return ('const', v & 0xFFFFFFFF)
        return ('opaque', op)
    if op in ('addu', 'or', 'daddu', 'move') :
        srcs = p[1:] if op != 'move' else p[1:2]
        ev = [evaluate(ins, addrs, r, a, depth + 1) for r in srcs]
        cs = [e for e in ev if e[0] == 'const']
        if len(ev) == 2 and len(cs) == 2: return ('const', (cs[0][1] + cs[1][1]) & 0xFFFFFFFF)
        if len(ev) == 1 or (len(cs) == 1 and cs[0][1] == 0): return [e for e in ev if not (e[0] == 'const' and e[1] == 0)][0] if any(not (e[0] == 'const' and e[1] == 0) for e in ev) else ('const', 0)
        if len(cs) == 1: return ('sum', cs[0][1], [e for e in ev if e[0] != 'const'][0])
        return ('sum2', ev)
    if op in ('sll',): return ('sll', p[1], imm(p[2]), a)
    if op == 'lw':
        m = MEMRE.match(p[1])
        if not m: return ('opaque', 'lw?')
        b = evaluate(ins, addrs, m.group(2), a, depth + 1)
        return ('load', imm(m.group(1)), b, a)
    return ('opaque', op)

rows = []; cls = collections.Counter(); ptrkind = collections.Counter()
for name, ins, lines in funcs:
    addrs = sorted(ins)
    # map each LOOKUP_FUNC to the last jr/jalr comment before it
    last = None
    for ln in lines:
        m = INS.match(ln)
        if m and m.group(2) in ('jr', 'jalr'): last = (int(m.group(1), 16), m.group(2), m.group(3))
        if 'LOOKUP_FUNC(ctx->r' in ln:
            a, op, ar = last
            reg = parse_args(ar)[-1] if op == 'jr' else parse_args(ar)[-1]
            if op == 'jalr': c = 'CALL'
            elif name.startswith(('data_gap_', 'fake_func_')): c = 'DATA'
            else:
                e = evaluate(ins, addrs, reg, a)
                if e[0] == 'const': c = 'CONST'
                elif e[0] == 'load':
                    b = e[2]
                    if b[0] == 'const': c = 'GLOBALPTR'     # lw from a fixed global: function-pointer variable
                    elif b[0] == 'sum' and b[2][0] == 'sll': c = 'TABLE'
                    elif b[0] in ('load', 'undef', 'opaque', 'sum', 'sum2'): c = 'PTR'
                    else: c = '?'
                    ptrkind[(c, b[0])] += 1
                else: c = '?'
                rows.append((c, name, '0x%08X' % a, op, ar, str(e)[:160]))
            cls[(op, c)] += 1
print('# LOOKUP_FUNC sites by (insn, class):', dict(cls))
for r in rows: print('J\t' + '\t'.join(r))

# ---------- jump tables ----------
SW = re.compile(r'switch \(jr_addend_([0-9A-F]{8}) >> 2\) \{')
CASE = re.compile(r'case (\d+): goto L_([0-9A-F]{8});')
def check_table(shift=0):
    out = []; tot = collections.Counter()
    for name, ins, lines in funcs:
        addrs = sorted(ins)
        i = 0
        while i < len(lines):
            m = SW.search(lines[i])
            if not m: i += 1; continue
            jra = int(m.group(1), 16); cases = {}
            j = i + 1
            while j < len(lines) and 'default:' not in lines[j]:
                c = CASE.search(lines[j])
                if c: cases[int(c.group(1))] = int(c.group(2), 16)
                if lines[j].strip() == '}': break
                j += 1
            i = j
            op, ar = ins[jra]; reg = parse_args(ar)[0]
            e = evaluate(ins, addrs, reg, jra)
            base = None; srd = False
            if e[0] == 'load':
                b = e[2]
                if b[0] == 'sum' and b[2][0] == 'sll': base = (b[1] + e[1]) & 0xFFFFFFFF
                elif b[0] == 'const':
                    # strength-reduced loop index (e.g. initHudStruct: index $s1 = 4*$s3, seeded by a constant
                    # in linear order): take the addu operand whose def chain ends in lui as the table base
                    la = e[3]; lw_base = MEMRE.match(parse_args(ins[la][1])[1]).group(2)
                    ad = lastdef(ins, addrs, lw_base, la)
                    if ad and ad[1] == 'addu':
                        for r in ad[2][1:]:
                            dd = lastdef(ins, addrs, r, ad[0])
                            if dd and dd[1] in ('lui', 'addiu') and (dd[1] == 'lui' or (lastdef(ins, addrs, dd[2][1], dd[0]) or (0, ''))[1] == 'lui'):
                                base = (evaluate(ins, addrs, r, ad[0])[1] + e[1]) & 0xFFFFFFFF; srd = True
            # bound: nearest sltiu before the jr
            bound = None
            for a in reversed(addrs):
                if a < jra and ins[a][0] == 'sltiu':
                    bound = imm(parse_args(ins[a][1])[2]); break
            lo, hi = fbound.get(name, (addrs[0], addrs[-1] + 4))
            if base is None:
                out.append(('NOBASE', name, '0x%08X' % jra, len(cases), bound, str(e)[:120])); tot['NOBASE'] += 1; continue
            base += shift
            words = [rom_word(secof(name, lo), base + 4 * k) for k in range(len(cases))]
            bad = [k for k in range(len(cases)) if words[k] != cases.get(k)]
            outside = [k for k, w in enumerate(words) if w is None or not (lo <= w < hi)]
            v = ('OK-SRIDX' if srd else 'OK') if not bad and not outside and bound == len(cases) else 'MISMATCH'
            if bound != len(cases) and not bad and not outside: v = 'BOUND%s' % bound
            tot[v] += 1
            out.append((v, name, '0x%08X' % jra, 'base=0x%08X' % base, 'n=%d' % len(cases), 'bound=%s' % bound,
                        'bad=%s' % bad[:6], 'outside=%s' % outside[:6]))
    return out, tot
out, tot = check_table()
print('# jump tables:', dict(tot), 'total', sum(tot.values()))
for r in out:
    if not r[0].startswith('OK') or r[0] == 'OK-SRIDX' or '-v' in sys.argv: print('T\t' + '\t'.join(map(str, r)))
_, tneg = check_table(shift=4)
print('# negative control (base+4):', dict(tneg))

# ---------- (d) the dropped table load ----------
# N64Recomp lowers `lw $r, 0($r)` before the jr into ADD32 (address, not the loaded code word), so $r holds
# the wrong value at every case label. Harmless only if each case writes $r before reading it. Linear scan
# from each case label until the first read or write of $r (or a jr/j/return-ish stop after 64 insns).
CALLER_SAVED = {'$v0', '$v1', '$a0', '$a1', '$a2', '$a3', '$t0', '$t1', '$t2', '$t3', '$t4', '$t5', '$t6', '$t7', '$t8', '$t9', '$at'}
ST = ('sw', 'sh', 'sb', 'sd', 'swc1', 'sdc1', 'swl', 'swr')
NOWRITE = ('jr', 'jalr', 'mtc1', 'dmtc1', 'ctc1', 'mult', 'multu', 'div', 'divu', 'teq', 'tne', 'j', 'jal', 'nop', 'cache', 'sync')
BR = re.compile(r'L_([0-9A-F]{8})$')
def srcs_of(op, p):
    r = []
    for x in p: r += [MEMRE.match(x).group(2)] if MEMRE.match(x) else [x]
    return r if (op in ST or op.startswith('b') or op in NOWRITE) else r[1:]
WRITES = []
def first_use(ins, addrs, start, reg, budget=int(__import__("os").environ.get("S7083_BUDGET", "600"))):
    """DFS over fall-through and branch-taken paths (delay slot included). Returns the worst outcome:
    READ@addr if any path reads reg before writing it; else 'write'/'call'/'exit'/'scanlimit'."""
    idx = {a: k for k, a in enumerate(addrs)}
    seen = set(); res = collections.Counter(); stack = [(start, budget)]
    while stack:
        a, b = stack.pop()
        if a not in idx: res['nolabel' if a == start else 'offfunc'] += 1; continue
        if a in seen: continue
        seen.add(a)
        if b <= 0: res['scanlimit'] += 1; continue
        op, ar = ins[a]; p = parse_args(ar)
        if reg in srcs_of(op, p): return 'READ@0x%08X' % a
        nxt = addrs[idx[a] + 1] if idx[a] + 1 < len(addrs) else None
        if op.startswith('b') or op in ('j', 'jal', 'jalr', 'jr'):
            if nxt is not None and reg in srcs_of(*((lambda o, q: (o, parse_args(q)))(*ins[nxt]))):
                return 'READ@0x%08X' % nxt          # delay slot
            if nxt is not None:
                o2, q2 = ins[nxt]; p2 = parse_args(q2)
                if p2 and o2 not in ST and o2 not in NOWRITE and not o2.startswith('b') and p2[0] == reg:
                    if op.endswith('l') and op.startswith('b'):
                        stack.append((addrs[idx[nxt] + 1], b - 2))   # likely: not-taken path skips the slot
                    res['write'] += 1; continue                       # slot write covers taken (and plain) paths
            if op in ('jr', 'j'): res['exit'] += 1; continue
            if op in ('jal', 'jalr'):
                if reg in CALLER_SAVED: res['call'] += 1; continue
                if nxt is not None: stack.append((addrs[idx[nxt] + 1] if idx[nxt] + 1 < len(addrs) else -1, b - 2))
                continue
            m = BR.search(ar)
            if m: stack.append((int(m.group(1), 16), b - 2))
            if op.endswith('l') and op not in ('bal',):   # likely: delay slot only on taken path; fall through skips it
                if nxt is not None and idx[nxt] + 1 < len(addrs): stack.append((addrs[idx[nxt] + 1], b - 2))
            elif op not in ('b',) and nxt is not None and idx[nxt] + 1 < len(addrs):
                stack.append((addrs[idx[nxt] + 1], b - 2))
            continue
        if p and op not in ST and op not in NOWRITE and p[0] == reg: res['write'] += 1; WRITES.append(a); continue
        if nxt is not None: stack.append((nxt, b - 1))
    return max(res, key=lambda k: ('scanlimit', 'offfunc', 'nolabel').index(k) + 10 if k in ('scanlimit', 'offfunc', 'nolabel') else 0) if res else 'empty'
dz = collections.Counter(); dbad = []
for name, ins, lines in funcs:
    addrs = sorted(ins)
    for i, ln in enumerate(lines):
        m = SW.search(ln)
        if not m: continue
        jra = int(m.group(1), 16); reg = parse_args(ins[jra][1])[0]
        tg = set()
        for l2 in lines[i + 1:i + 400]:
            c = CASE.search(l2)
            if c: tg.add(int(c.group(2), 16))
            if 'default:' in l2: break
        # positive control: from the table lw (reads reg as its base) the scan must report READ
        # control: start at the address-forming addu before the lw; on the fall-through path the lw/jr reads reg
        # only through the addu result, so instead start at the sll's successor chain: the jr itself reads reg
        dz['CONTROL-' + first_use(ins, addrs, jra, reg).split('@')[0]] += 1
        for t in sorted(tg):
            del WRITES[:]
            r = first_use(ins, addrs, t, reg); dz[r.split('@')[0]] += 1
            if r == 'write' and WRITES:
                # injected positive control: turn the first write found into a store of reg -> must read
                wa = WRITES[0]; saved = ins[wa]; ins[wa] = ('sw', reg + ', 0x0($sp)')
                dz['INJ-' + first_use(ins, addrs, t, reg).split('@')[0]] += 1
                ins[wa] = saved
            if r.startswith('READ') or r in ('nolabel', 'scanlimit'): dbad.append((name, '0x%08X' % jra, reg, '0x%08X' % t, r))
print('# (d) jump-register use at case targets:', dict(dz))
for r in dbad: print('D\t' + '\t'.join(r))

if '--check' in sys.argv:
    # s7722: the one non-CALL site, explained in docs/N64RECOMP-WARNING-CENSUS.md s7083 (hand-asm return, host-return
    # patch in fixup_game_funcs_vendored.py s2605, tools/check_jr_t9_host_return.py)
    ACCEPTED = {('convertMat3x4ToN64Mtx', '0x80018E58', 'jr')}
    seen = {(r[1], r[2], r[3]) for r in rows}
    opj = [r for r in rows if r[0] != 'CALL' and (r[1], r[2], r[3]) not in ACCEPTED]
    stale = sorted(ACCEPTED - seen)
    ntab = sum(tot.values()); badt = [r for r in out if not r[0].startswith('OK')]
    inj_other = {k: v for k, v in dz.items() if k.startswith('INJ-') and k != 'INJ-READ'}
    checks = [('lookup sites seen', sum(cls.values()) > 0), ('open lookup rows 0', not opj), ('accept list live', not stale),
              ('tables seen', ntab > 0), ('tables all OK', not badt),
              ('negative control base+4 hits every table', tneg.get('MISMATCH', 0) == ntab),
              ('jr read control on every table', dz.get('CONTROL-READ', 0) == ntab),
              ('injected-store control READ only', not inj_other and dz.get('INJ-READ', 0) > 0), ('case-target reuse 0', not dbad)]
    for r in opj: print('OPENROW\t' + '\t'.join(r))
    for a in stale: print('STALE-ACCEPT\t%s' % (a,))
    for n, ok in checks: print('check %-42s %s' % (n, 'ok' if ok else 'FAIL'))
    print('OPEN %d tables %d lookup %d' % (len(opj) + len(badt) + len(dbad) + len(stale), ntab, sum(cls.values())))
    print('VERDICT', 'PASS' if all(ok for _, ok in checks) else 'FAIL')
    sys.exit(0 if all(ok for _, ok in checks) else 1)
