# NEXT work unit (s2832) — design M5 audio de-stubbing sequence

HYPOTHESIS-ID: m5-audio-destub-design

## Work unit

Create `docs/M5-AUDIO-PLAN.md`. Survey every currently active audio stub,
trap, and gate in the runtime and generated code, then specify an incremental
de-stubbing order. For each step name the contract being restored, the
expected failure mode, the phase-qualified validation soak, and its positive
control. This work unit is documentation only; do not change runtime behavior
or run a game experiment.

## Competing hypotheses and discriminator

- H-audio-degenerate-paths: the current silent/stubbed paths plausibly cause
  recurring audio-related crashes or state corruption, so at least one planned
  de-stub has a concrete validation discriminator.
- H-audio-boundary-independent: the active stubs are not on the named crash or
  publication paths, so the plan must preserve them as controls and identify
  the evidence needed before de-stubbing.
- H-contract-unknown: a stub lacks enough contract evidence for safe execution,
  so it must remain parked behind a ground-truth or microcode prerequisite.

The discriminator is the complete inventory-to-step matrix in the new plan:
every active stub maps to either a bounded de-stub step with a measurable
outcome, an explicit control, or a named prerequisite. Missing mappings mean
the survey is incomplete.

## Exact commands

```sh
rg -n -i 'audio|aspMain|musyx|MORT|RspExitReason::Broke|audio.*stub|silent|waitForAnyAudioSlot|osAi|osSpTask|AI_' src lib RecompiledFuncs tools docs --glob '!*.log' --glob '!*.md' > scratch/agent/s2832_audio_inventory.txt
rg -n -i 'audio|aspMain|musyx|MORT|RspExitReason::Broke|audio.*stub|silent|waitForAnyAudioSlot|osAi|osSpTask|AI_' docs/CURRENT-TRUTH.md docs/PROJECT-OVERVIEW.md docs/debug-trace-env-vars.md
git diff --check
```
