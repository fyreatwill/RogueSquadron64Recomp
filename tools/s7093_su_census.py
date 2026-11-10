#!/usr/bin/env python3
"""s7093: RSPRecomp SCALAR-unit lowering census for the 3 compiled RSP TUs (main gfx ucode, audio ucode B, boot).

Independent of rabbitizer and of RSPRecomp's templates: every top-level record of the PRISTINE pass is given a vram
(by counting records from the TU's text_address; every L_XXXX label must agree with the count), its retail word is
read from the ROM (toml text_offset), and that word is decoded HERE into (op, rs, rt, rd, sa, imm, e). Then:
  A. mnemonic in the comment == mnemonic decoded from the ROM word (decoder sanity, every record).
  B. control flow: branch/j/jal goto label == target computed from the word; jal link line present; delay slot =
     the next ROM word, emitted inside the taken path before the goto and again as the following top-level record;
     no branch in a delay slot.
  C. cop0: mfc0/mtc0 action matches the decoded cop0 register; cop2 moves carry the decoded element / rd.
  D. semantics: every distinct emitted scalar line (ALU, shifts, set-less-than, loads, stores, branch conditions)
     from the LIVE TUs (fixup-tagged lines dropped) is compiled into a host function with the live rsp.hpp DMEM
     block and run against a Python reference of the decoded instruction (32-bit wrap, sign/zero extension, imm
     sign extension, unaligned + wrapping DMEM byte addressing, shift masks). Synthetic lines built with RSPRecomp's
     own format rules cover boundary immediates with rs = $zero (the literal "0") and rs = a register.
  E. cop2 moves: rsp.MFC2/MTC2<e> for all 16 e and CFC2/CTC2 for rd 0..3 vs a byte-level cxd4 su.c reference.
  F. jal link: RSPRecomp stores 0x1000|(pc+8); hardware stores (pc+8)&0xFFF. Every non-jr reader of $31 is listed
     with its reaching writer so the bit-12 difference can be proven harmless (or not).
Controls (--controls): mutant RSPRecomp shapes (sltiu compared signed, lb zero-extended, sra logical, beq->bne) are
injected into a copy and MUST be flagged; one ROM word corrupted must fail check A.
Usage: s7093_su_census.py [--controls]   (pristine dir: scratch/ucode_regen/pristine, from tools/ucode_regen.sh verify)
Exit 0 iff A-E pass with 0 differences and every control fires.
"""
import collections, os, random, re, struct, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRI = ROOT / 'scratch/ucode_regen/pristine'
LIVE = ROOT / 'build/factor5_ucode'
OUT = ROOT / 'scratch/s7093'
INC = ROOT / 'lib/N64ModernRuntime/librecomp/include/librecomp'
TUS = [('factor5_ucode_recompiled.c', 'rogue_squadron.z64', 0x025610, 0x1080, 0xF80),
       ('factor5_ucode_b_recompiled.c', 'rogue_squadron.z64', 0x09ABE0, 0x1080, 0xF80),
       ('factor5_boot_recompiled.c', 'factor5_boot_text.bin', 0x0, 0x1000, 0xD0)]
CMT = re.compile(r'^(\s*)// ([a-z][a-z0-9.]*)(?: {2,}(\S.*))?$')
LBL = re.compile(r'^([LR])_([0-9A-F]{4})(_delay)?:\s*$')
REGN = {'zero': 0, 'at': 1, 'v0': 2, 'v1': 3, 'a0': 4, 'a1': 5, 'a2': 6, 'a3': 7, 't0': 8, 't1': 9, 't2': 10, 't3': 11,
        't4': 12, 't5': 13, 't6': 14, 't7': 15, 's0': 16, 's1': 17, 's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22,
        's7': 23, 't8': 24, 't9': 25, 'k0': 26, 'k1': 27, 'gp': 28, 'sp': 29, 'fp': 30, 's8': 30, 'ra': 31}
C0 = ['SP_MEM_ADDR', 'SP_DRAM_ADDR', 'SP_RD_LEN', 'SP_WR_LEN', 'SP_STATUS', 'SP_DMA_FULL', 'SP_DMA_BUSY',
      'SP_SEMAPHORE', 'DPC_START', 'DPC_END', 'DPC_CURRENT', 'DPC_STATUS', 'DPC_CLOCK', 'DPC_BUFBUSY',
      'DPC_PIPEBUSY', 'DPC_TMEM']
C0_READ = {4: '0', 5: '0', 6: '0', 7: '0', 9: 'RSP_DPC_END_READ()', 10: 'RSP_DPC_CURRENT_READ()',
           11: 'RSP_DPC_STATUS_READ()', 12: 'RSP_DPC_CLOCK_READ()', 13: 'RSP_DPC_BUFBUSY_READ()',
           14: 'RSP_DPC_PIPEBUSY_READ()', 15: 'RSP_DPC_TMEM_READ()'}
C0_WRITE = {7: '', 4: '', 1: 'SET_DMA_DRAM', 0: 'SET_DMA_MEM', 2: 'DO_DMA_READ', 3: 'DO_DMA_WRITE',
            8: 'RSP_DPC_START', 9: 'RSP_DPC_END', 11: 'RSP_DPC_STATUS_WRITE'}
# (tu, vram) -> (emitted goto in the pristine pass, tag that the live fixup must carry). PORTING-STATE s5428-s5455:
# the wrap to IMEM 0x000 is the ucode's self-restart; fixup_factor5_ucode.py turns it into a goto to the entry.
EXPLAINED_TARGET = {('factor5_ucode_recompiled.c', 0x1FF0): ('goto L_0000;', 'fixup: L_0000 self-restart')}
BR = {'beq', 'bne', 'bgez', 'bgtz', 'blez', 'bltz', 'b'}
JMP = {'j', 'jal', 'jr', 'jalr'}
ALU = {'add', 'addu', 'sub', 'subu', 'negu', 'and', 'or', 'xor', 'nor', 'slt', 'sltu', 'sllv', 'srlv', 'srav', 'sll',
       'srl', 'sra', 'addi', 'addiu', 'andi', 'ori', 'xori', 'slti', 'sltiu', 'lui'}
LD = {'lb': (1, 1), 'lbu': (1, 0), 'lh': (2, 1), 'lhu': (2, 0), 'lw': (4, 0)}
ST = {'sb': 1, 'sh': 2, 'sw': 4}
M32 = 0xFFFFFFFF


def s16(x): x &= 0xFFFF; return x - 0x10000 if x & 0x8000 else x
def s32(x): x &= M32; return x - (1 << 32) if x & 0x80000000 else x


# ---------------------------------------------------------------- independent decoder (ROM word -> instruction)
def decode(w):
    op, rs, rt, rd, sa, fn, imm = w >> 26, (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31, (w >> 6) & 31, w & 63, w & 0xFFFF
    d = dict(w=w, rs=rs, rt=rt, rd=rd, sa=sa, imm=imm, e=(w >> 7) & 15)
    if w == 0: return dict(d, m='nop')
    if op == 0:
        m = {0: 'sll', 2: 'srl', 3: 'sra', 4: 'sllv', 6: 'srlv', 7: 'srav', 8: 'jr', 9: 'jalr', 13: 'break', 32: 'add',
             33: 'addu', 34: 'sub', 35: 'subu', 36: 'and', 37: 'or', 38: 'xor', 39: 'nor', 42: 'slt', 43: 'sltu'}.get(fn, '?')
        if m == 'subu' and rs == 0: m = 'negu'
        return dict(d, m=m)
    if op == 1: return dict(d, m={0: 'bltz', 1: 'bgez', 16: 'bltzal', 17: 'bgezal'}.get(rt, '?'))
    if op in (2, 3): return dict(d, m='j' if op == 2 else 'jal', tgt=(w & 0x3FFFFFF) << 2)
    m = {4: 'beq', 5: 'bne', 6: 'blez', 7: 'bgtz', 8: 'addi', 9: 'addiu', 10: 'slti', 11: 'sltiu', 12: 'andi',
         13: 'ori', 14: 'xori', 15: 'lui', 32: 'lb', 33: 'lh', 35: 'lw', 36: 'lbu', 37: 'lhu', 40: 'sb', 41: 'sh',
         43: 'sw'}.get(op)
    if m == 'beq' and rs == 0 and rt == 0: m = 'b'
    if m: return dict(d, m=m)
    if op == 16: return dict(d, m={0: 'mfc0', 4: 'mtc0'}.get(rs, '?'))
    if op == 18:
        if rs & 16: return dict(d, m='cop2vec')
        return dict(d, m={0: 'mfc2', 2: 'cfc2', 4: 'mtc2', 6: 'ctc2'}.get(rs, '?'))
    if op in (50, 58): return dict(d, m='lwc2' if op == 50 else 'swc2')
    return dict(d, m='?')


# ---------------------------------------------------------------- record parser
def parse(text):
    """Records in file order: dict(ind, m, ops, lines, delay, top, vram). Delay copies are the record right after a
    branch/jump record (state machine); top-level records get consecutive vrams."""
    L = text.split('\n'); recs = []; labels = []
    cur = None
    for i, l in enumerate(L):
        m = CMT.match(l)
        if m and (m.group(3) is None or len(m.group(2)) <= 11):
            cur = dict(ind=len(m.group(1)), m=m.group(2), ops=m.group(3) or '', lines=[], li=i, labels=list(labels))
            labels = []; recs.append(cur); continue
        lm = LBL.match(l)
        if lm: labels.append((lm.group(1), int(lm.group(2), 16), bool(lm.group(3)))); cur = None; continue
        if l.startswith('do_indirect_jump') or l.startswith('do_overlay_swap'): break
        if cur is not None and l.strip():
            cur['lines'].append(l.strip())
    pend = False
    for r in recs:
        r['delay'] = pend
        pend = (not pend) and (r['m'] in BR or r['m'] in JMP)
    return recs


def regs(ops):
    out = []
    for t in re.findall(r'\$([a-z0-9]+)', ops):
        out.append(int(t) if t.isdigit() else REGN.get(t, -1))
    return out


def fixup_line(s): return 'fixup' in s or re.search(r'\brs64_|\bs\d{4}\b', s) is not None


# ---------------------------------------------------------------- reference semantics of a decoded instruction
def ref_alu(d, R):
    m, rs, rt, rd, sa, imm = d['m'], R[d['rs']], R[d['rt']], d['rd'], d['sa'], d['imm']
    si = s16(imm) & M32
    f = {'add': lambda: (rs + rt), 'addu': lambda: (rs + rt), 'sub': lambda: (rs - rt), 'subu': lambda: (rs - rt),
         'negu': lambda: -rt, 'and': lambda: rs & rt, 'or': lambda: rs | rt, 'xor': lambda: rs ^ rt,
         'nor': lambda: ~(rs | rt), 'slt': lambda: int(s32(rs) < s32(rt)), 'sltu': lambda: int(rs < rt),
         'sllv': lambda: rt << (rs & 31), 'srlv': lambda: rt >> (rs & 31), 'srav': lambda: s32(rt) >> (rs & 31),
         'sll': lambda: rt << sa, 'srl': lambda: rt >> sa, 'sra': lambda: s32(rt) >> sa,
         'addi': lambda: rs + si, 'addiu': lambda: rs + si, 'andi': lambda: rs & imm, 'ori': lambda: rs | imm,
         'xori': lambda: rs ^ imm, 'slti': lambda: int(s32(rs) < s16(imm)), 'sltiu': lambda: int(rs < si),
         'lui': lambda: imm << 16}[m]
    dst = rd if m in ('add', 'addu', 'sub', 'subu', 'negu', 'and', 'or', 'xor', 'nor', 'slt', 'sltu', 'sllv', 'srlv',
                      'srav', 'sll', 'srl', 'sra') else d['rt']
    out = list(R)
    if dst: out[dst] = f() & M32
    return out, {}


def ref_mem(d, R, dm):
    m = d['m']; a = (R[d['rs']] + s16(d['imm'])) & 0xFFF; out = list(R); wr = {}
    if m in LD:
        n, sg = LD[m]; v = 0
        for i in range(n): v = (v << 8) | dm[(a + i) & 0xFFF]
        if sg and v >> (8 * n - 1): v -= 1 << (8 * n)
        if d['rt']: out[d['rt']] = v & M32
    else:
        n = ST[m]; v = R[d['rt']]
        for i in range(n): wr[(a + i) & 0xFFF] = (v >> (8 * (n - 1 - i))) & 0xFF
    return out, wr


def ref_cond(d, R):
    m, a, b = d['m'], R[d['rs']], R[d['rt']]
    return int({'beq': a == b, 'bne': a != b, 'bgez': s32(a) >= 0, 'bgtz': s32(a) > 0, 'blez': s32(a) <= 0,
                'bltz': s32(a) < 0, 'b': True}[m])


def from_comment(m, ops):
    """Decode a live record's disassembly text (used only for spliced overlay records without a ROM mapping; its
    agreement with the ROM decoder is checked on every pristine record first)."""
    r = regs(ops); nums = re.findall(r'(?<![$\w])(-?0x[0-9A-Fa-f]+|-?\d+)(?![\w])', re.sub(r'\$[a-z0-9]+', '', ops))
    d = dict(m=m, rs=0, rt=0, rd=0, sa=0, imm=0)
    if m in ('add', 'addu', 'sub', 'subu', 'and', 'or', 'xor', 'nor', 'slt', 'sltu'): d.update(rd=r[0], rs=r[1], rt=r[2])
    elif m == 'negu': d.update(rd=r[0], rt=r[1])
    elif m in ('sllv', 'srlv', 'srav'): d.update(rd=r[0], rt=r[1], rs=r[2])
    elif m in ('sll', 'srl', 'sra'): d.update(rd=r[0], rt=r[1], sa=int(nums[-1], 0))
    elif m in ('addi', 'addiu', 'andi', 'ori', 'xori', 'slti', 'sltiu'): d.update(rt=r[0], rs=r[1], imm=int(nums[-1], 0) & 0xFFFF)
    elif m == 'lui': d.update(rt=r[0], imm=int(nums[-1], 0) & 0xFFFF)
    elif m in LD or m in ST: d.update(rt=r[0], rs=r[1], imm=int(nums[0], 0) & 0xFFFF)
    elif m in ('beq', 'bne'): d.update(rs=r[0], rt=r[1])
    elif m in ('bgez', 'bgtz', 'blez', 'bltz'): d.update(rs=r[0])
    return d


def same_fields(a, b):
    m = a['m']
    keys = {'negu': ('rd', 'rt'), 'lui': ('rt', 'imm'), 'bgez': ('rs',), 'bgtz': ('rs',), 'blez': ('rs',), 'bltz': ('rs',),
            'beq': ('rs', 'rt'), 'bne': ('rs', 'rt'), 'b': ()}.get(m)
    if keys is None:
        if m in ('sll', 'srl', 'sra'): keys = ('rd', 'rt', 'sa')
        elif m in ('sllv', 'srlv', 'srav') or m in ('add', 'addu', 'sub', 'subu', 'and', 'or', 'xor', 'nor', 'slt', 'sltu'): keys = ('rd', 'rs', 'rt')
        else: keys = ('rt', 'rs', 'imm')
    return all(a[k] == b[k] for k in keys)


# ---------------------------------------------------------------- A/B/C/F on the pristine pass
def structural(tus, rom_override=None):
    bad = collections.Counter(); notes = []; per = collections.Counter(); r31 = []
    for name, rom, off, base, size in tus:
        text = (PRI / name).read_text(); recs = parse(text)
        data = rom_override if rom_override is not None and name == tus[0][0] else (ROOT / rom).read_bytes()
        top = [r for r in recs if not r['delay']]
        for k, r in enumerate(top):
            r['vram'] = base + 4 * k
            for kind, a, _ in r['labels']:
                if a != r['vram']: bad['label-vram'] += 1; notes.append(f'{name} label {kind}_{a:04X} at counted vram {r["vram"]:04X}')
        if len(top) * 4 != size: bad['record-count'] += 1; notes.append(f'{name}: {len(top)} top-level records, text size {size // 4}')
        for k, r in enumerate(top):
            w = struct.unpack('>I', data[off + 4 * k: off + 4 * k + 4])[0]
            d = decode(w); r['d'] = d
            cm = r['m']
            dm = d['m'] if d['m'] != 'cop2vec' and d['m'] not in ('lwc2', 'swc2') else None
            if dm is not None and dm != cm: bad['A-mnemonic'] += 1; notes.append(f'{name} {r["vram"]:04X} comment {cm} rom {dm} {w:08X}'); continue
            per[cm] += 1
            if cm in ALU or cm in LD or cm in ST or cm in ('beq', 'bne', 'bgez', 'bgtz', 'blez', 'bltz'):
                if not same_fields(from_comment(cm, r['ops']), d): bad['A-fields'] += 1; notes.append(f'{name} {r["vram"]:04X} {cm} {r["ops"]} != rom {w:08X}')
        # B: control flow + delay slots
        idx = {id(r): i for i, r in enumerate(recs)}
        for k, r in enumerate(top):
            d = r['d']; m = d['m']; v = r['vram']
            if m in BR or m in JMP:
                i = idx[id(r)]; ds = recs[i + 1] if i + 1 < len(recs) else None
                nxt = top[k + 1] if k + 1 < len(top) else None
                if ds is None or not ds['delay'] or nxt is None or (ds['m'], ds['ops']) != (nxt['m'], nxt['ops']):
                    bad['B-delay-identity'] += 1; notes.append(f'{name} {v:04X} {m}: delay copy != next word'); continue
                if nxt['m'] in BR or nxt['m'] in JMP: bad['B-branch-in-delay'] += 1; notes.append(f'{name} {v:04X} branch in delay slot')
                if m in BR:
                    tgt = 0x1000 | ((v + 4 + (s16(d['imm']) << 2)) & 0xFFF)
                elif m in ('j', 'jal'):
                    tgt = 0x1000 | (d['tgt'] & 0xFFF)
                else:
                    tgt = None
                if m in BR and m != 'b':
                    if not r['lines'] or not r['lines'][0].startswith('if ('): bad['B-cond-shape'] += 1; continue
                    gl = [l for l in ds['lines'] if l.startswith('goto ')]
                    if (name, v) in EXPLAINED_TARGET and gl[-1:] == [EXPLAINED_TARGET[(name, v)][0]] and \
                            EXPLAINED_TARGET[(name, v)][1] in (LIVE / name).read_text():
                        notes.append(f'{name} {v:04X} {m}: hardware target {tgt:04X} (PC wraps past IMEM end), emitted '
                                     f'{gl[-1]} -> EXPLAINED: {EXPLAINED_TARGET[(name, v)][1]} (live fixup)'); per['explained-target'] += 1
                    elif not gl or gl[-1] != f'goto L_{tgt:04X};': bad['B-target'] += 1; notes.append(f'{name} {v:04X} {m} expect goto L_{tgt:04X} got {gl[-1:]}')
                    if ds['ind'] <= r['ind']: bad['B-delay-not-inside'] += 1
                else:
                    gl = [l for l in ds['lines'] if l.startswith('goto ')]
                    want = f'goto L_{tgt:04X};' if tgt is not None else 'goto do_indirect_jump;'
                    if not gl or gl[-1] != want: bad['B-target'] += 1; notes.append(f'{name} {v:04X} {m} expect {want} got {gl[-1:]}')
                    if m == 'jal' and r['lines'] != [f'r31 = 0x{v + 8:04X};']: bad['B-jal-link'] += 1; notes.append(f'{name} {v:04X} jal link {r["lines"]}')
                    if m == 'jr' and r['lines'][:1] != [f'jump_target = r{d["rs"]};' if d['rs'] else 'jump_target = 0;']:
                        bad['B-jr'] += 1; notes.append(f'{name} {v:04X} jr {r["lines"]}')
            # C: cop0 / cop2 moves
            if m == 'mfc0':
                want = f'r{d["rt"]} = {C0_READ.get(d["rd"], "?")};'
                if r['lines'][:1] != [want]: bad['C-mfc0'] += 1; notes.append(f'{name} {v:04X} mfc0 {C0[d["rd"]]}: {r["lines"][:1]} want {want}')
                per[f'mfc0:{C0[d["rd"]]}'] += 1
            if m == 'mtc0':
                act = C0_WRITE.get(d['rd'], '?'); per[f'mtc0:{C0[d["rd"]]}'] += 1
                src = f'r{d["rt"]}' if d['rt'] else '0'
                ok = (act == '' and r['lines'][:1] in ([], [f'({src});'], [f'{src};'])) or any(l.startswith(f'{act}({src})') for l in r['lines'])
                if not ok: bad['C-mtc0'] += 1; notes.append(f'{name} {v:04X} mtc0 {C0[d["rd"]]}: {r["lines"][:2]}')
            if m in ('mfc2', 'mtc2'):
                want = f'rsp.{m.upper()}<{d["e"]}>(r{d["rt"]}, rsp.vpu.r[{d["rd"]}]);'
                per[f'{m}:e{d["e"]}'] += 1
                if r['lines'][:1] != [want]: bad['C-cop2'] += 1; notes.append(f'{name} {v:04X} {m}: {r["lines"][:1]} want {want}')
            if m in ('cfc2', 'ctc2'):
                want = f'rsp.{m.upper()}(r{d["rt"]}, {d["rd"]});'; per[f'{m}:rd{d["rd"]}'] += 1
                if r['lines'][:1] != [want]: bad['C-cop2'] += 1; notes.append(f'{name} {v:04X} {m}: {r["lines"][:1]} want {want}')
        # F: readers of $31 other than jr, with the reaching writer (straight-line back-scan, stops at a label)
        for k, r in enumerate(top):
            d = r['d']; m = d['m']
            reads = set()
            if m in ALU and m not in ('lui',):
                reads = {d['rs'], d['rt']} if m not in ('sll', 'srl', 'sra', 'negu') else {d['rt']}
                if m in ('addi', 'addiu', 'andi', 'ori', 'xori', 'slti', 'sltiu'): reads = {d['rs']}
            elif m in LD: reads = {d['rs']}
            elif m in ST: reads = {d['rs'], d['rt']}
            elif m in ('beq', 'bne'): reads = {d['rs'], d['rt']}
            elif m in ('bgez', 'bgtz', 'blez', 'bltz'): reads = {d['rs']}
            elif m in ('mtc2', 'ctc2', 'mtc0'): reads = {d['rt']}
            elif m in ('lwc2', 'swc2', 'cop2vec'): reads = {d['rs']} if m != 'cop2vec' else set()
            if 31 not in reads: continue
            wr = 'label/entry'
            for j in range(k - 1, -1, -1):
                p = top[j]; pd = p['d']; pm = pd['m']
                dst = None
                if pm == 'jal': dst = 31
                elif pm in ALU: dst = pd['rd'] if pm in ('add', 'addu', 'sub', 'subu', 'negu', 'and', 'or', 'xor', 'nor', 'slt', 'sltu', 'sllv', 'srlv', 'srav', 'sll', 'srl', 'sra') else pd['rt']
                elif pm in LD or pm in ('mfc0', 'mfc2', 'cfc2'): dst = pd['rt']
                if dst == 31: wr = f'{pm} {p["ops"]} @{p["vram"]:04X}'; break
                if top[j]['labels']: wr = f'label above {p["vram"]:04X}'; break
            r31.append((name, r['vram'], m, r['ops'], wr))
    return bad, notes, per, r31


# ---------------------------------------------------------------- D: host semantics harness
SPECIAL = [0, 1, 2, 31, 32, 33, 0x7FFF, 0x8000, 0xFFFF, 0x10000, 0x7FFFFFFF, 0x80000000, 0x80000001, 0xFFFFFFFF,
           0xFFFFFFFE, 0xFFFF8000, 0xFFFF7FFF, 0x00008001]


def fmt_hash(v, signed):  # fmt "{:#X}" of uint16 / int16, as RSPRecomp prints it
    if signed: v = s16(v)
    return ('-' if v < 0 else '') + ('0X%X' % abs(v))


def emit_template(d):
    """PRE-s7093 RSPRecomp scalar template (rsp_recomp.cpp 407-507), re-typed: the positive control for the sltiu fix."""
    g = lambda n: f'r{n}' if n else '0'
    m, rs, rt, rd, sa = d['m'], g(d['rs']), g(d['rt']), g(d['rd']), d['sa']
    ui, si = fmt_hash(d['imm'], False), fmt_hash(d['imm'], True)
    t = {'lui': f'{g(d["rt"])} = S32({ui} << 16)', 'addiu': f'{g(d["rt"])} = RSP_ADD32({rs}, {si})',
         'andi': f'{g(d["rt"])} = {rs} & {ui}', 'ori': f'{g(d["rt"])} = {rs} | {ui}', 'xori': f'{g(d["rt"])} = {rs} ^ {ui}',
         'slti': f'{g(d["rt"])} = RSP_SIGNED({rs}) < {si} ? 1 : 0', 'sltiu': f'{g(d["rt"])} = {rs} < {si} ? 1 : 0',
         'sltu': f'{rd} = {rs} < {rt} ? 1 : 0', 'slt': f'{rd} = RSP_SIGNED({rs}) < RSP_SIGNED({rt}) ? 1 : 0',
         'sll': f'{rd} = S32({rt}) << {sa}', 'srl': f'{rd} = S32(U32({rt}) >> {sa})', 'sra': f'{rd} = S32(RSP_SIGNED({rt}) >> {sa})',
         'lb': f'{g(d["rt"])} = RSP_MEM_B({si}, {rs})', 'lbu': f'{g(d["rt"])} = RSP_MEM_BU({si}, {rs})',
         'lh': f'{g(d["rt"])} = RSP_MEM_H_LOAD({si}, {rs})', 'lhu': f'{g(d["rt"])} = RSP_MEM_HU_LOAD({si}, {rs})',
         'lw': f'{g(d["rt"])} = RSP_MEM_W_LOAD({si}, {rs})', 'sw': f'RSP_MEM_W_STORE({si}, {rs}, {rt})',
         'sh': f'RSP_MEM_H_STORE({si}, {rs}, {rt})', 'sb': f'RSP_MEM_B({si}, {rs}) = {rt}'}[m]
    return t + ';'


def synthetic():
    out = []
    imms = sorted({0, 1, 2, 3, 0x7F, 0x80, 0xFF, 0x100, 0x7FFE, 0x7FFF, 0x8000, 0x8001, 0xFFFE, 0xFFFF, 0xF000, 0x0FFF,
                   0xFFC, 0xFFD, 0x1000, 0xEFFF} | set(random.Random(7093).sample(range(0x10000), 40)))
    for m in ('addiu', 'andi', 'ori', 'xori', 'slti', 'sltiu', 'lui'):
        for imm in imms:
            for rs in ((0,) if m == 'lui' else (0, 5)):   # lui has no rs field
                out.append(dict(m=m, rs=rs, rt=7, rd=0, sa=0, imm=imm))
    for m in ('sltu', 'slt'):
        for rs, rt in ((0, 6), (5, 0), (5, 6)): out.append(dict(m=m, rs=rs, rt=rt, rd=7, sa=0, imm=0))
    for m in ('sll', 'srl', 'sra'):
        for sa in range(32): out.append(dict(m=m, rs=0, rt=6, rd=7, sa=sa, imm=0))
    for m in list(LD) + list(ST):
        for imm in (0, 1, 2, 3, 0xFFF, 0xFFE, 0xFFD, 0x1000, 0xFFFF, 0xFFFE, 0xFFFD, 0x8000, 0x7FFF):
            for rs in (0, 5): out.append(dict(m=m, rs=rs, rt=7, rd=0, sa=0, imm=imm))
    return [(emit_template(d), d) for d in out]


OPC = {'addiu': 9, 'slti': 10, 'sltiu': 11, 'andi': 12, 'ori': 13, 'xori': 14, 'lui': 15, 'lb': 32, 'lh': 33, 'lw': 35,
       'lbu': 36, 'lhu': 37, 'sb': 40, 'sh': 41, 'sw': 43}
FN = {'sll': 0, 'srl': 2, 'sra': 3, 'slt': 42, 'sltu': 43}


def encode(d):
    if d['m'] in OPC: return (OPC[d['m']] << 26) | (d['rs'] << 21) | (d['rt'] << 16) | d['imm']
    return (d['rs'] << 21) | (d['rt'] << 16) | (d['rd'] << 11) | (d['sa'] << 6) | FN[d['m']]


def synthetic_rsprecomp():
    """Assemble the synthetic instructions into blobs, run the REAL RSPRecomp binary on them, return its lines."""
    exe = Path(os.environ.get('RSPRECOMP', ROOT.parent / 'N64Recomp/build/RSPRecomp'))
    ds = [d for _, d in synthetic()]; out = []
    OUT.mkdir(parents=True, exist_ok=True)
    for c in range(0, len(ds), 900):
        chunk = ds[c:c + 900]; tag = f'syn{c // 900}'
        blob = OUT / f'{tag}.bin'
        blob.write_bytes(b''.join(struct.pack('>I', encode(d)) for d in chunk) + struct.pack('>I', 0x0000000D))
        toml = OUT / f'{tag}.toml'
        toml.write_text(f'rom_file_path = "{blob}"\ntext_offset = 0x0\ntext_size = 0x{4 * (len(chunk) + 1):X}\n'
                        f'text_address = 0x04001000\noutput_file_path = "{OUT}/{tag}.c"\noutput_function_name = "{tag}"\n'
                        f'extra_indirect_branch_targets = []\n')
        r = subprocess.run([str(exe), str(toml)], capture_output=True, text=True, cwd=OUT)
        if r.returncode: raise SystemExit(f'RSPRecomp failed on {tag}: {r.stdout[-300:]} {r.stderr[-500:]}')
        recs = [x for x in parse((OUT / f'{tag}.c').read_text()) if x['m'] != 'break']
        if len(recs) != len(chunk): raise SystemExit(f'{tag}: {len(recs)} records for {len(chunk)} words')
        for x, d in zip(recs, chunk):
            if x['m'] != d['m'] or not x['lines']: raise SystemExit(f'{tag}: record {x["m"]} {x["lines"]} for {d}')
            out.append((x['lines'][0], d))
    return out


def harness(items, tag, mutate=None):
    """items: list of (kind, emitted_line, decoded). kind: alu|mem|cond. Returns (cases, bad, examples)."""
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(0x7093)
    dm = bytes(rng.randrange(256) for _ in range(0x1000))
    fns = []; vecs = []
    for n, (kind, line, d) in enumerate(items):
        if mutate: line = mutate(kind, line, d)
        decl = 'uint32_t ' + ', '.join(f'r{i} = R[{i}]' for i in range(1, 32)) + ';'
        back = ' '.join(f'R[{i}] = r{i};' for i in range(1, 32))
        if kind == 'cond':
            fns.append(f'static void F{n}(uint32_t* R){{ {decl} int c = 0; {line} c = 1; }} R[0] = c; }}')
        else:
            fns.append(f'static void F{n}(uint32_t* R){{ {decl} {line} {back} }}')
        vs = []
        for j in range(40):
            R = [0] + [rng.choice(SPECIAL) if rng.random() < 0.4 else rng.getrandbits(32) for _ in range(31)]
            vs.append(R)
        if kind == 'mem':  # force every wrap/unaligned edge through the base register
            for a in (0xFFC, 0xFFD, 0xFFE, 0xFFF, 0x000, 0x001, 0x002, 0x003, 0x7FF, 0x800):
                R = [0] + [rng.getrandbits(32) for _ in range(31)]
                if d['rs']: R[d['rs']] = (a - s16(d['imm']) + (rng.randrange(16) << 12)) & M32
                if d['rt'] == d['rs'] and kind == 'mem' and d['m'] in ST: pass
                vs.append(R)
        if kind == 'cond':
            for j in range(8):  # equal-operand cases for beq/bne
                R = [0] + [rng.getrandbits(32) for _ in range(31)]
                if d['rs']: R[d['rt']] = R[d['rs']] if d['rt'] else 0;
                if d['rs'] and not d['rt']: R[d['rs']] = 0 if j < 4 else R[d['rs']]
                vs.append(R)
        vecs.append(vs)
    src = OUT / f'h_{tag}.cpp'
    hdr = f'''#include <cstdint>
#include <cstdio>
#include <cstring>
static uint8_t g_dm[0x2000];
#define RS64_DMEM_BASE g_dm
extern "C" int rs64_g1e_dmem; int rs64_g1e_dmem = 1;
#define RS64_RSP_HOOKS_GATE rs64_rsp_hooks_on
extern "C" int rs64_rsp_hooks_on; int rs64_rsp_hooks_on = 0;
extern "C" void rs64_m5_audio_dmem_store(uint32_t, uint32_t, uint32_t, uint32_t) {{}}
#define S32(val) ((int32_t)(val))
#define U32(val) ((uint32_t)(val))
#include "dmem_block.inc"
'''
    body = '\n'.join(fns)
    tab = 'static void (*T[])(uint32_t*) = {' + ','.join(f'F{n}' for n in range(len(fns))) + '};'
    main = r'''
int main(int argc, char** argv) {
  static uint8_t img[0x1000]; FILE* f = fopen(argv[1], "rb"); fread(img, 1, 0x1000, f);
  int dmode = atoi(argv[3]); rs64_g1e_dmem = dmode;
  uint32_t nf, nv; fread(&nf, 4, 1, f); FILE* o = fopen(argv[2], "wb");
  for (uint32_t k = 0; k < nf; k++) { fread(&nv, 4, 1, f);
    for (uint32_t j = 0; j < nv; j++) { uint32_t R[32]; fread(R, 4, 32, f);
      for (int a = 0; a < 0x1000; a++) g_dm[a ^ 3] = img[a];
      T[k](R); fwrite(R, 4, 32, o);
      uint32_t nd = 0, dl[8][2];
      for (int a = 0; a < 0x1000; a++) if (g_dm[a ^ 3] != img[a] && nd < 8) { dl[nd][0] = a; dl[nd][1] = g_dm[a ^ 3]; nd++; }
      for (int a = 0x1000; a < 0x2000; a++) if (g_dm[a]) { if (nd < 8) { dl[nd][0] = a; dl[nd][1] = g_dm[a]; nd++; } g_dm[a] = 0; }
      fwrite(&nd, 4, 1, o); fwrite(dl, 8, nd, o); } }
  fclose(o); return 0; }
'''
    src.write_text(hdr + body + '\n' + tab + '\n#include <cstdlib>\n' + main)
    blk = []
    on = h = False
    for l in (INC / 'rsp.hpp').read_text().split('\n'):
        if l.startswith('#define RSP_MEM_B(offset'): on = True
        if on and l.startswith('#define SET_DMA_MEM'): break   # DMEM block + RSP_ADD32/SUB32/SIGNED, verbatim
        if on: blk.append(l)
    (OUT / 'dmem_block.inc').write_text('\n'.join(blk) + '\n')
    exe = OUT / f'h_{tag}'
    subprocess.check_call(['clang++', '-std=c++20', '-O1', '-w', f'-I{OUT}', str(src), '-o', str(exe)])
    vin = OUT / f'v_{tag}.bin'
    with open(vin, 'wb') as f:
        f.write(dm); f.write(struct.pack('<I', len(vecs)))
        for vs in vecs:
            f.write(struct.pack('<I', len(vs)))
            for R in vs: f.write(struct.pack('<32I', *R))
    cases = bad = 0; ex = []
    for dmode in (1, 0):  # fast DMEM path and byte loops
        vout = OUT / f'o_{tag}_{dmode}.bin'
        subprocess.check_call([str(exe), str(vin), str(vout), str(dmode)])
        raw = vout.read_bytes(); p = 0
        for n, (kind, line, d) in enumerate(items):
            for R in vecs[n]:
                got = list(struct.unpack_from('<32I', raw, p)); p += 128
                nd = struct.unpack_from('<I', raw, p)[0]; p += 4
                wr = {}
                for _ in range(nd): a, v = struct.unpack_from('<II', raw, p); p += 8; wr[a] = v
                if kind == 'cond':
                    exp = ref_cond(d, R); ok = got[0] == exp
                    gotv, expv = got[0], exp
                else:
                    er, ew = ref_mem(d, R, dm) if kind == 'mem' else ref_alu(d, R)
                    er = list(er); er[0] = got[0] = 0
                    ew = {a: v for a, v in ew.items() if dm[a] != v}
                    ok = got == er and wr == ew
                    gotv, expv = (got, wr), (er, ew)
                cases += 1
                if not ok:
                    bad += 1
                    if len(ex) < 12:
                        diff = [i for i in range(32) if kind != 'cond' and got[i] != expv[0][i]]
                        ex.append(f'dmem={dmode} {d["m"]} `{line}` regs-in ' +
                                  ' '.join(f'r{i}={R[i]:08X}' for i in sorted({d["rs"], d["rt"]}) if i) +
                                  (f' got r{diff[0]}={got[diff[0]]:08X} want {expv[0][diff[0]]:08X}' if diff else f' got {gotv} want {expv}' if kind == 'cond' else f' writes got {wr} want {expv[1]}'))
    return cases, bad, ex


# ---------------------------------------------------------------- E: cop2 moves vs byte-level cxd4 reference
COP2_SRC = r'''
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include "rsp_vu.hpp"
static uint8_t g_dm[0x2000];
#define RS64_DMEM_BASE g_dm
extern "C" int rs64_g1e_dmem; int rs64_g1e_dmem = 1;
#define RS64_RSP_HOOKS_GATE rs64_rsp_hooks_on
extern "C" int rs64_rsp_hooks_on; int rs64_rsp_hooks_on = 0;
extern "C" void rs64_m5_audio_dmem_store(uint32_t, uint32_t, uint32_t, uint32_t) {}
extern "C" void rs64_m5_audio_dmem_vector_store(uint32_t, uint32_t, uint32_t) {}
extern "C" void rs64_spike_sdv_note(uint32_t, uint32_t, const uint32_t*) {}
extern "C" int rs64_sdv_snap_enabled(void) { return 0; }
extern "C" int rs64_vu_ring_enabled(void) { return 0; }
extern "C" void rs64_vld_note(uint32_t, uint32_t, const char*) {}
extern "C" void rs64_vu_ring_vte(uint32_t, const uint16_t*) {}
extern "C" uint32_t rs64_vu_ring_prev_vd(void) { return 0; }
extern "C" void rs64_vu_ring_capture_prev(const uint16_t*) {}
extern "C" void rs64_vu_ring_push(uint32_t, uint32_t, uint32_t, const uint16_t*) {}
#include "dmem_block.inc"
uint16_t rspReciprocals[512], rspInverseSquareRoots[512];
#include "rsp_vu_impl.hpp"
static uint64_t s = 0x7093;
static uint32_t rnd() { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return (uint32_t)s; }
static RSP R; static long bad = 0, n = 0;
static void chk(bool ok, const char* w, int e, uint32_t a, uint32_t b) { n++; if (!ok && bad++ < 10) printf("BAD %s e=%d got %08X want %08X\n", w, e, a, b); }
template<int E> static void one() {
  for (int it = 0; it < 4096; it++) {
    uint8_t B[16]; for (int i = 0; i < 16; i++) B[i] = rnd();          // reference: vector reg as 16 big-endian bytes
    for (int i = 0; i < 16; i++) R.vpu.r[3].byte(i) = B[i];
    uint32_t rt = rnd(); R.MFC2<E>(rt, R.vpu.r[3]);
    uint32_t want = (uint32_t)(int32_t)(int16_t)((B[E] << 8) | B[(E + 1) & 15]);   // cxd4 su.c MFC2
    chk(rt == want, "MFC2", E, rt, want);
    uint32_t v = MUT_MTC2(rnd()); R.MTC2<E>(v, R.vpu.r[3]);
    B[E] = v >> 8; if (E != 15) B[E + 1] = v;                            // cxd4 MTC2 (e=15: byte 16 is outside vr)
    for (int i = 0; i < 16; i++) chk(R.vpu.r[3].byte(i) == B[i], "MTC2", E, R.vpu.r[3].byte(i), B[i]);
  }
}
template<int... E> static void all(std::integer_sequence<int, E...>) { (one<E>(), ...); }
int main() {
  all(std::make_integer_sequence<int, 16>{});
  for (int rd = 0; rd < 4; rd++) for (int it = 0; it < 65536; it++) {
    uint32_t v = (it & 0xFFFF) | (rnd() & 0xFFFF0000u);
    R.CTC2(v, rd); uint32_t got; R.CFC2(got, rd);
    uint32_t keep = rd >= 2 ? 0xFF : 0xFFFF;                             // VCE is 8 bits (cxd4 rwR_VCE / rwW_VCE)
    uint32_t want = (uint32_t)(int32_t)(int16_t)(v & keep);
    chk(got == want, "CTC2>CFC2", rd, got, want);
    // lane check: bit n of the low byte = lane n flag (cxd4 get_VCO/get_VCC: lo bits 0-7, hi bits 8-15)
    const RSP::r128& lo = rd == 0 ? R.vpu.vcol : rd == 1 ? R.vpu.vccl : R.vpu.vce;
    for (int l = 0; l < 8; l++) chk(lo.get(l) == (bool)(v >> l & 1), "lane", rd, lo.get(l), v >> l & 1);
  }
  printf("cop2 cases %ld bad %ld\n", n, bad); return bad != 0; }
'''


def cop2_test(mut=False):
    OUT.mkdir(parents=True, exist_ok=True)
    for f in ('rsp_vu.hpp', 'rsp_vu_impl.hpp'): (OUT / f).write_text((INC / f).read_text())
    src = OUT / 'cop2.cpp'; src.write_text(COP2_SRC.replace('MUT_MTC2(rnd())', 'rnd()'))
    hdr = (OUT / 'rsp_vu.hpp').read_text()
    if 'VCOL' not in hdr.split('struct VU')[0] and '#define VCOL' not in hdr:
        pass
    exe = OUT / ('cop2_mut' if mut else 'cop2')
    impl = OUT / 'rsp_vu_impl.hpp'
    if mut:  # positive control: MFC2 without the e+1 wrap
        t = impl.read_text(); t2 = t.replace('auto lo = vs.byte(e + 1 & 15);', 'auto lo = vs.byte(e + 1 & 7);')
        assert t2 != t, 'cop2 mutant did not apply'; impl.write_text(t2)
    r = subprocess.run(['clang++', '-std=c++20', '-O2', '-w', f'-I{OUT}', f'-I{ROOT}/lib/N64ModernRuntime/thirdparty/sse2neon',
                        str(src), '-o', str(exe)], capture_output=True, text=True)
    if r.returncode: print(r.stderr[:3000]); return None
    p = subprocess.run([str(exe)], capture_output=True, text=True)
    if mut: impl.write_text((INC / 'rsp_vu_impl.hpp').read_text())
    return p.returncode, p.stdout.strip().split('\n')[-1], p.stdout.strip().split('\n')[:3]


# ---------------------------------------------------------------- D input: distinct live lines
def live_items():
    items = {}; clash = []; per = collections.Counter(); shapes = collections.defaultdict(collections.Counter)
    for name, *_ in TUS:
        for r in parse((LIVE / name).read_text()):
            m = r['m']
            if not (m in ALU or m in LD or m in ST or m in ('beq', 'bne', 'bgez', 'bgtz', 'blez', 'bltz')): continue
            ls = [l for l in r['lines'] if not fixup_line(l)]
            if not ls: continue
            d = from_comment(m, r['ops'])
            if m in ('beq', 'bne', 'bgez', 'bgtz', 'blez', 'bltz'):
                if not ls[0].startswith('if (') or not ls[0].endswith('{'): continue
                line, kind = ls[0], 'cond'
            else:
                line, kind = ls[0], ('mem' if (m in LD or m in ST) else 'alu')
                dst = d['rd'] if kind == 'alu' and m not in ('addi', 'addiu', 'andi', 'ori', 'xori', 'slti', 'sltiu', 'lui') else d['rt']
                if dst == 0 and m not in ST:  # write to $zero: RSPRecomp emits no line (or a blank)
                    per['zero-dest'] += 1; continue
            per[m] += 1
            shapes[m][re.sub(r'\b0X[0-9A-F]+\b', 'IMM', re.sub(r'\br\d+\b', 'R', line))] += 1
            key = line
            if key in items and items[key][2] != d and not same_fields(items[key][2], d):
                clash.append((line, items[key][2], d))
            items.setdefault(key, (kind, line, d))
    return list(items.values()), per, shapes, clash


def main():
    controls = '--controls' in sys.argv
    if not (PRI / TUS[0][0]).exists():
        print('pristine pass missing: run zsh tools/ucode_regen.sh verify'); return 2
    bad, notes, per, r31 = structural(TUS)
    print('== A/B/C structural (pristine pass, ROM-decoded) ==')
    print('records per mnemonic:', ', '.join(f'{k}={v}' for k, v in sorted(per.items()) if ':' not in k))
    print('cop0/cop2 forms:', ', '.join(f'{k}={v}' for k, v in sorted(per.items()) if ':' in k))
    print('defects:', dict(bad) or 0)
    for n in notes[:30]: print('  ', n)
    print('== F: $31 readers other than jr (reaching writer) ==')
    for t in r31: print('  %s %04X %-6s %-22s <- %s' % t)
    items, lper, shapes, clash = live_items()
    print('== D: live distinct scalar lines ==', len(items), 'from', sum(v for k, v in lper.items() if k != 'zero-dest'),
          'records;', lper['zero-dest'], 'zero-dest records')
    multi = {m: s for m, s in shapes.items() if len(s) > 1}
    for m, s in sorted(shapes.items()): print(f'  {m:6s} shapes={len(s)} ' + ' | '.join(f'{k} x{v}' for k, v in s.most_common(3)))
    print('  same line, different decoded fields:', len(clash))
    kind = lambda d: 'mem' if (d['m'] in LD or d['m'] in ST) else 'alu'
    syn = [(kind(d), l, d) for l, d in synthetic_rsprecomp()]
    c1, b1, e1 = harness(items, 'live'); print(f'  live lines: cases {c1} bad {b1}'); [print('   ', x) for x in e1]
    c2, b2, e2 = harness(syn, 'syn'); print(f'  synthetic lines from the RSPRecomp binary: {len(syn)} lines, cases {c2} bad {b2}'); [print('   ', x) for x in e2]
    rc = cop2_test(); print('== E: cop2 moves ==', rc[1] if rc else 'BUILD FAILED')
    ok = not bad and not clash and b1 == 0 and b2 == 0 and rc and rc[0] == 0
    if controls:
        print('== controls ==')
        rom = bytearray((ROOT / 'rogue_squadron.z64').read_bytes())
        k = 0x025610 + 4 * 37; rom[k + 1] ^= 0x01  # flip one rt/rs bit of one main-ucode word
        cb, _, _, _ = structural(TUS[:1], rom_override=bytes(rom))
        print('  corrupted ROM word -> structural defects:', dict(cb), 'FIRES' if cb else 'DID NOT FIRE')
        def mut(kind, line, d):
            m = d['m']
            if m == 'sltiu': return re.sub(r'= (r\d+|0) <', r'= RSP_SIGNED(\1) <', line)
            if m == 'lb': return line.replace('RSP_MEM_B(', 'RSP_MEM_BU(')
            if m == 'sra': return line.replace('RSP_SIGNED(', 'U32(')
            if m == 'beq': return line.replace(' == ', ' != ')
            if m == 'sllv': return line.replace('& 31', '& 15')
            return line
        sub = [it for it in items if it[2]['m'] in ('sltiu', 'lb', 'sra', 'beq', 'sllv')]
        fired = {}
        for it in sub:
            c, b, _ = harness([it], 'ctl', mutate=mut); fired[it[2]['m']] = fired.get(it[2]['m'], 0) + (b > 0)
        tot = collections.Counter(it[2]['m'] for it in sub)
        print('  mutant shapes flagged (sites flagged / distinct lines):', {m: f'{fired[m]}/{tot[m]}' for m in tot})
        old = [(kind(d), l, d) for l, d in synthetic()]   # pre-s7093 RSPRecomp template (sltiu imm not U32-cast)
        c3, b3, e3 = harness(old, 'syn_old')
        print(f'  pre-s7093 sltiu template on the synthetic set: bad {b3} (must be > 0)'); [print('   ', x) for x in e3[:2]]
        rcm = cop2_test(mut=True); print('  cop2 MFC2 wrap mutant:', rcm[1] if rcm else 'build failed')
        ctl_ok = b3 > 0 and bool(cb) and all(fired.get(m, 0) > 0 for m in tot) and rcm and rcm[0] != 0
        print('  controls', 'PASS' if ctl_ok else 'FAIL'); ok = ok and ctl_ok
    print('verdict:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
