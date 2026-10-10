#!/usr/bin/env python3
"""s4562: M5 de-stub candidate. Retail order (s4562 static read): waitForMusyXAudioTaskDone drains the shutdown countdown, frees the
audio blocks (0x80179380, 0x801714D0, ...), and only AFTER musyxNoopStub returns does the guest clear gate 0x800A0F50. Retail's audio
thread never ran in that window (or lost the race harmlessly); the port's viRetraceHandlerThread keeps running musyxSynthFrame and walks
freed nodes. Fix: with env ROGUESQ_S4562_PAUSE=1, after the countdown spin finishes, set g_s4562_pause and wait for any in-flight
musyxSynthFrame to leave; clear it at wait-exit. musyxSynthFrame becomes a wrapper around musyxSynthFrame_s4562_impl.
Idempotent; apply after fixup_game_funcs.py and apply_s4561_synth_free_order.py."""
from pathlib import Path
MARK = "PATCH: s4562 pause"
f24 = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = f24.read_text()
if MARK not in s:
    a1 = 'RECOMP_FUNC void musyxSynthFrame(uint8_t* rdram, recomp_context* ctx) {'
    assert s.count(a1) == 1
    wrapper = ('/* ' + MARK + ' */\n'
      'volatile int g_s4562_pause = 0, g_s4562_in = 0; volatile unsigned g_s4562_skipped = 0;\n'
      'RECOMP_FUNC void musyxSynthFrame_s4562_impl(uint8_t* rdram, recomp_context* ctx);\n'
      'RECOMP_FUNC void musyxSynthFrame(uint8_t* rdram, recomp_context* ctx) {\n'
      '    if (__atomic_load_n(&g_s4562_pause, __ATOMIC_SEQ_CST)) { __atomic_add_fetch(&g_s4562_skipped, 1, __ATOMIC_SEQ_CST); return; }\n'
      '    __atomic_add_fetch(&g_s4562_in, 1, __ATOMIC_SEQ_CST);\n'
      '    if (__atomic_load_n(&g_s4562_pause, __ATOMIC_SEQ_CST)) { __atomic_sub_fetch(&g_s4562_in, 1, __ATOMIC_SEQ_CST); __atomic_add_fetch(&g_s4562_skipped, 1, __ATOMIC_SEQ_CST); return; }\n'
      '    musyxSynthFrame_s4562_impl(rdram, ctx);\n'
      '    __atomic_sub_fetch(&g_s4562_in, 1, __ATOMIC_SEQ_CST);\n'
      '}\n')
    s = s.replace(a1, wrapper + a1.replace('musyxSynthFrame(', 'musyxSynthFrame_s4562_impl('), 1)
    a2 = '    // 0x80091EE4: lui         $v0, 0x8015\n'
    assert s.count(a2) == 1
    pause = ('    { /* ' + MARK + ' */ static int s_on = -1; if (s_on < 0) { const char* e = getenv("ROGUESQ_S4562_PAUSE"); s_on = (e && e[0] == 49); }\n'
      '      if (s_on) { extern void yield_self_1ms(uint8_t* rdram); __atomic_store_n(&g_s4562_pause, 1, __ATOMIC_SEQ_CST);\n'
      '        int w = 0; while (__atomic_load_n(&g_s4562_in, __ATOMIC_SEQ_CST) > 0 && w < 2000) { yield_self_1ms(rdram); ++w; }\n'
      '        fprintf(stderr, "[s4562] pause set; waited %d ms for in-flight synth (in=%d skipped=%u)\\n", w, g_s4562_in, g_s4562_skipped); } }\n')
    s = s.replace(a2, pause + a2, 1)
    a3 = '    rs64_s2031_m5_gate_event(rdram, "wait-exit", "waitForMusyXAudioTaskDone",'
    assert s.count(a3) == 1
    clr = ('    if (__atomic_load_n(&g_s4562_pause, __ATOMIC_SEQ_CST)) { __atomic_store_n(&g_s4562_pause, 0, __ATOMIC_SEQ_CST); fprintf(stderr, "[s4562] pause cleared skipped=%u\\n", g_s4562_skipped); } /* ' + MARK + ' */\n')
    s = s.replace(a3, clr + a3, 1)
    f24.write_text(s)
print("ok")
