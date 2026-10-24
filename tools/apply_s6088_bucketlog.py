"""s6088 G1c ph2: ROGUESQ_BUCKETLOG=1 -> wrap findAndUnlinkSmallestEntry (0x8002221C) and dump the bucket
table (count lhu@0x8012EEF0, base ptr @0x8012F000; node: +0 next, +8 lhu cnt) on the first 3 zero returns,
on call #1 and every 4096th call (positive control: dump code must fire at dd1 too). Unset = silent.
Idempotent; funcs_6.c only. C++ side: rs64_s6088_fuse in src/main/upstream_compat.cpp."""
SIG = "RECOMP_FUNC void findAndUnlinkSmallestEntry(uint8_t* rdram, recomp_context* ctx) {\n"
NEW = ("RECOMP_FUNC void findAndUnlinkSmallestEntry_s6088_inner(uint8_t* rdram, recomp_context* ctx);\n"
       "extern void rs64_s6088_fuse(uint8_t*, uint32_t, uint32_t);\n"
       "RECOMP_FUNC void findAndUnlinkSmallestEntry(uint8_t* rdram, recomp_context* ctx) { uint32_t _ra = U32(ctx->r31); findAndUnlinkSmallestEntry_s6088_inner(rdram, ctx); rs64_s6088_fuse(rdram, U32(ctx->r2), _ra); } /* PATCH: s6088 bucketlog */\n"
       "RECOMP_FUNC void findAndUnlinkSmallestEntry_s6088_inner(uint8_t* rdram, recomp_context* ctx) {\n")
def apply6(text):
    if "PATCH: s6088 bucketlog" in text or SIG not in text: return text, 0
    return text.replace(SIG, NEW, 1), 1
if __name__ == "__main__":
    import pathlib
    p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_6.c"); t = p.read_text(); t2, n = apply6(t)
    if n: p.write_text(t2)
    print("funcs_6.c live patched x%d" % n)
