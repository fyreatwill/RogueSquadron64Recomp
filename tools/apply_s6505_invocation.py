"""s6505: key the EBC writer census to each stream invocation interval."""
import pathlib

p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
tag = "PATCH: s6505 invocation join"
if tag in t:
    print("already")
    raise SystemExit

needle = "static uint32_t s6500_wcount[4], s6500_wfirst[4], s6500_wlast[4]; /* PATCH: s6500 postring */\n"
assert t.count(needle) == 1
t = t.replace(needle, needle +
    "static uint32_t s6505_invocation_key; /* " + tag + " */\n", 1)

needle = "RECOMP_FUNC void streamTerrainGridCellsByDistance(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n"
assert t.count(needle) == 1
t = t.replace(needle, needle +
    "    uint32_t s6505_key = 0, s6505_start[4] = {0, 0, 0, 0};\n"
    "    if (getenv(\"ROGUESQ_FORFACE_LOG\")) {\n"
    "        s6505_key = __atomic_add_fetch(&s6505_invocation_key, 1u, __ATOMIC_RELAXED);\n"
    "        for (int i = 0; i < 4; i++) s6505_start[i] = s6500_wcount[i];\n"
    "    }\n", 1)

old = ('fprintf(stderr, "[postring] seq=%u ring=%u stores=%u non127=%u tbl=", s6497_seq, s6500_seq[ri], s6500_stores[ri], s6500_non127[ri]);')
assert t.count(old) == 1
new = ('fprintf(stderr, "[postring] key=%u seq=%u ring=%u stores=%u non127=%u tbl=", s6505_key, s6497_seq, s6500_seq[ri], s6500_stores[ri], s6500_non127[ri]);')
t = t.replace(old, new, 1)

old = ('fprintf(stderr, " posttid=%d streamtid=%d writers=%u:%u..%u,%u:%u..%u,%u:%u..%u,%u:%u..%u delta=%u:%u,%u:%u,%u:%u,%u:%u last=%u,%u,%u,%u\\n", s6501_post_tid, rogue_current_thread_id(rdram), s6500_wcount[0], s6500_wfirst[0], s6500_wlast[0], s6500_wcount[1], s6500_wfirst[1], s6500_wlast[1], s6500_wcount[2], s6500_wfirst[2], s6500_wlast[2], s6500_wcount[3], s6500_wfirst[3], s6500_wlast[3], s6500_wcount[0] - s6501_post_wcount[0], s6500_wcount[1] - s6501_post_wcount[1], s6500_wcount[2] - s6501_post_wcount[2], s6500_wcount[3] - s6501_post_wcount[3], s6500_wlast[0] - s6501_post_wlast[0], s6500_wlast[1] - s6501_post_wlast[1], s6500_wlast[2] - s6501_post_wlast[2], s6500_wlast[3] - s6501_post_wlast[3], s6500_wlast[0], s6500_wlast[1], s6500_wlast[2], s6500_wlast[3]);')
assert t.count(old) == 1
new = ('fprintf(stderr, " start=%u,%u,%u,%u end=%u,%u,%u,%u delta=%u,%u,%u,%u last=%u,%u,%u,%u\\n", s6505_start[0], s6505_start[1], s6505_start[2], s6505_start[3], s6500_wcount[0], s6500_wcount[1], s6500_wcount[2], s6500_wcount[3], s6500_wcount[0] - s6505_start[0], s6500_wcount[1] - s6505_start[1], s6500_wcount[2] - s6505_start[2], s6500_wcount[3] - s6505_start[3], s6500_wlast[0], s6500_wlast[1], s6500_wlast[2], s6500_wlast[3]);')
t = t.replace(old, new, 1)

p.write_text(t)
print("ok")
