"""s5641: env-gated (ROGUESQ_LOG_HUDBIT=1) entry log for the speech *consumer* path behind playSpeechClip's ring:
tickSpeechSubsystem, enqueueSpeechClip, queueSpeechClipWithPriority, advanceSpeechRingAndStopHead, loadSpeechFile,
findFreeSpeechVoiceSlot, allocAndConfigureNewVoice. First 40 calls (tick: first 5 + every 600th) + every 1000th.
Prints a0-a3 and the queue free-count byte 0x80139C72. One run says where the funnel stops after playSpeechClip enqueues.
Idempotent; replayed from fixup_game_funcs_vendored.py per file."""
import re
TAG = "PATCH: s5641 speechpath log"
NAMES = {"tickSpeechSubsystem", "enqueueSpeechClip", "queueSpeechClipWithPriority", "advanceSpeechRingAndStopHead",
         "loadSpeechFile", "findFreeSpeechVoiceSlot", "allocAndConfigureNewVoice"}
def _blk(nm):
    lim = "s_n <= 5 || (s_n % 600) == 0" if nm == "tickSpeechSubsystem" else "s_n <= 40 || (s_n % 1000) == 0"
    return ('    { static int s_n = 0, s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
            'if (s_e) { s_n++; if (%s) fprintf(stderr, "[spath] %s n=%%d a0=0x%%X a1=0x%%X a2=0x%%X a3=0x%%X g72=%%u\\n", s_n, '
            'U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), (unsigned)MEM_BU(-0X638E, 0xFFFFFFFF80140000ull)); } } /* %s */\n'
            % (lim, nm, TAG))
def apply(text):
    out, n = [], 0
    for part in re.split(r'(?m)^(?=RECOMP_FUNC void )', text):
        m = re.match(r'RECOMP_FUNC void (\w+)\(', part)
        if m and m.group(1) in NAMES and TAG not in part[:1200]:
            j = part.find("{\n") + 2
            part = part[:j] + _blk(m.group(1)) + part[j:]; n += 1
        out.append(part)
    return "".join(out), n
if __name__ == "__main__":
    import pathlib
    base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    for f in ("funcs_15.c", "funcs_16.c", "funcs_26.c"):
        p = base / f; t = p.read_text(); t2, n = apply(t)
        if n: p.write_text(t2)
        print(f, n)
