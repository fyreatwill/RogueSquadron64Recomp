#!/usr/bin/env python3
"""s7574 GUARD-6 last lever: ungated musyxKeyOnVoice div-trap tally.
The s2122 census (ROGUESQ_LOG_M5_KEYON_CENSUS) only records while the committed VI is one of four early-era
(width, origin) pairs, so at the owner recipe it printed nothing (s7573). This adds an always-on, low-rate tally:
entries, per-divide counts and min divisor, and every guard (break 7 / break 6 -> early return) fire.
Lines go to stderr as [s7574-keyon]. Positive control: ROGUESQ_S7574_KEYON_FORCE0=N zeroes the divisor of the
first divide on its Nth evaluation, so the 0x80090CEC guard must fire once. Measurement only otherwise.
Usage: apply_s7574_keyon_tally.py [RecompiledFuncs dir]"""
import sys, pathlib, re
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7574 keyon tally"
HEAD = "RECOMP_FUNC void musyxKeyOnVoice(uint8_t* rdram, recomp_context* ctx) {\n"
DECL = "/* %s */ extern int rs64_s7574_keyon(uint32_t, uint32_t, uint32_t, uint32_t);\n" % TAG
DIV = re.compile(r"(    rs64_s2122_m5_keyon_event\(rdram, 4u, (0x[0-9A-F]+)u, U32\(ctx->r2\), U32\(ctx->r4\), 0, 0, 0\); /\* PATCH: s2122 key-on divide witness \*/\n)")
GRD = re.compile(r"(    rs64_s2122_m5_keyon_event\(rdram, 2u, (0x[0-9A-F]+)u, U32\(ctx->r2\), U32\(ctx->r4\), 0, 0, 0\); /\* PATCH: s2122 key-on guard \*/\n)")
ENT = "    rs64_s2122_m5_keyon_event(rdram, 1u, 0x80090A3Cu, 0, 0, 0, 0, 0); /* PATCH: s2122 key-on entry */\n"
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text(errors="surrogateescape")
    if HEAD not in t: continue
    if TAG in t: print("already applied", p.name); sys.exit(0)
    t, nd = DIV.subn(lambda m: m.group(1) + "    if (rs64_s7574_keyon(0u, %su, U32(ctx->r2), U32(ctx->r4))) ctx->r4 = 0; /* %s */\n" % (m.group(2), TAG), t)
    t, ng = GRD.subn(lambda m: m.group(1) + "    rs64_s7574_keyon(1u, %su, U32(ctx->r2), U32(ctx->r4)); /* %s */\n" % (m.group(2), TAG), t)
    assert nd == 4 and ng == 8, (nd, ng)
    assert t.count(ENT) == 1, "entry anchor"
    t = t.replace(ENT, ENT + "    rs64_s7574_keyon(2u, 0x80090A3Cu, 0, 0); /* %s */\n" % TAG, 1)
    t = t.replace(HEAD, DECL + HEAD, 1)
    p.write_text(t, errors="surrogateescape"); print("applied", p.name, nd, ng); sys.exit(0)
sys.exit("musyxKeyOnVoice not found")
