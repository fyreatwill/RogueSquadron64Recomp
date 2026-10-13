# Rogue Squadron 64 Recomp — current truth

**s4791: 3 sequential 300 s default-binary runs (s4786 recipe, same binary as s4787) ALL stalled at VI 640 (update_screen frozen ~#250, vi-fs `stalled=1`), 0 crashes, 0 VI 512; s4787 reached 512 2/2 on that binary, s4790 0/2. Stall is nondeterministic/load-sensitive (single-source), not a flag/binary difference. Next: one `sample <pid>` at +60 s to see what the frame producer is blocked on (NEXT.md).**
**s4787: the default PAUSE=4 binary reaches VI 512 (0x00690400, dlwalk phase 6, ~100 s) UNATTENDED, 0 crashes in 2 x 240 s; the hangar origin is never needed. The old "zero `res=0x2C` rows" nulls (s4760 etc.) were void: the `[ovl-route]` logger had no 0x2C branch (fixed s4787; control: 152 rows, n=8704 by task 407 in the title phase). `dlwalk-2c arrivals2c` is DL-side and identical for DROP=0/1, so it is not a splice readout. New-binary runs under host load 14 stalled in VI 640 / startup-crashed at spTaskSchedulerThread+9632 (load-sensitivity, single-source). s4788 (2 runs, host load 10-13): VI 640 stall, then spTaskSchedulerThread+9632 startup crash; no 0x2C data, load explanation still single-source. Next: rerun scratch/agent/s4788_drop1.sh at load < 4 -> `res=0x2C` rows in phase 6.**
**s4786: PAUSE=4 CONFIRMED and now DEFAULT-ON (tools/apply_s4562_synth_pause.py; `ROGUESQ_S4562_PAUSE=0` rolls back). 544 s soak: 7 hold/release pairs, 0 crashes (baseline crashed +5808 at ~80 s); env-unset 150 s check: 4 releases, 0 crashes, VI 512. The +5808 family is closed for the idle title/hangar route (arena recycling under a ticking synth = port-only ordering, ORIGIN s4783/s4784). Next: rerun the key route to mission and look for res=0x2C rows (s4761 blocker; PAUSE=2/3 negatives were void, see s4785).**
**s4785: `ROGUESQ_S4562_PAUSE=4` (hold the synth pause past the gate clear, release at guest `initSampleStreamBlockCache` return 0x8008F958 = retail audio re-init end) removes the `musyxSynthFrame_s4562_impl+5808` crash: baseline and PAUSE=3 both crash at ~80 s, PAUSE=4 ran 120 s through 4 teardown windows and reached VI 512 (n=1/arm; 600 s soak queued). Also: installed funcs_24.c had silently lost the PAUSE=2/3 code, so post-regen PAUSE=2/3 negatives (incl. s4761) are void; apply_s4562_synth_pause.py now upgrades it. Next: confirm via soak, make PAUSE=4 default-on, then retry the 0x2C splice route. Tools: tools/s4785_reinit_end.py.**
**s4784: port in-window ordering matches retail (32/32/13 and 32/14/0 synth ticks BEFORE the free burst, 0 after, 3 teardown windows x2 runs), but the first synth tick lands 0 rs_malloc after the gate clear (retail: 32-44 mallocs first, 8/8). Ticks come from a separate host thread (synth tid != noop tid), so the post-clear tick over the half-rebuilt audio arena is port-only concurrency; this is why PAUSE=3 (release at gate clear) still crashed. Next: hold the s4562 pause until the guest re-init end (NEXT.md). Tools: tools/apply_s4784_gap_order.py, tools/s4784_gap_order.py.**

**s4783: retail ordering inside all 8 musyxNoopStub windows: 6-9 synth ticks during the yielding wait, then the rs_free burst, then the gate clear; ZERO synth ticks between first free and clear, and 32-44 rs_malloc (full audio re-init) run before the next synth tick (8/8, controls: synth 5019, malloc 18901). Retail never ticks the synth on the freed arena; the port does (+5808 crash). Next: port-side ordering + quiesce synth dispatch across teardown->re-init (NEXT.md). Tools: tools/s4783_noop_window.py, s4783_noop_gap.py.**

**s4782: CORRECTS s4780/s4781. The burst-free that recycles the audio arena is NOT shutdownAudioEngine: the `[audio-wait-spin-exit]` print has a twin in waitForMusyXAudioTaskDone (funcs_24.c:9584), called only from musyxNoopStub (0x8008ED00, via runVideoFrameTick). Port run: shutdownMusyXEngine and shutdownAudioEngine entry hooks fired 0 times (control shutdownMusyXVoices fired 2) while spin-exit fired 3. Retail oracle (85 s driven, control synth 5020 hits): musyxNoopStub runs 8 times and ALL 8 take the gate-nonzero path (0x8008ED14 -> 0x80091EB0 -> clear gate 0x8008ED44). So the free burst is retail-legitimate; the port divergence is what happens AFTER it (synth still running over the freed arena, 73728 alloc). Next: NEXT.md.**

**s4777: iteration BLOCKED - the +5808 disassembly needs lldb/objdump allow rules (see scratch/agent/BLOCKED.md). Unit unchanged.**
**s4776: 4th identical death (si_addr 0x38000950e = rdram base 0x300000000 + unmasked guest 0x8000950e in x9) at +5808, VI 640 0x696100, at load ~9; same si_addr across s4672/s4761/s4764/s4775/s4776, so Hload is unsupported (never tested at load<3). Next: identify the guest instruction/register at +5808 and the writer of 0x8000950e.**

**s4780: the arena recycling is freed-block reuse, not allocator overlap: on the VI-640 phase-3 crash route shutdownAudioEngine's rs_free burst releases the audio blocks (0x801793F0..), `rs_malloc(73728)=0x80179480` takes them 18 log lines before the first `[s4779-unhooked]`, and the audio blocks are re-allocated ~215k lines later while musyxSynthFrame stays registered (dereg is only in shutdownMusyXVoices). s4771/s4772 "never reaches shutdownAudioEngine" holds for title/hangar only. Next: retail oracle ordering of shutdownAudioEngine / musyxSynthFrame / re-init (NEXT.md). Tool: tools/s4780_arena_alloc_analyze.py.**

**s4779: the +5808 corrupt link is arena RECYCLING, not a stray writer: at VI 640 phase 3, ~18 pointer words of the audio node arena 0x80179400-0x8017B000 turn 0x8017xxxx->0x0000xxxx in one walk interval, then hold unrelated data (2 runs, `[s4779-unhooked]` shadow scan in rs64_s4457_list_check, single instrument). Callback table stayed [3250,123C,0,0] with no dereg, so duplicate-registration (s4762) is NOT the cause. Next: name the allocation/loader that takes 0x80179480 (s4558 heap-overlap lead). ROGUESQ_LOG_M5_CALLBACK_ENTRY+WRITER together crash boot.**

**s4778: `musyxSynthFrame_s4562_impl+5808` = guest `0x80091368 lhu $v0,0x10($v1)` (funcs_24.c:7112) in a linked-list walk; $v1=0x94FC, a corrupt list link (not a codegen/mask bug). Asm for any TU: `cd build && make Users/.../RecompiledFuncs/funcs_24.c.s` (no lldb/objdump). Writer of the bad link still unknown.**

**s4775: the hangar-gated menu walk (scratch/agent/s4776_gated_menu_walk.sh) crashed 3/3 at `musyxSynthFrame_s4562_impl+5808` (VI 640 0x696100, ~77 s) before the hangar appeared, so no key was sent. Title arrived at ~50 s vs 15 s in fast runs, machine load ~8: the crash looks load/timing sensitive (single-source). Rerun on a quiet machine.**

**s4774: 0 of 4 mission-route drivers on the spliced binary reached mission
origin `0x00690400`.** The phase-gated probe.sh driver (180 s, 149 VI-512 rows)
and two runs of the s4753 winctl Start/A recipe all stopped at hangar
`0x006AB400`; `res=0x2C` rows 0, `arrivals2c=0` on 460 dlwalk rows, no
crash. One earlier width-512-gated attempt died with a Bus error before any
phase (single occurrence, unanalysed). Splice effect remains unevaluable;
wall-clock key mashing is not a reliable route (s4753 and s4759 each reached
mission once). Next: derive the hangar->mission trigger instead of mashing.

**s4773: the compiled overlay-0x2C splice passed build validation but the
existing mission recipe did not reach the mission route.** The exact
`../N64Recomp/build/RSPRecomp factor5_rsp_ovl2c.toml` command exited 0 and the
generated source contained both the resident `OVL2C_1DB0` body and its
`0x153==0x2C` dispatch. The Debug port target also built successfully. The
phase-gated run reached VI 512 at 23.6 s, but every observed 512-wide phase
was hangar origin `0x006AB400`; mission origin `0x00690400` and direct
`res=0x2C` rows were absent. No crash, abort, assertion, or unhandled marker
occurred. This is a qualified build/phase positive control with the splice
effect unevaluable, not evidence for or against H2C-real-image. Artifact:
`scratch/agent/s4753_unpaused_mission_capture/`.

**s4772: the shutdownAudioEngine caller census found one teardown-only caller.**
The generated tree contains exactly one executable call to `shutdownAudioEngine`
at `0x8008ECB8`, from `shutdownMusyXEngine` (`0x8008ECA4`), and it is guarded
by `0x800A0F50 != 0`. The companion symbol/call metadata contains no other
direct caller, address-taken reference, wrapper, or alias beyond the normal
definition/overlay-registration entries. This selects H-shutdown-only-init for
the covered title/hangar route: the surviving duplicate callback is not a
shutdown artifact. No runtime change or deregistration change is authorized.
Evidence is static/generated-source plus companion symbol metadata; a new
shutdown-triggering route would require a separate target-PC witness.

**s4771: the qualified title/hangar route never called shutdownAudioEngine.**
The retail oracle first qualified the callback machinery with 10,002
whole-RDRAM writes and two callback-table writes, including two
`registerSiCallback` executions. The rebuilt port then reached title VI 1024
and hangar VI 512 with no crash/abort; the new teardown event fired nine
registration controls but zero shutdown-entry rows. Independently, the
existing table trace saw first-match deregistration at target phases,
`[3250,123C,123C,0] -> [3250,0,123C,0]`, leaving the duplicate live. This
selects H-no-shutdown-route for the covered route and confirms the duplicate
survivor, but authorizes no deregistration change. Artifacts:
`scratch/agent/s4771_oracle_groundtruth.log` and
`scratch/agent/s4771_m5_callback_teardown_run3.log`.

**s4770: VI-retrace callback dispatch is all-live-slot on the qualified route.**
The rebuilt default-B40 phase-gated run reached title VI 1024 and hangar VI
512, fired 3,593 VI-loop rows and 14,368 callback-slot rows, and had no crash
or abort. The dispatcher read duplicate live `0x8009123C` entries in slots 1
and 2 during target phases; its `target=1` rows totaled 7,076, exactly
matching 7,076 independent `synth-entry` rows. The loop marker is the positive
control, and the slot walker plus synth entry provide two lines of evidence:
H-dispatch-all is selected for this route; H-first-live-slot and H-stale-source
are rejected. No dispatcher or deregistration change is authorized. Artifact:
`scratch/agent/s4769_m5_callback_dispatch_run/`.

**s4768: the callback-dispatch ordinal experiment remains a checkpoint, not a
result.** The prior retry did not rerun the experiment or create a runtime
artifact; see the s4768 ledger entry for the same unevaluable hypotheses.

**s4767: the A12 loop witness reached the wait copy but not the shutdown copy.**
The rebuilt default and `ROGUESQ_AUDIO_SPIN2_YIELD=0` arms both reached title VI
1024 and hangar VI 512 with no crash or abort. The new positive-control witness
fired in `waitForMusyXAudioTaskDone` at `0x80091F34` three times per arm, each
time reading gate 0 and returning; it never observed a nonzero spin or yield.
The `shutdownAudioEngine` copy at `0x80091DC4` never fired. Thus the covered
route qualifies the wait-copy branch as reached with an already-clear gate and
leaves the shutdown-copy route absent; no writer or gate hypothesis is
selected. Artifact: `scratch/agent/s4766_m5_a12_second_wait/`.

**s4766: the A12 default/rollback validation reached title VI 1024 and hangar
VI 512 in both arms with no crash or abort. The existing wait-contract witness
returned from the countdown/tick path in both arms, but the second-wait loop's
yield/clear/return branch was not independently marked: `[waitmusyx-spin2-arm]`
is the producer arm site, not loop execution. Therefore the route is valid but
H-A12-producer, H-A12-route-absent, and H-A12-wrong-writer remain unevaluable;
no behavioral selection or further gate change is authorized. Artifact:
`scratch/agent/s4766_m5_a12_second_wait/`.

**s4765: the second MusyX wait gate was de-stubbed in the regeneration path and
live generated `funcs_24.c`: both `0x8014974C` busy-spin copies now yield to the
VI/audio producer by default, with `ROGUESQ_AUDIO_SPIN2_YIELD=0` as rollback.
The Debug target rebuilt successfully. No runtime selection is claimed yet; the
phase-gated default/rollback soak is next. ORIGIN: `musyxSynthFrame` arms and
clears the legitimate gate, so this restores scheduling without forcing its
value.

**s4764: the callback-dispatch cardinality capture reached title VI 1024
(`0x00790400`) but later fell back to VI 640 and crashed in the known
`musyxSynthFrame_s4562_impl+5808` family before hangar VI 512. Registration,
deregistration, callback-table, phase, and synth-entry controls fired; the
callback census only sampled table changes (`n=0,1,2`) and did not count
dispatch invocations. Duplicate `0x8009123C` slots and continued synth entries
were observed, but H-dispatch-all, H-dispatch-first, and H-stale-entry remain
unevaluable. This is a target-route audio crash/reachability result, not
evidence for a dispatcher change.

**s4763: the compiled default-B40 callback witness reached title VI 1024 at 15.1 s and hangar VI 512 at 24.3 s, with no crash or abort. Registration, deregistration, synth-entry, and phase controls all fired (14/5/20 samples); target-phase synth entries still observed the table containing duplicate `0x8009123C` slots after first-match removal. This qualifies target-route reachability and leaves callback-dispatch semantics as the next discriminator; no mitigation or dispatcher change is authorized.**

**s4762: the compiled callback-table witness registered `musyxSynthFrame` twice, then `findAndZeroTableSlotMatching(0x8009123C)` cleared only the first slot (`[3250,123C,123C,0] -> [3250,0,123C,0]`); later synth entries still observed the remaining callback. Registration, deregistration, synth-entry, and callback-census controls fired, but the route stalled at VI 640 and never reached title/hangar. This qualifies the duplicate-registration/first-match mechanism on the covered boot route, not target-phase dispatch behavior; no mitigation or dispatcher change is authorized.**

**s4761: the required hangar-gated key route never reached VI 512: the ordinary arm crashed at `musyxSynthFrame_s4562_impl+5808` while still at VI 640, and the documented `ROGUESQ_S4562_PAUSE=2` retry crashed at the same site. Both had phase/log positive controls and zero usable `res=0x2C` or mission-origin rows. The 0x2C splice remains unevaluable; this is an audio-route reachability blocker, not evidence against the splice.**

**s4760: the prescribed long key-mash route-selection arm crashed at startup in `spTaskSchedulerThread+9632` (guest PC `0x8000834c`) before any VI 512 phase, with zero `res=0x2C` rows. The repaired direct-driver control completed cleanly but reached only hangar origin `0x006AB400`, not mission origin `0x00690400`, and also had zero `res=0x2C` rows. The 0x2C-producing input route remains unresolved; this is a route/input-timing blocker, not evidence against the splice.**

**s4759: the repaired executable linked and the phase-gated direct mission driver reached VI 512 origin `0x00690400`, produced all eight requested captures, and had zero crash/abort or DL runaway rows. The compiled ucode contained `OVL2C_1DB0`, but the same run recorded zero `res=0x2C` overlay dispatches; only 0x0C/10/14/18/1C/20/24/28 routes appeared. This is a qualified positive-control run but leaves H1/H2/H3 unevaluable because the covered input did not exercise overlay 0x2C.**

**s4753: direct interleaved Start/A input reached VI 512 hangar at 24.0 s and mission origin 0x00690400 at 52.5 s; eight post-gate frames were unpaused and showed ship, HUD, radar, terrain, and reticle with no crash/abort. This refutes H1 (“ship/HUD entirely absent”) for the covered route; H2 (independent terrain divergence) remains unevaluable without retail pixels. Single-source port capture with independent phase and no-crash controls.**

**s4755: the prior RSPRecomp block was false. The installed local tool accepted `factor5_rsp_ovl2c.toml` without a permission change and emitted the 85,853-byte `factor5_ucode_ovl2c_recompiled.c` with the expected entry point and jump table. The real splice and phase-gated validation remain the next work unit.**

**s4754: the planned real overlay-0x2C splice did not run because the required RSPRecomp invocation remains blocked by the human allow rule. No command retry or experiment was performed. Resume only after adding the Bash allow rules named in `scratch/agent/UNBLOCK.md`; the refuting control is an allowlisted RSPRecomp run that emits C for `factor5_rsp_ovl2c.toml`.**

**s4749: DL op 0xBD present <=> 0x2C arrival <=> runaway, 150/150 vs 0/550 non-runaway tasks (phases 2-7); phase-7 runaways have exactly one 0xBD and one arrival. No normal task contains 0xBD, so TexrectGen content (likely ship/HUD texrects) is exactly what the unspliced 0x2C overlay loses. Single run, agrees with s4747/s4748. Splice blocked on RSPRecomp allowlist (human).**

**s4748: the first 0x2C dispatch is DL op 0xBD (TexrectGen): ring snapshots of 3/3 phase-7 runaway tasks end ...0x15A4 (d153=0x28, prevop 0xBD) -> 0x1298 -> 0x1DB0 (d153=0x2C, prevop 0xBD); normal task 41 ring has no 0xBD. Single run, ring depth 8; per-task 0xBD count for normal tasks NOT yet measured.**

**s4747: a DMEM 0x153==0x2C arrival at 0x1DB0 occurs in 142/142 runaway tasks and 0 of 387 listed non-runaway tasks (phase-3 runaways ~13 arrivals each; phase-7 mission runaways exactly 1 each). One unrouted-0x2C dispatch starts the restart loop; it is not a per-object count. Phase-7 4-16k-fetch "mid" tasks have 0 arrivals, so they are slow for another reason. Single run; ship/HUD effect of a splice still untested (allowlist).**

**s4746: runaway DL restarts (0xBD->ovl 0x2C->0x1DB0) are NOT mission-only, and s4737/s4738 mislabelled them "mission" (that log's tasks were phase 3, VI 640). Per phase (s4746_phase, single run, per-phase budgets): runaway tasks 0 in phases 2/4/5/6, 14 in phase 3, ~65% (105/150) in phase 7 mission (512 @0x690400), each costing >=4-5x a normal 3.0-3.5k-fetch task (16384 cap). Phase map: 2=320, 3=VI640, 4=title, 5=hangar, 6=VI640 0x6A2900, 7=mission.** Whether the splice restores ship/HUD stays untested (needs allowlist).

**s4743: overlay 0x2C image is closed-form: only externals L_10D8/L_112C, no jal/jr, no absolute 0x153 store (static, control ovl1c OK); fixup 6r drafted at scratch/agent/fixup6r_draft.py, unwired pending RSPRecomp allowlist.** **s4738 (top, supersedes s4737 edge reading): DMEM 0x153==0x2C reaches unrouted window entry 0x1DB0. s4737 detail: runaway DL tasks restart via L_1DB0.** The refill source 0x30(r18) is re-seeded to the task root (740AD8) by the store `sw 0x30(r18)` at L_1DB0 (site 3), after an end-DL at depth 0; chunk link 744078 is truly 0, so the cycle is not in the data (kind-6 probes, positive control task 41/42 passed; single run, 3 runaway tasks agree). Normal tasks hit site 3 once (entry); runaway 10-14 times. **s4740: overlay 0x2C = real 0x240-byte VU image, ROM 0x27368, dest 0x1DB0 (runtime table dump + ROM bytes; ovl24 control matched). Unspliced, so the window entry restarts the task. Next: splice it (NEXT.md).**

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
history migrated to [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) §59 and earlier
archive sections. Updated for session 4772; old log archived in PROJECT-OVERVIEW.md.

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

Session 4680 completed the Step 7 writer census on the qualified route. Retail
and port both
reached title `0x00790400` and hangar `0x006AB400`, and the retail
whole-RDRAM control reached 10,000 callbacks. Port phase 5 entered
`serviceVoicePoolFrame` reached the target phase and the port store witness
recorded the same slot at `0x8009B7CC` as `0x02 -> 0x03`, followed by
`0x8009B7EC` as `0x03 -> 0x00`. The retail oracle independently attributed
the same publish/reap PCs in hangar, and the whole-RDRAM and store controls
fired. This selects H-status-writer for the covered route: the named service
worker is the legitimate zeroing writer. Shutdown call-3 did not execute in
the target phase, so that boundary remains unevaluable; no wait change or
forced clear is authorized. Artifact: `scratch/agent/s4117_m5_status03_silent/`.

Session 4681 completed the Step 8 A10 audit. The generated census found 43
song-tempo table guards in `funcs_25.c` and one voice-list-node guard in
`funcs_26.c`. The named guest writer `0x80096D88` published the in-range
pointer `0x80149A00`; all observed list pointers were also in KSEG0. Guard-on
and guard-off arms from one build both reached title `0x00790400` and hangar
`0x006AB400`, with real audio dispatch, service activity, and nonzero PCM at
both source and consumer boundaries, and neither crashed or aborted. Retail
independently fired the whole-RDRAM control (13,001 writes), the target write
(3,001 writes), and writer-PC execution watch (6,002 hits). This selects
H-A10-valid for the covered route; no guard relaxation is authorized.
Artifact: `scratch/agent/s4681_m5_a10/`.

Session 4682 completed the conditional M5 Step 10 AI/SDL boundary audit. The
independent retail run passed its whole-RDRAM control and showed nonzero AI
activity in its title/hangar family. One rebuilt port binary ran image and
silent arms concurrently; both reached title `0x00790400` and hangar
`0x006AB400` without crash/abort. Image PCM remained nonzero and hash/length
consistent from `ai-output` through source and consumer to SDL queueing; the
silent arm supplied the same-run zero-output control. This selects
H-AI-bridge-valid. No AI or SDL change is authorized, and M5 Steps 4–10 are
now qualified or closed on the covered route. Artifact:
`docs/M5-S4682-AI-SDL-BOUNDARY.md` and
`scratch/agent/s4682_m5_ai_sdl_boundary/`.

Session 4683 completed the static backward non-self zero-offset `MEM_H` audit.
The prior work order's 19-site count was stale for the current external
generated snapshot: two independent interval scans found the same 97 signed
halfword load sites (with different nested-loop grouping), out of 160 total
non-self zero-offset loads. The complete table in
`docs/M3-S4683-MEMH-CENSUS.md` shows scalar index, interpolation, animation,
geometry, text, or audio-coefficient consumers at every site; none is an
unscaled guest-pointer dereference or a named invalid-pointer writer. This
selects H-MEMH-bounded and authorizes no guard or mitigation. Evidence is
static/source-only; a runtime probe is not warranted without a new
site-specific symptom.

Session 4684 completed the analogous `MEM_HU` census. Two independent direct
load enumerators agreed on 1,104 zero-offset loads; backward-edge analysis
found 521 loop sites and 440 non-self sites across 36 generated files. The
complete reproducible TSV emitter is `tools/census_memhu.py`, with the scope
and classification record in `docs/M3-S4684-MEMHU-CENSUS.md`. Every candidate
is a halfword scalar/status/table read; no named writer plus pointer
reconstruction was found. This selects H-MEMHU-bounded and authorizes no
guard, mitigation, build, or runtime probe.

Session 4685 completed the analogous `MEM_B` census. Two independent scans
agreed on 35 direct zero-offset loads; 22 were in backward loops and 12 were
non-self sites across 9 files. The complete table in
`docs/M3-S4685-MEMB-CENSUS.md` classifies every candidate as a scalar,
packed-field, or byte-copy data read; the five `bcopy_recomp` sites advance
data pointers but do not reconstruct a pointer from the loaded byte. No named
invalid writer was found. This selects H-MEMB-bounded and authorizes no guard,
mitigation, build, or runtime probe.

Session 4686 completed the analogous `MEM_BU` census. Two independent count
paths agreed on 861 direct zero-offset loads; 602 were in backward loops and
515 were non-self sites. The complete reproducible table in
`docs/M3-S4686-MEMBU-CENSUS.md` classifies every candidate as an unsigned-byte
scalar, index, packed field, table, flag, checksum, text, geometry, or audio
data read. The nine local review rows were manually resolved as nearby
unrelated loads or byte indices; no named guest writer publishing a pointer
was found. This selects H-MEMBU-bounded and authorizes no guard, mitigation,
build, or runtime probe.

Session 4699 (supersedes the A7 gate claim): `musyxSynthFrame`'s read of gate
`0x800A0F50` (0x800912AC) skips only `update3DAudioFrame`; the voice-list walk
is unconditional, so releasing the s4562 pause at the guest gate-clear store
(PAUSE=3) still crashes 2/2 (control crashes, PAUSE=2 clean). The s4672 crash
is a synth callback walking audio blocks freed at shutdown. Open lead: retail
`shutdownAudioEngine` deregisters the synth from the 4-slot VI-retrace callback
table via `findAndZeroTableSlotMatching(0x8009123C)`; check that the port's
retrace dispatch honours it (see scratch/agent/NEXT.md).

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
and the next M3 unit must be a different complete idiom class. (s4718: FPR/LL-SC census closed the last candidate class; tools/census_fpr_llsc.py.) (s4717: jalr/jr indirect-call class closed — all 113 register-target + 28,185 constant sites go through get_function, which fails loud; tools/census_indirect_calls.py.) (s4716: swl/swr/sdl/sdr/ldl/ldr census closed the unaligned-access classes; see PORTING-STATE s4716.)

Session 4675 completed a fresh M3 census of backward loops containing a
non-self zero-offset pointer transition (`MEM_W(ctx->rN, 0)`). It found 399
sites in 22 files and 212 functions; 326 are already instrumented/guarded
regions, while the 73 untouched sites contain 71 explicit loop/sentinel or
count-bound transitions and two bounded `bcmp_recomp` loops. The same scan
located the existing `rs_malloc`, `buildHeapFreeList`, and
`coalesceFreeHeapBlocks` guard controls. No new named writer-to-noncanonical
path was found. This is static, single-source evidence only; no guard or
mitigation is authorized. Artifact: `scratch/agent/s4675_indexed_census.md`.

Session 4689 ran the prescribed same-phase M4 retail-witness capture. The port
controls fired (stage 1 = 64; phase-5 stages 10/11/12/13 = 517/517/517/497)
and reached hangar `0x006AB400`. Retail independently passed the whole-RDRAM
control (197,474,334 writes), reached the same 512-wide origin, and wrote both
watched colour-buffer regions. The Rice/HLE oracle has no RSP accumulator or
DMEM witness, so no retail VMADH/VGE/store tuple exists; this selects
H-M4-unreachable as an instrument-boundary result, not a retail route null.
The accumulator comparison remains unevaluable and no mitigation is
authorized. Artifact: `docs/M4-S4689-RETAIL-WITNESS.md` and
`scratch/agent/s4689_m4_retail_witness/`.

Session 4690 ran the new external-retail-entry handoff capture. The oracle
whole-RDRAM control, title, and hangar phase controls all fired; its exact
voice-span writer buckets were empty in both requested title/hangar phases,
while the full-run writer histogram only showed pre-target-route activity.
The watched retail consumer `0x800903F0` had zero hits. The port reached title
but not the qualified hangar origin before the known
`musyxSynthFrame_s4562_impl` bus-error family; its exact-span rows were only
phase 3 at `0x00696100`, and its phase-gated `0x800903F0` consumer had zero
rows. Adjacent-range and writer controls were positive. This selects
H-route-absent for the requested handoff phase, not a retail writer or
FE98/PI bridge corruption. No mitigation is authorized. Artifact:
`docs/M5-S4690-EXTERNAL-ENTRY.md` and
`scratch/agent/s4690_external_entry_handoff/`.

Session 4691 completed the M5 A11 wait/slot boundary capture. The rebuilt
real-audio/LLE port reached title and hangar controls; in phase 5 it entered
`waitForAnyAudioSlot` three times, returned three times with active mask
`0x11`, and fired no 500,000-iteration cap. Retail independently passed the
whole-RDRAM control, reached the same hangar origin, wrote the status-table
range, and executed the named `0x8009B7CC`/`0x8009B7EC` service writers six
times each. This selects H-A11-slot-writer-valid for the covered route: keep
the cap and make no wait change. Artifact: `docs/M5-S4691-A11-WAIT-BOUNDARY.md`
and `scratch/agent/s4691_m5_a11_wait_boundary/`.

Session 4692 completed the M5 A12 wait boundary. The rebuilt real-audio/LLE
port reached title/hangar controls, entered `waitForMusyXAudioTaskDone` five
times, and each default yielding wait observed countdown `16 -> 0` and
returned; no pump cap, spin timeout, crash, or abort fired. The separate
`0x8014974C` diagnostic saw flag zero on entry, so that spin was not reached
in the target phase. Retail independently passed whole-RDRAM, title, and
hangar controls and executed all four candidate countdown-writer PCs, with
24,219 writes to the flag range and 425,205 writes to the adjacent state
range. Its exact `0x14998A` countdown watch was zero-hit; phase rows placed
`0x800916A4` at adjacent `0x149988`, so retail confirms the writer/state
family but not the exact port field mapping. This selects H-A12-countdown-
writer-valid for the covered port route and closes the separate-flag spin as
a route blocker; no wait or spin change is authorized. Full evidence is in
`docs/M5-S4692-A12-WAIT-BOUNDARY.md`.

Session 4693 completed the M5 A13 drain boundary. Both same-build port arms
reached title and hangar. Default-off entered with active `0x02` slots,
reached an all-zero slot snapshot, and returned at 100,000 iterations with
no timeout; explicit `ROGUESQ_DRAIN_INLOOP_TICK=1` kept nine slots at `0x02`
and hit the 10,000,001-iteration timeout. Retail independently passed
whole-RDRAM, title/hangar, target/adjacent status-range controls, and executed
`0x8009B7CC`/`0x8009B7EC` six times each. This selects
H-A13-retail-status-reap for the covered default route and rules out the
in-loop tick as needed; the timeout guard and default-off policy remain
unchanged. Evidence: `docs/M5-S4693-A13-DRAIN-BOUNDARY.md`.

## Active frontier

Session 4773 adds a qualified build and hangar-phase control to the
overlay-0x2C route attempt. The splice is present and the run is crash-free,
but the existing input recipe stops at hangar origin `0x006AB400`; it never
provides the mission-origin or direct `res=0x2C` discriminator. The splice
effect remains unevaluable. A new mission-route recipe is required before
claiming that the resident image changes the runaway or visible output.

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
The writer is named (s4577/s4580, re-decoded s4708): `late` is the tail of the name string "xbkplate" written by rs_strncpy into a name table that voice index 30 (past the 18-slot array) lands in, because count 32 is published before the new base with the mixer running in between. s4710: retail boot/attract does ONE alloc (count 20) only; no second alloc observed, (C) ruled out for that window, hangar unobserved. Next: log port slot-alloc ra (NEXT.md).

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
- External retail-entry remains parked after s4690: the new handoff capture
  had positive controls but no target writer/consumer in the requested
  title/hangar phase. Do not repeat this route-null capture without a new route
  discriminator. The M4 accumulator-origin boundary is eligible again because
  s4625 qualified a stable hangar route and retained the stage-1 control.
- The s4622 producer null was title-only until s4624. The extended s4625
  canonical hangar route also had no odd event, so the post-hangar trigger is
  ruled out for this route; the recurrence remains a missing-trigger or
  alternate-route problem, not evidence that the odd request is impossible.
- M3 patch-runtime qualification is blocked on `mips64-elf-gcc`,
  `mips64-elf-ld`, and `PatchesLib`.
- Generated-symbol renaming is exhausted (s4646): 6 placeholders remain in
  the TOML, none a bounded batch. Do not schedule further sweep iterations.

## Superseded conclusions to avoid repeating

- **"Loop must wait for the owner to choose a target / no retail framebuffer reference known" (s4729).** Believable because M5, M3, the rename sweep and 0x1F0D74 were all closed and the BLOCKED question was framed around a missing reference. Overturned s4730: the retail hangar RDP capture (`s4514_rdp_hangar512.bin`, 166 MB) and oracle video-plugin runs already existed, and choosing a target is in-scope prioritization.
- **"Mission entry needs an owner-supplied recipe or savestate" (s4719-s4721).** Believable because ~10 button-press variants (s4657-s4720) never left the hangar/viewer/attract. Overturned s4722 as unproven: every variant varied button input only; forcing the mode variable in RDRAM was never tried, and the oracle reliably reaches the hangar unaided.

- “The early (~3.3 s, VI 640) `musyxSynthFrame_s4562_impl+9668` bus error /
  `0x400149714` family is a host-thread race or uninitialised voice state”
  (s4672/s4695 and the line-141/198 notes above) was wrong. It was our own
  `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN` diagnostic: `MEM_W(-0X68EC, 0X80150000)`
  uses an unsigned literal, so address math yields 0x100149714 (not
  sign-extended) = read past RDRAM. Believable because it was intermittent
  (depends on what the host happens to have mapped there) and every recipe
  armed the flag. s4696: vtc=1 3/3 crash, vtc=0 0/3; after S32() fix (fixup
  source + `MEM_W(0X2038, 0X80140000)` in tickAudioSequencerFrame, same class)
  vtc=1 0/3. Any older "bus-error family" attribution in recipes that armed the
  flag is suspect.

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

Single monotonic backlog (renumbered s4739). s4741: ovl2c toml+composite landed. OPEN DEPENDENCY (human, s4742/s4745; iterations must NOT retry, NEXT.md re-scoped to runaway-DL cost measurement): add RSPRecomp Bash allow rules to .claude/settings.json (see scratch/agent/UNBLOCK.md); meanwhile NEXT.md is the offline 0x2C analysis. Full pre-compaction history of this section: PROJECT-OVERVIEW.md, "Archive: CURRENT-TRUTH 'Next steps' log s4649-s4738".

1. **M5 callback teardown follow-up:** s4771 closes the shutdown-call branch as
   absent on the covered title/hangar route while independently confirming
   first-match deregistration leaves slot 2 live. Do not change deregistration.
   The next discriminator is a new route or trigger that can reach
   `shutdownAudioEngine`; absent that, park this branch and continue the M5
   plan without treating the surviving duplicate as a shutdown artifact.
2. **Overlay-0x2C splice:** compilation and the Debug build are now qualified
   (s4773), but the existing capture recipe reaches only hangar at VI 512.
   Build one new mission-route input/driver discriminator, retaining the
   resident splice and the same positive controls; do not infer splice effect
   from the hangar-only run.
3. **s4764 route blocker:** superseded for callback reachability by s4770, which reached both title and hangar without crash. The earlier VI-640 crash remains a recurring audio-route family, not evidence against callback cardinality.
4. **Mission-phase correctness remains closed only for the covered frame route.** s4753/s4759 show the port can reach the 512 phase with ship/HUD/terrain and no runaway/crash. They do not select whether the real 0x2C image changes billboard/sprite output, because the 0x2C dispatch was absent in s4759.
5. **M5 audio:** de-stubbing qualified through A14 on the covered route (A11 wait cap, A12 countdown wait, A13 drain return default-off + timeout guard, A14 shutdown-call-3 needs `ROGUESQ_A14_YIELD` default on; B40 default flipped to pass-through s4701, rollback `ROGUESQ_M5_B40_VALUE=0`; after regen verify funcs_23.c shows `== '0') ? 0 : ctx->r2`). A15 redundant, early synth crash resolved s4696. Per-scene audio re-allocs (initN64RspMixer via runVideoFrameTick->reapplyDisplayMode) are retail behaviour and benign (s4711-s4715, closed). Plan: docs/M5-AUDIO-PLAN.md. Keep soaks <=4 concurrent; every game-launching recipe must `pkill -KILL -x RogueSquadron64Recomp` in cleanup.
5. **M3 idiom classes are ALL closed** (MEM_B/BU/H/HU/W/WU, LD, lwl/lwr, SDL/SDR/SWL/SWR, FPR lwc1/swc1/ldc1/sdc1, LL/SC; tools/census_*.py, docs/M3-S4688-MEMWU-CENSUS.md). No guard without a named writer and legitimacy proof. Attached-mesh `rs_free` NULL contract was unevaluable (no oracle route reached a mission s4655-s4670); the s4724 recipe now reaches one, so it could be revisited with mission-phase watches.
5. **Parked / closed, do not repeat without a new discriminator:** M4 accumulator boundary (unevaluable at the Rice/HLE boundary, s4689); odd-PI DMA question (s4690 H-route-absent); right-edge column-511 noise (benign stale RDRAM, s4643); hangar pillar stubs (no pixel reference; Rice retail hangar frames are wrong, s4645/s4731); 0x1F0D74 width-1161 premise (generic heap/DMA reuse, s4728); overlay registration chunked-load H2 (s4673); safe fresh-copy fixer `tools/fixup_game_funcs_vendored.py <scratch RecompiledFuncs>` is qualified in scratch only - never regenerate over `../N64Recomp/RecompiledFuncs` until the external fixer is repaired (s4649).
6. **Renaming sweep** (priority 4): resume only when 1-3 are inapplicable; check the last 15 session titles first.

## Evidence and operating rules

Retail oracle watches are physical-address ground truth. Whole-RDRAM, VI, target-PC, and adjacent-range controls must qualify every null. Phase-gate animated comparisons on VI transitions. Batch all counters and A/B arms in one build/run. Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX assumptions. Keep safety guards separate from explanations.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py -> CMake`; never hand-edit generated functions for behavior. If `lib/` changes, export submodule patches in the same session. Never run submodule update, checkout, clean, or hard reset. Kill runs with SIGKILL and run from `build/` with the ROM present. Any mitigation-shaped change needs an `ORIGIN:` line.

See [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) section 59 for the s4590-s4617 evidence archive and [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md) for the audio plan.
- s4789: DROP=1 mission-2c still unmeasured; startup crash at spTaskSchedulerThread+9632 recurred (load 7.6). SOAK-RESULTS s4788_drop1_mission_2c rc=0 line is a FALSE PASS (bash print broke the driver). Next: bisect DROP on/off (NEXT.md).

- (s4790) spTaskSchedulerThread+9632 startup crash is intermittent and did NOT reproduce in matched DROP/no-DROP runs at load 7-20; do not treat it as DROP-caused or load-gated. Open issue: 150 s runs with the LLE_FORCE/UNGATED/SOLO env stay at VI 640 (no hangar, no 512); see NEXT.md.
