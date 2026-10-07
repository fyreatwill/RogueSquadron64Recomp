# Next work unit: M5 Step 4i `0x80084860` return/input

HYPOTHESIS-ID: m5-audio-step4i-voice-modulator-return

Session 4083 qualified the predecessor arithmetic. Retail and port matched
zero-shaped stages at `0x8008D5D0`/`0x8008D5EC`, but retail's
`0x8008D614` input was nonzero while the port's `0x8008D610` lhs was zero.
That lhs is the return of the preceding `evaluateVoiceModulatorRecord` call
at `0x80084860`.

Competing hypotheses:

- Hcallee-return: retail returns a nonzero value from `0x80084860` while the
  qualified port returns zero; the callee or its input boundary is the first
  divergence.
- Hcallee-input: the call-entry pointer/offset or source record differs before
  the call, while the callee's arithmetic is otherwise comparable.
- Hcallee-match: retail and port return matching values; the divergence is in
  the caller's use of the return or a later path.
- Hcoverage: either arm lacks the whole-RDRAM, title/hangar, or positive
  call/phase controls, making the comparison unevaluable.

Discriminating measurement: batch one regeneration-safe witness at the
`0x8008D624` call-entry/delay-slot and the `0x80084860` callee entry/return,
including call arguments, returned `v0`, and phase/route identity. Use the
existing arithmetic/setup rows as positive controls. Hcallee-return selects a
qualified retail nonzero versus port zero return; Hcallee-input selects a
qualified argument mismatch before the call; Hcallee-match moves into the
caller-side use; Hcoverage rejects the run.

Exact preparation/run: extend the same `funcs_23.c` regeneration fixup and
host logger, then build Debug. Run the fixed control-first recipe in
`scratch/agent/run_s4083_m5_predecessor_arithmetic_fixed.sh` shape, with the
retail oracle first and the isolated port second; arm whole-RDRAM, title and
hangar controls and all existing M5 breadcrumbs. Capture under a new
`scratch/agent/s4084_*` directory. Do not infer a writer from a port-only
zero or from the invalid concurrent retry.
