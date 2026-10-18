#!/usr/bin/env python3
"""s5368: counter-only (non-rejecting) 0x100-alignment census on the free-list walk nodes.

ORIGIN: patches/heap_guards.c block_ok() requires 0x100-aligned nodes, but PatchesLib is
shadowed (s5366), so the live guards are only 4-byte-aligned. This measures whether real
walk nodes are 0x100-aligned, WITHOUT rejecting anything. ROGUESQ_A100_CTL=1 is the
positive control (predicate forced true -> every node counted/logged).
Idempotent. Usage: apply_s5368_align100_counter.py <RecompiledFuncs dir>. Run after
apply_s3285 (anchors on its ++s3285_walk line)."""
import re, sys, pathlib

MARK = "PATCH: s5368 a100 census"
pat = re.compile(
    r'(        int s_alloc_tail_guard3_bad = \((r\d+)_lo < 0x80000000u[^\n]*\+\+s3285_walk >= 0x8000u\);\n)')


def rep(m):
    r = m.group(2)
    return (
        f'        {{ /* {MARK} */\n'
        '            static int a100_ctl = -1; static unsigned a100_tot = 0, a100_mis = 0, a100_lg = 0;\n'
        '            if (a100_ctl < 0) { const char* e = getenv("ROGUESQ_A100_CTL"); a100_ctl = (e && e[0] && e[0] != \'0\') ? 1 : 0; }\n'
        f'            if ({r}_lo >= 0x80000000u && {r}_lo < 0x80800000u) {{\n'
        f'                a100_tot++; int mis = (({r}_lo & 0xFFu) != 0u) || a100_ctl; a100_mis += mis;\n'
        f'                if (mis && a100_lg < 48) {{ a100_lg++; fprintf(stderr, "[a100] site=%s node=0x%08X ra=0x%08X ctl=%d\\n", __func__, {r}_lo, U32(ctx->r31), a100_ctl); }}\n'
        '                if ((a100_tot & (a100_tot - 1u)) == 0) fprintf(stderr, "[a100-sum] site=%s tot=%u mis=%u ctl=%d\\n", __func__, a100_tot, a100_mis, a100_ctl);\n'
        '            }\n        }\n' + m.group(1))


# second census: function entry (reach control) and the guard2 head-pointer sites
ent = re.compile(r'(    unsigned s3285_walk = 0; /\* PATCH: s3285 freelist align\+cycle \*/\n)')
g2 = re.compile(r'(        uint32_t (r\d+)_lo = U32\(ctx->\2\);\n        s3285_walk = 0;\n)')


def rep_ent(m):
    return m.group(1) + (
        '    { static unsigned a100_ent = 0; a100_ent++; if ((a100_ent & (a100_ent - 1u)) == 0) '
        'fprintf(stderr, "[a100-ent] fn=%s calls=%u\\n", __func__, a100_ent); } /* PATCH: s5368 a100 census ent */\n')


def rep_g2(m):
    r = m.group(2)
    return m.group(1) + (
        f'        {{ static unsigned a100_g2 = 0, a100_g2m = 0; if ({r}_lo >= 0x80000000u && {r}_lo < 0x80800000u) {{ a100_g2++; '
        f'if ({r}_lo & 0xFFu) a100_g2m++; if ((a100_g2 & (a100_g2 - 1u)) == 0) '
        f'fprintf(stderr, "[a100-head] fn=%s tot=%u mis=%u last=0x%08X\\n", __func__, a100_g2, a100_g2m, {r}_lo); }} }} '
        '/* PATCH: s5368 a100 census head */\n')


tot = 0
for p in sorted(pathlib.Path(sys.argv[1]).glob("funcs_*.c")):
    t = p.read_text()
    if 'a100 census ent' in t or '++s3285_walk >= 0x8000u' not in t:
        continue
    t2, n = (t, 0) if MARK in t else pat.subn(rep, t)
    t2, n1 = ent.subn(rep_ent, t2)
    t2, n2 = g2.subn(rep_g2, t2)
    n += n1 + n2
    if n:
        p.write_text(t2)
        tot += n
        print(p.name, n)
print("patched", tot)
