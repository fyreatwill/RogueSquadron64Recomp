"""Install the s6512 full-grid writer/source probe in the live generated tree."""

from pathlib import Path

P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
MARK = "PATCH: s6512 all span writers"
if MARK in T:
    print("s6512 already applied")
    raise SystemExit(0)

decl = "static uint32_t s6512_n[8], s6512_first[8], s6512_last[8]; static uint32_t s6512_base_n; /* " + MARK + " */\n"
anchor = "static uint32_t s6511_wfull[4], s6511_wfirst[4], s6511_wlast[4]; /* PATCH: s6511 full span grid */\n"
assert T.count(anchor) == 1
T = T.replace(anchor, anchor + decl, 1)

old = '''static void s6500_note_writer(uint32_t pc, uint32_t value, uint32_t addr) {
    int i = s6500_writer_index(pc);
    if (i >= 0) { if (!s6500_wcount[i]) s6500_wfirst[i] = value & 0xffu;
      s6500_wlast[i] = value & 0xffu; s6500_wcount[i]++;
      if (addr >= 0x80130DB0u && addr < 0x80132DB0u) { if (!s6511_wfull[i]) s6511_wfirst[i] = addr; s6511_wlast[i] = addr; s6511_wfull[i]++; }
      if (addr >= 0x80130DB0u && addr < 0x80130DC8u) s6500_wmask[i] |= 1u << (addr - 0x80130DB0u);
    }
}
'''
new = old + '''static void s6512_note_writer(uint32_t pc, uint32_t value, uint32_t addr) {
    static const uint32_t pcs[8] = { 0x800426D8u, 0x80042820u, 0x80042A74u, 0x80042A78u,
        0x80042DB4u, 0x80042DC0u, 0x80042EBCu, 0x80042EC4u };
    int i = -1;
    for (int j = 0; j < 8; j++) if (pcs[j] == pc) { i = j; break; }
    if (i >= 0) { if (!s6512_n[i]) s6512_first[i] = addr; s6512_last[i] = addr; s6512_n[i]++; }
}
'''
assert T.count(old) == 1
T = T.replace(old, new, 1)

# Add a distinct call beside every known span-grid store.  The old four-site
# census remains untouched, so s6512 can be compared with prior sessions.
repls = {
    "rs64_m5_writer_parity('B', 0x800426D8u": "s6512_note_writer(0x800426D8u, U32(ctx->r3), U32(ctx->r2));\n    rs64_m5_writer_parity('B', 0x800426D8u",
    "rs64_m5_writer_parity('B', 0x80042820u": "s6512_note_writer(0x80042820u, U32(ctx->r3), U32(ctx->r2));\n    rs64_m5_writer_parity('B', 0x80042820u",
    "rs64_m5_writer_parity('B', 0x80042A74u": "s6512_note_writer(0x80042A74u, U32(ctx->r6), U32(ctx->r3));\n    rs64_m5_writer_parity('B', 0x80042A74u",
    "rs64_m5_writer_parity('B', 0x80042A78u": "s6512_note_writer(0x80042A78u, U32(ctx->r6), U32(ctx->r2));\n    rs64_m5_writer_parity('B', 0x80042A78u",
    "rs64_m5_writer_parity('B', 0x80042DB4u": "s6512_note_writer(0x80042DB4u, U32(ctx->r3), U32(ctx->r2));\n    rs64_m5_writer_parity('B', 0x80042DB4u",
    "rs64_m5_writer_parity('B', 0x80042DC0u": "s6512_note_writer(0x80042DC0u, U32(ctx->r3), U32(ctx->r21));\n    rs64_m5_writer_parity('B', 0x80042DC0u",
    "rs64_m5_writer_parity('B', 0x80042EBCu": "s6512_note_writer(0x80042EBCu, U32(ctx->r2), U32(ctx->r19));\n    rs64_m5_writer_parity('B', 0x80042EBCu",
    "rs64_m5_writer_parity('B', 0x80042EC4u": "s6512_note_writer(0x80042EC4u, U32(ctx->r2), U32(ctx->r21));\n    rs64_m5_writer_parity('B', 0x80042EC4u",
}
for needle, repl in repls.items():
    assert T.count(needle) >= 1, needle
    T = T.replace(needle, repl)

# Capture the grid before this stream invocation can write it.  This is a
# positive control independent of the later return snapshot.
needle = "    if (getenv(\"ROGUESQ_FORFACE_LOG\")) {\n        s6505_key = __atomic_add_fetch(&s6505_invocation_key, 1u, __ATOMIC_RELAXED);"
replacement = """    if (getenv("ROGUESQ_FORFACE_LOG")) {
        if (s6512_base_n++ < 2) { uint32_t h = 2166136261u, nz = 0; for (uint32_t gi = 0; gi < 0x2000u; gi++) { uint32_t gv = (uint8_t)MEM_B(0, (int64_t)(int32_t)(0x80130DB0u + gi)); h ^= gv; h *= 16777619u; if (gv != 0x7fu) nz++; } fprintf(stderr, "[span-base] call=%u dim=64x64 bytes=8192 hash=%08x non127=%u writers=%u,%u,%u,%u,%u,%u,%u,%u\\n", s6512_base_n, h, nz, s6512_n[0], s6512_n[1], s6512_n[2], s6512_n[3], s6512_n[4], s6512_n[5], s6512_n[6], s6512_n[7]); }
        s6505_key = __atomic_add_fetch(&s6505_invocation_key, 1u, __ATOMIC_RELAXED);"""
assert T.count(needle) == 1
T = T.replace(needle, replacement, 1)

# Replace the four-site tail with the complete writer table while retaining
# the existing keyed diff and table bytes on the same line.
old_tail = "s6511_wfull[3], s6511_wfirst[3], s6511_wlast[3]);"
new_tail = "s6511_wfull[3], s6511_wfirst[3], s6511_wlast[3]); fprintf(stderr, \" writers8=\"); for (int wi = 0; wi < 8; wi++) fprintf(stderr, \"%08x:%u:%08x..%08x,\", wi == 0 ? 0x800426D8u : wi == 1 ? 0x80042820u : wi == 2 ? 0x80042A74u : wi == 3 ? 0x80042A78u : wi == 4 ? 0x80042DB4u : wi == 5 ? 0x80042DC0u : wi == 6 ? 0x80042EBCu : 0x80042EC4u, s6512_n[wi], s6512_first[wi], s6512_last[wi]);"
assert T.count(old_tail) == 1
T = T.replace(old_tail, new_tail, 1)
P.write_text(T)
print("s6512 applied")
