# NEXT (s7619)
HYPOTHESIS-ID: g6-upstream-features

G6b step 1 landed s7618 (rs64_bindings.h table, defaults == old map, offline + same-run proof). Take G6b step 2 now.

G6b step 2: load overrides from `controls.json` in the data folder (find where saves/config live: grep "saves" /
get_data_dir in main.cpp; missing or unparsable file = built-in defaults + one stderr line). Format (upstream
`git show origin/main:src/input/input_bindings.cpp` is reference only): {"version":1,"buttons":{"A":["pad:a","key:z"],
"Z":["axis+:lefttrigger:16000","key:c"], ...},"stick":{"pad_x":"leftx","pad_y":"lefty","invert_y":true,"up":["key:w"],...}}.
A button listed in the file REPLACES that button's default list; unlisted buttons keep defaults. Names via
SDL_GameControllerGetButtonFromString / GetAxisFromString / SDL_GetScancodeFromName. Write a hand JSON reader or use a
JSON lib already in tree (check lib/ for nlohmann or similar; RT64 may vendor one).
Proof: extend tools/test_bindings.cpp: (a) parse(empty/missing) == defaults byte-identical (reuse the 233288-case sweep);
(b) a file remapping A to pad:b moves the bit (positive control); (c) a malformed file falls back to defaults.
Hypotheses: H-equal (no file -> identical to s7618) vs H-drift. Only H-equal may land.
Step 3: F6 ImGui Controls panel. Then README Controls + OWNER-OPT-INS. Do not change any default binding.
Runtime check recipe (s7618): cd build; env SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1 ROGUESQ_NO_SAVE_WRITE=1
ROGUESQ_BIND_SELFTEST=1 ./RogueSquadron64Recomp rogue_squadron.z64 (60 s, SIGKILL) -> [bind-check] mismatches=0, mutant>0.
Hygiene: one game at a time; never touch build/saves or clear ROGUESQ_NO_SAVE_WRITE; never launch under lldb.
