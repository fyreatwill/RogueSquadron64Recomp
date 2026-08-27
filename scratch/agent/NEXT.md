# NEXT work unit (s2512) — batch the reachable image-to-PCM writer provenance capture

HYPOTHESIS-ID: m5-image-payload-writer-provenance

## Single work unit

Run one qualified image-arm capture now that the staggered route reaches the
target phase. Use the existing all-in-one image-stage, DMA-join, AI-table,
PCM-consumer, guest-store, RSP-writer, and host-writer controls. The capture
must include the independent retail oracle controls first, then the port arm;
do not interpret a writer null unless the oracle whole-RDRAM/phase controls and
the port image-stage and PCM-consumer controls all fire.

## Competing hypotheses and discriminator

- `H-guest-payload-writer`: a generated guest CPU store writes nonzero bytes to
  an image-joined AI-table destination before the first PCM consumer.
- `H-rsp-payload-writer`: the Factor 5 image/RSP path writes the nonzero
  payload, with a destination and event join visible in the RSP/DMA controls.
- `H-host-payload-writer`: host audio plumbing writes the AI blocks after the
  guest/RSP boundary and before queue consumption.
- `H-no-observable-writer`: all positive controls fire but none of the three
  writer classes joins a nonzero consumer buffer in the target phase.

The discriminator is one phase-scoped table keyed by AI-table entry and image
ordinal: first nonzero writer class/PC or RSP event, destination, byte count,
payload fingerprint, image-DMA completion, and first PCM-consumer event. A
guest/RSP/host join selects its corresponding hypothesis; a fully controlled
null selects `H-no-observable-writer`; missing image or consumer controls makes
the result unevaluable and selects nothing.

## Exact commands

```sh
tools/oracle/build.sh
cmake --build build --target RogueSquadron64Recomp
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PHASE=1 \
ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 zsh scratch/agent/run_s2512_m5_payload_writer.sh
```

The driver must arm the retail positive control before its target-phase watch,
launch one port image arm from `build/`, gate at 1024 then 512 with
phase-relative keys, and SIGKILL the process after the bounded capture. Logs
must be absolute under `scratch/agent/s2512_m5_payload_writer/`.
