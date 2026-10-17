#!/usr/bin/env python3
"""Mirror the s5229 block of fixup_game_funcs_vendored.py into the live
N64Recomp/RecompiledFuncs/funcs_24.c (not pristine-regenable)."""
import sys
V = "/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/fixup_game_funcs_vendored.py"
F = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c"
src = open(V).read()
a = src.index('if p.name == "funcs_24.c" and "PATCH: s5229 entry writer" not in text:')
b = src.index('report.append("funcs_24.c: s5229 entry writer patched")', a)
body = src[a:b].split("\n", 1)[1]
text = open(F).read()
if "PATCH: s5229 entry writer" in text:
    sys.exit("already applied")
ns = {"text": text, "sys": sys, "changed": False, "p": type("P", (), {"name": "funcs_24.c"})()}
exec("if True:\n" + body, ns)
open(F, "w").write(ns["text"])
print("applied s5229")
