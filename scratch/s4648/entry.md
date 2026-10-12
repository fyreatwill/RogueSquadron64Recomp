
## Session 4648 (2026-10-11) — UNBLOCK: s4647 block refuted (regen repair needs no authorization)

s4647 blocked asking permission to repair the broken full regen. Refuted: fixup_game_funcs.py has one hard-coded output path (line 27); a repointed copy run on a copy of RecompiledFuncs.s4204-fresh in ../N64Recomp/scratch_s4648/ leaves the live tree untouched and reproduces the abort (rc=1, "s4339 C88C descriptor anchor count=0"). New root cause: that anchor is the s4332 probe, present only in the live hand-patched tree, not in the fixup script. 168 of 384 distinct PATCH sNNNN tags in live are absent from the fixup source (crude match); some are behavioral (s4563 stale-head skip default ON, s4296, s4580, s4571c, s4572), so a regen would silently change runtime behavior. Work unit re-scoped in NEXT.md (classify + backport + vendor script). Tooling in scratch/s4648/; details in scratch/agent/UNBLOCK.md.

ORIGIN: tooling/census only; no runtime, ROM, or generated-code change.
