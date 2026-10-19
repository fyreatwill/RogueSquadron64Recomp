#!/usr/bin/env python3
"""Replay of live-tree hand edits that the vendored fixer does not emit (s5540).
Usage: fixup_live_replay.py <RecompiledFuncs dir>. Idempotent; prints per-edit status."""
import re
import sys
import pathlib

d = pathlib.Path(sys.argv[1])
fail = 0


def sub(name, fname, old, new):
    global fail
    p = d / fname
    t = p.read_text()
    if new in t:
        print(f"{name}: already applied")
        return
    if t.count(old) != 1:
        print(f"{name}: FAIL expected 1 match, got {t.count(old)}")
        fail += 1
        return
    p.write_text(t.replace(old, new))
    print(f"{name}: ok")


# identifier renames mirrored from the live funcs.h
for old, new in (("func_8000040C", "clearMemory16ByteBlocks"),
                 ("fake_func_800B47C4", "menuControllerInputPreamble"),
                 ("fake_func_800B58B4", "playerAwingInitPreamble")):
    for p in list(sorted(d.glob("*.c"))) + [d / "funcs.h", d / "recomp_overlays.inl"]:
        if p.exists():
            t = p.read_text()
            if re.search(rf"\b{old}\b", t):
                p.write_text(re.sub(rf"\b{old}\b", new, t))
print("renames: done")

# funcs_0: MEM_W takes (offset, base)
sub("memw_order", "funcs_0.c",
    "MEM_W(S32(0X80110000u), -0XE8)", "MEM_W(-0XE8, S32(0X80110000u))")

# funcs_4: alloc_tail_guard2 force-log switch
sub("guard2_force", "funcs_4.c",
    "        if (r3_lo < 0x80000000u || r3_lo >= 0x80800000u) {\n"
    "            if (s_alloc_tail_guard2_enabled) {",
    "        static int s_alloc_tail_guard2_force = -1;\n"
    "        if (s_alloc_tail_guard2_force < 0) { const char* e = getenv(\"ROGUESQ_FORCE_ALLOC_TAIL_GUARD2\"); "
    "s_alloc_tail_guard2_force = (e && e[0] && e[0] != '0') ? 1 : 0; }\n"
    "        if (r3_lo < 0x80000000u || r3_lo >= 0x80800000u || s_alloc_tail_guard2_force) {\n"
    "            if (s_alloc_tail_guard2_enabled) {")
sub("guard2_goto", "funcs_4.c",
    "s_alloc_tail_guard2_n++;\n            }\n            goto L_80013EFC;\n",
    "s_alloc_tail_guard2_n++;\n            }\n"
    "            if (r3_lo < 0x80000000u || r3_lo >= 0x80800000u) goto L_80013EFC;  // force = log only\n")

# funcs_5: waitForPostSwapAck entry diagnostic
hdr = ("    rs64_s4913_mark(rdram, \"waitForPostSwapAck\"); // PATCH: s4913 ordering mark\n"
       "    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n")
sub("swap_ack_entry", "funcs_5.c", hdr,
    hdr +
    "    static long long s_swap_ack_call_n = 0;\n"
    "    static int s_swap_ack_wait_enabled = -1;\n"
    "    { // PATCH: waitForPostSwapAck entry diagnostic (s177) -- see fixup_game_funcs.py comment\n"
    "        if (s_swap_ack_wait_enabled < 0) { const char* e = getenv(\"ROGUESQ_LOG_SWAP_ACK_WAIT\"); "
    "s_swap_ack_wait_enabled = (e && e[0] && e[0] != '0') ? 1 : 0; }\n"
    "        if (s_swap_ack_wait_enabled) {\n"
    "            fprintf(stderr, \"[swap-ack-wait] call=%lld enter\\n\", s_swap_ack_call_n);\n"
    "        }\n"
    "        s_swap_ack_call_n++;\n"
    "    }\n")


# funcs_24: statement-order differences (s5541). Each rule moves every line matching
# `pat` by `delta` lines (negative = up) and asserts the expected match count.
def move_lines(name, fname, pat, delta, expect):
    global fail
    p = d / fname
    ls = p.read_text().split("\n")
    idx = [i for i, l in enumerate(ls) if re.search(pat, l)]
    if len(idx) != expect:
        print(f"{name}: FAIL expected {expect} matches, got {len(idx)}")
        fail += 1
        return
    for i in (reversed(idx) if delta > 0 else idx):
        ls.insert(i + delta, ls.pop(i))
    p.write_text("\n".join(ls))
    print(f"{name}: ok")


move_lines("order_s5223", "funcs_24.c", r"^    rs64_s5223_entry_join\(rdram, \"callsite-", -2, 4)
move_lines("order_lowfield", "funcs_24.c", r"^    rs64_m5_lowfield_store\('[HBW]', 0x800(91698|916A4|917C4|917F4)u", 1, 4)
move_lines("order_s4873", "funcs_24.c", r"^    \{ extern void rs64_s4873_ev\(int\); rs64_s4873_ev\(1\);", -4, 1)
sub("memw_order_24", "funcs_24.c",
    "MEM_W(S32(0x80150000), -0X6908)", "MEM_W(-0X6908, S32(0x80150000))")
# funcs_24 live-only diag content and layers the live tree lacks (s5542)
def cut(name, fname, old, new=""):
    sub(name, fname, old, new) if new else _cut(name, fname, old)


def _cut(name, fname, old):
    global fail
    p = d / fname
    t = p.read_text()
    if t.count(old) != 1:
        print(f"{name}: FAIL expected 1 match, got {t.count(old)}")
        fail += 1
        return
    p.write_text(t.replace(old, ""))
    print(f"{name}: ok")


cut("cb_transfer_24", "funcs_24.c",
    "    { extern void rs64_m5_callback_transfer_event(unsigned, unsigned, unsigned);\n"
    "      rs64_m5_callback_transfer_event(0x800919ECu, U32(ctx->r2), U32(ctx->r4)); }\n")
t24 = (d / "funcs_24.c").read_text()
m = re.search(r"^    \{ extern void rs64_m5_callback_teardown_event\(.*PATCH: s4894 m5 callback teardown return \*/\n", t24, re.M)
if m:
    (d / "funcs_24.c").write_text(t24.replace(m.group(0), "", 1)); print("cb_teardown_24: ok")
else:
    print("cb_teardown_24: already applied or no match")
cut("pause_comment_24", "funcs_24.c",
    " /* s4698: PAUSE=2 holds the pause past wait-exit (discriminator) */")
sub("spin2_gate_24", "funcs_24.c",
    "        rs64_m5_field348_store(width, pc, addr, value);\n    }\n",
    "        rs64_m5_field348_store(width, pc, addr, value);\n    }\n"
    "    extern void rs64_m5_spin2_gate_store(char width, uint32_t pc,\n"
    "                                          uint32_t addr, uint32_t value);\n"
    "    rs64_m5_spin2_gate_store(width, pc, addr, value);\n")
cut("s4690_comment_24", "funcs_24.c", " PATCH: s4690 external-entry phase attribution")

# funcs_24: helper block order (s5542). Live has the s4899 extern right after recomp.h and
# the s4867/s4864 helper blocks just before `#include "funcs.h"`.
def move_helpers_24():
    global fail
    p = d / "funcs_24.c"
    ls = p.read_text().split("\n")
    ext = "extern void rs64_s4899_ev(char); /* PATCH: s4899 */"
    try:
        a = ls.index("/* PATCH: s4867 bound helper */")
        e = ls.index(ext)
        anchor = next(i for i in range(e, len(ls)) if ls[i] == '#include "funcs.h"') - 2
    except (ValueError, StopIteration):
        print("helpers_24: already applied or no match")
        return
    if ls[anchor] != "#include <stdlib.h>" or not (a < e < anchor):
        print("helpers_24: FAIL layout")
        fail += 1
        return
    block = ls[a:e]
    mid = ls[e + 1:anchor]
    ls = ls[:1] + [ext] + ls[1:a] + mid + block + ls[anchor:]
    p.write_text("\n".join(ls))
    print("helpers_24: ok")


move_helpers_24()

# funcs_24: s5228 census + fill_range_edge helpers sit right after the s2084 comment in live (s5542).
def move_s5228_24():
    global fail
    p = d / "funcs_24.c"
    ls = p.read_text().split("\n")
    anc = "/* PATCH: s2084 fill-range reachability table */"
    try:
        a = ls.index("/* PATCH: s5228 store census */")
        e = a + next(i for i, l in enumerate(ls[a:]) if l.startswith("extern void rs64_s2031_m5_gate_event"))
        k = ls.index(anc)
    except (ValueError, StopIteration):
        print("s5228_24: already applied or no match")
        return
    if k > a:
        print("s5228_24: FAIL layout")
        fail += 1
        return
    block = ls[a:e]
    ls = ls[:k + 1] + block + ls[k + 1:a] + ls[e:]
    p.write_text("\n".join(ls))
    print("s5228_24: ok")


move_s5228_24()

# funcs_24 tail rules (s5543): s4534 phase gate absent in live; format drops phase/width/origin.
cut("s4534_gate_24", "funcs_24.c",
    "    extern uint32_t rs64_phase_ord(void);\n"
    "    extern uint32_t rs64_vi_committed_width(void);\n"
    "    extern uint32_t rs64_vi_committed_origin(void);\n"
    "    uint32_t phase = rs64_phase_ord();\n"
    "    uint32_t vi_width = rs64_vi_committed_width();\n"
    "    uint32_t vi_origin = rs64_vi_committed_origin() & 0x00FFFFFFu;\n"
    "    if (!((vi_width == 1024u && vi_origin == 0x00790400u) ||\n"
    "          (vi_width == 512u && vi_origin == 0x006AB400u))) return;\n")
_f = "phase=%u width=%u origin=0x%06X "
t24 = (d / "funcs_24.c").read_text()
if "phase, vi_width, vi_origin, " in t24:
    t24 = t24.replace("[s4534-jal] kind=arm " + _f, "[s4534-jal] kind=arm ")
    t24 = t24.replace("[s4534-jal] kind=%s " + _f, "[s4534-jal] kind=%s ")
    t24 = t24.replace("            phase, vi_width, vi_origin, site, pc,", "            site, pc,")
    t24 = t24.replace('bad ? "bad" : "ctl", phase, vi_width, vi_origin, site,', 'bad ? "bad" : "ctl", site,')
    (d / "funcs_24.c").write_text(t24)
    print("s4534_fmt_24: ok")

# s4938 extern sits after the s5078 extern in live, not mid-file
ext38 = "extern void rs64_s4938_aux_store(char, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);\n"
t24 = (d / "funcs_24.c").read_text()
anc = "extern void rs64_s5078_flight_store(uint32_t, uint32_t);\n"
if t24.count(ext38) == 1 and t24.count(anc) == 1 and t24.index(ext38) > t24.index(anc):
    t24 = t24.replace(ext38, "").replace(anc, anc + ext38)
    (d / "funcs_24.c").write_text(t24)
    print("s4938_ext_24: ok")
else:
    print("s4938_ext_24: already applied or no match")

# s4873 RA diagnostic gained a timestamp in live
sub("s4873_ra_fmt_24", "funcs_24.c",
    'for (int k = 0; k < nra; k++) fprintf(stderr, "[s4873] RA 0x%08X x%lu\\n", ras[k], cnt[k]); fflush(stderr); }',
    'struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); fprintf(stderr, "[s4873] RA t_ms=%lu n=%lu msgs=%lu\\n", '
    '(unsigned long)(ts.tv_sec*1000UL + ts.tv_nsec/1000000UL), n, rs64_s4873_n[0]); '
    'for (int k = 0; k < nra; k++) fprintf(stderr, "[s4873] RA 0x%08X x%lu\\n", ras[k], cnt[k]); fflush(stderr); }')
move_lines("order_s5223_site", "funcs_24.c", r"^    rs64_s5223_entry_join\(rdram, \"callsite-0x800903F0\"", -2, 1)
move_lines("order_s4873_fix", "funcs_24.c", r"^    \{ extern void rs64_s4873_ev\(int\); rs64_s4873_ev\(1\);", 1, 1)

# s4700 cbtable: live puts the 2-line block at the top of the musyxSynthFrame wrapper
p = d / "funcs_24.c"
ls = p.read_text().split("\n")
try:
    a = next(i for i, l in enumerate(ls) if "PATCH: s4700 cbtable" in l)
    w = next(i for i, l in enumerate(ls) if l.startswith("RECOMP_FUNC void musyxSynthFrame(uint8_t* rdram"))
    if a > w:
        blk = ls[a:a + 2]
        del ls[a:a + 2]
        ls[w + 1:w + 1] = blk
        p.write_text("\n".join(ls))
        print("s4700_move_24: ok")
    else:
        print("s4700_move_24: already applied")
except StopIteration:
    print("s4700_move_24: FAIL no match"); fail += 1

# funcs_23 (s5544): live hoists the s4870 helper block above the s4784 helper; externs sit right after recomp.h
p = d / "funcs_23.c"
t23 = p.read_text()
_h = "#include \"recomp.h\"\n\n/* PATCH: s4784 gap order helper */"
_i = t23.find("extern void rs64_s4899_ev(char); /* PATCH: s4899 */\n")
_c = t23.find("/* PATCH: s4870 producer/entry helper */")
_j = t23.find("#include <stdlib.h>\n#include <stdio.h>\n#include \"funcs.h\"")
if t23.startswith(_h) and 0 < _i < _c < _j:
    ext = t23[_i:_c].lstrip("\n")
    body = t23[_c:_j]
    rest = t23[:_i].rstrip("\n").split("\n", 2)
    t23 = ("#include \"recomp.h\"\n" + ext.rstrip("\n") + "\n\n" + body + "\n" + t23[len("#include \"recomp.h\"\n"):_i].lstrip("\n").join(["", ""]) + t23[_j:])
    p.write_text(t23)
    print("s4870_hoist_23: ok")
else:
    print("s4870_hoist_23: already applied or no match")

# funcs_23 (s5544) remaining: blank after hoisted block, extern block move, B40 ternary polarity, entry-census line, gate-clear order
p23 = d / "funcs_23.c"
t23 = p23.read_text()
_ext4 = ("extern void rs64_s4597_target_store(char, uint32_t, uint32_t, uint32_t);\n"
         "extern void rs64_audioloop_witness(uint8_t* rdram, recomp_context* ctx, uint32_t stage);\n"
         "extern void rs64_m5_lowfield_store(char, uint32_t, uint32_t, uint32_t);\n"
         "extern void rs64_s4299_store_watch(char, uint32_t, uint32_t, uint32_t);\n")
_anc4 = "extern void rs64_s4222_pc(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);\n"
if t23.count(_ext4) == 1 and t23.count(_anc4) == 1 and t23.index(_ext4) < t23.index(_anc4):
    t23 = t23.replace(_ext4, "").replace(_anc4, _ext4 + _anc4)
    print("ext4_move_23: ok")
_b = 'getenv("ROGUESQ_M5_B40_VALUE")[0] == \'0\') ? 0 : ctx->r2)'
if _b in t23:
    t23 = t23.replace(_b, 'getenv("ROGUESQ_M5_B40_VALUE")[0] != \'0\') ? ctx->r2 : 0)')
    print("b40_polarity_23: ok")
t23 = re.sub(r"^        rs64_m5_selector_store_entry\(0x8008EB5Cu, .*s4712 reapplyDisplayMode census \*/\n", "", t23, flags=re.M)
p23.write_text(t23)
move_lines("order_s4784_gate", "funcs_23.c", r"^        \{ /\* PATCH: s4784 gate-clear", -2, 1)

sys.exit(1 if fail else 0)
