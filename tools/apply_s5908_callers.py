"""s5908: tally findSegmentObjectSphereHit calls / v0!=0 per call site (return address = jal pc+8) at all 9 callers.
Positive control: sum of calls over sites == total wrapper calls; site 0x8005D24C (the hooked RET site) hit count must equal fine-hit totals.
Idempotent. Run on N64Recomp/RecompiledFuncs after apply_s5907_hitobj.py; rebuild with cmake."""
import pathlib, re
OLD_HEAD = 'void rs5908_call(uint8_t* rdram, recomp_context* ctx, uint32_t ra) {\n    findSegmentObjectSphereHit(rdram, ctx);\n'
NEW_HEAD = 'void rs5908_call(uint8_t* rdram, recomp_context* ctx, uint32_t ra) {\n    { static int on = -1; if (on < 0) { const char *h = getenv("ROGUESQ_LOG_HITS"), *g = getenv("ROGUESQ_G1E_TRIM"); on = (h && h[0] == \'1\') || (g && g[0] == \'0\'); } if (!on) { findSegmentObjectSphereHit(rdram, ctx); return; } } /* PATCH: s7442 gate */\n    findSegmentObjectSphereHit(rdram, ctx);\n'
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
if "PATCH: s5908 per-caller tally" not in t:  # s7442: the old split test never matched (helper sits AFTER the marker) and re-inserted it
    helper = '''
/* PATCH: s5908 per-caller tally */
static struct { uint32_t ra; unsigned calls, hits; } rs5908_T[16]; static unsigned rs5908_nT, rs5908_tot;
void rs5908_call(uint8_t* rdram, recomp_context* ctx, uint32_t ra) {
    { static int on = -1; if (on < 0) { const char *h = getenv("ROGUESQ_LOG_HITS"), *g = getenv("ROGUESQ_G1E_TRIM"); on = (h && h[0] == '1') || (g && g[0] == '0'); } if (!on) { findSegmentObjectSphereHit(rdram, ctx); return; } } /* PATCH: s7442 gate */
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
# s7442 class CY: the tally ran and printed [s5908] every 1024 sphere-hit calls at the owner recipe (2127 lines, 529 KB of
# stderr per 4-min run, scratch/s7441); gate it on ROGUESQ_LOG_HITS / ROGUESQ_G1E_TRIM=0 (old path). Upgrade an applied tree.
t = g.read_text()
if OLD_HEAD in t and "PATCH: s7442 gate" not in t:
    t = t.replace(OLD_HEAD, NEW_HEAD, 1); g.write_text(t); n += 1
print("sites patched:", n)
