"""s5665: env-gated (ROGUESQ_LOG_HUDBIT=1) CPU-decode gate log for the speech voice slot 0x80153420.
decodeAndFillVoiceBlock (0x8009C904) is the ONLY writer of the slot+0x198 sample buffer (called from serviceStreamingVoice
fill loop gated on 11DD==1 || 11A0!=0, 11DE>0, 11D8-11D4 < 19C-0xA0, and (11D0==0 || 11A4!=0 || 11D0-11CC>=0x25)).
Logs: [dgate] serviceStreamingVoice entry snapshot of every gate field for slot 0x80153420 (first 40 + every 500th, and on
11DD change); [dec] decodeAndFillVoiceBlock entry (slot a0, dst a1; first 40 + every 500th; counts hits with a0==0x80153420
and dst inside slot+0x198 buffer). Control: [dec] total count for ANY slot, and [dgate] entry count. Idempotent."""
import re
TAG = "PATCH: s5665 decodegate log"
EN = '{ static int s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } if (s_e)'
SL = '0x80153420u'
G = ('    %s { if (U32(ctx->r4) == %s) { static int s_n = 0; static int s_l = -1; int d = (int)MEM_BU(0X11DD, ctx->r4); s_n++; '
     'if (s_n <= 40 || (s_n %% 500) == 0 || d != s_l) { s_l = d; static int s_p = 0; if (++s_p <= 400) fprintf(stderr, '
     '"[dgate] n=%%d b11DC=%%u b11DD=%%u b11DE=%%u h11A0=0x%%X w11A4=0x%%X w11D0=0x%%X w11CC=0x%%X w11D8=0x%%X w11D4=0x%%X w19C=0x%%X w198=0x%%X\\n", '
     's_n, (unsigned)MEM_BU(0X11DC, ctx->r4), (unsigned)d, (unsigned)MEM_BU(0X11DE, ctx->r4), (unsigned)MEM_HU(0X11A0, ctx->r4), '
     'U32(MEM_W(0X11A4, ctx->r4)), U32(MEM_W(0X11D0, ctx->r4)), U32(MEM_W(0X11CC, ctx->r4)), U32(MEM_W(0X11D8, ctx->r4)), '
     'U32(MEM_W(0X11D4, ctx->r4)), U32(MEM_W(0X19C, ctx->r4)), U32(MEM_W(0X198, ctx->r4))); } } } } /* %s */\n' % (EN, SL, TAG))
D = ('    %s { static int s_t = 0, s_h = 0; s_t++; int hit = (U32(ctx->r4) == %s); if (hit) s_h++; '
     'if (s_t <= 40 || (s_t %% 500) == 0 || (hit && s_h <= 40)) fprintf(stderr, "[dec] total=%%d slotHits=%%d a0=0x%%X a1=0x%%X a2=0x%%X\\n", s_t, s_h, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6)); } } /* %s */\n' % (EN, SL, TAG))
NAMES = {"serviceStreamingVoice": G, "decodeAndFillVoiceBlock": D}
def apply(text):
    out, n = [], 0
    for part in re.split(r'(?m)^(?=RECOMP_FUNC void )', text):
        m = re.match(r'RECOMP_FUNC void (\w+)\(', part)
        if m and m.group(1) in NAMES and TAG not in part[:4000]:
            j = part.find("{\n") + 2
            part = part[:j] + NAMES[m.group(1)] + part[j:]; n += 1
        out.append(part)
    return "".join(out), n
if __name__ == "__main__":
    import pathlib
    base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    for f in ("funcs_26.c", "funcs_27.c"):
        p = base / f; t = p.read_text(); t2, n = apply(t)
        if n: p.write_text(t2)
        print(f, n)
