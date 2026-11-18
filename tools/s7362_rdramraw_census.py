#!/usr/bin/env python3
"""s7362 class AM census: raw host pointer arithmetic on guest RDRAM (`rdram + X`, `rdram[X]`, `&rdram[X]`)
in owned host code, classified by whether X can leave librecomp's 4 GB rdram reservation.

Model (librecomp addresses.hpp, recomp.cpp:872): rdram = mmap(4 GB, PROT_NONE), first 512 MB RW. Nothing is
reserved BEFORE rdram or AFTER rdram + 4 GB, so:
  * an offset of C type uint32 (whole sum evaluated in 32-bit unsigned) is in [0, 4 GB): guest RAM or a
    deterministic fault, never host memory -> U32 (contained; a junk value faults, it does not corrupt);
  * a signed 32-bit offset can be NEGATIVE -> host memory below rdram -> SIGNED (by hand: provably >= 0?);
  * a 64-bit offset, or u32 + a further pointer-level term (`rdram + u32 + k`), can pass rdram + 4 GB
    -> WIDE / U32+K (by hand);
  * a top-level `& M` with M < 0x20000000 or a literal offset < 512 MB -> MASK / CONST (contained in RW).
Rows: MASK, CONST, U32, SIGNED, NEG (sext KSEG0 added unbiased), U32+K, WIDE, UNK.
`--check` exits 1 on any non-contained row without a hand verdict in REVIEWED; `--gen DIR` scans a generated tree.  `--selftest` runs planted rows of every class.
"""
import re, sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
_s = importlib.util.spec_from_file_location('c61', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7361_memzext_census.py'))
c61 = importlib.util.module_from_spec(_s); _s.loader.exec_module(c61)

SITE = re.compile(r'(&\s*)?\brdram\s*(\[|\+)')
RW = 0x20000000


def take_expr(text, i, close):
    """From index i, return the expression up to the matching close char (']') or, for '+', up to a
    top-level ',', ')', ';' or '?' / ':' ."""
    d = 0; j = i
    while j < len(text):
        c = text[j]
        if c in '([{':
            d += 1
        elif c in ')]}':
            if d == 0:
                return text[i:j]
            d -= 1
        elif d == 0 and close == '+' and c in ',;?:':
            return text[i:j]
        j += 1
    return text[i:j]


def top_split_plus(e):
    """Split a pointer-level sum `A + B - C` into top-level terms."""
    out, d, cur = [], 0, ''
    for c in e:
        if c in '([':
            d += 1
        elif c in ')]':
            d -= 1
        if d == 0 and c in '+-' and cur.strip():
            out.append(cur); cur = c if c == '-' else ''
            continue
        cur += c
    if cur.strip():
        out.append(cur)
    return out


def strip_parens(e):
    e = e.strip()
    while e.startswith('(') and c61._skip_parens(e, 0) == len(e):
        e = e[1:-1].strip()
    return e


def top_mask(e):
    """Value of a top-level `X & M` / `(X & M) ^ k` mask, else None."""
    e = strip_parens(e)
    m = re.search(r'&\s*\(?\s*(0[xX][0-9A-Fa-f]+|\d+)[uUlL]*\s*\)?\s*$', e)
    d = 0
    if m:
        pre = e[:m.start()]
        if pre.count('(') == pre.count(')'):
            v = int(m.group(1), 0)
            return v
    m = re.match(r'^\((.*)\)\s*\^\s*(0[xX][0-9A-Fa-f]+|\d+)[uU]?$', e)
    if m and c61._skip_parens(e, 0) == len(m.group(1)) + 2:
        v = top_mask(m.group(1))
        if v is not None:
            return v | int(m.group(2), 0)
    return None


def literal(e):
    e = strip_parens(e)
    m = re.fullmatch(r'(0[xX][0-9A-Fa-f]+|\d+)[uUlL]*(?:\s*\^\s*(0[xX][0-9A-Fa-f]+|\d+)[uU]?)?', e)
    if m:
        return int(m.group(1), 0) ^ (int(m.group(2), 0) if m.group(2) else 0)
    m = re.fullmatch(r'(0[xX][0-9A-Fa-f]+|\d+)[uUlL]*\s*\+\s*(0[xX][0-9A-Fa-f]+|\d+)[uUlL]*', e)
    if m:
        return int(m.group(1), 0) + int(m.group(2), 0)
    return None


def classify_term(t, text, pos):
    t = strip_parens(t.lstrip('+').strip())
    neg = False
    if t.startswith('-'):
        neg = True; t = t[1:].strip()
    v = literal(t)
    if v is not None:
        return ('NEGCONST' if neg else ('CONST' if v < RW else 'CONSTHI')), hex(v)
    mk = top_mask(t)
    if mk is not None and mk < RW and not neg:
        return 'MASK', hex(mk)
    k, why = c61.combine(c61.operands(t, text, pos))
    if k == 'S64' and re.search(r'\(\s*int64_t\s*\)\s*\(\s*int32_t\s*\)', t) and not re.search(r'0[xX][fF]{8}80000000', t):
        return 'SEXTRAW', 'sign-extended KSEG0 address added unbiased: rdram - 2 GB + phys'
    if neg:
        return 'SIGNED', 'negated ' + why
    return {'U32': 'U32', 'S32': 'SIGNED', 'S64': 'WIDE', 'Z64': 'WIDE', 'U64': 'WIDE'}.get(k, 'UNK'), k + ':' + why


def classify(expr, text, pos, bracket):
    terms = [expr] if bracket else top_split_plus(expr)
    cls = [classify_term(t, text, pos) for t in terms]
    ks = [c for c, _ in cls]
    why = ' | '.join('%s:%s' % c for c in cls)
    if len(ks) == 1:
        k = ks[0]
        return ({'NEGCONST': 'SIGNED', 'CONSTHI': 'UNK', 'SEXTRAW': 'NEG'}.get(k, k)), why
    if 'SEXTRAW' in ks:
        return 'NEG', why
    if all(k in ('CONST', 'MASK') for k in ks):
        return 'MASK', why
    if 'UNK' in ks or 'CONSTHI' in ks:
        return 'UNK', why
    if 'WIDE' in ks:
        return 'WIDE', why
    if 'SIGNED' in ks or 'NEGCONST' in ks:
        return 'SIGNED', why
    if 'U32' in ks:
        return 'U32+K', why
    return 'UNK', why


def scan(path, text):
    rows = []
    text = re.sub(r'/\*.*?\*/', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), text, flags=re.S)   # block comments
    for m in SITE.finditer(text):
        ls = text.rfind('\n', 0, m.start()) + 1
        pre = text[ls:m.start()]
        if re.match(r'\s*(//|\*|/\*|#\s*define)', pre) or '//' in pre:
            continue
        if re.search(r'\b(uint8_t|char)\s*\*\s*$', pre):   # a declaration `uint8_t* rdram + ...` cannot occur; skip params
            pass
        bracket = m.group(2) == '['
        expr = take_expr(text, m.end(), ']' if bracket else '+')
        line = text.count('\n', 0, m.start()) + 1
        c, why = classify(expr, text, m.start(), bracket)
        rows.append((path, line, ('&' if m.group(1) else '') + ('[]' if bracket else '+'), ' '.join(expr.split())[:70], c, why[:120]))
    return rows


# Hand verdicts for every non-contained row (s7362).  key: (path suffix, expression prefix) -> verdict.
REVIEWED = {
    ('dpc_bridge.cpp', 'p + 4u'): 'MASK: p in [from&~7, to-8], to = end & 0x3FFFFFF (s7486 EK window; s7558 verdict)',
    ('s7521_ucode_watch.cpp', 'f.phys ^ 3'): 'MASK: (ucode ptr & 0x1FFFFFFF) + <=0x100 (s7521 ctl flip; s7558 verdict)',
    ('mod_config_api.cpp', 'offset'): 'SEXT-BIASED: str_rdram - 0xFFFFFFFF80000000 in [0,4G)',
    ('sp.cpp', 'i ^ 3'): 'BOUNDED: i < 0x800000',
    ('events.cpp', 'addrs[0]'): 'U32-ENV: ROGUESQ_DD_ADDRS strtoul->uint32, in [0,4G)',
    ('events.cpp', 'addrs[i]'): 'U32-ENV: ROGUESQ_DD_ADDRS strtoul->uint32, in [0,4G)',
    ('events.cpp', 'ia[i]'): 'U32-ENV: ROGUESQ_DD_IADDRS strtoul->uint32, in [0,4G)',
    ('events.cpp', 'a'): 'U32-ENV: range-for over std::vector<uint32_t> (evaluator misses `T a :`)',
    ('main.cpp', 'base + i * 4u'): 'CHECKED: task_ptr == 0x800377C8 -> base 0x377C8, i < 16',
    ('main.cpp', 'base + (i * 4u ^ 3u)'): 'CHECKED: task_ptr == 0x800377C8, i < 16',
    ('main.cpp', 'base + field * 4u'): 'CHECKED: task_ptr == 0x800377C8, field <= 14',
    ('main.cpp', 'ranges[i]'): 'CONST: {0x726200,0x732A10}',
    ('main.cpp', '(uintptr_t)(slot & 0x1FFFFFFu)'): 'MASK: 0x1FFFFFF',
    ('main.cpp', '0x%X'): 'STRING: format text, not code',
    ('rt64_render_context.cpp', '(pl - 0x80000000u) + 0x4C'): 'CHECKED: 0x80001000 <= pl < ram_top-0x100',
    ('upstream_compat.cpp', '0x130DB0u + r * 64'): 'BOUNDED: r in [20,24)',
    ('upstream_compat.cpp', '0x131DB0u + r * 64'): 'BOUNDED: r in [20,24)',
    ('upstream_compat.cpp', '0x132DB0u + 4 * k'): 'BOUNDED: k in [0,4)',
    ('upstream_compat.cpp', 'P'): 'STRING: format text, not code',
    ('upstream_compat.cpp', '0x17D000u + i * 4u'): 'BOUNDED: i < 0x480',
    ('upstream_compat.cpp', 'A[i]'): 'CONST: A[3] literal table',
    ('upstream_compat.cpp', '((uint64_t)(int64_t)(int32_t)g - 0xFFFFFFFF80000000ull) ^ 3u'): 'SEXT-BIASED: [0,4G)',
    ('upstream_compat.cpp', '((uint64_t)(int64_t)(int32_t)0x8011A8C8u'): 'SEXT-BIASED const',
    ('upstream_compat.cpp', '((uint64_t)(int64_t)(int32_t)0x8011A8C9u'): 'SEXT-BIASED const',
    ('upstream_compat.cpp', '((uint64_t)(int64_t)(int32_t)(0x80128EA8u + i)'): 'SEXT-BIASED const, i < 16',
}
CONTAINED = {'MASK', 'CONST', 'U32'}


def reviewed(r):
    for (suf, pre), v in REVIEWED.items():
        if r[0].endswith(suf) and r[3] == pre or (r[0].endswith(suf) and len(pre) > 12 and r[3].startswith(pre)):
            return v
    return None


def scope():
    pats = ['src/**/*.c', 'src/**/*.cpp', 'src/**/*.h', 'src/**/*.hpp',
            'lib/N64ModernRuntime/librecomp/src/*.cpp', 'lib/N64ModernRuntime/librecomp/include/librecomp/*.hpp',
            'lib/N64ModernRuntime/ultramodern/src/*.cpp', 'lib/N64ModernRuntime/ultramodern/include/ultramodern/*.h*']
    out = []
    for p in pats:
        out += glob.glob(p, recursive=True)
    return sorted(set(out))


SELFTEST = [
    ('uint32_t a = 5; x = rdram[(a + 1) & 0x007FFFFFu];', 'MASK'),
    ('y = *(uint32_t*)(rdram + 0x137DBCu);', 'CONST'),
    ('uint32_t w = f(); v = *(uint32_t*)(rdram + (w - 0x80000000u));', 'U32'),
    ('int k = -4; v = rdram[k];', 'SIGNED'),
    ('uint32_t pl = f(); memcpy(v, rdram + (pl - 0x80000000u) + 0x4C, 12);', 'U32+K'),
    ('uint64_t q = f(); v = rdram[q];', 'WIDE'),
    ('v = rdram[s.field];', 'UNK'),
    ('uint32_t p = f(); v = rdram[p ^ 3u];', 'U32'),
    ('uint32_t g = f(); const uint8_t* q = rdram + (int64_t)(int32_t)g;', 'NEG'),
    ('uint32_t g = f(); v = rdram[((uint64_t)(int64_t)(int32_t)g - 0xFFFFFFFF80000000ull) ^ 3u];', 'WIDE'),
]


def selftest():
    bad = 0
    for src, want in SELFTEST:
        r = scan('<t>', src)
        got = r[0][4] if r else None
        ok = got == want
        bad += not ok
        print('%s %-7s want %-7s | %s' % ('PASS' if ok else 'FAIL', got, want, src))
    print('selftest', 'PASS' if not bad else 'FAIL %d' % bad)
    return bad


def main():
    if '--selftest' in sys.argv:
        sys.exit(1 if selftest() else 0)
    rows = []
    paths = scope()
    if '--gen' in sys.argv:
        g = sys.argv[sys.argv.index('--gen') + 1]
        paths = sorted(glob.glob(os.path.join(g, '*.c')))
    for p in paths:
        try:
            rows += scan(p, open(p, errors='replace').read())
        except IsADirectoryError:
            pass
    from collections import Counter
    cnt = Counter(r[4] for r in rows)
    open_rows = 0
    for r in rows:
        if r[4] in CONTAINED:
            continue
        v = reviewed(r)
        open_rows += v is None
        print('%s:%d %s %-6s %s  [%s] -> %s' % (r[0], r[1], r[2], r[4], r[3], r[5], v or 'OPEN'))
    print('rows', len(rows), dict(cnt), 'open', open_rows)
    if '--check' in sys.argv and open_rows:
        sys.exit(1)


if __name__ == '__main__':
    main()
