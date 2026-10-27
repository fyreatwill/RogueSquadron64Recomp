"""s6500: retain post-bin span snapshots until matching stream return."""
import pathlib

p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
tag = "PATCH: s6500 postring"
if tag in t:
    # The first attempt used a file-wide newline anchor and placed the
    # postring print in an unrelated file-scope diagnostic. Repair that
    # generated output before continuing, so this fixup is rerunnable.
    bad = ('fprintf(stderr, "\\n"); { uint32_t ri = s6497_seq & 63u; fprintf(stderr, "[postring] seq=%u ring=%u stores=%u non127=%u tbl=", s6497_seq, s6500_seq[ri], s6500_stores[ri], s6500_non127[ri]); for (int i = 0; i < 24; i++) fprintf(stderr, "%u,", (unsigned)s6500_tbl[ri][i]); fprintf(stderr, " writers=%u:%u..%u,%u:%u..%u,%u:%u..%u,%u:%u..%u\\n", s6500_wcount[0], s6500_wfirst[0], s6500_wlast[0], s6500_wcount[1], s6500_wfirst[1], s6500_wlast[1], s6500_wcount[2], s6500_wfirst[2], s6500_wlast[2], s6500_wcount[3], s6500_wfirst[3], s6500_wlast[3]); } }')
    t = t.replace(bad, 'fprintf(stderr, "\\n"); }', 1)
    # Continue below to place the corrected print at the streamdump site.

needle = "static int8_t s6499_post_tbl[24]; /* PATCH: s6499 storecensus */\n"
assert t.count(needle) == 1
decl = needle + (
    "static uint32_t s6500_seq[64], s6500_stores[64], s6500_non127[64];\n"
    "static uint8_t s6500_tbl[64][24];\n"
    "static uint32_t s6500_wcount[4], s6500_wfirst[4], s6500_wlast[4]; /* " + tag + " */\n"
    "static int s6500_writer_index(uint32_t pc) {\n"
    "    switch (pc) { case 0x80042DB4u: return 0; case 0x80042DC0u: return 1;\n"
    "    case 0x80042EBCu: return 2; case 0x80042EC4u: return 3; default: return -1; }\n"
    "}\n"
    "static void s6500_note_writer(uint32_t pc, uint32_t value) {\n"
    "    int i = s6500_writer_index(pc);\n"
    "    if (i >= 0) { if (!s6500_wcount[i]) s6500_wfirst[i] = value & 0xffu;\n"
    "      s6500_wlast[i] = value & 0xffu; s6500_wcount[i]++; }\n"
    "}\n")
t = t.replace(needle, decl, 1)

old = ("      s6499_post_seq = s6497_seq;\n"
       "      for (int i = 0; i < 24; i++) s6499_post_tbl[i] = (int8_t)MEM_B(0, (int64_t)(int32_t)(0x80130DB0 + i));\n")
assert t.count(old) == 1
new = ("      s6499_post_seq = s6497_seq;\n"
       "      { uint32_t ri = s6497_seq & 63u; s6500_seq[ri] = s6497_seq; s6500_stores[ri] = s6499_stores; s6500_non127[ri] = s6499_non127;\n"
       "        for (int i = 0; i < 24; i++) { uint8_t v = (uint8_t)MEM_B(0, (int64_t)(int32_t)(0x80130DB0 + i)); s6499_post_tbl[i] = (int8_t)v; s6500_tbl[ri][i] = v; } }\n")
t = t.replace(old, new, 1)

for pc, addr, val in (("0x80042DB4u", "ctx->r2", "ctx->r3"),
                      ("0x80042DC0u", "ctx->r21", "ctx->r3"),
                      ("0x80042EBCu", "ctx->r19", "ctx->r2"),
                      ("0x80042EC4u", "ctx->r21", "ctx->r2")):
    old = "s6499_note(U32(" + addr + "), U32(" + val + ")); MEM_B"
    new = "s6499_note(U32(" + addr + "), U32(" + val + ")); s6500_note_writer(" + pc + ", U32(" + val + ")); MEM_B"
    assert t.count(old) >= 1, (pc, old)
    t = t.replace(old, new)

old = ('fprintf(stderr, "[streamdump] %s seq=%u ret=%u post=%u nstore=%u non127=%u bounds=%d,%d,%d,%d stores=%08x..%08x w=%d,%d,%d,%d tbl=", emp ? "EMPTY" : "ok", s6497_seq, s6497_ret_seq, s6499_post_seq, s6499_stores, s6499_non127, s6497_x0, s6497_x1, s6497_z0, s6497_z1, s6497_first, s6497_last, (int)MEM_W(0, (int64_t)(int32_t)0x80132DB0), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB4), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB8), (int)MEM_W(0, (int64_t)(int32_t)0x80132DBC));')
assert t.count(old) == 1
new = ('fprintf(stderr, "[streamdump] %s seq=%u ret=%u post=%u ring=%u/%u nstore=%u non127=%u bounds=%d,%d,%d,%d stores=%08x..%08x w=%d,%d,%d,%d tbl=", emp ? "EMPTY" : "ok", s6497_seq, s6497_ret_seq, s6499_post_seq, s6500_seq[s6497_seq & 63u], s6500_non127[s6497_seq & 63u], s6499_stores, s6499_non127, s6497_x0, s6497_x1, s6497_z0, s6497_z1, s6497_first, s6497_last, (int)MEM_W(0, (int64_t)(int32_t)0x80132DB0), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB4), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB8), (int)MEM_W(0, (int64_t)(int32_t)0x80132DBC));')
t = t.replace(old, new, 1)

lines = t.splitlines(True)
idx = next(i for i, line in enumerate(lines) if '[streamdump]' in line)
assert 'tb[i]' in lines[idx + 1]
lines[idx + 1] = ('      for (int i = 0; i < 24; i++) fprintf(stderr, "%d,", tb[i]); fprintf(stderr, "\\n"); '
                  '{ uint32_t ri = s6497_seq & 63u; fprintf(stderr, "[postring] seq=%u ring=%u stores=%u non127=%u tbl=", s6497_seq, s6500_seq[ri], s6500_stores[ri], s6500_non127[ri]); '
                  'for (int i = 0; i < 24; i++) fprintf(stderr, "%u,", (unsigned)s6500_tbl[ri][i]); '
                  'fprintf(stderr, " writers=%u:%u..%u,%u:%u..%u,%u:%u..%u,%u:%u..%u\\n", '
                  's6500_wcount[0], s6500_wfirst[0], s6500_wlast[0], s6500_wcount[1], s6500_wfirst[1], s6500_wlast[1], '
                  's6500_wcount[2], s6500_wfirst[2], s6500_wlast[2], s6500_wcount[3], s6500_wfirst[3], s6500_wlast[3]); } } } /* PATCH: s6493b emptydump */\\n')
t = ''.join(lines)

p.write_text(t)
print("ok")
