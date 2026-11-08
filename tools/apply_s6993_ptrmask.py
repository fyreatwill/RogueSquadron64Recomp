#!/usr/bin/env python3
"""s6993: the game's own "is this a pointer?" test `(p & 0xFF000000) == 0x80000000` rejects our dd>1 spill arena (0x81000000+).

ORIGIN (s6993, static read of the generated code, L15 21:9 dd4 crash s6991): loadLevelTextureCache builds each "ltex_cache_N"
header in an rs_malloc block and passes TLUT pointer hdr+0x1058 to loadTextureToMemory (via registerHmtTextureInTable ->
parseHmtMaterials). loadTextureToMemory (0x8001FC20) treats its TLUT arg as a pointer only if its top byte is 0x80; otherwise it
stores the arg as a TLUT slot id in record+0xE. With OSMEM_MB=12 at dd>1 the spill arena sits at 0x81000000 (s6587/s6858), so a
header spilled to 0x81xx0000 gives slot id 0x1058 = 4184 >= table 2000, and hudDisplayUpdateWorker (0x800496A8) later copies a
palette to table[4184], inside the material pool (s6991/s6992 MATWATCH chain). Retail never has heap pointers above 0x80800000.

Class audit (s6993): every `lui 0xFF00; and; lui 0x8000; compare` in RecompiledFuncs = 7 sites, all patched here:
relocateSndPointer 0x800925FC, allocTextureTlutBlock 0x8001E5DC, loadTextureToMemory 0x8001FC20 + 0x8001FD50,
loadAndDecodeTexture 0x80023164, getTextureAttrBySlot+tail (texture-attr helper) 0x8002340C, texPackTlutSlotOrAlloc 0x80023570.
The other 7 `lui 0xFF00` sites are 0xFF00FF00 fill masks; the 0xF0000000 tests (musyxInitVoiceFromSample, loadSpeechFile)
already accept 0x81. The mask load becomes rs64_s6993_mask(pc, value): 0xF0000000 (accepts 0x80000000-0x8FFFFFFF; the
non-pointer values at these sites are 16-bit slot ids / small offsets; 0xB0 ROM addresses still match relocateSndPointer's
second test) unless ROGUESQ_PTRMASK=0 (retail 0xFF000000). Logs [s6993] for the first 16 calls where the verdict changes.
Usage: apply_s6993_ptrmask.py [RecompiledFuncs dir]"""
import sys, pathlib, re
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6993 ptrmask"
SITES = {"800925FC": "r5", "8001E5DC": "r10", "8001FC20": "r21", "8001FD50": "r21", "80023164": "r23", "8002340C": "r11", "80023570": "r10"}
done = 0
for f in sorted(D.glob("funcs_*.c")):
    t = f.read_text(errors="surrogateescape")
    if TAG in t:
        done += t.count(TAG); continue
    k = 0
    for pc, reg in SITES.items():
        pat = "    // 0x%s: lui         $v0, 0xFF00\n    ctx->r2 = S32(0XFF00 << 16);\n" % pc
        c = t.count(pat)
        if not c: continue
        assert c == 1, (pc, c)
        t = t.replace(pat, "    // 0x%s: lui         $v0, 0xFF00\n    { extern uint32_t rs64_s6993_mask(uint32_t, uint32_t); ctx->r2 = (gpr)(int32_t)rs64_s6993_mask(0x%su, U32(ctx->%s)); } /* %s */\n" % (pc, pc, reg, TAG), 1)
        k += 1
    if k:
        f.write_text(t, errors="surrogateescape"); done += k
assert done == len(SITES), ("patched", done, "of", len(SITES))
print("s6993 ptrmask sites:", done)
