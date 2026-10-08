#!/usr/bin/env python3
"""s4230: print allocator list state when 0x8008FD60 (lw $a0,0($v1) in fillSampleStreamRange) runs with v1==0. Idempotent."""
from pathlib import Path
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
MARK = "PATCH: s4230 fd60"
s = RF.read_text()
if MARK not in s:
    a = "    // 0x8008FD60: lw          $a0, 0x0($v1)\n"
    assert s.count(a) == 1
    p = ('    if (ctx->r3 == 0) { fprintf(stderr, "[s4230-FD60] v1=0 head=%08X tail=%08X pool=%08X t0=%016llX ra=%016llX sp=%016llX\\n", '
         '(uint32_t)MEM_W(-0X661C, S32(0X8015 << 16)), (uint32_t)MEM_W(-0X664C, S32(0X8015 << 16)), '
         '(uint32_t)MEM_W(-0X6634, S32(0X8015 << 16)), (unsigned long long)ctx->r8, (unsigned long long)ctx->r31, (unsigned long long)ctx->r29); } /* ' + MARK + ' */\n')
    RF.write_text(s.replace(a, p + a))
