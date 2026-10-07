"""M5 A11 de-stub arm: yield inside the waitForAnyAudioSlot spin.

ROGUESQ_WAITFORSLOT_YIELD=N (N>0) calls yield_self_1ms every N laps while no slot
is active, so audio ticks (musyxRenderVoiceSamples) can run and clear the slot
byte instead of the 500k cap firing. Unset = unchanged (control arm).

ORIGIN: s4196 showed the slot-0 byte clears only after the cap fires; the spin is
non-yielding and starves the producer. Yield tests that starvation directly.
Patches the generated funcs_15.c and the fixup_game_funcs.py template.
"""
from pathlib import Path

root = Path(__file__).resolve().parents[2] / "N64Recomp"
gen = root / "RecompiledFuncs" / "funcs_15.c"
fix = root / "fixup_game_funcs.py"
MARK = "PATCH: s4197 waitforslot yield"

OLD = "        if (ctx->r2 == 0 && g_audio_drain_iters >= s_waitforslot_guard_cap) {\n"
NEW = (
    "        if (ctx->r2 == 0) { /* PATCH: s4197 waitforslot yield */\n"
    "            static long s_wfs_yield_n = -1; static long s_wfs_yields = 0;\n"
    "            if (s_wfs_yield_n < 0) { const char* e = getenv(\"ROGUESQ_WAITFORSLOT_YIELD\"); s_wfs_yield_n = (e && e[0]) ? atol(e) : 0; }\n"
    "            if (s_wfs_yield_n > 0 && (g_audio_drain_iters % s_wfs_yield_n) == 0) {\n"
    "                extern void yield_self_1ms(uint8_t* rdram);\n"
    "                yield_self_1ms(rdram); ++s_wfs_yields;\n"
    "                if (s_wfs_yields <= 5 || (s_wfs_yields % 1000) == 0) { fprintf(stderr, \"[waitforslot-yield] yields=%ld iters=%ld\\n\", s_wfs_yields, g_audio_drain_iters); fflush(stderr); }\n"
    "            }\n"
    "        }\n"
) + OLD


def tpl(s):
    out = ""
    for line in s.splitlines(keepends=True):
        out += '            "' + line[:-1].replace("\\", "\\\\").replace('"', '\\"') + '\\n"\n'
    return out


t = gen.read_text()
if MARK not in t:
    assert t.count(OLD) == 1, t.count(OLD)
    gen.write_text(t.replace(OLD, NEW))
    print("patched gen")
t = fix.read_text()
if MARK not in t:
    o, n = tpl(OLD), tpl(NEW)
    assert t.count(o) == 1, t.count(o)
    fix.write_text(t.replace(o, n))
    print("patched template")
