"""s4899: retrace/audio-done/synth cadence join. Adds rs64_s4899_ev(kind) calls (helper lives in
src/main/upstream_compat.cpp, per-VI flush in rt64_render_context.cpp). Gate ROGUESQ_LOG_S4899=1.
Sites: funcs_4.c recv1 exit (R) / recv2 exit (T); funcs_23.c audio-loop recv enter (W) / return (A|a);
funcs_24.c musyxSynthFrame entry (S). ORIGIN: read-only counters. Idempotent live-tree patch."""
from pathlib import Path
base = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
DECL = 'extern void rs64_s4899_ev(char); /* PATCH: s4899 */\n'
def patch_after_label(fn, label_anchor, new):
    """Insert `new` immediately after the first line of label_anchor (the label), idempotently."""
    p = base / fn; t = p.read_text()
    if new in t: print(fn, "already"); return
    assert t.count(label_anchor) == 1, (fn, label_anchor[:40], t.count(label_anchor))
    first, rest = label_anchor.split("\n", 1)
    t = t.replace(label_anchor, first + "\n" + new + rest, 1)
    if DECL not in t:
        inc = '#include "recomp.h"\n'; assert inc in t
        t = t.replace(inc, inc + DECL, 1)
    p.write_text(t); print(fn, "patched")
def patch(fn, anchor, new, before=False):
    p = base / fn; t = p.read_text()
    if new in t: print(fn, "already"); return
    assert t.count(anchor) == 1, (fn, anchor[:40], t.count(anchor))
    t = t.replace(anchor, (new + anchor) if before else (anchor + new), 1)
    if DECL not in t:
        inc = '#include "recomp.h"\n'; assert inc in t
        t = t.replace(inc, inc + DECL, 1)
    p.write_text(t); print(fn, "patched")
patch_after_label("funcs_4.c", "    after_3:\n    { // PATCH: vi-cb-recv1 exit diagnostic",
      "    rs64_s4899_ev('R'); /* PATCH: s4899 */\n")
patch_after_label("funcs_4.c", "    after_7:\n    { // PATCH: vi-cb-recv2 exit diagnostic",
      "    rs64_s4899_ev('T'); /* PATCH: s4899 */\n")
p = base / "funcs_23.c"; t = p.read_text()
if "PATCH: s4899" in t: print("funcs_23.c already")
else:
    a = "    rs64_m5_frequency_caller(rdram, ctx, 0x8008EE1Cu); /* PATCH: s3438 frequency caller */\n"
    assert t.count(a) == 1
    t = t.replace(a, a + "    rs64_s4899_ev('W'); /* PATCH: s4899 */\n", 1)
    b = "    after_4:\n    rs64_audioloop_witness(rdram, ctx, 1u); /* PATCH: s4432 audioloop */\n"
    assert t.count(b) == 1
    t = t.replace(b, b + "    rs64_s4899_ev(MEM_BU(MEM_W(ctx->r29, 0X10), 0X0) == 1 ? 'A' : 'a'); /* PATCH: s4899 */\n", 1)
    inc = '#include "recomp.h"\n'; t = t.replace(inc, inc + DECL, 1)
    p.write_text(t); print("funcs_23.c patched")
patch("funcs_24.c", "    rs64_m5_synth_parent_gate_event(0x8009123Cu, 0u, 0u, 0u, 0u, 0u, 0u, U32(ctx->r31)); /* PATCH: musyxSynthFrame parent entry 0x8009123C */\n",
      "    rs64_s4899_ev('S'); /* PATCH: s4899 */\n")
