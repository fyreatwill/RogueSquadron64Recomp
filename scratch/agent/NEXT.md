# NEXT work unit (s2132) — classify the next generated-symbol collision

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Resolve one bounded companion-symbol mapping question for `0x800BF790`.
The generated tree currently has `func_800BF790`; `main_overlay.txt` calls it
`updateHudHealthIndicator`, while `mission_overlay.txt` still carries the
placeholder. Test source ownership, ELF section, generated boundaries, and
every caller before applying the two-line move.

## Competing hypotheses and discriminator

- `H-MissionMapping`: moving the human name to `mission_overlay.txt` emits
  `updateHudHealthIndicator` in `.ovl.mission`, preserves the start, size/end
  boundary, and all callers.
- `H-RegenerationStale`: the source mapping is already effective and a clean
  make-ELF/N64Recomp/fixup sequence changes the generated name without editing
  either symbol line.
- `H-BoundaryOrCollision`: source ownership or a duplicate/boundary collision
  is real. Moving the name changes the emitted section, drops the symbol,
  changes the function boundary, or produces a caller mismatch; leave the
  placeholder and advance without inventing a name.

The discriminator is one table containing source file and section; ELF name,
section, start, size, and end; generated prototype/definition/overlay entry;
and every generated caller. Select `H-MissionMapping` only when the human
symbol is emitted in `.ovl.mission`, the placeholder disappears, no-edit
boundaries remain unchanged, and all callers resolve to the human name.
Select `H-RegenerationStale` only if regeneration alone produces that table.
Any conflict, dropped symbol, changed boundary, or caller mismatch selects
`H-BoundaryOrCollision` and no rename is landed.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    grep -n '^## Session ' PORTING-STATE.md | tail -15
    rg -n -C 4 'updateHudHealthIndicator|func_800BF790|800BF790' ../rogue_squadron64/symbol_files ../N64Recomp/RecompiledFuncs/funcs_28.c ../N64Recomp/RecompiledFuncs/funcs.h ../N64Recomp/RecompiledFuncs/recomp_overlays.inl

If the preflight confirms the duplicate, first run the no-edit control:

    cd /Users/williambuckley/Documents/Tools/rogue_squadron64
    python3 tools/make_elf.py
    cd /Users/williambuckley/Documents/Tools/N64Recomp
    ./build/N64Recomp rogue_squadron.toml
    python3 fixup_game_funcs.py

If the placeholder remains, use `apply_patch` to remove only the
`updateHudHealthIndicator = 0x800BF790` line from
`../rogue_squadron64/symbol_files/main_overlay.txt` and change only the
`func_800BF790 = 0x800BF790` entry in
`../rogue_squadron64/symbol_files/mission_overlay.txt` to the human name.
Then rerun the same make-ELF/N64Recomp/fixup sequence and:

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    cmake --build build --config Debug --target RogueSquadron64Recomp
    rg -n -C 2 'updateHudHealthIndicator|func_800BF790|0x800BF790' ../N64Recomp/RecompiledFuncs/funcs_28.c ../N64Recomp/RecompiledFuncs/funcs.h ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
    rg -n -g 'funcs_*.c' '\b(updateHudHealthIndicator|func_800BF790)\b' ../N64Recomp/RecompiledFuncs
    objdump -t ../rogue_squadron64/build/roguesquadron.elf | rg 'updateHudHealthIndicator|func_800BF790|800bf790'
    git -C ../rogue_squadron64 diff --check -- symbol_files/main_overlay.txt symbol_files/mission_overlay.txt
    git -C ../N64Recomp diff --check -- fixup_game_funcs.py

Do not run a game soak: this work unit is complete when the static
source/ELF/generated boundary table selects one hypothesis.
