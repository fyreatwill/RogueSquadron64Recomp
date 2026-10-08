"""M5 A14 de-stub: let the shutdownMusyXVoices slot-scan spin yield to the host.

The loop at 0x8009BCEC..0x8009BD10 rescans voice-slot status bytes (0x80154620
+ n*0x1228) until a slot is nonzero and the index matches $a1. Retail relies on
the voice-pool worker (serviceVoicePoolFrame) preempting this thread; on the
port the guest thread owns the host thread, so the worker/VI/SI messages can
starve. ROGUESQ_A14_YIELD (unset/!=0 = on, =0 = old blind spin) calls
yield_self_1ms every 20000 backward iterations; no state is forced or cleared.
Bounded [a14-yield] log rows (first 8 + every 1000th yield) carry b0.

ORIGIN: the status byte is cleared by the guest worker (serviceVoicePoolFrame),
never by this loop; the yield only gives that writer host time (same shape as
A12, s4192). Live-tree patch (full regen is broken, REGEN WARNING s4204).
"""
from pathlib import Path

gen = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_26.c"
OLD = (
    "L_8009BD10:\n"
    "    // 0x8009BD10: bne         $a0, $a1, L_8009BCEC\n"
    "    if (ctx->r4 != ctx->r5) {\n"
)
NEW = (
    "L_8009BD10:\n"
    "    // 0x8009BD10: bne         $a0, $a1, L_8009BCEC\n"
    "    if (ctx->r4 != ctx->r5) { /* PATCH: s4296 A14 spin yield */\n"
    "        static int s_a14_on = -1; static unsigned long s_a14_it = 0, s_a14_y = 0;\n"
    "        if (s_a14_on < 0) { const char* e = getenv(\"ROGUESQ_A14_YIELD\"); s_a14_on = (e && e[0] == '0') ? 0 : 1; }\n"
    "        if (s_a14_on && (++s_a14_it % 20000ul) == 0) {\n"
    "            extern void yield_self_1ms(uint8_t* rdram);\n"
    "            yield_self_1ms(rdram); ++s_a14_y;\n"
    "            if (s_a14_y <= 8 || (s_a14_y % 1000ul) == 0) { fprintf(stderr, \"[a14-yield] n=%lu yields=%lu a0=%u a1=%u b0=0x%02X\\n\", s_a14_it, s_a14_y, (unsigned)ctx->r4, (unsigned)ctx->r5, (unsigned)MEM_BU(0, S32(0x80154620u))); fflush(stderr); }\n"
    "        }\n"
)
t = gen.read_text()
if "PATCH: s4296 A14 spin yield" in t:
    print("already patched")
else:
    if t.count(OLD) != 1:
        raise SystemExit(f"expected 1 anchor, got {t.count(OLD)}")
    gen.write_text(t.replace(OLD, NEW))
    print("patched", gen)
