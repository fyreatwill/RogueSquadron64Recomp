# NEXT work unit — qualify the allocateSongChannelArray caller boundary

HYPOTHESIS-ID: m5-port-setup-state-producer

Session 3424 selected `H-PortEarlierSetupProducer`: both port arms already had
`s1=0x5622`, `t0=1`, `t1=0`, `ra=0` at the first observed setup edge
`0x8008F2A8`, unchanged through `0x8008F2C8` and the target entry. Retail
target rows remain `s1=0x561F`, `t0=0x2000FF01`, `t1=0x8010FEF8`,
`ra=0x8008F2D4`.

Competing hypotheses and the single discriminating measurement:

- `H-UpstreamCallerContract`: `allocateSongChannelArray` entry already has the
  port tuple, so the divergence is supplied by its caller or dispatch contract.
- `H-InternalMallocReturn`: entry matches retail, and the tuple diverges after
  the first `rs_malloc` return at `0x8008F2A0`.
- `H-SetupMissing`: entry/return controls or target rows disappear, so this
  boundary is unevaluable.

Run one fresh Debug build and one concurrent silent/image port pair using
`scratch/agent/run_s3423_m5_writer_setup.sh`, extending its same bounded
witness with `allocateSongChannelArray` entry and return-from-`rs_malloc`
(`0x8008F2A0`) rows. Keep the existing whole-route, title 1024, hangar 512,
non-target writer-state, audio-ABI/DMA, image-stage, and PCM controls. If entry
already has the port tuple, select `H-UpstreamCallerContract`; if entry matches
retail and `0x8008F2A0` is the first divergence, select `H-InternalMallocReturn`;
if controls or target rows disappear, select `H-SetupMissing`. Do not change
waits, slots, dispatch, clear behavior, or PCM writeback.

Use `cmake --build build --config Debug --target RogueSquadron64Recomp` and
extend `scratch/agent/run_s3423_m5_writer_setup.sh` with the new preceding-edge
witness. The prior independent retail control is
`scratch/agent/s3423_groundtruth/oracle_narrow.log`; its positive control and
target write fired, but it did not produce a phase-qualified field summary.
