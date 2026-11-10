#!/usr/bin/env python3
"""s7085 N64Recomp integer-lowering census over the pristine front-end output (scratch/s7082/regen,
regenerate with tools/regen_front.sh).

Every integer instruction site whose host semantics could differ from the R4300 is shape-checked:
the first lowered statement after the generator's "// 0xADDR: mnemonic" comment must match the
lowering that is correct for the op (sign extension of 32-bit results, 64-bit casts before div,
masked variable shifts, sign-extended sltiu immediates compared unsigned, ...). It also reports:
  * divide-by-zero / INT_MIN/-1 guards: for every div/divu/ddiv/ddivu, whether the following ops are
    GCC's `bne rt,$zero` + `break 7` (and, for signed div, `break 6`). On hardware the quotient of a
    divide by zero is defined (lo = rs<0 ? 1 : -1 for div, -1 for divu, hi = rs); in C it is UB and
    arm64 sdiv/udiv gives 0. A guarded site traps on retail (break 7 -> fault), so a difference is
    only reachable on a path where retail itself dies;
  * hi/lo scope: N64Recomp declares hi/lo per function, so an mflo/mfhi with no mult/div earlier in
    the same function reads 0 instead of the caller's value;
  * add/addi/daddi sites (overflow trap dropped: retail would fault, so only a crash path differs).
Positive control: the 0x800464F4 div (guarded, break 7 + break 6) must be enumerated and guarded.
Negative control: one mult lowering is mutated S64(S32 -> U64(U32 in memory; the shape check must
flag exactly that site. Exit 0 iff both controls pass and no unexplained shape mismatch remains."""
import collections, glob, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REGEN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'scratch', 's7082', 'regen')

R = r'ctx->r\d+'
RZ = r'(?:ctx->r\d+|0)'
IMM = r'-?0X[0-9A-F]+'
SHAPES = {
    'mult':  r'^result = S64\(S32\(' + R + r'\)\) \* S64\(S32\(' + R + r'\)\); lo = S32\(result >> 0\); hi = S32\(result >> 32\);',
    'multu': r'^result = U64\(U32\(' + R + r'\)\) \* U64\(U32\(' + R + r'\)\); lo = S32\(result >> 0\); hi = S32\(result >> 32\);',
    'div':   r'^lo = S32\(S64\(S32\((' + R + r')\)\) / S64\(S32\((' + R + r')\)\)\); hi = S32\(S64\(S32\(\1\)\) % S64\(S32\(\2\)\)\);',
    'divu':  r'^lo = S32\(U32\((' + R + r')\) / U32\((' + R + r')\)\); hi = S32\(U32\(\1\) % U32\(\2\)\);',
    'ddivu': r'^DDIVU\(U64\(' + R + r'\), U64\(' + R + r'\), &lo, &hi\);',
    'ddiv':  r'^DDIV\(S64\(' + R + r'\), S64\(' + R + r'\), &lo, &hi\);',
    'dmult': r'^DMULT\(S64\(' + R + r'\), S64\(' + R + r'\), &lo, &hi\);',
    'dmultu': r'^DMULTU\(U64\(' + R + r'\), U64\(' + R + r'\), &lo, &hi\);',
    'mflo':  r'^' + R + r' = lo;', 'mfhi': r'^' + R + r' = hi;',
    'mtlo':  r'^lo = ' + RZ + ';', 'mthi': r'^hi = ' + RZ + ';',
    'sll':   r'^' + R + r' = S32\(' + RZ + r' << \d+\);',
    'srl':   r'^' + R + r' = S32\(U32\(' + RZ + r'\) >> \d+\);',
    'sra':   r'^' + R + r' = S32\(SIGNED\(' + RZ + r'\) >> \d+\);',
    'sllv':  r'^' + R + r' = S32\(' + RZ + r' << \(' + RZ + r' & 31\)\);',
    'srlv':  r'^' + R + r' = S32\(U32\(' + RZ + r'\) >> \(' + RZ + r' & 31\)\);',
    'srav':  r'^' + R + r' = S32\(SIGNED\(' + RZ + r'\) >> \(' + RZ + r' & 31\)\);',
    'dsll':  r'^' + R + r' = ' + RZ + r' << \d+;',
    'dsll32': r'^' + R + r' = ' + RZ + r' << \(\d+ \+ 32\);',
    'dsrl':  r'^' + R + r' = ' + RZ + r' >> \d+;',
    'dsrl32': r'^' + R + r' = ' + RZ + r' >> \(\d+ \+ 32\);',
    'dsra':  r'^' + R + r' = SIGNED\(' + RZ + r'\) >> \d+;',
    'dsra32': r'^' + R + r' = SIGNED\(' + RZ + r'\) >> \(\d+ \+ 32\);',
    'dsllv': r'^' + R + r' = ' + RZ + r' << \(' + RZ + r' & 63\);',
    'dsrlv': r'^' + R + r' = ' + RZ + r' >> \(' + RZ + r' & 63\);',
    'dsrav': r'^' + R + r' = SIGNED\(' + RZ + r'\) >> \(' + RZ + r' & 63\);',
    'slt':   r'^' + R + r' = SIGNED\(' + RZ + r'\) < SIGNED\(' + RZ + r'\) \? 1 : 0;',
    'sltu':  r'^' + R + r' = ' + RZ + r' < ' + RZ + r' \? 1 : 0;',
    'slti':  r'^' + R + r' = SIGNED\(' + RZ + r'\) < ' + IMM + r' \? 1 : 0;',
    # sltiu: the 16-bit immediate is sign-extended to 64 bits, then compared unsigned. The census
    # records the immediates; any >= 0x8000 (negative) must be emitted as a 64-bit sign-extended value.
    'sltiu': r'^' + R + r' = ' + RZ + r' < (' + IMM + r') \? 1 : 0;',
    # addu feeding a jump table is lowered to the s7083-verified `gpr jr_addend_<jr addr> = rN;` form
    'addu':  r'^(?:' + R + r' = ADD32\(' + RZ + ', (?:' + RZ + '|' + IMM + r')\);|gpr jr_addend_[0-9A-F]{8} = ' + R + ';)',
    'addiu': r'^' + R + r' = ADD32\(' + RZ + ', (?:' + IMM + r'|RELOC_\w+\([^)]*\)|\(int16_t\)RELOC_\w+\([^)]*\))\);',
    'add':   r'^' + R + r' = ADD32\(' + RZ + ', ' + RZ + r'\);',
    'subu':  r'^' + R + r' = SUB32\(' + RZ + ', ' + RZ + r'\);',
    'lwl':   r'^' + R + r' = do_lwl\(rdram, ' + RZ + ', ' + R + ', ' + IMM + r'\);',
    'lwr':   r'^' + R + r' = do_lwr\(rdram, ' + RZ + ', ' + R + ', ' + IMM + r'\);',
    'swl':   r'^do_swl\(rdram, ' + IMM + ', ' + R + ', ' + RZ + r'\);',
    'swr':   r'^do_swr\(rdram, ' + IMM + ', ' + R + ', ' + RZ + r'\);',
}
OP = re.compile(r'// 0x([0-9A-F]{8}): ([a-z0-9]+)\s+(.*)$')
FUNC = re.compile(r'^RECOMP_FUNC void (\w+)\(')
FAKE = re.compile(r'^(data_gap_|fake_func_)')
MULDIV = {'mult', 'multu', 'div', 'divu', 'dmult', 'dmultu', 'ddiv', 'ddivu', 'mtlo', 'mthi'}
DIVS = {'div', 'divu', 'ddiv', 'ddivu'}


def load():
    files = sorted(glob.glob(os.path.join(REGEN, 'funcs_*.c')))
    if not files:
        sys.exit(f'no regen output in {REGEN} (run tools/regen_front.sh)')
    return [(os.path.basename(f), open(f, errors='replace').read().split('\n')) for f in files]


def functions(files):
    """yield (file, func, [(line_index, addr, op, operands, stmt_index, stmt)]) per function, in text order.
    Delay-slot copies of a branch appear twice (inside the taken block and after it); both are kept,
    deduplicated by address where order matters."""
    for fn, lines in files:
        func, ops = None, []
        for i, ln in enumerate(lines):
            m = FUNC.match(ln)
            if m:
                if func:
                    yield fn, func, ops
                func, ops = m.group(1), []
                continue
            m = OP.search(ln)
            if not m or func is None:
                continue
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            stmt = lines[j].strip() if j < len(lines) else ''
            ops.append((i, m.group(1), m.group(2), m.group(3).strip(), j, stmt))
        if func:
            yield fn, func, ops


def census(files, mutate=None):
    per = collections.defaultdict(lambda: [0, 0]); bad = []
    divs = []; hilo = []; traps = []; sltiu_imm = collections.Counter()
    for fn, func, ops in functions(files):
        fake = bool(FAKE.match(func))
        seen_md = False
        uniq = []
        for k, (i, addr, op, args, j, stmt) in enumerate(ops):
            if op not in SHAPES:
                if op in MULDIV:
                    seen_md = True
                continue
            if mutate and (fn, j) == mutate:
                stmt = stmt.replace('S64(S32(', 'U64(U32(')
            m = re.search(SHAPES[op], stmt)
            ok = m is not None
            per[op][0 if ok else 1] += 1
            if not ok:
                bad.append((fn, i + 1, func, addr, op, stmt[:110], fake))
            if op == 'sltiu' and m:
                sltiu_imm[m.group(1)] += 1
            if op in MULDIV:
                seen_md = True
            if op in ('mflo', 'mfhi') and not seen_md:
                hilo.append((fn, i + 1, func, addr, op, fake))
            if op in ('add', 'addi', 'daddi', 'dadd'):
                traps.append((fn, func, addr, op, fake))
            if op in DIVS:
                # look at the next distinct-address ops: GCC emits bne rt,$zero,L ; nop ; break 7
                rt = args.split(',')[-1].strip()
                nxt, seen = [], {addr}
                for (_, a2, o2, g2, _, _) in ops[k + 1:]:
                    if a2 in seen:
                        continue
                    seen.add(a2); nxt.append((o2, g2))
                    if len(nxt) >= 10:
                        break
                txt = ' | '.join(f'{o} {g}' for o, g in nxt)
                zero = bool(re.search(r'(bne|bnez) +' + re.escape(rt) + r', \$zero', txt)) and 'break 7' in txt
                ovf = 'break 6' in txt
                # a preceding beqz/bnez on the divisor in the previous 6 ops also counts as a guard
                prev = ' | '.join(f'{o} {g}' for (_, _, o, g, _, _) in ops[max(0, k - 6):k])
                pre = bool(re.search(r'(beq|beqz|bne|bnez|beql|bnel) +' + re.escape(rt) + r', \$zero', prev))
                divs.append(dict(file=fn, line=i + 1, func=func, addr=addr, op=op, rt=rt, zero=zero,
                                 ovf=ovf, pre=pre, fake=fake))
        _ = uniq
    return per, bad, divs, hilo, traps, sltiu_imm


def main():
    files = load()
    per, bad, divs, hilo, traps, sltiu_imm = census(files)
    print('== shape census (op ok bad)')
    tot = 0
    for op in sorted(per):
        print(f'  {op:7s} {per[op][0]:6d} {per[op][1]:3d}'); tot += sum(per[op])
    print(f'  total sites {tot}, shapes {len(per)}')
    real_bad = [b for b in bad if not b[6]]
    print(f'== shape mismatches: {len(bad)} ({len(real_bad)} outside data_gap_/fake_func_)')
    for b in bad[:40]:
        print('  ', b)
    neg_imm = {k: v for k, v in sltiu_imm.items() if k.startswith('-') or int(k, 16) >= 0x8000}
    print(f'== sltiu immediates: {len(sltiu_imm)} distinct, {sum(sltiu_imm.values())} sites; negative/high: {neg_imm or "none"}')
    print('== divide sites')
    cls = collections.Counter()
    for d in divs:
        if d['fake']:
            c = 'data'
        elif d['zero'] and (d['op'] != 'div' or d['ovf']):
            c = 'guarded(break7' + ('+break6' if d['ovf'] else '') + ')'
        elif d['zero']:
            c = 'guarded(break7,no-ovf-check)'
        elif d['pre']:
            c = 'pre-checked'
        else:
            c = 'UNGUARDED'
        d['cls'] = c; cls[(d['op'], c)] += 1
    for k, v in sorted(cls.items()):
        print(f'  {k[0]:6s} {k[1]:30s} {v}')
    for d in divs:
        if d['cls'] in ('UNGUARDED', 'pre-checked', 'guarded(break7,no-ovf-check)'):
            print(f"    {d['cls']:28s} {d['op']:5s} 0x{d['addr']} {d['func']} ({d['file']}:{d['line']}) rt={d['rt']}")
    print(f'== mflo/mfhi with no mult/div earlier in the same function: {len(hilo)}')
    for h in hilo:
        print('  ', h)
    print(f'== overflow-trapping adds lowered without the trap: {len(traps)}')
    for t in traps:
        print('  ', t)

    # positive control: 0x800464F4 div guarded with break 7 + break 6
    pc = [d for d in divs if d['addr'] == '800464F4']
    pc_ok = len(pc) >= 1 and all(d['cls'].startswith('guarded(break7+break6') for d in pc)
    print(f'== positive control 0x800464F4: {[d["cls"] for d in pc]} -> {"PASS" if pc_ok else "FAIL"}')
    # negative control: mutate the first mult lowering
    tgt = None
    for fn, func, ops in functions(files):
        for (i, addr, op, args, j, stmt) in ops:
            if op == 'mult':
                tgt = (fn, j); break
        if tgt:
            break
    _, bad2, *_ = census(files, mutate=tgt)
    extra = [b for b in bad2 if b not in bad]
    neg_ok = len(extra) == 1 and extra[0][4] == 'mult'
    print(f'== negative control (mutated mult at {tgt}): {len(extra)} new mismatch -> {"PASS" if neg_ok else "FAIL"}')
    sys.exit(0 if pc_ok and neg_ok and not real_bad else 1)


if __name__ == '__main__':
    main()
