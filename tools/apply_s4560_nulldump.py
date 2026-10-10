#!/usr/bin/env python3
"""s4560: when rs_malloc returns NULL for a flags&4 request, dump the guest heap-region globals (0x8010FEE8..0x8010FF1C)
and walk the header chain of the flags=4 region (head word at 0x8010FEFC; next = hdr + size + 0x10), printing
flags/size/hdr for the first 40 steps and every free (flags&1) block, with free/used totals and the largest free block.
Positive control: the same dump is printed for the first 2 SUCCESSFUL flags=4 mallocs ([rs-nulldump-ctl]).
Env ROGUESQ_LOG_RS_MALLOC=1. Idempotent."""
from pathlib import Path
f = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c")
s = f.read_text()
MARK = "PATCH: s4560 nulldump"
if MARK in s:
    raise SystemExit("already applied")
anchor = '              if (rp && s_hd_n < 65536) s_hd_ptrs[s_hd_n++] = rp; }\n'
assert s.count(anchor) == 1
new = anchor + (
 '            { static int s_nd_ctl = 0; /* ' + MARK + ' */\n'
 '              if ((s_rsmalloc_flags & 4u) && ((U32(ctx->r2) == 0u) || s_nd_ctl < 2)) {\n'
 '                const char* tag = U32(ctx->r2) == 0u ? "rs-nulldump" : "rs-nulldump-ctl"; if (U32(ctx->r2) != 0u) s_nd_ctl++;\n'
 '                fprintf(stderr, "[%s] req=%u globals:", tag, s_rsmalloc_req_size);\n'
 '                for (uint32_t g = 0x8010FEE8u; g <= 0x8010FF1Cu; g += 4u) fprintf(stderr, " %08X=%08X", g, U32(MEM_W(0, S32(g))));\n'
 '                fprintf(stderr, "\\n");\n'
 '                uint32_t h = U32(MEM_W(0, S32(0x8010FEFCu))); uint64_t freeb = 0, usedb = 0; uint32_t bigfree = 0; unsigned steps = 0;\n'
 '                while (h >= 0x80000000u && h < 0x80800000u && steps < 400u) {\n'
 '                  uint16_t hf = (uint16_t)MEM_HU(0, S32(h)); uint32_t hs = U32(MEM_W(4, S32(h)));\n'
 '                  if (hf & 1u) { freeb += hs; if (hs > bigfree) bigfree = hs; } else usedb += hs;\n'
 '                  if (steps < 40u || (hf & 1u)) fprintf(stderr, "[%s] step=%u hdr=0x%08X flags=0x%04X size=0x%X\\n", tag, steps, h, hf, hs);\n'
 '                  if (hs == 0u || hs > 0x800000u) { fprintf(stderr, "[%s] chain-stop bad size at 0x%08X\\n", tag, h); break; }\n'
 '                  h = h + hs + 0x10u; steps++;\n'
 '                }\n'
 '                fprintf(stderr, "[%s] end h=0x%08X steps=%u free=%llu used=%llu bigfree=%u\\n", tag, h, steps, (unsigned long long)freeb, (unsigned long long)usedb, bigfree);\n'
 '              } }\n')
s = s.replace(anchor, new, 1)
f.write_text(s)
print("ok")

# part 3 (applied by hand to funcs_0.c in s4560, re-apply after regen): before the 'req=%u globals' fprintf insert
#   static unsigned s_nd_nulls; count NULLs; print "[tag] n=.. req=.. gateA89A=<byte 0x8011A89A> gate44=<[*(0x8010FCB0)+0x44]> cb=.. vi=.." (cap 40).
# part 2: the s4466 [rs-hdr] print dereferenced ptr-0x10 for a NULL result (host SIGBUS at 0x7FFFFFF0); guard it.
s = f.read_text()
old = 'fprintf(stderr, "[rs-hdr] ptr=0x%08X hflags=0x%04X hsize=0x%08X\\n", rp, (unsigned)(uint16_t)MEM_HU(0, S32(rp - 0x10u)), U32(MEM_W(4, S32(rp - 0x10u))));'
if "PATCH: s4560 null guard" not in s and s.count(old) == 1:
    f.write_text(s.replace(old, 'if (rp) ' + old + ' /* PATCH: s4560 null guard */', 1))
    print("guard ok")
