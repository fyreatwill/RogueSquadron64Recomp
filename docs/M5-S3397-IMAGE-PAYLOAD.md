# M5 s3397 — image payload checkpoint

The independent retail oracle was rebuilt so its live SIGUSR1 checkpoint also
reports post-store words, then run with the whole-RDRAM positive control,
title/hangar phase gates, four candidate destination watches, and the
`0x800078EC` writer filter. The positive control reached 10,000 callbacks and
the title and hangar phases were both observed.

At the checkpoint, retail had 16 writes each to `0x166D50`, `0x167050`, and
`0x167350`, but no post-value samples for those three watches. Retail had 36
writes to `0x1935E0`; 18 post-value samples were retained, including 12
nonzero words from `0x800078EC` and 4 zero words from that PC. This is
single-source ground-truth evidence for a nonzero stage-3 publication at the
retail candidate destination.

The paired port build reached title and hangar in both concurrent arms with no
crash or abort. The silent arm had 678 ABI/DMA rows and no image-stage rows.
The image arm had 673 ABI rows and 2,740 image-stage rows. Its stage-2 rows
for the candidate destinations were zero-valued (`FNV=F59C39C5`, `nz=0`), and
its stage-3 publication was predominantly to `0x178D80` (651 rows), not the
retail candidate `0x1935E0`; the two observed `0x1935E0` rows were also zero.
PCM remained zero in the image arm. These are two independent lines of
evidence and select `H-ImageEdgeMissing` for the observed stage-3 publication
contract. This does not yet identify why the port destination differs or prove
that the stage-2 zero publication is illegitimate.
