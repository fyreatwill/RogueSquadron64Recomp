#!/usr/bin/env python3
"""s7392 class BB: static census of every guest osSendMesg / osJamMesg call site.

Usage: tools/s7392_mesg_census.py [disasm]   (default /tmp/s7392.dis; make it with
  mips64-elf-objdump -d --no-show-raw-insn ../rogue_squadron64/build/roguesquadron.elf > /tmp/s7392.dis)
      tools/s7392_mesg_census.py --check     exit 1 if a NOBLOCK site with an ignored result lacks a verdict row in
                                             tools/s7392_mesg_reviewed.tsv (a NEW site after a regen / rebuild).

Per site: caller function, the mq argument (a0, resolved when it is a lui/addiu constant or a register copy),
flags (a2: 0 = OS_MESG_NOBLOCK, 1 = OS_MESG_BLOCK, '?' unresolved), and what happens to v0 after the call
along the fall-through path: TESTED (a branch reads it), USED (any other read), RETURNED (reaches jr ra
unwritten), IGNORED (overwritten or another call first). Only NOBLOCK + IGNORED/USED-not-tested can drop a
message silently; those rows need a hand verdict.
"""
import re, sys, os

DIS = '/tmp/s7392.dis'
REVIEWED = os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7392_mesg_reviewed.tsv')
TARGETS = ('osSendMesg', 'osJamMesg')
STORES = {'sb', 'sh', 'sw', 'sd', 'swl', 'swr', 'swc1', 'sdc1', 'sc', 'scd', 'sdl', 'sdr'}
NODEST = STORES | {'jr', 'jalr', 'mtc1', 'dmtc1', 'mthi', 'mtlo', 'mult', 'multu', 'div', 'divu', 'dmult',
                   'dmultu', 'ddiv', 'ddivu', 'teq', 'tne', 'ctc1', 'mtc0', 'break', 'syscall', 'nop', 'sync', 'cache'}
BL = {0x14: 'beql', 0x15: 'bnel', 0x16: 'blezl', 0x17: 'bgtzl'}
REGN = ['zero', 'at', 'v0', 'v1', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7',
        's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 't8', 't9', 'k0', 'k1', 'gp', 'sp', 'fp', 'ra']
LINE = re.compile(r'^([0-9a-f]{8}):\s+(\S+)\s*(.*)$')
FUNC = re.compile(r'^([0-9a-f]{8}) <([^>]+)>:$')


def parse(path):
    funcs, cur, insns = {}, None, []
    for ln in open(path):
        ln = ln.rstrip()
        m = FUNC.match(ln)
        if m:
            cur = m.group(2)
            continue
        m = LINE.match(ln)
        if m and cur:
            ops = [o.strip() for o in m.group(3).split(',')] if m.group(3) else []
            mn = m.group(2)
            if mn == '.word':  # objdump leaves branch-likely (beql/bnel/blezl/bgtzl) undecoded on this ELF
                w = int(ops[0], 16)
                op = w >> 26
                if op in BL:
                    rs, rt = (w >> 21) & 31, (w >> 16) & 31
                    tgt = (int(m.group(1), 16) + 4 + (((w & 0xFFFF) ^ 0x8000) - 0x8000) * 4) & 0xFFFFFFFF
                    mn, ops = BL[op], [REGN[rs], REGN[rt], '%08x' % tgt]
            insns.append((int(m.group(1), 16), mn, ops, cur))
    return insns


def regs_in(op):
    return re.findall(r'\b(zero|at|v[01]|a[0-3]|t[0-9]|s[0-8]|k[01]|gp|sp|fp|ra)\b', op)


def dest_of(mn, ops):
    if mn in NODEST or mn.startswith('b') or mn in ('j', 'jal'):
        return None
    return ops[0] if ops else None


def resolve(insns, i, reg, depth=0):
    """Backward linear scan in the same function for the last write of reg (call delay slot i+1 included)."""
    fn = insns[i][3]
    cand = [i + 1] + list(range(i - 1, max(-1, i - 60), -1))
    hi = None
    for k in cand:
        a, mn, ops, f = insns[k]
        if f != fn:
            break
        if k < i and mn in ('jal', 'jalr'):
            return '?'
        d = dest_of(mn, ops)
        if d != reg:
            continue
        if mn == 'li':
            return int(ops[1], 0)
        if mn == 'move':
            if ops[1] == 'zero':
                return 0
            return resolve_from(insns, k, ops[1], depth)
        if mn == 'addiu' and ops[1] == 'zero':
            return int(ops[2], 0) & 0xFFFFFFFF
        if mn == 'addiu' and ops[1] == reg:
            lo = int(ops[2], 0)
            base = resolve_from(insns, k, reg, depth)
            return (base + lo) & 0xFFFFFFFF if isinstance(base, int) else '?'
        if mn == 'lui':
            return (int(ops[1], 0) << 16) & 0xFFFFFFFF
        if mn == 'ori' and ops[1] == reg:
            base = resolve_from(insns, k, reg, depth)
            return base | int(ops[2], 0) if isinstance(base, int) else '?'
        if mn in ('or', 'addu') and 'zero' in ops[1:]:
            src = ops[2] if ops[1] == 'zero' else ops[1]
            return resolve_from(insns, k, src, depth)
        return '%s:%s' % (mn, ','.join(ops[1:]))
    return '?'


def resolve_from(insns, k, reg, depth):
    if depth > 4:
        return '?'
    fn = insns[k][3]
    for j in range(k - 1, max(-1, k - 60), -1):
        a, mn, ops, f = insns[j]
        if f != fn or mn in ('jal', 'jalr'):
            return '?'
        if dest_of(mn, ops) == reg:
            # re-enter with a fake call position so resolve() scans from j
            return resolve(insns, j - 1, reg, depth + 1) if False else _single(insns, j, reg, depth + 1)
    return '?'


def _single(insns, j, reg, depth):
    a, mn, ops, f = insns[j]
    if mn == 'li':
        return int(ops[1], 0)
    if mn == 'lui':
        return (int(ops[1], 0) << 16) & 0xFFFFFFFF
    if mn == 'move':
        return 0 if ops[1] == 'zero' else resolve_from(insns, j, ops[1], depth)
    if mn == 'addiu':
        if ops[1] == 'zero':
            return int(ops[2], 0) & 0xFFFFFFFF
        base = resolve_from(insns, j, ops[1], depth)
        return (base + int(ops[2], 0)) & 0xFFFFFFFF if isinstance(base, int) else '?'
    if mn == 'ori':
        base = resolve_from(insns, j, ops[1], depth)
        return base | int(ops[2], 0) if isinstance(base, int) else '?'
    return '%s:%s' % (mn, ','.join(ops[1:]))


def v0_fate(insns, i):
    fn = insns[i][3]
    k = i + 2
    for _ in range(40):
        if k >= len(insns) or insns[k][3] != fn:
            return 'END'
        a, mn, ops, f = insns[k]
        d = dest_of(mn, ops)
        reads = [r for n, o in enumerate(ops) for r in regs_in(o) if not (n == 0 and d is not None)]
        if 'v0' in reads:
            return 'TESTED' if mn.startswith('b') else 'USED:%s' % mn
        if mn == 'jr' and ops and ops[0] == 'ra':
            # delay slot may write v0
            a2, mn2, ops2, _ = insns[k + 1]
            return 'IGNORED' if dest_of(mn2, ops2) == 'v0' else 'RETURNED'
        if mn in ('jal', 'jalr'):
            return 'IGNORED'
        if d == 'v0':
            return 'IGNORED'
        if mn in ('j', 'b'):
            tgt = int(ops[-1].split()[0], 16)
            idx = next((n for n, x in enumerate(insns) if x[0] == tgt), None)
            if idx is None:
                return 'END'
            # delay slot first
            a2, mn2, ops2, _ = insns[k + 1]
            if dest_of(mn2, ops2) == 'v0':
                return 'IGNORED'
            k = idx
            continue
        k += 1
    return 'FAR'


def fmt(v):
    return '%08X' % v if isinstance(v, int) else str(v)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    check = '--check' in sys.argv
    insns = parse(args[0] if args else DIS)
    rows = []
    for i, (a, mn, ops, fn) in enumerate(insns):
        if mn != 'jal' or not ops:
            continue
        t = re.search(r'<([^>+]+)>', ops[0])
        if not t or t.group(1) not in TARGETS:
            continue
        rows.append((a, fn, t.group(1), fmt(resolve(insns, i, 'a0')), fmt(resolve(insns, i, 'a2')), v0_fate(insns, i)))
    rev = {}
    if os.path.exists(REVIEWED):
        for ln in open(REVIEWED):
            if ln.startswith('#') or not ln.strip():
                continue
            p = ln.rstrip('\n').split('\t')
            rev[p[0].upper()] = p
    need, missing = 0, []
    for a, fn, tgt, mq, fl, fate in rows:
        risky = fl not in ('00000001',) and not fate.startswith('TESTED') and fate != 'RETURNED'
        key = '%08X' % a
        verdict = rev.get(key, [None, None, None, ''])[3] if risky else ''
        if risky:
            need += 1
            if not verdict:
                missing.append(key)
        print('%s\t%-34s\t%s\tmq=%s\tflags=%s\tv0=%s\t%s' % (key, fn[:34], tgt, mq, fl, fate,
                                                              ('REVIEW:' + verdict) if risky else ''))
    n_nb = sum(1 for r in rows if r[4] == '00000000')
    n_b = sum(1 for r in rows if r[4] == '00000001')
    print('SUMMARY sites=%d send=%d jam=%d noblock=%d block=%d unresolved=%d need_review=%d missing=%d' % (
        len(rows), sum(r[2] == 'osSendMesg' for r in rows), sum(r[2] == 'osJamMesg' for r in rows), n_nb, n_b,
        len(rows) - n_nb - n_b, need, len(missing)))
    if check and missing:
        print('MISSING ' + ' '.join(missing))
        sys.exit(1)


if __name__ == '__main__':
    main()
