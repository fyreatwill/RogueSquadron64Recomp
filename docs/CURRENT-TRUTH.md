# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md).
Do not read the ledger whole. Material moved out of this file in the
s4495 maintenance pass is [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) §57
(s4352 snapshot) and §58 (s4413–s4496). Older narrative is in
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md)
and the per-site `docs/M3-S*.md` notes.

Updated for session 4530 (s4530: the odd-phys join never reached VI 512. Both runs died at VI 640 on the first `ALLOW_WILD_FL` writeback, widths 913 and 1185. The SIGSEGV is `copyToRAM`, memcpy length equal to that range; `fillSampleStreamRange+15116` is a stale guest PC on that run. See NEXT.md). Prior: session 4529 (VI-512 heads' words 0 and 1 are sibling pointers, not the odd ROM address). Prior: session 4528 (list-link holder; tagged 0x8017D030 is below the freed block; full rs-malloc logging is not a late-window witness). Prior: session 4527 (holder poller built; its own run died at 20 s, late window then measured by the queued soak). Prior: session 4526 (s4526 corrected s4525: retail's list is populated and relocates to 0x801F9CE0 on the same schedule; the text batch is the port's ~122 s phase). Prior: session 4525. Prior: session 4524 (s4524: stub-gate hypothesis for the stale stream-node crash refuted, see docs/M5-STREAM-NODE-LIFETIME.md). Prior: session 4521 (s4521: stub-region tris use the stock TEX0*SHADE combiner with shade <=165, no stream-side cause; hangar triage PARKED, a pixel->tri map via an RT64 tri-index mask render would be the next probe). Prior: session 4520 (s4520: white pillar stubs are in the retail RDP stream too - aligned frame 1246/1249 tris byte-identical - so they are renderer-side or genuine, not RSP). Prior: session 4518 (s4518: RSP LUV/LFV/LHV sign-extension bug fixed in lib rsp_vu_impl.hpp; hangar entry-frame shade diff vs retail 588 -> 3 tris). Prior: session 4517 (s4517: aligned port-vs-retail RDP byte diff of hangar entry frame: all state/edge/texture words identical, shade-colour words sign-extended in port (0xFFxx vs 0x00xx) in 588/1249 tris => RSP shade-output defect, not raster/VI; see NEXT.md). Prior: session 4516 (s4516: retail with the port's 11-Start schedule reaches the same 195-texrect/~1130-tri frame, so the s4515 count difference is scene timing, H1a; ucode counts agree, remaining suspect H3 raster/VI at an aligned scene point). Prior: session 4515 (port hangar sync: tris~1125, texrect 195 vs retail 1244/0, selects H1; see NEXT.md). Prior: session 4513 (BLOCKED: retail RDP stream needs LLE RSP+RDP plugin, BLOCKED.md). Prior: session 4512 (s4512: op04 blobs are DL scratch, vertex diffs void). Prior: session 4511 (s4511: child-DL data blobs dumped on both sides; texture blob identical, 6 static vertex blobs differ but the dump window/layout is unqualified). Prior: session 4505 (2026-10-09). Session 4495 was the
maintenance pass that left this file at one backlog sequence. Item 2
is the sweep-revisit target the iteration contract calls "Next steps
#2".

## Current state

The qualified native route boots through attribution, N64 logo, intro
cinematic, Factor 5 logo, title VI 1024 (`0x00790400`) and hangar VI 512
(`0x006AB400`) on the real-audio/LLE/ungated/solo/spin-yield route.
(s4514) Retail RDP stream IS obtainable: `scratch/agent/s4514_cxd4.sh` (oracle --rsp cxd4 + tools/oracle/rdplog); retail hangar VI-512 frame ~1244 tris (0x0D x275, 0x0F x969), 2 setcimg w512, ~205 KB RDP; the s4513 BLOCK was false. Hangar geometry and colour artifacts remain, localized (s4505): the entry frame is a nearly complete scene with a rim colour band, blue holo spikes and right-edge column garbage; a later frame is black with right-edge garbage. `ROGUESQ_AUDIO_UCODE=0` is
the silent control. VI 640 is the intro, not a stuck state.

Audio is no longer a zero-output stub on that route. Fresh 7F saves
produce nonzero PCM; reset `build/saves` before an audio A/B and use
`RS64_EEP_TRACE=1`. AI byte order is fixed (`p[i ^ 3]`,
`queue_samples ^ 3`). Title AI buffers matched ucode output in the
qualified capture. MusyX/MORT is still only partially de-stubbed and
must not reach stock `aspMain`. [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)
steps 1–10 are closed or conditional-unneeded (s4475). Do not reopen a
closed step without a new discriminator.

Full regeneration has been unsafe since s4204. `N64Recomp` then
`fixup_game_funcs.py` aborts at the E088 anchor and can clobber live
generated functions. Use the existing `tools/apply_s*.py` workflow
unless that failure is explicitly repaired.

## Active frontier

The M3 `jal rs_free` idiom-class audit (`m3-idiom-class-audit`) is
closed (s4502). Its last closed site is s4500:
`freePlayerAuxBuffersIfActive` at `0x80100F90` frees the slot +0xC
`rs_malloc(count << 1, 0)` return (stored `0x80100854`), once; zero
count skips it; no guard. With s4499 (`0x80100F84`) the function is
closed, and a scan of `0x80100F98..0x8010B6D0` (control passed) found
no later `jal rs_free` in `.ovl.mission`. The chain from
`loadCraftShadowTextures` (`0x8006B814`, s4477) through s4500 is
Complete. Index: PROJECT-OVERVIEW §58; notes `docs/M3-S4477-*.md`
through `docs/M3-S4500-*.md`. Headless note: `.venv-splat` python is
not allowlisted; use system `python3` with `scratch/agent/s4500_dis.py`.

The rs_free class closed in s4502. The live work is the intro `ALLOW_WILD_FL` writeback that blocks the odd-DMA join (Next steps #1). Hangar artifact triage stays behind that.

One older Gap stays open and is not this frontier. s3636
`attachedMeshOverlayNpcHandler` at `0x80054344` can free `0x1C`/`0x20`
without a prior NULL store. Do not land a skip-path NULL store unless
a census names that same writer. See §56.

## Parked lines

Do not revive these by repeating a null measurement.

- **Pool-link writer unnamed.** `musyxSynthFrame+5436` is
  `lhu 0x10($v1)` at `0x80091368` after a corrupt `next`. s4459 refuted
  the `0x80061520` 0xFF font fill as a live-node clobber. The writer of
  a `0x80193C18`-valued link is still unnamed. The s4457 harness reran
  0/6 (cumulative `+5436` 1/26). Do not re-run it.
  `fillSampleStreamRange+15116` is the same parked family.
- **s4465 allocator overlap** at VI 1024
  (`rs_malloc(3964) = 0x801931F0`) is single-source. s4466 and s4468
  did not recur it (0/8). No more heap-header instrumentation. The
  s4467 soak was invalid: its `cd` resolved into `scratch/` and never
  launched the game.
- **AI-event cadence is not a crash cause.** `ROGUESQ_AI_EVENT_HZ=115`
  and `ROGUESQ_AI_EVENT_DRAIN=768` stay default-off. Retail also submits
  about one AI buffer per VI (s4437). The port mix rate tracks the
  AI-event rate and sits below retail's 114/s unless HZ=115, which hits
  the same crash families sooner (s4456, single-source, n=4/arm).
  mupen's AI drain timing may be slow; that is not confirmed past s4439.
- **Status-03 reaping is legitimate** guest behaviour. Retail executes
  the same `0x8009B7CC` chain (s4472). s4470's "retail never does" is
  superseded. A whole-RDRAM watch capped at 10,000 hits goes silent
  before title. Late-phase writer hunts need a narrow watch whose own
  hits are the control.
- **Graphics wrap-restore.** `ROGUESQ_WRAP_RESTORE` cut ODD colour-image
  events from 60 to 0 in three runs. Hangar impact is unqualified. Do
  not broaden this ahead of the M3 frontier.
- **VI-640 crash family** and broad M3 guard classes stay parked. No
  mitigation without an `ORIGIN:` line naming the writer and whether
  the value is legitimate.
- **External retail-entry boundary** and **M4 accumulator-origin** stay
  parked until a new handoff or a live target-phase control exists
  (PROJECT-OVERVIEW §52). A generated-symbol sweep does not substitute
  for either. Fifteen consecutive sweep sessions must revisit one of
  them instead of taking another sweep step.
- **M3 pre-publication guard runtime qualification** is blocked until a
  host has `mips64-elf-gcc`, `mips64-elf-ld`, and `PatchesLib`.

## Superseded conclusions

Kept here only when a later session would otherwise repeat them.
The s4413–s4433 selector narrative and the s4434–s4475 audio narrative
are in PROJECT-OVERVIEW §58.

- "A VI-640 death before the odd `do_rom_read` is the parked `fillSampleStreamRange+15116` bus error" (s4529 NEXT, and that session's two signal-10 runs) was believable because `last-guest-pc` stays `0x8000834c` and those runs' faulting PC was that function. s4530 run b faults in `NativeTarget::copyToRAM`; the memcpy length is the `ALLOW_WILD_FL` range. Classify a VI-640 death as the bus error only when the faulting stack is `fillSampleStreamRange`.
- s4528 "the next measurement is romA/romB of the VI-512 heads, and odd or ASCII there means the list is walking overlay bytes" was the right next read, and it was done (s4529). Those words are 0 or a pointer to the adjacent slot. Do not snapshot them again expecting ASCII or a ROM offset.
- s4527 "the late window was not reached, so nothing is selected between a list link and a voice pointer" was true of that run, which died at 20 s. The queued s4522-recipe soak reached the window (s4528). Do not re-read the 20 s log as the late-window result.
- "Hangar is wholly broken" (implicit in the pre-s4505 wording "geometry/colour artifacts") was believable because old sessions chased a band and later frames are black. s4505 (single-source, visual) shows the entry frame is nearly correct; defects are local.
- s4503 "priority ladder exhausted, human direction required" was believable because every ladder rung was closed. It conflated the ladder with the project: the hangar artifacts in Current state were never a rung. Re-scoped in s4504; BLOCKED.md removed.
- s4476 "M3 has no unaudited `jal rs_free` class" was believable because
  the s397 frequency scan looked exhausted. It never covered `funcs_16.c`
  upward. The walk continued through `0x800F9F94` (s4498). Do not
  stop while unaudited sites remain.
- s4414/s4416/s4417 "port enters `0x80029E78`, retail enters
  `0x80029E80`" was believable because both witnesses were guest PCs.
  The port submits through `osAiSetNextBuffer_recomp`, so that guest PC
  cannot fire. Closed in s4432. Retail also calls `reapplyAudioConfig`
  at the title-to-hangar change (s4433). No selector or reapply
  divergence remains.
- s4417's caller/precall zero was a missing generated probe, not a guest
  path (s4418). Restored in s4419. A zero from a witness counts only
  after the generated artifact contains the call.
- s4424's empty title writer buckets were real and one VI mode early
  (s4425), not "no writer". That boundary is not the selector divergence
  (s4430, s4433). Do not reopen it. A breakpoint samples the register
  before the instruction runs (s4426).
- "The port paces ~1 audio buffer per VI, half of what is needed"
  (s4435) was believable from 59 vs 115 buffers/s. Retail also submits
  ~1 per VI (s4437). The gap is not the game-side submit rate.

## Next steps

One sequence. Closed audits are not items. Item 1 is the next iteration
unless Step 0 maintenance triggers again.

1. **Wild-width freelist writeback** (HYPOTHESIS-ID: allow-wild-fl-writeback). s4530: the odd-phys join did not reach VI 512. Both runs died at VI 640 on the first `[ost-wb] ALLOW_WILD_FL` (s659: a width outside {320,512,640,1024} whose range covers freelist `0x1F3CC0` is written anyway). Widths were 913 then 1185, so the value is not a stable legitimate mode. The SIGSEGV run's memcpy length equals that range and the stack is `copyToRAM`, which does not check `nativeReadbackBufferSize`. `[cimg-oob-1]` logged no WIDTH hit, so it is not a head-of-submission `G_SETCIMG`. Do not add another skip. The s4529 head snapshot still stands; resume the odd-phys join only after a run reaches VI 512 with `[s4298-odd]` armed. Next measurement is in NEXT.md. No `ROGUESQ_LOG_RS_MALLOC`.
2. **External retail-entry boundary.** Parked. Revisit only when the
   last fifteen session titles are all generated-symbol sweep steps, or
   when a new attributable handoff exists. Do not repeat a null
   measurement. This is the item the iteration contract calls
   "Next steps #2".
3. **M3 pre-publication guard runtime qualification.** Blocked on
   `mips64-elf-gcc`, `mips64-elf-ld`, and `PatchesLib`.
4. **Generated-symbol renaming sweep**, slug
   `generated-symbol-renaming-sweep`. Only when item 1 is parked for
   lack of a discriminator and item 3 is still blocked. Mapping-only
   edits do not reset the engineering-change gate. If the last fifteen
   titles are all sweep titles, do item 2 or the M4 boundary below
   instead of another sweep step.

### Durable boundaries

- **M4 accumulator-origin.** Parked. Its target phase and positive
  control are not live (PROJECT-OVERVIEW §52). Same revisit rule as
  item 2.

## Evidence boundary and operating rules

Retail oracle watches are physical-address ground truth. Whole-RDRAM,
VI, and target-PC controls qualify coverage. A route failure invalidates
a null. Every instrument needs an independent witness, a same-run
positive control, a phase-scoped budget, and a second evidence line
before it is promoted. Phase-gate animated comparisons on VI
transitions. Batch every A/B arm into one build and one iteration.

Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX
assumptions. The graphics path is LLE-only. Keep safety guards separate
from explanations. Regeneration order is `make_elf.py -> N64Recomp ->
fixup_game_funcs.py -> CMake`. Never hand-edit generated functions for
behavior. If `lib/` changes, export submodule patches in the same
session. Never run submodule update, checkout, clean, or hard reset.
Kill runs with SIGKILL and run from `build/` with the ROM present. Any
mitigation-shaped change needs an `ORIGIN:` line naming its writer and
whether the value is legitimate.

## Evidence index

[M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md),
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md),
[PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) §57 and §58, and
[PORTING-STATE.md](../PORTING-STATE.md).
