"""s6038 G1c: probe in streamTerrainGridCellsByDistance (funcs_9.c, 0x80042D88 'lb $v0,3($v1)'): s6037 dd2c died 5/5 here with a
guest-NULL read (v1+3 == 0). Logs (first 8) every time v1 falls outside RDRAM: table ptr *(0x80130004), cell u16 s2, idx, window,
terrain dims. Always-on but silent unless the bad-pointer condition holds (retail never hits it). Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "    // 0x80042D88: lb          $v0, 0x3($v1)\n"
NEW = r'''    { /* PATCH: s6038 cellprobe */ static int n6038 = 0; uint32_t v1b = (uint32_t)ctx->r3;
      if ((v1b < 0x80000000u || v1b >= 0x80800000u) && n6038 < 8) { n6038++;
        int64_t h = (int64_t)(int32_t)0x80132000, t = (int64_t)(int32_t)0x80136000;
        fprintf(stderr, "[cellprobe] v1=0x%08X t0=0x%08X tbl=0x%08X s2=0x%08X cell=0x%04X idx=%u win x0=%u w=%u z0=%u d=%u terr=%ux%u a0=%d\n", v1b, (uint32_t)ctx->r8,
          (uint32_t)MEM_W(4, (int64_t)(int32_t)0x80130000), (uint32_t)ctx->r18, (unsigned)MEM_HU(0, ctx->r18), (unsigned)(MEM_HU(0, ctx->r18) & 0x1FFF),
          (uint32_t)MEM_W(0xDB0, h), (uint32_t)MEM_W(0xDB4, h), (uint32_t)MEM_W(0xDB8, h), (uint32_t)MEM_W(0xDBC, h), (unsigned)MEM_HU(0xDF8, t), (unsigned)MEM_HU(0xDFA, t), (int)ctx->r4);
      } }
'''
def apply9(text):
    if "PATCH: s6038 cellprobe" in text or OLD not in text: return text, 0
    assert text.count(OLD) == 1
    return text.replace(OLD, NEW + OLD), 1
if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
