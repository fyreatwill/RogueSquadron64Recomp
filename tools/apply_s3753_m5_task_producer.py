#!/usr/bin/env python3
"""Add the s3753 phase-gated task-data producer census to generated funcs.

The census is deliberately attached to the existing all-scalar-store helper,
so it covers computed-address producers without hand-editing individual MIPS
functions.  Re-running this script is idempotent.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "../N64Recomp/RecompiledFuncs"
MARKER = "PATCH: s3753 M5 task-data producer census"

SNIPPET = f'''    /* {MARKER} */
    {{
        static int s3753_enabled = -1;
        static unsigned s3753_rows = 0;
        static int s3753_control = 0;
        if (s3753_enabled < 0) {{
            const char* e = getenv("ROGUESQ_LOG_M5_TASK_PRODUCER");
            const char* all = getenv("ROGUESQ_LOG_ALL");
            s3753_enabled = ((e && e[0] && e[0] != '0') ||
                             (all && all[0] && all[0] != '0')) ? 1 : 0;
        }}
        if (s3753_enabled) {{
            extern uint32_t rs64_vi_committed_width(void);
            extern uint32_t rs64_vi_committed_origin(void);
            extern uint32_t rs64_phase_ord(void);
            if (!s3753_control) {{
                fprintf(stderr, "[m5-task-producer-control] any_scalar_store=1 pc=0x%08X\\n", pc);
                fflush(stderr);
                s3753_control = 1;
            }}
            unsigned s3753_width = rs64_vi_committed_width();
            unsigned s3753_origin = rs64_vi_committed_origin();
            unsigned s3753_span = width == 'B' ? 1u : (width == 'H' ? 2u : 4u);
            unsigned s3753_adjust = width == 'B' ? 3u : (width == 'H' ? 2u : 0u);
            unsigned s3753_phys = ((addr ^ s3753_adjust) - 0x80000000u) & 0x007FFFFFu;
            if ((s3753_width == 1024u && s3753_origin == 0x00790400u) ||
                (s3753_width == 512u && s3753_origin == 0x006AB400u)) {{
                if (s3753_phys < 0x171F70u && s3753_phys + s3753_span > 0x171E70u &&
                    s3753_rows < 4096u) {{
                    fprintf(stderr,
                            "[m5-task-producer] row=%u phase=%u width=%u origin=0x%06X "
                            "pc=0x%08X phys=0x%06X len=%u value=0x%08X\\n",
                            s3753_rows++, rs64_phase_ord(), s3753_width,
                            s3753_origin, pc, s3753_phys, s3753_span, value);
                    fflush(stderr);
                }}
            }}
        }}
    }}
'''


def main() -> int:
    changed = 0
    files = sorted(ROOT.glob("funcs_*.c"))
    if not files:
        raise SystemExit(f"no generated files under {ROOT}")
    for path in files:
        text = path.read_text()
        if MARKER in text:
            continue
        anchor = "        rs64_m5_route_value_writer(width, pc, addr, value);\n"
        if text.count(anchor) != 1:
            raise RuntimeError(f"{path}: route writer anchor count={text.count(anchor)}")
        text = text.replace(anchor, anchor + SNIPPET, 1)
        path.write_text(text)
        changed += 1
    print(f"s3753: patched {changed} generated files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
