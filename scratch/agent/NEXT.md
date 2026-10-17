# Next: generated-symbol renaming sweep — adjacent libultra candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Bounded work unit: audit `bzero_recomp -> bzero` at guest address
`0x8002A080`.

Competing hypotheses and discriminator:

- H-name-correct: companion name, generated start address, exact overlay span,
  and at least one independent generated caller agree; apply the rename.
- H-span-mismatch: the generated address or `recomp_overlays.inl` span crosses
  a split/neighboring entry; leave it unchanged.
- H-unproven: no live generated caller or no usable semantic companion
  evidence; leave it unchanged and advance to the next candidate later.

Discriminating measurement: compare the companion symbol address with the
generated prologue, compare `recomp_overlays.inl`'s span with the next entry,
and count direct generated callsites in one bounded inspection.

Commands:

    grep -n '^## Session ' PORTING-STATE.md | tail -15
    rg -n 'bzero_recomp|0x8002A080' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
    rg -n -C 2 'bzero_recomp' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl

If all gates pass, add the explicit address mapping to
`tools/rename_generated_symbols.py`, run the bounded helper for
`0x8002A080..0x8002B190`, and record the audit in a new `docs/RENAME-S*.md`.
Do not build or soak if the candidate fails a gate.
