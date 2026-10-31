"""s6695 G1d: stamp the swap number when renderRadarMinimap (0x800C5F90, funcs_34.c, flight-only) runs.
rs64_region_scan (src/rsp/dpc_bridge.cpp) shifts the radar disc only while the radar was drawn recently;
before this the screen-box shift also moved level-select scenery (doorway hole) and title texrects. Idempotent."""
import pathlib
T = "PATCH: s6695 radar mark"
ANC = "RECOMP_FUNC void renderRadarMinimap(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
ADD = "    { extern void rs64_radar_mark(void); rs64_radar_mark(); } /* PATCH: s6695 radar mark */\n"
def apply34(text):
    if T in text or text.count(ANC) != 1: return text, 0
    return text.replace(ANC, ANC + ADD), 1
if __name__ == "__main__":
    p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_34.c"); t = p.read_text(); t2, n = apply34(t)
    if n: p.write_text(t2)
    print("funcs_34.c live patched x%d" % n)
