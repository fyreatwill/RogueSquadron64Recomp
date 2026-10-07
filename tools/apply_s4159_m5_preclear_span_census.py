#!/usr/bin/env python3
"""Add a phase-scoped full-intersection census to the scalar-store hook."""

from pathlib import Path

TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_2.c")
MARKER = "PATCH: s4159 M5 preclear span census"


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    if MARKER in text:
        old = "census_rows[census_phase] < 512u"
        new = "census_rows[census_phase] < 4096u"
        if old in text:
            TARGET.write_text(text.replace(old, new, 1), encoding="utf-8")
            print("s4159 span census budget refreshed")
        else:
            print("s4159 span census already present")
        return
    anchor = "    (void)value;\n    for (off = 0u; off < span; off += 4u) {\n"
    if text.count(anchor) != 1:
        raise SystemExit("s4159: scalar-store anchor is not unique")
    insert = (
        "    /* " + MARKER + " */\n"
        "    if (getenv(\"ROGUESQ_LOG_M5_PRECLEAR_SPAN\") || getenv(\"ROGUESQ_LOG_ALL\")) {\n"
        "        static unsigned census_control = 0;\n"
        "        static unsigned census_rows[2] = {};\n"
        "        unsigned census_width = rs64_vi_committed_width();\n"
        "        unsigned census_origin = rs64_vi_committed_origin() & 0x00FFFFFFu;\n"
        "        unsigned census_phase = (census_width == 1024u && census_origin == 0x00790400u) ? 0u :\n"
        "                                ((census_width == 512u && census_origin == 0x006AB400u) ? 1u : 2u);\n"
        "        if (census_phase < 2u) {\n"
        "            if (!census_control) {\n"
        "                fprintf(stderr, \"[m5-span-census-control] phase=%u width=%u origin=0x%06X pc=0x%08X\\n\",\n"
        "                        rs64_phase_ord(), census_width, census_origin, pc);\n"
        "                fflush(stderr);\n"
        "                census_control = 1;\n"
        "            }\n"
        "            uint32_t census_phys = ((addr ^ adjust) - 0x80000000u) & 0x1FFFFFFFu;\n"
        "            uint32_t census_end = census_phys + span;\n"
        "            if (census_phys < 0x179A48u && census_end > 0x1797B0u &&\n"
        "                census_rows[census_phase] < 4096u) {\n"
        "                fprintf(stderr,\n"
        "                        \"[m5-span-census] row=%u phase=%u width=%u origin=0x%06X \"\n"
        "                        \"pc=0x%08X store_width=%c phys=0x%06X end=0x%06X value=0x%08X\\n\",\n"
        "                        census_rows[census_phase]++, rs64_phase_ord(), census_width,\n"
        "                        census_origin, pc, width, census_phys, census_end, value);\n"
        "                fflush(stderr);\n"
        "            }\n"
        "        }\n"
        "    }\n"
    )
    text = text.replace(anchor, insert + anchor, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("s4159 span census patched funcs_2.c")


if __name__ == "__main__":
    raise SystemExit(main())
