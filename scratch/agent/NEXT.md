# NEXT work unit (s2610) — reproduce the title PCM positive control

HYPOTHESIS-ID: m5-hangar-pcm-writer

## Single work unit

s2609 proved directly that the default `0x80094648` writer stores legitimate
`0x7F` channel bytes in both title and hangar, while sampled PCM stayed zero.
However, the required title `nz=768` positive control failed in both s2609
runs, so the title/hangar PCM contrast is not yet admissible. Determine which
non-invasive run condition restores the already-known title control, using one
same-build concurrent A/B: baseline s2608 marker set versus the smallest
single omitted s2608 logging knob or route condition identified from the
existing s2608 command evidence. Do not change C88, ED48, `0x80094648`, or any
audio behavior.

## Competing hypotheses and discriminator

- `H-ControlConfounded`: one of the added s2609 logging arms changes timing or
  scheduling enough to suppress the title PCM burst.
- `H-ControlNondeterministic`: the title PCM burst is not stable under the
  accepted route, so the s2608 positive control was a one-run artifact.
- `H-ControlCommandMismatch`: s2609 omitted a required s2608 environment knob,
  and restoring it brings back `nz=768`.

The discriminator is a single build and concurrent A/B run that reaches title
and hangar: baseline s2608 flags versus the minimally corrected arm. A valid
result requires `[m5-94648-control]` in both phases and title PCM `nz=768` in
at least one arm. If only the corrected arm restores it, select
`H-ControlCommandMismatch`; if neither does, select `H-ControlNondeterministic`;
if baseline restores it while the prior extra-logging recipe does not, select
`H-ControlConfounded`. Do not interpret any PCM null without a same-run
positive control.

## Exact checks

1. Preserve the s2609 live probe and run `python3 tools/check_jr_t9_host_return.py`
   plus `python3 tools/check_c88_default_store.py`.
2. Identify the smallest command difference from the s2608 marker set using
   existing s2608 log markers; no new instrumentation is needed.
3. Build Debug `RogueSquadron64Recomp` only, with no N64Recomp regeneration.
4. Run both arms concurrently from `build/` for 90 seconds, SIGKILL both, with
   `ROGUESQ_AUDIO_UCODE=0`, `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`,
   `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, the validated AUTOPILOT and
   `ROGUESQ_AUTOPILOT_STOP_WIDTH=512`, plus the s2608 logging set and
   `ROGUESQ_LOG_M5_CHANNEL_STORE=1`. Capture baseline and corrected logs under
   `scratch/agent/s2610_*.log`.
5. Report per arm: title/hangar phase, title PCM distribution, new-witness
   controls and rows, C88/gate/song markers, crash/abort/missing-function.
