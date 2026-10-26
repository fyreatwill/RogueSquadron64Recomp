"""s6287 dd3 DL-chunk cache: ROGUESQ_PPLOG=1 -> count pushes (sw rK,0x63B0(r1) at the S5798-tagged sites) and pops
(inline `lui 0x8011; lw rK,0x63B0(rK)`) per guest pc between consecutive beginFrameDLChunk calls, and print
begins ROGUESQ_PPLOG_LO..HI (default 38..48) from rs64_s6098 (needs ROGUESQ_DLPOOLLOG=1). Applies to every funcs_*.c.
Idempotent. C++ side: rs64_s6287* in src/main/upstream_compat.cpp."""
import re, pathlib, glob
TAG = "PATCH: s6287 ppcount"
EXT = "extern void rs64_s6287(int, uint32_t); /* " + TAG + " */\n"
_ST = re.compile(r"(RS64_S5798_ST\((0x[0-9A-Fa-f]+u), 0X63B0, ctx->r\d+, 4\);) \}")
_LD = re.compile(r"^    ctx->r(\d+) = MEM_W\(ctx->r\1, 0X63B0\);$")
_PC = re.compile(r"^    // (0x[0-9A-Fa-f]{8}):")
def apply(text):
    if TAG in text: return text, 0
    out, n, pc = [], 0, None
    for ln in text.split("\n"):
        m = _PC.match(ln)
        if m: pc = m.group(1)
        if _ST.search(ln):
            ln = _ST.sub(lambda m: m.group(1) + " rs64_s6287(1, %s); }" % m.group(2), ln); n += 1
        elif _LD.match(ln) and pc:
            out.append("    rs64_s6287(0, %su); /* %s */" % (pc, TAG)); n += 1
        out.append(ln)
    text = "\n".join(out)
    if n:
        j = text.find("RECOMP_FUNC"); text = text[:j] + EXT + text[j:]
    return text, n
if __name__ == "__main__":
    for f in sorted(glob.glob("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c")):
        p = pathlib.Path(f); t = p.read_text(); t2, n = apply(t)
        if n: p.write_text(t2); print(p.name, "x%d" % n)
