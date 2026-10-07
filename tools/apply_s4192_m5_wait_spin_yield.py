"""M5 A12 de-stub arm: let the countdown wait spin yield to the real decrementer.

ROGUESQ_AUDIO_WAIT_NOPUMP=2 replaces the pump's blind spin with a spin that
calls yield_self_1ms, so the retail-shaped producer (musyxSynthFrame via the
video/audio dispatch) can run instead of the guest pumping it inline.
Mode 1 keeps the pre-s327 blind spin, unset keeps the pump. Every mode logs a
bounded [audio-wait-*] row carrying the seed countdown, so the arms share one
positive control (a row with countdown0>0 means the wait was really entered).

ORIGIN: the countdown at 0x8014998A is written only by musyxSynthFrame (s327);
the pump is a host hatch for a producer that cannot run while the guest thread
spins. The yield arm tests whether yielding alone lets the real writer run.
Diagnostic arm only: the 5000-yield cap logs and falls out, never default.

Patches BOTH the live generated funcs_24.c and the fixup_game_funcs.py template
so a regen reproduces it.
"""

from pathlib import Path

root = Path(__file__).resolve().parents[2] / "N64Recomp"
gen = root / "RecompiledFuncs" / "funcs_24.c"
fix = root / "fixup_game_funcs.py"

MODE_OLD = "s_audiowait_pump_off = (e && e[0] && e[0] != '0') ? 1 : 0; }\n"
MODE_NEW = "s_audiowait_pump_off = (e && e[0] && e[0] != '0') ? (e[0] == '2' ? 2 : 1) : 0; }\n"

C0_OLD = "        int s_audiowait_pump_iters = 0;\n"
C0_NEW = C0_OLD + "        int s_aw_c0 = (int)MEM_HU(S32(0X8015 << 16), -0X6676); /* PATCH: s4192 wait-spin yield arm */\n"

SPIN_OLD = (
    "        if (s_audiowait_pump_off) { // fallback: restore the pre-s327 blind spin for A/B (deadlocks by design)\n"
    "            while (SIGNED(S32(MEM_HU(S32(0X8015 << 16), -0X6676) << 16)) > 0) { }\n"
    "        }\n"
)
SPIN_NEW = (
    "        if (!s_audiowait_pump_off && s_aw_c0 > 0) {\n"
    "            static int s_aw_pump_n = 0;\n"
    "            if (s_aw_pump_n < 20) { s_aw_pump_n++; fprintf(stderr, \"[audio-wait-pump] countdown0=%d pumps=%d remaining=%d\\n\", s_aw_c0, s_audiowait_pump_iters, (int)MEM_HU(S32(0X8015 << 16), -0X6676)); }\n"
    "        }\n"
    "        if (s_audiowait_pump_off) { // mode 1: pre-s327 blind spin (deadlocks by design); mode 2: yielding spin\n"
    "            static int s_aw_spin_n = 0;\n"
    "            unsigned long s_aw_it = 0; int s_aw_yields = 0;\n"
    "            if (s_aw_c0 > 0 && s_aw_spin_n < 20) { fprintf(stderr, \"[audio-wait-spin-enter] mode=%d countdown0=%d\\n\", s_audiowait_pump_off, s_aw_c0); fflush(stderr); }\n"
    "            while (SIGNED(S32(MEM_HU(S32(0X8015 << 16), -0X6676) << 16)) > 0) {\n"
    "                ++s_aw_it;\n"
    "                if (s_audiowait_pump_off == 2 && (s_aw_it % 2000) == 0) {\n"
    "                    extern void yield_self_1ms(uint8_t* rdram);\n"
    "                    yield_self_1ms(rdram); ++s_aw_yields;\n"
    "                    if (s_aw_yields >= 5000) { fprintf(stderr, \"[audio-wait-spin-timeout] mode=2 countdown=%d iters=%lu\\n\", (int)MEM_HU(S32(0X8015 << 16), -0X6676), s_aw_it); fflush(stderr); break; }\n"
    "                }\n"
    "            }\n"
    "            if (s_aw_c0 > 0 && s_aw_spin_n < 20) { s_aw_spin_n++; fprintf(stderr, \"[audio-wait-spin-exit] mode=%d iters=%lu yields=%d countdown=%d\\n\", s_audiowait_pump_off, s_aw_it, s_aw_yields, (int)MEM_HU(S32(0X8015 << 16), -0X6676)); fflush(stderr); }\n"
    "        }\n"
)

PAIRS = [(MODE_OLD, MODE_NEW), (C0_OLD, C0_NEW), (SPIN_OLD, SPIN_NEW)]


def esc(s):
    """Render C text the way the fixup template spells it (python string lines)."""
    out = []
    for line in s.splitlines(keepends=True):
        body = line[:-1] if line.endswith("\n") else line
        out.append(body.replace("\\", "\\\\").replace('"', '\\"') + "\\n")
    return out


def patch_generated():
    t = gen.read_text()
    if "PATCH: s4192 wait-spin yield arm" in t:
        print("generated funcs_24.c already patched")
        return
    for old, new in PAIRS:
        if t.count(old) != 2:
            raise SystemExit(f"generated: expected 2 sites, got {t.count(old)} for {old[:50]!r}")
        t = t.replace(old, new)
    gen.write_text(t)
    print(f"patched {gen} (x2 sites)")


def template_lines(s):
    return "".join('            "' + l + '"\n' for l in esc(s))


def patch_template():
    t = fix.read_text()
    if "PATCH: s4192 wait-spin yield arm" in t:
        print("fixup template already patched")
        return
    for old, new in PAIRS:
        o, n = template_lines(old), template_lines(new)
        if old is MODE_OLD:
            # MODE line is a fragment inside a longer template line.
            o = old.replace("\\", "\\\\").replace('"', '\\"')[:-1]
            n = new.replace("\\", "\\\\").replace('"', '\\"')[:-1]
        if t.count(o) != 1:
            raise SystemExit(f"template: expected 1 site, got {t.count(o)} for {o[:60]!r}")
        t = t.replace(o, n)
    fix.write_text(t)
    print(f"patched {fix}")


patch_generated()
patch_template()
