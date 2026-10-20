"""s5642: env-gated (ROGUESQ_LOG_HUDBIT=1) gate/exit log inside allocAndConfigureNewVoice (0x8009B160 region).
s5641 showed alloc is entered for every speech clip; this says whether it reaches the voice-start calls
(0x8009B1F4 jal 0x8009BE40, 0x8009B220 jal 0x8009AF60) or bails at L_8009B230. Entry line prints the
pool count 0x80154670, the first 4 slot-used bytes at 0x80154620 + i*0x1228, and a0 (compared against count at B0A8).
Idempotent; replayed from fixup_game_funcs_vendored.py per file."""
TAG = "PATCH: s5642 allocgate log"
def _pr(tag, extra=""):
    return ('    { static int s_n = 0, s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
            'if (s_e && ++s_n <= 60) fprintf(stderr, "[aloc] %s n=%%d%s\\n", s_n%s); } /* %s */\n' % (tag, extra[0], extra[1], TAG))
ENTRY = _pr("entry", (" a0=0x%X cnt=0x%X u0=%u u1=%u u2=%u u3=%u",
    ", U32(ctx->r4), U32(MEM_W(0x4670, 0xFFFFFFFF80150000ull)), (unsigned)MEM_BU(0x4620, 0xFFFFFFFF80150000ull), "
    "(unsigned)MEM_BU(0x4620+0x1228, 0xFFFFFFFF80150000ull), (unsigned)MEM_BU(0x4620+2*0x1228, 0xFFFFFFFF80150000ull), "
    "(unsigned)MEM_BU(0x4620+3*0x1228, 0xFFFFFFFF80150000ull)"))
def apply(text):
    i = text.find("RECOMP_FUNC void allocAndConfigureNewVoice(")
    if i < 0: return text, 0
    j = text.find("\n}\n", i)
    body = text[i:j]
    if TAG in body: return text, 0
    k = body.find("{\n") + 2
    body = body[:k] + ENTRY + body[k:]
    for marker, tag in (("    // 0x8009B1F4: jal", "reach_B1F4"), ("    // 0x8009B220: jal", "reach_B220"), ("L_8009B230:\n", "label_B230")):
        m = body.find(marker)
        if m < 0: continue
        if marker.startswith("L_"): m += len(marker)
        body = body[:m] + _pr(tag, ("", "")) + body[m:]
    return text[:i] + body + text[j:], 1
if __name__ == "__main__":
    import pathlib
    p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_26.c")
    t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print(p.name, n)
