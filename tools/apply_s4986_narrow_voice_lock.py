#!/usr/bin/env python3
"""s4986: lock only the voice-array publication and paired observation."""
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
p23 = root / "funcs_23.c"
p24 = root / "funcs_24.c"
s23 = p23.read_text()
s24 = p24.read_text()
marker = "PATCH: s4986 narrow voice lock"
if marker in s23 or marker in s24:
    print("s4986 already applied")
    raise SystemExit(0)

def remove_broad(text, func):
    enter = "    rs64_s4985_voice_lock(); /* PATCH: s4985 voice lock enter */\n"
    exit = "    rs64_s4985_voice_unlock(); /* PATCH: s4985 voice lock exit */\n"
    if text.count(enter) != 1 or text.count(exit) != 1:
        raise SystemExit(f"broad lock markers missing in {func}")
    text = text.replace(enter, "", 1)
    text = text.replace(exit, "", 1)
    return text

s23 = remove_broad(s23, "allocateSongChannelArray")
s24 = remove_broad(s24, "musyxMixActiveVoices")

base = "    __atomic_store_n((uint32_t*)(rdram + 0x1496F8u), (uint32_t)ctx->r2, __ATOMIC_RELEASE); /* PATCH: s4984 atomic base store */\n"
count = "    __atomic_store_n((uint16_t*)(rdram + 0x149702u), (uint16_t)ctx->r16, __ATOMIC_RELEASE); /* PATCH: s4984 atomic count store */\n"
if s23.count(base) != 1 or s23.count(count) != 1:
    raise SystemExit("publication stores not unique")
s23 = s23.replace(base, "    rs64_s4985_voice_lock(); /* PATCH: s4986 narrow voice lock publication enter */\n" + base, 1)
s23 = s23.replace(count, count + "    rs64_s4985_voice_unlock(); /* PATCH: s4986 narrow voice lock publication exit */\n", 1)

count_load = "    { uint32_t s4575_a = U32(ADD32(ctx->r4, -0X6900)); ctx->r4 = rs64_s4984_load_voice_count(rdram); rs64_s4307_synth_read(rdram, 0x80090E1Cu, s4575_a, U32(ctx->r4)); } /* PATCH: s4984 atomic count load */\n"
base_load = "    { uint32_t s4575_a = U32(ADD32(ctx->r4, -0X6908)); ctx->r4 = rs64_s4984_load_voice_base(rdram); rs64_s4307_synth_read(rdram, 0x80090E78u, s4575_a, U32(ctx->r4)); } /* PATCH: s4984 atomic base load */\n"
if s24.count(count_load) != 1 or s24.count(base_load) != 1:
    raise SystemExit("paired observation loads not unique")
s24 = s24.replace(count_load, "    rs64_s4985_voice_lock(); /* PATCH: s4986 narrow voice lock observation enter */\n" + count_load, 1)
s24 = s24.replace(base_load, base_load + "    rs64_s4985_voice_unlock(); /* PATCH: s4986 narrow voice lock observation exit */\n", 1)

p23.write_text(s23)
p24.write_text(s24)
print("s4986 narrow voice lock applied")
