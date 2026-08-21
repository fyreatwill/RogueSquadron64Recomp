# NEXT work unit (s2129) — repair one generated-symbol section mapping

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the required sweep preflight, then make one bounded companion-symbol
mapping correction for `0x800AD380`. The already-regenerated
`func_80001354` lead is synchronized as `runVideoFrameTick`, so do not reopen
it. The next lead is `func_800AD380` -> `computeTrackedObjectWorldAnchor`.

The companion has the human name in `symbol_files/main_overlay.txt`, but
`0x800AD380` is outside the main `.text` range and inside `.ovl.mission`;
`symbol_files/mission_overlay.txt` still has the placeholder. Because
`make_elf.py` keeps the first duplicate name and assigns sections from the
source file, the likely correction is to remove the misplaced main-overlay
entry and rename the mission-overlay entry. This is a symbol metadata change,
not game logic or mitigation.

## Competing hypotheses and discriminator

- `H-MissionMapping`: the duplicate is the cause. Moving the human name to
  `mission_overlay.txt` makes `computeTrackedObjectWorldAnchor` the emitted
  function at `0x800AD380`, with the same overlay offset/size and callers.
- `H-RegenerationStale`: the source mapping is already effective and the
  generated placeholder is stale. A clean make-ELF/N64Recomp/fixup sequence
  changes the generated name without editing symbol files.
- `H-BoundaryOrCollision`: the companion name is wrong for this generated
  function or another section owns the address. The regenerated ELF either
  drops the human symbol or produces a boundary/duplicate conflict; leave the
  placeholder and advance to the next candidate rather than inventing a name.

The discriminating table is: source file and section for the address; ELF
emission; generated definition/prototype/overlay entry; function start/end
(`0x800AD380` through the next generated boundary); and every generated
caller. Select `H-MissionMapping` only if the human symbol is emitted in
`.ovl.mission`, the placeholder disappears at that address, boundaries remain
unchanged, and all callers resolve to the human name. Select
`H-RegenerationStale` only if regeneration alone makes the same table true.
Any dropped symbol, changed boundary, or duplicate conflict selects
`H-BoundaryOrCollision` and no rename is landed.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    grep -n '^## Session ' PORTING-STATE.md | tail -15
    rg -n -C 3 'computeTrackedObjectWorldAnchor|func_800AD380|800AD380' ../rogue_squadron64/symbol_files ../N64Recomp/RecompiledFuncs/funcs_28.c ../N64Recomp/RecompiledFuncs/funcs.h ../N64Recomp/RecompiledFuncs/recomp_overlays.inl

If the preflight confirms the mapping above, use `apply_patch` to remove only
the misplaced `computeTrackedObjectWorldAnchor = 0x800AD380` line from
`../rogue_squadron64/symbol_files/main_overlay.txt` and change only the
`func_800AD380 = 0x800AD380` entry in
`../rogue_squadron64/symbol_files/mission_overlay.txt` to the human name.
Then run the mandated regeneration order:

    cd /Users/williambuckley/Documents/Tools/rogue_squadron64
    python3 tools/make_elf.py
    cd /Users/williambuckley/Documents/Tools/N64Recomp
    ./build/N64Recomp rogue_squadron.toml
    python3 fixup_game_funcs.py
    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    cmake --build build --config Debug --target RogueSquadron64Recomp

Inspect only the bounded result:

    rg -n -C 2 'computeTrackedObjectWorldAnchor|func_800AD380|0x800AD380' ../N64Recomp/RecompiledFuncs/funcs_28.c ../N64Recomp/RecompiledFuncs/funcs.h ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
    git -C ../rogue_squadron64 diff --check -- symbol_files/main_overlay.txt symbol_files/mission_overlay.txt
    git -C ../N64Recomp diff --check -- fixup_game_funcs.py

Do not run a game soak: this work unit is complete when the source/ELF/
generated boundary table selects one hypothesis. If the table does not select
one, restore no files destructively; record the conflict and choose the next
placeholder lead in the next ledger entry.
