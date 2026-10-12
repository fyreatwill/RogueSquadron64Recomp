# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
history migrated to [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) §59 and earlier
archive sections. Updated for session 4629.

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
The s4620 M4 capture qualified the stage-1 control but exhausted its
run-lifetime target cap in transient phase 3; that null was invalid for the
hangar discriminator. The corrected s4626 capture set
`ROGUESQ_M4_PHASE_FROM=5`: the stage-1 control fired 64 rows, hangar phase 5
produced 517 rows each at stages 10–12 and 497 stage-13 rows, and the port
remained crash/abort free. The independent retail oracle reached hangar and
its whole-RDRAM control hit 10,000. A local reconstruction matched VMADH for
all 4,128 paired lanes with zero mismatches; 31 lanes changed between
post-VMADH and post-VGE. This is single-source port evidence selecting the
VGE/store boundary arm, not a retail arithmetic proof. Artifacts are in
`scratch/agent/s4626_m4_accumulator_boundary_fixed/`.

Session 4622 audited both PI guest entry arms and the converged `do_dma` path
with one batched trace. The real-audio/LLE route reached title 1024 but not
hangar in 75 seconds: all 16 retained rows were even, from `osPiStartDma` and
matching `do_dma` calls; `osEPiStartDma` and odd events were absent. The retail
oracle independently passed its whole-RDRAM control (10,000 callbacks) but
stayed at 320-wide boot. This is a qualified single-source port result, not a
global null for the earlier odd request.

Session 4624 repeated the batched audit on the canonical hangar schedule. The
retail oracle whole-RDRAM control reached 10,000 callbacks but stayed at title
1024, while the port reached repeated hangar VI `0x006AB400` at width 512 and
ran through the 100-second watchdog. The port emitted 16 even
`osPiStartDma`/`do_dma` pairs and zero odd events, including in the hangar
phase. This is a qualified hangar-route single-source null: it does not select
the guest, host-corruption, or stale-record hypotheses, and does not explain
the separate recurring odd request.

Session 4625 extended the same canonical route past the first hangar phase for
120 seconds. The port again reached hangar and retained 16 even
`osPiStartDma`/`do_dma` pairs, with zero odd events anywhere in the extended
route. The independent retail oracle passed its whole-RDRAM control at 10,000
callbacks (but remained at 320-wide boot). This is a qualified port null for
the post-hangar-trigger hypothesis and provisionally selects a missing-trigger
or alternate-route explanation for the separate recurring odd request; it is
not evidence that the odd request is globally impossible. Artifacts are in
`scratch/agent/s4625_post_hangar/`.

Session 4627 requalified the M4 port arm with the stage-1 control and
phase-5 target budget: 64 control rows and 517/517/517/497 rows at stages
10/11/12/13. The corrected retail Rice oracle independently reached the
512-wide `0x006AB400` hangar origin and its whole-RDRAM control reached 10,000
callbacks. The apparent stage-13 `record=` bytes are not usable store
evidence: `r9` is the DMEM record base (`0x670..0x6C0`), but the probe reads
`rdram[r9+0x18]`. This selects H-instrument-boundary for the store
discriminator; no VGE/store conclusion is advanced beyond s4626's
single-source VGE-boundary selection.

Session 4628 repaired the store witness (probe now reads RSP DMEM with `^3`
byte lanes) and re-ran the same port route: counts 64 / 517 / 517 / 517 / 497
reproduced. In 488/488 well-formed stage-13 rows v6 lanes 0-2 and 4-6 sit in
the DMEM record at the expected offsets and equal the post-VGE lanes, so the
store/writeback arm is refuted on the port (single-source; lanes 3/7 are
overwritten by design). Surviving arms: VGE semantics vs. upstream operand
(v0/v4) source. Artifacts: `scratch/agent/s4628_m4_dmem_store/`.

Session 4629 closed the VGE arm offline: `RSP::VGE` is a pure `max_signed`
(VCO cannot change the output value), and across 4,112 stage-11->12 lanes only
29 change, all negative->0 clamps. Arithmetic (s4626), store (s4628) and VGE
are all closed on the port; only H-source (upstream v0/v4 / pre-VMADH
accumulator inputs) survives. Single-source.

Session 4630 added DMA-source and loop-head operand probes (Fixup 22) and a
four-arm retail peek. The stage-10 vertex input is RDRAM `0x720320`+ (DMA to
DMEM 0x280, task 1169); 13 sampled blocks (56 words) equal retail at hangar
with zero diffs. Vertex content is therefore not the divergence; the matrix
span (`0x700000/40/80`, dynamic in retail) is the remaining RDRAM-visible
operand and is not yet compared byte-for-byte. Artifacts:
`scratch/agent/s4630_m4_operand_source/`.

Session 4631 compared the matrix span against retail: 0x700000..3C (DMEM 0x590)
is byte-identical (retail 24 samples, 1 value; port 6 reads, same value). The
per-object matrices at 0x700040+ animate in retail itself (35-67 distinct
values), so cross-run equality is not a valid test; they stay unqualified.
Artifacts: `scratch/agent/s4631_m4_matrix_span/`.

Session 4638 (single-source, controlled): CPU store watch on the hangar buffer
0x656400 saw no nonzero-valued store to col 511 at width 512 (body stores and
a zero-fill clear at pc 0x800078EC fired as controls) while the col-511 noise
persisted. H-cpu is out; remaining H-rdp-host / H-dma / H-stale. See
`tools/apply_s4638_edgewatch.py`, `scratch/agent/s4635_w38d/`.

## Parked and closed

- The M3 `jal rs_free` idiom audit is closed through s4502. The separate
  `attachedMeshOverlayNpcHandler` NULL/free gap at `0x80054344` remains open.
- The wild-width writeback is a named garbage-region SETCIMG writer; do not
  add a skip without a new origin proof.
- VI-640 crash families and broad M3 guard classes are parked. A mitigation
  needs an `ORIGIN:` line naming the writer and whether the value is
  legitimate.
- External retail-entry remains parked until a new attributable handoff. The
  M4 accumulator-origin boundary is eligible again because s4625 qualified a
  stable hangar route and retained the stage-1 control.
- The s4622 producer null was title-only until s4624. The extended s4625
  canonical hangar route also had no odd event, so the post-hangar trigger is
  ruled out for this route; the recurrence remains a missing-trigger or
  alternate-route problem, not evidence that the odd request is impossible.
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

1. M4 RSP thread is closed (s4634); s4635 showed the right-edge garbage is not
   tri-submit. s4636 (`ROGUESQ_EDGE_DUMP=dir`, 4 runs, ~640 dumps) selects
   H-rdram: in the 512x16bpp hangar colour image, column 511 holds per-frame
   noise (110-126 distinct values over 240 rows) in buffer 0x00656400 in 4/4
   runs, and is zero in buffer 0x006AB400; columns <=510 are normal. Screenshot
   bimodality plausibly = which buffer is on screen (mapping single-source,
   dumps not frame-synced to screenshots). Next: name the WRITER of
   0x656400 + 1022 + 1024*row (RT64 RDRAM writeback vs recomp CPU/RSP/RDP
   code); see scratch/agent/NEXT.md.
   s4637: NOT RT64 colour writeback (ROGUESQ_NO_WB_W=512 zeroes buffer
   0x6AB400 as control, yet 0x656400 col 511 stays noisy, 2/2 runs). Writer is
   CPU/RSP/RDP/other host write; next = store watch (NEXT.md).
2. Keep the odd-PI question parked as a missing-trigger/alternate-route
   problem; do not align, skip, or mitigate the DMA without a new trigger.
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
