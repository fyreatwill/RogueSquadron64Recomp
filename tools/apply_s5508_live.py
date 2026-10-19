#!/usr/bin/env python3
"""Apply the s5508 initMission/manifest patches (defined in
fixup_game_funcs_vendored.py) to the LIVE RecompiledFuncs, mirroring what the
fixup does on regen. Idempotent (guarded by the PATCH sentinel)."""
import textwrap

SRC = "/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/fixup_game_funcs_vendored.py"
BASE = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/"
src = open(SRC).read()
i = src.index('    if p.name == "funcs_42.c" and "PATCH: s5508')
j = src.index('    if p.name == "funcs_27.c" and "PATCH: s3305 cinematic')
blk = src[i:j]
k1 = blk.index('    if p.name == "funcs_1.c"')
subs = {"funcs_42.c": blk[:k1], "funcs_1.c": blk[k1:]}
for name, sub in subs.items():
    class P:
        pass
    p = P()
    p.name = name
    text = open(BASE + name).read()
    report = []
    ns = {"p": p, "text": text, "changed": False, "report": report}
    exec(textwrap.dedent(sub), ns)
    open(BASE + name, "w").write(ns["text"])
    print(name, report)
