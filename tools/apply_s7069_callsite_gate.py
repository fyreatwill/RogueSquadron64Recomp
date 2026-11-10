#!/usr/bin/env python3
"""s7069 host-selftime-audit: inline call-site gate for the two generated store/load diag hooks.
rs64_m5_lowfield_store (funcs_23.c, funcs_24.c; ~1300 sites) and rs64_s4307_synth_read (funcs_24.c; ~730 sites) are called
from generated code on every hooked guest store/load; since s7068 each returns at once when its logs are off, so the cost
left is the call itself. ~10 later patches (s4542, s4805, s4981-s4987, fixup_live_replay) key on the exact call-line text,
so this does NOT edit any call line. It adds, after the LAST extern declaration of each hook in a file, a same-name
function-like macro:
    #define rs64_m5_lowfield_store(w,p,a,v) (g_rs64_lowfield_hook ? (rs64_m5_lowfield_store)(w,p,a,v) : (void)0)
The parenthesised name inside does not re-expand. Arguments are pure (U32/ADD32/ctx regs, two getenv reads), so skipping
them changes no guest state. The host flags start at 1 and the hook clears its own flag on its first call when every log
gate is off (src/main/main.cpp, src/main/upstream_compat.cpp), so static-init order cannot matter.
ROGUESQ_DIAG_CALLSITE=0 (or ROGUESQ_DIAG_GATE=0) keeps the flags at 1 = old path, same binary.
Runs last in RS64_REPLAY; nothing may declare either hook after it. Idempotent.
Usage: apply_s7069_callsite_gate.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7069 callsite gate"
HOOKS = [
    ("extern void rs64_m5_lowfield_store(char, uint32_t, uint32_t, uint32_t);\n",
     "extern int g_rs64_lowfield_hook; /* %s */\n"
     "#define rs64_m5_lowfield_store(w, p, a, v) (g_rs64_lowfield_hook ? (rs64_m5_lowfield_store)(w, p, a, v) : (void)0)\n"),
    ("extern void rs64_s4307_synth_read(uint8_t*, uint32_t, uint32_t, uint32_t);\n",
     "extern int g_rs64_synthread_hook; /* %s */\n"
     "#define rs64_s4307_synth_read(r, p, a, v) (g_rs64_synthread_hook ? (rs64_s4307_synth_read)(r, p, a, v) : (void)0)\n"),
]
total = 0
for fn in sorted(D.glob("funcs_*.c")):
    t = fn.read_text(errors="surrogateescape")
    changed = False
    for decl, mac in HOOKS:
        name = decl.split("(")[0].split()[-1]
        if t.count(name + "(") == 0:
            continue
        if ("#define " + name + "(") in t:
            print(fn.name, name, "already applied"); continue
        i = t.rfind(decl)
        assert i >= 0, (fn.name, name, "call sites but no declaration")
        first_call = t.find(name + "(", 0)
        while first_call >= 0 and t.startswith(decl, first_call - len("extern void ")):
            first_call = t.find(name + "(", first_call + 1)
        assert first_call > i, (fn.name, name, "a call precedes the last declaration")
        j = i + len(decl)
        t = t[:j] + (mac % TAG) + t[j:]
        n = t.count(name + "(") - t.count(decl) - 2
        total += n; changed = True
        print(fn.name, name, "gated", n, "call sites")
    if changed:
        fn.write_text(t, errors="surrogateescape")
print("total gated", total)
