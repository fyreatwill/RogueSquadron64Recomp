# NEXT work unit (s2308) — M5 PCM writer provenance for payload mismatch

HYPOTHESIS-ID: m5-payload-tuple-mismatch-provenance

## Work unit

Ask the retail oracle for ground truth first, then run one phase-gated
same-run port/retail capture that attributes the writer/caller for every PCM
source and consumer row whose physical destination is one of the two current
nonzero image-stage slots (`0x167650` and `0x167950`). Retain the image-stage
DMA tuple, task ordinal, global event, payload FNV/nonzero count, phase, and
the writer class for all target ring slots. Keep the qualified default image
arm, title/hangar gates, 45-second retention, and all passive controls. Do not
change runtime behavior or add writeback, consumer, slot, gate, guard, or
address-remap machinery.

## Competing hypotheses and discriminating measurement

- H-ZeroFillLegitimate: the same-destination zero-payload PCM rows are an
  intentional zero-fill or silence writer, and the nonzero image-stage output
  is a separate diagnostic overlap. Retail and port writer classes/ordering
  match this interpretation.
- H-ImagePublicationGap: the image-stage DMA produces the nonzero tuple, but
  the port's PCM destination is later zeroed or never published. The writer
  provenance shows a distinct zeroing/overwrite edge after stage DMA, while
  retail's corresponding target-slot writer is nonzero or differently ordered.
- H-RingAddressMismatch: the equal physical addresses are not the same logical
  ring role. Writer PCs, task ordinals, and phase transitions correlate the
  PCM rows with a different ring slot than the image-stage row.
- H-CoverageInvalid: the retail whole-RDRAM control, both title/hangar VI
  origins, a target-range writer control, or the port title/hangar gates fail.

The discriminator is one complete table covering every nonzero target image
stage row and every same-destination PCM source/consumer row, with columns
`phase,origin,stage_event,pcm_event,kind,dest,len,stage_fnv,stage_nz,pcm_fnv,
pcm_nz,writer_pc/writer_class,stage_before_pcm,retail_writer_class`. A positive
retail control plus a port writer control is required before any null is read.
The result selects one hypothesis at this capture scope; a writer/legitimacy
null is not permission to add a mitigation.

## Exact commands

1. Ask ground truth before changing the driver or adding an instrument:

   `grep -a -E 'positive-control threshold|watch write \[0x00167650|watch write \[0x00167950|origin=0x00790400 width=1024|origin=0x006ab400 width=512|writer-pc-phase origin=0x006ab400 width=512 watch=2|writer-pc pc=' scratch/agent/s2307_m5_cross_phase_join/../s2306_m5_temporal_recurrence/oracle.log | tail -100`

   Require the whole-RDRAM threshold, both VI origins, both target-range
   watch summaries, and the three existing target writer-PC controls. If any
   is absent, repair the oracle recipe before adding a port instrument.

2. Add one bounded writer/caller provenance field to the existing PCM/stage
   capture, keeping all existing controls and passive diagnostics. If a file
   under `lib/` changes, run `./submodule-patches/export.sh` and include the
   refreshed patch in this iteration. Build all required arms together.

3. Create/update `scratch/agent/run_s2308_m5_pcm_writer_provenance.sh`, syntax
   check it, and run the one capture:

   `zsh -n scratch/agent/run_s2308_m5_pcm_writer_provenance.sh`

   `zsh scratch/agent/run_s2308_m5_pcm_writer_provenance.sh`

   Use SIGKILL cleanup, run from `build/`, and report the complete provenance
   table and the retail/port positive controls before interpreting a null.
