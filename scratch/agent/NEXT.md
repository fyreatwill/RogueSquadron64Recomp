# NEXT work unit — qualify retail producer-entry ground truth

HYPOTHESIS-ID: m5-producer-entry-ground-truth-qualification

Session 3417 left the producer entry contract unevaluable before any port
instrumentation: the prescribed oracle had no hangar phase rows, and the fixed
Rice route stopped at title VI 1024 / VI 2037 around 34.6 seconds. The next
unit must make the independent retail arm reach hangar 512 with its controls
and final summaries intact.

Competing hypotheses and the single discriminating measurement:

- H-RetailRouteRecipe: the s3417 early stop is caused by a stale or incomplete
  video/input/configuration recipe.
- H-RetailOracleRuntime: the route is correct but the debugger/video core stops
  before hangar independently of the recipe.
- H-RetailPhaseArm: the route reaches hangar, but the phase/histogram arm is
  wrong and hides the target rows.

The discriminator is one fresh retail-only run using the validated Rice/input
recipe, with whole-RDRAM, title 1024, hangar 512, producer execution, explicit
hangar phase, and final histogram controls. Reaching hangar with target rows
qualifies the next unit. Reaching hangar with no phase rows selects
H-RetailPhaseArm. An early stop with the recipe independently verified selects
H-RetailOracleRuntime; a stop that changes with recipe correction selects
H-RetailRouteRecipe. Any missing positive control is unevaluable.

Exact qualification command should be derived from the known s3414 Rice route
and run from the repo root, capturing output under a non-dot final path:

`tools/oracle/build/rs64_oracle --core <debug-core> --rom <retail-rom> --video <rice-plugin> --secs 120 --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179A48 --watch-pc 0x800078EC --pc-hist-phase 0x006AB400:512 --pc-hist-watch 1 --post-value-watch 1 --post-value-pc 0x800078EC --vi-trace --press <validated-s3414-presses>`

Do not add port instrumentation, change waits, slots, dispatch, clear behavior,
or PCM writeback until this command reaches hangar and emits its summaries.
