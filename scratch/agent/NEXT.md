# NEXT work unit — bounded generated-symbol audit at 0x8007C298

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Competing hypotheses and discriminator

- H-exact-callable: the companion symbol and generated body identify one
  callable; synchronize the project TOML to the human name.
- H-inline-fragment: the address is only an inline boundary or data gap; keep
  the placeholder and record why a rename would be unsafe.
- H-ambiguous: callers, header, or overlay registration disagree or duplicate
  the identity; preserve the placeholder and report the conflict.

The discriminator is one evidence table covering companion symbol/source,
generated prologue/body boundary, direct callers, header declaration, and
overlay registration. An exact callable with consistent boundaries selects a
rename; an inline body selects preservation; any disagreement selects an
ambiguity audit rather than a rename. The generated snapshot is the positive
control: its callable token and overlay entry must both visibly exist.

## Exact commands

    rg -n -C 12 '8007C298|fake_func_8007C298' \
      /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
      /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
    rg -n '8007C298|fake_func_8007C298' syms/rogue_squadron.syms.toml
    cmake --build build --config Debug --target RecompiledFuncs -- -j2

Write the bounded source table under
`scratch/agent/s3034_generated_symbol_rename/`, synchronize only the project
symbol TOML if the discriminator selects the exact callable, and build the
generated-functions target. Do not run the game.
