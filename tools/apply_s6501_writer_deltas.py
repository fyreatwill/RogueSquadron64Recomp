"""s6501: attribute post-bin mutations to the four known byte writers."""
import pathlib

p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
tag = "PATCH: s6501 writer deltas"
if tag in t:
    print("already")
    raise SystemExit

needle = "static uint8_t s6500_tbl[64][24];\n"
assert t.count(needle) == 1
t = t.replace(needle, needle +
    "static uint32_t s6501_post_wcount[64][4], s6501_post_wlast[64][4]; /* " + tag + " */\n", 1)

old = "for (int i = 0; i < 24; i++) { uint8_t v = (uint8_t)MEM_B(0, (int64_t)(int32_t)(0x80130DB0 + i)); s6499_post_tbl[i] = (int8_t)v; s6500_tbl[ri][i] = v; } }\n"
assert t.count(old) == 1
new = "for (int i = 0; i < 24; i++) { uint8_t v = (uint8_t)MEM_B(0, (int64_t)(int32_t)(0x80130DB0 + i)); s6499_post_tbl[i] = (int8_t)v; s6500_tbl[ri][i] = v; } for (int i = 0; i < 4; i++) { s6501_post_wcount[ri][i] = s6500_wcount[i]; s6501_post_wlast[ri][i] = s6500_wlast[i]; } }\n"
t = t.replace(old, new, 1)

old = 'fprintf(stderr, " writers=%u:%u..%u,%u:%u..%u,%u:%u..%u,%u:%u..%u\\n", s6500_wcount[0], s6500_wfirst[0], s6500_wlast[0], s6500_wcount[1], s6500_wfirst[1], s6500_wlast[1], s6500_wcount[2], s6500_wfirst[2], s6500_wlast[2], s6500_wcount[3], s6500_wfirst[3], s6500_wlast[3]);'
assert t.count(old) == 1
new = 'fprintf(stderr, " writers=%u:%u..%u,%u:%u..%u,%u:%u..%u,%u:%u..%u delta=%u:%u,%u:%u,%u:%u,%u:%u last=%u,%u,%u,%u\\n", s6500_wcount[0], s6500_wfirst[0], s6500_wlast[0], s6500_wcount[1], s6500_wfirst[1], s6500_wlast[1], s6500_wcount[2], s6500_wfirst[2], s6500_wlast[2], s6500_wcount[3], s6500_wfirst[3], s6500_wlast[3], s6500_wcount[0] - s6501_post_wcount[ri][0], s6500_wcount[1] - s6501_post_wcount[ri][1], s6500_wcount[2] - s6501_post_wcount[ri][2], s6500_wcount[3] - s6501_post_wcount[ri][3], s6500_wlast[0] - s6501_post_wlast[ri][0], s6500_wlast[1] - s6501_post_wlast[ri][1], s6500_wlast[2] - s6501_post_wlast[ri][2], s6500_wlast[3] - s6501_post_wlast[ri][3], s6500_wlast[0], s6500_wlast[1], s6500_wlast[2], s6500_wlast[3]);'
t = t.replace(old, new, 1)
p.write_text(t)
print("ok")
