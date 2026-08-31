# M5 Session 3424 — first divergent writer setup state

The fresh Debug build added a bounded, regeneration-safe witness at the five
setup instructions immediately before the target `jal 0x800078E0` in
`allocateSongChannelArray`. The concurrent silent and Factor 5 image arms both
reached the qualified hangar phase and fired the positive controls:

| arm | phase rows | setup-step | target setup | ABI/DMA | image-stage | crash/abort |
|---|---:|---:|---:|---:|---:|---:|
| silent | 134 | 5 | 4 | 1189/1189 | 0 | 0/0 |
| image | 148 | 5 | 4 | 1188/1188 | 4833 | 0/0 |

All five observed setup steps in both arms already had the port tuple
`s1=0x5622`, `t0=1`, `t1=0`, `ra=0`, beginning at `0x8008F2A8` and remaining
unchanged through `0x8008F2C8`. The target caller rows and `rs_memset` entry
retained that tuple. The independent retail control had the target tuple
`s1=0x561F`, `t0=0x2000FF01`, `t1=0x8010FEF8`, `ra=0x8008F2D4`.

This selects `H-PortEarlierSetupProducer`: the divergence predates the first
instrumented setup instruction in `allocateSongChannelArray`. It refutes an
internal setup instruction among the five observed edges and the host-wrapper
state explanation at this target call. It does not identify the upstream
caller or establish whether the divergent state is legitimate; no audio
behavior changed.

Evidence: `scratch/agent/s3423_m5_writer_setup/driver.log` and the two arm
logs in that directory. Independent positive-control evidence is
`scratch/agent/s3423_groundtruth/oracle_narrow.log`.
