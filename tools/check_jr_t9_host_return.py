#!/usr/bin/env python3
"""Fail if convertMat3x4ToN64Mtx still LOOKUP_FUNC's its jr-$t9 tail.

s2190 inserts writer_parity before SD(); the fixup regex must still replace
LOOKUP_FUNC(ctx->r25) with a host return. 0x800155EC is a JAL continuation,
not a function (s2586/s2587 abort, restored s2605).
"""
import re, sys
from pathlib import Path

p = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_4.c"
text = p.read_text()
m = re.search(
    r"RECOMP_FUNC void convertMat3x4ToN64Mtx\(uint8_t\* rdram, recomp_context\* ctx\) \{",
    text)
if not m:
    sys.exit("convertMat3x4ToN64Mtx missing")
func_re = re.compile(r"RECOMP_FUNC void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{")
end = func_re.search(text, m.end())
body = text[m.end(): end.start() if end else len(text)]
if "LOOKUP_FUNC(ctx->r25)" in body:
    sys.exit("convertMat3x4ToN64Mtx still LOOKUP_FUNC(ctx->r25) after jr $t9")
if "host return resumes the sole generated after_4 continuation" not in body:
    sys.exit("convertMat3x4ToN64Mtx missing jr-$t9 host-return patch")
print("ok: convertMat3x4ToN64Mtx jr-$t9 host return present")
