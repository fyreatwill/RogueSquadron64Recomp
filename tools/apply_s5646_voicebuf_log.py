"""s5646: env-gated (ROGUESQ_LOG_HUDBIT=1) speech-voice slot buffer census. consumeVoiceSamples does NOT read the buffer
(it only advances slot+0x11D4 / state byte 0x11DD), so NEXT.md's "buffer it reads" premise was wrong. Instead, at selected
serviceStreamingVoice calls, scan the whole 0x1228-byte slot for words that look like RDRAM pointers (0x80000000..0x80780000)
and log per pointer the nonzero-byte count of the 0x800 bytes it targets + first 8 bytes. Controls: nz of 0x800 bytes at
0x80000400 (game code, must be ~nonzero) and at the slot itself. Dump schedule: calls 1,40,200,1000,5000,20000,60000 per run. Idempotent."""
import re
TAG = "PATCH: s5646 voicebuf log"
EN = '{ static int s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } if (s_e)'
BLK = ('    %s { static int s_n = 0; s_n++; if (s_n == 1 || s_n == 40 || s_n == 200 || s_n == 1000 || s_n == 5000 || s_n == 20000 || s_n == 60000) { '
       'uint32_t sl = U32(ctx->r4); if (sl >= 0x80000000u && sl < 0x80780000u - 0x1228) { '
       'fprintf(stderr, "[vbuf] dump n=%%d slot=0x%%X\\n", s_n, sl); '
       'for (uint32_t o = 0; o < 0x1228; o += 4) { uint32_t pv = U32(MEM_W(o, ctx->r4)); '
       'if (pv >= 0x80000000u && pv < 0x80780000u - 0x800u) { uint64_t tr = (uint64_t)(int64_t)(int32_t)pv; int nz = 0; '
       'for (int i = 0; i < 0x800; i++) if (MEM_BU(i, tr)) nz++; '
       'fprintf(stderr, "[vbuf]  +0x%%X -> 0x%%X nz800=%%d first8=%%02X%%02X%%02X%%02X%%02X%%02X%%02X%%02X\\n", o, pv, nz, '
       '(unsigned)MEM_BU(0, tr), (unsigned)MEM_BU(1, tr), (unsigned)MEM_BU(2, tr), (unsigned)MEM_BU(3, tr), (unsigned)MEM_BU(4, tr), (unsigned)MEM_BU(5, tr), (unsigned)MEM_BU(6, tr), (unsigned)MEM_BU(7, tr)); } } '
       '{ uint64_t t1 = 0xFFFFFFFF80000400ull; int nz1 = 0; for (int i = 0; i < 0x800; i++) if (MEM_BU(i, t1)) nz1++; fprintf(stderr, "[vbuf] control code@0x80000400 nz800=%%d\\n", nz1); } '
       '} } } } /* %s */\n' % (EN, TAG))
def apply(text):
    out, n = [], 0
    for part in re.split(r'(?m)^(?=RECOMP_FUNC void )', text):
        m = re.match(r'RECOMP_FUNC void (\w+)\(', part)
        if m and m.group(1) == "serviceStreamingVoice" and TAG not in part[:6000]:
            j = part.find("{\n") + 2
            part = part[:j] + BLK + part[j:]; n += 1
        out.append(part)
    return "".join(out), n
if __name__ == "__main__":
    import pathlib
    base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    for f in ("funcs_26.c", "funcs_27.c"):
        p = base / f; t = p.read_text(); t2, n = apply(t)
        if n: p.write_text(t2)
        print(f, n)
