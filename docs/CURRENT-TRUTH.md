# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md).
Do not read the ledger whole. Material moved out of this file in the
s4495 maintenance pass is [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) §57
(s4352 snapshot) and §58 (s4413–s4496). Older narrative is in
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md)
and the per-site `docs/M3-S*.md` notes.

Updated for session 4607 (retail `$a1` at the phase-gated `rs_strncpy` entry is a repeated shared RDRAM table operand, selecting the alternate-source-table hypothesis). Prior: session 4606 (retail source-span snapshot is all `0xFF` in VI 512 while the target span contains the five name records; the alternate input remains unresolved). Prior: session 4605 (retail target writer histogram attributes all 76 target-range writes to `0x80007670` in VI 512; one writer is selected). Prior: session 4604 (retail hangar snapshots contain the same five name records in the target span, while the port source span is all `0xFF`; retail-equivalent source location is refuted). Prior: session 4603 (the source-byte witness shows caller `0x80022B44` copying five stable, printable name-like records; `0x8062BA64` supplies `late`). Prior: session 4602 (the caller table selected the five source/destination pairs but semantic identity and retail equivalence remained open). Prior: session 4601 (the widened phase-3 span census saw `rs_strncpy` write the complete `late` bytes at offsets `0x34..0x37` of physical `0x1724C0`; the immediate writer is now selected). Prior text follows.
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

- (s4588) "The audio mixer thread (tid 3) issues the odd-address DMA" (s4580): believable because tid 3 issued the surrounding DMAs and the ASCII node was in the audio queue; the clean run shows the odd call comes from tid 1 pri 120. Demoted to unproven.

- (s4567) "hangar-reach via autopilot is CLOSED" (s4552) and "s4298 scan reports hits=0 so the node is unlocated": believable because every recipe fired keys at VI 640 before the title, and the scan compared the physical word, not the guest word (phys+0x50000000). Both overturned in s4565/s4567.

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

## s4591 finding (single-source oracle)
Retail reaches the 512 hangar phase and passes the whole-RDRAM positive control (13,140 callbacks; control removed at 10,000). The physical target range 0x179A60..0x179A68 receives 3,140 writes, including 687 VI frames at origin 0x006AB400. Post-store rows at 0x179A64 are B0xxxxxx pointers, never 0x77696E67 ("wing"); the same builder/copier PCs 0x8008FB64/68 and 0x8008FE98/A0 write the range. This is one independent retail witness, not yet a two-source origin proof. It refutes H-legit-retail for the ASCII tag and leaves H-key-unresolved vs H-port-writer open on the port.

## s4592 finding (three-arm port watch plus independent value probe)
The corrected s4569 recipe enabled both the adjacent-range positive control and the target writer hook. All three arms reached VI width 512, fired the odd DMA, and produced target writer rows at 0x8008FE98 and 0x8008FB64 for 0x179A64. The independent s4532 fill probe in the same logs reported `site=FE98 dev=0x6C637265 size=0x300` in all three arms; FE98 stores that `dev` into the cart field at node+4, so the port really writes ASCII `lcre` (the DMA later reads the same node as physical `0x1C637265`, guest `0x6C637265`). The positive control fired in each corrected arm. Together with s4591's retail oracle witness, this establishes the immediate port writer and the retail B0-pointer role; s4593's static census refutes a resource/tag lookup on the upstream FE98 path. The generic s4569 value field is single-source-unusable because the legacy parity helper passes zero; the s4532 value probe is the independent value evidence.

## s4590 finding (single-source)
The odd DMA's cart word 'wing' is an ASCII 4cc tag in the cart slot of 12-byte {len,tag,ram} records (siblings wizg/witg/wiyg/lcre); not an overrun string. The static chain has no resource lookup; the runtime writer/input pair remains open.

s4593 static census closes the resource-key branch. `fillSampleStreamRange`
at `0x8008FAAC` writes cache node `+8` at `0x8008FDC0` as
`a1 - node+4`, then FE98 copies that derived value into the output record;
no string, ROM lookup, or tag translation occurs on this path. The cache
initialization/acquire/recycle functions only manipulate links, buffer
pointers, state, and the same numeric range fields. All four callers in
`musyxRenderVoiceSamples` (`0x8009024C`, `0x800902CC`, `0x8009039C`,
`0x800903F0`) form `a1` from `voice+0x34` plus a calculated offset, with
`a3 = voice+0x34 + 0x100`. Thus port `lcre` is a derived-field defect or
bad input pair, not a legitimate resource key. This is static-source-only;
the writer of the bad operand at runtime remains open.

s4594 ground-truthed retail again and then ran the phase-scoped port census.
The first 512-gated run passed four valid controls but produced no bad row;
the existing FE98 bad row appeared only after VI changed to 640/origin
`0x006A2900`, so the gate was corrected and rerun. The corrected run passed
four controls and captured the bad subtraction at `0x8008FDC0`:
`a1=0x6C63745D`, `a3=0x6C617465`, computed `0x6C637265`, while the selected
node's `+4=0x8017DD58` remained a cache-list pointer. This selects
H-caller-input over stale node state. Retail's independent target watch still
shows B0xxxxxx pointer stores at the normal builder PCs, so the port-only
ASCII input remains illegitimate. The run then hit the known odd-PI alignment
abort; no mitigation was added. The exact upstream writer/translation of the
caller inputs remains open.

s4595 ran the required retail control first: whole-RDRAM activity and the
VI-512 target watch fired, and the normal retail builder PCs stored only
B0xxxxxx pointers. The single phase-gated port run reached VI-640/origin
`0x006A2900`, fired four adjacent-range controls, and captured the first bad
caller row at `0x800903F0`: voice `0x801724C0` had `+0x34=0x6C617465`
(`late`), constructed `a1=0x6C63745D`, and `a3=0x6C617465`; the FE98 row
received the same malformed `a1/a3`. Sites `0x8009024C`, `0x800902CC`, and
`0x8009039C` produced no bad row in the phase budget. This selects
H-caller-input-source over H-cache-node, with the retail pointer role as the
independent second evidence line. The run ended at the known odd-PI abort;
no mitigation was added. The remaining question is which writer/translation
puts printable data into voice `+0x34` before `0x800903F0`.

s4598 ran the independent retail oracle first: whole-RDRAM activity reached
10,004 writes, and physical target `0x1724F4` had four retail writes, all
from `0x80007670`; the target 640 phase had zero retail rows because those
writes occur in the 512 phase. The regenerated port census was present in all
51 generated function units. Its adjacent-range control fired after the port
reached VI width 640/origin `0x006A2900`, but the generated-store hook
produced zero target rows before the known odd-PI alignment abort. This rules
out a target-phase generated writer, but not a pre-640 generated writer or a
host/translation path. No mitigation was added.

s4600 ran the phase-bucketed generated-store census from boot through the
qualified route. The entry control fired in phases 2 and 3, the adjacent
generated-store control fired in phase 3, and the target physical address
`0x1724F4` received three generated byte stores in phase 3. All three came
from `rs_strncpy` at `0x80007670`, with values `0x6C, 0, 0`; the run then
continued through phase 3 without a new target writer row. This selects a
generated guest writer over a lifetime host/translation-only explanation and
names the immediate writer, while leaving the source of the later `late`
word unresolved because the exact-byte witness did not observe that value.
The adjacent control was present in the same run. ORIGIN: diagnostic-only;
no value was filtered, skipped, or guarded.

s4601 widened that same census to physical `0x1724C0..0x17250B` and retained
the first row for each phase/PC/offset. The entry and adjacent controls fired
in the same qualified run. In phase 3 (VI 640), `rs_strncpy` at `0x80007670`
wrote offsets `0x34..0x37` as bytes `l`, `a`, `t`, `e`, exactly naming the
immediate generated writer of the later value read by the bad caller. The
oracle arm passed its whole-RDRAM control but stopped near VI 1000 before the
target phase, so it is not a retail target-phase null; this result is
single-source for the port writer, with prior static caller census as the
independent source boundary. No mitigation was added. ORIGIN: diagnostic-only;
the `late` bytes are legitimate name text, not filtered or guarded.

s4602 first grounded the same physical span against retail: the whole-RDRAM
control fired, retail reached the 512 hangar and later 640 activity, and the
span received 76 writes from guest `0x80007670`. The qualified port caller
table passed the entry/adjacent controls and selected caller `0x80022B44`:
five calls wrote 16-byte chunks to `0x801724C0`, `0x801724D0`,
`0x801724E0`, `0x801724F0`, and `0x80172500`, from sources
`0x8062B9F8`, `0x8062BA1C`, `0x8062BA40`, `0x8062BA64`, and `0x8062BA88`.
The fourth chunk contains `late` at destination offsets `0x34..0x37`, matching
the span census. This selects the generated caller and source-table path over
the host/translation-only branch. The source record's semantic identity and
retail equivalence remain open. No mitigation was added. ORIGIN:
`rs_strncpy` copies legitimate name text; no value was filtered, skipped, or
guarded. The first run's origin gate was invalid; the fixed width-only gate
was the result used here. Artifacts: `scratch/agent/s4602_oracle/`,
`scratch/agent/s4602_callers/`.

s4603 extended the regeneration-preserved caller hook to read the guest-endian
16-byte source and destination preimage. The corrected qualified run passed
the entry, adjacent, and 76-row span controls. Caller `0x80022B44` copied
stable records from `0x8062B9F8`, `0x8062BA1C`, `0x8062BA40`, `0x8062BA64`,
and `0x8062BA88`; their payloads decode as printable name-like strings
(`xengilight`, `xlaserbod`, `xtopbdydet`, `xbkplate`, and `newx_glw_15`).
The fourth source supplies `late` at the target span. This single-source
semantic result selects H-name-table over an incidental generic record copy;
retail source-table equivalence remains open. The run ended in the known
`musyxSynthFrame_s4562_impl+5808` stale-head crash after the measurement. No
mitigation was added. ORIGIN: the source and destination bytes are legitimate
name records; no value was filtered, skipped, or guarded. Artifacts:
`scratch/agent/s4603_source_records_fixed/`.

s4604 ran the independent retail oracle with whole-RDRAM, candidate-source,
and target-span controls. The driven run reached the 512 hangar phase and
passed the whole-RDRAM control (21,009 callbacks; 3,580 VI). At the hangar
phase snapshot, candidate source physical `0x62B9F8..0x62BA98` was all
`0xFF` (160/160 nonzero bytes), while target `0x1724C0..0x17250C` contained
the same five name-like records, including `late` at offsets `0x34..0x37`.
The source span therefore is not retail's source table. This refutes
H-retail-equivalent and selects H-retail-different-table over H-port-only-source
as the working model: retail publishes the same records through another
source or direct literal path. The alternate source location and target
writer remain open. No mitigation was added. ORIGIN: the compared name bytes
are legitimate data; nothing was filtered, skipped, or guarded. Artifacts:
`scratch/agent/s4604_retail_source_table/`,
`scratch/agent/s4604_retail_source_table_driven/`, and
`scratch/agent/s4604_retail_source_table_snapshot/`.

s4606 repeated the retail source/target comparison in one 90-second driven
oracle run with the whole-RDRAM positive control. The control fired 21,009
times and the run reached VI 512 at origin `0x006AB400`. The candidate source
span `0x62B9F8..0x62BA98` was all `0xFF` at the hangar snapshot (160/160
nonzero bytes), while the target span again received 76 writes, all from
`0x80007670`; its snapshot retained the same name records. The candidate
source watch had 10,933 lifetime writes, so this is a phase-local content
result, not an absent-watch result. This independently refutes the candidate
span as retail's live input, but does not distinguish an alternate retail
table from distinct call-site operands or a host-side translation before the
same guest writer. No mitigation was added. ORIGIN: the compared bytes are
legitimate name data; nothing was filtered, skipped, or guarded. Artifact:
`scratch/agent/s4606_retail_source_snapshot.log`.

## Next steps

One sequence. Closed audits are not items. Item 1 is the next iteration
unless Step 0 maintenance triggers again.

0j. **[s4586, extends 0i]** In the rs_malloc window (opens VI ~115, never closes in 190 s) tid 3 gets 0 handoffs; only the 117/118/122 threads run, ~3 handoffs/VI with ~5-7.5 ms wall slices vs ~0.04 ms out of window (2 arms, out-of-window control fired). H-handler-cost selected; H-sched and H-hostblock refuted. Open: guest compute vs host wait inside the slice (PC sampler, scratch/agent/s4586_rq.sh + s4586_an.py).
0k. **[s4587, SUPERSEDES 0f-0j as an intrinsic-hang model]** The permanent rs_malloc window (tid 3 starved, ~7.5 ms slices) is an OBSERVER ARTIFACT of `ROGUESQ_LOG_S4581=1`: its `backtrace_symbols_fd` on every in-window handoff. 1 kHz host-PC sampler (mach thread_get_state; threads.cpp s4587) put ~80% of in-window pri-117/118/122 samples in dyld `findClosestSymbol` called from `s4581_log_switch` (plus `__writev`); pri-117 etc. spend the slice symbolizing. A/B in one iteration (new env `ROGUESQ_S4581_NOBT=1`): arm A (backtrace) stuck at VI ~115 for 200 s, t3pops frozen at 186; arm B (no backtrace) window opens/closes (vi 114, 421, 3282, closed 5850), tid 3 keeps running (t3pops 469@VI300 -> 7732@VI5850) and the run dies at VI ~5850 on the known `pi.cpp:113` odd-DMA assert. So s4580-s4586 (window, starvation) measured the instrument; the real failure is the pi.cpp:113 death. Caveat: in-window slices in arm B are still ~4 ms (not yet explained; sampler suspends 1 kHz). Next: NEXT.md.
0l. **[s4588, confirms 0k]** Instrument-free arm A and arm B (+`ROGUESQ_LOG_S4588` caller log in `do_rom_read`) both die on the `pi.cpp:128` odd-DMA assert, so the death does not depend on instruments. The bad call is tid 1 (pri 120), last guest PC 0x80001B08, cart addr 0x17696E67 (ASCII "ing"), ram 0x801A9B90, 0x600 bytes; preceding even DMAs came from tid 3 (pri 10). Weakens the s4580 audio-mixer-issues-the-DMA theory (single-source: guest PC may be a wrapper). Next: NEXT.md (S4298 RDRAM hit scan to find the node holding the ASCII value).

0g. **[s4582, extends 0f]** In alloc #2's rs_malloc window the audio thread (pri 122, 0x3001494b0) is first readied by a Vi retrace message (mq 0x80114388) drained inside the allocator's own osRecvMesg (`dequeue_external_messages -> do_send -> schedule_running_thread`), 3/3 arms, control fired. H-ai-event refuted. Open: why the displaced pri-10 allocator is never re-popped (running_queue contents at run_next/check_running_queue, in-window). Instruments: ROGUESQ_LOG_S4582 (scheduling.cpp, mesgqueue.cpp), recipe scratch/agent/s4582_enq.sh.
0h. **[s4583, extends 0g]** H-starve selected: during alloc #2's rs_malloc window tid 3 (pri 10) is in running_queue in 91308/91316 dumps (state QUEUED, queue=-1), behind pri 117/118/122 threads; 16251/16253 run_next pops take a 117-122 head. Not yet separated: legit contention vs those threads polling (yield_self/timed wait) due to an audio/VI stub. Next: per-thread blocking-site table at run_next (queue addr / yield kind). Recipe scratch/agent/s4583_rq.sh.
0i. **[s4584, extends 0h]** H-poll refuted: in alloc #2's window every run_next caller is truly blocked on a mesgqueue; pri-122 audio thread alternates Ai queue 0x80149670 / Sp queue 0x8011A420 and hands the CPU to the 117/118 threads (6084+1948 of ~10000 pops); tid 3 runs only when the pri-117 thread blocks on Vi queue 0x80114388 (4 pops). Open: is the Ai enqueue rate per VI frame inflated by our AI drain? Recipe scratch/agent/s4584_rq.sh.

0f. **[s4580, supersedes 0e]** The 7th `rs_malloc(4352)` does NOT block on lock queue `0x8010FEE0`: all ~25k recv/send events are one guest thread, vc always 1->0->1, no blocked recv (3/3 arms, matched-pair control). The run dies right after alloc #7 on `pi.cpp:113` (odd-DMA assert) after the mixer, running inside the count-published/base-unpublished window with count 32 > old capacity 18, feeds ASCII nodes to the PI DMA. The old "blocks at 0x80001B04" PC was a stale global last-guest-pc. A mixer-hold A/B (`ROGUESQ_S4580_HOLDMIX=1`) deadlocks at alloc #2 (hold times out, alloc still in flight): the allocating thread is descheduled mid-`rs_malloc` and the mixer thread is the running guest thread. Next: find the scheduler switch (NEXT.md).

0e. **[s4579, SUPERSEDED by 0f: lock queue is balanced, nothing blocks]** Count 32 is the pre-lock `sh` of the 7th `allocateSongChannelArray`; its `rs_malloc(4352)` blocks at `0x80001B04` (osRecvMessage on lock queue `0x8010FEE0`, BLOCK) and never logs an exit. The mixer is always a separate host thread running during every alloc (same_tid=0, also in successful allocs #2-#6), so concurrency is not the differentiator. Next: log recv/send on `0x8010FEE0` to name the lock holder (see NEXT.md). Single-source for the PC (global last-guest-pc); the missing exit line is independent support.

0d. **[s4577, supersedes the s4571-s4576 record-table framing for the abort]** The bad `musyxRenderVoiceSamples` a0 = voice array 0x801714D0 + 30*0x88 lies past the 18-voice array in a live name-string table (strings written by `rs_strncpy` 0x80007670; render also stores into it); 'late' is name text, not a voice-record writer defect. The loop bound halfword 0x80149700 reads 18 at jal 80000 and 32 at the bad call (81166); last visible guest store is the allocator `sh` 0x8008F0CC (hook `val` column is unusable, always 0). **s4578 resolved it**: host poll shows 32 is the allocator `sh` 0x8008F0CC of a 6th `allocateSongChannelArray` whose `rs_malloc` never returns (no 6th [s4542-alloc]); count is published before base, mixer runs in the window (host write and misread refuted, host_page=0 of 7.76M). Next: which thread/IRQ-mask state lets the mixer run inside that window (see NEXT.md). Arms A,B identical, C died early (3 arms, 2 usable).
0. **[s4572, extends s4571]** Dynamic guest-store watch on the render-record tables (tools/apply_s4572_record_storewatch.py, 3/3 arms identical, control fired in all classes): chunk-2+ records (idx>=count) are written by the SAME render PCs as in-range records (0x8008FF04..9C, 0x8009025C..0x80091000, i.e. musyxRenderVoiceSamples/fillSampleStreamRange itself) = H-render-self; only foreign writes are 6 zero-valued stores at stale wrapper pc 0x80001C18..50 (idx 44/61, host-side/stale attribution, unresolved). Cursor halfwords 0x80149710/12 have a SECOND writer besides the bump (0x80090F24) and reset (0x8009135C): pc 0x80090FE8 (1873 stores) = candidate for the phantom +1. Next: per-PC offset table for words 0..7 of chunk-2+ records and decode 0x80090FE8 (see NEXT.md).
0c. **[s4574]** per-word writer table (3 arms, control present): words 0..7 of voice records (both classes) are written only by bulk fills 0x8001E2C0/E2F0/21EB4, never by render code; H-offset0-7-render and H-hostzero refuted. Chunk-2+ words 8..33 use the same render PCs as in-range. Read side (s4575): no genuine load of chunk-2+ words 0..7 by the 4 hooked render functions (BU/HU/W only; all apparent hits were dest==base hook artifacts) -> H-inert. **s4576**: hook fixed (pre-load address, all load forms incl. LH/LB/LWL/LWR, all of funcs_24.c, 729 loads); 3 arms, positive control (chunk-2+ word 18 loads) present, ZERO loads of words 0..7 in either class -> H-inert closed for funcs_24.c (other funcs_*.c/host readers uncovered). Thread closed.
0b. **[s4573]** 0x80090FE8 decoded statically: post-increment record alloc (cursor=old+1, record addressed by old), a second legitimate bump path, NOT a phantom +1. H-fe8-phantom refuted; open: H-offset0-7-render, H-hostzero (per-offset table build).
0. **[s4571, supersedes the s4570 item below]** The "bad voice index" is NOT bad: `lhu 0($s1)` (0x80090ED8) reads a per-buffer render-record cursor (0x80149710+2*buf), reset once per buffer at 0x8009135C; mix runs in 0xC0-sample chunks from 3 call sites, table cap=(count+1)*3 records, so idx>=count is the normal chunk-2+ case (3/3 arms, control present). Records idx<count read all-zero pre/post; chunk-2+ records hold deterministic non-zero words written by guest code AFTER allocation (zeroing tables at alloc leaves them unchanged and the s4534 bad jal/abort persist; single replicate, arm C died early). Next: dynamic guest-store watch on [tbl0, tbl0+cap*0x88) naming the writer PC of chunk-2+ records, and log words 8..33 for ASCII shape (see NEXT.md, HYPOTHESIS-ID m5-audio-destub).
0. **[s4570, supersedes item 1's framing]** No (count>=30, base 0x801714D0) is ever published (3/3 arms: pairs 20,17,16,15,18 only), so voice 30 is a bad INDEX (single-source, one recipe), not a text-corrupted record. Index comes from `lhu 0($s1)` at 0x80090ED8 in `musyxMixActiveVoices`; next is to log that list entry when index >= count (see NEXT.md, HYPOTHESIS-ID m5-audio-destub).
1. **[s4607, extends s4606] Locate the retail alternate source table.** The retail
512 phase passed the whole-RDRAM control and the phase-gated execution watch at
`0x80007640` fired 2,079 times. The relevant caller `0x80022B44` repeatedly
passed `$a1=0x80165D9C` (105 rows in the bounded capture), an RDRAM pointer;
the other target writer call-site operands were not five distinct literals.
Together with the 76 target-range writes and the same-run controls, this selects
H-alt-source-table over H-direct-callsite and H-host-translation. The source
table's exact five-record layout and the retail-to-port mapping remain open.
Next: phase-gated source-table snapshot/watch around physical `0x165D9C`, joined
to the target writer, to identify the five records and compare their bytes with
the target records. Do not add a mitigation.
HYPOTHESIS-ID: m5-audio-destub.
1a. **[s4606, extends s4605] Identify the retail input to the target writer.** The retail
512 phase passed the whole-RDRAM control and recorded all 76 target-range
writes from one guest PC, `0x80007670`; H-composed-writers and H-host-path are
refuted for this target range. The immediate writer is the same
`rs_strncpy`-family routine seen in the port, but the candidate source span is
all `0xFF` at the hangar snapshot despite 10,933 lifetime writes. Next:
capture the source operand (`$a1`) at the phase-gated `rs_strncpy` entry and
compare it with the five port source addresses. A shared alternate operand
selects H-alt-source-table; five distinct literal or derived operands select
H-direct-callsite; a non-RDRAM or unstable operand keeps H-host-translation
open. The whole-RDRAM control and target-span writer are required in the same
run. Do not add a mitigation.
HYPOTHESIS-ID: m5-audio-destub.
1b. **[s4568, answered by s4569]** Poller on node copy 0x179A64 saw `B04319B8 8019BC90` -> `6C637265 801AB990` in one step at 141.7 s (pair written together; guest_pc 0x80001B08 is a stale wrapper PC, not an attribution). Arm C never mashed (no result). Real writer PC still unnamed: needs a guest-store hook, not the host poller.
1. **[s4567] Name the writer of the ASCII cart word 0x6C637265 in the post-hangar odd-DMA node** (HYPOTHESIS-ID: m5-audio-destub). s4567 (scan fixed to match guest word): node is {len 0x300, cart 0x6C637265, ram 0x8019C990} in 3 RDRAM copies (0x1120B0, 0x179A64, 0x17DBC8, last followed by ASCII 'late'); Start-mash triggers it, a single Start reaches hangar clean (single-run per arm). Next: write watch on those copies for the first writer PC, plus a hangar-only Start-count arm. See NEXT.md.
1b. **SUPERSEDED by s4565 (hangar IS reachable with a 5 s Start mash; s4552 blamed the route, the recipe fired all keys before the title)** [s4552: 420 s late-route, 2 arms, 0 crashes, odd=0, but VI 1024 for ~400 s and VI 512 never reached; hangar-reach via autopilot is CLOSED until the route/menu input is fixed. Move to M5 audio de-stub.]** Prior text: Hangar-length run with the ring-lap fix default (HYPOTHESIS-ID: wild-setcimg-writeback). s4549 made `ROGUESQ_DPC_WRAP_FLUSH` and `ROGUESQ_S4272` default ON (restore already was); the wild SETCIMG origin is the s4283-s4287 ring-lap overwrite, not a port misparse (supersedes the "writer unnamed" wording). s4550: pre-hangar 175 s run confirms odd=0 (control 60) but never reached VI 512, so the hangar question stays open; s4551: the early route (`3:start,6:start,...`, recipe `s4551_hangar.sh`) reaches the title in both fix arms but both then die at `musyxSynthFrame+5436`, so the hangar is blocked by the parked pool-link crash on that route and by time on the late route; next needs either a run with the +5436 walk guarded/avoided or a longer late-route run (>=300 s). Open: does a >=150 s default run show hangar-phase odd cimgs / fb-set growth gone (s4287 Q1, unmeasured). thr11d benefit of the old allow stays unmeasured (s4547). Recipe `scratch/agent/s4549d_defaults.sh`.
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
- **s4558 (2 arms, control present): the 0x8001E2C0 clear loop wrote 0x80179510 once, at vi=640, into its own correctly-sized array (0x80179480, N=0x800); that array was freed by coalesce at vi=640, and the audio list link written by 0x8008F7C8 predates it, so node 0x80179510 is a dangling pre-640 audio node, not a live overwrite. Supersedes the s4555 "overlap" framing. Open: owner/free of the memory under the audio list when it was built.**
- **s4557 (offline re-read of s4556 logs, 2 arms agree; single-source = [s4465-hdr] store log + recompiled source, control s4457-control present): the 120 KB block 0x801767E0 IS released, just not via the hooked rs_free. Its header flags go 2->1 at guest pc 0x800023AC (inside syms-named `coalesceFreeHeapBlocks`, 0x800022F8, called from 0x80001430; function stores its a0..a3 into globals 0x8010FF08.. and re-walks the heap from head) at log line 1381, BEFORE the nested mallocs 0x801793F0 (line 1507), 0x80179480 (28392), 0x80179380 (309340). So the nesting is legitimate allocator behaviour; the s4556 "never freed" claim is SUPERSEDED (it only grepped [rs-free], which does not see this path). Open: why does the +5436 corrupt-link writer (initTextureLUTAndAllocBuffers clear loop, s4555) overlap the live 73728-byte block 0x80179480..0x8018B480?**

## Update s4559 (supersedes s4556-s4558 heap-corruption chain)
The audio list at 0x80179510 is legitimate (built at vi=1024 in space freed by the LUT block coalesce); no corruption, no dangling node. The last allocator event before the 2/2 crash is rs_malloc size=24 flags=0x4 -> ptr=0, then a deref of the NULL result (si_addr 0x37ffffff2). Single-source (s4559 armA/armB). Next: why that malloc fails (free-list/heap-end state at the NULL return vs retail).

## Update s4560 (supersedes s4559's "last malloc NULL -> deref" and "audio list legitimate" as complete accounts)
The s4559 NULL-deref crash was our own `[rs-hdr]` print (guarded now). flags=4 mallocs return NULL 833x (2/2 arms) because the guest gate `[0x80037560+0x44] & 0x80` (word 0x2C0, writer 0x800C59B4) blocks the per-frame scratch-region rebuild; not heap exhaustion. After 0x800A9BD8 resets the word to 0x40 the guest frees the audio blocks (0x80179380 list nodes, 0x801714D0 voice lattice, ...) and reallocates over them; `musyxSynthFrame+5436` then walks the stale link. Hypothesis (ordering observed, thread liveness not yet measured): use-after-free by the audio thread. Next: who frees 0x80179380 (host backtrace) and what quiesces the audio thread in retail. Detail: PORTING-STATE s4560, NEXT.md.

## Update s4561 (refines s4560 hypothesis)
Frees of 0x80179380/0x801714D0 come from the main thread (guest shutdown span inside `waitForMusyXAudioTaskDone`<-musyxNoopStub<-runVideoFrameTick); the crash is on viRetraceHandlerThread (`musyxSynthFrame+5800`). Synth ran 10610 entries across both teardowns with gate byte 0x800A0F50=1 at the free (use-after-free race: H-not-uaf refuted). Not yet split: retail-has-same-window vs port-missing-quiesce; H-stale-head open. Next: static order of gate write vs frees in that span. Single-source (s4561 armB).

## Update s4562 (supersedes s4561 'next')
Static: gate 0x800A0F50 is cleared AFTER the frees in musyxNoopStub (guest has no quiesce; H-quiesce-missing refuted). Pausing musyxSynthFrame across the wait (tools/apply_s4562_synth_pause.py, ROGUESQ_S4562_PAUSE=1, default off) leaves the crash unchanged in the A/B (both +5688 at ~180 lines after teardown 2) -> the stale link persists beyond the free window; H-stale-head is the lead. Next: log the list-head load at the crash site vs re-init (NEXT.md).

## Update s4564
400 s A/B: skip on = 0 crashes (phase 9, viw=640, hangar=0); skip off = 36 crashes (first zcfree<-inflate_trees_free). Skip holds, but hangar is not reached; next: why (see NEXT.md).

## Update s4563 (supersedes s4562 'next')
musyxSynthFrame+5688 crash = walk of stale audio-list head 0x801499B0 (still points into freed block 0x80179380..0x8017970C; guest realloc fill pc 0x8001E2C0 corrupts node next) for ~5 synth calls until guest init zeroes the head. tools/apply_s4563_stale_head_skip.py (default ON, ROGUESQ_S4563_SKIP=0 disables; re-apply after regen with the s4561/s4562 scripts) skips the frame in that window: same-run A/B, A 0 crashes in 150 s (x2), B crashes (x2). Next: longer soak with skip on to find the next death; arm B once crashed at viRetraceHandlerThread+9296 (unexamined).


### s4581 addendum (m5-audio-destub)
Allocator thread (gtid 3, pri 10) is preempted inside rs_malloc at the lock osRecvMesg->check_running_queue by the already-queued pri-122 audio thread (entry 0x8008ED70); alloc #1 window had 0 handoffs, alloc #2 has the first. Single-source (3 identical arms). Open: who readied it and why retail's audio thread isn't mixing during reapplyAudioConfig. Tool: tools/apply_s4581_switchlog.py + ROGUESQ_LOG_S4581=1.

- s4585: Ai-source enqueue to queue 0x80149670 is exactly 1.00 per VI frame (guest self-sends 0; Si 0.82, Sp 0.47/VI). Message inflation is NOT the cause of allocator starvation; see scratch/agent/NEXT.md.
