"""s5640: env-gated (ROGUESQ_LOG_HUDBIT=1) entry log for the voice funnel: playSpeechClip (funcs_15) and
playObjectiveVoiceLine2 (funcs_36; lv2 uses Line2, not Line1). First 40 calls + every 1000th. playSpeechClip also logs
every early-out gate input (0x80139C8E/8C/72 bytes, word 0x80130B50) so one run says which gate eats the call.
Idempotent; replayed from fixup_game_funcs_vendored.py per file."""
import re
TAG = "PATCH: s5640 speechclip log"
B = "0xFFFFFFFF80140000ull"
def _blk(nm, gates):
    g = ""
    if gates:
        g = (' g8E=%%u g8C=%%u g72=%%u w0B50=%%d' )
        ga = (', (unsigned)MEM_BU(-0X6372, %s), (unsigned)MEM_BU(-0X6374, %s), (unsigned)MEM_BU(-0X638E, %s), (int)MEM_W(0XB50, 0xFFFFFFFF80130000ull)' % (B, B, B))
    else:
        ga = ""
    return ('    { static int s_n = 0, s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
            'if (s_e) { s_n++; if (s_n <= 40 || (s_n %% 1000) == 0) '
            'fprintf(stderr, "[speech] %s n=%%d a0=0x%%X a1=0x%%X a2=0x%%X a3=0x%%X%s\\n", s_n, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7)%s); } } /* %s */\n'
            % (nm, g.replace('%%', '%'), ga, TAG)).replace('%s_n', 's_n')
def apply(text, names):
    out, n = [], 0
    for part in re.split(r'(?m)^(?=RECOMP_FUNC void )', text):
        m = re.match(r'RECOMP_FUNC void (\w+)\(', part)
        if m and m.group(1) in names and TAG not in part[:900]:
            j = part.find("{\n") + 2
            part = part[:j] + _blk(m.group(1), m.group(1) == "playSpeechClip") + part[j:]; n += 1
        out.append(part)
    return "".join(out), n
if __name__ == "__main__":
    import pathlib
    base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    for f, nm in (("funcs_15.c", {"playSpeechClip"}), ("funcs_36.c", {"playObjectiveVoiceLine2"})):
        p = base / f; t = p.read_text(); t2, n = apply(t, nm)
        if n: p.write_text(t2)
        print(f, n)
