"""s5908: tally findSegmentObjectSphereHit calls / v0!=0 per call site (return address = jal pc+8) at all 9 callers.
Positive control: sum of calls over sites == total wrapper calls; site 0x8005D24C (the hooked RET site) hit count must equal fine-hit totals.
Idempotent. Run on N64Recomp/RecompiledFuncs after apply_s5907_hitobj.py; rebuild with cmake."""
import pathlib, re
D = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
CALL = "    findSegmentObjectSphereHit(rdram, ctx);"
n = 0
for f in sorted(D.glob("funcs_*.c")):
    t = f.read_text()
    if CALL not in t or "PATCH: s5908" in t: continue
    lines = t.split("\n"); out = []; last = None
    for ln in lines:
        m = re.search(r"// 0x([0-9A-F]{8}): jal\s+0x8006A944", ln)
        if m: last = int(m.group(1), 16) + 8
        if ln == CALL:
            assert last, (f, ln)
            ln = "    { void rs5908_call(uint8_t*, recomp_context*, uint32_t); rs5908_call(rdram, ctx, 0x%08Xu); } /* PATCH: s5908 */" % last; n += 1; last = None
        out.append(ln)
    f.write_text("\n".join(out))
g = D / "funcs_16.c"; t = g.read_text()
if "rs5908_call" not in t.split("RECOMP_FUNC void findSegmentObjectSphereHit")[0]:
    helper = '''
/* PATCH: s5908 per-caller tally */
static struct { uint32_t ra; unsigned calls, hits; } rs5908_T[16]; static unsigned rs5908_nT, rs5908_tot;
void rs5908_call(uint8_t* rdram, recomp_context* ctx, uint32_t ra) {
    findSegmentObjectSphereHit(rdram, ctx);
    unsigned z; for (z = 0; z < rs5908_nT; z++) if (rs5908_T[z].ra == ra) break;
    if (z == rs5908_nT && z < 16) { rs5908_T[z].ra = ra; rs5908_nT++; }
    if (z < 16) { rs5908_T[z].calls++; if ((uint32_t)ctx->r2) rs5908_T[z].hits++; }
    if ((++rs5908_tot & 1023) == 0) { fprintf(stderr, "[s5908] callers tot=%u:", rs5908_tot); for (z = 0; z < rs5908_nT; z++) fprintf(stderr, " %08x{calls=%u hits=%u}", rs5908_T[z].ra, rs5908_T[z].calls, rs5908_T[z].hits); fprintf(stderr, "\\n"); }
}
'''
    marker = "RECOMP_FUNC void findSegmentObjectSphereHit"
    i = t.index(marker); j = t.index("\n}\n", i) + 3
    t = t[:j] + helper + t[j:]; g.write_text(t)
print("sites patched:", n)
