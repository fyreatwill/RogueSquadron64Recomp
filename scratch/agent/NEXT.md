# NEXT work unit (s2131) — classify the next generated-symbol collision

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the required sweep preflight, then resolve one bounded companion-symbol
mapping question for `0x800C41B0`. The current generated tree has
`func_800C41B0`; `main_overlay.txt` calls it `plotRadarBlipColumn`, while
`mission_overlay.txt` still carries the placeholder. Test source ownership,
ELF section, generated boundaries, and every caller before applying the
two-line move.

## Competing hypotheses and discriminator

- `H-MissionMapping`: the duplicate is the cause. Moving the human name to
  `mission_overlay.txt` emits `plotRadarBlipColumn` in `.ovl.mission`,
  preserving the `0x800C41B0` start, the no-edit ELF size/end boundary, and
  every caller.
- `H-RegenerationStale`: the source mapping is already effective and the
  placeholder is stale. A clean make-ELF/N64Recomp/fixup sequence changes the
  generated name without editing either symbol line.
- `H-BoundaryOrCollision`: source ownership or a duplicate/boundary collision
  is real. Moving the name changes the emitted section, drops the symbol,
  changes the function boundary, or produces a duplicate/conflicting caller
  mapping; leave the placeholder and advance without inventing a name.

The discriminating table is: source file and section for the address; ELF
symbol name, section, start, size, and end; generated prototype/definition/
overlay entry; and every generated caller. Select `H-MissionMapping` only if
the human symbol is emitted in `.ovl.mission`, the placeholder disappears at
that address, the no-edit boundaries remain unchanged, and all callers resolve
to the human name. Select `H-RegenerationStale` only if regeneration alone
produces that same table. Any conflict, dropped symbol, changed boundary, or
caller mismatch selects `H-BoundaryOrCollision` and no rename is landed.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    grep -n '^## Session ' PORTING-STATE.md | tail -15
    rg -n -C 4 'plotRadarBlipColumn|func_800C41B0|800C41B0' ../rogue_squadron64/symbol_files ../N64Recomp/RecompiledFuncs/funcs_28.c ../N64Recomp/RecompiledFuncs/funcs.h ../N64Recomp/RecompiledFuncs/recomp_overlays.inl

If the preflight confirms the duplicate without establishing a boundary
conflict, first run the mandated regeneration order without editing the
symbol files to test `H-RegenerationStale`. If the placeholder remains, use
`apply_patch` to remove only the `plotRadarBlipColumn = 0x800C41B0` line from
`../rogue_squadron64/symbol_files/main_overlay.txt` and change only the
`func_800C41B0 = 0x800C41B0` entry in
`../rogue_squadron64/symbol_files/mission_overlay.txt` to the human name.
Do not touch unrelated comments or any other symbol.

    cd /Users/williambuckley/Documents/Tools/rogue_squadron64
    python3 tools/make_elf.py
    cd /Users/williambuckley/Documents/Tools/N64Recomp
    ./build/N64Recomp rogue_squadron.toml
    python3 fixup_game_funcs.py
    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    cmake --build build --config Debug --target RogueSquadron64Recomp

Inspect only the bounded result:

    rg -n -C 2 'plotRadarBlipColumn|func_800C41B0|0x800C41B0' ../N64Recomp/RecompiledFuncs/funcs_28.c ../N64Recomp/RecompiledFuncs/funcs.h ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
    rg -n -g 'funcs_*.c' '\b(plotRadarBlipColumn|func_800C41B0)\b' ../N64Recomp/RecompiledFuncs
    objdump -t ../rogue_squadron64/build/roguesquadron.elf | rg 'plotRadarBlipColumn|func_800C41B0|800c41b0'
    git -C ../rogue_squadron64 diff --check -- symbol_files/main_overlay.txt symbol_files/mission_overlay.txt
    git -C ../N64Recomp diff --check -- fixup_game_funcs.py

Do not run a game soak: this work unit is complete when the source/ELF/
generated boundary table selects one hypothesis. If it does not select one,
record the conflict and choose the next placeholder lead in the next ledger
entry.
