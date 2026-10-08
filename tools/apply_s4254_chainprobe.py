#!/usr/bin/env python3
"""s4254: at fillSampleStreamRange entry, for n>=15000 log head node words 0..3 and the word0-chain length (cap 400)
every 100 calls, and on every call whose chain length differs from the previous one. Idempotent. Run after apply_s4234_entryprobe.py."""
from pathlib import Path
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
MARK = "PATCH: s4254 chain"
s = RF.read_text()
if MARK not in s:
    a = '    rs64_s2084_fill_range_edge("entry", 0x8008FAACu, ctx);'
    assert s.count(a) == 1
    p = ('    { static unsigned n = 0, last = 0xFFFFFFFFu; ++n; if (n >= 15000) { uint32_t h = (uint32_t)MEM_W(-0X661C, S32(0X8015 << 16)); '
         'uint32_t c = h, len = 0; while (c >= 0x80000000u && c < 0x80800000u && len < 400) { c = (uint32_t)MEM_W(0, (int32_t)c); ++len; } '
         'int ok = (h >= 0x80000000u && h < 0x80800000u); '
         'if (n % 100 == 0 || len != last) { fprintf(stderr, "[s4254-CHAIN] n=%u head=%08X len=%u end=%08X w0..3=%08X %08X %08X %08X\\n", n, h, len, c, '
         'ok ? (uint32_t)MEM_W(0, (int32_t)h) : 0, ok ? (uint32_t)MEM_W(4, (int32_t)h) : 0, '
         'ok ? (uint32_t)MEM_W(8, (int32_t)h) : 0, ok ? (uint32_t)MEM_W(12, (int32_t)h) : 0); last = len; } } } /* ' + MARK + ' */\n')
    RF.write_text(s.replace(a, p + a, 1))
print("ok")
