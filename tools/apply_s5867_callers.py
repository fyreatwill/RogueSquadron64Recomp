"""s5867: per-caller census for updatePlayerCraftPhysics (G1 frozen-ship gate hunt).

Counts, per second, entries of each of the 9 per-craft update functions that call updatePlayerCraftPhysics, the
call-site reach (after any early return), and entries of updatePlayerCraftPhysics itself, with the last entry ra
(the dispatcher return address).  [plc] line prints under ROGUESQ_PLAYER_DUMP, with player record words
+0x00/+0x14/+0x18 (0x80137DB0 base) for flag context.  Control: pre-freeze/post-A windows must show non-zero counts.
Idempotent; registered in fixup_game_funcs_vendored.py after apply_s5866_plwatch.py.
"""
import pathlib
import re
import sys

T = "PATCH: s5867 callers"
T2 = "PATCH: s5867 msg"
FUNCS = ["composeEffectObjectTransformMatrix", "playWeaponFireSound", "resetEngineTrailQuads", "tickCraftAbilityCooldown",
         "updateVwingEngineEffect", "computeFalconFlightTransform", "computeTieInterceptorTransform",
         "computeT16Transform", "buildNabooSubmodelTransform", "updatePlayerCraftPhysics"]
EXT = "extern void rs64_s5867_hit(int, uint8_t*, uint32_t);"
CALL = "    updatePlayerCraftPhysics(rdram, ctx);\n"
DEF = r'''
void rs64_s5867_hit(int idx, uint8_t* r, uint32_t ra) { /* ''' + T + r''' */
    extern long long rs64_s5773_ms(void);
    static uint32_t n[40], lra[40]; static long long last = -1; static int e = -1;
    if (e < 0) { const char* s = getenv("ROGUESQ_PLAYER_DUMP"); e = (s && s[0]) ? 1 : 0; }
    if (!e) return;
    n[idx]++; lra[idx] = ra;
    if (idx == 1 && n[1] == 1) { static int bt = 0; if (bt++ < 3) { /* host backtrace + table scan */
        extern int backtrace(void**, int); void* fr[16]; int k = backtrace(fr, 16);
        fprintf(stderr, "[plc-bt] slide_ref=%p frames:", (void*)rs64_s5867_hit); for (int i = 0; i < k; i++) fprintf(stderr, " %p", fr[i]); fprintf(stderr, "\n");
        if (bt == 1) { fprintf(stderr, "[plc-tab] words==800B4588 at:"); for (uint32_t a = 0; a < 0x400000; a += 4) if (*(uint32_t*)(r + a) == 0x800B4588u) fprintf(stderr, " %08x", 0x80000000u + a); fprintf(stderr, "\n"); } } }
    long long ms = rs64_s5773_ms(); if (last < 0) last = ms;
    if (ms - last >= 1000) {
        char b[900]; int o = 0;
        for (int i = 0; i < 40; i++) if (n[i]) { if (i >= 20) o += snprintf(b + o, sizeof(b) - o, " msg%d:%u", i - 20, n[i]); else o += snprintf(b + o, sizeof(b) - o, " %s%d:%u", i >= 10 ? "call" : "ent", i % 10, n[i]); }
        uint32_t w0 = 0, w14 = 0, w18 = 0;
        if (r) { w0 = *(uint32_t*)(r + 0x137DC0); w14 = *(uint32_t*)(r + 0x137DC0 + 0x14); w18 = *(uint32_t*)(r + 0x137DC0 + 0x18); }
        fprintf(stderr, "[plc] t=%lld rec0=%08x rec14=%08x rec18=%08x g10CA1C=%08x |%s\n", ms, w0, w14, w18, *(uint32_t*)(r + 0x10CA1C), b);
        memset(n, 0, sizeof(n)); last = ms;
    }
}
'''


def apply(text, name=""):
    if T in text:
        return text, 0
    cnt = 0
    for i, f in enumerate(FUNCS):
        m = re.search(r"RECOMP_FUNC void " + f + r"\(uint8_t\* rdram, recomp_context\* ctx\) \{\n", text)
        if not m:
            continue
        ins = "    " + EXT + " rs64_s5867_hit(%d, rdram, (uint32_t)ctx->r31); /* %s */\n" % (i, T)
        text = text[:m.end()] + ins + text[m.end():]
        cnt += 1
    if name in ("funcs_28.c", "funcs_31.c", "funcs_32.c"):
        # call-site markers: attribute each call line to its enclosing function
        out, cur = [], -1
        for line in text.split("\n"):
            m = re.match(r"RECOMP_FUNC void (\w+)\(", line)
            if m:
                cur = FUNCS.index(m.group(1)) if m.group(1) in FUNCS else -1
            if line + "\n" == CALL and 0 <= cur < 9:
                out.append("    " + EXT + " rs64_s5867_hit(%d, rdram, (uint32_t)ctx->r31); /* %s */" % (10 + cur, T))
                cnt += 1
            out.append(line)
        text = "\n".join(out)
    if name == "funcs_13.c":
        text += DEF + "\n"
        cnt += 1
    return (text + "\n/* " + T + " */\n" if cnt else text), cnt


if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    tot = 0
    for p in sorted(base.glob("funcs_*.c")):
        t = p.read_text()
        t2, n = apply(t, p.name)
        if t2 != t:
            p.write_text(t2)
        tot += n
    print("sites patched:", tot)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5867_callers" in s:
        print("fixup already")
    else:
        lst = '    "apply_s5866_plwatch.py",\n]\n'
        assert s.count(lst) == 1
        fp.write_text(s.replace(lst, '    "apply_s5866_plwatch.py",\n    "apply_s5867_callers.py",\n]\n', 1))
        print("fixup patched")
