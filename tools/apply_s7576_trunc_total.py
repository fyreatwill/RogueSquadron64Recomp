#!/usr/bin/env python3
"""s7576: make the generated trunc.w.s / trunc.w.d total (no C UB on NaN / out-of-range) and witness every
out-of-range conversion. recomp.h emits `ctx->fD.u32l = TRUNC_W_S(ctx->fS.fl);` = a bare (int32_t) cast, which is
UB in C for NaN or |v| >= 2^31; clang -O2 deletes code on that basis (tools/s7576_trunc_census.py control). The
rewrite calls RS64_TRUNC_W_S/D(v, pc) (include/rsp_dpc_macros.h): arm64 fcvtzs semantics (what the bare cast compiled
to), plus a cold report of the trunc's guest PC when the value is unrepresentable (retail R4300 traps there).
Idempotent. Usage: apply_s7576_trunc_total.py [RecompiledFuncs dir]"""
import sys, re, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
CMT = re.compile(r"^\s*// (0x[0-9A-F]{8}): trunc\.w\.([sd])\b")
SITE = re.compile(r"TRUNC_W_([SD])\((ctx->f\d+\.(?:fl|d))\);")
n = 0; bad = []
for p in sorted(D.glob("funcs_*.c")):
    lines = p.read_text(errors="surrogateescape").split("\n"); pc = None; ch = 0
    for i, ln in enumerate(lines):
        m = CMT.match(ln)
        if m: pc = (m.group(1), m.group(2).upper()); continue
        if "TRUNC_W_" in ln and "RS64_TRUNC_W_" not in ln:
            s = SITE.search(ln)
            if not s or not pc or pc[1] != s.group(1): bad.append("%s:%d" % (p.name, i + 1)); continue
            lines[i] = ln.replace(s.group(0), "RS64_TRUNC_W_%s(%s, %su); /* PATCH: s7576 trunc total */" % (s.group(1), s.group(2), pc[0]))
            ch += 1; pc = None
    if ch: p.write_text("\n".join(lines), errors="surrogateescape"); n += ch
done = sum(p.read_text(errors="replace").count("PATCH: s7576 trunc total") for p in D.glob("funcs_*.c"))
left = sum(len(re.findall(r"(?<!RS64_)TRUNC_W_[SD]\(", p.read_text(errors="replace"))) for p in D.glob("funcs_*.c"))
print("[s7576-trunc] rewrote=%d total_patched=%d unrewritten=%d unanchored=%s" % (n, done, left, bad[:5]))
sys.exit(1 if left or bad or done == 0 else 0)
