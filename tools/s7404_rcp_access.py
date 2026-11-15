#!/usr/bin/env python3
"""s7404 class BN: direct RCP / PI-cart register access census.
Every load/store in the retail disassembly whose BASE register holds a lui/ori/addiu constant in KSEG1
(0xA0000000-0xBFFFFFFF), or a pointer KSEG1-converted by `or/addu rd, rs, rt` with a 0xA0000000 / 0x20000000
constant operand. Rows: region, function, insn addr, R/W, address, tag LIVE / REPLACED / dead (s7401 live()).
Also lists constant addresses only materialised (not dereferenced) in a live function, as a second-line net
(an address passed to a callee that dereferences it).
Usage: tools/s7404_rcp_access.py [disasm=/tmp/s7392.dis] [--all]"""
import re, sys, os, importlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
c7392 = importlib.import_module('s7392_mesg_census')
c7400 = importlib.import_module('s7400_replaced_contract')
c7401 = importlib.import_module('s7401_replaced_args')
LOADS = {'lb', 'lbu', 'lh', 'lhu', 'lw', 'lwu', 'ld', 'lwl', 'lwr', 'lwc1', 'ldc1', 'll'}
MEMOP = re.compile(r'^(-?\w+)\((\w+)\)$')
REGIONS = [(0xA0000000, 0xA0800000, 'RDRAM-K1'), (0xA3F00000, 0xA4000000, 'RDRAM-REG'), (0xA4000000, 0xA4002000, 'SP-MEM'),
           (0xA4040000, 0xA4100000, 'SP-REG'), (0xA4100000, 0xA4200000, 'DP-REG'), (0xA4300000, 0xA4400000, 'MI'),
           (0xA4400000, 0xA4500000, 'VI'), (0xA4500000, 0xA4600000, 'AI'), (0xA4600000, 0xA4700000, 'PI'),
           (0xA4700000, 0xA4800000, 'RI'), (0xA4800000, 0xA4900000, 'SI'), (0xA5000000, 0xA8000000, 'CART-D'),
           (0xA8000000, 0xB0000000, 'CART-SRAM'), (0xB0000000, 0xBFC00000, 'CART-ROM'), (0xBFC00000, 0xBFC00800, 'PIF')]
K1 = 'K1PTR'
SYMLIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'N64Recomp', 'src', 'symbol_lists.cpp')


def ignored():
    """N64Recomp::ignored_funcs: never emitted, so never executed (a live jal into one would fail to link)"""
    src = open(SYMLIST).read()
    i = src.index('N64Recomp::ignored_funcs')
    return set(re.findall(r'"(\w+)"', src[i:src.index('};', i)]))


def region(v):
    if v == K1:
        return 'K1-CONV'
    for lo, hi, n in REGIONS:
        if lo <= v < hi:
            return n
    return 'K1-other'


def scan(ins):
    out = collections.defaultdict(list)   # fn -> (kind, value, insn_addr, mnemonic)
    k, cur = {}, None
    for a, mn, ops, fn in ins:
        if fn != cur:
            cur, k = fn, {}
        if mn == 'lui' and len(ops) == 2:
            k[ops[0]] = (int(ops[1], 0) << 16) & 0xFFFFFFFF
            continue
        if mn in ('addiu', 'daddiu') and len(ops) == 3 and isinstance(k.get(ops[1]), int):
            k[ops[0]] = (k[ops[1]] + int(ops[2], 0)) & 0xFFFFFFFF
            if k[ops[0]] >= 0xA0000000 and k[ops[0]] < 0xC0000000:
                out[fn].append(('A', k[ops[0]], a, mn))
            continue
        if mn == 'ori' and len(ops) == 3 and isinstance(k.get(ops[1]), int):
            k[ops[0]] = k[ops[1]] | (int(ops[2], 0) & 0xFFFF)
            if 0xA0000000 <= k[ops[0]] < 0xC0000000:
                out[fn].append(('A', k[ops[0]], a, mn))
            continue
        if mn in ('or', 'addu', 'daddu') and len(ops) == 3:
            cs = [k.get(r) for r in ops[1:]]
            if any(isinstance(c, int) and c in (0xA0000000, 0x20000000) for c in cs) and not all(isinstance(c, int) for c in cs):
                k[ops[0]] = K1   # a conversion alone is not an access (flag words OR 0x20000000 too)
                continue
        if (mn in c7392.STORES or mn in LOADS) and len(ops) == 2:
            m = MEMOP.match(ops[1])
            if m and m.group(2) in k:
                b = k[m.group(2)]
                v = K1 if b == K1 else (b + int(m.group(1), 0)) & 0xFFFFFFFF
                if v == K1 or 0xA0000000 <= v < 0xC0000000:
                    out[fn].append(('W' if mn in c7392.STORES else 'R', v, a, mn))
            if mn in LOADS and ops[0] in k:
                del k[ops[0]]
            continue
        if ops and mn not in c7392.NODEST and ops[0] in k:
            del k[ops[0]]
        if mn in ('jal', 'jalr'):
            for r in ('v0', 'v1', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 'at'):
                k.pop(r, None)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    ins = c7392.parse(args[0] if args else c7392.DIS)
    allb = c7400.bodies()
    ign = ignored()
    acc = scan(ins)
    tally = collections.Counter()
    livec = {}
    for fn in sorted(acc):
        if fn not in livec:
            livec[fn] = fn not in allb and fn not in ign and c7401.live(ins, fn, allb)
        tag = 'LIVE' if livec[fn] else ('REPLACED' if fn in allb else ('IGNORED' if fn in ign else 'dead'))
        for kind, v, a, mn in acc[fn]:
            r = region(v)
            tally[(tag, kind, r)] += 1
            if tag == 'LIVE' or '--all' in sys.argv:
                vs = v if v == K1 else '%08X' % v
                print('%-8s %-9s %s %-5s %-9s %-44s @%s' % (tag, r, kind, mn, vs, fn, a))
    print('---')
    for key in sorted(tally):
        print('%-8s %s %-9s %d' % (key[0], key[1], key[2], tally[key]))
    nlive = sum(n for (t, kd, r), n in tally.items() if t == 'LIVE' and kd in 'RW')
    # positive control: the scanner must see the SI/PI/VI/AI register writes inside replaced/ignored libultra
    ctl = {r for (t, kd, r), n in tally.items() if t != 'LIVE' and kd == 'W'}
    cpass = {'SI', 'PI', 'VI', 'AI'} <= ctl
    print('--- ignored_funcs=%d live_deref_rows=%d control=%s (non-live W regions %s)' % (
        len(ign), nlive, 'PASS' if cpass else 'FAIL', ','.join(sorted(ctl))))
    return 0 if cpass and not nlive else 1


if __name__ == '__main__':
    sys.exit(main())
