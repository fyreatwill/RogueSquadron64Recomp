#!/usr/bin/env python3
"""s4466: after each [rs-malloc] line, record the ptr; when a 3964-byte block is returned, print the CURRENT heap-header
flags/size (ptr-0x10 half, ptr-0xC word) of every earlier recorded block that lies inside the returned range, plus the
returned block's own header. Discriminates allocator overlap (nested headers still say allocated) from an unlogged free
(nested headers say free). Env ROGUESQ_LOG_RS_MALLOC=1. Idempotent."""
from pathlib import Path
f = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c")
s = f.read_text()
MARK = "PATCH: s4466 hdrdump"
if MARK in s:
    raise SystemExit("already applied")
old = 'fprintf(stderr, "[rs-malloc] ptr=0x%08X size=%u flags=0x%X caller_ra=0x%08X\\n", U32(ctx->r2), s_rsmalloc_req_size, s_rsmalloc_flags, s_rsmalloc_caller_ra);\n'
assert s.count(old) == 1
new = old + (
 '            { static uint32_t s_hd_ptrs[65536]; static unsigned s_hd_n = 0; uint32_t rp = U32(ctx->r2); /* ' + MARK + ' */\n'
 '              fprintf(stderr, "[rs-hdr] ptr=0x%08X hflags=0x%04X hsize=0x%08X\\n", rp, (unsigned)(uint16_t)MEM_HU(0, S32(rp - 0x10u)), U32(MEM_W(4, S32(rp - 0x10u))));\n'
 '              if (rp && s_rsmalloc_req_size == 3964u) { for (unsigned i = 0; i < s_hd_n; i++) { uint32_t q = s_hd_ptrs[i]; if (q > rp && q < rp + 3964u) fprintf(stderr, "[rs-hdr-nested] outer=0x%08X inner=0x%08X hflags=0x%04X hsize=0x%08X idx=%u\\n", rp, q, (unsigned)(uint16_t)MEM_HU(0, S32(q - 0x10u)), U32(MEM_W(4, S32(q - 0x10u))), i); } }\n'
 '              if (rp && s_hd_n < 65536) s_hd_ptrs[s_hd_n++] = rp; }\n')
s = s.replace(old, new, 1)
f.write_text(s)
print("ok")
