# NEXT work unit (s2123) — synchronize the runVideoFrameTick symbol

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Perform one bounded, metadata-only generated-symbol rename: change the main
overlay TOML entry at `0x80001354` from `func_80001354` to
`runVideoFrameTick`. Do not rename any parked holdout or edit generated C.
This is a source-name synchronization; no build or runtime soak is needed if
the exact-definition and uniqueness checks pass.

## Competing hypotheses and discriminator

- `H-ExactMapping`: the companion mapping, generated function start, live
  body span, and callers all identify `runVideoFrameTick` at `0x80001354`.
- `H-OverlayCollision`: the address is reused by another overlay or the
  generated tree has more than one definition, so the TOML must remain a
  placeholder until the collision is resolved.
- `H-NameCollision`: `runVideoFrameTick` is already assigned to another
  address in the TOML or companion symbol files, so applying this rename would
  create an ambiguous dispatch name.

The discriminator is one bounded source census: exactly one generated
`RECOMP_FUNC` definition named `runVideoFrameTick`, its first body comment is
`0x80001354`, the TOML size is `0x2C8`, the companion mapping is the same
address, and all generated callers resolve to that name. H-ExactMapping permits
the one-line TOML rename; either collision outcome stops the rename and records
the precise holdout rather than guessing.

## Exact commands

1. Verify the mapping and boundaries before editing:

       cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
       rg -n 'func_80001354|runVideoFrameTick' \
         syms/rogue_squadron.syms.toml \
         /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/main_overlay.txt \
         /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c
       rg -n -U 'RECOMP_FUNC void runVideoFrameTick\\([^\\n]*\\) \\{[\\s\\S]{0,1200}// 0x80001354:' \
         /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c
       rg -n 'name = "runVideoFrameTick"|runVideoFrameTick[[:space:]]*=' \
         syms /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files

   The first command must show the companion definition and the generated
   function; the second must show one generated start; the third must show no
   competing address/name assignment. If any check fails, do not edit.

2. Apply only the exact TOML name change, then validate and inspect the diff:

       apply_patch <<'PATCH'
       *** Begin Patch
       *** Update File: syms/rogue_squadron.syms.toml
       @@
       -    { name = "func_80001354", vram = 0x80001354, size = 0x2C8 },
       +    { name = "runVideoFrameTick", vram = 0x80001354, size = 0x2C8 },
       *** End Patch
       PATCH
       python3 -c 'import tomllib; tomllib.load(open("syms/rogue_squadron.syms.toml", "rb")); print("TOML OK")'
       git diff --check
       git diff -- syms/rogue_squadron.syms.toml

Do not regenerate or build unless the source census finds a mismatch that
requires checking the generated pipeline; this unit is complete after the
one-line rename and TOML validation.
