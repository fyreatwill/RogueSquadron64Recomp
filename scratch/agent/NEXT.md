# NEXT work unit (s2150) — leftover fake_func class census

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

The two-line overlay-move class is closed: s2149's post-move census found
zero remaining human-in-main versus placeholder-in-overlay mismatches.
Remaining generated `func_*` names are five parked or intentional holds
(`func_8000040C`, `func_800927B0`, `func_80092A54`, `func_80092CF0`,
`func_800E9AE0`) — do not re-census or invent names for those.

The next source is leftover `fake_func_*` with ELF size `> 0xC` that are
not on PROJECT-OVERVIEW's parked list. Run a host-only ELF/companion
census (no game run, no regen unless a renameable leftover is selected
and then only after writing the discriminator table). Classify every
such leftover as renameable, overlapping-named-symbol, parked, or hold.
If one renameable leftover has a companion human name, unique ELF
section, and no overlap with a named symbol, that leftover is the next
mapping unit; if none do, close the leftover class as holds.

Do not run the game or change runtime, audio, task, output, guard, or
mitigation behavior.

## Competing hypotheses and discriminator

- `H-LeftoverRenameable`: at least one leftover with size `> 0xC` has a
  companion human name, a unique ELF section, and no overlap with a
  named symbol; the census names that leftover as the next two-line or
  one-line mapping unit.
- `H-LeftoverAllHolds`: every leftover with size `> 0xC` is parked,
  overlaps a named ELF symbol (including rspboot/ucode/data/BSS), or
  is an exception/cop0 trap body with no independent companion name.
- `H-CensusStale`: the ELF leftover list does not match generated
  `fake_func_*` prototypes, so the leftover class cannot be closed or
  selected from this tree.

The discriminator is one leftover table containing name, ELF
section/start/size/end, overlapping named symbols, parked-list
membership, and companion-comment/human-name hits. A non-empty
renameable row selects `H-LeftoverRenameable`; an empty renameable set
with complete coverage selects `H-LeftoverAllHolds`; a prototype/ELF
mismatch selects `H-CensusStale`.

## Exact commands

    /opt/homebrew/opt/llvm/bin/llvm-nm -S --format=posix \
      /Users/williambuckley/Documents/Tools/rogue_squadron64/build/roguesquadron.elf \
      > scratch/agent/s2150_elf_syms.txt
    /opt/homebrew/opt/llvm/bin/llvm-objdump -t \
      /Users/williambuckley/Documents/Tools/rogue_squadron64/build/roguesquadron.elf \
      > scratch/agent/s2150_elf_objdump.txt
    python3 - <<'PY'
    # Build one leftover table from the ELF dumps + parked list in
    # docs/PROJECT-OVERVIEW.md + companion symbol_files comments.
    # Write scratch/agent/s2150_leftover_table.txt with every fake_func
    # whose size > 0xC, classified renameable / overlap / parked / hold.
    PY

Compare generated `funcs.h` `fake_func_*` prototypes to the ELF leftover
names in the same table so `H-CensusStale` is tested in the same pass.
The work unit is complete when the table selects one of the three
hypotheses and, if renameable, names the single next mapping lead.
