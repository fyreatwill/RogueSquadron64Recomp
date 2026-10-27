"""s6499 G1c: count span-table byte stores and snapshot the table at bin return.

This is a regeneration-safe fixup for the generated funcs_9.c output. It is
intentionally bounded by the existing ROGUESQ_FORFACE_LOG stream budget.
"""
import pathlib

p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
tag = "PATCH: s6499 storecensus"
if tag in t:
    print("already")
    raise SystemExit

# s6496 was inserted twice by its original fixup; retain one declaration so
# this instrumentation build has a deterministic generated-C input.
dup = "static float s6496_v[15]; static uint32_t s6496_a0, s6496_n, s6496_tot; static float s6496_div; "
if t.count(dup) == 2:
    first = t.find(dup)
    second = t.find(dup, first + len(dup))
    t = t[:second] + t[second + len(dup):]

needle = "static int32_t s6497_x0, s6497_x1, s6497_z0, s6497_z1; /* PATCH: s6497 rasterizerbounds */\n"
assert t.count(needle) == 1
decl = needle + r'''static uint32_t s6499_stores, s6499_non127, s6499_first_addr, s6499_last_addr;
static uint32_t s6499_first_val, s6499_last_val, s6499_post_seq;
static int8_t s6499_post_tbl[24]; /* PATCH: s6499 storecensus */
static void s6499_note(uint32_t addr, uint32_t value) {
    uint8_t v = (uint8_t)value;
    if (!s6499_stores) { s6499_first_addr = addr; s6499_first_val = v; }
    s6499_last_addr = addr; s6499_last_val = v; s6499_stores++;
    if (v != 0x7f) s6499_non127++;
}
'''
t = t.replace(needle, decl, 1)

entry = "    { s6497_seq++; s6497_first = 0; s6497_last = 0; s6497_x0 = s6497_x1 = s6497_z0 = s6497_z1 = 0; }\n"
assert t.count(entry) == 1
t = t.replace(entry, entry + "    s6499_stores = s6499_non127 = 0; s6499_first_addr = s6499_last_addr = 0; s6499_first_val = s6499_last_val = 0;\n", 1)

# Count actual stores, not rejected out-of-range attempts. These are the
# complete byte-store set in this generated function cluster.
sites = [
    ("else { MEM_B(0X0, ctx->r2) = ctx->r3;", "s6499_note(U32(ctx->r2), U32(ctx->r3));"),
    ("else { MEM_B(0X0, ctx->r3) = ctx->r6;", "s6499_note(U32(ctx->r3), U32(ctx->r6));"),
    ("else { MEM_B(0X0, ctx->r2) = ctx->r6;", "s6499_note(U32(ctx->r2), U32(ctx->r6));"),
    ("else { MEM_B(0X0, ctx->r21) = ctx->r2;", "s6499_note(U32(ctx->r21), U32(ctx->r2));"),
]
for old, add in sites:
    count = t.count(old)
    assert count >= 1, (old, count)
    t = t.replace(old, "else { " + add + " " + old[len("else { "):])

# Snapshot immediately after the binning function's last scan conversion and
# before its return; the stream consumer can compare this with its own sample.
ret = "    // 0x80042B48: jr          $ra\n"
assert t.count(ret) == 1
post = r'''    if (getenv("ROGUESQ_FORFACE_LOG")) {
      s6499_post_seq = s6497_seq;
      for (int i = 0; i < 24; i++) s6499_post_tbl[i] = (int8_t)MEM_B(0, (int64_t)(int32_t)(0x80130DB0 + i));
      static int np6499 = 0;
      if (np6499++ < 33) { fprintf(stderr, "[raspost] seq=%u stores=%u non127=%u first=%08x:%u last=%08x:%u tbl=", s6499_post_seq, s6499_stores, s6499_non127, s6499_first_addr, s6499_first_val, s6499_last_addr, s6499_last_val); for (int i = 0; i < 24; i++) fprintf(stderr, "%d,", s6499_post_tbl[i]); fprintf(stderr, "\n"); }
    } /* ''' + tag + " */\n"
t = t.replace(ret, post + ret, 1)

# Include the post-return identity and census in the existing stream row.
old = 'fprintf(stderr, "[streamdump] %s seq=%u ret=%u bounds=%d,%d,%d,%d stores=%08x..%08x w=%d,%d,%d,%d tbl=", emp ? "EMPTY" : "ok", s6497_seq, s6497_ret_seq, s6497_x0, s6497_x1, s6497_z0, s6497_z1, s6497_first, s6497_last, (int)MEM_W(0, (int64_t)(int32_t)0x80132DB0), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB4), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB8), (int)MEM_W(0, (int64_t)(int32_t)0x80132DBC));'
assert t.count(old) == 1
new = 'fprintf(stderr, "[streamdump] %s seq=%u ret=%u post=%u nstore=%u non127=%u bounds=%d,%d,%d,%d stores=%08x..%08x w=%d,%d,%d,%d tbl=", emp ? "EMPTY" : "ok", s6497_seq, s6497_ret_seq, s6499_post_seq, s6499_stores, s6499_non127, s6497_x0, s6497_x1, s6497_z0, s6497_z1, s6497_first, s6497_last, (int)MEM_W(0, (int64_t)(int32_t)0x80132DB0), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB4), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB8), (int)MEM_W(0, (int64_t)(int32_t)0x80132DBC));'
t = t.replace(old, new, 1)

p.write_text(t)
print("ok")
