"""s5773: correlate the executed bit1 post at 0x800B1140 with the lives byte.

Guest logs (ROGUESQ_LOG_MTM=1), sharing rs64_s5773_ord/ms with the host poll:
  [bit1]       the delay-slot store that ORs mask bit 1 (only path that posts it)
  [lives]      the sb at 0x800FB28C that decrements lives[0x80130B10+slot]
  [livesatmtm] lives bytes at requestMissionTransitionMode entry (control)

Idempotent. The host any-writer watch is in src/main/main.cpp ([livesctl]/[livesbyte]).
"""
import pathlib
import sys

TAG = "PATCH: s5773 bit1 lives"

BIT1_ANCHOR = (
    "    MEM_W(-0X3620, ctx->r5) = ctx->r2;\n"
    "    { static int s_e = -1, s_n = 0; if (s_e < 0) { const char* e = getenv(\"ROGUESQ_LOG_MTM\"); s_e = (e && e[0]) ? 1 : 0; } if (s_e && s_n < 300) { s_n++; fprintf(stderr, \"[mtmst] pc=0x800B1140 val=0x%08X ra=0x%X\\n\", (unsigned)MEM_W(-0X3620, ctx->r5), U32(ctx->r31)); } } /* PATCH: s5754 mask store log */\n"
    "        goto L_800B13C4;\n"
)

BIT1_LOG = (
    "    { static int s5773_e = -1, s5773_n = 0; if (s5773_e < 0) { const char* e = getenv(\"ROGUESQ_LOG_MTM\"); s5773_e = (e && e[0]) ? 1 : 0; } "
    "if (s5773_e && s5773_n < 80) { s5773_n++; extern long long rs64_s5773_ms(void); extern unsigned long rs64_s5773_ord(void); "
    "unsigned slot = (unsigned)(ctx->r4 & 0xFFu); unsigned lives = (unsigned)MEM_BU(S32(0X8013 << 16), 0xB10 + (int)slot); "
    "unsigned b0 = (unsigned)MEM_BU(S32(0X8013 << 16), 0xB10); unsigned phase = (unsigned)MEM_W(S32(0X8011 << 16), -0X35E0); "
    "fprintf(stderr, \"[bit1] ord=%lu t=%lld pc=0x800B1140 slot=%u lives=%u b0=%u phase=%u mask=0x%08X s1=0x%08X\\n\", "
    "rs64_s5773_ord(), rs64_s5773_ms(), slot, lives, b0, phase, (unsigned)U32(ctx->r2), (unsigned)U32(ctx->r17)); fflush(stderr); } } "
    "/* " + TAG + " */\n"
)

LIVES_ANCHOR = (
    "    // 0x800FB288: addiu       $v0, $v0, -0x1\n"
    "    ctx->r2 = ADD32(ctx->r2, -0X1);\n"
    "    // 0x800FB28C: sb          $v0, 0x0($v1)\n"
)

LIVES_LOG = (
    "    ctx->r2 = ADD32(ctx->r2, -0X1);\n"
    "    { static int s5773_e = -1, s5773_n = 0; if (s5773_e < 0) { const char* e = getenv(\"ROGUESQ_LOG_MTM\"); s5773_e = (e && e[0]) ? 1 : 0; } "
    "if (s5773_e && s5773_n < 80) { s5773_n++; extern long long rs64_s5773_ms(void); extern unsigned long rs64_s5773_ord(void); "
    "unsigned before = (unsigned)MEM_BU(ctx->r3, 0); unsigned after = (unsigned)(U32(ctx->r2) & 0xFFu); "
    "fprintf(stderr, \"[lives] ord=%lu t=%lld pc=0x800FB28C addr=0x%08X before=%u after=%u\\n\", "
    "rs64_s5773_ord(), rs64_s5773_ms(), (unsigned)U32(ctx->r3), before, after); fflush(stderr); } } "
    "/* " + TAG + " */\n"
    "    // 0x800FB28C: sb          $v0, 0x0($v1)\n"
)

MTM_ANCHOR = "/* PATCH: s5748 mtm log */\n"

MTM_LOG = (
    "/* PATCH: s5748 mtm log */\n"
    "    { static int s5773m_e = -1, s5773m_n = 0; if (s5773m_e < 0) { const char* e = getenv(\"ROGUESQ_LOG_MTM\"); s5773m_e = (e && e[0]) ? 1 : 0; } "
    "if (s5773m_e && s5773m_n < 40) { s5773m_n++; extern long long rs64_s5773_ms(void); extern unsigned long rs64_s5773_ord(void); "
    "unsigned b0 = (unsigned)MEM_BU(S32(0X8013 << 16), 0xB10); unsigned b1 = (unsigned)MEM_BU(S32(0X8013 << 16), 0xB11); "
    "unsigned b2 = (unsigned)MEM_BU(S32(0X8013 << 16), 0xB12); unsigned phase = (unsigned)MEM_W(S32(0X8011 << 16), -0X35E0); "
    "fprintf(stderr, \"[livesatmtm] ord=%lu t=%lld a0=%u b0=%u b1=%u b2=%u phase=%u\\n\", "
    "rs64_s5773_ord(), rs64_s5773_ms(), (unsigned)U32(ctx->r4), b0, b1, b2, phase); fflush(stderr); } } "
    "/* " + TAG + " */\n"
)


def apply_30(text):
    if TAG in text:
        return text, 0
    if text.count(BIT1_ANCHOR) != 1:
        raise RuntimeError(f"s5773 bit1 anchor count={text.count(BIT1_ANCHOR)}")
    return text.replace(BIT1_ANCHOR, BIT1_LOG + BIT1_ANCHOR, 1), 1


def apply_42(text):
    if TAG in text:
        return text, 0
    if text.count(LIVES_ANCHOR) != 1:
        raise RuntimeError(f"s5773 lives anchor count={text.count(LIVES_ANCHOR)}")
    if text.count(MTM_ANCHOR) != 1:
        raise RuntimeError(f"s5773 mtm anchor count={text.count(MTM_ANCHOR)}")
    text = text.replace(LIVES_ANCHOR, LIVES_ANCHOR.replace(
        "    ctx->r2 = ADD32(ctx->r2, -0X1);\n    // 0x800FB28C: sb          $v0, 0x0($v1)\n",
        LIVES_LOG, 1), 1)
    text = text.replace(MTM_ANCHOR, MTM_LOG, 1)
    return text, 2


def apply(text, name):
    if name == "funcs_30.c":
        return apply_30(text)
    if name == "funcs_42.c":
        return apply_42(text)
    return text, 0


if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    total = 0
    for name, fn in (("funcs_30.c", apply_30), ("funcs_42.c", apply_42)):
        p = base / name
        updated, n = fn(p.read_text())
        if n:
            p.write_text(updated)
        total += n
        print(f"{p.name}: s5773 x{n}")
    if total == 0:
        print("s5773 already applied")
