# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md).
Do not read the ledger whole. Material moved out of this file in the
s4495 maintenance pass is [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) §57
(s4352 snapshot) and §58 (s4413–s4496). Older narrative is in
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md)
and the per-site `docs/M3-S*.md` notes.

Updated for session 4551 (s4551: early-autopilot 150 s run, defaults+HARD_SKIP=0 arms odd=0, control odd=60 and stuck in intro; both fix arms die at the parked `musyxSynthFrame+5436` list-walk crash after the title, `vi_width=512` still never logged). Prior: session 4550 (s4550: 175 s default run, 3 concurrent arms: defaults odd=0, no-fix control odd=60, fix-only arm odd=0, 0 crashes; but `vi_width=512` never logged so the hangar was NOT reached). Prior: session 4549 (s4549: the wild SETCIMG's writer is the s4283-s4287 ring-lap overwrite; `WRAP_FLUSH`+shadow+restore are now default ON; odd cimgs 0 and no VI-640 failure in 4/4 fix arms, no-fix arm failed 2/3). Prior: session 4548 (s4548: `ROGUESQ_FL_HDR_HARD_SKIP` now defaults ON in rt64; default arm 3/3 survive 180 s, forced allow `=0` dies at VI 640 with the heap wipe; thr11d stall cost unmeasured). Prior: session 4545 (s4545: offline diff shows the s4541 and current binaries differ by exactly 2 symbols, so the lost route to the bad call is thread timing, not code; pivot to the deterministic VI-640 death). Prior: session 4544 (s4544: three more runs of the s4541 recipe all died at the intro VI-640 bus error about 3 s in; 0/8 recent runs reach the bad call. H-env and saves are refuted; H-flaky is disfavoured; a build difference since s4541 is the open cause). Prior: session 4543 (s4543: a no-print control died the same way as the print runs, so the VI-640 `fillSampleStreamRange` bus error is baseline, not caused by the print; 0/4 recent runs reach the bad call, so count 32 / base `0x801714D0` is still unmeasured). Prior: session 4542 (s4542: the alloc-pair print's control fired, then both runs died in `fillSampleStreamRange` before VI 1024. That is not the bad-call edge. Count 32 with base `0x801714D0` is still unmeasured. See NEXT.md). Prior: session 4541 (H-index-30). Session 4495 was the
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

The rs_free class closed in s4502. The wild-width writeback's writer is named (s4531) and stays parked: a garbage-region SETCIMG, not a short readback buffer. Do not add a skip. The odd DMA's node field is named (s4533), its jal is named (s4534), and s4535 selected H-neither for the two named stores. s4536 selected H-port-only: retail does not store `0x6C617465` at physical `0x1724F4` in the armed window. The only armed writer is `musyxInitVoiceFromSample` `0x800921E8`, and all 87 words are `0xB0` pointers. s4537 selected H-init-skipped (0 stores to that voice, `n_phys=0`). s4539 selected H-outside. The 565 lattice rows are one base, `0x801714D0`, indices exactly 0..17; k=30 is outside that span, and `B + 30*0x88` is the voice. The bad jal still reads `0x6C617465` (`n_this=0`). s1 at that jal is the entry a0 of `musyxRenderVoiceSamples` (`addu` at `0x8008FFB4`, no later write). s4540 selects H-one-caller. s4541 selects H-index-30 on that same jal. The bad line is `s0=30`, base `0x801714D0`, count `32`, `sum=0x801724C0` equal to a0. `0x801714D0 + 30*0x88` is that voice. The arm is a different array (`base=0x8018D4A0`, `s0=0`, count 16, `sum==a0`). All 18 indices 0..17 also have `sum==a0`. On this base the count was 15, then 18, then 32; 32 is late. The only original store of the count halfword is `allocateSongChannelArray` `sh` at `0x8008F0CC`, and the base word is the following `sw` at `0x8008F0EC` (s3602, static). Do not re-read ra. Do not re-run the index print. Do not grep for a skipped index. Do not add a skip. s4542 did not reach a bad call. Both runs died in the parked bus error before VI 1024. The print control passed: count 16, base `0x8018D4A0`, then the arm line reads that pair. The pre-title lattice store is count 17 and is overwritten by that arm store before mix. Do not read it as H-no-32. Next is still whether a later store publishes count 32 with base `0x801714D0` before the bad jal. Hangar artifact triage stays behind a new discriminator.

One older Gap stays open and is not this frontier. s3636
`attachedMeshOverlayNpcHandler` at `0x80054344` can free `0x1C`/`0x20`
without a prior NULL store. Do not land a skip-path NULL store unless
a census names that same writer. See §56.

## Parked lines

Do not revive these by repeating a null measurement.

- **Mix index of the bad voice is 30** (s4541). Base `0x801714D0`, count 32, `sum==a0`. The arm and all 18 in-range lines also have `sum==a0`. Do not re-run the index print. Do not read `r5` as the scaled offset.
- **Entry ra is not the caller** (s4540). `ctx->r31` is 0 at `0x8008FFB4` on the arm, the in-range entry, and the bad voice. Direct jal does not assign it. `in_match=1` is that single zero. Do not re-run the entry-only probe.
- **Init index span misses this voice** (s4539). Base `0x801714D0`, indices exactly 0..17, k=30, n=565. The same run's render ctl voice `0x80172328` is that base at index 27. Do not re-run the span. Do not grep for a skipped index.
- **Init writes this voice's lattice and not the voice** (s4538). `n_lattice=560`, `n_this=0`, arm residue 128. First lattice voice `0x801714D0` word `0xB03910A0`, exactly 30 slots below `0x801724C0`. Do not re-run that census. Do not grep for the skipped index.
- **Port init does not store to voice `0x801724C0`** (s4537). At the bad jal, `n_all=1178`, `n_this=0`, `n_phys=0`. The arm store was `0xB0373B68` on voice `0x8018D4A0`, so a `0xB0` word would have been printed. Do not re-run that census. Do not add a skip.
- **Retail does not store `0x6C617465` at physical `0x1724F4` in the armed window** (s4536). Do not re-run that oracle. The only armed writer is `0x800921E8`; every sampled word is a `0xB0` pointer (`mismatch=0`). `0x80090C80` wrote this address 0 times. The 4 pre-title `rs_strncpy` (`0x80007670`) writes are unsampled and are not the producer.
- **Named voice+0x34 stores are not the `0x6C617465` producer** (s4535). Do not re-probe `0x80090C80` or `0x800921E8` for this word. Do not grep for another `sw` of voice+0x34.
- **s4553 (single-source): the +5436 crash fires identically with ROGUESQ_AUDIO_UCODE=0 (image off) and with defaults, 3/3 arms; not an audio-image artifact. Tick-on arm stalled in the intro (VI 640 only).**
- **s4554 (static, single-source):** `musyxSynthFrame` 0x80091368..0x80091380 is an unbounded countdown-list walk (`lhu/sh 0x10(n)`, `n=*n`); generated code is in the sibling N64Recomp/RecompiledFuncs/funcs_24.c:7158. No guard exists, only the s4307 trace hook. See NEXT.md.
- **s4555 (3/3 arms, control present): the +5436 corrupt link's writer is `sh $zero,0($a0)` at `0x8001E2C0`, the clear loop of `initTextureLUTAndAllocBuffers` (36-byte `rs_malloc` entries). It overlaps the live audio pool node `0x80179510` (link `0x801794FC` -> `0x000094FC`). The writer is named; open: why `rs_malloc` returned memory the audio pool owns (port heap/free bug vs retail). Supersedes "Pool-link writer unnamed" below.**
- **Pool-link writer unnamed (SUPERSEDED by s4555 above).** `musyxSynthFrame+5436` is
  `lhu 0x10($v1)` at `0x80091368` after a corrupt `next`. s4459 refuted
  the `0x80061520` 0xFF font fill as a live-node clobber. The writer of
  a `0x80193C18`-valued link is still unnamed. The s4457 harness reran
  0/6 (cumulative `+5436` 1/26). Do not re-run it.
  `fillSampleStreamRange+15116` is the same parked family. s4531 run B
  died there again (signal 10, guest pc `0x8000834c`) after the allow
  line. s4532 run B died the same way before VI 1024
  (`fillSampleStreamRange+15156`, guest pc `0x8000834c`, zero
  `[s4532-fill]`). s4542 runs A and B died the same way before VI 1024
  (2/2, `+15156`, guest pc `0x8000834c`). Still parked. Do not re-run it
  to catch the odd DMA. A later alloc-pair attempt may still use the
  qualified route; a death on this stack is not that pair.
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

- "A build difference since s4541 changed the route (H-patch / stale binary)" (s4544 open cause) was believable because 0/8 recent runs reached the bad call after the s4542 print landed. s4545 refuted it: the binaries differ by exactly two symbols (the print helpers), the s4543 no-print control died identically, and the log diffs differ only in thread timing. The s4541 route was a lucky schedule.
Kept here only when a later session would otherwise repeat them.
The s4413–s4433 selector narrative and the s4434–s4475 audio narrative
are in PROJECT-OVERVIEW §58.

- "The pre-title lattice store, count 17 at base `0x801714D0`, is the halfword the bad jal reads" (the obvious reading of the s4542 early lines; believable because that base is the lattice and this `sh` is the only original store) was checked against the next lines in both s4542 runs. The following store is count 16 at base `0x8018D4A0`, and the arm line reads that pair. Count 17 is not live at the first mix call. The bad jal was not reached. Do not read those three lines as H-no-32.
- "The index, base, and count at the bad `musyxMixActiveVoices` jal are unnamed, so the voice could be slot 30 of the init lattice, a slot of another array, or not `s0` at all" (s4540 next step; believable because the loop was only static and the entry ra was 0) was tested in s4541. The bad line is `s0=30`, base `0x801714D0`, count 32, `sum==a0`. The arm is base `0x8018D4A0` with `sum==a0`, and every index 0..17 of the lattice also has `sum==a0`. This is H-index-30. Not another base. Not a stale `s0`. Do not re-run that print.
- "ra at the `0x8008FFB4` addu is the caller of `musyxRenderVoiceSamples`" (s4539 next step; believable because the MIPS prologue has not overwritten `$ra`) was tested in s4540. Both edge runs printed `ra=0x00000000`, including the arm whose a0 top byte is `0x80`. `funcs_24.c` has no constant store to `ctx->r31`. The call-site probe names the caller. Do not re-read ra.
- "The unprinted lattice stores might be a hole inside a span that covers voice `0x801724C0`, or a span that never reaches it" (s4538 next step; believable because only four of 560 lattice addresses were printed, and those four were consecutive slots) was tested in s4539. All 565 lattice rows are indices 0..17 of base `0x801714D0`, each index repeated, none above 17. k=30 is outside. Not a hole. Do not re-run that span.
- "Init's `0x800921E8` addresses cannot be voice `0x801724C0`, because the arm voice is a different residue and two pointers do not classify the other stores" (s4537 next step; believable because `0x8018D4A0` has residue 128 and `0x80172328` being 3 slots below does not speak for the rest) was tested in s4538. The arm line printed residue 128. `n_lattice=560`, `n_this=0`, raw34 still `0x6C617465`. Lattice voice `0x801714D0` is exactly 30 slots below the target and holds `0xB03910A0`. Init addresses this lattice and does not store this slot. Do not re-run that census.
- "The port's `0x800921E8` may still store to voice `0x801724C0`, and the s4535 probe would hide it because a `0xB0` word is not printed" (s4536 next step; believable because that probe returns on a non-ASCII, even, above-`0x01000000` word) was tested in s4537. The new counter prints every such store, cap 16, and snapshots `n_all`/`n_this` on the bad jal. `n_all=1178`, `n_this=0`, `n_phys=0`, no target-voice line. The arm word on a different voice was `0xB0373B68`, so a pointer store is visible. Init does not write this voice. Do not re-run that census.
- "Retail writes `0x6C617465` at physical `0x1724F4` during the armed window, from a named store or some other PC" (s4535 next step; believable because the port reads that word from voice `0x801724C0` at the 512-to-640 edge) was tested in s4536. Origin `0x6a2900` was reached (763 VI). Watch 0 fired. Post-value overflow=0, 23 unique values, all `0xB0xxxxxx`, sole sampled PC `0x800921E8` (87/87, scalar mismatch 0). The word is absent. Do not re-run that watch. `post-target-summary seen=0` is the hangar gate (no writes at origin `0x6ab400`), not "init never stored".
- "One of the two named voice+0x34 stores wrote `0x6C617465`" (s4534 next step; believable because those are the two `sw` instructions already named for that offset) was tested in s4535. Neither store printed the word. The same run's `0x800903F0` bad jal still had raw34=a3=`0x6C617465` on voice `0x801724C0`. Init's control is the arm word `0xB0373B68`, which the following `0x800902CC` jal reads back; that site stored no in-range even word. Keyon's in-range control is `0x00000000`. These two stores are not the producer. Do not re-probe them for that word. A `0xB0` store is invisible to that probe.
- "Which `musyxRenderVoiceSamples` jal passed a3, and whether that a3 was the raw voice word or the word plus `0x100`, is unnamed" (s4533) was believable because the callee's ra is 0 and both delay-slot shapes can produce a3 `0x6C617465`. s4534's only bad row is jal `0x800903F0` with raw34 == a3 == `0x6C617465`. The same run's `0x800902CC` row showed raw34+`0x100` == a3 on a different value and returned. The voice word is `0x6C617465`. Do not re-probe the four jals.
- "The node field that supplied `0x6C637265` is an unnamed foreign writer, and the neighbouring word makes it the string `lcrelate`" (s4532, and the obvious reading of the s4533 bad row) was believable because FE98 only copies node+8 into the DMA slot and the two words are printable ASCII. The only edge into FE98 stores node+8 first, at `0x8008FDC0`, as `a3 + 0x600*k`, and stores node+0xC = a3 at `0x8008FDCC`. The soak words give k=`0x55` with remainder 0. Those bytes are not in the ROM. Do not watch the node for a string store.
- "A VI-640 death before the odd `do_rom_read` is the parked `fillSampleStreamRange+15116` bus error" (s4529 NEXT, and that session's two signal-10 runs) was believable because `last-guest-pc` stays `0x8000834c` and those runs' faulting PC was that function. s4530 run b faults in `NativeTarget::copyToRAM`; the memcpy length is the `ALLOW_WILD_FL` range. Classify a VI-640 death as the bus error only when the faulting stack is `fillSampleStreamRange`. s4531 run B is that stack again; s4530 run b is not overturned.
- "The s4298 scan's `hits=0` means the odd cart word is not in RDRAM" (s4532 soak, readable that way) was believable because the scan said so. It compared against physical `0x1C637265`. The guest word is raw_r7 `0x6C637265`. Do not read that zero as absence of the guest word.
- "A hangar run with `[s4298-odd] 0` has covered the odd DMA" (s4531 run A) was believable because the tag was armed through VI 512. The soak's only hit is the later 512-to-640 edge (`initVideoSubsystem`, 169.7s). A run that stays at 512 is not that edge.
- "The first `ALLOW_WILD_FL` dies in `copyToRAM` because the readback buffer may be short" (s4530 NEXT) was believable because that run's faulting `x2` equaled the write range. s4531 run B's allow has `nativeReadbackBufferSize == bufferOffset+bufferSize` (1400748) and the fault is not `copyToRAM`. A short buffer is not required for the allow to fire. Do not treat a later allow death as a short memcpy unless the stack is `copyToRAM`.
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

1. **[s4552: 420 s late-route, 2 arms, 0 crashes, odd=0, but VI 1024 for ~400 s and VI 512 never reached; hangar-reach via autopilot is CLOSED until the route/menu input is fixed. Move to M5 audio de-stub.]** Prior text: Hangar-length run with the ring-lap fix default (HYPOTHESIS-ID: wild-setcimg-writeback). s4549 made `ROGUESQ_DPC_WRAP_FLUSH` and `ROGUESQ_S4272` default ON (restore already was); the wild SETCIMG origin is the s4283-s4287 ring-lap overwrite, not a port misparse (supersedes the "writer unnamed" wording). s4550: pre-hangar 175 s run confirms odd=0 (control 60) but never reached VI 512, so the hangar question stays open; s4551: the early route (`3:start,6:start,...`, recipe `s4551_hangar.sh`) reaches the title in both fix arms but both then die at `musyxSynthFrame+5436`, so the hangar is blocked by the parked pool-link crash on that route and by time on the late route; next needs either a run with the +5436 walk guarded/avoided or a longer late-route run (>=300 s). Open: does a >=150 s default run show hangar-phase odd cimgs / fb-set growth gone (s4287 Q1, unmeasured). thr11d benefit of the old allow stays unmeasured (s4547). Recipe `scratch/agent/s4549d_defaults.sh`.
2. **External retail-entry boundary.** Parked. Revisit only when the
   last fifteen session titles are all generated-symbol sweep steps, or
   when a new attributable handoff exists. Do not repeat a null
   measurement. This is the item the iteration contract calls
   "Next steps #2".
3. **M3 pre-publication guard runtime qualification.** Blocked on
   `mips64-elf-gcc`, `mips64-elf-ld`, and `PatchesLib`.
4. **Generated-symbol renaming sweep**, slug
   `generated-symbol-renaming-sweep`. Do this only when item 1 cannot
   be run.
   The last bounded lead was `0x8000A000..0x8000B000` (s3796).
   Mapping-only edits do not reset the engineering-change gate. If the
   last fifteen titles are all sweep titles, do item 2 or the M4
   boundary below instead of another sweep step.

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
- **s4556 (2 arms, control present, crash not reproduced under heap logging): rs_malloc 0x801793F0 and 0x80179480 (covering audio node 0x80179510) are returned INSIDE the never-freed 120 KB block 0x801767E0. Writer of the nested free-list state unnamed (single-source: allocator log only).**
