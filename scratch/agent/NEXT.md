# NEXT work unit (s2149) — validate the next generated-symbol mapping

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the bounded static rename unit for `func_800B3824` ->
`buildLevelSelectTextTextures`. The companion symbol files currently put
the human name in `main_overlay.txt` and the placeholder in
`menu_overlay.txt` at the same VRAM address. First run the fresh no-edit
regeneration as the baseline; then move only those two symbol-file lines so
the human name is in `menu_overlay.txt`, rerun the same regeneration, and
compare the complete ELF/generated boundary and caller table. Do not run the
game or change runtime, audio, task, output, guard, or mitigation behavior.

The s419 `m4_known_bad.txt` record is a live-crash warning
(`last-guest-pc=0x8000b650`, isolated alone from the s419 75-name batch),
not a static boundary conflict. Treat it as a reason to inspect the static
table, not as permission to skip the mapping. There is no leftover
`fake_func_*` immediately before this start: `tickFormatMessageWorker`
ends at `0x800B3824`.

A post-s2148 census found this as the last remaining human-in-main versus
placeholder-in-overlay mismatch. After it, the two-line overlay-move
pattern is exhausted and the next sweep lead needs a new source.

## Competing hypotheses and discriminator

- `H-MenuMapping`: after the two-line move, the ELF has exactly one
  `buildLevelSelectTextTextures` in `.ovl.menu` at `0x800B3824`,
  size `0x2D8`, ending at unchanged `0x800B3AFC`; the generated prototype,
  definition, overlay entry, and every generated caller use the human name.
- `H-RegenerationStale`: the no-edit baseline or the moved-source rebuild
  still leaves `func_800B3824` in the ELF/generated tree, so source mapping
  changes are not reaching the pipeline.
- `H-BoundaryCallerConflict`: the move creates a duplicate/section mismatch,
  changes the `0x800B3AFC` adjacent `buildScaledFormatTextElement` boundary,
  or leaves any caller unresolved; do not retain the move if this occurs.

The discriminator is one baseline-versus-treatment table containing ELF
section/start/size/end, adjacent `buildScaledFormatTextElement` at
`0x800B3AFC`, generated prototype/definition/overlay-entry names, and the
generated call-site name (`initVwingHudAndSlotState` at `jal 0x800B3824`).
A clean treatment row with unchanged boundaries and callers selects
`H-MenuMapping`; a stale treatment selects `H-RegenerationStale`; any
duplicate, section, boundary, or caller defect selects
`H-BoundaryCallerConflict`.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/rogue_squadron64
    python3 tools/make_elf.py
    cd /Users/williambuckley/Documents/Tools/N64Recomp
    ./build/N64Recomp rogue_squadron.toml
    python3 fixup_game_funcs.py
    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    grep -n 'func_800B3824\|buildLevelSelectTextTextures\|buildScaledFormatTextElement' \
      /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
      /Users/williambuckley/Documents/Tools/rogue_squadron64/build/roguesquadron.elf \
      > scratch/agent/s2149_baseline_table.txt
    /opt/homebrew/opt/llvm/bin/llvm-nm -S --format=posix \
      /Users/williambuckley/Documents/Tools/rogue_squadron64/build/roguesquadron.elf \
      | grep -E 'func_800B3824|buildLevelSelectTextTextures|buildScaledFormatTextElement|tickFormatMessageWorker'

Then apply only the prescribed two-line move in
`/Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/main_overlay.txt`
and `menu_overlay.txt`, rerun the same five commands, and write the
treatment table to `scratch/agent/s2149_treatment_table.txt`. Verify the ELF
row with `/opt/homebrew/opt/llvm/bin/llvm-nm -S --format=posix` plus
`llvm-objdump -t` on the companion ELF, and the generated callers with the
same grep query. The work unit is complete only after both baseline and
treatment tables are compared.
