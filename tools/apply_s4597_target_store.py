#!/usr/bin/env python3
"""Reapply the s4597 diagnostic calls lost by generated-function regeneration."""
from pathlib import Path

p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_2.c")
s = p.read_text()
if "rs64_s4597_target_store" not in s:
    s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\nextern void rs64_s4597_target_store(char, uint32_t, uint32_t, uint32_t);\n', 1)
    anchor = "RECOMP_FUNC void rs_strncpy(uint8_t* rdram, recomp_context* ctx) {\n"
    if s.count(anchor) != 1:
        raise SystemExit("rs_strncpy anchor count is not one")
    s = s.replace(anchor, anchor + "    rs64_s4597_target_store('E', 0x80007640u, 0xFFFFFFFFu, 0u); /* PATCH: s4597 entry control */\n", 1)
    call = "rs64_s4597_target_store('B', 0x80007670u, U32(ADD32(ctx->r7, 0X0)), U32(ctx->r3)); /* PATCH: s4597 */\n"
    anchors = [
        "        // 0x80007670: sb          $v1, 0x0($a3)\n",
        "    // 0x80007670: sb          $v1, 0x0($a3)\n",
    ]
    if any(s.count(anchor) != 1 for anchor in anchors):
        raise SystemExit("store anchors are not the expected two sites")
    for anchor in anchors:
        indent = anchor[:len(anchor) - len(anchor.lstrip())]
        s = s.replace(anchor, anchor + indent + call, 1)
    p.write_text(s)
    print("applied")
else:
    print("already applied")
