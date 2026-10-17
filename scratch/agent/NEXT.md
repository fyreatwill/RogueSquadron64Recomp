# Next: verify regen post-condition end to end
HYPOTHESIS-ID: m6-mission-stall
Step 1: on the next regen (make_elf -> N64Recomp -> fixup_game_funcs -> cmake) tee fixup output and confirm `[s4648-replay] post-condition ok` appears; then tools/check_a14_yield_patch.py.
Step 2: if no regen is pending, run the fixup against a scratch copy of RecompiledFuncs with the marker stripped (expect exit nonzero).
Then: M5/M3 are closed; remaining options are owner-level (see CURRENT-TRUTH s5008 list).
