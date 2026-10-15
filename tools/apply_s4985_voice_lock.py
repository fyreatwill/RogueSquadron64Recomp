#!/usr/bin/env python3
"""s4985: serialize voice-array publication and observation with a host lock.

ORIGIN: allocateSongChannelArray publishes the legitimate voice-array base and
count while musyxMixActiveVoices scans them on another host thread. This is an
exclusion experiment, not a value guard or stale-pointer filter.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
p23 = root / "funcs_23.c"
p24 = root / "funcs_24.c"
s23 = p23.read_text()
s24 = p24.read_text()
marker = "PATCH: s4985 voice lock"
if marker in s23 or marker in s24:
    print("s4985 already applied")
    raise SystemExit(0)

decl = "extern void rs64_s4985_voice_lock(void);\nextern void rs64_s4985_voice_unlock(void);\n/* PATCH: s4985 voice lock */\n"
anchor23 = "RECOMP_FUNC void allocateSongChannelArray(uint8_t* rdram, recomp_context* ctx) {\n"
anchor24 = "RECOMP_FUNC void musyxMixActiveVoices(uint8_t* rdram, recomp_context* ctx) {\n"
if s23.count(anchor23) != 1 or s24.count(anchor24) != 1:
    raise SystemExit(f"anchors: alloc={s23.count(anchor23)} mix={s24.count(anchor24)}")
s23 = s23.replace(anchor23, decl + anchor23 + "    rs64_s4985_voice_lock(); /* PATCH: s4985 voice lock enter */\n", 1)
s24 = s24.replace(anchor24, decl + anchor24 + "    rs64_s4985_voice_lock(); /* PATCH: s4985 voice lock enter */\n", 1)

end23 = "    // 0x8008F2F8: nop\n\n;}"
end24 = "    // 0x80091030: nop\n\n;}"
if s23.count(end23) != 1 or s24.count(end24) != 1:
    raise SystemExit(f"ends: alloc={s23.count(end23)} mix={s24.count(end24)}")
s23 = s23.replace(end23, "    // 0x8008F2F8: nop\n\n    rs64_s4985_voice_unlock(); /* PATCH: s4985 voice lock exit */\n;}" , 1)
s24 = s24.replace(end24, "    // 0x80091030: nop\n\n    rs64_s4985_voice_unlock(); /* PATCH: s4985 voice lock exit */\n;}" , 1)
p23.write_text(s23)
p24.write_text(s24)
print("s4985 voice lock applied")
