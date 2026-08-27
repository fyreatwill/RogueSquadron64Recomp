# NEXT work unit (s2513) — qualified image-arm PCM payload writer provenance capture

HYPOTHESIS-ID: m5-image-payload-writer-provenance

## Context

s2512 was a close-out iteration: it applied the pending no-engineering churn guard
to tools/agent/loop.sh (65 lines added). No experiment ran.

The active work unit is the image-to-PCM payload writer provenance capture from
the prior NEXT.md. s2511 showed that staggered startup separates the pre-target
paired failure from the later crash — so the staggered-startup approach is now the
qualified recipe. Use it for the payload writer capture.

## Single work unit

Run one qualified image-arm capture under the staggered-startup recipe. The
baseline single-image arm must reach 1024 first (positive control), then start
the paired arms. Capture must include ALL of: image-stage, DMA-join, AI-table,
PCM-consumer, guest-store, RSP-writer, and host-writer controls active. Do not
interpret a null unless ALL those controls fire.

## Competing hypotheses and discriminator

- `H-guest-payload-writer`: a generated guest CPU store writes nonzero bytes to
  an image-joined AI-table destination before the first PCM consumer.
- `H-rsp-payload-writer`: the Factor 5 image/RSP path writes the nonzero payload,
  visible in RSP/DMA controls with a destination joining the AI table.
- `H-host-payload-writer`: host audio plumbing writes the AI blocks after the
  guest/RSP boundary and before queue consumption.
- `H-no-observable-writer`: all positive controls fire but none of the three
  writer classes joins a nonzero consumer buffer in the target phase.

The discriminator is one phase-scoped table keyed by AI-table entry and image
ordinal: first nonzero writer class/PC or RSP event, destination, byte count,
payload fingerprint, image-DMA completion, and first PCM-consumer event. A
guest/RSP/host join selects its hypothesis; a fully controlled null selects
`H-no-observable-writer`; missing image or consumer controls makes the result
unevaluable.

## Exact commands

```sh
# 1. Build (if not already current):
cmake --build build --target RogueSquadron64Recomp

# 2. Run (staggered startup: baseline arm first, wait for 1024, then pair):
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PHASE=1 \
ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 zsh scratch/agent/run_s2513_m5_payload_writer.sh
```

The driver script should:
- Launch one baseline (image-arm) process and wait until it logs phase=1024
- Then start the paired capture arm (image + all payload-writer controls active)
- Phase-gate the pair at 1024 then 512 with phase-relative keys
- SIGKILL all processes after the bounded capture (≤300 s)
- Write audit to scratch/agent/s2513_m5_payload_writer/

If the qualified staggered recipe crashes before reaching 512, document the
crash site and do NOT attempt mitigation — record the crash location and the
discriminating controls that fired/didn't.

## Budget rule

This is iteration 1 on slug m5-image-payload-writer-provenance with the
staggered-startup recipe. If 3 consecutive iterations produce no discriminating
result (writer table unevaluable), stop and write BLOCKED with the specific
missing positive control.
