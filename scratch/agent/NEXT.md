# NEXT work unit (s1117)

HYPOTHESIS-ID: retail-oracle-mode-state-route

Perform one bounded static audit of the generated and companion callers and
arguments of `initVideoBootWrapper` and `advanceVideoFrame`, and the mode
record table around `0x80128D50`. Do not build or run another oracle capture;
the s1116 controls were positive and all eight writer watches fired, but
retail stayed at width 320.

Before inspecting details, competing hypotheses and discriminator:

- H-mode-record-constant: callers pass a fixed 320-mode record or the table
  entry is fixed; finding the concrete record/index and width selects this.
- H-mode-record-state-gate: a state/feature/input predicate selects the
  320 record; finding the guarding branch and its producer selects this.
- H-mode-record-pointer-corrupt: the caller/table pointer is computed or
  overwritten before the mode copy; finding a non-table target or writer
  selects this.

Discriminator: identify every caller, argument construction, table base/index,
and width-bearing load/store from generated output plus companion symbols. A
concrete 320 constant/table entry selects H-mode-record-constant; a reachable
predicate and its state producer selects H-mode-record-state-gate; a pointer
or overwrite outside the expected table selects H-mode-record-pointer-corrupt.
If all three remain unresolved, record the exact missing boundary and choose
one source-level witness for the next unit; do not add another runtime field.

Commands:

```sh
rg -n "initVideoBootWrapper|advanceVideoFrame|initVideoSubsystem|swapBufferWithViMode|selectAndApplyViMode|80128D50|D_80128D50" RecompiledFuncs patches lib src tools
rg -n "initVideoBootWrapper|advanceVideoFrame|initVideoSubsystem|swapBufferWithViMode|selectAndApplyViMode|80128D50|D_80128D50" ../rogue_squadron64 2>/dev/null
rg -n "80017CA0|80017CB0|80017CD0|80017CEC|8011A864|8011A865|8011A862|80128D50" RecompiledFuncs syms docs
```

Read only bounded windows around hits; append the classification and ruled-out
alternatives to `PORTING-STATE.md` and `docs/CURRENT-TRUTH.md`.
