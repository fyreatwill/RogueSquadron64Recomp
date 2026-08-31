# M5 Session 3421 — writer-loop state witness

The independent retail preflight passed the whole-RDRAM positive control and
observed 3,230,451 executions at `0x800078EC`. Its exact target-span capture
also passed with 1,166 writes. The retail field witness showed the ordinary
512-byte loop entering with `s0=a0`, `s1=0x18`, and the loop advancing `v0`
from `a0`; this is the positive ground-truth shape for the new port probe.

The regeneration-safe port witness was installed by
`tools/apply_s3421_m5_writer_state.py` and built cleanly after correcting one
format-argument warning. Silent and Factor 5 image arms ran concurrently.
Both reached title 1024 and hangar 512, and both had the new witness live:
72 writer-state rows, 2 writer-entry control rows, 1,216 audio ABI/DMA rows,
and no crash or abort. The image arm had 4,942 image-stage rows; silent had
zero, confirming the arms remained distinct.

At the first target store in both port arms the tuple was identical:

    a0=0x801797B0 a1=0 a2=0x298 ra=0
    t0=1 t1=0 s0=0x12 s1=0x5622
    v0=0x801797B0 v1=0 pred=1

The bounded target rows then advanced `v0` and `v1` normally. The probe's
non-target control rows independently showed `s0=a0` and `s1=a2`, so the
state witness is live and distinguishes the target call from a normal loop.

This selects `H-PortWriterStateDiffers` at the observed port target boundary
and refutes `H-PortWriterStateMatches` for the measured port-vs-retail
control shape. It does not identify whether `s0=0x12`/`s1=0x5622` is caused by
the caller contract or by host recomp register setup, and it is not a license
to synthesize or overwrite those registers. The next probe should capture a
like-for-like retail target row or move to the publication boundary.
