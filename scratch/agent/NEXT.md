# NEXT work unit (s2443) — test the port-side second-range consumer boundary

HYPOTHESIS-ID: m5-port-second-range-consumer

## Work unit

Using the now-grounded retail relation (`0x8002BEEC` → `0x800078EC`), add one
regeneration-safe, observation-only port table around the image-arm hangar
path. Build one Debug binary, then run the validated eleven-Start route with
the silent-stub and Factor 5 image arms in the same capture recipe. Record,
phase-gated by `0x006AB400:512`, the task ordinal/row, task data pointer,
image-DMA ordinal/row, and every later port write or consumer event that can
join those identities. Keep the existing independent retail-oracle controls
and do not change audio or output behavior.

## Competing hypotheses and discriminator

- H-PortSecondRangeConsumer: the image arm has a hangar consumer that joins
  the validated task/image identity and produces a bounded post-DMA event.
- H-PortSecondRangeMissing: the image arm completes its task and DMA but has
  no later hangar consumer event; the stub arm remains quiet at the same key.
- H-PortSecondRangeDifferentIdentity: a consumer exists, but the current
  task/DMA identity is not the join key and a stable alternate field is
  required.

The discriminator is one same-build, same-phase table containing both arms:
an image-row with a joined later consumer selects H-PortSecondRangeConsumer;
an image-row with no later consumer while the stub control is valid selects
H-PortSecondRangeMissing; repeated consumer events with a stable alternate
field but no current-key join selects H-PortSecondRangeDifferentIdentity.
No null is interpreted unless both port arms pass title and hangar controls,
the image arm shows DMEM work/generated DMA/SP completion, and the retail
whole-RDRAM/title/hangar controls pass in the paired recipe.

## Exact commands

First run `cmake --build build --config Debug --target
RogueSquadron64Recomp`. Then run the existing paired eleven-Start driver after
adding the single bounded table to the appropriate fixup/runtime source; use
`ROGUESQ_AUDIO_UCODE=0` for the stub arm and the default image arm, with
`ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1`. Run the retail oracle separately only as the required
ground-truth control, with `--watch-write 0x0:0x800000`, title/hangar VI
controls, exact ranges `0x167650:0x167C50` and `0x1798B0:0x179A48`, and the
eleven-Start schedule. Use shell-native watchdogs and SIGKILL.
