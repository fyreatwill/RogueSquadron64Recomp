# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
history migrated to [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) §59 and earlier
archive sections. Updated for session 4679.

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
`aspMain`. Session 4676 created the required live inventory and incremental
plan in [docs/M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md). Session 4677 qualified the
Step 4 `0x80094648` boundary: both port arms reached title and hangar, matched
the retail `0x7F` channel-byte writer shape, kept the MusyX gate at `0x01`,
completed real-image tasks, and produced nonzero hangar PCM. This rejects gate
suppression for the covered route; no gate change was made. The next M5 unit
is Step 5's complete key-on early-return idiom audit. Session 4678 completed
that audit: all four executed divide sites received divisor `0xC0`, all eight
early-return guard counters were zero, the normal tail ran, and slot `0x02`/
`0x00` transitions fired in hangar phase 5. Retail's independent hangar route
reached `0x006AB400` with key-on entry/tail execution and no trap-PC hits.
This selects H-keyon-valid for the covered route, but no return was removed;
the next M5 unit is Step 7's status-03 service-reaping boundary.

Session 4678's hangar tables reached entry `12260`, normal tail `12259`, and
divisor `0xC0` at sites `0x80090CEC/0x80090D30/0x80090D74/0x80090DB8`;
sites `0x80090D04/0x80090D48/0x80090D8C/0x80090DD0` had zero divide and guard
rows. The run recorded 206 slot-`02` and 152 slot-`00` rows before SIGKILL
cleanup. Artifact: `scratch/agent/s4678_m5_keyon_port/`.

Session 4679 qualified the Step 7 route and controls: retail and port both
reached title `0x00790400` and hangar `0x006AB400`, and the retail
whole-RDRAM control reached 10,000 callbacks. Port phase 5 entered
`serviceVoicePoolFrame` 9,181 times, including 10 entries with table status
`03`; later reads of `D_80154620` observed status `00`. The worker therefore
is reached and status-03 is not persistent on this route, but the batch had
no exact status-zero writer attribution and no shutdown call-3 return marker.
This refutes H-status-unreached without selecting H-status-writer or
H-status-source; no wait change or forced clear is authorized. Artifact:
`scratch/agent/s4117_m5_status03_silent/`.

Session 4677 ran the corrected boot-relative Start-mash route after two shorter
recipe attempts stopped before title. Both arms reached title 1024 and hangar
512; the positive controls fired; each produced 30 `m5-94648` rows and 2
control rows, with hangar rows storing `0x7F` at `0x80141AD8..0x80141B08`.
Phase-5 gate rows showed gate `0x01`, real-image task rows showed exit/Broke,
DMEM/DMA activity, and PCM sanity was nonzero. Independent retail writer
evidence from sessions 4078/4166 supplies the second line. Both port processes
later aborted after the target window while leaving the route; that does not
invalidate the phase evidence. Artifact: `scratch/agent/soak_results/s4264_gate/`.

Session 4676 was design-only: it inspected the current dispatch arms, task
staging, DMEM ownership, wait gates, generated safety exits, and PCM handoff.
No build or runtime result was claimed.

Session 4671 restored the canonical full-section `load_overlays` registration
call to every ROM-to-RDRAM DMA in addition to the existing chunk-start helper.
This covers both complete overlay transfers and the game's fixed-size chunked
loads; the Debug executable rebuilt successfully. Runtime route qualification
is the next discriminator, so this change does not yet claim that H2 is proven.

Session 4672 ran the rebuilt macOS target with the canonical real-audio/LLE
configuration and `ROGUESQ_LOG_DMA=1`. The positive DMA control fired 6,853
rows; menu and cinematic transfers produced the existing start-match rows at
0x10C2D0 and 0x137580, but no full-range matcher row was observed. The run
reached VI 1024 and then VI 640, never the qualified 512 hangar origin, and
ended in `musyxSynthFrame_s4562_impl` with a bus error. The full-range matcher
has no independent positive-control counter, so its missing row is a
single-source, unqualified null: do not claim H1/H2 from it or remove the
call yet. Artifact: `scratch/agent/s4672_overlay_route/`.

Session 4673 added phase-scoped call/match probes to both overlay arms and ran
the same route for 100 seconds. The DMA positive control fired 6,871 rows;
both matcher arms were called. The full-range arm matched only boot sections
0/1, while the start arm matched menu section 3 at 0x10C2D0 and cinematic
section 4 at 0x137580. The section table independently gives those overlays
sizes 0x283F0 and 0xB810, versus the observed 0x4000 chunk transfers, so H2
is selected for the covered route: the loads are chunked and the start matcher
is the operative registration path. VI still reached 1024 then 640, not the
qualified 512 hangar origin, and the run crashed in `musyxSynthFrame`; this
does not claim overlay dispatch is the remaining route blocker. Artifact:
`scratch/agent/s4673_overlay_probe/`.

Full regeneration remains unsafe since s4204: the newer N64Recomp followed by
`fixup_game_funcs.py` aborts at the E088 anchor and may clobber generated
functions. Use the existing `tools/apply_s*.py` workflow unless that failure
is explicitly repaired.

Session 4674 completed the bounded M3 audit of every generated backward
self-referential `MEM_W(p, 0)` walk: 30 sites in 14 functions, independently
reproduced by a second exact scan. The sites are bounded table, sentinel list,
render-reference, or audio-list walks; no named writer was shown to publish an
invalid pointer. The existing heap-list guard probes supplied the positive
control. This is static evidence only: no guard or mitigation is authorized,
and the next M3 unit must be a different complete idiom class.

Session 4675 completed a fresh M3 census of backward loops containing a
non-self zero-offset pointer transition (`MEM_W(ctx->rN, 0)`). It found 399
sites in 22 files and 212 functions; 326 are already instrumented/guarded
regions, while the 73 untouched sites contain 71 explicit loop/sentinel or
count-bound transitions and two bounded `bcmp_recomp` loops. The same scan
located the existing `rs_malloc`, `buildHeapFreeList`, and
`coalesceFreeHeapBlocks` guard controls. No new named writer-to-noncanonical
path was found. This is static, single-source evidence only; no guard or
mitigation is authorized. Artifact: `scratch/agent/s4675_indexed_census.md`.

## Active frontier

Session 4649 qualified a safe regeneration repair harness: the vendored fixer
completed rc=0 against a clean `RecompiledFuncs.s4204-fresh` copy, and the five
target live-only arms (s4563, s4296, s4580, s4571c, s4572) matched the live
tag census. The first four are behavior-changing when their arm is active;
s4572 is diagnostic-only. Five residual tag-count differences are
diagnostic-only probe drift (s4079, s4084, s4323, s4329, and one s4560 gate),
so exact textual equality is not required. The live tree was not touched.

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

Session 4651 completed the queued M4 offline reconstruction. After grouping by
task, phase, and `r9`, 515 complete stage-10/11/12 triplets (4,120 lanes)
reconstruct with zero post-VMADH mismatches; both synthetic controls pass.
This refutes the remaining arithmetic arm H3 on the port. The requested join
to s4630/s4631 cannot be completed because those are separate animated runs
with disjoint task IDs and no shared frame/object/lane key. The independent
s4630 vertex comparison still disfavors H2, but H1 (dynamic matrix source)
remains unevaluable. No mitigation is authorized. Details:
`scratch/agent/s4649_m4_join.md`.

Session 4653 reran the qualified regeneration repair harness against a fresh
`RecompiledFuncs.s4204-fresh` copy outside the live external tree. The vendored
fixer returned rc=0 with `failures=0`; the positive-control census reported
`live=173`, `cand=174`, and exactly the five expected diagnostic-only
differences (`s4079`, `s4084`, `s4323`, `s4329`, `s4560`). The four
behavior-changing arms (`s4563`, `s4296`, `s4580`, `s4571c`) and diagnostic
`s4572` matched the qualified classification. This supports H1 and rejects
fresh-copy failure H3 and behavior-changing drift H2 for this copy. The live
generated tree was not touched. Artifacts: `scratch/agent/s4653_fixup.log`,
`scratch/agent/s4653_tagcmp.tsv`.

Session 4652 checked the available image and oracle artifacts for a retail
hangar pixel reference. Every matching PNG is a port soak output, including
the late hangar AB directories; retail artifacts are logs, tables, or memory
watches and contain no pixel capture. The M4 H-source thread is therefore
closed as unevaluable: this does not establish whether the remaining white
pillar stubs are a port defect. No runtime instrument or mitigation was added.

Session 4654 revalidated the attached-mesh overlay NPC NULL/free census against
the fresh s4204 generated copy and the independent `rogue_squadron64` symbol
notes. `attachedMeshOverlayNpcHandler` is present at `0x8005427C`, its action-2
loop frees `+0x1C` and `+0x20` without a NULL test, and the only matching
pointer writer is the two-iteration `rs_malloc(0x80, 0)` in
`dispatchOverlaySetupByParentAssetName`. Unmatched parent names and NULL parent
mesh paths skip that writer but still reach action 2; the decomp notes confirm
nine spawn sites and the same action contract. This reselects the static gap
hypothesis, but runtime pool occupancy and value legitimacy are still unproven,
so no guard or patch was added.

Session 4655 found that the queued `load_full_header_image` audit was already
completed in Session 3637, and the proposed fallback `freeLevelDatBuffers`
audit was already completed in Session 3638. Fresh-copy inspection reproduced
both recorded attributions and classifications. The broader M3 `rs_free`
campaign was closed at Session 4502, so no new M3 idiom unit was available;
the stale queue was reconciled without a build, runtime run, guard, or
mitigation.

Session 4655 ran the new attached-mesh runtime discriminator against retail.
The independent oracle whole-RDRAM control reached 10,000 callbacks and the
retail route reached 320, 640, and 1024-wide VI phases. `rs_free` executed
extensively, but `attachedMeshOverlayNpcHandler` at `0x8005427C` never
executed and no `rs_free` `prev_pc` fell inside its body. This selects H3
route-absent for the covered boot/title route only; it does not establish that
the handler is globally dead or that its NULL/free gap is harmless in a
mission. No guard or mitigation was added. Artifact:
`scratch/agent/s4660_attached_mesh_oracle.log`.

Session 4656 extended the independent retail oracle with repeated Start
presses through 180 seconds and watches on `attachedMeshOverlayNpcHandler`
(`0x8005427C`) and `rs_free` (`0x80001ACC`). The whole-RDRAM control fired
(hit output capped at 200), and the handler executed, but its first observed
rows were at 512-wide attract/demo origins (`0x00690800`, `0x00690400`, and
`0x00620800`) after the hangar route, not in a mission phase. `rs_free`
executed extensively, but this run did not provide a mission attachment
contract or a usable action-2 free classification. This is qualified
single-source evidence that the handler is not boot/title-only; it does not
select H1/H2 for a mission and does not authorize a guard. Artifact:
`scratch/agent/s4666_attached_mesh_mission/oracle.log`.

Session 4657 ran the prescribed mission-capable retail sequence with the
whole-RDRAM control, Rice video, VI tracing, and both execution watches. The
control fired 25,543 hits and retail reached 1024-wide title followed by
512-wide post-title origins, but those origins matched the previously seen
hangar/attract route and did not establish a mission phase. The attached-mesh
handler had zero executions in the qualified run. This is H4/unevaluable for
the mission discriminator, not evidence that the handler is mission-absent;
no guard, patch, or mitigation was added. Artifacts are in
`scratch/agent/s4667_attached_mesh_mission/`.

## Parked and closed

- The M3 `jal rs_free` idiom audit is closed through s4502. The separate
  `attachedMeshOverlayNpcHandler` NULL/free gap at `0x80054344` is statically
  confirmed; runtime occupancy remains open and no mitigation is authorized.
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
- Generated-symbol renaming is exhausted (s4646): 6 placeholders remain in
  the TOML, none a bounded batch. Do not schedule further sweep iterations.

## Superseded conclusions to avoid repeating

- “M5 audio plan steps 1–10 are closed or conditionally unnecessary” was too
  broad for the current code. Nonzero PCM proves route activity, not that the
  remaining task-contract, state-ownership, wait-gate, safety-exit, and MORT
  boundaries are correct; use `docs/M5-AUDIO-PLAN.md` as the active sequence.

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

0. M5 audio de-stubbing is the strategic priority. Step 7's first status-03
   service-reaping run is qualified: the route and controls fired, and
   `serviceVoicePoolFrame` entered with status `03`, but the exact zeroing
   writer and shutdown call-3 return were not observed. H-status-unreached is
   refuted; do not change the wait or force-clear status. Execute a complete
   status-table writer attribution census next, including every generated
   store to `D_80154620`, exact slot/address/value, worker entry/exit, and
   call-3 boundaries in one build/run.

   Step 5's complete key-on early-return audit is qualified on the covered
   title/hangar route: valid divisor `0xC0`, zero guard fires, normal tails,
   and slot `02` then `00`. Do not remove the returns from this result alone.

- (s4649) Safe full-regen repair is qualified in scratch only; use
  `tools/fixup_game_funcs_vendored.py <scratch RecompiledFuncs>` and compare
  behavioral tags using `scratch/s4648/classification.md`. Never regenerate
  over `../N64Recomp/RecompiledFuncs` until the external fixer is repaired.

1. M4 RSP thread is closed (s4634); s4635 showed the right-edge garbage is not
   tri-submit. s4636 (`ROGUESQ_EDGE_DUMP=dir`, 4 runs, ~640 dumps) selects
   H-rdram: in the 512x16bpp hangar colour image, column 511 holds per-frame
   noise (110-126 distinct values over 240 rows) in buffer 0x00656400 in 4/4
   runs, and is zero in buffer 0x006AB400; columns <=510 are normal. Screenshot
   bimodality plausibly = which buffer is on screen (mapping single-source,
   dumps not frame-synced to screenshots). Next: name the WRITER of
   0x656400 + 1022 + 1024*row (RT64 RDRAM writeback vs recomp CPU/RSP/RDP
   code); see scratch/agent/NEXT.md.
   s4637/s4638: not RT64 wb-only, not CPU stores. s4639 (ROGUESQ_BUF_WATCH,
   scratch/agent/s4639_bw.sh) selects H-stale: 0x656400 col 511 is already
   non-zero 240/240 at the first 512-wide VI; later 512-wide RT64 writeback
   (phys 0x656000 len 0x54C00) converges col 510 but never col 511 (stays
   ~205/240; 0x6AB400 stays 0). Next: why copyNativeToRAM at width 512 omits
   col 511 (native fb width/scissor/VI crop) -- read rt64 copyNativeToRAM and log
   the native fb width + colorWriteWidth. No mitigation without ORIGIN.
   s4640 (ROGUESQ_WB_COL_PROBE, scratch/agent/s4640_wbcol.sh): 0x656000 ww=512
   writeback changes col 510 until converged but col 511 changes 0 rows after the
   first call; control 0x7AB000/0x795C00 do change col 511 -> not a generic loop
   bound. Selects H-native-unrendered: hangar draws never cover x=511. Next: log
   SETSCISSOR extents + draw-rect max x for target 0x656000 (single run).
   s4641 DONE: 0x656000 draw rect is x=140..375 only (121/121 lines); control
   0x7AB000 rectR=512 does change col 511. Col 511 = stale prior-stride RDRAM that
   nothing ever rewrites (not an RT64 bug). Next: compare VI hstart/hend (crop of
   col 511?) in the hangar; if VI shows col 511, check whether retail clears the
   buffer (needs oracle hangar reach) -- else close the thread as stale/benign.
   s4642 DONE: hangar VI xScale 0x333 -> 511.9 visible src cols (controls 320/640
   exact); both 0x656400/0x6AB400 are scanned out. Col 511 = <=1 output px, so it
   cannot explain a multi-pixel right-edge band. Next: measure the real band width
   in a hangar frame capture; if >1 px the cause is not col 511.
   s4643 DONE: band ~5 of 1280 px (col 511 + bilinear halo), bimodal, benign; thread CLOSED.
2. Keep the odd-PI question parked as a missing-trigger/alternate-route
   problem; do not align, skip, or mitigate the DMA without a new trigger.
3. Revisit the external retail-entry boundary only with a new attributable
   handoff; do not repeat the now-qualified all-phase name-copy null.
4. s4644: rim band and holo spikes are no longer visible in current hangar frames (single-source visual); residual candidate is white pillar stubs at x~200/430/865/1085/1130. Need a retail pixel reference before treating it as a defect (retail may light those edges by design). s4645: no reference obtainable; thread PARKED, craft-select frame renders clean.
5. s4647/s4649/s4653: the safe fresh-copy fixer and tag comparison are
   qualified; do not regenerate over the live external tree until the normal
   generation workflow is intentionally repaired or a candidate build path is
   specified. Session 4654 revalidated the attached-mesh gap; the next
   bounded unit is the `load_full_header_image` `rs_free` idiom audit.
   s4651 refutes the port arithmetic arm of M4, while the separate-run matrix
   join is unavailable. s4652 found no retail hangar pixel reference, so H1 is
   closed as unevaluable; no runtime mitigation is authorized. s4655 found
   the two queued M3 audits were historical duplicates (s3637/s3638), and the
   full M3 `rs_free` campaign is already closed (s4502). Do not repeat them;
   owner direction is required for a genuinely new discriminator.
   s4655: the attached-mesh handler was absent from the driven retail
   boot/title route despite qualified oracle controls. s4656 extended the
   route and found the handler in 512-wide attract/demo origins, but still no
   mission phase or action-2 free classification. s4657 repeated the
   post-title Start/A sequence with the correct Rice-video setup and again
   reached only the hangar/attract route. Do not treat these nulls as a
   mission NULL contract proof or add a guard; s4658's distinct post-512
   sequence still stayed on known attract/demo origins despite handler
   activity. s4669 repeated the route with the installed Rice path and a
   post-512 A/Start/A/Z sequence; it again stayed on known attract/demo
   origins before a Rice shader failure ended the run. The next revisit needs
   a genuinely different mission-entry control, not another timing variant.
   s4670's three-Start schedule was invalid because it never reached 512;
   the next run must use the README's verified six-plus Start schedule before
   testing a post-hangar transition.
   s4672's overlay qualification did not reach the required 512 origin and
   lacked a full-range positive control. s4673 supplied both matcher controls
   in one run and selected chunked-load H2; keep the canonical full-range call
   for future complete-section DMAs, but do not treat it as the explanation
   for the current 1024-to-640 route failure. Overlay registration is parked
   pending a new dispatch-attribution discriminator.

Session 4658 tried a distinct post-512 input sequence with PIF tracing. The
whole-RDRAM control hit 10,000 and retail ran for 180 seconds through title,
512-wide attract/demo, title, and hangar-like 512-wide origins. The watched
attached-mesh handler executed 148 times, but every retained row was in the
known attract/demo origins (`0x00690400`, `0x00620400`, `0x00620800`, or
`0x00690800`); `rs_free` executed 24,465 times. This selects H3 for the new
route: it still did not reach a mission, so the handler's mission NULL/free
contract remains unevaluable and no guard is authorized. Artifact:
`scratch/agent/s4668_attached_mesh_route/oracle.log`.

Session 4669 corrected the Rice plugin path in the prescribed mission-route
oracle command after the first invocation proved H4: the Cellar path was
absent and dummy video stayed at 320-wide. The corrected run passed the
whole-RDRAM control at 10,000 callbacks, reached 512-wide at 69.7s, and
executed `attachedMeshOverlayNpcHandler` 280 times. All retained handler rows
were in the known attract/demo origins (`0x00620400`, `0x00620800`,
`0x00690400`, `0x00690800`); no mission origin appeared. The process exited
138 at about 87s during repeated Rice shader-compilation errors, before the
180s budget, but after the discriminator had resolved H3. This is qualified
single-source evidence that this new route still did not establish mission
entry; it does not prove the handler is absent from missions and authorizes no
guard. Artifacts: `scratch/agent/s4669_attached_mesh_route/`.

Session 4670 ran the prescribed hangar-origin A sequence with Rice, the
whole-RDRAM positive control, VI tracing, PIF tracing, and both execution
watches. The control fired 33,429 times and `rs_free` at `0x80001ACC` fired
20,129 times, but the route only reached 320, 640, and 1024-wide phases; it
never produced a 512-wide hangar or attract origin, and
`attachedMeshOverlayNpcHandler` at `0x8005427C` fired zero times. The run
completed normally at 120 seconds. This selects H3 route-invalid for the
requested mission discriminator and does not establish mission absence or
authorize a guard. Artifact:
`scratch/agent/s4670_attached_mesh_hangar_action/`.

The next M3 unit is a new complete census of backward non-self zero-offset
`MEM_H` pointer transitions (the fresh scan reports 19 sites), with the same
allocator/free-list controls. Do not repeat s4674 or s4675, and do not add a
guard without a writer/legitimacy proof.

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
