#!/usr/bin/env python3
"""s7784 gate: every s5660 unaligned-store hook must report the store's DESTINATION, i.e. its ADD32 register must be the BASE
register of the do_swl/do_swr/do_sdl/do_sdr call it precedes (do_sxx(rdram, offset, base, value)).

Found s7784: tools/apply_s5660_unaligned_store_census.py took the register from the VALUE slot, so all 404 hooks since s5660
reported value+offset. That made s7783 read vertex words (0x006F0004-class packed coords) as "DL chunks inside the framebuffer
pair" (item 32 H-overlap); with the base register the same route gives 0 DL stores in any FB slot and retail's 720000 pool.
Usage: s7784_ustore_base_census.py [--controls] [RecompiledFuncs dir]
Prints hooks=<n> ok=<n> bad=<n> orphan=<n> (hook not followed by a do_s* call). Exit 0 iff hooks>0, bad=0, orphan=0.
--controls (iron rule 1): a planted wrong-register hook must count bad=1, a planted correct one bad=0, else exit 3."""
import pathlib, re, sys

HOOK = re.compile(r"\{ uint32_t s5660_a = U32\(ADD32\((ctx->r\d+), [^)]+\)\) & ~3u; rs64_s5660_ustore\((0x[0-9A-Fa-f]+)u[^\n]*PATCH: s5660 \*/\n([^\n]*)")
CALL = re.compile(r"do_(?:swl|swr|sdl|sdr)\(rdram, [^,]+, (ctx->r\d+), (ctx->r\d+)\);")


def scan(text):
    hooks = ok = bad = orphan = 0
    first_bad = []
    for m in HOOK.finditer(text):
        hooks += 1
        c = CALL.search(m.group(3))
        if not c:
            orphan += 1
            continue
        if m.group(1) == c.group(1):
            ok += 1
        else:
            bad += 1
            if len(first_bad) < 5:
                first_bad.append("%s hook=%s base=%s" % (m.group(2), m.group(1), c.group(1)))
    return hooks, ok, bad, orphan, first_bad


def controls():
    good = ("    { uint32_t s5660_a = U32(ADD32(ctx->r3, 0X0)) & ~3u; rs64_s5660_ustore(0x8000D5A8u, s5660_a, 0u, 'L'); } /* PATCH: s5660 */\n"
            "    { RS64_S7488_UST(0x8000D5A8u, 178, ctx->r3, 0X0, 1); do_swl(rdram, 0X0, ctx->r3, ctx->r4); }\n")
    wrong = good.replace("ADD32(ctx->r3", "ADD32(ctx->r4", 1)
    g, w = scan(good), scan(wrong)
    okc = g[:4] == (1, 1, 0, 0) and w[:4] == (1, 0, 1, 0)
    print("controls: good=%s wrong=%s %s" % (g[:4], w[:4], "PASS" if okc else "FAIL"))
    return okc


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--controls" in sys.argv and not controls():
        return 3
    d = pathlib.Path(args[0] if args else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    tot = [0, 0, 0, 0]
    shown = []
    for p in sorted(d.glob("funcs_*.c")):
        h, o, b, r, fb = scan(p.read_text(errors="replace"))
        for i, v in enumerate((h, o, b, r)):
            tot[i] += v
        shown += ["%s: %s" % (p.name, x) for x in fb]
    print("hooks=%d ok=%d bad=%d orphan=%d" % tuple(tot))
    for s in shown[:10]:
        print("BAD", s)
    return 0 if tot[0] > 0 and tot[2] == 0 and tot[3] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
