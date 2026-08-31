# NEXT work unit — audit callback-table population for the missing slot/status edge

HYPOTHESIS-ID: m5-slot-status-callback-table-audit

Session 3331 found all four retail consumer PCs as generated bodies, but the
three voice-side bodies have no direct generated callsite. Perform one bounded
static audit of the indirect callback table around `0x80019B74`; do not build,
run, change behavior, or add a mitigation.

## Competing hypotheses

- `H-CallbackTargetsInstalled`: the callback table contains the expected
  `0x8009B5A8` and `0x8009BD7C` targets and its initializer is reachable.
- `H-CallbackTargetsAbsent`: one or both targets are never written into the
  table, selecting callback-table/source coverage as the missing edge.
- `H-CallbackTargetsGated`: the targets are written, but the table initializer
  is behind a predicate that is false on the qualified port route.

## Discriminator

No build or runtime run. From the repository root, inspect the current
generated tree and callback setup/dispatch code:

    rg -n -i '80019b68|80019b74|80019b78|8009b5a8|8009bd7c|8009bde8' \
      /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
    rg -n -i '8012a4a4|8012a4a8|callback|jalr|0x8009b5a8|0x8009bd7c' \
      /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
      /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files

Enumerate every store feeding the callback slots and the immediate
initialization/caller chain. `H-CallbackTargetsInstalled` requires both target
values plus a reachable initializer; `H-CallbackTargetsAbsent` requires a
complete writer census with neither value; `H-CallbackTargetsGated` requires
the target writes plus a concrete false predicate. If any slot or writer
cannot be classified, record the unresolved site list and redesign rather
than infer a hypothesis.

The Session 3330 qualification and Session 3331 audit authorize no Step 3
contract change.
