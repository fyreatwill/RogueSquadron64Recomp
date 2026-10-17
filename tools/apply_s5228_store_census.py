#!/usr/bin/env python3
"""Mirror the s5228 store-census block of fixup_game_funcs_vendored.py into the
live N64Recomp/RecompiledFuncs/funcs_24.c (the live tree is not pristine-regenable).
Extracts the block verbatim from the vendored fixup so the two cannot drift."""
import sys
import textwrap

V = "/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/fixup_game_funcs_vendored.py"
F = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c"

src = open(V).read()
start_marker = 'if p.name == "funcs_24.c" and "PATCH: s5228 store census" not in text:'
a = src.index(start_marker)
b = src.index('report.append("funcs_24.c: s5228 store census patched x2")', a)
body = src[a:b].split("\n", 1)[1]
text = open(F).read()
if "PATCH: s5228 store census" in text:
    sys.exit("already applied")
ns = {"text": text, "sys": sys, "changed": False}
exec("if True:\n" + body, ns)
open(F, "w").write(ns["text"])
print("applied s5228")
