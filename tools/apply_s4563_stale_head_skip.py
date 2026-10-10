#!/usr/bin/env python3
"""s4563: ORIGIN: the audio list head 0x801499B0 is last written by the list-build store 0x8008F7C0 and is never cleared/rebuilt after the
guest's teardown frees the 900-byte node block 0x80179380 (s4562 [s4457-ptr]); the freed nodes are then overwritten by guest code at
pc 0x8001E2C0 (halfword store, e.g. node+0 -> 0x000094FC) while viRetraceHandlerThread keeps calling musyxSynthFrame, which walks the
stale head. Retail has no such caller after teardown (audio task is scheduled, not free-running). With ROGUESQ_S4563_SKIP=1 the
wrapper skips a frame while the head still points into the freed block (flag set at rs_free(0x80179380), cleared when head leaves the
range). Counters: [s4563] first-skip line + skipped count at exit-of-condition. Default off. Apply after apply_s4562_synth_pause.py."""
from pathlib import Path
MARK = "PATCH: s4563 stale head"
f0 = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c")
s = f0.read_text()
if MARK not in s:
    old = '              if (fp == 0x80179380u || fp == 0x801714D0u) { g_s4561_freed = 1;'
    assert s.count(old) == 1
    new = ('              if (fp == 0x80179380u) { extern volatile uint32_t g_s4563_blk_freed; g_s4563_blk_freed = 1; /* ' + MARK + ' */ }\n') + old
    s = s.replace(old, new, 1)
    f0.write_text(s)
f24 = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = f24.read_text()
if MARK not in s:
    a = '    if (__atomic_load_n(&g_s4562_pause, __ATOMIC_SEQ_CST)) { __atomic_add_fetch(&g_s4562_skipped, 1, __ATOMIC_SEQ_CST); return; }\n'
    assert s.count(a) == 1
    chk = ('    { /* ' + MARK + ' */ static int s_on = -1; static unsigned s_sk; if (s_on < 0) { const char* e = getenv("ROGUESQ_S4563_SKIP"); s_on = !(e && e[0] == 48); }\n'
      '      if (s_on && g_s4563_blk_freed) { uint32_t head = U32(MEM_W(0, S32(0x801499B0u)));\n'
      '        if (head >= 0x80179380u && head < 0x8017970Cu) { if (s_sk++ == 0) fprintf(stderr, "[s4563] skip synth: head=0x%08X in freed block\\n", head); return; }\n'
      '        fprintf(stderr, "[s4563] head left freed block (0x%08X); skipped=%u\\n", head, s_sk); g_s4563_blk_freed = 0; } }\n')
    s = s.replace(a, a + chk, 1)
    s = s.replace('volatile int g_s4562_pause = 0,', 'volatile uint32_t g_s4563_blk_freed = 0;\nvolatile int g_s4562_pause = 0,', 1)
    f24.write_text(s)
print("ok")
