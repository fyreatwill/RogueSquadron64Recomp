"""s6417 G1c: ROGUESQ_DD_MESHLOG=1 logs, right after buildGridCellMeshForFace returns inside buildVisibleTerrainGridAroundCamera
(funcs_9.c, label after_11, 0x80043AAC): the 10 floats at 0x8009DE94..DEB8 (LOD dist^2 table DE98/9C/A0, far cutoff DEB4, window scalars DEAC/B0),
the render-chain start (*s4), chain length (link = word at p+0), and, over the doubly linked cell list from head s0 (next +0, prev +4),
node count and dist^2 (+8) bins: <DE98, <DE9C, <DEA0, <DEB4, >=DEB4 and max. Every 30th call. Default unset = silent. Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "    after_11:\n    // 0x80043AAC: lw          $v0, 0x14($s0)\n"
NEW = r'''    { /* PATCH: s6417 meshlog */ static int on6417 = -1; static int n6417 = 0;
      if (on6417 < 0) { const char* e = getenv("ROGUESQ_DD_MESHLOG"); on6417 = (e && *e && *e != '0') ? 1 : 0; }
      if (on6417 && (n6417++ % 30) == 0) {
        float tb[10]; int i; for (i = 0; i < 10; i++) { union { uint32_t u; float f; } c; c.u = (uint32_t)MEM_W((int64_t)(int32_t)(0x8009DE94u + 4 * i), 0); tb[i] = c.f; }
        uint32_t cs = (uint32_t)MEM_W(0, ctx->r20); int chain = 0; uint32_t p = cs;
        while (p && chain < 100000 && p >= 0x80000000u && p < 0x80800000u) { chain++; p = (uint32_t)MEM_W(0, (int64_t)(int32_t)p); }
        int total = 0, b0 = 0, b1 = 0, b2 = 0, b3 = 0, bfar = 0; float dmax = -1.0f; int pass;
        for (pass = 0; pass < 2; pass++) { uint32_t node = (uint32_t)ctx->r16; if (pass) node = node ? (uint32_t)MEM_W(0x4, (int64_t)(int32_t)node) : 0;
          while (node && total < 100000) { union { uint32_t u; float f; } d; d.u = (uint32_t)MEM_W(0x8, (int64_t)(int32_t)node);
            if (d.f > dmax) dmax = d.f; if (d.f < tb[1]) b0++; else if (d.f < tb[2]) b1++; else if (d.f < tb[3]) b2++; else if (d.f < tb[8]) b3++; else bfar++;
            total++; node = (uint32_t)MEM_W(pass ? 0x4 : 0x0, (int64_t)(int32_t)node); } }
        fprintf(stderr, "[meshlog] tbl[94..B8]=%.1f %.1f %.1f %.1f %.1f %.1f %.1f %.1f %.1f %.1f chain_start=0x%08X chain=%d list=%d bins[<98:%d <9C:%d <A0:%d <B4:%d >=B4:%d] d2max=%.1f\n",
          tb[0], tb[1], tb[2], tb[3], tb[4], tb[5], tb[6], tb[7], tb[8], tb[9], cs, chain, total, b0, b1, b2, b3, bfar, dmax);
      } }
'''
def apply9(text):
    if "PATCH: s6417 meshlog" in text or OLD not in text: return text, 0
    assert text.count(OLD) == 1
    return text.replace(OLD, OLD.replace("    after_11:\n", "    after_11:\n" + NEW)), 1
if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
