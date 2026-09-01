#!/usr/bin/env python3
"""Install the regeneration-safe M5 mixer-entry witness."""
from pathlib import Path


TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
MARKER = "PATCH: s3514 M5 mixer entry"

text = TARGET.read_text(encoding="utf-8")
if MARKER in text:
    print("apply_s3514: already present")
    raise SystemExit(0)

decl = "extern void rs64_m5_mix_entry(uint8_t* rdram, recomp_context* ctx, uint32_t pc);\n"
text = text.replace(decl, "")
anchor = "extern void rs64_m5_audio_sequencer_event(uint32_t source, uint32_t edge_kind, uint32_t target, uint32_t guest_ra);\n"
if text.count(anchor) != 1:
    raise SystemExit("apply_s3514: file-level declaration anchor is not unique")
text = text.replace(anchor, anchor + decl, 1)

anchor = "RECOMP_FUNC void musyxMixActiveVoices(uint8_t* rdram, recomp_context* ctx) {\n"
insert = "    rs64_m5_mix_entry(rdram, ctx, 0x80090E04u); /* PATCH: s3514 M5 mixer entry */\n"
if text.count(anchor) != 1:
    raise SystemExit("apply_s3514: mixer entry anchor is not unique")
text = text.replace(anchor, anchor + insert, 1)
TARGET.write_text(text, encoding="utf-8")
print("apply_s3514: inserted mixer-entry witness")
