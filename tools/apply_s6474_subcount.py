"""s6474 G1c: ROGUESQ_DD_SUBLOG=1 per-30-build entry counters for the terrain per-cell chain under buildGridCellMeshForFace (0x8004317C):
buildGridCellMesh(0x8004B930) and its sub-builders emitGridCellTileStrip/Adjacent/Diagonal, mapCellGeometryToGridSpace, buildGridCellLabel,
selectGridCellTileVariant. Discriminates dd2 vs dd3: does buildGridCellMesh get fewer entries (H-guestcull) or enter but call fewer emitters
(H-vtxdl / H-lod)? Default unset = no output (counters still tick, ~free). Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
FUNCS = ["buildGridCellMesh", "emitGridCellTileStrip", "emitGridCellTileStripAdjacent", "emitGridCellTileStripDiagonal",
         "mapCellGeometryToGridSpace", "buildGridCellLabel", "selectGridCellTileVariant"]
HDR = "    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
def apply10(text):
    if "PATCH: s6474 subcount" in text: return text, 0
    n = 0
    for i, f in enumerate(FUNCS):
        sig = "RECOMP_FUNC void %s(uint8_t* rdram, recomp_context* ctx) {\n" % f
        if text.count(sig) != 1: continue
        k = text.index(sig) + len(sig)
        if not text.startswith(HDR, k): continue
        text = text[:k + len(HDR)] + "    g_s6474[%d]++; /* PATCH: s6474 subcount */\n" % i + text[k + len(HDR):]
        n += 1
    first = text.index("RECOMP_FUNC void ")
    text = text[:first] + "uint32_t g_s6474[8]; /* PATCH: s6474 subcount */\n" + text[first:]
    return text, n
OLD = "    // 0x80043AAC: lw          $v0, 0x14($s0)\n"
NEW = r'''    { /* PATCH: s6474 subcount */ extern uint32_t g_s6474[8]; static int on6474 = -1; static int n6474 = 0;
      if (on6474 < 0) { const char* e = getenv("ROGUESQ_DD_SUBLOG"); on6474 = (e && *e && *e != '0') ? 1 : 0; }
      if (on6474 && ++n6474 >= 30) { n6474 = 0;
        fprintf(stderr, "[sublog] /30builds mesh=%u stripN=%u stripAdj=%u stripDiag=%u mapGeom=%u label=%u variant=%u\n", g_s6474[0], g_s6474[1], g_s6474[2], g_s6474[3], g_s6474[4], g_s6474[5], g_s6474[6]);
        for (int i = 0; i < 8; i++) g_s6474[i] = 0; } }
'''
def apply9(text):
    if "PATCH: s6474 subcount" in text or "PATCH: s6417 meshlog" not in text: return text, 0
    anchor = "      } }\n" + OLD
    assert text.count(anchor) == 1
    return text.replace(anchor, "      } }\n" + NEW + OLD), 1
if __name__ == "__main__":
    for name, fn in (("funcs_9.c", apply9), ("funcs_10.c", apply10)):
        p = base / name; t = p.read_text(); t2, n = fn(t)
        if n: p.write_text(t2)
        print(name, "x%d" % n)
