"""s6502: isolate the s6497-s6501 writer probe per guest thread."""
import pathlib

p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
tag = "PATCH: s6502 thread-local writer probe"
if tag in t:
    print("already")
    raise SystemExit

old = "static uint32_t s6497_seq, s6497_ret_seq, s6497_first, s6497_last; static int32_t s6497_x0, s6497_x1, s6497_z0, s6497_z1; /* PATCH: s6497 rasterizerbounds */"
assert t.count(old) == 1
t = t.replace(old, "static _Thread_local uint32_t s6497_seq, s6497_ret_seq, s6497_first, s6497_last; static _Thread_local int32_t s6497_x0, s6497_x1, s6497_z0, s6497_z1; /* PATCH: s6497 rasterizerbounds */", 1)

for old, new in (
    ("static uint32_t s6499_stores, s6499_non127, s6499_first_addr, s6499_last_addr;", "static _Thread_local uint32_t s6499_stores, s6499_non127, s6499_first_addr, s6499_last_addr;"),
    ("static uint32_t s6499_first_val, s6499_last_val, s6499_post_seq;", "static _Thread_local uint32_t s6499_first_val, s6499_last_val, s6499_post_seq;"),
    ("static int8_t s6499_post_tbl[24];", "static _Thread_local int8_t s6499_post_tbl[24];"),
    ("static uint32_t s6500_seq[64], s6500_stores[64], s6500_non127[64];", "static _Thread_local uint32_t s6500_seq[64], s6500_stores[64], s6500_non127[64];"),
    ("static uint8_t s6500_tbl[64][24];", "static _Thread_local uint8_t s6500_tbl[64][24];"),
    ("static uint32_t s6501_post_wcount[64][4], s6501_post_wlast[64][4];", "static _Thread_local uint32_t s6501_post_wcount[64][4], s6501_post_wlast[64][4];"),
    ("static uint32_t s6500_wcount[4], s6500_wfirst[4], s6500_wlast[4];", "static _Thread_local uint32_t s6500_wcount[4], s6500_wfirst[4], s6500_wlast[4];"),
):
    assert t.count(old) == 1, old
    t = t.replace(old, new, 1)

t = t.replace("/* PATCH: s6501 writer deltas */", "/* PATCH: s6501 writer deltas; " + tag + " */", 1)
p.write_text(t)
print("ok")
