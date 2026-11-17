#!/usr/bin/env python3
"""s7508 class FE: RSP scalar-unit lowering, the two gaps s7093 (tools/s7093_su_census.py) leaves open.

s7093 already proves, for the 3 compiled RSP TUs: ROM word == comment fields on every PRISTINE base record (A), control
flow / cop0 / cop2 (B, C), and host semantics of every distinct LIVE scalar line vs a Python model with the DMEM fast path
on and off (D). Two things it does not do:
  G1 ROM truth for the LIVE composite. The 9 overlay streams spliced into factor5_ucode_recompiled.c (CLIP_/OVL*_ labels)
     exist only in the live file; s7093 decodes their fields from the disassembly comment (from_comment), so a wrong
     comment + matching wrong line would pass D. Here every live record (base, splices, slot copies) is mapped to its
     (stream, IMEM address) - resync on every stream label - and its ROM word is read from the stream's own toml image
     (s7507 load_instrs). Checks: mnemonic + fields == comment; every scalar record's first non-fixup line == the line
     RSPRecomp's CURRENT template (rsp_recomp.cpp process_instruction, re-typed below, incl. the s7093 sltiu U32 cast)
     builds from the ROM fields; zero-destination writes emit nothing (add/addu/and) or are listed (others).
  G2 compile flags. s7093 D builds its harness at -O1. The production gfx TU is -O2 -mllvm -inline-threshold=4000 with a
     link-time-constant DMEM base. D is re-run here with the production flags (the harness and model are s7093's).
Controls: (c1) one ROM word of a spliced stream flipped -> G1 field defect; (c2) one spliced ori imm in the live text
changed -> G1 template defect; (c3) one spliced sra emitted as srl -> template defect; (c4) G2 harness with the s7093
mutants under -O2 must still flag.
Usage: tools/s7508_rsp_scalar_gaps.py   rc 0 = 0 defects + every control fires."""
import os, re, sys, collections, importlib.util, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn)); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m
su = _load('su7093', 's7093_su_census.py')
cf = _load('cf7507', 's7507_rsp_ctrl_flow.py')
ROOT = os.path.join(HERE, '..')
LIVE = os.path.join(ROOT, 'build/factor5_ucode')
SCALAR = su.ALU | set(su.LD) | set(su.ST)
RD_OPS = {'add', 'addu', 'sub', 'subu', 'negu', 'and', 'or', 'xor', 'nor', 'slt', 'sltu', 'sllv', 'srlv', 'srav',
          'sll', 'srl', 'sra'}

def g(n): return 'r%d' % n if n else '0'

def template(d):
    """RSPRecomp process_instruction (current source) for a scalar op, from decoded ROM fields. None = emits nothing."""
    m, rs, rt, rd, sa = d['m'], g(d['rs']), g(d['rt']), g(d['rd']), d['sa']
    ui, si = su.fmt_hash(d['imm'], False), su.fmt_hash(d['imm'], True)
    if m in ('add', 'addu', 'and') and d['rd'] == 0: return None
    t = {'lui': f'{rt} = S32({ui} << 16)',
         'add': f'{rd} = RSP_ADD32({rs}, {rt})', 'addu': f'{rd} = RSP_ADD32({rs}, {rt})',
         'negu': f'{rd} = RSP_SUB32({rs}, {rt})', 'sub': f'{rd} = RSP_SUB32({rs}, {rt})', 'subu': f'{rd} = RSP_SUB32({rs}, {rt})',
         'addi': f'{rt} = RSP_ADD32({rs}, {si})', 'addiu': f'{rt} = RSP_ADD32({rs}, {si})',
         'and': f'{rd} = {rs} & {rt}', 'andi': f'{rt} = {rs} & {ui}', 'or': f'{rd} = {rs} | {rt}', 'ori': f'{rt} = {rs} | {ui}',
         'nor': f'{rd} = ~({rs} | {rt})', 'xor': f'{rd} = {rs} ^ {rt}', 'xori': f'{rt} = {rs} ^ {ui}',
         'sll': f'{rd} = S32({rt}) << {sa}', 'sllv': f'{rd} = S32({rt}) << ({rs} & 31)',
         'sra': f'{rd} = S32(RSP_SIGNED({rt}) >> {sa})', 'srav': f'{rd} = S32(RSP_SIGNED({rt}) >> ({rs} & 31))',
         'srl': f'{rd} = S32(U32({rt}) >> {sa})', 'srlv': f'{rd} = S32(U32({rt}) >> ({rs} & 31))',
         'slt': f'{rd} = RSP_SIGNED({rs}) < RSP_SIGNED({rt}) ? 1 : 0', 'slti': f'{rt} = RSP_SIGNED({rs}) < {si} ? 1 : 0',
         'sltu': f'{rd} = {rs} < {rt} ? 1 : 0',
         'sltiu': f'{rt} = {rs} < {"U32(%s)" % si if su.s16(d["imm"]) < 0 else si} ? 1 : 0',
         'lw': f'{rt} = RSP_MEM_W_LOAD({si}, {rs})', 'lh': f'{rt} = RSP_MEM_H_LOAD({si}, {rs})',
         'lb': f'{rt} = RSP_MEM_B({si}, {rs})', 'lhu': f'{rt} = RSP_MEM_HU_LOAD({si}, {rs})',
         'lbu': f'{rt} = RSP_MEM_BU({si}, {rs})', 'sw': f'RSP_MEM_W_STORE({si}, {rs}, {rt})',
         'sh': f'RSP_MEM_H_STORE({si}, {rs}, {rt})', 'sb': f'RSP_MEM_B({si}, {rs}) = {rt}'}[m]
    return t + ';'

def dest(d):
    if d['m'] in su.ST: return None
    return d['rd'] if d['m'] in RD_OPS else d['rt']

def words_for(fname, cfgs):
    """prefix -> {imem addr: ROM word} for this live file."""
    out = {'L': {x['v']: x['word'] for x in cf.load_instrs(cfgs[fname])}}
    if fname == 'factor5_ucode_recompiled.c':
        for P, f in cf.PREFIX_FILE.items():
            if f: out[P] = {x['v']: x['word'] for x in cf.load_instrs(cfgs['factor5_ucode_%s_recompiled.c' % f])}
    return out

def audit(fname, lines, words, notes):
    segs, _, _ = cf.segments(lines)
    bad = collections.Counter(); info = collections.Counter(); per = collections.Counter()
    P, a = 'L', min(words['L']); copy_next = False; prev_ctrl_addr = None
    for sg in segs:
        labs = [l for l in sg['labels'] if l[0] in cf.PREFIX_FILE and not l[2]]
        if labs and not copy_next:
            P, a = labs[0][0], labs[0][1]
            if P not in words: bad['no-stream'] += 1; notes.append(f'{fname}: label {P} has no ROM stream'); return bad, info, per
        if copy_next: addr, is_copy = prev_ctrl_addr + 4, True
        else: addr, is_copy = a, False
        w = words[P].get(addr)
        if w is None: bad['addr-out-of-image'] += 1; notes.append(f'{fname} {P}_{addr:04X}: no ROM word'); return bad, info, per
        d = su.decode(w); cm = cf.ALIAS.get(sg['mnem'], sg['mnem']) if sg['mnem'] not in ('b',) else 'b'
        dm = d['m']
        info['records'] += 1; info['copies'] += is_copy; info['splice' if P != 'L' else 'base'] += 1
        cmp_m = {'beqz': 'beq', 'bnez': 'bne'}.get(sg['mnem'], sg['mnem'])
        if dm not in ('cop2vec', 'lwc2', 'swc2', '?') and cmp_m != dm and not (cmp_m == 'move' and dm in ('or', 'addu')):
            bad['mnemonic'] += 1; notes.append(f'{fname} {P}_{addr:04X} comment {sg["comment"]!r} rom {dm} {w:08X}')
            return bad, info, per          # alignment lost: stop this file
        if dm in SCALAR:
            ops = sg['comment'].split(None, 2)[2] if len(sg['comment'].split(None, 2)) > 2 else ''
            if not su.same_fields(su.from_comment(dm, ops), d):
                bad['fields'] += 1; notes.append(f'{fname} {P}_{addr:04X} {sg["comment"]!r} != rom {w:08X}')
            want = template(d)
            body = [c for c in sg['code'] if not su.fixup_line(c)]
            got = body[0] if body else None
            if want is None:
                info['zero_dest_blank'] += 1
                if got is not None and not got.startswith('goto ') and got != '}': bad['zero-dest-emitted'] += 1; notes.append(f'{fname} {P}_{addr:04X} {got!r}')
            elif dest(d) == 0:
                info['zero_dest_other'] += 1; notes.append(f'{fname} {P}_{addr:04X} writes $zero: {got!r}')
                if got != want: bad['template'] += 1
            elif got != want:
                bad['template'] += 1; notes.append(f'{fname} {P}_{addr:04X} {dm}: got {got!r} want {want!r}')
            else: per[dm] += 1; info['scalar_ok'] += 1; info['scalar_ok_splice'] += P != 'L'
        ctrl = dm in su.BR or dm in su.JMP
        if is_copy: copy_next = False
        else:
            a += 4
            if ctrl: copy_next, prev_ctrl_addr = True, addr
    return bad, info, per

def run_g1(cfgs, override=None):
    tot = collections.Counter(); notes = []; infos = {}; per = collections.Counter()
    for fname in ('factor5_ucode_recompiled.c', 'factor5_ucode_b_recompiled.c', 'factor5_boot_recompiled.c'):
        lines = (override or {}).get(fname) or open(os.path.join(LIVE, fname)).read().split('\n')
        words = words_for(fname, cfgs)
        if override and '_words' in override and fname == 'factor5_ucode_recompiled.c': override['_words'](words)
        b, i, p = audit(fname, lines, words, notes); tot += b; infos[fname] = i; per += p
    return tot, notes, infos, per

def run_g2(mut=False):
    """s7093 D harness, built with the production gfx-TU flags."""
    orig = su.subprocess.check_call
    def cc(args, *k, **kw):
        if args and args[0] == 'clang++':
            args = [x for x in args if x != '-O1'] + ['-O2', '-mllvm', '-inline-threshold=4000']
        return orig(args, *k, **kw)
    su.subprocess.check_call = cc
    su.OUT = su.ROOT / 'scratch/s7508'; su.OUT.mkdir(parents=True, exist_ok=True)
    try:
        items, _, _, _ = su.live_items()
        syn = [(('mem' if (d['m'] in su.LD or d['m'] in su.ST) else 'alu'), l, d) for l, d in su.synthetic_rsprecomp()]
        c1, b1, _ = su.harness(items, 'live_o2'); c2, b2, _ = su.harness(syn, 'syn_o2')
        def m(kind, line, d):
            if d['m'] == 'sltiu': return re.sub(r'= (r\d+|0) <', r'= RSP_SIGNED(\1) <', line)
            if d['m'] == 'lb': return line.replace('RSP_MEM_B(', 'RSP_MEM_BU(')
            if d['m'] == 'sra': return line.replace('RSP_SIGNED(', 'U32(')
            if d['m'] == 'lh': return line.replace('RSP_MEM_H_LOAD(', 'RSP_MEM_HU_LOAD(')
            return line
        sub = [it for it in items if it[2]['m'] in ('sltiu', 'lb', 'sra', 'lh')]
        fired = collections.Counter(); tot = collections.Counter()
        for it in sub:
            tot[it[2]['m']] += 1; fired[it[2]['m']] += su.harness([it], 'ctl_o2', mutate=m)[1] > 0
        return (c1, b1, c2, b2), {k: f'{fired[k]}/{tot[k]}' for k in tot}, all(fired[k] == tot[k] for k in tot) and tot
    finally:
        su.subprocess.check_call = orig

def main():
    cfgs = cf.tomls()
    bad, notes, infos, per = run_g1(cfgs)
    print('== G1 live composite vs ROM (every record, splices + slot copies) ==')
    for f, i in infos.items():
        print(f'  {f:30s} records={i["records"]} base={i["base"]} splice={i["splice"]} copies={i["copies"]} '
              f'scalar_ok={i["scalar_ok"]} (splice {i["scalar_ok_splice"]}) zero_dest blank={i["zero_dest_blank"]} other={i["zero_dest_other"]}')
    print('  scalar ops checked:', ' '.join(f'{k}={v}' for k, v in sorted(per.items())))
    print('  defects:', dict(bad) or 0)
    for n in notes[:20]: print('   ', n)
    ok = not bad
    print('== G2 s7093 D harness at production flags (-O2, inline-threshold=4000) ==')
    (c1, b1, c2, b2), fired, fired_ok = run_g2()
    print(f'  live cases {c1} bad {b1}; synthetic cases {c2} bad {b2}; mutants flagged {fired}')
    ok &= b1 == 0 and b2 == 0
    print('== controls ==')
    main_lines = open(os.path.join(LIVE, 'factor5_ucode_recompiled.c')).read().split('\n')
    # c1: flip the rt field of the first spliced scalar word (ROM side)
    segs, _, _ = cf.segments(main_lines)
    first = None
    for sg in segs:
        labs = [l for l in sg['labels'] if l[0] != 'L' and l[0] in cf.PREFIX_FILE and not l[2]]
        if labs and sg['mnem'] in ('ori', 'addiu', 'andi'): first = labs[0]; break
    def flip(words): words[first[0]][first[1]] ^= 1 << 16
    c1b, _, _, _ = run_g1(cfgs, {'_words': flip})
    # c2/c3: live-text mutants inside spliced streams
    def text_mut(pat, repl):
        L = list(main_lines); in_splice = False
        for i, l in enumerate(L):
            if re.match(r'^(CLIP|OVL[0-9A-F]+)_[0-9A-F]{4}:', l): in_splice = True
            if in_splice and re.match(r'\s+r\d+ = ' + pat, l):
                L[i] = re.sub(pat, repl, l, count=1); return L
        raise SystemExit('no splice site for ' + pat)
    c2b, _, _, _ = run_g1(cfgs, {'factor5_ucode_recompiled.c': text_mut(r'r\d+ \| 0X([0-9A-F]+);', r'r1 | 0X\g<1>0;')})
    c3b, _, _, _ = run_g1(cfgs, {'factor5_ucode_recompiled.c': text_mut(r'S32\(RSP_SIGNED\((r\d+)\)', r'S32(U32(\1)')})
    res = {'c1_rom_flip_splice': sum(c1b.values()) > sum(bad.values()), 'c2_ori_imm_splice': sum(c2b.values()) > sum(bad.values()),
           'c3_sra_as_srl_splice': sum(c3b.values()) > sum(bad.values()), 'c4_o2_mutants': bool(fired_ok)}
    print(f'  c1 {first} -> {dict(c1b)}; c2 -> {dict(c2b)}; c3 -> {dict(c3b)}; c4 -> {fired}')
    for k, v in res.items(): print(f'  {k}: {"PASS" if v else "FAIL"}')
    ok &= all(res.values())
    print('verdict:', 'PASS (FE H-equal)' if ok else 'FAIL')
    return 0 if ok else 3

if __name__ == '__main__':
    sys.exit(main())
