#!/usr/bin/env python3
"""s4234: fillSampleStreamRange entry row [s4234-ENTRY] n/head/tail/pool/ra/sp, interleaved on stderr with the
[s4222-S] allocator-list store rows (apply_s4230_listwatch.py), so one log orders calls against the init/clear stores.
Prints the first 30 entries plus every entry with head==0 or ra==0. Idempotent."""
from pathlib import Path
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
MARK = "PATCH: s4234 entry"
s = RF.read_text()
if MARK not in s:
    a = '    rs64_s2084_fill_range_edge("entry", 0x8008FAACu, ctx);'
    assert s.count(a) == 1
    p = ('    { static unsigned s4234_n = 0; uint32_t h = (uint32_t)MEM_W(-0X661C, S32(0X8015 << 16)); ++s4234_n; '
         'if (s4234_n <= 30 || h == 0 || ctx->r31 == 0) fprintf(stderr, "[s4234-ENTRY] n=%u head=%08X tail=%08X pool=%08X ra=%016llX sp=%016llX a0=%016llX\\n", s4234_n, h, '
         '(uint32_t)MEM_W(-0X664C, S32(0X8015 << 16)), (uint32_t)MEM_W(-0X6634, S32(0X8015 << 16)), '
         '(unsigned long long)ctx->r31, (unsigned long long)ctx->r29, (unsigned long long)ctx->r4); } /* ' + MARK + ' */\n')
    RF.write_text(s.replace(a, p + a, 1))
print("ok")
