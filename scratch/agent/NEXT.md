# NEXT work unit — locate the first producer of target writer setup state

HYPOTHESIS-ID: m5-port-setup-state-producer

Session 3423 selected `H-PortSetupStateDiffers`: both port arms already had
`s1=0x5622`, `t0=1`, `t1=0`, `ra=0` at caller edge `0x8008F2CC`, and the same
tuple at `rs_memset` entry. Retail target rows remain `s1=0x561F`,
`t0=0x2000FF01`, `t1=0x8010FEF8`, `ra=0x8008F2D4`.

Competing hypotheses and the single discriminating measurement:

- `H-PortEarlierSetupProducer`: an earlier guest instruction establishes the
  divergent `s1/t0/t1` state before `0x8008F2CC`.
- `H-PortSetupCallerContract`: the preceding setup matches retail until the
  caller edge, where the port call contract differs.
- `H-PortSetupMissing`: the preceding setup witness is absent or the current
  target row is not the relevant producer.

Run one fresh Debug build and one concurrent silent/image port pair with a
bounded witness at the preceding setup edge of `0x8008F2CC`. Keep the existing
whole-route, title 1024, hangar 512, non-target writer-state, audio-ABI/DMA,
image-stage, and PCM controls. Capture the first setup instruction that writes
or loads the divergent `s1/t0/t1` state, then compare it with the existing
caller and entry rows. If the new edge supplies the state, select
`H-PortEarlierSetupProducer`; if it matches the retail tuple until that edge,
select `H-PortSetupCallerContract`; if controls or target rows disappear,
mark unevaluable. Do not change waits, slots, dispatch, clear behavior, or PCM
writeback.

Use `cmake --build build --config Debug --target RogueSquadron64Recomp` and
extend `scratch/agent/run_s3423_m5_writer_setup.sh` with the new preceding-edge
witness. The prior independent retail control is
`scratch/agent/s3423_groundtruth/oracle_narrow.log`; its positive control and
target write fired, but it did not produce a phase-qualified field summary.
