"""s5644: env-gated (ROGUESQ_LOG_HUDBIT=1) downstream-of-alloc speech voice log. NOTE queue 0x80154650 is a pool LOCK
(recv=lock/send=unlock in alloc/stop/setMix/servicePool/getProgress/initTable), not a consumer queue. The real consumer is
serviceVoicePoolFrame -> serviceStreamingVoice(slot) which polls slot+0x11AC queue (osRecvMesg @0x8009BF44, <0 = empty) and
calls consumeVoiceSamples. Logs: entry of serviceVoicePoolFrame/serviceStreamingVoice/consumeVoiceSamples/initMusyXVoiceSlot
(first 30 + every 3000th; streaming: also on ANY change of the slot tuple), and the recv result at BF44.
Slot tuple = b+0x1200, w+0x120C, w+0x11A4, w+0x11C8, w+0x11D0, b+0x11DC. Idempotent."""
import re
TAG = "PATCH: s5644 voicedown log"
NAMES = {"serviceVoicePoolFrame", "serviceStreamingVoice", "consumeVoiceSamples", "initMusyXVoiceSlot"}
EN = '{ static int s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } if (s_e)'
def _blk(nm):
    base = ('    %s { static int s_n = 0; s_n++; if (s_n <= 30 || (s_n %% 3000) == 0) fprintf(stderr, "[vdown] %s n=%%d a0=0x%%X a1=0x%%X a2=0x%%X\\n", s_n, '
            'U32(ctx->r4), U32(ctx->r5), U32(ctx->r6)); } } /* %s */\n' % (EN, nm, TAG))
    if nm != "serviceStreamingVoice": return base
    chg = ('    %s { static uint32_t s_a[8]; static uint64_t s_t[8]; static int s_c = 0; uint32_t sl = U32(ctx->r4); '
           'if (sl >= 0x80000000u && sl < 0x80780000u - 0x1228) { uint64_t t = (uint64_t)MEM_BU(0X1200, ctx->r4) | ((uint64_t)U32(MEM_W(0X120C, ctx->r4)) << 8) '
           '^ ((uint64_t)U32(MEM_W(0X11A4, ctx->r4)) * 1000003ull) ^ ((uint64_t)U32(MEM_W(0X11C8, ctx->r4)) * 998244353ull) ^ ((uint64_t)U32(MEM_W(0X11D0, ctx->r4)) << 3) ^ ((uint64_t)MEM_BU(0X11DC, ctx->r4) << 50); '
           'int k = -1; for (int i = 0; i < s_c; i++) if (s_a[i] == sl) k = i; if (k < 0 && s_c < 8) { k = s_c++; s_a[k] = sl; s_t[k] = ~t; } '
           'if (k >= 0 && s_t[k] != t) { s_t[k] = t; static int s_p = 0; if (++s_p <= 120) fprintf(stderr, "[vdown] slotchg slot=0x%%X b1200=%%u w120C=0x%%X w11A4=0x%%X w11C8=0x%%X w11D0=0x%%X b11DC=%%u\\n", sl, '
           '(unsigned)MEM_BU(0X1200, ctx->r4), U32(MEM_W(0X120C, ctx->r4)), U32(MEM_W(0X11A4, ctx->r4)), U32(MEM_W(0X11C8, ctx->r4)), U32(MEM_W(0X11D0, ctx->r4)), (unsigned)MEM_BU(0X11DC, ctx->r4)); } } } } /* %s */\n' % (EN, TAG))
    return base + chg
RECV = ('    %s { static int s_r = 0, s_neg = 0, s_ok = 0; if ((int32_t)ctx->r2 < 0) s_neg++; else s_ok++; if (++s_r %% 5000 == 0 || (s_ok > 0 && s_ok <= 20 && (int32_t)ctx->r2 >= 0)) '
        'fprintf(stderr, "[vdown] slotrecv n=%%d ok=%%d empty=%%d last=%%d\\n", s_r, s_ok, s_neg, (int)(int32_t)ctx->r2); } } /* %s */\n' % (EN, TAG))
def apply(text):
    out, n = [], 0
    for part in re.split(r'(?m)^(?=RECOMP_FUNC void )', text):
        m = re.match(r'RECOMP_FUNC void (\w+)\(', part)
        if m and m.group(1) in NAMES and TAG not in part[:3000]:
            j = part.find("{\n") + 2
            part = part[:j] + _blk(m.group(1)) + part[j:]; n += 1
            if m.group(1) == "serviceStreamingVoice":
                k = part.find("osRecvMesg_recomp(rdram, ctx);\n")
                if k >= 0:
                    k += len("osRecvMesg_recomp(rdram, ctx);\n"); part = part[:k] + RECV + part[k:]
        out.append(part)
    return "".join(out), n
if __name__ == "__main__":
    import pathlib
    base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    for f in ("funcs_26.c", "funcs_27.c"):
        p = base / f; t = p.read_text(); t2, n = apply(t)
        if n: p.write_text(t2)
        print(f, n)
