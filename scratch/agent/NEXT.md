# NEXT work unit (s1169)

HYPOTHESIS-ID: musyx-synth-indirect-callback-contract

Perform one bounded runtime capture of the indirect VI callback dispatch that
invokes `musyxSynthFrame`, with a phase-scoped positive control and a single
discriminator for the callback's guest stack/return register handoff at entry.
Do not add a guard, skip, restore, or mitigation.

Competing hypotheses and discriminator:

- H1: the indirect callback dispatcher hands `musyxSynthFrame` a corrupted
  guest `$sp`/`$ra`; the entry discriminator shows a bad value before the
  function's prologue executes.
- H2: the dispatcher handoff is valid at entry and the fault is downstream of
  callback dispatch; the same run reaches the independent callback positive
  control and records valid entry state.
- H3: the callback path is not reached in the pre-1024 arm; the independent
  positive control is absent, making the capture unevaluable rather than a
  null result.

The discriminating measurement is one phase-gated callback-entry table with
the independent callback positive control, entry `$sp`/`$ra`, and the first
`musyxSynthFrame` prologue values in the same run. A bad handoff with the
control live selects H1; a valid handoff with the control live selects H2;
missing control is H3/unevaluable.

Exact commands:

    sed -n '4200,4320p' ../N64Recomp/RecompiledFuncs/funcs_24.c
    sed -n '420,510p' lib/N64ModernRuntime/librecomp/src/overlays.cpp
    rg -n "tickfunc|8009123C|0x11A8A8|callback" src lib/N64ModernRuntime
    rg -n "ROGUESQ_LOG_TICKFUNC_CALLER|AUDIOTICK_TRACE|PROBE_PHASE" tools scratch/agent

Before building, write the exact positive-control and handoff fields into the
instrument plan; batch them in one build and run. If the existing callback
entry instrumentation cannot expose the handoff, redesign the probe before
building rather than adding a non-discriminating field.
