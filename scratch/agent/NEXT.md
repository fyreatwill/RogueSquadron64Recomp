# NEXT work unit (s2148) — validate the next generated-symbol mapping

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the bounded static rename unit for `func_800B2630` ->
`buildFormatMessageGlyphBuffer`. The companion symbol files currently put
the human name in `main_overlay.txt` and the placeholder in
`menu_overlay.txt` at the same VRAM address. First run the fresh no-edit
regeneration as the baseline; then move only those two symbol-file lines so
the human name is in `menu_overlay.txt`, rerun the same regeneration, and
compare the complete ELF/generated boundary and caller table. Do not run the
game or change runtime, audio, task, output, guard, or mitigation behavior.

The s419 `m4_known_bad.txt` record is a live-crash warning
(`last-guest-pc=0x800290d4`, isolated alone from the s419 75-name batch),
not a static boundary conflict. Treat it as a reason to inspect the static
table, not as permission to skip the mapping. Leave leftover
`fake_func_800B2628` at `0x800B2628` untouched.

Mission-overlay human-versus-placeholder mismatches are exhausted; this is
the first remaining menu-overlay instance of the same two-line pattern.

## Competing hypotheses and discriminator

- `H-MenuMapping`: after the two-line move, the ELF has exactly one
  `buildFormatMessageGlyphBuffer` in `.ovl.menu` at `0x800B2630`,
  size `0x468`, ending at unchanged `0x800B2A98`; the generated prototype,
  definition, overlay entry, and every generated caller use the human name.
- `H-RegenerationStale`: the no-edit baseline or the moved-source rebuild
  still leaves `func_800B2630` in the ELF/generated tree, so source mapping
  changes are not reaching the pipeline.
- `H-BoundaryCallerConflict`: the move creates a duplicate/section mismatch,
  changes the `0x800B2A98` adjacent `allocFormatTextElement` boundary, or
  leaves any caller unresolved; do not retain the move if this occurs.

The discriminator is one baseline-versus-treatment table containing ELF
section/start/size/end, adjacent `allocFormatTextElement` at
`0x800B2A98`, generated prototype/definition/overlay-entry names, and all
generated call-site names (`tickFormatMessageWorker` at `jal 0x800B2630`,
`buildScaledFormatTextElement` at `jal 0x800B2630`, and
`processAndDisposeFormatMessage` at `jal 0x800B2630`). A clean treatment
row with unchanged boundaries and callers selects `H-MenuMapping`; a stale
treatment selects `H-RegenerationStale`; any duplicate, section, boundary,
or caller defect selects `H-BoundaryCallerConflict`.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/rogue_squadron64
    python3 tools/make_elf.py
    cd /Users/williambuckley/Documents/Tools/N64Recomp
    ./build/N64Recomp rogue_squadron.toml
    python3 fixup_game_funcs.py
    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    grep -n 'func_800B2630\|buildFormatMessageGlyphBuffer\|allocFormatTextElement' \
      /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
      /Users/williambuckley/Documents/Tools/rogue_squadron64/build/roguesquadron.elf \
      > scratch/agent/s2148_baseline_table.txt
    /opt/homebrew/opt/llvm/bin/llvm-nm -S --format=posix \
      /Users/williambuckley/Documents/Tools/rogue_squadron64/build/roguesquadron.elf \
      | grep -E 'func_800B2630|buildFormatMessageGlyphBuffer|allocFormatTextElement|fake_func_800B2628'

Then apply only the prescribed two-line move in
`/Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/main_overlay.txt`
and `menu_overlay.txt`, rerun the same five commands, and write the
treatment table to `scratch/agent/s2148_treatment_table.txt`. Verify the ELF
row with `/opt/homebrew/opt/llvm/bin/llvm-nm -S --format=posix` plus
`llvm-objdump -t` on the companion ELF, and the generated callers with the
same grep query. The work unit is complete only after both baseline and
treatment tables are compared.
