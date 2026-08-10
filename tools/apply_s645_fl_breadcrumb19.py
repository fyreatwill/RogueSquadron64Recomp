#!/usr/bin/env python3
"""Apply s645 BREADCRUMB19 freelist header-store guest-PC stamps + memset dest probe."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

BASE = Path(
    os.environ.get(
        "RECOMP_FUNCS_DIR",
        str(Path.home() / "Documents/Tools/N64Recomp/RecompiledFuncs"),
    )
)

FUNC_RE = re.compile(r"RECOMP_FUNC void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{")
INSTR_RE = re.compile(r"^([ \t]*)(// (0x[0-9A-Fa-f]+): .*)$", re.M)

TARGETS = [
    ("funcs_0.c", "rs_malloc", "BREADCRUMB19a"),
    ("funcs_0.c", "rs_free", "BREADCRUMB19b"),
    ("funcs_2.c", "rs_memset", "BREADCRUMB19c"),
    ("funcs_3.c", "heapWalker", "BREADCRUMB19d"),
    ("funcs_0.c", "buildHeapFreeList", "BREADCRUMB19e"),
]

MEMSET_PROBE = """\
    { // PATCH: memset-fl-dest (s645, item -398) -- see fixup_game_funcs.py BREADCRUMB19c comment
        static int s_msfl_en = -1;
        if (s_msfl_en < 0) {
            const char* e = getenv("ROGUESQ_LOG_FL_ZERO_WATCH");
            s_msfl_en = (e && e[0] && e[0] != '0') ? 1 : 0;
        }
        if (s_msfl_en) {
            uint32_t ms_dst = U32(ctx->r4);
            uint32_t ms_val = U32(ctx->r5) & 0xFFu;
            uint32_t ms_len = U32(ctx->r6);
            uint32_t ms_tgt = 0x801F3CC0u;
            int ms_hit = 0;
            if (ms_len > 0u && ms_len <= 0x800000u) {
                uint32_t ms_end = ms_dst + ms_len; /* may wrap; checked below */
                if (ms_end > ms_dst) {
                    if (ms_dst <= ms_tgt && ms_end > ms_tgt) ms_hit = 1;
                }
                if (ms_dst >= 0x801F3CC0u && ms_dst < 0x801F3CD0u) ms_hit = 1;
                /* also flag any clear whose range covers the whole E8 freelist head area */
                if (ms_dst <= 0x801F0000u && ms_end > 0x80200000u) ms_hit = 2;
            }
            static int s_msfl_n = 0;
            static int s_msfl_all = 0;
            /* same-run posctrl: first 8 calls always, then hits only */
            int ms_log = ms_hit || (s_msfl_all < 8) || ((s_msfl_all % 500) == 0);
            if (ms_log) {
                fprintf(stderr,
                    "[memset-fl-dest] n=%d all=%d hit=%d dst=0x%08X val=0x%02X len=0x%X ra=0x%08X\n",
                    s_msfl_n, s_msfl_all, ms_hit, ms_dst, ms_val, ms_len, U32(ctx->r31));
                fflush(stderr);
            }
            if (ms_hit) s_msfl_n++;
            s_msfl_all++;
        }
    }
"""


def breadcrumb_body(body: str) -> tuple[str, int]:
    def _patch(m: re.Match[str]) -> str:
        indent, comment, addr = m.group(1), m.group(2), m.group(3)
        return f"{indent}{comment}\n{indent}g_rs64_last_guest_pc = {addr}u;"

    return re.subn(INSTR_RE, _patch, body)


def apply_one(path: Path, func_name: str, tag: str) -> str:
    text = path.read_text()
    m = re.search(
        r"RECOMP_FUNC void " + func_name + r"\(uint8_t\* rdram, recomp_context\* ctx\) \{\n",
        text,
    )
    if not m:
        return f"ERROR {tag}: {func_name} open not found in {path.name}"
    body_start = m.end()
    next_m = FUNC_RE.search(text, body_start)
    body_end = next_m.start() if next_m else len(text)
    body = text[body_start:body_end]
    existing = body.count("g_rs64_last_guest_pc")
    if existing >= 5:
        return f"{tag} {func_name}: already breadcrumbed ({existing} stamps)"
    new_body, n = breadcrumb_body(body)
    if n == 0:
        return f"ERROR {tag}: {func_name} no instruction comments to stamp"
    path.write_text(text[:body_start] + new_body + text[body_end:])
    return f"{tag} {func_name}: patched x{n}"


def apply_memset_probe() -> str:
    path = BASE / "funcs_2.c"
    text = path.read_text()
    if "memset-fl-dest (s645" in text:
        return "memset-fl-dest: already present"
    marker = "RECOMP_FUNC void rs_memset(uint8_t* rdram, recomp_context* ctx) {\n"
    if marker not in text:
        return "ERROR memset-fl-dest: rs_memset not found"
    text = text.replace(marker, marker + MEMSET_PROBE, 1)
    if "#include <stdio.h>" not in text:
        text = text.replace('#include "recomp.h"\n', '#include "recomp.h"\n#include <stdio.h>\n', 1)
    path.write_text(text)
    return "memset-fl-dest: patched"


def main() -> int:
    report = []
    for fname, fn, tag in TARGETS:
        path = BASE / fname
        if not path.is_file():
            report.append(f"ERROR missing {path}")
            continue
        report.append(apply_one(path, fn, tag))
    report.append(apply_memset_probe())
    for line in report:
        print(line)
    if any(r.startswith("ERROR") for r in report):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
