#!/usr/bin/env python3
"""Add the s2877 target-phase consumer probe to generated funcs_36.c."""
from pathlib import Path

GEN = Path(__file__).resolve().parents[1] / "../N64Recomp/RecompiledFuncs/funcs_36.c"
MARK = "/* PATCH: s2877 M5 route consumer entry */"
text = GEN.read_text()
if MARK in text:
    raise SystemExit("s2877 probe already present; regenerate before reapplying")

helper = r'''/* PATCH: s2877 M5 route consumer helper */
static void rs64_s2877_route_consumer(uint8_t *rdram, uint32_t pc,
                                      uint32_t arg0, uint32_t arg1,
                                      uint32_t guest_ra) {
    static int enabled = -1;
    static unsigned long rows = 0;
    if (enabled < 0) {
        const char *e = getenv("ROGUESQ_LOG_M5_ROUTE_CONSUMER");
        enabled = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    if (!enabled || rows >= 256ul) return;
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    uint32_t width = rs64_vi_committed_width();
    uint32_t origin = rs64_vi_committed_origin();
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    uint32_t base = 0x80130B40u & 0x1FFFFFFFu;
    fprintf(stderr,
            "[m5-route-consumer] pc=0x%08X width=%u origin=0x%06X row=%lu "
            "arg0=0x%08X arg1=0x%08X ra=0x%08X state=",
            pc, width, origin, rows, arg0, arg1, guest_ra);
    for (unsigned i = 0; i < 0x30u; ++i)
        fprintf(stderr, "%02X", rdram[base + i]);
    fputc('\n', stderr);
    fflush(stderr);
    ++rows;
}
'''
anchor = '#include "funcs.h"\n'
if text.count(anchor) != 1:
    raise SystemExit(f"include anchor count={text.count(anchor)}")
text = text.replace(anchor, anchor + helper + "\n", 1)

header = "RECOMP_FUNC void playObjectiveVoiceLine2(uint8_t* rdram, recomp_context* ctx) {\n"
if text.count(header) != 1:
    raise SystemExit(f"consumer header count={text.count(header)}")
entry = (
    "    rs64_s2877_route_consumer(rdram, 0x800C7D1Cu, U32(ctx->r4), "
    "U32(ctx->r5), U32(ctx->r31)); " + MARK + "\n"
)
text = text.replace(header, header + entry, 1)
if '#include <stdio.h>' not in text:
    text = text.replace('#include "recomp.h"\n', '#include "recomp.h"\n#include <stdio.h>\n', 1)
if '#include <stdlib.h>' not in text:
    text = text.replace('#include "recomp.h"\n', '#include "recomp.h"\n#include <stdlib.h>\n', 1)
GEN.write_text(text)
print(f"patched {GEN}")
