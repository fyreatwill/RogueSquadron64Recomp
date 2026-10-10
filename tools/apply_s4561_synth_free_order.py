#!/usr/bin/env python3
"""s4561: order musyxSynthFrame entries vs the guest's frees of audio-list blocks. At rs_free(0x80179380|0x801714D0) print
gate 0x800A0F50, mode word 0x800375A4, synth-entry count n and the last 8 entry stamps; after the first such free, log every
musyxSynthFrame entry (cap 40) with gate/mode/n and whether the shutdown countdown is zero. Env ROGUESQ_LOG_RS_FREE=1.
Positive control: [s4561-ctl] prints the first 3 synth entries unconditionally. Idempotent; re-apply after regen."""
from pathlib import Path
MARK = "PATCH: s4561 order"
f0 = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c")
s = f0.read_text()
if MARK not in s:
    old = 'backtrace_symbols_fd(bt, bn, 2); } /* PATCH: s4300 rsfree bt */\n'
    assert s.count(old) == 1
    new = old + (
     '            { extern volatile uint32_t g_s4561_synth_n, g_s4561_freed; uint32_t fp = U32(ctx->r4); /* ' + MARK + ' */\n'
     '              if (fp == 0x80179380u || fp == 0x801714D0u) { g_s4561_freed = 1;\n'
     '                fprintf(stderr, "[s4561-free] ptr=0x%08X gate=%u mode=0x%08X synth_n=%u\\n", fp, U32(MEM_W(0, S32(0x800A0F50u))), U32(MEM_W(0, S32(0x800375A4u))), (unsigned)g_s4561_synth_n); } }\n')
    s = s.replace(old, new, 1)
    f0.write_text(s)
f24 = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = f24.read_text()
if MARK not in s:
    anchor = '/* PATCH: musyxSynthFrame parent entry 0x8009123C */\n'
    assert s.count(anchor) == 1
    new = anchor + (
     '    { /* ' + MARK + ' */ unsigned n = ++g_s4561_synth_n; static unsigned s_after;\n'
     '      if (n <= 3) fprintf(stderr, "[s4561-ctl] synth entry n=%u gate=%u\\n", n, U32(MEM_W(0, S32(0x800A0F50u))));\n'
     '      if (g_s4561_freed && s_after < 40) { s_after++; fprintf(stderr, "[s4561-synth] after-free #%u n=%u gate=%u mode=0x%08X\\n", s_after, n, U32(MEM_W(0, S32(0x800A0F50u))), U32(MEM_W(0, S32(0x800375A4u)))); } }\n')
    s = s.replace(anchor, new, 1)
    s = s.replace('RECOMP_FUNC void musyxSynthFrame(', 'volatile uint32_t g_s4561_synth_n = 0, g_s4561_freed = 0;\nRECOMP_FUNC void musyxSynthFrame(', 1)
    f24.write_text(s)
print("ok")
