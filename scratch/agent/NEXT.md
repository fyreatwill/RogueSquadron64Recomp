# NEXT work unit (s2444) — independently repeat the port-side second-range boundary

HYPOTHESIS-ID: m5-port-second-range-consumer

## Work unit

Repeat the completed s2443 paired recipe with the new table unchanged. Build
one Debug binary and run the silent-stub and Factor 5 image arms with the
eleven-Start schedule, retaining the phase-gated task/DMA identity and every
later `0x1798B0..0x179A48` port event. Run the independent retail oracle with
the exact second-range controls. Do not change audio or output behavior.

## Competing hypotheses and discriminator

These are the hypotheses written before the build for this iteration:

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

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s2325_m5_task_output_join.sh s2444_m5_port_second_range_consumer`

The driver must use `ROGUESQ_AUDIO_UCODE=0` for the stub and `=1` for the image
arm, with
`ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1`, the eleven-Start schedule, and retail controls including
`--watch-write 0x0:0x800000`, title/hangar VI controls, exact ranges
`0x167650:0x167C50` and `0x1798B0:0x179A48`, plus the
`0x8002BEEC`/`0x800078EC` relation. Use shell-native watchdogs and SIGKILL.
