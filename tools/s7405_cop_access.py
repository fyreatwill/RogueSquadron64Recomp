#!/usr/bin/env python3
"""s7405 class BO: coprocessor CONTROL-state access census.
Every mfc0/mtc0/dmfc0/dmtc0 (COP0: Status/IE, Cause, Count, Compare...), cfc1/ctc1 (FCSR $31 / FCR0), cache, eret and
TLB op in the retail disassembly, per function, tagged LIVE / REPLACED / IGNORED / dead (s7404 tagging).
For ctc1 rows the value written is constant-propagated (lui/ori/addiu/li within the function, plus the common
cfc1 rX; ori/and/xor; ctc1 rX read-modify-write) and decoded: RM bits 0-1, FS bit 24, enables bits 7-11.
Positive control: the scanner must see the Status/Count/Compare accesses inside replaced/ignored libultra
(__osDisableInt / osGetCount / __osSetCompare-class bodies) - if it does not, the regexes or tagging are broken.
Usage: tools/s7405_cop_access.py [disasm=/tmp/s7392.dis] [--all]"""
import re, sys, os, importlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
c7392 = importlib.import_module('s7392_mesg_census')
c7400 = importlib.import_module('s7400_replaced_contract')
c7401 = importlib.import_module('s7401_replaced_args')
c7404 = importlib.import_module('s7404_rcp_access')
COP = {'mfc0', 'mtc0', 'dmfc0', 'dmtc0', 'cfc1', 'ctc1', 'cache', 'eret', 'tlbwi', 'tlbwr', 'tlbp', 'tlbr'}
RMN = ['RN', 'RZ', 'RP', 'RM']


def fcsr(v):
    if not isinstance(v, int):
        return 'value=?'
    return 'value=%08X RM=%s FS=%d EN=%02X' % (v, RMN[v & 3], (v >> 24) & 1, (v >> 7) & 0x1F)


def scan(ins):
    out = collections.defaultdict(list)
    k, cur = {}, None
    for a, mn, ops, fn in ins:
        if fn != cur:
            cur, k = fn, {}
        if mn in COP:
            reg = ops[1] if len(ops) > 1 else ''
            extra = ''
            if mn == 'ctc1':
                extra = fcsr(k.get(ops[0]))
            out[fn].append((mn, reg, a, extra))
            if mn in ('mfc0', 'dmfc0', 'cfc1') and ops:
                k[ops[0]] = 'CF' if mn == 'cfc1' else None
            continue
        if mn == 'lui' and len(ops) == 2:
            k[ops[0]] = (int(ops[1], 0) << 16) & 0xFFFFFFFF
            continue
        if mn in ('addiu', 'daddiu', 'ori', 'andi', 'xori') and len(ops) == 3:
            b = 0 if ops[1] == 'zero' else k.get(ops[1])
            imm = int(ops[2], 0)
            if isinstance(b, int):
                v = {'ori': b | (imm & 0xFFFF), 'andi': b & imm & 0xFFFF, 'xori': b ^ (imm & 0xFFFF)}.get(mn, (b + imm) & 0xFFFFFFFF)
                k[ops[0]] = v
            elif b == 'CF':   # read-modify-write of FCSR: assume default FCSR 0x01000800 (libultra boot value) for decode
                k[ops[0]] = ('CF', mn, imm)
            else:
                k.pop(ops[0], None)
            continue
        if mn in ('li',) and len(ops) == 2:
            k[ops[0]] = int(ops[1], 0) & 0xFFFFFFFF
            continue
        if mn in ('move', 'or') and len(ops) >= 2:
            src = ops[1] if mn == 'move' else (ops[2] if ops[1] == 'zero' else ops[1] if ops[2] == 'zero' else None)
            if src is not None and src in k:
                k[ops[0]] = k[src]
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
    ign = c7404.ignored()
    acc = scan(ins)
    tally = collections.Counter()
    nonlive_regs = set()
    nlive = 0
    for fn in sorted(acc):
        live = fn not in allb and fn not in ign and c7401.live(ins, fn, allb)
        tag = 'LIVE' if live else ('REPLACED' if fn in allb else ('IGNORED' if fn in ign else 'dead'))
        for mn, reg, a, extra in acc[fn]:
            tally[(tag, mn, reg)] += 1
            if not live:
                nonlive_regs.add(reg)
            else:
                nlive += 1
            if live or '--all' in sys.argv:
                print('%-8s %-6s %-10s %-44s @%08x %s' % (tag, mn, reg, fn, a, extra))
    print('---')
    for key in sorted(tally):
        print('%-8s %-6s %-10s %d' % (key[0], key[1], key[2], tally[key]))
    cpass = {'c0_sr', '$9', '$11'} <= nonlive_regs   # objdump: $9=Count $11=Compare
    print('--- ignored_funcs=%d live_rows=%d control=%s (non-live regs %s)' % (
        len(ign), nlive, 'PASS' if cpass else 'FAIL', ','.join(sorted(r for r in nonlive_regs if r))))
    return 0 if cpass else 2


if __name__ == '__main__':
    sys.exit(main())
