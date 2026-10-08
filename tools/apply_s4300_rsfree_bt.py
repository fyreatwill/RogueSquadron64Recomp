#!/usr/bin/env python3
"""s4300: add a host backtrace (backtrace_symbols_fd, 10 frames) + g_rs64_last_guest_pc to the [rs-free] log so the
freeing guest function is named (ctx->r31 reads 0 at rs_free entry). Env ROGUESQ_LOG_RS_FREE=1. Idempotent."""
from pathlib import Path
f = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c")
s = f.read_text()
MARK = "PATCH: s4300 rsfree bt"
if MARK in s:
    raise SystemExit("already applied")
old = 'fprintf(stderr, "[rs-free] ptr=0x%08X caller_ra=0x%08X\\n", U32(ctx->r4), U32(ctx->r31));\n'
assert s.count(old) == 1
new = old + ('            { extern volatile uint32_t g_rs64_last_guest_pc; void* bt[12]; int bn = backtrace(bt, 12); '
             'fprintf(stderr, "[rs-free-bt] ptr=0x%08X guest_pc=0x%08X\\n", U32(ctx->r4), (unsigned)g_rs64_last_guest_pc); '
             'backtrace_symbols_fd(bt, bn, 2); } /* ' + MARK + ' */\n')
s = s.replace(old, new, 1)
s = s.replace('#include "recomp.h"\n', '#include "recomp.h"\n#include <execinfo.h>\n', 1)
f.write_text(s)
print("ok")
