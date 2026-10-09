"""M5 step 7: log entries to stopVoiceSlotSynced / stopVoiceByHandle / shutdownMusyXVoices.

Diagnostic only (no state change). Answers which guest path writes status 0x03
to 0x80154620 in the port's title->hangar transition, where retail never
executes 0x8009B30C. Rows: [s4471-stop] fn=.. phase=.. thr=.. a0=.. b0=.. n=..
Live-tree patch (full regen is broken, REGEN WARNING s4204).
"""
from pathlib import Path

gen = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_26.c"
FUNCS = ["stopVoiceSlotSynced", "stopVoiceByHandle", "shutdownMusyXVoices"]
t = gen.read_text()
for fn in FUNCS:
    mark = f"PATCH: s4471 {fn}"
    if mark in t:
        print("already", fn); continue
    hdr = f"RECOMP_FUNC void {fn}(uint8_t* rdram, recomp_context* ctx) {{\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
    if t.count(hdr) != 1:
        raise SystemExit(f"{fn}: anchor count {t.count(hdr)}")
    blk = (
        f"    {{ /* {mark} */\n"
        "        static unsigned long n = 0; extern uint32_t rs64_phase_ord(void); extern int rogue_current_thread_id(uint8_t*);\n"
        "        uint32_t ph = rs64_phase_ord();\n"
        "        if (ph >= 3u && ++n <= 60ul) { unsigned a0 = (unsigned)ctx->r4; unsigned b0 = (a0 < 16u) ? (unsigned)MEM_BU(0, S32(0x80154620u + a0 * 0x1228u)) : 0xFFu;\n"
        f"            fprintf(stderr, \"[s4471-stop] fn={fn} phase=%u thr=%d a0=0x%08X b0=0x%02X n=%lu\\n\", ph, rogue_current_thread_id(rdram), a0, b0, n); fflush(stderr); }}\n"
        "    }\n"
    )
    t = t.replace(hdr, hdr + blk)
    print("patched", fn)
gen.write_text(t)

# --- B7CC writer witness (status <- 3 inside serviceVoicePoolFrame) ---
t = gen.read_text()
mark = "PATCH: s4471 B7CC"
if mark not in t:
    old = ("    // 0x8009B7C8: addu        $at, $at, $s0\n"
           "    ctx->r1 = ADD32(ctx->r1, ctx->r16);\n"
           "    // 0x8009B7CC: sb          $t0, 0x4620($at)\n")
    probe = (
        "    { /* " + mark + " */ static unsigned long n = 0; extern uint32_t rs64_phase_ord(void); extern int rogue_current_thread_id(uint8_t*);\n"
        "      if (++n <= 40ul) { fprintf(stderr, \"[s4471-b7cc] phase=%u thr=%d n=%lu slotoff=0x%X s4=0x%08X s4b=0x%02X fp=0x%02X old=0x%02X\\n\", rs64_phase_ord(), rogue_current_thread_id(rdram), n, (unsigned)ctx->r16, (unsigned)ctx->r20, (unsigned)MEM_BU(ctx->r20, 0), (unsigned)ctx->r30, (unsigned)MEM_BU(0X4620, ctx->r1)); fflush(stderr); } }\n"
    )
    new = old.replace("    // 0x8009B7CC", probe + "    // 0x8009B7CC", 1)
    if t.count(old) != 1:
        raise SystemExit("B7CC anchor count %d" % t.count(old))
    gen.write_text(t.replace(old, new)); print("patched B7CC")
