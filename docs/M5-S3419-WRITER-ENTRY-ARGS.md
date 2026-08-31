# M5 Session 3419 — writer-loop entry arguments

The fresh Debug build ran the silent and Factor 5 image arms concurrently with
the same phase-qualified controls. Both arms reached title VI 1024 and hangar
VI 512, and both emitted the writer-entry positive control. Neither arm
crashed or aborted.

In the hangar bucket, both arms recorded the same target-span entry:

    target=1 phase=5 width=512 origin=0x6AB400
    a0=0x801797B0 a1=0x00000000 a2=0x298 v0=0x801797B0

The target predicate is the physical span 0x1797B0:0x179A48; v0 is the first
loop address computed as a0 + 0. The entry-control rows also fired in both
title and hangar buckets, proving the witness was live on ordinary
phase-qualified calls. The image arm had 1,213 audio ABI/DMA rows and 4,909
image-stage rows; the silent arm had 1,214 ABI/DMA rows and no image-stage
rows, as expected. PCM remained zero in both arms.

This selects H-PortEntryArgsZero for the observed target call: the port enters
the writer with a zero fill value and the known 0x298 target length. It refutes
H-PortEntryArgsMatch at this boundary. The saved return register was zero in
the generated host call, so the witness does not classify the caller route;
H-PortRouteMismatch remains open. The independent retail control from Session
3418 showed nonzero target-span stores from 0x800078EC; a like-for-like retail
entry tuple is still required before claiming the port zero is illegitimate or
naming the missing producer.

Source logs: scratch/agent/s3411_m5_downstream_join/{silent,image}.log.
