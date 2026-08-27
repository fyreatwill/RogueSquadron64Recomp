# NEXT work unit (s2776) — explicitly wire phase-relative probe keys

HYPOTHESIS-ID: m5-step1-qualified-rebaseline

## Work unit

Run one compiled Debug build with concurrent image and silent arms, explicitly
launching `tools/probe.sh` for each arm with
`PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start'`,
`PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, and `PROBE_LEAVE_OK=1`.
Keep C88 unset and retain the existing phase/M5 controls. Run the retail
oracle whole-RDRAM positive control first, then both port arms, and SIGKILL
the remaining process group after the bounded window. Do not interpret
downstream nulls unless both title `1024` and hangar origin `0x006AB400` are
observed in both arms.

## Competing hypotheses and discriminator

- H-InputRepair: both arms reach title 1024 and hangar origin with the
  explicitly wired probe-key path, making the image/silent comparison valid.
- H-RouteInvalid: either arm still stalls before both target phases, so no
  audio-contract conclusion is valid.
- H-InputPathMismatch: an arm reaches the phases only after the probe-key
  schedule is active, identifying the prior driver wiring as the blocker.

The discriminator is one same-build table keyed by arm and phase: target-phase
reachability, image DMEM/DMA/completion counts, silent-arm zero controls, and
PCM/service joins. Target phases in both arms make the comparison valid;
missing target phases select recipe-invalid and require another input repair.

## Exact commands

1. Use a self-contained two-arm driver based on `tools/probe.sh`; verify its
   logs contain the phase-gate line before any key is sent. Launch both arms
   concurrently from `build/` and SIGKILL after 90 seconds.
2. Preserve `ROGUESQ_M5_C88_VALUE` unset, set `ROGUESQ_AUDIO_UCODE=1` only on
   the image arm and `0` only on the control, and retain the existing
   phase/M5 logging variables.
3. Compare only rows at title 1024 and hangar `0x006AB400`; write the result
   and phase validity to the next ledger entry.

Expected outcomes: qualified target phases in both arms permit the image vs
silent task/PCM comparison; absent target phases invalidate the row and select
recipe repair, not an audio hypothesis.
