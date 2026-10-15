#!/usr/bin/env python3
"""s4994: sample ordinary s4540 caller rows at mission origins."""
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
p = root / "funcs_24.c"
s = p.read_text()
marker = "PATCH: s4994 mission-origin ordinary caller sample"
if marker in s:
    print("s4994 already applied")
    raise SystemExit(0)
anchor = "    a0 = (uint32_t)ctx->r4;\n"
if s.count(anchor) != 1:
    raise SystemExit(f"s4994 caller anchor count={s.count(anchor)}")
sample = (
    "    {\n"
    "        const uint32_t sample_origin = rs64_vi_committed_origin();\n"
    "        const uint32_t sample_width = rs64_vi_committed_width();\n"
    "        const int mission_origin = sample_width == 512u &&\n"
    "            (sample_origin == 0x00690400u || sample_origin == 0x00620400u);\n"
    "        static uint32_t sample_phase = 0xFFFFFFFFu;\n"
    "        static unsigned sample_rows = 0;\n"
    "        static int sample_control = 0;\n"
    "        if (!sample_control) {\n"
    "            sample_control = 1;\n"
    "            fprintf(stderr, \"[s4994-s4540] kind=arm width=%u origin=0x%08X\\n\",\n"
    "                sample_width, sample_origin);\n"
    "            fflush(stderr);\n"
    "        }\n"
    "        if (mission_origin) {\n"
    "            const uint32_t phase = rs64_phase_ord();\n"
    "            if (phase != sample_phase) { sample_phase = phase; sample_rows = 0; }\n"
    "            if (sample_rows < 32u) {\n"
    "                const uint32_t sample_guest_base = (uint32_t)MEM_W(-0x6908, S32(0x8015 << 16));\n"
    "                const uint32_t sample_guest_count = (uint32_t)MEM_HU(-0x6900, S32(0x8015 << 16));\n"
    "                const int sample_current = sample_guest_base == 0x8018C720u && sample_guest_count == 20u;\n"
    "                fprintf(stderr,\n"
    "                    \"[s4994-s4540] kind=row n=%u phase=%u width=%u origin=0x%08X pc=0x80090F00 r31=0x%08X r4=0x%08X a0=0x%08X base=0x%08X count=%u status=%s\\n\",\n"
    "                    sample_rows++, phase, sample_width, sample_origin, (uint32_t)ctx->r31,\n"
    "                    (uint32_t)ctx->r4, a0, sample_guest_base, sample_guest_count,\n"
    "                    sample_current ? \"current\" : \"stale\");\n"
    "                fflush(stderr);\n"
    "            }\n"
    "        }\n"
    "    } /* PATCH: s4994 mission-origin ordinary caller sample */\n"
)
s = s.replace(anchor, anchor + sample, 1)
p.write_text(s)
print("s4994 mission-origin sample applied")
