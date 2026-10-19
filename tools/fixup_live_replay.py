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
sys.exit(1 if fail else 0)
