"""s7489 class EN: give the s5798 store hook (RS64_S5798_ST -> rs64_s5798_st -> rs64_s7475_store) back to the guest stores that
earlier patches rewrote without it, so the s7475 slack canary / s7480 freed-block UAF store watch sees every live store form.

tools/s7489_store_path_census.py (this regen) found 25648/25649 sw, 5378/5391 sb, 4593/4603 sh hooked, every swc1/sdc1/sd and (s7488)
swl/swr hooked. The live unhooked sites are exactly the ones whose store statement another patch replaced:
  - s5520 [b40w] logger (apply_s5520_b40log.py) rewrote 6 `sb ..., 0xB40(base)` sites (9 texts incl. delay-slot copies)
  - s4984 atomic voice pair (apply_s4984_atomic_voice_pair.py) rewrote `sw $v0,-0x6908($at)` 0x8008F0EC and `sh $s0,-0x6900($at)` 0x8008F0CC
The rest are not live stores: data_gap_80024A0C ($zero-based sb/sh into KUSEG 0x153.., a data region decoded as code), swc2/sc/scd/sdc2
(do_break traps), cache (no-op). This script appends `RS64_S5798_ST(pc, off, ctx->rN, w);` after the replacement statement of every
store whose text up to the next `// 0x` comment has no hook, skipping data_gap_ functions and do_break bodies. Measurement only (the
macro is gated by g_rs64_store_diag). Idempotent (marker). Registered in fixup_game_funcs_vendored.py after apply_s7488_ustorewatch.py."""
import re, sys
from pathlib import Path
D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "/* PATCH: s7489 storegap */"
REGS = ["zero","at","v0","v1","a0","a1","a2","a3","t0","t1","t2","t3","t4","t5","t6","t7","s0","s1","s2","s3","s4","s5","s6","s7",
        "t8","t9","k0","k1","gp","sp","fp","ra"]
W = {"sb": 1, "sh": 2, "sw": 4, "sd": 8}
CMT = re.compile(r"^(\s*)// 0x([0-9A-Fa-f]{8}): (sb|sh|sw|sd)\s+\$\w+,\s*(-?0x[0-9A-Fa-f]+|-?\d+)\(\$(\w+)\)")
ANY = re.compile(r"^\s*// 0x[0-9A-Fa-f]{8}: ")
FN = re.compile(r"^RECOMP_FUNC void (\w+)\(")
STMT = re.compile(r"MEM_[BHWD]\(|__atomic_store_n\(")
n = 0; files = 0
for p in sorted(D.glob("funcs_*.c")):
    L = p.read_text().split("\n"); out = []; fn = ""; i = 0; ch = 0
    while i < len(L):
        m = FN.match(L[i])
        if m: fn = m.group(1)
        c = CMT.match(L[i])
        if not c or fn.startswith("data_gap_") or c.group(5) not in REGS:
            out.append(L[i]); i += 1; continue
        j = i + 1
        while j < len(L) and not ANY.match(L[j]) and not L[j].startswith("}"): j += 1
        body = L[i + 1:j]; txt = "\n".join(body)
        if "RS64_S5798_ST(" in txt or MARK in txt or "do_break(" in txt or not any(STMT.search(b) for b in body):
            out.extend(L[i:j]); i = j; continue
        k = max(x for x, b in enumerate(body) if STMT.search(b))
        pc, op, off, reg = c.group(2).upper(), c.group(3), c.group(4), c.group(5)
        offv = int(off, 0); offs = ("-0X%X" % -offv) if offv < 0 else ("0X%X" % offv)
        base = "0" if reg == "zero" else "ctx->r%d" % REGS.index(reg)
        ind = re.match(r"^(\s*)", body[k]).group(1)
        body = body[:k + 1] + [f"{ind}RS64_S5798_ST(0x{pc}u, {offs}, {base}, {W[op]}); {MARK}"] + body[k + 1:]
        out.append(L[i]); out.extend(body); n += 1; ch = 1; i = j
    if ch: p.write_text("\n".join(out)); files += 1
print("s7489 storegap: hooked", n, "store texts in", files, "files")
