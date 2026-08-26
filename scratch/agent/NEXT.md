# NEXT work unit (s2370) — M5 A1 null-function origin

HYPOTHESIS-ID: m5-a1-null-function-origin

## Work unit

Run one ground-truth-first capture at guest PC `0x80001F88` to determine
whether the port's `get_function(0)` request is a port-only call-site or a
retail call-site with a different/nonzero target. Keep the existing read-only
abort table and one build; use the retail oracle before the port. Retain the
whole-RDRAM and both target-origin controls plus the port early-640 transition
control. Do not add a null fallback, change dispatch, change VI selection, or
edit task/audio data.

## Competing hypotheses and discriminating measurement

- H-RetailCallsiteNonzero: the oracle executes `0x80001F88` in the target
  phase with a nonzero `$a0`/requested target while both port arms request
  `0x00000000`; this selects a port call-site/input divergence.
- H-RetailCallsiteNull: the oracle reaches `0x80001F88` with the same null
  request in the target phase; this selects a shared guest null-function
  origin and rules out a port-only call-site.
- H-RetailCallsiteAbsent: the oracle reaches both target origins with positive
  controls but has zero execution rows at `0x80001F88`; this selects that the
  port reaches a call-site retail does not.

The discriminator is one arm/phase table containing oracle watch-PC rows and
GPR `$a0`, oracle target-origin rows, port `[a1-abort]` requested address and
last guest PC, port early-640 transition rows, and crash/abort status. A null
oracle result is invalid unless the whole-RDRAM, target-origin, and named-PC
controls are all positive.

## Exact commands

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2370_m5_a1_null_function_origin.sh s2370_m5_a1_null_function_origin
    grep -E '^(controls|table|verdict) ' scratch/agent/s2370_m5_a1_null_function_origin/driver.log

The driver must run the oracle first with `--watch-write 0x0:0x800000`, both
target-origin watches, and `--watch-pc 0x80001F88`, then launch control and
alternate port arms from the same build and SIGKILL them after the table is
complete.
