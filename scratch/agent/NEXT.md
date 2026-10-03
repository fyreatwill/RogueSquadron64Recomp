# Next work unit: bounded generated-symbol lead after the synchronized display-list range

HYPOTHESIS-ID: generated-symbol-renaming-sweep

M5 remains parked pending a new arm-stability discriminator, and the measured
M3 `rs_zcfree` idiom remains closed at static scope. The next unit is one
bounded, regeneration-safe symbol-renaming lead, not a runtime experiment.

Competing hypotheses and discriminator:

- H1: `0x80009000..0x8000A000` contains an exact companion semantic mapping
  for one or more generated placeholders; rename only one-to-one mappings.
- H2: the range contains candidates but they are ambiguous, fake fragments, or
  lack semantic source; preserve placeholders and record them.
- H3: the range has no stale placeholder references; select no rename.

The discriminating measurement is the rename tool's bounded table joined to
the verified sibling `rogue_squadron64/symbol_files` directory. A valid run
must show named companion rows such as `rs_zcalloc` as `already-synchronized`
in the same output. H1 predicts selected mappings and changed generated
references; H2 predicts candidate rows with no safe change; H3 predicts only
positive-control/already-synchronized rows or no remaining placeholders.

Exact commands:

    grep -n '^## Session ' PORTING-STATE.md | tail -15
    env RSR_FUNCS_DIR=/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x80009000 --end-address 0x8000A000 --limit 32

Do not build unless the mapping pipeline requires it. Do not start a second
range. If the companion positive control is absent, treat the run as invalid
and fix the path before drawing a conclusion.
