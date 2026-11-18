#!/usr/bin/env python3
"""s7575: make the generated 32-bit div/divu total (no C UB on a zero divisor), MIPS-exact.
N64Recomp emits `lo = S32(S64(S32(a)) / S64(S32(b))); hi = ...%...;` BEFORE the compiler's `bne b,$zero; break 7` check.
A zero divisor is UB in C, so clang -O2 (RecompiledFuncs is built -O2) infers b != 0 from the dominating divide and deletes
the check: measured s7575, 31 data-dependent break-7 + 5 break-6 do_break calls absent from the -O2 IR, so a zero divisor
there continued silently with lo=garbage and no log could ever witness it (tools/s7575_break_census.py --ir).
RS64_DIV32/RS64_DIVU32 (include/rsp_dpc_macros.h) branch on b == 0 and return the R4300 results (div: lo = a<0 ? 1 : -1,
hi = a; divu: lo = 0xFFFFFFFF, hi = a), identical to the old code for every b != 0 (INT_MIN/-1 stays the S64 path).
Idempotent. Usage: apply_s7575_div_total.py [RecompiledFuncs dir]"""
import sys, re, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OP = r"(ctx->r\d+|0)"
SDIV = re.compile(r"lo = S32\(S64\(S32\(%s\)\) / S64\(S32\(%s\)\)\); hi = S32\(S64\(S32\(\1\)\) %% S64\(S32\(\2\)\)\);" % (OP, OP))
UDIV = re.compile(r"lo = S32\(U32\(%s\) / U32\(%s\)\); hi = S32\(U32\(\1\) %% U32\(\2\)\);" % (OP, OP))
ns = nu = 0
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text(errors="surrogateescape")
    t2, a = SDIV.subn(lambda m: "RS64_DIV32(%s, %s); /* PATCH: s7575 div total */" % (m.group(1), m.group(2)), t)
    t2, b = UDIV.subn(lambda m: "RS64_DIVU32(%s, %s); /* PATCH: s7575 div total */" % (m.group(1), m.group(2)), t2)
    if a or b: p.write_text(t2, errors="surrogateescape"); ns += a; nu += b
left = sum(len(re.findall(r"lo = S32\([^;]* / [^;]*\); hi = ", p.read_text(errors="replace"))) for p in D.glob("funcs_*.c"))
done = sum(p.read_text(errors="replace").count("PATCH: s7575 div total") for p in D.glob("funcs_*.c"))
print("[s7575-div] rewrote div=%d divu=%d total_patched=%d unrewritten_divides=%d" % (ns, nu, done, left))
sys.exit(1 if left or done == 0 else 0)
