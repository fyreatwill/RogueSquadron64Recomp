#!/usr/bin/env python3
"""s7626 G6c step 3c instrument (measurement only): does the game's scene-graph walk reach the stand-ins, and with what matrix?
traverseSceneGraphRecursive (0x80015548) loop head L_8001558C: $s2 = node. Before its jal convertMat3x4ToN64Mtx at 0x800155E4
($a1 = sp+0x10 camera-space mat3x4, translation at +0x24/+0x28/+0x2C): host rs64_sg_draw tallies the node (stand-in region
0x81700000..0x81800000 vs every other node = the control) and inside convertMat3x4ToN64Mtx at 0x80018DEC the scale $f12, so
the packed translation t*f12 can be compared with the N64 matrix reach (|t| < 128). Gated by rs64_sg_probe (host sets it only
under ROGUESQ_STANDINS_LOG=1), so default runs pay one load per node. Idempotent; RS64_REPLAY after apply_s7625_standins_far.py."""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7626 sg probe"
f = D / "funcs_4.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied", TAG)
else:
    a = "    s6555_visit(U32(ctx->r18), U32(ctx->r29), 0); /* PATCH: s6555 travwalk */\n"
    assert t.count(a) == 1, ("visit", t.count(a))
    t = t.replace(a, a + "    { extern int rs64_sg_probe; if (__builtin_expect(rs64_sg_probe, 0)) { extern void rs64_sg_visit(uint32_t); rs64_sg_visit(U32(ctx->r18)); } } /* %s */\n" % TAG, 1)
    b = ("    ctx->r31 = 0x800155EC; // PATCH: s2475 JAL link for convertMat3x4ToN64Mtx\n"
         "    ctx->r5 = ADD32(ctx->r29, 0X10);\n"
         "    convertMat3x4ToN64Mtx(rdram, ctx);\n")
    assert t.count(b) == 1, ("draw", t.count(b))
    t = t.replace(b, b.replace("    convertMat3x4ToN64Mtx(rdram, ctx);\n",
        "    { extern int rs64_sg_probe; if (__builtin_expect(rs64_sg_probe, 0)) { extern void rs64_sg_draw(uint8_t*, uint32_t, uint32_t); rs64_sg_draw(rdram, U32(ctx->r18), U32(ctx->r5)); } } /* %s */\n"
        "    convertMat3x4ToN64Mtx(rdram, ctx);\n"
        "    { extern int rs64_sg_probe; if (__builtin_expect(rs64_sg_probe, 0)) { extern void rs64_sg_draw_end(void); rs64_sg_draw_end(); } } /* %s */\n" % (TAG, TAG)), 1)
    c = "    // 0x80018DEC: mul.s       $f4, $f4, $f12\n"
    assert t.count(c) == 1, ("mul", t.count(c))
    t = t.replace(c, "    { extern int rs64_sg_probe; if (__builtin_expect(rs64_sg_probe, 0)) { extern void rs64_sg_scale(float, float, float, float); rs64_sg_scale(ctx->f4.fl, ctx->f6.fl, ctx->f8.fl, ctx->f12.fl); } } /* %s */\n" % TAG + c, 1)
    f.write_text(t, errors="surrogateescape"); print("applied", TAG)

# Part 2: processSceneNode (0x80014FA0) branch tally per leaf, stand-in region vs others. The traverse call site (0x80015644) sets the
# side from $a2 (the leaf) and records a zero return (zero stops the whole walk); inside, every label below and every face-render call
# (with its return value) is counted. Host: rs64_psn_mark / rs64_psn_side in src/main/rs64_standins.cpp.
TAG2 = "PATCH: s7626 psn probe"
t = f.read_text(errors="surrogateescape")
if TAG2 in t: print("already applied", TAG2)
else:
    s = t.index("RECOMP_FUNC void processSceneNode(uint8_t* rdram, recomp_context* ctx) {")
    e = t.index("RECOMP_FUNC ", s + 10)
    body = t[s:e]
    M = lambda k: "    { extern int rs64_sg_probe; if (__builtin_expect(rs64_sg_probe, 0)) { extern void rs64_psn_mark3(uint8_t*, int, int, uint32_t); rs64_psn_mark3(rdram, %d, (int)ctx->r2, U32(ctx->r16)); } } /* %s */\n" % (k, TAG2)
    labels = ["L_80014FE8", "L_80015040", "L_8001513C", "L_800151E0", "L_80015320", "L_80015360", "L_80015528"]
    for i, L in enumerate(labels):
        a = "\n%s:\n" % L
        assert body.count(a) == 1, (L, body.count(a))
        body = body.replace(a, a + M(i), 1)
    k = len(labels)
    import re
    calls = ["renderUnlitMeshFaces", "renderLitTexturedMeshFaces", "renderFlatMeshFaceGroup", "renderLitMeshFaceGroup", "submitSceneNodeRender"]
    out = []; n = 0
    for line in body.split("\n"):
        out.append(line)
        m = re.match(r"^    (\w+)\(rdram, ctx\);$", line)
        if m and m.group(1) in calls:
            out.append(M(100 + n).rstrip("\n")); n += 1
    body = "\n".join(out)
    t = t[:s] + body + t[e:]
    c = "    processSceneNode(rdram, ctx);\n"
    i0 = t.index("RECOMP_FUNC void traverseSceneGraphRecursive(")
    i1 = t.index(c, i0)
    assert t.count(c, i0, t.index("RECOMP_FUNC ", i0 + 10)) == 1
    t = t[:i1] + ("    { extern int rs64_sg_probe; if (__builtin_expect(rs64_sg_probe, 0)) { extern void rs64_psn_side(uint32_t); rs64_psn_side(U32(ctx->r6)); } } /* %s */\n" % TAG2) + c + \
        ("    { extern int rs64_sg_probe; if (__builtin_expect(rs64_sg_probe, 0)) { extern void rs64_psn_mark3(uint8_t*, int, int, uint32_t); rs64_psn_mark3(rdram, 99, (int)ctx->r2, U32(ctx->r16)); extern void rs64_psn_side(uint32_t); rs64_psn_side(0); } } /* %s */\n" % TAG2) + t[i1 + len(c):]
    f.write_text(t, errors="surrogateescape"); print("applied", TAG2, "render call marks", n)

# Part 3: the prebuilt-DL queue (0x80116400, 12-byte entries {DL, matrix, leaf}, count *0x80128C6C) that processSceneNode's
# L_80014FE8 fills: at each count reset (frameStartReset 0x8000A748, initRenderStateArrays 0x8000B67C) the host tallies which
# queued entries carry a stand-in matrix and which beginFrameDLChunk read (0x8000AB4C/AD08/AE30/AF58, entry = $at + 0x6400).
TAG3 = "PATCH: s7626 queue probe"
f3 = D / "funcs_3.c"
t = f3.read_text(errors="surrogateescape")
if TAG3 in t: print("already applied", TAG3); sys.exit(0)
for pc in ("8000A748", "8000B67C"):
    a = "    // 0x%s: sw          $zero, -0x7394($at)\n" % pc
    assert t.count(a) == 1, (pc, t.count(a))
    t = t.replace(a, "    { extern int rs64_sg_probe; if (__builtin_expect(rs64_sg_probe, 0)) { extern void rs64_q_reset(uint8_t*, uint32_t); rs64_q_reset(rdram, 0x%su); } } /* %s */\n" % (pc, TAG3) + a, 1)
for pc, ins in (("8000AB4C", "lw          $v0, 0x6400($at)"), ("8000AD08", "lw          $v0, 0x6404($at)"), ("8000AE30", "lw          $a0, 0x6404($at)"), ("8000AF58", "lw          $v1, 0x6400($at)")):
    a = "    // 0x%s: %s\n" % (pc, ins)
    assert t.count(a) == 1, (pc, t.count(a))
    t = t.replace(a, "    { extern int rs64_sg_probe; if (__builtin_expect(rs64_sg_probe, 0)) { extern void rs64_q_read(uint32_t); rs64_q_read(U32(ctx->r1) + 0x6400u); } } /* %s */\n" % TAG3 + a, 1)
f3.write_text(t, errors="surrogateescape"); print("applied", TAG3)
