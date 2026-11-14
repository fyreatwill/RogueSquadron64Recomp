#!/usr/bin/env python3
"""s7361 class AL census: guest-pointer dereferences in owned host code, classified by whether the
base can leave librecomp's 4 GB rdram reservation.

Model (lib/N64ModernRuntime/N64Recomp/include/recomp.h, librecomp addresses.hpp):
  MEM_x(off, base) = *(rdram + ((base + off) - 0xFFFFFFFF80000000)).  rdram is a 4 GB PROT_NONE
  reservation with the first 512 MB read/write.  For a SIGN-EXTENDED 32-bit base the host offset
  is always in [0, 4 GB): a junk guest pointer lands in guest RAM or faults deterministically,
  never on host memory.  A ZERO-EXTENDED base (uint32_t / u32 / unsuffixed 0x8xxxxxxx literal,
  or a uint32 cast to 64 bits) adds 4 GB: the access lands PAST the reservation on whatever the
  host has mapped there -> silent host corruption or a wild fault, even for a VALID pointer.
  TO_PTR(T, v) masks with 0x1FFFFFF -> always inside the RW 512 MB: CONTAINED.
Row classes: SEXT (contained), MASK (TO_PTR, contained), ZEXT (hole unless proven dead),
UNK (type not resolved -> by hand).  `--selftest` runs planted controls.
"""
import re, sys, os, glob

MEMRE = re.compile(r'\b(MEM_(?:W|H|B|HU|BU|D)|SD|LD|LWL|LWR|SWL|SWR|SW|SH|SB)\s*\(')
SEXT_T = r'(?:gpr|int64_t|s64|int32_t|s32|int|long long|int16_t|s16|int8_t|s8|uint16_t|u16|uint8_t|u8|PTR\([^)]*\)|recomp_context\s*\*)'
ZEXT_T = r'(?:uint32_t|u32|unsigned int|unsigned)'
U64_T = r'(?:uint64_t|u64|size_t|uintptr_t)'


def split_args(s, i):
    """s[i] is just after '(' ; return list of top-level args and end index."""
    depth, cur, args = 0, '', []
    while i < len(s):
        c = s[i]
        if c in '([{':
            depth += 1
        elif c in ')]}':
            if depth == 0:
                args.append(cur.strip())
                return args, i
            depth -= 1
        elif c == ',' and depth == 0:
            args.append(cur.strip()); cur = ''; i += 1; continue
        cur += c
        i += 1
    return None, i


def decl_type(text, pos, name):
    """Nearest preceding declaration of `name` (same file, within 30000 chars)."""
    lo = max(0, pos - 200000)
    seg = text[lo:pos]
    pat = re.compile(r'(?:\b(?:const|static|volatile|register)\s+)*(' + SEXT_T + '|' + ZEXT_T + '|' + U64_T +
                     r'|auto)\s+(?:const\s+)?(?:(?:[^;{}()]|\((?:[^;{}()]|\([^;{}()]*\))*\))*?,\s*)?' + re.escape(name) + r'\s*(?:[=;,)\[]|\{)')
    last = None
    for m in pat.finditer(seg):
        last = m
    if not last:
        return None
    t = last.group(1)
    if re.fullmatch(r'gpr|int64_t|s64|long long', t):
        return 'S64'
    if re.fullmatch(SEXT_T, t):
        return 'S'
    if re.fullmatch(ZEXT_T, t):
        return 'Z'
    if re.fullmatch(U64_T, t):
        # a uint64_t is only sign-extended if its initialiser was; look at the initialiser
        tail = text[lo + last.end() - 1: lo + last.end() + 160].split(';')[0]
        if re.search(r'\(uint32_t\)|\(u32\)', tail):
            return 'ZU64'
        if re.search(r'ctx->r\d|\(int32_t\)|\(s32\)|\(int64_t\)|\(gpr\)\s*\(int32_t\)', tail):
            return 'S'
        return 'U64'
    if t == 'auto':
        tail = text[lo + last.end() - 1: lo + last.end() + 160].split(';')[0]
        if re.search(r'ctx->r\d|\(int32_t\)|\(s32\)|\(gpr\)', tail):
            return 'S'
        if re.search(r'\(uint32_t\)|\(u32\)', tail):
            return 'Z'
        return None
    return None


# C-type evaluator: every primary operand gets one of
#   S32 (signed <=32 bit, incl. promoted u8/u16), U32 (unsigned 32), S64 (64-bit holding a sign-extended value),
#   Z64 (64-bit holding a zero-extended 32-bit value), U64 (64-bit, provenance unknown), UNK.
# Sum rule (C usual arithmetic conversions, then the macro adds 0xFFFFFFFF80000000ULL):
#   any S64 -> SEXT;  else any Z64 -> ZEXT;  else any U64 -> UNK;  else any U32 -> ZEXT;  else any UNK -> UNK;
#   else all S32 -> SEXT.
CAST_S32 = r'int32_t|s32|int|int16_t|s16|int8_t|s8|uint16_t|u16|uint8_t|u8|short|char'
CAST_U32 = r'uint32_t|u32|unsigned int|unsigned'
CAST_64 = r'gpr|uint64_t|u64|int64_t|s64|uintptr_t|size_t|long long|unsigned long long'
MEMVAL = {'MEM_W': 'S32', 'MEM_H': 'S32', 'MEM_B': 'S32', 'MEM_HU': 'S32', 'MEM_BU': 'S32', 'MEM_D': 'S64'}


def _skip_parens(s, i):
    d = 0
    while i < len(s):
        if s[i] == '(':
            d += 1
        elif s[i] == ')':
            d -= 1
            if d == 0:
                return i + 1
        i += 1
    return i


def operands(b, text, pos):
    """Yield (kind, token) for each primary operand of expression b."""
    out = []
    i, n = 0, len(b)
    pending = None   # cast applying to the next primary
    while i < n:
        c = b[i]
        if c.isspace() or c in '+-*/%&|^~<>!?:':
            i += 1; continue
        if c == '(':
            m = re.match(r'\(\s*(' + CAST_64 + '|' + CAST_U32 + '|' + CAST_S32 + r')\s*\)', b[i:])
            if m:
                t = m.group(1)
                if pending is None:
                    pending = t
                elif re.fullmatch(CAST_64, pending) and re.fullmatch(CAST_S32, t):
                    pending = '64S'
                elif re.fullmatch(CAST_64, pending) and re.fullmatch(CAST_U32, t):
                    pending = '64Z'
                i += m.end(); continue
            j = _skip_parens(b, i)
            sub = operands(b[i + 1:j - 1], text, pos)
            out.append(apply_cast(pending, combine(sub), '(...)')); pending = None
            i = j; continue
        m = re.match(r'(S32|SX|ADD32|SUB32)\s*\(', b[i:])
        if m:
            j = _skip_parens(b, i + m.end() - 1)
            out.append(apply_cast(pending, ('S64' if m.group(1) != 'S32' else 'S32', m.group(1)), m.group(1))); pending = None
            i = j; continue
        m = re.match(r'(MEM_(?:W|H|B|HU|BU|D))\s*\(', b[i:])
        if m:
            j = _skip_parens(b, i + m.end() - 1)
            out.append(apply_cast(pending, (MEMVAL[m.group(1)], m.group(1)), m.group(1))); pending = None
            i = j; continue
        m = re.match(r'0[xX]([0-9A-Fa-f]+)([uUlL]*)|(\d+)([uUlL]*)', b[i:])
        if m:
            if m.group(1):
                v, suf = int(m.group(1), 16), m.group(2).lower()
                if 'll' in suf or v > 0xFFFFFFFF:
                    k = 'S64' if v >= 0xFFFFFFFF80000000 else ('S64' if v < 0x80000000 else 'Z64')
                elif 'u' in suf or v >= 0x80000000:
                    k = 'U32'
                else:
                    k = 'S32'
            else:
                v, suf = int(m.group(3)), m.group(4).lower()
                k = 'U32' if 'u' in suf else ('S64' if 'll' in suf else 'S32')
            out.append(apply_cast(pending, (k, m.group(0)), m.group(0))); pending = None
            i += m.end(); continue
        m = re.match(r'[A-Za-z_]\w*(?:\s*(?:->|\.)\s*\w+)*', b[i:])
        if m:
            tok = re.sub(r'\s+', '', m.group(0))
            i += m.end()
            if i < n and b[i:].lstrip().startswith('['):
                j = b.index('[', i); d = 0
                while j < n:
                    if b[j] == '[': d += 1
                    elif b[j] == ']':
                        d -= 1
                        if d == 0: break
                    j += 1
                i = j + 1
                out.append(apply_cast(pending, ('UNK', tok + '[]'), tok)); pending = None; continue
            if i < n and b[i:].lstrip().startswith('('):   # function call
                j = _skip_parens(b, b.index('(', i))
                i = j
                out.append(apply_cast(pending, ('UNK', tok + '()'), tok)); pending = None; continue
            if tok == 'sizeof':
                continue
            if re.match(r'ctx->r\d+$', tok):
                k = 'S64'
            elif '->' in tok or '.' in tok:
                k = 'UNK'
            else:
                d = decl_type(text, pos, tok)
                k = {'S64': 'S64', 'S': 'S32', 'Z': 'U32', 'U64': 'U64', None: 'UNK'}.get(d, 'UNK')
                if d == 'ZU64':
                    k = 'Z64'
            out.append(apply_cast(pending, (k, tok), tok)); pending = None
            continue
        i += 1
    return out


def apply_cast(cast, kt, tok):
    k, t = kt
    if cast is None:
        return (k, t)
    if cast == '64S':
        return ('S64', t)
    if cast == '64Z':
        return ('Z64', t)
    if re.fullmatch(CAST_S32, cast):
        return ('S32', t)
    if re.fullmatch(CAST_U32, cast):
        return ('U32', t)
    # 64-bit cast of x: preserves sext of S32, zext of U32
    return {'S32': 'S64', 'U32': 'Z64', 'S64': 'S64', 'Z64': 'Z64'}.get(k, 'UNK'), t


def combine(ops):
    ks = [k for k, _ in ops]
    if not ks:
        return ('UNK', 'empty')
    if 'U64' in ks and 'S32' in ks and not ({'S64', 'Z64', 'U32', 'UNK'} & set(ks)):
        return ('S64', 'S32 promoted beside a 64-bit counter')
    for want, res in (('S64', 'S64'), ('Z64', 'Z64'), ('U64', 'U64'), ('U32', 'U32'), ('UNK', 'UNK')):
        if want in ks:
            return (res, ','.join(t for k, t in ops if k == want))
    return ('S32', 'signed32')


def classify(base, text, pos):
    k, why = combine(operands(base, text, pos))
    return {'S64': 'SEXT', 'S32': 'SEXT', 'Z64': 'ZEXT', 'U32': 'ZEXT'}.get(k, 'UNK'), k + ':' + why


FAST_SEXT = re.compile(r'\s*ctx->r\d+\s*,\s*-?0X[0-9A-F]+\s*\)')


def scan(path, text, fast=False):
    rows = []
    for m in MEMRE.finditer(text):
        if fast and FAST_SEXT.match(text, m.end()):
            continue   # pristine N64Recomp emission MEM_x(ctx->rN, 0XOFF): always sign-extended
        name = m.group(1)
        args, end = split_args(text, m.end())
        if not args:
            continue
        if name.startswith('MEM_'):
            if len(args) != 2:
                continue
            base = '(' + args[0] + ') + (' + args[1] + ')'   # reg+offset is symmetric; N64Recomp emits (reg, off)
        elif name in ('SD', 'SW', 'SH', 'SB', 'SWL', 'SWR'):
            if len(args) != 3:
                continue
            base = args[2]
        else:  # LD/LWL/LWR(offset, reg) style
            if len(args) < 2:
                continue
            base = args[-1]
        line = text.count('\n', 0, m.start()) + 1
        pre = text[text.rfind('\n', 0, m.start()) + 1:m.start()]
        if re.match(r'\s*(//|#\s*define)', pre):
            continue
        c, why = classify(base, text, m.start())
        rows.append((path, line, name, base.replace('\n', ' ')[:60], c, why))
    for m in re.finditer(r'\bTO_PTR\s*\(', text):
        line = text.count('\n', 0, m.start()) + 1
        pre = text[text.rfind('\n', 0, m.start()) + 1:m.start()]
        if re.match(r'\s*(//|#\s*define)', pre):
            continue
        rows.append((path, line, 'TO_PTR', '', 'MASK', '& 0x1FFFFFF'))
    return rows


def scope():
    fs = []
    for pat in ['src/**/*.cpp', 'src/**/*.c', 'src/**/*.h', 'src/**/*.hpp',
                'lib/N64ModernRuntime/librecomp/src/*.cpp', 'lib/N64ModernRuntime/ultramodern/src/*.cpp',
                'tools/fixup_*.py', 'tools/apply_*.py']:
        fs += glob.glob(pat, recursive=True)
    return sorted(set(fs))


SELFTEST = r'''
void a(uint8_t* rdram, recomp_context* ctx) {
    uint32_t za = 0x80001000;          // ZEXT ctl
    int32_t  sa = 0x80001000;          // SEXT ctl
    PTR(u8)  pa = _arg<0, PTR(u8)>(rdram, ctx);
    gpr ga = ctx->r4;
    uint64_t ua = (uint64_t)(uint32_t)ctx->r4;
    MEM_W(0, za) = 1;                  // expect ZEXT
    MEM_W(0, sa) = 1;                  // expect SEXT
    MEM_B(0, pa) = 1;                  // expect SEXT
    MEM_H(2, ctx->r5) = 1;             // expect SEXT
    MEM_W(0, 0x80123456) = 1;          // expect ZEXT (unsigned literal)
    MEM_W(0, (int32_t)0x80123456) = 1; // expect SEXT
    MEM_W(0, ua) = 1;                  // expect ZEXT
    MEM_W(0, ga + za) = 1;             // expect SEXT (64-bit sext operand dominates)
    MEM_W(0, (gpr)za) = 1;             // expect ZEXT
    u8* q = TO_PTR(u8, ga);            // expect MASK
}
'''
EXPECT = ['ZEXT', 'SEXT', 'SEXT', 'SEXT', 'ZEXT', 'SEXT', 'ZEXT', 'SEXT', 'ZEXT', 'MASK']


def main():
    if '--selftest' in sys.argv:
        rows = scan('selftest', SELFTEST)
        got = [r[4] for r in rows if r[2] != 'TO_PTR'] + [r[4] for r in rows if r[2] == 'TO_PTR']
        ok = got == EXPECT
        for r, e in zip(rows, EXPECT):
            pass
        print('selftest', 'PASS' if ok else 'FAIL', got)
        sys.exit(0 if ok else 1)
    allrows = []
    if '--gen' in sys.argv:
        d = sys.argv[sys.argv.index('--gen') + 1]
        for f in sorted(glob.glob(d + '/*.c')):
            allrows += [r for r in scan(f, open(f, errors='replace').read(), fast=True) if r[2] != 'TO_PTR']
        from collections import Counter
        print('GEN TOTAL(non-pristine)', len(allrows), dict(Counter(r[4] for r in allrows)))
        for r in allrows:
            if r[4] in ('ZEXT', 'UNK'):
                print('%s:%d %s base=[%s] %s (%s)' % r)
        sys.exit(1 if any(r[4] == 'ZEXT' for r in allrows) else 0)   # regen gate: a zero-extended base is a defect
    for f in scope():
        try:
            t = open(f, errors='replace').read()
        except Exception:
            continue
        allrows += scan(f, t)
    from collections import Counter
    c = Counter(r[4] for r in allrows)
    print('TOTAL', len(allrows), dict(c))
    for r in allrows:
        if r[4] in ('ZEXT', 'UNK'):
            print('%s:%d %s base=[%s] %s (%s)' % r)


if __name__ == '__main__':
    main()
