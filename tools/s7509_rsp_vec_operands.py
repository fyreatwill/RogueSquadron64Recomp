#!/usr/bin/env python3
"""s7509 class FF: RSPRecomp vector-op OPERAND EXTRACTION vs the ROM bits.

s7091 compares live text to pristine generator text (same generator both sides) and s7092 checks vector
implementations only, so a rabbitizer field slip (GetRsp_vd/vs/vt, elementhigh vs elementlow, GetRsp_de()&7, the Imm7
sign extension, VtIndex/VsIndex) would be invisible to both. Here:
  V1 every live record of the 3 compiled RSP TUs (base + 9 splice streams + delay-slot copies; walk = s7508 audit) whose
     ROM word is cop2 (computational or mfc2/mtc2/cfc2/ctc2), lwc2 or swc2 is decoded INDEPENDENTLY from the ROM word
     (field layout from the RSP manual, not rabbitizer) and the exact expected `rsp.NAME<e>(args);` line is rebuilt
     from rsp_recomp.cpp's vector_operands table order; it must equal the record's only rsp.* line, and the comment
     mnemonic must equal the independent name.
  V2 offset scaling: every LxV/SxV in librecomp rsp_vu_impl.hpp must compute `rs + imm * size` with the hardware size
     (lbv/sbv 1, lsv/ssv 2, llv/slv 4, ldv/sdv/lpv/spv/luv/suv 8, the rest 16), and take imm as s8 (the -64..63 Imm7
     range fits). Every live immediate must sit in -64..63.
  V3 controls: (a) flip the element bits of one spliced vector ROM word; (b) swap vs/vt in one live line; (c) the Imm7
     sign dropped (0x7F mask) on one negative-offset live line's ROM word; (d) a V2 size table with lpv=16 -> must flag.
Usage: tools/s7509_rsp_vec_operands.py   rc 0 = 0 defects + every control fires."""
import os, re, sys, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn)); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m
fe = _load('fe7508', 's7508_rsp_scalar_gaps.py')
su, cf = fe.su, fe.cf
ROOT = os.path.join(HERE, '..')
LIVE = os.path.join(ROOT, 'build/factor5_ucode')
IMPL = os.path.join(ROOT, 'lib/N64ModernRuntime/librecomp/include/librecomp/rsp_vu_impl.hpp')

VCOMP = {0: 'vmulf', 1: 'vmulu', 2: 'vrndp', 3: 'vmulq', 4: 'vmudl', 5: 'vmudm', 6: 'vmudn', 7: 'vmudh', 8: 'vmacf',
         9: 'vmacu', 10: 'vrndn', 11: 'vmacq', 12: 'vmadl', 13: 'vmadm', 14: 'vmadn', 15: 'vmadh', 16: 'vadd', 17: 'vsub',
         19: 'vabs', 20: 'vaddc', 21: 'vsubc', 29: 'vsar', 32: 'vlt', 33: 'veq', 34: 'vne', 35: 'vge', 36: 'vcl',
         37: 'vch', 38: 'vcr', 39: 'vmrg', 40: 'vand', 41: 'vnand', 42: 'vor', 43: 'vnor', 44: 'vxor', 45: 'vnxor',
         48: 'vrcp', 49: 'vrcpl', 50: 'vrcph', 51: 'vmov', 52: 'vrsq', 53: 'vrsql', 54: 'vrsqh', 55: 'vnop'}
LS = ['bv', 'sv', 'lv', 'dv', 'qv', 'rv', 'pv', 'uv', 'hv', 'fv', 'wv', 'tv']
SIZE = {'bv': 1, 'sv': 2, 'lv': 4, 'dv': 8, 'qv': 16, 'rv': 16, 'pv': 8, 'uv': 8, 'hv': 16, 'fv': 16, 'wv': 16, 'tv': 16}
DE_OPS = {'vmov', 'vrcp', 'vrcpl', 'vrcph', 'vrsq', 'vrsql', 'vrsqh'}

def r(n): return 'rsp.vpu.r[%d]' % n
def g(n): return 'r%d' % n if n else '0'
def hx(v): return ('-0X%X' % -v) if v < 0 else '0X%X' % v

def vdecode(w):
    """ROM word -> (name, expected line) for a vector-unit word, or None if not one. Independent of rabbitizer."""
    op = w >> 26
    if op == 18:
        rs, rt, rd = (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31
        if rs & 16:
            e, vt, vs, vd, fn = (w >> 21) & 15, (w >> 16) & 31, (w >> 11) & 31, (w >> 6) & 31, w & 63
            n = VCOMP.get(fn)
            if n is None: return ('?vfn%d' % fn, None)
            N = n.upper()
            if n == 'vnop': return n, 'rsp.VNOP();'
            if n == 'vmacq': return n, f'rsp.VMACQ({r(vd)});'
            if n == 'vsar': return n, f'rsp.VSAR<{e}>({r(vd)}, {r(vs)});'
            if n in ('vrndn', 'vrndp'): return n, f'rsp.{N}<{e}>({r(vd)}, {vs}, {r(vt)});'
            if n in DE_OPS: return n, f'rsp.{N}<{e}>({r(vd)}, {vs & 7}, {r(vt)});'
            return n, f'rsp.{N}<{e}>({r(vd)}, {r(vs)}, {r(vt)});'
        e = (w >> 7) & 15
        n = {0: 'mfc2', 2: 'cfc2', 4: 'mtc2', 6: 'ctc2'}.get(rs)
        if n is None: return ('?cop2rs%d' % rs, None)
        if n in ('cfc2', 'ctc2'): return n, f'rsp.{n.upper()}({g(rt)}, {rd});'
        return n, f'rsp.{n.upper()}<{e}>({g(rt)}, {r(rd)});'
    if op in (50, 58):
        base, vt, sub, e, off = (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31, (w >> 7) & 15, w & 0x7F
        off = off - 0x80 if off & 0x40 else off
        if sub >= len(LS): return ('?lsc2sub%d' % sub, None)
        n = ('l' if op == 50 else 's') + LS[sub]
        a = str(vt) if LS[sub] == 'tv' else r(vt)
        return n, f'rsp.{n.upper()}<{e}>({a}, {g(base)}, {hx(off)});'
    return None

def walk(fname, lines, words, notes, ctl_line=None):
    """s7508 audit() address walk; vector check instead of scalar. ctl_line(seg, code) may mutate code (control)."""
    segs, _, _ = cf.segments(lines)
    bad = collections.Counter(); info = collections.Counter(); per = collections.Counter(); sites = []
    P, a = 'L', min(words['L']); copy_next = False; prev = None
    for sg in segs:
        labs = [l for l in sg['labels'] if l[0] in cf.PREFIX_FILE and not l[2]]
        if labs and not copy_next:
            P, a = labs[0][0], labs[0][1]
            if P not in words: bad['no-stream'] += 1; return bad, info, per, sites
        addr, is_copy = (prev + 4, True) if copy_next else (a, False)
        w = words[P].get(addr)
        if w is None: bad['addr-out-of-image'] += 1; notes.append(f'{fname} {P}_{addr:04X}: no ROM word'); return bad, info, per, sites
        d = su.decode(w); info['records'] += 1
        v = vdecode(w)
        if v is not None:
            n, want = v
            info['vec'] += 1; info['vec_splice'] += P != 'L'; info['vec_copy'] += is_copy
            body = [c for c in sg['code'] if c.startswith('rsp.')]
            others = [c for c in sg['code'] if not c.startswith('rsp.') and not su.fixup_line(c)
                      and not c.startswith('goto ') and c != '}']
            if ctl_line: body = ctl_line(sg, P, addr, body)
            cm = sg['mnem']
            if cm != n:
                bad['mnemonic'] += 1; notes.append(f'{fname} {P}_{addr:04X} comment {sg["comment"]!r} independent {n} {w:08X}')
            if want is None:
                bad['undecodable'] += 1; notes.append(f'{fname} {P}_{addr:04X} {w:08X} {n}')
            elif len(body) != 1 or body[0] != want:
                bad['operands'] += 1; notes.append(f'{fname} {P}_{addr:04X} {n}: got {body!r} want {want!r}')
            else:
                per[n] += 1; info['vec_ok'] += 1
                sites.append((fname, P, addr, n, want))
            if others: info['vec_extra_lines'] += 1; notes.append(f'{fname} {P}_{addr:04X} extra {others!r}')
            m = re.search(r', (-?0X[0-9A-F]+)\);$', want or '')
            if m and n[0] in 'ls' and n[1:] in SIZE:
                iv = int(m.group(1).replace('0X', ''), 16) if not m.group(1).startswith('-') else -int(m.group(1)[3:], 16)
                if not -64 <= iv <= 63: bad['imm-range'] += 1
                info['neg_imm'] += iv < 0
        elif d['m'] in ('cop2vec', 'lwc2', 'swc2', 'mfc2', 'mtc2', 'cfc2', 'ctc2'):
            bad['decoder-disagree'] += 1
        elif d['m'] != '?' and {'beqz': 'beq', 'bnez': 'bne'}.get(sg['mnem'], sg['mnem']) != d['m'] and \
                not (sg['mnem'] == 'move' and d['m'] in ('or', 'addu')):
            bad['alignment'] += 1; notes.append(f'{fname} {P}_{addr:04X} comment {sg["comment"]!r} rom {d["m"]} {w:08X}')
            return bad, info, per, sites
        ctrl = d['m'] in su.BR or d['m'] in su.JMP
        if is_copy: copy_next = False
        else:
            a += 4
            if ctrl: copy_next, prev = True, addr
    return bad, info, per, sites

FILES = ('factor5_ucode_recompiled.c', 'factor5_ucode_b_recompiled.c', 'factor5_boot_recompiled.c')
def run_v1(cfgs, words_mut=None, ctl_line=None):
    tot = collections.Counter(); notes = []; infos = {}; per = collections.Counter(); sites = []
    for fname in FILES:
        lines = open(os.path.join(LIVE, fname)).read().split('\n')
        words = fe.words_for(fname, cfgs)
        if words_mut and fname == FILES[0]: words_mut(words)
        b, i, p, s = walk(fname, lines, words, notes, ctl_line if fname == FILES[0] else None)
        tot += b; infos[fname] = i; per += p; sites += s
    return tot, notes, infos, per, sites

def run_v2(size=SIZE):
    src = open(IMPL).read(); bad = []; seen = {}
    for m in re.finditer(r'auto RSP::([LS][A-Z]V)\(([^)]*)\) -> void \{(.*?)\n\}', src, re.S):
        name, args, body = m.group(1).lower(), m.group(2), m.group(3)
        k = name[1:]
        if k not in size: continue
        am = re.search(r'auto address = rs \+ imm(?: \* (\d+))?;', body)
        scale = int(am.group(1)) if am and am.group(1) else (1 if am else None)
        ok = scale == size[k] and 's8 imm' in args
        seen[name] = scale
        if not ok: bad.append(f'{name}: scale {scale} want {size[k]} args {args!r}')
    want = {p + k for p in 'ls' for k in size}
    missing = sorted(want - set(seen))
    return bad, seen, missing

def main():
    cfgs = cf.tomls()
    bad, notes, infos, per, sites = run_v1(cfgs)
    print('== V1 vector operand extraction vs independent ROM decode (live composite, splices + slot copies) ==')
    for f, i in infos.items():
        print(f'  {f:30s} records={i["records"]} vec={i["vec"]} (splice {i["vec_splice"]}, copies {i["vec_copy"]}) '
              f'ok={i["vec_ok"]} neg_imm={i["neg_imm"]} extra_lines={i["vec_extra_lines"]}')
    print('  ops:', ' '.join(f'{k}={v}' for k, v in sorted(per.items())))
    print('  defects:', dict(bad) or 0)
    for n in notes[:20]: print('   ', n)
    ok = not bad and bool(sites)
    # coverage: every rsp.* call line in the compiled TUs' instruction region is one of the checked sites
    for f in FILES:
        L = open(os.path.join(LIVE, f)).read().split('\n')
        st = next((i for i, l in enumerate(L) if l.strip() == 'RSP rsp{};'), 0)
        en = next((i for i, l in enumerate(L) if l.startswith('do_indirect_jump:')), len(L))
        n = sum(1 for l in L[st:en] if l.strip().startswith('rsp.'))
        print(f'  coverage {f}: rsp.* lines {n} vs vec records {infos[f]["vec"]}')
        ok &= n == infos[f]['vec']
    print('== V2 LxV/SxV offset scaling in rsp_vu_impl.hpp ==')
    b2, seen, missing = run_v2()
    print('  scales:', ' '.join(f'{k}={v}' for k, v in sorted(seen.items())))
    used = sorted({s[3] for s in sites if s[3][0] in 'ls' and s[3][1:] in SIZE})
    print('  used by live sites:', ' '.join(used), '| not implemented:', missing or 'none', '| defects:', b2 or 0)
    ok &= not b2 and not (set(used) & set(missing))
    print('== V3 controls ==')
    # (a) flip element bits of the first spliced computational vector word
    fa = next(s for s in sites if s[0] == FILES[0] and s[1] != 'L' and s[3].startswith('v') and '<' in s[4])
    def flip_e(words): words[fa[1]][fa[2]] ^= 1 << 22
    ca = run_v1(cfgs, words_mut=flip_e)[0]
    # (b) swap vs/vt in one live 3-register line
    fb = next(s for s in sites if s[0] == FILES[0] and re.match(r'rsp\.V\w+<\d+>\(rsp\.vpu\.r\[(\d+)\], rsp\.vpu\.r\[(\d+)\], rsp\.vpu\.r\[(?!\2\])\d+\]\);', s[4]))
    def swap(sg, P, addr, body):
        if (P, addr) != fb[1:3]: return body
        mm = re.match(r'(rsp\.\w+<\d+>\(rsp\.vpu\.r\[\d+\], )(rsp\.vpu\.r\[\d+\]), (rsp\.vpu\.r\[\d+\])\);', body[0])
        return [f'{mm.group(1)}{mm.group(3)}, {mm.group(2)});']
    cb = run_v1(cfgs, ctl_line=swap)[0]
    # (c) Imm7 sign dropped: emulate a generator that masks 0x7F on one negative-offset site (live line mutated)
    fc = next(s for s in sites if s[0] == FILES[0] and ', -0X' in s[4])
    def unsign(sg, P, addr, body):
        if (P, addr) != fc[1:3]: return body
        mm = re.search(r'-0X([0-9A-F]+)\);$', body[0]); v = (-int(mm.group(1), 16)) & 0x7F
        return [body[0][:mm.start()] + '0X%X);' % v]
    cc = run_v1(cfgs, ctl_line=unsign)[0]
    cd, _, _ = run_v2(dict(SIZE, pv=16))
    res = {'a_elem_flip_splice': sum(ca.values()) > sum(bad.values()), 'b_vs_vt_swap': sum(cb.values()) > sum(bad.values()),
           'c_imm7_unsigned': sum(cc.values()) > sum(bad.values()), 'd_lpv16_table': len(cd) > len(b2)}
    print(f'  a {fa[1]}_{fa[2]:04X} {fa[3]} -> {dict(ca)}; b {fb[1]}_{fb[2]:04X} -> {dict(cb)}; '
          f'c {fc[1]}_{fc[2]:04X} {fc[3]} -> {dict(cc)}; d -> {cd}')
    for k, v in res.items(): print(f'  {k}: {"PASS" if v else "FAIL"}')
    ok &= all(res.values())
    print('verdict:', 'PASS (FF H-equal)' if ok else 'FAIL')
    return 0 if ok else 3

if __name__ == '__main__':
    sys.exit(main())
