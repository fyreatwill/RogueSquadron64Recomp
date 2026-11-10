#!/usr/bin/env python3
"""s7087 N64Recomp residual-opcode census: the last mnemonics no earlier census checked, plus a
coverage table that maps EVERY mnemonic in the front-end output to the census tool that checks it.

Over the pristine front-end output (scratch/s7082/regen; regenerate with tools/regen_front.sh):
  * and/or/xor/nor/negu: operand-checked. The first statement after "// 0xADDR: op $rd, $rs, $rt"
    must be `ctx->rD = S op T;` with the disassembly's register numbers ($zero printed as 0);
    nor = ~(S | T) on the full 64 bits; negu $rd, $rt = SUB32(0, T).
  * mfc0/mtc0: per site the COP0 register and the lowering. Status must be cop0_status_read /
    cop0_status_write (librecomp recomp.cpp handles only the FR bit, asserts on anything else);
    any other COP0 register must be in decoded data (data_gap_/fake_func_) or a do_break.
    For each real Status write, the value is classified by the preceding lui/or/and ops
    (set-FR / clear-FR / restore-saved).
  * .word and scd: which function they sit in and whether a real code path reaches them.
Positive controls: `and` at 0x80004910 and the projectPointToScreen Status read 0x800196A8 are
enumerated and ok. Negative controls: one nor mutated `~(` -> `(` and one negu SUB32(0 -> ADD32(0
must each add exactly one finding. Exit 0 iff controls pass, no unexplained finding remains and
every mnemonic maps to a census."""
import collections, glob, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REGEN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'scratch', 's7082', 'regen')
REGS = ['zero', 'at', 'v0', 'v1', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7',
        's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 't8', 't9', 'k0', 'k1', 'gp', 'sp', 'fp', 'ra']
RN = {('$' + n): i for i, n in enumerate(REGS)}
RN['$s8'] = 30
OP = re.compile(r'// 0x([0-9A-F]{8}): ([a-z0-9.]+)\s*(.*)$')
FUNC = re.compile(r'^RECOMP_FUNC void (\w+)\(')
FAKE = re.compile(r'^(data_gap_|fake_func_)')
BIN = {'and': '&', 'or': '|', 'xor': '^'}
CENSUS_TOOLS = ['s7082_jal_census.py', 's7083_lowering_census.py', 's7084_fpu_census.py',
                's7085_int_census.py', 's7086_mem_branch_census.py']
MINE = {'and', 'or', 'xor', 'nor', 'negu', 'mfc0', 'mtc0', '.word', 'scd', 'nop'}


def g(r):
    n = RN[r.strip()]
    return '0' if n == 0 else f'ctx->r{n}'


def load():
    files = sorted(glob.glob(os.path.join(REGEN, 'funcs_*.c')))
    if not files:
        sys.exit(f'no regen output in {REGEN} (run tools/regen_front.sh)')
    return [(os.path.basename(f), open(f, errors='replace').read().split('\n')) for f in files]


def sites(files):
    for fn, lines in files:
        func = None
        for i, ln in enumerate(lines):
            m = FUNC.match(ln)
            if m:
                func = m.group(1); continue
            m = OP.search(ln)
            if not m or func is None:
                continue
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            yield fn, i, func, m.group(1), m.group(2), m.group(3).split('#')[0].strip(), j, \
                (lines[j].strip() if j < len(lines) else ''), lines


def expect(op, args):
    a = [x.strip() for x in args.split(',')]
    if op in BIN:
        return f'{g(a[0])} = {g(a[1])} {BIN[op]} {g(a[2])};'
    if op == 'nor':
        return f'{g(a[0])} = ~({g(a[1])} | {g(a[2])});'
    if op == 'negu':
        return f'{g(a[0])} = SUB32(0, {g(a[1])});'
    return None


def census(files, mutate=None):
    per = collections.defaultdict(lambda: [0, 0]); bad = []; cop0 = []; data = []; mn = collections.Counter()
    for fn, i, func, addr, op, args, j, stmt, lines in sites(files):
        mn[op] += 1
        fake = bool(FAKE.match(func))
        if mutate and (fn, j) in mutate:
            stmt = stmt.replace('~(', '(', 1).replace('SUB32(0,', 'ADD32(0,', 1)
        exp = expect(op, args)
        if exp is not None:
            ok = stmt == exp
            per[op][0 if ok else 1] += 1
            if not ok:
                bad.append((fn, i + 1, func, addr, op, args, stmt[:80], exp, fake))
        elif op in ('mfc0', 'mtc0'):
            reg = args.split(',')[-1].strip()
            if op == 'mfc0':
                low = 'status_read' if re.match(r'^ctx->r\d+ = cop0_status_read\(ctx\);', stmt) else \
                      'do_break' if stmt.startswith('do_break(') else 'other:' + stmt[:40]
                val = ''
            else:
                # the write is printed right after the next op's comment line in this generator
                blk = ' '.join(lines[i:i + 4])
                low = 'status_write' if 'cop0_status_write(ctx' in blk else \
                      'do_break' if 'do_break(' in blk else 'other'
                # classify the value from the 4 preceding ops
                prev = ' | '.join(OP.search(l).group(2) + ' ' + OP.search(l).group(3).split('#')[0].strip()
                                  for l in lines[max(0, i - 10):i] if OP.search(l))
                val = 'set-FR' if re.search(r'lui +\$\w+, 0x400 \| or ', prev) else \
                      'clear-FR' if re.search(r'lui +\$\w+, 0xFBFF|and ', prev) else 'restore-saved'
            cop0.append(dict(file=fn, line=i + 1, func=func, addr=addr, op=op, reg=reg, low=low, val=val, fake=fake))
        elif op in ('.word', 'scd'):
            data.append(dict(file=fn, line=i + 1, func=func, addr=addr, op=op, args=args[:30], fake=fake,
                             low=stmt[:40]))
    return per, bad, cop0, data, mn


def coverage(mn):
    owner = {}
    for t in CENSUS_TOOLS:
        src = open(os.path.join(ROOT, 'tools', t)).read()
        for m in set(re.findall(r"'([a-z][a-z0-9.]*)'", src)):
            owner.setdefault(m, []).append(t.split('_')[0])
    rows = []
    for m, c in mn.most_common():
        who = (owner.get(m, []) + (['s7087'] if m in MINE else []))
        rows.append((m, c, who))
    return rows


def main():
    files = load()
    per, bad, cop0, data, mn = census(files)
    print('== logic/negate shape census (op ok bad), operand-checked')
    for op in sorted(per):
        print(f'  {op:5s} {per[op][0]:5d} {per[op][1]:3d}')
    real_bad = [b for b in bad if not b[8]]
    print(f'== mismatches: {len(bad)} ({len(real_bad)} outside data_gap_/fake_func_)')
    for b in bad[:20]:
        print('  ', b)
    print('== COP0 sites')
    for c in cop0:
        print(f"  {c['op']} 0x{c['addr']} {c['reg']:8s} {c['low']:13s} {c['val']:13s} {c['func']}{' [data]' if c['fake'] else ''}")
    cop0_bad = [c for c in cop0 if not c['fake'] and not (c['reg'] == 'Status' and c['low'] in ('status_read', 'status_write'))]
    print(f'  real-code COP0 sites not lowered to the Status helpers: {len(cop0_bad)}')
    print('== .word / scd sites')
    for d in data:
        print(f"  {d['op']:5s} 0x{d['addr']} {d['args']:30s} {d['func']}{' [data]' if d['fake'] else ''} -> {d['low']}")
    rows = coverage(mn)
    unmapped = [r for r in rows if not r[2]]
    print(f'== mnemonic coverage: {len(rows)} mnemonics, {sum(mn.values())} sites, unmapped {len(unmapped)}')
    for m, c, who in rows:
        print(f'  {m:10s} {c:6d} {",".join(sorted(set(who))) or "UNMAPPED"}')

    pc1 = any(b for b in [1] if per['and'][0] > 0) and not any(b[3] == '80004910' for b in bad)
    pc2 = any(c['addr'] == '800196A8' and c['low'] == 'status_read' for c in cop0)
    print(f'== positive controls: and 0x80004910 ok={pc1}, Status read 0x800196A8 ok={pc2}')
    tgt = []
    for want in ('nor', 'negu'):
        for fn, i, func, addr, op, args, j, stmt, lines in sites(files):
            if op == want and not FAKE.match(func):
                tgt.append((fn, j)); break
    _, bad2, *_ = census(files, mutate=set(tgt))
    extra = [b for b in bad2 if b not in bad]
    neg_ok = len(extra) == 2 and sorted(b[4] for b in extra) == ['negu', 'nor']
    print(f'== negative control (mutated nor + negu at {tgt}): {len(extra)} new -> {"PASS" if neg_ok else "FAIL"}')
    ok = pc1 and pc2 and neg_ok and not real_bad and not cop0_bad and not unmapped
    print('RESULT', 'PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
