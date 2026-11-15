#!/usr/bin/env python3
"""s7402 class BL: replaced-libultra SIDE-EFFECT contract census.
For every replaced libultra function with live guest callers (s7400 rows), walk its RETAIL body plus transitive guest
callees and collect absolute-address stores (lui/addiu/ori constant base + offset). Join each written global with every
LIVE guest reader (non-replaced function, s7401 live()) that loads the same address or materialises its address.
Then ask whether the port writes it: the address (or a symbol from KNOWN) appears in a port replacement body / src.
  H-unwritten  retail writes G, a live game function reads G, the port never writes G  (rc 1 unless reviewed)
  PORT-WRITES  the port source references G
  NO-READER    retail writes G but no live guest code reads it
Usage: tools/s7402_side_effects.py [disasm=/tmp/s7392.dis] [--rows]"""
import re, sys, os, glob, importlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
c7392 = importlib.import_module('s7392_mesg_census')
c7400 = importlib.import_module('s7400_replaced_contract')
c7401 = importlib.import_module('s7401_replaced_args')
LOADS = {'lb', 'lbu', 'lh', 'lhu', 'lw', 'lwu', 'ld', 'lwl', 'lwr', 'lwc1', 'ldc1', 'll'}
MEMOP = re.compile(r'^(-?\w+)\((\w+)\)$')
REVIEWED = os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7402_side_reviewed.tsv')


def imm(s):
    return int(s, 0)


def scan(ins):
    """per function: list of (kind, addr, insn_addr) kind in W (store) R (load) A (address materialised)"""
    out = collections.defaultdict(list)
    k = {}
    cur = None
    for a, mn, ops, fn in ins:
        if fn != cur:
            cur, k = fn, {}
        if mn in ('lui',) and len(ops) == 2:
            k[ops[0]] = (imm(ops[1]) << 16) & 0xFFFFFFFF
            continue
        if mn in ('addiu', 'daddiu') and len(ops) == 3 and ops[1] in k:
            v = (k[ops[1]] + imm(ops[2])) & 0xFFFFFFFF
            out[fn].append(('A', v, a)); k[ops[0]] = v
            continue
        if mn == 'ori' and len(ops) == 3 and ops[1] in k:
            v = k[ops[1]] | (imm(ops[2]) & 0xFFFF); out[fn].append(('A', v, a)); k[ops[0]] = v
            continue
        if (mn in c7392.STORES or mn in LOADS) and len(ops) == 2:
            m = MEMOP.match(ops[1])
            if m and m.group(2) in k:
                v = (k[m.group(2)] + imm(m.group(1))) & 0xFFFFFFFF
                if 0x80000000 <= v < 0x80800000:
                    out[fn].append(('W' if mn in c7392.STORES else 'R', v, a))
            if mn in LOADS and ops[0] in k:
                del k[ops[0]]
            continue
        if ops and mn not in c7392.NODEST and ops[0] in k:
            del k[ops[0]]
        if mn in ('jal', 'jalr'):
            for r in ('v0', 'v1', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 'at'):
                k.pop(r, None)
    return out


def closure(ins, root, byfn):
    seen, todo = set(), [root]
    while todo:
        f = todo.pop()
        if f in seen:
            continue
        seen.add(f)
        for a, mn, ops, fn in byfn.get(f, ()):
            if mn == 'jal' and ops:
                m = re.search(r'<([^>+]+)>', ops[0])
                if m:
                    todo.append(m.group(1))
    return seen


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    ins = c7392.parse(args[0] if args else c7392.DIS)
    allb = c7400.bodies()
    byfn = collections.defaultdict(list)
    for x in ins:
        byfn[x[3]].append(x)
    acc = scan(ins)
    port_src = '\n'.join(open(f, errors='replace').read() for f in c7400.SRC)
    port_lc = port_src.lower()
    livecache = {}

    def live(fn):
        if fn not in livecache:
            livecache[fn] = fn not in allb and c7401.live(ins, fn, allb)
        return livecache[fn]
    # every global any live function reads / takes the address of
    readers = collections.defaultdict(set)
    for fn, lst in acc.items():
        for kind, v, a in lst:
            if kind in ('R', 'A'):
                readers[v].add(fn)
    rev = {}
    if os.path.exists(REVIEWED):
        for ln in open(REVIEWED):
            if ln.strip() and not ln.startswith('#'):
                p = ln.rstrip('\n').split('\t'); rev[p[0].upper()] = p
    roots = sorted(n for n in allb if any(mn == 'jal' and ops and ('<%s>' % n) in ops[0] and fn not in allb and live(fn)
                                          for a, mn, ops, fn in ins))
    gw = collections.defaultdict(set)   # global -> retail writer roots
    for r in roots:
        for f in closure(ins, r, byfn):
            for kind, v, a in acc.get(f, ()):
                if kind == 'W':
                    gw[v].add('%s/%s' % (r, f) if f != r else r)
    tally, flagged = collections.Counter(), 0
    for g in sorted(gw):
        lr = sorted(f for f in readers.get(g, set()) | readers.get(g & ~3, set()) if live(f))
        hexs = '%08x' % g
        pw = hexs in port_lc or ('0x%x' % g) in port_lc or ('0x%x' % (g & 0x1FFFFFFF)) in port_lc
        if not lr:
            c = 'NO-READER'
        elif pw:
            c = 'PORT-WRITES'
        else:
            c = 'H-unwritten'
        if c == 'H-unwritten' and hexs.upper() in rev:
            c = 'REVIEWED:' + rev[hexs.upper()][1]
        tally[c.split(':')[0] + (':' + c.split(':')[1] if ':' in c else '')] += 1
        flagged += c == 'H-unwritten'
        if c != 'NO-READER' or '--rows' in sys.argv:
            print('%-22s %08X writers=%s' % (c, g, ','.join(sorted(gw[g]))[:110]))
            if c != 'NO-READER':
                print('    readers(%d)=%s' % (len(lr), ','.join(lr)[:160]))
    print('--- roots=%d globals_written=%d %s unreviewed_H-unwritten=%d' % (len(roots), len(gw), dict(tally), flagged))
    return 1 if flagged else 0


if __name__ == '__main__':
    sys.exit(main())
