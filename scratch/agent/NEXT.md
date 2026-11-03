# NEXT: which RT64 writeback first carries the abort wipe, and from what input?
HYPOTHESIS-ID: g3-wide-abort-wipe

State (s6843): the 4:3 abort wipe is in port RDRAM and rt64_writeback is its only writer (store watch + memset positive
control). The decoded gfx stream is x-invariant across the wipe (paused scene; only the full-screen pause-dim overlay prim
alpha 0x80 -> 0 changes). RT64 does 3 colour writebacks per swap per fb ([wbcol]: rows 200-448 rect 256-512, rows 0-448,
rows 0-447).

Hypotheses:
- H-rt64: RT64 creates the edge from state outside the commands (fb-pair re-upload from RDRAM, a stale/partial render target,
  a resolve/rect logic bug) -> the black first appears in a writeback whose RDP segment has no new draw.
- H-stream-gap: RT64 executes commands RS64_RDP_BIN_PORT does not record (second submit path, merged [dpc-merge] lists)
  -> RT64's own per-draw log shows a draw near the right edge that port.bin lacks.
- H-retail-same: the retail wipe is made the same way by real RDP commands we are mis-decoding -> compare the retail rdplog
  (tools/g3_rdp_frame_match.py inputs) for the same VIs.

Discriminator, ONE port 4:3 run (scratch/s6843/port_abort.sh <tag> "<env>"):
  extend ROGUESQ_WB_COL_PROBE in lib/rt64/src/hle/rt64_state.cpp to log, per writeback of 0x620000/0x690000, the pre/post
  16-bit VALUES at (row 224, col 100/300/480/510) plus the framebuffer-pair index and the RDP command index range of that
  pair (then ./submodule-patches/export.sh + commit). Positive control: col 100 must change with the pause-dim fade.
  Outcome: black at col 480 appears in writeback k of swap 3734 -> dump the commands of that pair from port.bin
  (tools/rdp_bin_cmds.py); if the pair has no right-edge draw -> H-rt64 (read RT64's fb-pair/re-upload path for that pair);
  if RT64's own draw log (RT64 per-call rect) shows a draw port.bin lacks -> H-stream-gap.
Budget: this slug has 2 iterations; s6843 discriminated (H-rdram refuted). If the next one does not select H-rt64 vs
H-stream-gap, park the thread (cosmetic abort transition, wide-only symptom) and take the next ladder rung.
