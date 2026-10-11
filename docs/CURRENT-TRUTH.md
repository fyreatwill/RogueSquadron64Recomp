# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
history migrated to [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) §59 and earlier
archive sections. Updated for session 4622.

## Current state

The qualified native route boots through attribution, N64 logo, intro
cinematic, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) on the real-audio/LLE/ungated/solo/spin-yield route. Retail RDP
is obtainable: hangar frame data is about 1244 triangles and 205 KB RDP.
Port hangar geometry and colour artifacts remain localized; the entry frame is
nearly complete, with a rim band, blue holo spikes, and right-edge garbage.

Audio is no longer a zero-output stub on that route. Fresh 7F saves produce
nonzero PCM, AI byte order is fixed, and title AI buffers match ucode output.
MusyX/MORT remains only partially de-stubbed and must not reach stock
`aspMain`. M5 audio plan steps 1–10 are closed or conditionally unnecessary.

Full regeneration remains unsafe since s4204: the newer N64Recomp followed by
`fixup_game_funcs.py` aborts at the E088 anchor and may clobber generated
functions. Use the existing `tools/apply_s*.py` workflow unless that failure
is explicitly repaired.

## Active frontier

The all-phase retail five-name census is complete. The target span contains
five stable records in title and hangar snapshots, but the candidate source
span and its 17 visible pointer targets do not. The live immediate writer is
`0x80007670`; its 76 lifetime target-span writes produced zero rows in every
requested 320, 640, title-1024, attract/demo-512, and hangar-512 bucket. The
whole-RDRAM, target-span, `0x80007640`, and `0x80007670` controls all fired,
so this is a qualified single-source oracle result selecting
H-no-live-copy provisionally: the names predate the covered route or arrive
through an unarmed earlier/alternate path. No mitigation is authorized.

The recurring odd PI DMA remains an explanation problem, not a skip target.
The port writes ASCII `lcre` into a cart record through the FE98 path, while
retail writes B0xxxxxx pointers in the corresponding target range. The bad
caller input is the `0x800903F0` render path reading `late` from voice `+0x34`.
The allocator/count-32 and audio-list ownership chain is open; the writer
and legitimacy of any wild value must be named before a guard is considered.

The s4619 route qualification reached the required hangar origin on both
arms: the port logged 512-wide `0x006AB400`, while retail independently logged
the same origin and its whole-RDRAM positive control retained 10,000 hits.
The port M4 instrument emitted origin-change summaries for both transient and
hangar origins but zero accumulator rows, including zero rows at
`0x006AB400`. Because the M4 instrument has no same-run positive control, this
is an instrument-boundary null, not evidence for arithmetic, VGE/store, or
source divergence. The paired discriminator remains unevaluable.

The s4620 M4 capture qualified the instrument's stage-1 positive control: 64
rows fired with changing accumulator state. The target stages also fired (519
rows each for stages 10–12 and 491 stage-13 rows), but all rows were phase 3
(transient 640), with no hangar-phase row. The retail oracle independently
passed its whole-RDRAM control (10,000 callbacks) but reached title 1024 and
not hangar in its 60-second arm. The s4621 repeat emitted 2,112 target rows,
but the known odd-physical-address PI abort occurred before a hangar row. The
M4 arithmetic/VGE/store/source discriminator is therefore still unevaluable
after four consecutive attempts; no arm selected a hypothesis.

Session 4622 audited both PI guest entry arms and the converged `do_dma` path
with one batched trace. The real-audio/LLE route reached title 1024 but not
hangar in 75 seconds: all 16 retained rows were even, from `osPiStartDma` and
matching `do_dma` calls; `osEPiStartDma` and odd events were absent. The retail
oracle independently passed its whole-RDRAM control (10,000 callbacks) but
stayed at 320-wide boot. This is a qualified single-source port result, not a
global null for the earlier odd request.

## Parked and closed

- The M3 `jal rs_free` idiom audit is closed through s4502. The separate
  `attachedMeshOverlayNpcHandler` NULL/free gap at `0x80054344` remains open.
- The wild-width writeback is a named garbage-region SETCIMG writer; do not
  add a skip without a new origin proof.
- VI-640 crash families and broad M3 guard classes are parked. A mitigation
  needs an `ORIGIN:` line naming the writer and whether the value is
  legitimate.
- External retail-entry and M4 accumulator-origin boundaries are parked until
  a new attributable handoff or live target-phase control exists. The M4
  thread must pivot to the odd-PI origin before another target-phase run.
- The s4622 producer null is qualified only for its title-only route; repeat
  the audit on the canonical hangar schedule before interpreting it.
- M3 patch-runtime qualification is blocked on `mips64-elf-gcc`,
  `mips64-elf-ld`, and `PatchesLib`.
- Generated-symbol renaming is fallback work only after the active M5/M3
  frontier is inapplicable; it does not reset the engineering-change gate.

## Superseded conclusions to avoid repeating

- `0x80007640` is not the live target writer; `0x80007670` is. The former is
  retained only as a same-run execution control.
- The five records are not in the flat `0x165D9C` source span or its 17
  visible pointer targets. Derived or alternate sourcing remains open.
- The odd DMA is not established as an audio-mixer-thread issue. Instrument-
  free arms still reach the `pi.cpp` odd-address assertion, and the bad call
  was issued by tid 1.
- The count-32 voice case is not explained by a simple bad index or an
  inert chunk-2 record. Those interpretations were tested and closed.

## Next steps

1. Repeat the complete odd-physical-address PI-DMA producer audit on the
   canonical autopilot route that reaches `0x006AB400`; retain the s4622
   entry/convergence trace and compare any odd event with a retail physical
   watch. This is an origin audit, not permission to skip or align the DMA.
2. Re-run the M4 capture only after the odd-PI audit supplies a stable,
   attributable route that reaches `0x006AB400`; retain the stage-1 positive
   control and do not interpret transient phase-3 rows.
3. Revisit the external retail-entry boundary only with a new attributable
   handoff; do not repeat the now-qualified all-phase name-copy null.
4. Keep M5 de-stubbing and M3 idiom audits ahead of generated-symbol naming.

## Evidence and operating rules

Retail oracle watches are physical-address ground truth. Whole-RDRAM, VI,
target-PC, and adjacent-range controls must qualify every null. Phase-gate
animated comparisons on VI transitions. Batch all counters and A/B arms in one
build/run. Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. Keep safety guards separate from explanations.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake`; never hand-edit generated functions for behavior. If `lib/` changes,
export submodule patches in the same session. Never run submodule update,
checkout, clean, or hard reset. Kill runs with SIGKILL and run from `build/`
with the ROM present. Any mitigation-shaped change needs an `ORIGIN:` line.

See [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) §59 for the s4590–s4617
evidence archive and [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md) for the audio plan.
