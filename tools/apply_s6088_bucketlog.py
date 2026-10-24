"""s6088 G1c ph2: ROGUESQ_BUCKETLOG=1 -> wrap findAndUnlinkSmallestEntry (0x8002221C) and dump the bucket
table (count lhu@0x8012EEF0, base ptr @0x8012F000; node: +0 next, +8 lhu cnt) on the first 3 zero returns,
on call #1 and every 4096th call (positive control: dump code must fire at dd1 too). Unset = silent.
Idempotent; funcs_6.c only. C++ side: rs64_s6088_fuse in src/main/upstream_compat.cpp."""
SIG = "RECOMP_FUNC void findAndUnlinkSmallestEntry(uint8_t* rdram, recomp_context* ctx) {\n"
NEW = ("RECOMP_FUNC void findAndUnlinkSmallestEntry_s6088_inner(uint8_t* rdram, recomp_context* ctx);\n"
       "extern void rs64_s6088_fuse(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);\n"
       "RECOMP_FUNC void findAndUnlinkSmallestEntry(uint8_t* rdram, recomp_context* ctx) { uint32_t _ra = U32(ctx->r31); findAndUnlinkSmallestEntry_s6088_inner(rdram, ctx); rs64_s6088_fuse(rdram, U32(ctx->r2), _ra, (uint32_t)MEM_HU(S32(0X8013 << 16), -0X7110), U32(MEM_W(S32(0X8013 << 16), -0X7100)), U32(MEM_W(S32(0X8011 << 16), 0X63B0))); } /* PATCH: s6088 bucketlog */\n"
       "RECOMP_FUNC void findAndUnlinkSmallestEntry_s6088_inner(uint8_t* rdram, recomp_context* ctx) {\n")
SIG2 = "RECOMP_FUNC void initTextureLUTAndAllocBuffers(uint8_t* rdram, recomp_context* ctx) {\n"
NEW2 = ("extern void rs64_s6090_init(uint32_t, uint32_t, uint32_t);\n"
        "RECOMP_FUNC void initTextureLUTAndAllocBuffers(uint8_t* rdram, recomp_context* ctx) {\n"
        "    rs64_s6090_init(U32(ctx->r4), U32(ctx->r5), U32(ctx->r31)); /* PATCH: s6090 lutinit */\n")
def apply6(text):
    n = 0
    if "PATCH: s6088 bucketlog" not in text and SIG in text: text = text.replace(SIG, NEW, 1); n += 1
    if "PATCH: s6090 lutinit" not in text and SIG2 in text: text = text.replace(SIG2, NEW2, 1); n += 1
    return text, n
if __name__ == "__main__":
    import pathlib
    p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_6.c"); t = p.read_text(); t2, n = apply6(t)
    if n: p.write_text(t2)
    print("funcs_6.c live patched x%d" % n)
