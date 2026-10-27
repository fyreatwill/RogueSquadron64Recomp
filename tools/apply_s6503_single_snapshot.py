"""s6503: replace the aliased ring join with one guest-thread-labelled snapshot."""
import pathlib

p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
tag = "PATCH: s6503 single snapshot"
if tag in t:
    print("already")
    raise SystemExit

t = t.replace("static _Thread_local ", "static ", 10)
t = t.replace("static uint32_t s6501_post_wcount[64][4], s6501_post_wlast[64][4];", "static uint32_t s6501_post_wcount[4], s6501_post_wlast[4]; static int s6501_post_tid; /* " + tag + " */")
t = t.replace("s6501_post_wcount[ri][i] = s6500_wcount[i]; s6501_post_wlast[ri][i] = s6500_wlast[i];", "s6501_post_wcount[i] = s6500_wcount[i]; s6501_post_wlast[i] = s6500_wlast[i];")
t = t.replace("s6501_post_wcount[ri][0]", "s6501_post_wcount[0]").replace("s6501_post_wcount[ri][1]", "s6501_post_wcount[1]").replace("s6501_post_wcount[ri][2]", "s6501_post_wcount[2]").replace("s6501_post_wcount[ri][3]", "s6501_post_wcount[3]")
t = t.replace("s6501_post_wlast[ri][0]", "s6501_post_wlast[0]").replace("s6501_post_wlast[ri][1]", "s6501_post_wlast[1]").replace("s6501_post_wlast[ri][2]", "s6501_post_wlast[2]").replace("s6501_post_wlast[ri][3]", "s6501_post_wlast[3]")
t = t.replace("for (int i = 0; i < 4; i++) { s6501_post_wcount[i] = s6500_wcount[i]; s6501_post_wlast[i] = s6500_wlast[i]; } }", "for (int i = 0; i < 4; i++) { s6501_post_wcount[i] = s6500_wcount[i]; s6501_post_wlast[i] = s6500_wlast[i]; } s6501_post_tid = rogue_current_thread_id(rdram); }")
t = t.replace("fprintf(stderr, \"[streamdump]", "fprintf(stderr, \"[streamdump]")
t = t.replace("writers=%u:%u..%u,%u:%u..%u,%u:%u..%u,%u:%u..%u delta=", "posttid=%d streamtid=%d writers=%u:%u..%u,%u:%u..%u,%u:%u..%u,%u:%u..%u delta=", 1)
t = t.replace("s6500_wcount[0], s6500_wfirst[0]", "s6501_post_tid, rogue_current_thread_id(rdram), s6500_wcount[0], s6500_wfirst[0]", 1)
t = t.replace('#include "funcs.h"\n', '#include "funcs.h"\nextern int rogue_current_thread_id(uint8_t* rdram);\n', 1)
p.write_text(t)
print("ok")
