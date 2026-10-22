"""s5907: attribute RET to the object whose fine test last returned a hit (rs5907_hitobj) vs last in-sphere obj (sinobj).
Adds per-class hret counter + agree/nohit/disagree totals. Idempotent; patches funcs_16.c and apply_s5835_sphere_probe.py (run after apply_s5906_fine.py)."""
import pathlib
P = [pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_16.c"),
     pathlib.Path(__file__).with_name("apply_s5835_sphere_probe.py")]
subs = [
 ("unsigned fc, fr; float r2lo, r2hi; } rs5904_T[32]; float rs5906_r2;", "unsigned fc, fr, hret; float r2lo, r2hi; } rs5904_T[32]; float rs5906_r2; uint32_t rs5907_hitobj; unsigned rs5907_agree, rs5907_nohit, rs5907_dis; /* PATCH: s5907 */"),
 ("else if (kind == 3) rs5904_T[z].fr++;", "else if (kind == 3) { rs5904_T[z].fr++; rs5907_hitobj = obj; } else if (kind == 4) rs5904_T[z].hret++;"),
 ("fine=%u/%u r2=", "fine=%u/%u hret=%u r2="),
 ("rs5904_T[z].fc, rs5904_T[z].fr, rs5904_T[z].r2lo", "rs5904_T[z].fc, rs5904_T[z].fr, rs5904_T[z].hret, rs5904_T[z].r2lo"),
 ('fprintf(stderr, "\\n"); }\n', 'fprintf(stderr, "\\n[s5907] RET attribution: agree=%u nohit=%u disagree=%u\\n", rs5907_agree, rs5907_nohit, rs5907_dis); }\n'),
 ("rs5856_cin = 0; rs5856_sinobj = 0;", "rs5856_cin = 0; rs5856_sinobj = 0; rs5907_hitobj = 0;"),
 ("rs5904_tally(rdram, rs5856_sinobj, 1);", "rs5904_tally(rdram, rs5856_sinobj, 1); if (!rs5907_hitobj) rs5907_nohit++; else { rs5904_tally(rdram, rs5907_hitobj, 4); if (rs5907_hitobj == rs5856_sinobj) rs5907_agree++; else rs5907_dis++; }"),
 ("extern float rs5906_r2;", "extern float rs5906_r2; extern uint32_t rs5907_hitobj; extern unsigned rs5907_agree, rs5907_nohit, rs5907_dis;"),
]
for p in P:
    t = p.read_text()
    if "PATCH: s5907" in t: print(p, "already"); continue
    for a, b in subs:
        print(p.name, t.count(a), a[:40])
        t = t.replace(a, b)
    p.write_text(t)
