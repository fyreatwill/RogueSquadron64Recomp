# Next work unit

HYPOTHESIS-ID: guest-2vi-wait

s4915 result: flag A is skipped-clear at the first retrace exactly when bufferArbiterAllocSlot(1) (0x8001BF20) returns 0 (28/28 two-recv calls; 156/156 one-recv calls return nonzero). Slot bytes differ: ret-0 has +2,+3 = 04 05 / 05 04 and +6,+7 = 01 02; ret-nz has +2,+3 = 00 05 / 05 00 and +6,+7 = 00 01.
Hypotheses: H-prev-frame-dl-still-running (slot held until the previous frame's RDP/SP-done event, which our host delivers a retrace late), H-host-timing-only (retail also needs 2 VIs), H-wrong-release-path (a guest releaser we stub/skip never runs the first time).
ONE build, one run: extend the poll thread to log every change of bytes 0x80128EA8..B7 with last guest mark/tid (positive control: ret-nz acquire must show a +2/+3 change), plus marks at the releaser candidates found by statically grepping writers of the slot-byte base in funcs_*.c. Decode bufferArbiterAllocSlot (0x15C bytes) first so the table is keyed by slot index.
Outcome: releaser runs on the gfx/RDP-done path late => compare timing with oracle/host event; releaser never runs first time => stubbed/skipped function; both retail-like => 2-VI wait is genuine and not a bug.
If stalled, resume the M5 audio plan.
