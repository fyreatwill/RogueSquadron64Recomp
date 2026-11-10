#!/usr/bin/env python3
"""s7086 N64Recomp memory-access + conditional-branch lowering census over the pristine front-end output
(scratch/s7082/regen, regenerate with tools/regen_front.sh), plus a link-register check against the LIVE
fixed-up output (../N64Recomp/RecompiledFuncs).

Checked per site, with OPERANDS (register numbers and immediate VALUES), not just the statement shape:
  * loads lb/lbu/lh/lhu/lw/lwu/ld -> ctx->rT = MEM_B/BU/H/HU/W/WU/LD(base, off); the macro picks the
    swizzle (B ^3, H ^2, W none, LD = two words, high at +0) - verified on the host by tools/s7086_mem_test.
    stores sb/sh/sw/sd -> MEM_x(off, base) = rT / SD(rT, off, base). The immediate printed in C must equal
    the disassembly's sign-extended 16-bit offset. Constant offsets misaligned for the access width are listed.
  * lui -> S32(0XIMM << 16); addiu -> ADD32(rs, simm16); ori/andi/xori -> zero-extended imm16.
  * conditional branches (beq/bne/blez/bgtz/bltz/bgez and the -l likely forms): the condition operator and
    operands; the taken block holds the delay slot (A+4) then `goto L_target;`. Non-likely: the delay slot is
    emitted again on the fall-through path. Likely: fall-through is `goto skip_N;` past the copy, so the delay
    slot runs only when taken; both copies must be the same statement. Labels on a delay slot address are
    located relative to the copies.
  * link ops (jal/jalr/bgezal/bltzal): MIPS writes $ra = A+8, N64Recomp's C call does not. Any read of $ra
    after a link op and before a write/restore of it is listed, and each must carry a `ctx->r31 = A+8` patch
    in the live output (s1971 fixed the 6 bltzal $zero PIC sites in funcs_27.c).
Positive controls: ld 0x800934D4 and beql 0x8000354C must be enumerated and ok; the 6 s1971 sites must be
found as $ra consumers and patched. Negative controls: mutate an lbu macro to MEM_HU, drop one beql
`goto skip_`, and drop one s1971 patch line: each must add exactly one finding.
Exit 0 iff all controls pass and no unexplained mismatch remains outside data_gap_/fake_func_."""
import collections, glob, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REGEN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'scratch', 's7082', 'regen')
LIVE = sys.argv[2] if len(sys.argv) > 2 else os.path.abspath(os.path.join(ROOT, '..', 'N64Recomp', 'RecompiledFuncs'))

REGS = ['zero', 'at', 'v0', 'v1', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7',
        's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 't8', 't9', 'k0', 'k1', 'gp', 'sp', 'fp', 'ra']
RN = {('$' + n): i for i, n in enumerate(REGS)}
RN['$s8'] = 30
OP = re.compile(r'// 0x([0-9A-F]{8}): ([a-z0-9.]+)\s*(.*)$')
FUNC = re.compile(r'^RECOMP_FUNC void (\w+)\(')
FAKE = re.compile(r'^(data_gap_|fake_func_)')
LOADS = {'lb': 'MEM_B', 'lbu': 'MEM_BU', 'lh': 'MEM_H', 'lhu': 'MEM_HU', 'lw': 'MEM_W', 'lwu': 'MEM_WU', 'ld': 'LD'}
STORES = {'sb': 'MEM_B', 'sh': 'MEM_H', 'sw': 'MEM_W', 'sd': 'SD'}
WIDTH = {'lb': 1, 'lbu': 1, 'sb': 1, 'lh': 2, 'lhu': 2, 'sh': 2, 'lw': 4, 'lwu': 4, 'sw': 4, 'ld': 8, 'sd': 8}
CMP2 = {'beq': '==', 'bne': '!=', 'beql': '==', 'bnel': '!='}
CMP1 = {'blez': '<=', 'bgtz': '>', 'bltz': '<', 'bgez': '>=', 'blezl': '<=', 'bgtzl': '>', 'bltzl': '<',
        'bgezl': '>='}
LIKELY = {'beql', 'bnel', 'blezl', 'bgtzl', 'bltzl', 'bgezl'}
# branch sites whose block runs past the function's end: decoded data, never executed (s7082 table, s5xxx tails)
KNOWN_DATA = {('rspbootTextPreamble', '800825CC'): 'rspboot text preamble, 0 references (DECODED-TAIL-CENSUS)',
              ('applyVoiceDelayFilter', '8009D97C'): 'word after jr ra 0x8009D970, bltzal PIC table (s1971/s7082)',
              ('static_3_8009D978', '8009D97C'): 'same table word, dead static_3 copy (s7082)'}
LINK = {'jal', 'jalr', 'bgezal', 'bltzal'}


def reg_c(r):
    n = RN[r]
    return '0' if n == 0 else f'ctx->r{n}'


def imm_c(v):
    return ('-0X%X' % -v) if v < 0 else ('0X%X' % v)


def parse_imm(s):
    s = s.strip()
    neg = s.startswith('-')
    v = int(s.lstrip('-'), 16) if s.lstrip('-').lower().startswith('0x') else int(s.lstrip('-'))
    return -v if neg else v


def load(d):
    files = sorted(glob.glob(os.path.join(d, 'funcs_*.c')))
    if not files:
        sys.exit(f'no generated output in {d}')
    return [(os.path.basename(f), open(f, errors='replace').read().split('\n')) for f in files]


def functions(files):
    for fn, lines in files:
        func, start = None, 0
        for i, ln in enumerate(lines):
            m = FUNC.match(ln)
            if m:
                if func:
                    yield fn, func, lines, start, i
                func, start = m.group(1), i
        if func:
            yield fn, func, lines, start, len(lines)


def nonblank(lines, i, end):
    while i < end and not lines[i].strip():
        i += 1
    return i


def stmt_after(lines, i, end):
    """statements between a comment line i and the next comment/label/brace line"""
    out = []
    j = i + 1
    while j < end:
        s = lines[j].strip()
        if not s:
            j += 1; continue
        if s.startswith('//') or re.match(r'^(L_|skip_|after_)\w+:$', s) or s in ('}',) or s.startswith('if (') or s.startswith('goto '):
            break
        out.append(s); j += 1
    return out, j


def mem_expect(op, args):
    m = re.match(r'(\$\w+), (-?0x[0-9A-Fa-f]+|-?\d+)\((\$\w+)\)$', args)
    if not m:
        return None, None
    rt, off, base = m.group(1), parse_imm(m.group(2)), m.group(3)
    if op in LOADS:
        if RN[rt] == 0:
            return off, ''  # load to $zero: generator may drop it
        return off, f'ctx->r{RN[rt]} = {LOADS[op]}({reg_c(base)}, {imm_c(off)});'
    if op == 'sd':
        return off, f'SD({reg_c(rt)}, {imm_c(off)}, {reg_c(base)});'
    return off, f'{STORES[op]}({imm_c(off)}, {reg_c(base)}) = {reg_c(rt)};'


def alu_expect(op, args):
    p = [a.strip() for a in args.split(',')]
    if op == 'lui':
        return f'{reg_c(p[0])} = S32(0X{parse_imm(p[1]) & 0xFFFF:X} << 16);'
    v = parse_imm(p[2])
    if op == 'addiu':
        v = ((v & 0xFFFF) ^ 0x8000) - 0x8000
        return re.escape(f'{reg_c(p[0])} = ADD32({reg_c(p[1])}, {imm_c(v)});')
    sym = {'ori': '|', 'andi': '&', 'xori': '^'}[op]
    return re.escape(f'{reg_c(p[0])} = {reg_c(p[1])} {sym} 0X{v & 0xFFFF:X};')


def census(files, mutate=None):
    per = collections.defaultdict(lambda: [0, 0])
    bad, misal, sites, ra_reads, ds_labels = [], [], {}, [], collections.Counter()
    known = []
    for fn, func, lines, s0, s1 in functions(files):
        fake0 = bool(FAKE.match(func))
        comments = [(i, m) for i in range(s0, s1) for m in [OP.search(lines[i])] if m]
        # label positions (line index) keyed by address
        labels = {}
        for i in range(s0, s1):
            m = re.match(r'^L_([0-9A-F]{8}):$', lines[i].strip())
            if m:
                labels[m.group(1)] = i
        first_seen = {}
        for i, m in comments:
            first_seen.setdefault(m.group(1), i)
        for ci, (i, m) in enumerate(comments):
            addr, op, args = m.group(1), m.group(2), m.group(3).strip()
            if first_seen[addr] != i and op not in LOADS and op not in STORES:
                continue  # second copy of a delay slot: checked via its branch
            st, _ = stmt_after(lines, i, s1)
            stmt = st[0] if st else ''
            if mutate and mutate[0] == 'lbu' and (fn, i) == mutate[1]:
                stmt = stmt.replace('MEM_BU', 'MEM_HU')
            key = None; ok = True; why = ''; fake = fake0
            if op in LOADS or op in STORES:
                key = op
                off, exp = mem_expect(op, args)
                if exp is None:
                    ok, why = False, 'unparsed operands'
                elif exp and stmt != exp:
                    nx = comments[ci + 1][1] if ci + 1 < len(comments) else None
                    rt_c = exp.split(' = ')[0]
                    if (op == 'lw' and nx and nx.group(2) == 'jr' and stmt.startswith(rt_c + ' = ADD32(')):
                        why = 'KNOWN jump-table lw dropped (s7083: table word never read)'
                    else:
                        ok, why = False, f'want {exp}'
                if off is not None and off % WIDTH[op] and op in WIDTH:
                    misal.append((fn, i + 1, func, addr, op, args, fake))
            elif op in ('lui', 'addiu', 'ori', 'andi', 'xori'):
                p = [a.strip() for a in args.split(',')]
                if RN.get(p[0], 1) == 0:
                    continue
                key = op
                exp = alu_expect(op, args)
                if op == 'lui':
                    ok = stmt == exp
                else:
                    ok = re.fullmatch(exp, stmt) is not None or 'RELOC' in stmt or 'jr_addend' in stmt
                if not ok:
                    why = f'want {exp}'
            elif op in CMP2 or op in CMP1:
                key = op
                p = [a.strip() for a in args.split(',')]
                tgt = p[-1]
                if op in CMP2:
                    cond = f'if ({reg_c(p[0])} {CMP2[op]} {reg_c(p[1])}) {{'
                else:
                    cond = f'if (SIGNED({reg_c(p[0])}) {CMP1[op]} 0) {{'
                j = nonblank(lines, i + 1, s1)
                ds = '%08X' % (int(addr, 16) + 4)
                if lines[j].strip() != cond:
                    ok, why = False, f'cond {lines[j].strip()!r} want {cond!r}'
                else:
                    k = nonblank(lines, j + 1, s1)
                    dm = OP.search(lines[k])
                    if not dm or dm.group(1) != ds:
                        ok, why = False, 'taken block does not start with delay slot'
                    else:
                        ds_in, k2 = stmt_after(lines, k, s1)
                        k2 = nonblank(lines, k2, s1)
                        tail = []
                        while k2 < s1 and lines[k2].strip() != '}':
                            tail.append(lines[k2].strip()); k2 = nonblank(lines, k2 + 1, s1)
                        if not tail or tail[-1] != f'goto {tgt};':
                            ok, why = False, f'taken block ends {tail[-1:]!r} want goto {tgt}'
                        k3 = nonblank(lines, k2 + 1, s1)
                        nxt = lines[k3].strip()
                        if mutate and mutate[0] == 'beql' and (fn, i) == mutate[1]:
                            nxt = '/* mutated */'
                        if ok and op in LIKELY:
                            sm = re.match(r'^goto (skip_\d+);$', nxt)
                            k4 = nonblank(lines, k3 + 1, s1)
                            dm2 = OP.search(lines[k4])
                            if not sm:
                                ok, why = False, f'likely fall-through {nxt!r} is not goto skip_'
                            elif not dm2 or dm2.group(1) != ds:
                                ok, why = False, 'likely: no delay-slot copy after goto skip_'
                            else:
                                ds_out, k5 = stmt_after(lines, k4, s1)
                                k5 = nonblank(lines, k5, s1)
                                if ds_out != ds_in:
                                    ok, why = False, f'likely copies differ {ds_in} vs {ds_out}'
                                elif lines[k5].strip() != sm.group(1) + ':':
                                    ok, why = False, f'likely: {lines[k5].strip()!r} after copy, want {sm.group(1)}:'
                                if ds in labels:
                                    ds_labels[('likely', 'after-skip' if k3 < labels[ds] < k4 else 'ELSEWHERE')] += 1
                        elif ok:
                            dm2 = OP.search(lines[k3])
                            if not (dm2 and dm2.group(1) == ds) and not (nxt == f'L_{ds}:'):
                                k4 = nonblank(lines, k3 + 1, s1); dm3 = OP.search(lines[k4])
                                if re.match(r'^L_[0-9A-F]{8}:$', nxt) and dm3 and dm3.group(1) == ds:
                                    why = 'KNOWN stray out-of-function label before the delay slot (s7081 selfbranch)'
                                else:
                                    ok, why = False, f'non-likely fall-through {nxt!r} is not the delay slot'
                            elif ds in labels:
                                ds_labels[('plain', 'before-copy' if k2 < labels[ds] <= k3 else 'ELSEWHERE')] += 1
            if op in LINK:
                # scan forward for a read of $ra before it is written; stop at jr/j/b/return
                link = '%08X' % (int(addr, 16) + 8)
                for (i2, m2) in comments[ci + 1: ci + 40]:
                    a2, o2, g2 = m2.group(1), m2.group(2), m2.group(3)
                    if a2 == '%08X' % (int(addr, 16) + 4):
                        continue
                    ps = [x.strip() for x in re.split(r'[,()]', g2) if x.strip()]
                    if o2 == 'jr' and ps and ps[0] == '$ra':
                        break
                    rds = ps[1:] if o2 not in STORES and not o2.startswith('b') else ps
                    if o2 in STORES or o2 in ('sw', 'sd'):
                        rds = ps
                    if '$ra' in rds:
                        ra_reads.append((fn, func, addr, op, link, a2, o2, g2.strip(), fake)); break
                    if ps and ps[0] == '$ra' and o2 not in STORES and not o2.startswith('b'):
                        break  # $ra written (lw ra / addu ra)
                    if o2 in ('j', 'jr', 'b', 'jal', 'jalr', 'bgezal', 'bltzal') or o2 in CMP1 or o2 in CMP2:
                        break
            if key and not ok and (func, addr) in KNOWN_DATA:
                why = 'KNOWN decoded data: ' + KNOWN_DATA[(func, addr)]; fake = True
            if key and why.startswith('KNOWN'):
                known.append((fn, func, addr, op, why)); ok = True
            if key:
                per[key][0 if ok else 1] += 1
                if not ok:
                    bad.append((fn, i + 1, func, addr, op, args, why[:120], fake))
                if addr in ('800934D4', '8000354C'):
                    sites[addr] = (op, ok)
    census.known = known
    return per, bad, misal, sites, ra_reads, ds_labels


def live_patches(files, drop=None):
    pat = re.compile(r'ctx->r31 = 0x([0-9A-F]{8})u; /\* PATCH: s1971')
    found = set()
    for fn, lines in files:
        for i, ln in enumerate(lines):
            if drop and (fn, i) == drop:
                continue
            m = pat.search(ln)
            if m:
                found.add(m.group(1))
    return found


def first(files, opname, want_ok_pair=True):
    for fn, func, lines, s0, s1 in functions(files):
        for i in range(s0, s1):
            m = OP.search(lines[i])
            if m and m.group(2) == opname and not FAKE.match(func):
                return (fn, i)


def main():
    files = load(REGEN)
    per, bad, misal, sites, ra_reads, ds_labels = census(files)
    print('== shape census (op ok bad)')
    tot = 0
    for op in sorted(per):
        print(f'  {op:7s} {per[op][0]:6d} {per[op][1]:3d}'); tot += sum(per[op])
    print(f'  total sites {tot}, shapes {len(per)}')
    real_bad = [b for b in bad if not b[7]]
    print(f'== mismatches: {len(bad)} ({len(real_bad)} outside data_gap_/fake_func_)')
    for b in bad[:40]:
        print('  ', b)
    kc = collections.Counter(k[4].split(' (')[0][:60] for k in census.known)
    print(f'== known/explained differences: {len(census.known)}')
    for k, v in kc.items():
        print(f'  {v:4d}  {k}')
    print(f'== constant offsets misaligned for the access width: {len(misal)} '
          f'({sum(1 for x in misal if not x[6])} outside data)')
    for x in misal[:30]:
        print('  ', x)
    print(f'== delay-slot labels: {dict(ds_labels)}')
    print(f'== $ra read after a link op before any write: {len(ra_reads)}')
    live = load(LIVE)
    patched = live_patches(live)
    unpatched = [r for r in ra_reads if r[4] not in patched and not r[8]]
    for r in ra_reads:
        print('  ', r[:8], 'PATCHED' if r[4] in patched else ('data' if r[8] else 'UNPATCHED'))
    s1971 = {'8009D7E8', '8009D8F4', '8009DBAC', '8009DBD0', '8009DBF4', '8009DC18'}
    pc_ra = s1971 <= {r[4] for r in ra_reads} and s1971 <= patched
    pc_ok = sites.get('800934D4') == ('ld', True) and sites.get('8000354C') == ('beql', True)
    print(f'== positive controls: ld/beql {sites.get("800934D4")} {sites.get("8000354C")}, s1971 6/6 found+patched '
          f'{pc_ra} -> {"PASS" if pc_ok and pc_ra else "FAIL"}')
    # negative controls
    t = first(files, 'lbu'); _, b2, *_ = census(files, mutate=('lbu', t))
    n1 = len([b for b in b2 if b not in bad]) == 1
    t = first(files, 'beql'); _, b3, *_ = census(files, mutate=('beql', t))
    n2 = len([b for b in b3 if b not in bad]) == 1
    drop = None
    for fn, lines in live:
        for i, ln in enumerate(lines):
            if 'PATCH: s1971 bltzal-link' in ln and drop is None:
                drop = (fn, i)
    n3 = len(s1971 - live_patches(live, drop)) == 1
    neg_ok = n1 and n2 and n3
    print(f'== negative controls: lbu->MEM_HU {n1}, beql drop goto skip {n2}, drop s1971 patch {n3} -> '
          f'{"PASS" if neg_ok else "FAIL"}')
    ok = pc_ok and pc_ra and neg_ok and not real_bad and not unpatched
    print('== RESULT', 'PASS' if ok else 'FAIL', f'(unpatched $ra consumers: {len(unpatched)})')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
