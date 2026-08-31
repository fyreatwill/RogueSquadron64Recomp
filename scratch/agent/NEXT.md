# NEXT work unit — locate the first producer of target writer-state divergence

HYPOTHESIS-ID: m5-retail-target-writer-state

Session 3422 selected `H-RetailTargetStateDiffers` with the exact target-row
join: retail has `s1=0x561F`, `t0=0x2000FF01`, `t1=0x8010FEF8`,
`ra=0x8008F2D4`, while both port arms have `s1=0x5622`, `t0=1`, `t1=0`,
`ra=0`. Port `s0=0x12` matches retail.

Competing hypotheses and the single discriminating measurement:

- `H-PortSetupStateDiffers`: the differing state is established by the port
  guest caller/setup before `rs_memset`.
- `H-HostWrapperStateDiffers`: guest setup matches retail and the divergence is
  introduced by the host wrapper's call/register contract.
- `H-RetailTargetOtherWriter`: the apparent join is still wrong despite the
  current 664-row retail attribution.

Run one fresh Debug build and one concurrent silent/image port pair with a
bounded setup witness immediately before the `rs_memset` host entry. Keep the
existing whole-route, title 1024, hangar 512, non-target writer-state,
audio-ABI/DMA, image-stage, and PCM controls. Capture `s1`, `t0`, `t1`, `ra`,
and the target predicate at the last guest-side setup edge and at host entry.
If values differ before entry, select `H-PortSetupStateDiffers`; if they first
differ at entry, select `H-HostWrapperStateDiffers`; if target rows or the
writer edge disappear, mark the discriminator unevaluable and do not infer
from the null. Do not change waits, slots, dispatch, clear behavior, or PCM
writeback.

The prior retail command used whole-RDRAM and target controls plus
`--store-field-dump 1:0x800078EC`, with phase buckets
`0x006AB800:1024` and `0x006AB400:512`. The port command is
`env zsh scratch/agent/run_s3421_m5_writer_state.sh` after the fresh build,
extended with the new setup witness.
