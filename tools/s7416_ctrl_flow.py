#!/usr/bin/env python3
"""s7416 class BZ: control-flow emission semantics (branches, jumps, calls, delay slots).
N64Recomp lowers a conditional branch at A (slot at A+4) to
    if (COND) { <slot A+4>; goto L_T; }  [goto skip_N;]  <slot A+4>  [skip_N:]
(likely variants add `goto skip_N;` so the fall-through copy of the slot is skipped), jal to
    <slot>; F(rdram, ctx); goto after_N; <slot copy, dead>; after_N:
jr $ra to `<slot>; return;`, jr through a jump table to `switch (jr_addend_A >> 2) { case i: goto L_x; }` and
jr/jalr through a register to `LOOKUP_FUNC(ctx->rS)(...)` emitted AFTER the slot.
Checks (all over ../N64Recomp/RecompiledFuncs, pass-through prefixes stripped):
 S1 every conditional branch: COND text == the expected text for op/regs (64-bit gpr, SIGNED for blez/bgtz/bltz/bgez),
    COND precedes the slot (MIPS evaluates before the slot), goto target == disasm target, label defined in the
    function (or a tail call), slot copy inside == slot copy outside, likely <=> `goto skip_N;` + skip label after copy.
 S2 jal: call name resolves to the function whose first instruction is the jal target; slot precedes the call.
 S3 j: goto L_T (defined) or tail call to the function at T + return.
 S4 jr/jalr through a register: HAZARD if the slot writes the jump register (emission reads it after the slot).
    jr $ra: HAZARD if the slot writes $ra.
 S5 jump tables: every switch case target == the word in the ELF jump table (table address from switch_error),
    jr_addend captured from the index register.
 S6 the distinct COND forms compiled verbatim against recomp.h, driven with 64-bit edge values vs a MIPS model;
    mutants (32-bit compare, signed<->unsigned, operator flip) must flag.
 S7 structural positive control: synthetic emissions with the slot moved before the condition, the likely skip
    dropped / added, a wrong target, a diverging slot copy must each be flagged by the S1 checker.
s7506: the generator now latches rS before a slot that writes it (S4 accepts `gpr jr_target_A = ctx->rS;` +
    LOOKUP_FUNC(jr_target_A); latch control: reverted copy must show the 2 hazards again).
Usage: tools/s7416_ctrl_flow.py   rc 0 = H-equal + all controls PASS, rc 3 otherwise."""
import os, re, sys, struct, subprocess, tempfile, collections, random
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
INC = os.path.join(ROOT, 'lib/N64ModernRuntime/N64Recomp/include')
FUNCS = os.path.join(ROOT, '../N64Recomp/RecompiledFuncs')
ELF = os.path.join(ROOT, '../rogue_squadron64/build/roguesquadron.elf')
REGN = ('zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra').split()
RI = {n: i for i, n in enumerate(REGN)}
RI['s8'] = 30
COND2 = {'beq': '==', 'bne': '!=', 'beql': '==', 'bnel': '!='}
COND1 = {'blez': '<=', 'bgtz': '>', 'bltz': '<', 'bgez': '>=', 'blezl': '<=', 'bgtzl': '>', 'bltzl': '<', 'bgezl': '>=',
         'bltzal': '<', 'bgezal': '>='}
LIKELY = set('beql bnel blezl bgtzl bltzl bgezl bc1tl bc1fl'.split())
FPB = {'bc1t': 'if (c1cs) {', 'bc1tl': 'if (c1cs) {', 'bc1f': 'if (!c1cs) {', 'bc1fl': 'if (!c1cs) {'}
CONDOPS = set(COND2) | set(COND1) | set(FPB) | {'b', 'bal'}
STORES = set('sb sh sw sd swl swr sdl sdr swc1 sdc1 sc scd cache sync nop'.split())
cpat = re.compile(r'^\s*// 0x([0-9A-F]{8}): (\S+)(?:\s+(.*?))?\s*$')
fnpat = re.compile(r'^(?:RECOMP_FUNC|static) void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{')


def rx(r):
    return '0' if r == 0 else 'ctx->r%d' % r


def regs(args):
    return [RI[x] for x in re.findall(r'\$(\w+)', args.split('#')[0]) if x in RI]


def norm(l):
    l = re.sub(r'/\*.*?\*/', '', l).strip()
    if not l or l == ';' or l.startswith('//'): return None
    if re.match(r'g_rs64_last_guest_pc = 0x[0-9A-F]+u;$', l) or re.match(r'CHECK_FR\(ctx, \d+\);$', l): return None
    return re.sub(r'\s+', ' ', l)


def tokenize(lines):
    """-> list of functions: (name, [tok]) ; tok = ('C',addr,op,args,lineno) | ('L',name) | ('X',text)"""
    out = []; cur = None
    for i, line in enumerate(lines):
        m = fnpat.match(line)
        if m: cur = (m.group(1), []); out.append(cur); continue
        if cur is None: continue
        m = cpat.match(line)
        if m:
            cur[1].append(('C', int(m.group(1), 16), m.group(2), m.group(3) or '', i)); continue
        m = re.match(r'^\s*(L_[0-9A-F]{8}|skip_\d+|after_\d+):\s*$', line)
        if m: cur[1].append(('L', m.group(1))); continue
        n = norm(line)
        if n is not None: cur[1].append(('X', n))
    return out


def expect_cond(op, args):
    r = regs(args)
    if op in COND2:
        return 'if (%s %s %s) {' % (rx(r[0]), COND2[op], rx(r[1]))
    if op in COND1:
        return 'if (SIGNED(%s) %s 0) {' % (rx(r[0]), COND1[op])
    if op in FPB: return FPB[op]
    return None


def target(args):
    m = re.search(r'L_([0-9A-F]{8})|0x([0-9A-F]{8})\b', args)
    return int(m.group(1) or m.group(2), 16) if m else None


def check_cond(toks, k, fnlabels, starts):
    pass


def check_cond(toks, k, fnlabels, starts):
    """toks[k] is a conditional-branch comment. Returns (ok, why, cond_text)."""
    _, a, op, args, _ = toks[k]
    j = k + 1; pre = []
    while j < len(toks) and toks[j][0] != 'C': pre.append(toks[j]); j += 1
    if op in ('b', 'bal'):
        return None, 'uncond', None
    want = expect_cond(op, args)
    pl = [t[1] for t in pre]
    if pl != [want]:
        # deliberate fixup patches: pass-through logging calls before the if, or a cond that keeps the guest test
        # as its first conjunct.  Reported as PATCHED (listed for review), not as emission defects.
        if (pl and all(re.match(r'(rs64_\w+|\{ extern)', x) or PATCHLINE.search(x) for x in pl[:-1]) and
                (pl[-1] == want or pl[-1].startswith(want[:-3] + ' && ') or pl[-1].startswith(want[:-3] + ' || '))):
            check_cond.patched.append((op, args, pl[-1][:160], len(pl) - 1))
        else:
            return False, 'cond %r want %r' % (pl, want), None
    if j >= len(toks) or toks[j][1] != a + 4: return False, 'no slot after cond', want
    j += 1; inside = []
    while j < len(toks) and toks[j][0] == 'X' and 'goto L_' not in toks[j][1] and not toks[j][1].endswith('(rdram, ctx);'):
        inside.append(toks[j][1]); j += 1
    T = target(args)
    if j < len(toks) and toks[j][0] == 'X' and toks[j][1].endswith('(rdram, ctx);'):   # link-branch / out-of-fn tail
        call = toks[j][1]; j += 1
        if j < len(toks) and toks[j][1] in ('return;',) or (j < len(toks) and toks[j][1].startswith('goto after_')): j += 1
        nm = re.match(r'(\w+)\(rdram, ctx\);', call)
        if not nm or starts.get(nm.group(1)) != T: return False, 'call target %s != %08X' % (call, T or 0), want
    else:
        if j < len(toks) and toks[j][0] == 'X' and toks[j][1] != 'goto L_%08X;' % T and toks[j][1].endswith('goto L_%08X; }' % T):
            check_cond.patchgoto += 1   # s7081 selfbranch wrapper: `{ if (g_rs64_sbx_on) {...; return; } goto L_T; }`
        elif j >= len(toks) or toks[j][1] != 'goto L_%08X;' % T: return False, 'goto %r want L_%08X' % (toks[j][1] if j < len(toks) else None, T), want
        if ('L_%08X' % T) not in fnlabels: return False, 'label L_%08X undefined' % T, want
        j += 1
    if j >= len(toks) or toks[j][1] != '}': return False, 'no close brace', want
    j += 1
    lk = j < len(toks) and toks[j][0] == 'X' and re.match(r'goto skip_\d+;$', toks[j][1])
    skipname = None
    if lk: skipname = toks[j][1][5:-1]; j += 1
    if bool(lk) != (op in LIKELY): return False, 'likely skip %s for %s' % (bool(lk), op), want
    while j < len(toks) and toks[j][0] == 'L' and not toks[j][1].startswith('skip_'): j += 1   # label at slot addr
    if j >= len(toks) or toks[j][0] != 'C' or toks[j][1] != a + 4: return False, 'no fallthrough slot copy', want
    j += 1; outside = []
    while j < len(toks) and toks[j][0] == 'X': outside.append(toks[j][1]); j += 1
    core = lambda L: [x for x in L if not PATCHLINE.search(x)]
    if outside != inside and core(outside) == core(inside):
        check_cond.patchslot += 1
    elif outside != inside: return False, 'slot copy differs in=%r out=%r' % (inside[:2], outside[:2]), want
    if skipname and not (j < len(toks) and toks[j] == ('L', skipname)): return False, 'skip label not after copy', want
    return True, '', want


check_cond.patched = []
check_cond.patchslot = 0
check_cond.patchgoto = 0
check_cond.patchcall = 0
PATCHLINE = re.compile(r'rs64_|RS64_|g_s\d|s\d{4}_|__builtin_expect|^\{ extern|^extern |PATCH|fprintf|fflush|slot_ret_path')


def slot_dest(op, args):
    if op in STORES or op.startswith('b') or op.startswith('j'): return None
    if op in ('mtc1', 'dmtc1', 'ctc1', 'mtc0', 'mthi', 'mtlo', 'mult', 'multu', 'div', 'divu', 'dmult', 'dmultu', 'ddiv', 'ddivu'): return None
    if op.startswith('c.') or op.startswith('.'): return None
    r = re.findall(r'\$(\w+)', args.split('#')[0])
    if r and r[0] in RI: return RI[r[0]]
    return None


def elf_reader():
    d = open(ELF, 'rb').read()
    assert d[:4] == b'\x7fELF'
    phoff, = struct.unpack('>I', d[28:32]); phentsize, phnum = struct.unpack('>HH', d[42:46])
    segs = []
    for i in range(phnum):
        p = d[phoff + i * phentsize: phoff + (i + 1) * phentsize]
        typ, off, va, pa, fsz, msz = struct.unpack('>IIIIII', p[:24])
        if typ == 1: segs.append((va, off, fsz))
    def word(va, seg=None):
        for i, (v, o, s) in enumerate(segs):
            if seg is not None and i != seg: continue
            if v <= va < v + s: return struct.unpack('>I', d[o + va - v: o + va - v + 4])[0]
        return None
    word.nseg = len(segs)
    return word


def elf_syms():
    d = open(ELF, 'rb').read()
    shoff, = struct.unpack('>I', d[32:36]); shentsize, shnum, shstrndx = struct.unpack('>HHH', d[46:52])
    sh = [struct.unpack('>10I', d[shoff + i * shentsize: shoff + i * shentsize + 40]) for i in range(shnum)]
    out = {}
    for h in sh:
        if h[1] != 2: continue
        strtab = sh[h[6]]; so = strtab[4]
        for k in range(h[5] // 16):
            nm, val, sz, info, oth, ndx = struct.unpack('>IIIBBH', d[h[4] + 16 * k: h[4] + 16 * k + 16])
            e = d.index(b'\0', so + nm); out.setdefault(d[so + nm:e].decode(errors='replace'), val)
    return out


def harvest(files):
    res = collections.Counter(); bad = []; conds = collections.Counter(); haz = []; jt = []; slotlab = 0
    funcs = []
    for f in files:
        funcs += tokenize(open(f, errors='replace').read().split('\n'))
    starts = {}
    for name, toks in funcs:
        for t in toks:
            if t[0] == 'C': starts.setdefault(name, t[1]); break
    for nm, v in elf_syms().items():
        starts.setdefault(nm + '_recomp', v)
    addr2fn = {}
    for n, s in starts.items(): addr2fn.setdefault(s, set()).add(n)
    word = elf_reader()
    for name, toks in funcs:
        labels = {t[1] for t in toks if t[0] == 'L'}
        seen = set()
        for k, t in enumerate(toks):
            if t[0] != 'C': continue
            _, a, op, args, ln = t
            if a in seen: continue   # second (fall-through / dead) copy of a slot comment
            seen.add(a)
            nxt = [u for u in toks[k + 1:k + 40] if u[0] == 'C']
            slot = nxt[0] if nxt else None
            if op in CONDOPS and op not in ('b', 'bal'):
                ok, why, c = check_cond(toks, k, labels, starts)
                res[('cond', ok)] += 1
                if c: conds[(op, c)] += 1
                if not ok: bad.append((name, '%08X' % a, op, args, why))
                if slot: seen.add(slot[1])
            elif op in ('jal', 'j', 'b', 'jr', 'jalr', 'bal'):
                if slot: seen.add(slot[1])
                pre = []
                j = k + 1
                while j < len(toks) and toks[j][0] != 'C': pre.append(toks[j]); j += 1
                if op == 'j' and pre == [('X', 'pause_self(rdram);')] and target(args) == a:
                    res[('j_selfloop_pause', True)] += 1; continue
                if pre and op != 'jr' and all(PATCHLINE.search(x[1]) or re.match(r'rs64_\w+\(', x[1]) for x in pre if x[0] == 'X'):
                    res[(op + '_patched_prefix', True)] += 1; pre = []
                # s7506: N64Recomp latches the jump register before a slot that overwrites it: `gpr jr_target_A = ctx->rS;`
                latch = None
                if op in ('jr', 'jalr') and pre and pre[-1][0] == 'X' and pre[-1][1].startswith('gpr jr_target_%08X = ' % a):
                    latch = pre[-1][1]; pre = pre[:-1]
                if pre and pre[0] == ('X', 'do_break(%d);' % a):
                    res[(op + '_do_break_trap', True)] += 1; continue
                if pre and op != 'jr':
                    res[(op, False)] += 1; bad.append((name, '%08X' % a, op, args, 'code before slot %r' % (pre[:1],))); continue
                j += 1; body = []
                while j < len(toks) and toks[j][0] == 'X': body.append(toks[j][1]); j += 1
                T = target(args)
                sd = slot_dest(slot[2], slot[3]) if slot else None
                if op in ('jal', 'bal'):
                    calls = [b for b in body if re.match(r'\w+\(rdram, ctx\);$', b)]
                    nm = calls[-1][:-len('(rdram, ctx);')] if calls else None
                    if not calls:   # call wrapped by a fixup timing/log patch: `{ ...; NAME(rdram, ctx); ... }`
                        wc = [m.group(1) for b in body for m in [re.search(r'(?:^|[;{] )(\w+)\(rdram, ctx\);', b)] if m and PATCHLINE.search(b)]
                        if wc: nm = wc[-1]; calls = [nm]; check_cond.patchcall += 1
                    lk = [b for b in body if b == 'LOOKUP_FUNC(0x%08X)(rdram, ctx);' % T]
                    if lk and not calls: res[('jal_lookup_const', True)] += 1; continue
                    ok = nm is not None and (starts.get(nm) == T or nm in addr2fn.get(T, ()))
                    if not ok and nm and T in addr2fn: ok = True
                    res[(op, ok)] += 1
                    if not ok: bad.append((name, '%08X' % a, op, args, 'call %r start %s' % (nm, starts.get(nm))))
                elif op in ('j', 'b'):
                    g = [b for b in body if b.startswith('goto L_')]
                    ok = bool(g) and g[-1] == 'goto L_%08X;' % T and ('L_%08X' % T) in labels
                    if not ok:
                        calls = [b for b in body if re.match(r'\w+\(rdram, ctx\);$', b)]
                        ok = bool(calls) and (calls[-1][:-13] in addr2fn.get(T, ()) or starts.get(calls[-1][:-13]) == T)
                    res[(op, ok)] += 1
                    if not ok: bad.append((name, '%08X' % a, op, args, 'j body %r' % (body[-2:],)))
                elif op == 'jr' and args.startswith('$ra'):
                    ok = bool(body) and (body[-1:] == ['return;'] or body[-2:] == ['return;', ';}'])
                    res[('jr_ra', ok)] += 1
                    if not ok: bad.append((name, '%08X' % a, op, args, 'jr ra body %r' % (body[-2:],)))
                    if sd == 31: haz.append((name, '%08X' % a, 'jr $ra slot writes $ra', slot[2], slot[3]))
                else:   # jr reg / jalr
                    rs = regs(args)[-1] if regs(args) else None
                    sw = any(b.startswith('switch (jr_addend_%08X' % a) for b in body)
                    if op == 'jr' and sw:
                        sw_err = [b for b in body if b.startswith('default: switch_error(')]
                        cases = [(int(m.group(1)), int(m.group(2), 16)) for b in body for m in [re.match(r'case (\d+): goto L_([0-9A-F]{8}); break;', b)] if m]
                        tab = int(re.search(r'0x([0-9A-F]+)\);', sw_err[0]).group(1), 16) if sw_err else None
                        enc = (rs << 21) | 8
                        segok = [sg for sg in range(word.nseg) if word(a, sg) == enc and tab is not None and
                                 all(word(tab + 4 * i, sg) == x for i, x in cases)]
                        mism = [] if segok else [(i, x) for i, x in cases if tab is None or word(tab + 4 * i) != x]
                        undef = [x for _, x in cases if 'L_%08X' % x not in labels]
                        # where is jr_addend captured?
                        cap = None
                        for kk, u in enumerate(toks):
                            if u[0] == 'X' and u[1].startswith('gpr jr_addend_%08X = ' % a):
                                cap = u[1]; capc = [v for v in toks[:kk] if v[0] == 'C'][-1]
                        jt.append((name, '%08X' % a, len(cases), '%08X' % (tab or 0), len(mism), len(undef), cap,
                                   capc[2] + ' ' + capc[3] if cap else None))
                        ok = not mism and not undef and cap is not None and tab is not None
                        res[('jtable', ok)] += 1
                        if not ok: bad.append((name, '%08X' % a, op, args, 'jtable mism=%d undef=%d cap=%r' % (len(mism), len(undef), cap)))
                    else:
                        if latch is not None:
                            want = 'LOOKUP_FUNC(jr_target_%08X)(rdram, ctx);' % a
                            ok = want in body and latch == 'gpr jr_target_%08X = %s;' % (a, rx(rs))
                            res[(op + '_reg_latched', ok)] += 1
                        else:
                            want = 'LOOKUP_FUNC(%s)(rdram, ctx);' % rx(rs)
                            ok = want in body
                            res[(op + '_reg', ok)] += 1
                        if not ok: bad.append((name, '%08X' % a, op, args, 'body %r latch %r' % (body[-3:], latch)))
                        if sd is not None and sd == rs and rs != 0 and latch is None:
                            haz.append((name, '%08X' % a, '%s slot writes jump reg' % op, slot[2], slot[3]))
                        if op == 'jalr' and sd == 31:
                            haz.append((name, '%08X' % a, 'jalr slot writes $ra', slot[2], slot[3]))
                        if op == 'jalr' and not re.match(r'^\$\w+$', args.split('#')[0].strip()):
                            haz.append((name, '%08X' % a, 'jalr rd != ra', op, args))
    return res, bad, conds, haz, jt


C_HEAD = r'''
#include <stdint.h>
#include <stdio.h>
#include "recomp.h"
'''


def compile_conds(forms, mutate=None):
    """forms: list of (op, cond text). Generates one test fn per form with the operands remapped to ctx->r8/ctx->r9."""
    body = []; tab = []
    for i, (op, c) in enumerate(forms):
        e = c[len('if ('):-len(') {')]
        e = re.sub(r'ctx->r\d+', 'CTXR', e)
        # first CTXR -> ctx->r8, second -> ctx->r9
        n = [0]
        def sub(m):
            n[0] += 1; return 'ctx->r8' if n[0] == 1 else 'ctx->r9'
        e = re.sub('CTXR', sub, e)
        if mutate: e = mutate(op, e)
        body.append('static int t%d(recomp_context* ctx) { return (%s) ? 1 : 0; }' % (i, e))
        two = op in COND2
        z = c.count('ctx->r') == 1 and two   # beq rX, $zero form
        kind = {'==': 0, '!=': 1, '<=': 2, '>': 3, '<': 4, '>=': 5}[COND2.get(op) or COND1[op]]
        tab.append('{t%d, %d, %d, %d}' % (i, kind, c.count('ctx->r'), 1 if (two and c.count('ctx->r') == 2) else 0))
    src = C_HEAD + '\n'.join(body) + r'''
typedef int (*tfn)(recomp_context*);
typedef struct { tfn f; int kind, two, tworeg; } T;
static T TAB[] = {''' + ','.join(tab) + r'''};
static const uint64_t EV[] = {0,1,0xFFFFFFFFFFFFFFFFull,0x7FFFFFFFull,0x80000000ull,0xFFFFFFFF80000000ull,0xFFFFFFFFull,
  0x100000000ull,0x7FFFFFFFFFFFFFFFull,0x8000000000000000ull,0x00000001FFFFFFFFull,0xFFFFFFFE00000000ull,
  0x0000000100000000ull,0xFFFFFFFF00000000ull,0x00000000FFFFFFFEull,0x123456789ABCDEF0ull};
#define NE 16
static int model(int kind, uint64_t a, uint64_t b) {
    int64_t s = (int64_t)a;
    switch (kind) { case 0: return a == b; case 1: return a != b; case 2: return s <= 0; case 3: return s > 0;
                    case 4: return s < 0; default: return s >= 0; }
}
int main(void) {
    long mism = 0, cases = 0; int nf = sizeof(TAB) / sizeof(TAB[0]); recomp_context c;
    for (int i = 0; i < nf; i++) { long m = 0;
        for (int x = 0; x < NE; x++) for (int y = 0; y < NE; y++) {
            if (!TAB[i].two && (x || y)) continue; if (!TAB[i].tworeg && y) continue;
            uint64_t a = TAB[i].two ? EV[x] : 0, b = TAB[i].tworeg ? EV[y] : 0;
            c.r8 = a; c.r9 = b; cases++;
            if (TAB[i].f(&c) != model(TAB[i].kind, a, b)) m++; }
        if (m) printf("FORM %d mism %ld\n", i, m); mism += m; }
    printf("forms=%d cases=%ld mism=%ld\n", nf, cases, mism); return 0;
}
'''
    d = tempfile.mkdtemp(prefix='s7416_')
    p = os.path.join(d, 't.c'); open(p, 'w').write(src)
    exe = os.path.join(d, 't')
    r = subprocess.run(['cc', '-O2', '-w', '-I', INC, p, '-o', exe], capture_output=True, text=True)
    if r.returncode: print(r.stderr[:2000]); return None
    o = subprocess.run([exe], capture_output=True, text=True).stdout
    m = re.search(r'mism=(\d+)', o)
    bym = [int(x) for x in re.findall(r'FORM (\d+) mism', o)]
    return int(m.group(1)), bym, o.strip().split('\n')[-1]


SYN = '''RECOMP_FUNC void syn(uint8_t* rdram, recomp_context* ctx) {
    // 0x80000000: %(op)s %(args)s
%(pre)s    // 0x80000004: addiu $v0, $v0, 0x1
%(inside)s            goto L_80000010;
    }
%(skip)s    // 0x80000004: addiu $v0, $v0, 0x1
%(outside)s%(skiplab)sL_80000010:
    // 0x80000010: nop
;}'''


def syn(op='bne', args='$v0, $zero, L_80000010', **kw):
    d = dict(op=op, args=args, pre='    if (ctx->r2 != 0) {\n', inside='        ctx->r2 = ADD32(ctx->r2, 0X1);\n',
             outside='    ctx->r2 = ADD32(ctx->r2, 0X1);\n', skip='', skiplab='')
    if op in LIKELY: d.update(skip='    goto skip_0;\n', skiplab='    skip_0:\n')
    d.update(kw)
    return SYN % d


def check_syn(text):
    fn = tokenize(text.split('\n'))[0]
    toks = fn[1]; labels = {t[1] for t in toks if t[0] == 'L'}
    k = [i for i, t in enumerate(toks) if t[0] == 'C'][0]
    return check_cond(toks, k, labels, {})[0]


def main():
    files = sorted(os.path.join(FUNCS, f) for f in os.listdir(FUNCS) if f.endswith('.c'))
    rc = 0
    # S7 structural control first
    ctl = []
    ctl.append(('good bne', check_syn(syn()), True))
    ctl.append(('good bnel', check_syn(syn(op='bnel', pre='    if (ctx->r2 != 0) {\n')), True))
    ctl.append(('slot before cond', check_syn(syn().replace('    if (ctx->r2 != 0) {\n    // 0x80000004: addiu $v0, $v0, 0x1\n        ctx->r2 = ADD32(ctx->r2, 0X1);\n',
                                                              '    // 0x80000004: addiu $v0, $v0, 0x1\n        ctx->r2 = ADD32(ctx->r2, 0X1);\n    if (ctx->r2 != 0) {\n')), False))
    ctl.append(('likely w/o skip', check_syn(syn(op='bnel', skip='', skiplab='')), False))
    ctl.append(('nonlikely with skip', check_syn(syn(skip='    goto skip_0;\n', skiplab='    skip_0:\n')), False))
    ctl.append(('wrong target', check_syn(syn(args='$v0, $zero, L_80000014')), False))
    ctl.append(('slot copy differs', check_syn(syn(outside='    ctx->r2 = ADD32(ctx->r2, 0X2);\n')), False))
    ctl.append(('32-bit cond', check_syn(syn(pre='    if ((uint32_t)ctx->r2 != 0) {\n')), False))
    ctl.append(('unsigned blez', check_syn(syn(op='blez', args='$v0, L_80000010', pre='    if (ctx->r2 <= 0) {\n')), False))
    ctl.append(('swapped regs', check_syn(syn(op='bne', args='$v0, $v1, L_80000010', pre='    if (ctx->r3 != ctx->r2) {\n')), False))
    ctl.append(('good blez', check_syn(syn(op='blez', args='$v0, L_80000010', pre='    if (SIGNED(ctx->r2) <= 0) {\n')), True))
    sctl = all(got == exp for _, got, exp in ctl)
    for n, got, exp in ctl:
        if got != exp: print('S7 CONTROL miss:', n, got, exp)
    print('S7 structural control %d/%d -> %s' % (sum(g == e for _, g, e in ctl), len(ctl), 'PASS' if sctl else 'FAIL'))
    # s7506 S4 latch control: the live data_gap_80024A0C (latched) must give 0 hazards / 0 bad; reverted to the
    # pre-s7506 slot-first emission it must give 2 hazards; a latch of the wrong register must be BAD.
    f7 = os.path.join(FUNCS, 'funcs_7.c'); src7 = open(f7, errors='replace').read()
    m7 = re.search(r'RECOMP_FUNC void data_gap_80024A0C\(.*?\n;?}', src7, re.S)
    if not m7 or 'jr_target_80024A54' not in m7.group(0):  # s7739: the adopted sized regen sizes data_gap_80024A0C to 4 bytes (s6871), so its jr
        # sites are no longer decoded; the control runs on the frozen pre-s7739 emission instead
        m7 = re.search(r'RECOMP_FUNC void data_gap_80024A0C\(.*?\n;?}', open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 's7416_data_gap_80024A0C.c')).read(), re.S)
    lctl = False
    if m7 and 'jr_target_80024A54' in m7.group(0):
        fn = m7.group(0)
        rev = re.sub(r'    gpr jr_target_([0-9A-F]{8}) = ctx->r2;\n', '', fn)
        rev = re.sub(r'LOOKUP_FUNC\(jr_target_[0-9A-F]{8}\)', 'LOOKUP_FUNC(ctx->r2)', rev)
        wrong = fn.replace('gpr jr_target_80024A54 = ctx->r2;', 'gpr jr_target_80024A54 = ctx->r3;')
        outs = []
        for txt in (fn, rev, wrong):
            with tempfile.NamedTemporaryFile('w', suffix='.c', delete=False) as tf: tf.write(txt)
            r_, b_, _, h_, _ = harvest([tf.name]); os.unlink(tf.name)
            outs.append((sum(1 for h in h_ if 'jump reg' in h[2]), sum(1 for b in b_ if b[2] in ('jr', 'jalr') and 'latch' in b[4])))
        lctl = outs[0] == (0, 0) and outs[1][0] == 2 and outs[2][1] >= 1
        print('S4 latch control live=%s reverted=%s wrong-reg=%s -> %s' % (outs[0], outs[1], outs[2], 'PASS' if lctl else 'FAIL'))
    else:
        print('S4 latch control: data_gap_80024A0C not latched in live tree -> FAIL')
    sctl = sctl and lctl
    res, bad, conds, haz, jt = harvest(files)
    print('S1-S5 census:')
    for k in sorted(res): print('  %-10s ok=%-5s %d' % (k[0], k[1], res[k]))
    # classify every non-H-equal site: dead data_gap region, deliberate fixup patch block in the site window, or UNEXPLAINED
    raw = {}
    for f in files:
        L = open(f, errors='replace').read().split('\n')
        fn = None
        for i, l in enumerate(L):
            mf = fnpat.match(l)
            if mf: fn = mf.group(1); continue
            m = cpat.match(l)
            if m and (fn, m.group(1)) not in raw: raw[(fn, m.group(1))] = '\n'.join(L[i:i + 45])
    callers = collections.Counter()
    for f in files:
        for m in re.finditer(r'(data_gap_[0-9A-F]{8})\(rdram, ctx\);', open(f, errors='replace').read()): callers[m.group(1)] += 1
    cls = collections.Counter(); unexpl = []
    for b in bad:
        if b[0].startswith('data_gap_'): c = 'DATA_GAP(callers=%d)' % callers[b[0]]
        elif any(re.search(r'PATCH|s\d{4}_|g_s\d{4}|rs5908|a5379|a5370|_rogue_\w+_check', l) and 'PATCH: s2190 m5 scalar' not in l
                 for l in raw.get((b[0], b[1]), '').split('\n')[:25]): c = 'FIXUP_PATCH'
        else: c = 'UNEXPLAINED'; unexpl.append(b)
        cls[c] += 1
    print('BAD %d by class %s' % (len(bad), dict(cls)))
    for b in bad: print('  ', b[:4], b[4][:110])
    print('UNEXPLAINED %d' % len(unexpl))
    for b in unexpl: print('  ', b)
    livehaz = [h for h in haz if not h[0].startswith('data_gap_') or callers[h[0]]]
    byop = collections.Counter()
    for (op, c), n in conds.items(): byop[op] += n
    print('cond sites by op:', dict(byop))
    print('PATCHED slot copies (differ only in fixup patch lines) %d' % check_cond.patchslot)
    print('PATCHED gotos (s7081 selfbranch wrapper) %d' % check_cond.patchgoto)
    print('PATCHED conds %d' % len(check_cond.patched))
    for x in check_cond.patched: print('  ', x)
    print('HAZARDS %d' % len(haz))
    for h in haz: print('  ', h)
    print('JTABLES %d, mism %d, undef %d, capture forms %s' % (len(jt), sum(x[4] for x in jt), sum(x[5] for x in jt),
          dict(collections.Counter(re.sub(r'_[0-9A-F]{8}', '', x[6] or 'None') for x in jt))))
    capops = collections.Counter((x[7] or '').split()[0] for x in jt); print('  capture at ops', dict(capops))
    # S6
    forms = sorted({(op, c) for (op, c) in conds if op not in FPB})
    gp = [f for f in forms]
    shapes = sorted({(op, re.sub(r'ctx->r\d+', 'R', c)) for op, c in gp})
    print('S6 %d distinct cond texts, %d shapes:' % (len(gp), len(shapes)), [s[1] for s in shapes][:20])
    r0 = compile_conds(gp)
    if r0 is None: print('S6 compile FAIL'); return 3
    print('S6 verbatim:', r0[2])
    muts = {
        'width32': lambda op, e: re.sub(r'ctx->r(\d)', r'(uint32_t)ctx->r\1', e),
        'unsigned': lambda op, e: e.replace('SIGNED(ctx->r8)', 'ctx->r8') if 'SIGNED' in e else e.replace('==', '!=') if '==' in e else e.replace('!=', '=='),
        'opflip': lambda op, e: re.sub(r' (<=|>=|<|>|==|!=) ', lambda m: ' ' + {'<=': '<', '>=': '>', '<': '<=', '>': '>=', '==': '!=', '!=': '=='}[m.group(1)] + ' ', e),
        'signext32': lambda op, e: re.sub(r'ctx->r(\d)', r'(uint64_t)(int64_t)(int32_t)ctx->r\1', e),
    }
    mctl = True
    for mn, mf in muts.items():
        rm = compile_conds(gp, mf)
        flagged = len(set(rm[1]))
        print('  mutant %-9s mism=%d forms flagged %d/%d' % (mn, rm[0], flagged, len(gp)))
        if rm[0] == 0: mctl = False
    hequal = (r0[0] == 0 and not unexpl and not livehaz)
    print('HAZARDS live (non-dead) %d of %d; latent generator defect: jr/jalr emit the slot BEFORE reading the jump register' % (len(livehaz), len(haz)))
    print('CONTROL structural=%s mutants=%s' % ('PASS' if sctl else 'FAIL', 'PASS' if mctl else 'FAIL'))
    print('VERDICT', 'H-equal' if hequal else ('H-slotorder' if livehaz else 'H-other (see UNEXPLAINED/S6)'))
    return 0 if (hequal and sctl and mctl) else 3


if __name__ == '__main__':
    sys.exit(main())
