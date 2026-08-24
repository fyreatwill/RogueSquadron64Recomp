# NEXT work unit (s2309) — dynamic-ring zero-fill ground truth

HYPOTHESIS-ID: m5-dynamic-zero-fill-retail-provenance

## Work unit

Ask the retail oracle for ground truth first, then run one phase-gated
same-run port/retail capture using the existing PCM writer provenance. Keep
the whole-ring port table and discover the current nonzero image-stage
destinations from the port log; do not assume `0x167650`/`0x167950` or any
other fixed pair. Arm the oracle's whole PCM ring (`0x166450..0x169450`) as
the phase writer/post-value watch so the retail result covers whichever slots
the port selects. Keep the title/hangar gates, 45-second retention, positive
controls, and SIGKILL cleanup. No runtime behavior or mitigation change.

## Competing hypotheses and discriminating measurement

- H-StableImageDmaZeroFill: the later zero PCM rows are a normal repeated
  image-DMA output for rotating ring slots. Retail's ring-wide phase writer
  and post-value summaries show the same slot activity and zero/nonzero
  polarity as the port's exact stage→PCM→zero sequence.
- H-PortOnlyZeroFill: the port image arm emits the later zero rows, but retail
  does not write the dynamically selected slots with the same zero polarity or
  ordering. This points to a port-side contract divergence, not a generic
  silence writer.
- H-SlotRotation: the apparent overwrite is only a slot-selection artifact.
  The dynamic port stage destination, PCM destination, and retail writer
  bucket do not remain the same physical ring role across the joined rows.
- H-CoverageInvalid: the whole-RDRAM control, title/hangar origins, ring-wide
  writer control, or port title/hangar/retention gate fails.

The discriminator is one complete table keyed by dynamically discovered
destination, with port stage event/FNV/nz, first exact PCM source/consumer
event/FNV/nz, first later zero PCM event, image-DMA writer sequence/class, and
the retail ring-wide writer PC/count/post-value FNV/nz for the same physical
slot. A positive control must pass in the same run before any null is read.
The outcome must select one hypothesis at this capture scope; it must not
authorize writeback, a writer guard, slot guard, consumer change, address
remap, or a default change.

## Exact commands

1. Ground-truth preflight and ring-wide recipe check:

   `grep -a -E 'positive-control threshold|watch write \[0x00166000|watch write \[0x00167650|watch write \[0x00167950|origin=0x00790400 width=1024|origin=0x006ab400 width=512|writer-pc-phase origin=0x006ab400 width=512' scratch/agent/s2308_m5_pcm_writer_provenance/oracle.log | tail -100`

   The new oracle recipe must include `--watch-write 0x0:0x800000`,
   `--watch-write 0x166450:0x169450`, `--pc-hist-watch 1`,
   `--pc-hist-phase 0x006AB400:512`, and `--post-value-watch 1`, with the
   ring watch after the whole-RDRAM control. Require whole-RDRAM `10,000`,
   both VI origins, and a nonzero ring-wide writer/post-value control before
   adding or interpreting any port row.

2. Reuse the qualified build and existing writer hooks; if the driver needs
   changes, create `scratch/agent/run_s2309_m5_dynamic_zero_fill.sh`, then:

   `zsh -n scratch/agent/run_s2309_m5_dynamic_zero_fill.sh`

   `zsh scratch/agent/run_s2309_m5_dynamic_zero_fill.sh`

3. Report the dynamic-slot table, the retail ring-wide writer/post-value
   summaries, all positive controls, and the selected hypothesis. Do not
   treat a fixed-slot null as evidence when the port's nonzero stage pair has
   rotated.
