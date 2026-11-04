# NEXT: G5 renaming sweep, next bounded batch (ladder: G1-G4 rungs closed, parked or awaiting owner)
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Why: g1-true-flight-hold closed s6867 (docs/G1-TRUE-FLIGHT.md). Next steps offer only owner-judgement items and G4 parks repeat holds, so ITERATION item 3c falls through to G5 / item 4.
First: run `grep -n '^## Session ' PORTING-STATE.md | tail -15`. If all 15 belong to the sweep, this is a REVISIT (see item 4). s6867 checked: 0 of 15 did.
Then: count remaining placeholders, pick one bounded batch by evidence, not by address. Use tools/rename/find_callers.py and tools/rename_generated_symbols.py (RENAMES table, checked batch). Each name needs a stated reason in its comment, as the table does. bcmp/bzero must keep the _recomp suffix (s5223 boot crash): check any libc-like name against libSystem interposition.
Hypotheses: H-name (the function's callers and body fix its role: rename) / H-unclear (evidence supports only a shape name: use *Preamble or data_gap style, or leave it) / H-collision (the name interposes a host symbol: boot fails at once, so boot after the batch).
Discriminator per batch: regen order make_elf -> N64Recomp -> fixup_game_funcs -> cmake, then tools/regen_verify.sh and one lvl1 dd1 boot with [initMission] reached. A rename must change no machine code: expect the same 2708/75 split.
Watch the meter: a rename edit alone reads as no engineering change (iron rule 14). If the streak nears 6, land a tool or code change.
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_replay.sh + regen_verify.sh to the CLAUDE.md regen order (owner file, not edited).
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous. Owner can lift the park for these.
