#!/usr/bin/env python3
"""s5370: unconditional path census for allocateDisplayListBuffer / allocDLBlockToFillRectList.

ORIGIN: s5368/s5369 saw 0 head/walk lines, but their counters sat behind a range filter and the
sites are only reachable when the cached slot (0x801163B0) is zero AND findAndUnlinkSmallestEntry
returns non-null. This counts every stage unconditionally: ent (function entries), slot0 (cached
slot empty -> falls into the unlink path), g2 (head site reached, any value), g2bad (head outside
range / unaligned), g3 (walk loop-back reached), g3bad. null-return count = slot0 - g2.
Counter-only; never rejects. Idempotent. Run after apply_s5368_align100_counter.py on the
RecompiledFuncs dir."""
import re, sys, pathlib

MARK = "PATCH: s5370 path census"
PRINT = ('if (a5370_p) fprintf(stderr, "[a5370] fn=%s ent=%u slot0=%u g2=%u g2bad=%u g3=%u g3bad=%u\\n", '
         '__func__, a5370_ent, a5370_slot0, a5370_g2, a5370_g2bad, a5370_g3, a5370_g3bad);')

decl = re.compile(r'(    unsigned s3285_walk = 0; /\* PATCH: s3285 freelist align\+cycle \*/\n)')
ent = re.compile(
    r'(a100 census ent \*/\n(?:(?!\n    if \(ctx).)*?\n)(    // 0x\w+: bne +\$\w+, \$zero, L_\w+\n)(    if \(ctx->r(\d+) != 0\) \{\n)',
    re.S)
g2 = re.compile(r'(/\* PATCH: s5368 a100 census head \*/\n)(        if \((r\d+)_lo < 0x80000000u)')
g3 = re.compile(r'(        int s_alloc_tail_guard3_bad = \((r\d+)_lo < 0x80000000u[^\n]*\n)')


def site(counter, r):
    return (f'        {{ a5370_{counter}++; int bad = ({r}_lo < 0x80000000u || {r}_lo >= 0x80800000u || ({r}_lo & 3u)); '
            f'a5370_{counter}bad += bad; a5370_p = (a5370_{counter} & (a5370_{counter} - 1u)) == 0; {PRINT} }} /* {MARK} */\n')


tot = 0
for p in sorted(pathlib.Path(sys.argv[1]).glob("funcs_*.c")):
    t = p.read_text()
    if MARK in t or 'a100 census ent' not in t:
        continue
    chunks = re.split(r'(?=^RECOMP_FUNC )', t, flags=re.M)
    out = []
    n_all = 0
    for c in chunks:
        if 'a100 census ent' in c:
            c, n0 = decl.subn(lambda m: m.group(1) + '    static unsigned a5370_ent, a5370_slot0, a5370_g2, a5370_g2bad, '
                              f'a5370_g3, a5370_g3bad; int a5370_p = 0; /* {MARK} decl */\n', c)
            c, n1 = ent.subn(lambda m: m.group(1) + m.group(2) + (
                f'    a5370_ent++; if (ctx->r{m.group(4)} == 0) a5370_slot0++; '
                f'a5370_p = ((a5370_ent & (a5370_ent - 1u)) == 0) || ((a5370_ent & 0x7FFu) == 0); {PRINT} /* {MARK} */\n')
                + m.group(3), c)
            c, n2 = g2.subn(lambda m: m.group(1) + site('g2', m.group(3)) + m.group(2), c)
            c, n3 = g3.subn(lambda m: site('g3', m.group(2)) + m.group(1), c)
            print(p.name, n0, n1, n2, n3)
            n_all += n0
        out.append(c)
    if n_all:
        p.write_text(''.join(out))
        tot += n_all
print("patched", tot)
