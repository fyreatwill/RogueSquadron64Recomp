"""s6043 G1c: transition watch on the terrain table pointer (0x80136DC4) at the buildVisibleTerrainGridAroundCamera knob site
(0x80043918, runs every frame, runs for ANY multiplier incl. retail). Logs the first 40 changes of the pointer: prev->now, call ordinal,
and the footprint window words 0x80132DB0..BC. Purpose: s6042 dd2s/dd15s died in-mission with tbl==0 and window x0=0x7F7F0017;
dd1 (retail) control shows whether the same nonzero->0 transition happens in retail without crashing. Passive, silent unless it changes. Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s6043 tblwatch"
OLD = "    { /* PATCH: s6036 dd */"
NEW = r'''    { /* PATCH: s6043 tblwatch */ static uint32_t prev6043 = 0xFFFFFFFFu; static unsigned n6043 = 0, calls6043 = 0; calls6043++;
      uint32_t now6043 = (uint32_t)MEM_W(4, (int64_t)(int32_t)0x80136DC0);
      if (now6043 != prev6043 && n6043 < 40) { n6043++; int64_t h = (int64_t)(int32_t)0x80132000;
        fprintf(stderr, "[tblwatch] call=%u tbl %08X->%08X win %08X %08X %08X %08X terr=%ux%u\n", calls6043, prev6043, now6043,
          (uint32_t)MEM_W(0xDB0, h), (uint32_t)MEM_W(0xDB4, h), (uint32_t)MEM_W(0xDB8, h), (uint32_t)MEM_W(0xDBC, h),
          (unsigned)MEM_HU(0xDF8, (int64_t)(int32_t)0x80136000), (unsigned)MEM_HU(0xDFA, (int64_t)(int32_t)0x80136000)); }
      prev6043 = now6043; }
'''
def apply9(text):
    if MARK in text or OLD not in text: return text, 0
    assert text.count(OLD) == 1
    return text.replace(OLD, NEW + OLD), 1
if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
