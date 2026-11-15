#!/usr/bin/env python3
"""s7419 class CB: objdump vs rabbitizer (RecompiledFuncs disasm comments) agreement, per (function, address).

Usage: tools/s7419_dis_agree.py [disasm=/tmp/s7419_canon.dis] [--verbose] [--controls]
  rc 0 = no WORD / DIFF / NOMATCH / weak-join row outside data_gap fillers, RSP ucode and the REVIEWED table
  (and, with --controls, the plain `objdump -d` listing IS flagged: ldc1/sdc1/cache as .word, the
  texPackTlutAtAllocSlot body as NOMATCH). rc 1 otherwise.

Rows: SAME / ALIAS (pseudo-op spelling, listed) / WORD (objdump left it as .word; raw word + rabbitizer op) /
DIFF (different instruction). Operands are compared too for SAME rows (registers + integers, normalised).
"""
import re, sys, os, glob, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUNCS = os.path.join(ROOT, '../N64Recomp/RecompiledFuncs')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
args = [a for a in sys.argv[1:] if not a.startswith('--')]
DIS = args[0] if args else '/tmp/s7419_canon.dis'
VERB = '--verbose' in sys.argv
BAD = []
UCODE = re.compile(r'^(gsp\w+TextStart|asp\w+(Text|Data)Start|rspboot\w*|\w+_?ucode\w*)$')
LINE = re.compile(r'^([0-9a-f]{8}):\s+(\S+)\s*(.*)$')
FUNC = re.compile(r'^([0-9a-f]{8}) <([^>]+)>:$')
CMT = re.compile(r'// 0x([0-9A-F]{8}): (\S+)\s*([^/]*)')
# objdump spelling -> set of rabbitizer spellings that encode the same instruction
ALIAS = {'move': {'or', 'addu', 'daddu'}, 'li': {'addiu', 'ori'}, 'b': {'beq'}, 'beqz': {'beq'}, 'bnez': {'bne'},
         'negu': {'subu'}, 'not': {'nor'}, 'bal': {'bgezal'}, 'beqzl': {'beql'}, 'bnezl': {'bnel'}, 'neg': {'sub'},
         'dnegu': {'dsubu'}, 'dneg': {'dsub'}, 'nop': {'sll'}, 'dmove': {'daddu', 'or'}, 'ssnop': {'sll'},
         'mul': {'mult'}, 'mtc0': {'mtc0'}, 'sync': {'sync'}}
def norm_ops(s):
    s = s.split('<')[0].replace('$', '').lower().replace('s8', 'fp').replace('c1_fcsr', 'fpccsr').replace('c0_sr', 'status')
    s = re.sub(r'(c0|cop0)?\b(status|\$?12)\b', 'status', s) if False else s
    toks = re.findall(r'-?0x[0-9a-f]+|\b[0-9a-f]{8}\b|-?\d+|[a-z_][a-z0-9._]*', s)
    out = []
    for t in toks:
        if re.match(r'^[0-9a-f]{8}$', t): out.append(int(t, 16))
        elif re.match(r'^(-?0x[0-9a-f]+|-?\d+)$', t): out.append((int(t, 16) if 'x' in t else int(t, 10)) & 0xFFFFFFFF)
        elif t.startswith('l_'): out.append(int(t[2:], 16))
        elif t.startswith('func_') or t.startswith('data_gap_'): out.append(int(t.split('_')[-1], 16))
        else: out.append(t)
    return out
def objdump():
    rows, cur = {}, None
    for ln in open(DIS):
        ln = ln.rstrip()
        m = FUNC.match(ln)
        if m: cur = m.group(2); continue
        m = LINE.match(ln)
        if m and cur: rows[(cur, int(m.group(1), 16))] = (m.group(2), m.group(3))
    return rows
def rabbit():
    rows = {}
    for f in sorted(glob.glob(FUNCS + '/*.c')):
        fn = None
        for l in open(f, errors='replace'):
            m = re.match(r'(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC void (\w+)\(', l)
            if m: fn = m.group(1)
            for m in CMT.finditer(l):
                rows.setdefault((fn, int(m.group(1), 16)), (m.group(2), m.group(3).strip()))
    return rows
def name_map(dis=None):
    """{RecompiledFuncs name: objdump function name} by majority mnemonic agreement over the function's addresses."""
    global DIS
    if dis: DIS = dis
    od, rb = objdump(), rabbit()
    byaddr = collections.defaultdict(list)
    for (fn, a) in od: byaddr[a].append(fn)
    votes = collections.defaultdict(collections.Counter)
    for (fn, a), (rop, rops) in rb.items():
        for ofn in byaddr.get(a, []):
            o = od[(ofn, a)][0]
            votes[fn][ofn] += (o == rop or rop in ALIAS.get(o, ()) or o in ALIAS.get(rop, ()))
    return {fn: (fn if votes[fn].get(fn) == max(votes[fn].values()) else votes[fn].most_common(1)[0][0])
            for fn in votes if votes[fn] and max(votes[fn].values()) > 0}
def main():
    od, rb = objdump(), rabbit()
    byaddr = collections.defaultdict(list)
    for (fn, a) in od: byaddr[a].append(fn)
    cnt, ex, pairs, opdiff, unmatched = collections.Counter(), collections.defaultdict(list), collections.Counter(), collections.Counter(), 0
    # function join by vote: renamed symbols (apply_symbol_renames) and overlays sharing VRAM make (name, addr) ambiguous,
    # so each RecompiledFuncs function maps to the objdump function that agrees on the most mnemonics at its addresses.
    def agree(o, r): return o == r or r in ALIAS.get(o, ()) or o in ALIAS.get(r, ())
    votes = collections.defaultdict(collections.Counter)
    for (fn, a), (rop, rops) in rb.items():
        for ofn in byaddr.get(a, []):
            votes[fn][ofn] += agree(od[(ofn, a)][0], rop)
    fmap = {fn: (fn if fn in votes[fn] and votes[fn][fn] == max(votes[fn].values()) else votes[fn].most_common(1)[0][0])
            for fn in votes if votes[fn]}
    for (fn, a), (rop, rops) in sorted(rb.items(), key=lambda x: (x[0][1], x[0][0] or '')):
        c = byaddr.get(a, [])
        best = max(c, key=lambda o: (votes[fn][o], o == fn)) if c else None
        fb = best != fn and votes[fn][best] * 2 < sum(votes[fn].values())   # minority overlay copy = weak join
        k = (best, a)
        if k not in od:
            unmatched += 1; cnt['NOMATCH'] += 1; ex['NOMATCH'].append((fn, a, rop, rops)); BAD.append(('NOMATCH', fn, None, a, None, rop)); continue
        oop, oops = od[k]
        if oop == rop:
            cnt['SAME'] += 1
            no, nr = norm_ops(oops), norm_ops(rops)
            if rop in ('mfc0', 'mtc0', 'dmfc0', 'dmtc0', 'cfc1', 'ctc1'): no, nr = no[:1], nr[:1]   # cop0/FCSR register naming differs
            if 'reg' in nr and len(nr) == len(no): nr = [o if r == 'reg' else r for o, r in zip(no, nr)]  # N64Recomp `$reg` reloc spelling
            if no != nr and not (rop in ('j', 'jal') ):
                opdiff[rop] += 1
                if len(ex['OPDIFF:' + rop]) < 3: ex['OPDIFF:' + rop].append((fn, a, oops, rops))
        elif oop == '.word':
            BAD.append(('WORD', fn, k[0], a, oop, rop)); cnt['WORD'] += 1; pairs[('.word', rop)] += 1; ex['WORD:' + rop].append((fn, a, oops, rops))
        elif rop in ALIAS.get(oop, ()) or oop in ALIAS.get(rop, ()):
            cnt['ALIAS'] += 1; pairs[(oop, rop)] += 1
        else:
            BAD.append(('DIFF_FALLBACK' if fb else 'DIFF', fn, k[0], a, oop, rop))
            if fb: cnt['DIFF_FALLBACK'] += 1; ex['DIFFFB'].append((fn, k[0], a, oop, rop)); continue
            cnt['DIFF'] += 1; pairs[(oop, rop)] += 1; ex['DIFF:%s/%s' % (oop, rop)].append((fn, a, oops, rops))
    print('[s7419] rabbitizer rows %d, objdump rows %d' % (len(rb), len(od)))
    print('[s7419] classes', dict(cnt))
    print('[s7419] pairs (objdump -> rabbitizer):')
    for (o, r), n in pairs.most_common(): print('   %-10s -> %-10s %6d  %s' % (o, r, n, 'ALIAS' if o != '.word' and (r in ALIAS.get(o, ()) or o in ALIAS.get(r, ())) else ''))
    print('[s7419] same-mnemonic operand mismatches:', dict(opdiff))
    for k in sorted(ex):
        if k.startswith(('WORD', 'DIFF', 'OPDIFF', 'NOMATCH')) and (VERB or not k.startswith('WORD:')):
            print('  ex %s n=%d %s' % (k, len(ex[k]), ex[k][:3]))
    # per-function table of every non-agreeing row in a function that is neither an N64Recomp data_gap filler nor RSP ucode
    tab = collections.defaultdict(collections.Counter); odn = collections.defaultdict(set)
    for cls, fn, ofn, a, oop, rop in BAD:
        if fn is None or fn.startswith('data_gap_') or UCODE.match(fn): continue
        tab[fn][cls] += 1; odn[fn].add(ofn)
    print('[s7419] non-agreeing rows outside data_gap/ucode: %d functions' % len(tab))
    for fn in sorted(tab, key=lambda f: -sum(tab[f].values())):
        print('   %-44s %-40s objdump-as=%s' % (fn, dict(tab[fn]), ','.join(sorted(str(o) for o in odn[fn]))[:120]))
    return cnt, pairs, ex
# reviewed residue: (RecompiledFuncs function, addr) -> reason
REVIEWED = {('setRngSeed', a): 'after setRngSeed `jr ra; nop` + `return;`: rngSeed data word (0 -> nop) and 3 unlabelled words up to '
                                'submitDmaSlot; no L_ label, no branch/jal target in RecompiledFuncs -> unreachable (s7419)'
            for a in (0x80003470, 0x80003474, 0x80003478, 0x8000347C)}
def survivors():
    return [r for r in BAD if r[1] is not None and not r[1].startswith('data_gap_') and not UCODE.match(r[1])
            and (r[1], r[3]) not in REVIEWED]
if __name__ == '__main__':
    if DIS == '/tmp/s7419_canon.dis': __import__('s7419_canon_dis').ensure(DIS)
    cnt, pairs, ex = main()
    sv = survivors()
    print('[s7419] survivors (outside data_gap / ucode / REVIEWED): %d %s' % (len(sv), sv[:6]))
    ok = not sv
    if '--controls' in sys.argv:
        import subprocess, tempfile, io, contextlib
        with tempfile.NamedTemporaryFile('w', suffix='.dis', delete=False) as f:
            subprocess.run(['mips64-elf-objdump', '-d', '--no-show-raw-insn', __import__('s7419_canon_dis').ELF], stdout=f, check=True)
        DIS = f.name; BAD.clear()
        with contextlib.redirect_stdout(io.StringIO()): c2, p2, e2 = main()
        sv2 = survivors(); os.unlink(f.name)
        w = collections.Counter(r[5] for r in sv2 if r[0] == 'WORD')
        hid = sum(1 for r in sv2 if r[0] == 'NOMATCH' and r[1] == 'getTextureAttrBySlot' and 0x800233B0 <= r[3] < 0x80023514)
        cpass = w['ldc1'] > 0 and w['sdc1'] > 0 and w['cache'] > 0 and hid > 0
        print('[s7419] CONTROL plain objdump -d: survivors %d, .word ldc1=%d sdc1=%d cache=%d, hidden texPackTlutAtAllocSlot rows=%d -> %s'
              % (len(sv2), w['ldc1'], w['sdc1'], w['cache'], hid, 'PASS' if cpass else 'FAIL'))
        ok = ok and cpass
    print('[s7419] VERDICT %s' % ('H-clean (canonical listing == rabbitizer on every live instruction)' if not sv else 'H-blind'))
    sys.exit(0 if ok else 1)
