#!/usr/bin/env python3
"""s7507 class FD: RSPRecomp control-flow emission audit (the BZ / s7416 audit, for the RSP side).
RSPRecomp (../N64Recomp/RSPRecomp/src/rsp_recomp.cpp process_instruction) lowers, for an instruction at V with slot V+4:
  bcc:  if (COND) {  <slot copy, 8-space indent>  goto L_T; }   <linear slot V+4>
  j/b:  <slot copy> goto L_T;                                     <linear slot, dead unless labelled>
  jal:  r31 = 0xV+8; <slot copy> goto L_T;
  jr:   jump_target = rS; debug_file = ...; <slot copy> goto do_indirect_jump;
  jalr: jump_target = rS; rD = 0xV+8; ...
do_indirect_jump: switch ((jump_target | 0x1000) & 0x1FFF) { case X: goto L_X; ... }
The ucode is decoded INDEPENDENTLY here from the toml's ROM image (big-endian words), not from the C comments.
Checks per file:
 R1 conditional branches: COND text == expected for op/regs (rN are uint32_t; RSP_SIGNED = int32 cast), COND emitted
    before the slot (branch segment holds only the `if`), copy target == decoded target, label defined, slot copy ==
    linear slot code.
 R2 jal: `r31 = 0xV+8` before the slot; return address in the indirect switch; target label defined.
 R3 jr/jalr: jump_target latched before the slot (flag a slot that writes rS anyway - it must still be latched);
    jalr rd==rs listed; every switch case has a label; jr sites by register (ra vs table-driven).
 R4 branch/jump in a delay slot; mtc0 SP_RD_LEN (overlay-swap resume) in a slot; R_ resume labels.
 R5 COND forms compiled with cc against rsp.hpp's RSP_SIGNED and driven with 32-bit edge values vs a model.
 R6 positive controls: mutated copies (slot before cond, wrong copy target, diverging copy, unsigned bgez, jr latch
    after slot, wrong jal ra, dropped switch case) must each add >=1 defect.
Alignment control: every decoded control op must sit under a comment with a matching mnemonic and every non-control
op under a non-control comment; any misalignment is a defect.
Usage: tools/s7507_rsp_ctrl_flow.py [dir ...]   (default: build/factor5_ucode and scratch/ucode_regen/pristine)
rc 0 = 0 defects + all controls PASS, rc 3 otherwise."""
import os, re, sys, struct, subprocess, tempfile, glob, random, collections
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
MASK = 0x1FFF
CTRL = {'beq', 'bne', 'bgez', 'bltz', 'bgtz', 'blez', 'j', 'jal', 'jr', 'jalr', 'bltzal', 'bgezal'}
ALIAS = {'b': 'beq', 'beqz': 'beq', 'bnez': 'bne', 'bal': 'bgezal'}

def tomls():
    out = {}
    for t in glob.glob(os.path.join(ROOT, 'factor5*rsp*.toml')):
        kv = {}
        for line in open(t):
            m = re.match(r'\s*(\w+)\s*=\s*("([^"]*)"|0x[0-9A-Fa-f]+|\d+)', line)
            if m: kv[m.group(1)] = m.group(3) if m.group(3) is not None else int(m.group(2), 0)
        kv['_toml'] = t; out[os.path.basename(kv['output_file_path'])] = kv
    return out

def gpr(r): return 'r%d' % r if r else '0'

def decode(word, v):
    op = word >> 26; rs = (word >> 21) & 31; rt = (word >> 16) & 31; rd = (word >> 11) & 31
    imm = word & 0xFFFF; simm = imm - 0x10000 if imm & 0x8000 else imm
    bt = (v + 4 + (simm << 2)) & MASK
    d = dict(op='other', rs=rs, rt=rt, rd=rd, v=v, word=word)
    if op == 0 and (word & 63) == 8: d.update(op='jr')
    elif op == 0 and (word & 63) == 9: d.update(op='jalr')
    elif op == 0 and (word & 63) == 13: d.update(op='break')
    elif op == 1: d.update(op={0: 'bltz', 1: 'bgez', 0x10: 'bltzal', 0x11: 'bgezal'}.get(rt, 'regimm?'), t=bt)
    elif op == 2: d.update(op='j', t=(word << 2) & MASK)
    elif op == 3: d.update(op='jal', t=(word << 2) & MASK)
    elif op in (4, 5, 6, 7): d.update(op=['beq', 'bne', 'blez', 'bgtz'][op - 4], t=bt)
    elif op == 16 and rs == 4: d.update(cop0w=rd)       # mtc0
    # gpr written by this instruction (for the jr/slot hazard listing)
    w = None
    if op == 0 and (word & 63) not in (8, 13, 12) and word != 0: w = rd
    elif op in (8, 9, 10, 11, 12, 13, 14, 15, 32, 33, 35, 36, 37): w = rt
    elif op == 16 and rs == 0: w = rt                    # mfc0
    elif op == 18 and rs in (0, 2): w = rt               # mfc2/cfc2
    elif op == 3: w = 31
    elif op == 0 and (word & 63) == 9: w = rd
    d['w'] = w
    return d

def expected_cond(d):
    s, t = gpr(d['rs']), gpr(d['rt'])
    return {'beq': 'if (%s == %s) {' % (s, t), 'bne': 'if (%s != %s) {' % (s, t),
            'bgez': 'if (RSP_SIGNED(%s) >= 0) {' % s, 'bltz': 'if (RSP_SIGNED(%s) < 0) {' % s,
            'bgtz': 'if (RSP_SIGNED(%s) > 0) {' % s, 'blez': 'if (RSP_SIGNED(%s) <= 0) {' % s}[d['op']]

def load_instrs(cfg):
    rom = os.path.join(ROOT, cfg['rom_file_path'])
    data = open(rom, 'rb').read()[cfg['text_offset']:cfg['text_offset'] + cfg['text_size']]
    base = cfg['text_address'] & MASK
    return [decode(struct.unpack('>I', data[i:i + 4])[0], (base + i) & MASK) for i in range(0, len(data) - 3, 4)]

LABEL = re.compile(r'^([A-Z][A-Z0-9]*)_([0-9A-F]{4})(_delay)?:')
PREFIX_FILE = {'L': None, 'CLIP': 'ovl4', 'OVL10': 'ovl10', 'OVL12': 'ovl12', 'OVL14': 'ovl14', 'OVL18': 'ovl18',
               'OVL1C': 'ovl1c', 'OVL20': 'ovl20', 'OVL24': 'ovl24', 'OVL2C': 'ovl2c'}

def segments(lines):
    """-> (segs, labels, cases). seg = dict(comment, mnem, code[list], pre[list], labels[list], line).
    Code after a label and before the next comment is the next instruction's `pre` (patch hooks at a label)."""
    try: start = next(i for i, l in enumerate(lines) if l.strip() == 'RSP rsp{};') + 1
    except StopIteration: start = 0
    end = next((i for i, l in enumerate(lines) if l.startswith('do_indirect_jump:')), len(lines))
    segs, pend, pre, labels, after_label = [], [], [], set(), False
    for i in range(start, end):
        l = lines[i]
        m = LABEL.match(l)
        if m:
            pend.append((m.group(1), int(m.group(2), 16), bool(m.group(3)))); labels.add(l.split(':')[0]); after_label = True; continue
        m = re.match(r'^(\s*)// (\S+)', l)
        if m:
            segs.append(dict(comment=l.strip(), mnem=m.group(2), code=[], pre=pre, labels=pend, line=i + 1))
            pend, pre, after_label = [], [], False; continue
        if l.strip():
            if after_label or not segs: pre.append(l.strip())
            else: segs[-1]['code'].append(l.strip())
    # switch: case groups (empty bodies fall through to the next body)
    cases, group, body = {}, [], []
    def flush():
        txt = ' '.join(body)
        if re.sub(r'/\*.*?\*/', '', txt).strip():
            for c in group: cases[c] = txt
            group.clear()
        body.clear()
    for l in lines[end:]:
        if 'Unhandled jump target' in l: break
        m = re.match(r'\s*case 0x([0-9A-F]{4}):(.*)', l)
        if m:
            if group and re.sub(r'/\*.*?\*/', '', ' '.join(body)).strip(): flush()
            else: body.clear()
            group.append(int(m.group(1), 16)); body.append(m.group(2)); continue
        if group: body.append(l.strip())
    flush()
    return segs, labels, cases

def norm(code): return [c for c in code if 'fixup' not in c]
COMPILED = {'factor5_ucode_recompiled.c', 'factor5_ucode_b_recompiled.c', 'factor5_boot_recompiled.c'}  # CMakeLists.txt
CONDOPS = ('beq', 'bne', 'bgez', 'bltz', 'bgtz', 'blez')

def window(dec, a, n=64):
    """word list from a to the first unconditional exit (j/jr/jalr/break) + its slot."""
    out = []
    while a in dec and len(out) < n:
        out.append(dec[a]['word'])
        if dec[a]['op'] in ('j', 'jr', 'jalr', 'break') or (dec[a]['op'] == 'beq' and dec[a]['rs'] == 0 == dec[a]['rt']):
            if a + 4 in dec: out.append(dec[a + 4]['word'])
            break
        a += 4
    return out

class Auditor:
    def __init__(s, name, lines, decs):
        s.name, s.decs = name, decs            # decs: prefix -> {addr: decoded}
        s.segs, s.labels, s.cases = segments(lines)
        s.defects, s.info = [], collections.Counter()
        s.jr_other, s.jal_returns, s.exits_to_base = [], [], set()
        s.copies = {}; s._reg = {}

    def bad(s, P, a, msg): s.defects.append('%s %s_%04X: %s' % (s.name, P, a, msg))

    def target_ok(s, P, t, txt):
        """goto text for target t from prefix P. Returns error or None."""
        m = re.match(r'goto (\w+);$', txt)
        if not m: return 'no goto in %r' % txt
        lab = m.group(1)
        if t == 0 and lab == 'RS64_UCODE_ENTRY': s.info['imem_wrap_restart'] += 1; return None   # s-era L_0000 fixup
        if lab not in s.labels and not (t == 0 and lab == 'L_0000'): return 'label %s undefined' % lab
        if t == 0 and lab == 'L_0000': s.info['imem_wrap_undefined'] += 1; return None   # never compiled (ovl ref files)
        if lab == '%s_%04X' % (P, t): return None
        if P != 'L' and lab == 'L_%04X' % t: s.exits_to_base.add((P, t)); return None
        q = lab.rsplit('_', 1)[0]
        if P != 'L' and q in s.decs and t not in s.region(P) and t in s.region(q):
            s.info['cross_resident'] += 1; return None     # P's DMA did not cover t: Q's image is what is resident
        return 'goto %s != %s_%04X' % (lab, P, t)

    def region(s, P):
        if P not in s._reg:
            base = s.decs['L0'] if 'L0' in s.decs else s.decs['L']
            s._reg[P] = {a for a, d in s.decs[P].items() if a in base and d['word'] != base[a]['word']}
        return s._reg[P]

    def walk(s, k, P, a, stop):
        """audit instructions of prefix P from address a, starting at segment k, until segment `stop` or a new stream."""
        dec = s.decs[P]
        while k < stop and a in dec:
            sg = s.segs[k]
            if k and any(l[0] != P or l[1] != a for l in sg['labels'] if l[0] in PREFIX_FILE and not l[2]) and \
                    not any(l[0] == P and l[1] == a for l in sg['labels']):
                return k                        # a new spliced stream starts here
            d = dec[a]; k += 1
            mn = ALIAS.get(sg['mnem'], sg['mnem'])
            if (d['op'] in CTRL) != (mn in CTRL) or (d['op'] in CTRL and mn != d['op']):
                s.bad(P, a, 'alignment: decoded %s, comment %r' % (d['op'], sg['comment'])); return None
            code = norm(sg['code'])
            if (P, a) in s.copies and s.copies.pop((P, a)) != code:
                s.bad(P, a, 'slot copy != linear %r' % code)
            if d['op'] not in CTRL:
                if d['op'] == 'break' and 'return RspExitReason::Broke;' not in code: s.bad(P, a, 'break not lowered')
                a += 4; continue
            if d['op'] in ('bltzal', 'bgezal'): s.bad(P, a, 'linking regimm branch'); a += 4; continue
            slot = dec.get(a + 4)
            if slot is None or k >= len(s.segs): a += 4; continue
            if slot['op'] in CTRL: s.info['slot_ctrl'] += 1; s.bad(P, a, 'control op in delay slot')
            if slot.get('cop0w') == 2: s.info['slot_dma'] += 1
            sc = s.segs[k]; k += 1
            if sc['labels'] or sc['pre']: s.bad(P, a, 'label/pre inside slot copy')
            nxt = s.segs[k]['comment'] if k < len(s.segs) else None
            uncond = d['op'] in ('j', 'jr') or (d['op'] == 'beq' and d['rs'] == 0 == d['rt'])
            trimmed = False
            if sc['comment'] != nxt:
                newstream = k < len(s.segs) and any(l[0] in PREFIX_FILE and l[0] != 'L' for l in s.segs[k]['labels'])
                if P != 'L' and uncond and newstream and '%s_%04X' % (P, a + 4) not in s.labels and (a + 4) not in s.cases:
                    s.info['trimmed_dead_slot'] += 1; trimmed = True
                else: s.bad(P, a, 'slot copy comment %r != linear %r' % (sc['comment'], nxt))
            cc = norm(sc['code']); op = d['op']
            if any('fixup: L_0000 self-restart' in c for c in sc['code']) and d.get('t') == 0:
                # s-era restart fixup: the taken copy is <slot>, restart logging, goto RS64_UCODE_ENTRY. Keep the
                # slot body (lines before the marker) and the final goto; the logging block between is ours.
                mk = next(j for j, c in enumerate(sc['code']) if 'fixup: L_0000 self-restart' in c)
                cc = norm(sc['code'][:mk]) + [c for c in sc['code'][mk:] if c.startswith('goto ') or c == '}'][-2:]
                s.info['restart_fixup_copy'] += 1
            uncond_b = op == 'beq' and d['rs'] == 0 == d['rt']
            if op in CONDOPS and not uncond_b:
                s.info['cond'] += 1
                if code != [expected_cond(d)]: s.bad(P, a, 'branch segment %r != [%r]' % (code, expected_cond(d)))
                if cc[-1:] != ['}']: s.bad(P, a, 'copy not closed %r' % cc[-1:])
                e = s.target_ok(P, d['t'], cc[-2] if len(cc) > 1 else '')
                if e: s.bad(P, a, e)
                body = cc[:-2]
            elif op in ('j', 'jal') or uncond_b:
                s.info['b' if uncond_b else op] += 1
                pre = ['r31 = 0x%04X;' % ((a + 8) & 0xFFFF)] if op == 'jal' else []
                if code != pre: s.bad(P, a, '%s segment %r != %r' % (op, code, pre))
                e = s.target_ok(P, d['t'], cc[-1] if cc else '')
                if e: s.bad(P, a, e)
                body = cc[:-1]
                if op == 'jal': s.jal_returns.append((P, a + 8))
            else:
                s.info['jr'] += 1
                if op == 'jr':
                    pre = ['jump_target = %s;' % gpr(d['rs'])]
                    if d['rs'] == 31: s.info['jr_ra'] += 1
                    else: s.jr_other.append('%s_%04X:r%d' % (P, a, d['rs']))
                else:
                    pre = [re.sub(r'\s+', ' ', 'jump_target = %s; %s = 0x%8X;' % (gpr(d['rs']), gpr(d['rd']), a + 8))]
                    if d['rd'] == d['rs']: s.info['jalr_rdrs'] += 1
                    code = [re.sub(r'\s+', ' ', c) for c in code]
                    s.jal_returns.append((P, a + 8))
                pre.append('debug_file = __FILE__; debug_line = __LINE__;')
                if code != pre: s.bad(P, a, 'jr segment %r != %r' % (code, pre))
                if slot.get('w') == d['rs'] and d['rs']: s.info['slot_writes_jr'] += 1
                if cc[-1:] != ['goto do_indirect_jump;']: s.bad(P, a, 'copy tail %r' % cc[-1:])
                body = cc[:-1]
            if trimmed: return k
            s.copies[(P, a + 4)] = body
            a += 4
        return k

    def run(s, base_addr):
        k = s.walk(0, 'L', base_addr, len(s.segs))
        if k is None: return
        while k < len(s.segs):                   # spliced overlay streams (live composite only)
            labs = [l for l in s.segs[k]['labels'] if l[0] in PREFIX_FILE and l[0] != 'L' and not l[2]]
            if not labs:
                s.defects.append('%s: unlabelled code after the base stream at C line %d' % (s.name, s.segs[k]['line'])); return
            P, a = labs[0][0], labs[0][1]
            if P not in s.decs: s.defects.append('%s: no decode for %s' % (s.name, P)); return
            s.info['splice_streams'] += 1
            k2 = s.walk(k, P, a, len(s.segs))
            if k2 is None: return
            if k2 == k: s.defects.append('%s: stuck at %s_%04X' % (s.name, P, a)); return
            k = k2
        for (P, a) in s.copies: s.bad(P, a, 'slot copy never matched a linear copy')
def cond_semantics():
    """R5: compile each COND form with rsp.hpp's RSP_SIGNED and compare to a 32-bit model on edge values."""
    hdr = open(os.path.join(ROOT, 'lib/N64ModernRuntime/librecomp/include/librecomp/rsp.hpp')).read()
    m = re.search(r'#define RSP_SIGNED\(val\)\s*\\\s*\n\s*(.*)', hdr)
    vals = [0, 1, 2, 0x7FFFFFFF, 0x80000000, 0x80000001, 0xFFFFFFFF, 0xFFFFFFFE, 0x12345678]
    forms = {'beq': ('a == b', lambda a, b: a == b), 'bne': ('a != b', lambda a, b: a != b),
             'bgez': ('RSP_SIGNED(a) >= 0', lambda a, b: a < 0x80000000), 'bltz': ('RSP_SIGNED(a) < 0', lambda a, b: a >= 0x80000000),
             'bgtz': ('RSP_SIGNED(a) > 0', lambda a, b: 0 < a < 0x80000000), 'blez': ('RSP_SIGNED(a) <= 0', lambda a, b: a == 0 or a >= 0x80000000)}
    def run(fs):
        src = '#include <stdio.h>\n#include <stdint.h>\n#define RSP_SIGNED(val) %s\nint main(void){uint32_t v[]={%s};\n' % (
            m.group(1), ','.join('0x%XU' % x for x in vals))
        src += 'for(int i=0;i<%d;i++)for(int j=0;j<%d;j++){uint32_t a=v[i],b=v[j];printf("%s\\n",%s);}return 0;}\n' % (
            len(vals), len(vals), '%d' * len(fs), ','.join('(int)(%s)' % f for f in fs))
        with tempfile.TemporaryDirectory() as td:
            c = os.path.join(td, 'c.c'); open(c, 'w').write(src)
            subprocess.check_call(['cc', '-O0', '-o', os.path.join(td, 'c'), c])
            return subprocess.check_output([os.path.join(td, 'c')]).decode().split()
    names = list(forms)
    out = run([forms[n][0] for n in names]); bad = 0; idx = 0
    for a in vals:
        for b in vals:
            for j, n in enumerate(names):
                if (out[idx][j] == '1') != forms[n][1](a, b): bad += 1
            idx += 1
    mut = run(['(a) >= 0', '(int32_t)a == (int32_t)b + 1', '(a) > 0'])   # unsigned bgez / off-by-one beq / unsigned bgtz
    idx = 0; mbad = [0, 0, 0]
    for a in vals:
        for b in vals:
            for j, f in enumerate([forms['bgez'][1], forms['beq'][1], forms['bgtz'][1]]):
                if (mut[idx][j] == '1') != f(a, b): mbad[j] += 1
            idx += 1
    return bad, mbad

def mutate(lines, kind):
    L = list(lines); r = random.Random(7)
    if kind == 'switch_drop':
        i = next(i for i, l in enumerate(L) if re.match(r'\s*case 0x1090: goto L_1090;', l)); del L[i]; return L
    if kind == 'splice_target':
        i = next(i for i, l in enumerate(L) if l.startswith('CLIP_'))
        j = next(j for j in range(i, len(L)) if re.match(r'\s*goto CLIP_[0-9A-F]{4};', L[j]))
        L[j] = re.sub(r'CLIP_([0-9A-F]{4})', lambda m: 'CLIP_%04X' % (int(m.group(1), 16) ^ 0), L[j]).replace('goto CLIP_', 'goto L_'); return L
    segs, _, _ = segments(L)
    for si, s in enumerate(segs):
        c = norm(s['code'])
        if kind in ('slot_before', 'wrong_target', 'copy_diverge', 'unsigned') and len(c) == 1 and c[0].startswith('if (') \
                and (kind != 'unsigned' or 'RSP_SIGNED' in c[0]) and len(norm(segs[si + 1]['code'])) >= 3:
            li = s['line'] - 1
            ifl = next(j for j in range(li, li + 4) if L[j].strip().startswith('if ('))
            if kind == 'unsigned': L[ifl] = L[ifl].replace('RSP_SIGNED(', '(')
            elif kind == 'slot_before':
                body = segs[si + 1]['code'][0]; L.insert(ifl, '    ' + body)
            elif kind == 'wrong_target':
                j = next(j for j in range(ifl, ifl + 40) if 'goto L_' in L[j]); L[j] = re.sub(r'L_([0-9A-F]{4})', 'L_0000', L[j])
            else:
                j = segs[si + 1]['line']; L[j] = L[j].rstrip(';') + ' + 1;'
            return L
        if kind == 'jr_late' and c and c[0].startswith('jump_target = '):
            li = s['line']
            j = next(j for j in range(li, li + 40) if 'goto do_indirect_jump' in L[j])
            moved = L.pop(li); L.insert(j - 1, moved); return L
        if kind == 'jal_ra' and c and c[0].startswith('r31 = 0x'):
            L[s['line']] = L[s['line']].replace('r31 = 0x', 'r31 = 0x1'); return L
    raise SystemExit('control %s: no site to mutate' % kind)

def route_checks(au, cfg, decs):
    """switch-case coverage: base jal returns / toml extras -> L_x; spliced jal returns -> P_x; overlay routes and
    splice exits into base code must land on identical code."""
    base = decs['L']
    for P, r in au.jal_returns:
        body = au.cases.get(r)
        if body is None: au.bad(P, r - 8, 'return %04X has no switch case' % r); continue
        if 'goto %s_%04X;' % (P, r) in body: continue
        if P != 'L' and 'goto L_%04X;' % r in body and window(base, r) == window(decs[P], r): continue
        au.bad(P, r - 8, 'return case %04X does not reach %s_%04X: %s' % (r, P, r, body[:120]))
    for t in cfg.get('extra', []):
        body = au.cases.get(t, '')
        if 'goto L_%04X;' % t not in body and not ('rs64_clip_stray' in body):
            au.defects.append('%s: extra target %04X case %r' % (au.name, t, body[:100]))
    for t, body in au.cases.items():
        for lab in re.findall(r'goto (\w+);', body):
            if lab not in au.labels and lab not in ('rs64_clip_stray',): au.defects.append('%s: case %04X -> undefined %s' % (au.name, t, lab))
        for b, P, x in re.findall(r'RSP_MEM_BU\(0X153, 0\) == 0x([0-9A-F]+)\) \{[^}]*?goto (\w+?)_([0-9A-F]{4});', body):
            au.info['ovl_routes'] += 1
            fb = 'ovl%x' % int(b, 16); pf = PREFIX_FILE.get(P)
            if fb != pf and fb in decs.get('_files', {}):
                fP = [q for q, f in PREFIX_FILE.items() if f == fb][0]
                if int(x, 16) not in au.region(fP): au.info['cross_resident_routes'] += 1
                elif window(decs['_files'][fb], int(x, 16)) != window(decs[P], int(x, 16)):
                    au.defects.append('%s: byte %s routed to %s_%s but %s code differs there' % (au.name, b, P, x, fb))
                else: au.info['cross_routes_equal'] += 1
    for P, t in sorted(au.exits_to_base):
        if window(base, t) != window(decs[P], t): au.bad(P, t, 'splice exit to base L_%04X lands on different code' % t)
        else: au.info['base_exits_equal'] += 1

def extras(path):
    txt = open(path).read(); m = re.search(r'extra_indirect_branch_targets\s*=\s*\[(.*?)\]', txt, re.S)
    return [int(x, 16) for x in re.findall(r'0x[0-9A-Fa-f]+', re.sub(r'#.*', '', m.group(1)))] if m else []

def audit_file(path, cfgs, lines=None):
    b = os.path.basename(path); cfg = dict(cfgs[b])
    cfg['extra'] = [t & MASK for t in extras(cfg['_toml'])]
    lst = load_instrs(cfg); decs = {'L': {d['v']: d for d in lst}, '_files': {}}
    if b == 'factor5_ucode_recompiled.c':
        for P, f in PREFIX_FILE.items():
            if f: decs[P] = {d['v']: d for d in load_instrs(cfgs['factor5_ucode_%s_recompiled.c' % f])}; decs['_files'][f] = decs[P]
    au = Auditor(b.replace('_recompiled.c', ''), lines if lines is not None else open(path).read().split('\n'), decs)
    au.run(lst[0]['v']); route_checks(au, cfg, decs)
    return au, len(lst)

def main():
    dirs = sys.argv[1:] or [os.path.join(ROOT, 'build/factor5_ucode'), os.path.join(ROOT, 'scratch/ucode_regen/pristine')]
    cfgs = tomls(); total = 0; rc = 0; ctl_src = None
    for dr in dirs:
        if not os.path.isdir(dr): print('missing dir %s (run tools/ucode_regen.sh verify)' % dr); rc = 3; continue
        print('== %s' % os.path.relpath(dr, ROOT))
        for f in sorted(glob.glob(os.path.join(dr, '*.c'))):
            au, n = audit_file(f, cfgs)
            ref_only = 'build' in dr and os.path.basename(f) not in COMPILED
            if not ref_only: total += len(au.defects)
            i = au.info
            print('%-30s n=%4d cond=%3d b=%d j=%3d jal=%3d jr=%2d(ra %d) cases=%2d streams=%d routes=%d xeq=%d basex=%d '
                  'slotw_jr=%d slot_ctrl=%d slot_dma=%d wrap=%d/%d defects=%d' % (
                      au.name, n, i['cond'], i['b'], i['j'], i['jal'], i['jr'], i['jr_ra'], len(au.cases), i['splice_streams'],
                      i['ovl_routes'], i['cross_routes_equal'], i['base_exits_equal'], i['slot_writes_jr'], i['slot_ctrl'],
                      i['slot_dma'], i['imem_wrap_restart'], i['imem_wrap_undefined'], len(au.defects))
                  + (' (reference copy, not compiled)' if ref_only else '')
                  + (' xres=%d/%d trimmed=%d' % (i['cross_resident'], i['cross_resident_routes'], i['trimmed_dead_slot']) if i['splice_streams'] else ''))
            if au.jr_other: print('   jr via table/reg:', ' '.join(au.jr_other))
            for x in au.defects[:15]: print('   DEFECT', x)
            if ctl_src is None and os.path.basename(f) == 'factor5_ucode_recompiled.c' and 'build' in dr: ctl_src = f
    bad, mbad = cond_semantics()
    print('R5 cond semantics: %d mismatches over 6 forms x 81 pairs; mutants flagged %s' % (bad, mbad))
    ok = bad == 0 and all(mbad)
    base_lines = open(ctl_src).read().split('\n'); n0 = len(audit_file(ctl_src, cfgs)[0].defects)
    for kind in ['slot_before', 'wrong_target', 'copy_diverge', 'unsigned', 'jr_late', 'jal_ra', 'switch_drop', 'splice_target']:
        n = len(audit_file(ctl_src, cfgs, mutate(base_lines, kind))[0].defects) - n0
        print('R6 control %-13s +defects=%d %s' % (kind, n, 'PASS' if n > 0 else 'FAIL')); ok &= n > 0
    print('verdict: defects=%d controls=%s' % (total, 'PASS' if ok else 'FAIL'))
    return 0 if total == 0 and ok and rc == 0 else 3

if __name__ == '__main__':
    sys.exit(main())
