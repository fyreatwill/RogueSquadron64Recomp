# NEXT work unit (s1968) — hangar hologram-beam artifact: writer vs stale-read

HYPOTHESIS-ID: hangar-hologram-beam-artifact

## What s1967 found

Extended `rs64_m4_y8000_flush` (`src/rsp/dpc_bridge.cpp`) to check
`YH<=YM<=YL` ordering and degeneracy on EVERY flushed `0xC8`-class Fill
Triangle in the hangar/512 gate, not just the (closed) M4 Y=`0x8000`
subset. Result, captured in
`scratch/agent/soak_results/s1968_hangar_tri_dump_20260818-085342/run.log`:

- `tri_degenerate` stayed 0 throughout — no zero-height triangles.
- `tri_order_bad` reaches exactly 1 per gate-window across most of ~700
  sampled heartbeats in the ~4s hangar capture. Always the SAME
  pattern: one command at a variable offset in `0xE80-0xEA8` (about
  nine 32-byte slots past the flush region's start at `0xD60`), header
  byte varying frame to frame but always validly `0xC8-0xCF`, with
  `YL`/`YM`/`YH`/edge fields at implausible magnitudes (thousands of
  pixels as signed s10.2) and a real ordering violation.

This did NOT select H2. Two explanations survive and the current
instrument can't split them:
- (a) a genuinely malformed/corrupted triangle command reaches the RDP
  queue for this draw (real H2, and plausibly the visual spike defect).
- (b) the scanned range `[0xD60, end)` — `end` derived from the `r16`
  write-pointer at flush time — includes bytes past what this frame
  actually wrote. If `r16` ever advances further than real stores (a
  narrower, previously-untested claim; `docs/M4-ACCUMULATOR-GROUND-
  TRUTH.md`'s H-dead-store refutation covered the 640-attribution case,
  not this later multi-triangle-per-flush hangar case), the walker
  would read stale leftover bytes from a differently-shaped earlier
  command and misinterpret them as a new triangle header purely by
  chance landing in `0xC8-0xCF`.

ORIGIN not named (ambiguous between writer and stale-read) — iron rule
11 blocks any mitigation until this is settled. Do not add a skip/guard
for this offset without first doing the check below.

## Discriminating measurement to build next

Tag the DMEM scratch region so a stale read is directly distinguishable
from a fresh write:
1. Immediately after each `SP_WR_LEN` DMA that drains `[0xD60, r16)`
   (the same site `rs64_m4_y8000_flush` is called from), memset the
   drained range to a fixed sentinel byte (e.g. `0xEE`) BEFORE the next
   frame's restage writes begin. This requires finding the actual
   drain/reset point in the generated ovl20 `L_112C`-equivalent flush
   path (see `docs/M4-ACCUMULATOR-GROUND-TRUTH.md` for the site names)
   or, more simply, sentinel-fill the buffer once at hangar-gate entry
   and re-fill everything up to the PREVIOUS frame's `end` right after
   each flush is processed — either gives the same discriminating
   signal.
2. In `rs64_m4_y8000_flush`, when a `tri_order_bad` hit is found, check
   whether the bytes at that offset still carry any sentinel byte in a
   position `L_17F0` would have overwritten if a real store happened
   this frame (e.g. the unused padding byte at `off+1`, which `L_17F0`
   per s1840 does not write). Sentinel present == (b) stale-read
   confirmed, no writer bug. Sentinel absent == real bytes were stored
   here this frame == (a) selected, promote to a "who wrote this
   specific offset" hunt (watch DMEM `0xE80-0xEA8` writes directly with
   an `RSP_MEM` write-side hook, restricted to the hangar gate).
3. Same-run positive control: a deliberately UN-drained slot (or the
   known-good `0xD60` triangle in the same flush) must show sentinel
   absent, proving the tagging mechanism actually marks fresh writes.

Run with the existing hangar recipe (`scratch/agent/soak_queue/done/
s1950_hangar_yield_repro_*.sh` as template, add
`ROGUESQ_LOG_M4_TRI_DUMP=1`). Same ~4s window budget; do not expect the
crash timing to change.

## If this doesn't discriminate cleanly in one session

Per iteration budget rule 8: this is the SAME hypothesis thread as
s1967 (not yet a 3rd stalled iteration on it — s1967 was the first). If
s1968 also comes back ambiguous, write the hypothesis/evidence table
explicitly into this file and consider the fallback: an H1 probe
(census every `SETOTHERMODE_L/H_EX` in the hangar window's flushed
stream — different instrument, same buffer) since H2's own instrument
has now been tried once without a clean answer.

## Do not repeat

- Do not conflate this with the closed M4 Y=`0x8000` accumulator
  question (`y8000_any=0` again this session) — different mechanism,
  different offset, do not re-walk VMADH/VGE.
- Do not point the oracle at DMEM `0xD60` — confirmed s1967 the
  RSP-HLE plugin never executes guest `L_17F0`, so there is nothing
  comparable to watch there.
- Do not land a skip/guard for the `0xE80-0xEA8` offset without first
  running the sentinel check above — that would be exactly the
  mitigation-without-explanation trap iron rule 11 exists to block.
- Do not resume the generated-symbol sweep (closed, 57 RE/hold left,
  s1966).
- Cross-run A/B on this scene without phase-gating still forbidden —
  the hangar window is ~4s of animating content.
