# Next: generated-symbol renaming sweep — next companion-mapped candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Bounded work unit: select the next companion-mapped generated placeholder in
the adjacent libultra range after `0x8002A080`, then audit only that candidate.
Use the companion semantic name, generated prologue address, exact overlay
span, and at least one independent generated caller as gates.

Competing hypotheses and discriminator:

- H-name-correct: all four gates agree; apply the rename.
- H-span-mismatch: the generated address or overlay span crosses a split or
  neighboring entry; leave it unchanged.
- H-unproven: no live caller or usable semantic companion evidence; leave it
  unchanged and record why.

Discriminating measurement: compare the companion symbol address with the
generated prologue, compare `recomp_overlays.inl`'s span with the next entry,
and count direct generated callsites in one bounded inspection. Each outcome
selects rename, leave unchanged, or advance without a build/soak.

Commands:

    grep -n '^## Session ' PORTING-STATE.md | tail -15
    rg -n 'func_[0-9A-Fa-f]{8}' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -80
    rg -n '0x8002A0|0x8002A1|0x8002A2' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl

If all gates pass, add the explicit address mapping to
`tools/rename_generated_symbols.py`, run the bounded helper, and record the
audit in a new `docs/RENAME-S*.md`. Do not build or soak if the candidate
fails a gate.
