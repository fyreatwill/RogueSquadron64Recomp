#!/usr/bin/env python3
"""s7844 G3 det sweep: one-shot override of runInMissionFrame's snapped frame dt, so a retail oracle lag tick can be
replayed in the port as a same-run causal lever. Site 0x800FA7D0 (L_800FA7D0: after the 1/60 snap + clamp + demo
timestep, f20 = the dt stored at sp+0x88 and handed to the whole mission frame). Env ROGUESQ_S7844_DT_AT=<tick>:<hex>[,..] (up to 32)
(tick = 0-based count of passes through this site; hex = float32 bits): on that pass f20 is replaced. Banner
`[dt7844] armed` + one `[dt7844] tick=N f20 OLD -> NEW` line per override (positive control: the line must appear).
Retail twin: rs64_oracle --watch-pc 0x800FA738,0x800FA7D0 + RS64_ORACLE_FPR=..,20 (tick k = k-th 0x800FA7D0 hit;
scratch/s7844/snap.py). Unset = untouched. Idempotent; in fixup_game_funcs_vendored.py's RS64_REPLAY."""
import pathlib, sys
BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7844 dt_at"
ANCHOR = "L_800FA7D0:\n    // 0x800FA7D0: jal         0x80002FF4\n"
BODY = ('    { /* ' + MARK + ' */ static int n7844 = -1; static long long t7844[32]; static uint32_t v7844[32]; static long long k7844 = 0;\n'
        '      if (n7844 < 0) { n7844 = 0; const char* e = getenv("ROGUESQ_S7844_DT_AT");\n'
        '        while (e && *e && n7844 < 32) { char* q; long long t = strtoll(e, &q, 10); if (*q != \':\') break; uint32_t v = (uint32_t)strtoul(q + 1, &q, 16);\n'
        '          t7844[n7844] = t; v7844[n7844] = v; n7844++; e = (*q == \',\') ? q + 1 : NULL; }\n'
        '        if (n7844) fprintf(stderr, "[dt7844] armed %d override(s)\\n", n7844); }\n'
        '      for (int i = 0; i < n7844; i++) if (t7844[i] == k7844) { fprintf(stderr, "[dt7844] tick=%lld f20 %08X -> %08X\\n", k7844, ctx->f20.u32l, v7844[i]); ctx->f20.u32l = v7844[i]; }\n'
        '      k7844++; }\n')
n = 0
for p in sorted(BASE.glob("funcs_*.c")):
    s = p.read_text()
    if MARK in s:
        print("s7844 dt_at: already applied", p.name); sys.exit(0)
    if ANCHOR not in s:
        continue
    assert s.count(ANCHOR) == 1, p
    s = s.replace(ANCHOR, ANCHOR.split("\n")[0] + "\n" + BODY + ANCHOR.split("\n", 1)[1], 1)
    p.write_text(s); n += 1
print("s7844 dt_at: %d file(s)" % n)
assert n == 1
