# NEXT work unit (s1972) — drainAudioAndFinalizeSpeechBuffer spin class

HYPOTHESIS-ID: audio-drain-spin-class

## What s1971 settled

The bltzal $zero PIC-idiom link-register class is closed. Six sites in
`funcs_27.c` (`filterVoiceSampleBlock`, `applyVoiceDelayFilter`,
`renderVoiceAudioBlock`) never received `ctx->r31 = PC+8` from N64Recomp's
direct-call lowering. The s1971 patch applied all six. Hangar now runs
60s+ / 17 frames with no crash vs 1 frame / 4s before.

New observation: `drainAudioAndFinalizeSpeechBuffer` spinning at 218M+
iterations across the full 60-second window. VI advancing normally
(update_screen #5312 at 60s) so rendering is not blocked. Whether audio is
blocked is unknown. The 180s soak in `soak_queue/s1971_hangar_180s.sh` may
arrive before this runs.

## Single next work unit

Investigate the `drainAudioAndFinalizeSpeechBuffer` spin. First check the
180s soak result (SOAK-RESULTS.md). Then, if the soak shows stability, a
spin-yield arm comparison run:

1. Find `drainAudioAndFinalizeSpeechBuffer` in `funcs_34.c` (or wherever the
   slot-ret-caller probe fires for it) and locate the spin loop.
2. Check whether the loop body is the same `beq v0==0` pattern (guest idling
   for a condition from the host, which hardware would preempt).
3. If it is, add a third `yield_self_1ms` gate with a new `siten` value under
   `ROGUESQ_SPIN_YIELD`, modeled on the existing two gates in `funcs_34.c`.
4. Run two arms in ONE build: yield=1 and yield=0, each for 60s, looking for
   audio-path differences.

## Competing hypotheses and discriminator

- **H-spin-benign:** the spin resolves once audio data arrives; VI continues
  because the spin and VI run in independent threads. Evidence: if 180s soak
  shows stable hangar with no new crash.
- **H-spin-starves-audio:** the spin starves the audio-mix thread, causing
  silence or eventual crash. Evidence: if 180s soak crashes or audio-path
  instrumentation shows zero audio output while the spin runs.
- **H-new-yield-needed:** like `menuControllerInput`, adding ROGUESQ_SPIN_YIELD
  to this loop unblocks forward progress. Evidence: yield=1 arm shows audio
  advance while yield=0 arm stays stuck.

Discriminator: check 180s soak first. If stable → H-spin-benign tentative
(single-source; need audio-output evidence to confirm). If crash →
investigate `drainAudioAndFinalizeSpeechBuffer` in static code, find the
loop, determine if it's a `beq v0==0` idle spin, add yield gate, run A/B.

## Exact commands

Check soak result first:
```sh
tail -5 scratch/agent/SOAK-RESULTS.md
```

Find the function in generated code:
```sh
rg -n 'drainAudioAndFinalizeSpeechBuffer\|drainAudio' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c | grep 'RECOMP_FUNC\|void'
```

Find the spin loop (same pattern as L_800B8050 / L_800C5930):
```sh
grep -n 'beq.*v0\|beq.*r2.*r0\|ctx->r2.*ctx->r0' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/[relevant_file].c | head -30
```

If a new yield site is needed, the existing pattern in funcs_34.c is:
```
ROGUESQ_SPIN_YIELD == site=menuInit | site=menuInput
```
Model the new site as `site=audioDrain`.

Run A/B probe in one build:
```sh
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1972_audio_yield 60 2
```
(And a second run without ROGUESQ_SPIN_YIELD=1 for the no-yield arm, if A/B within one run is not feasible.)

Positive control: same-run hangar phase entry + known VI progression.
