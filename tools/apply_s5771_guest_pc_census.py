"""s5771: log the two guest PCs that set craft slot kill-state bits.

The anchors are the generated instructions at 0x800B0348 and 0x800B08DC,
not host symbols.  The log is gated by ROGUESQ_LOG_MTM so it shares the
existing mission-transition positive control.
"""
import pathlib

TAG = "PATCH: s5771 guest-pc census"


def apply(text):
    if TAG in text:
        return text, 0

    a = "    // 0x800B0348: sh          $v1, 0x180($s2)\n"
    b = "    // 0x800B08DC: sh          $v1, 0x180($s0)\n"
    if text.count(a) != 1 or text.count(b) < 1:
        raise RuntimeError(f"s5771 anchors count={text.count(a)}/{text.count(b)}")
    common = (
        "    { static unsigned long s_s5771_n = 0; static int s_s5771_e = -1; "
        "if (s_s5771_e < 0) { const char* e = getenv(\"ROGUESQ_LOG_MTM\"); "
        "s_s5771_e = (e && e[0]) ? 1 : 0; } if (s_s5771_e && s_s5771_n < 200) { "
    )
    ca = common + (
        "s_s5771_n++; fprintf(stderr, \"[killset] ord=%lu pc=0x800B0348 a0=0x%08X "
        "slot=0x%08X before=0x%04X after=0x%04X\\n\", s_s5771_n, U32(ctx->r4), "
        "U32(ctx->r18), (unsigned)MEM_HU(ctx->r18, 0X180), (unsigned)U32(ctx->r3)); } } "
        "/* " + TAG + " */\n"
    )
    cb = common + (
        "s_s5771_n++; fprintf(stderr, \"[killset] ord=%lu pc=0x800B08DC a0=0x%08X "
        "slot=0x%08X before=0x%04X after=0x%04X\\n\", s_s5771_n, U32(ctx->r4), "
        "U32(ctx->r16), (unsigned)MEM_HU(ctx->r16, 0X180), (unsigned)U32(ctx->r3)); } } "
        "/* " + TAG + " */\n"
    )
    text = text.replace(a, ca + a, 1).replace(b, cb + b, 1)
    return text, 2


if __name__ == "__main__":
    base = pathlib.Path(__import__("sys").argv[1])
    p = base / "funcs_29.c"
    updated, count = apply(p.read_text())
    p.write_text(updated)
    print(f"{p}: s5771 guest-pc census x{count}")
