# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Compacted
at s4798 (61 KB -> ~15 KB); the verbatim s4740-s4797 headline log, the old
"Current state" and "Active frontier" sections are archived in
[PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) under "Archive: CURRENT-TRUTH headline
log s4740-s4797 ...". Git history preserves the pre-compaction file.

## Headline (as of s4859)

- **s4859 closed the M5 A16 AI-shim caller boundary.** The independent retail
  oracle fired its whole-RDRAM positive control at 10,000 callbacks, reached
  title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and repeatedly
  sampled nonzero AI length with status `0x40000000`. The same-build image
  port reached both phases, completed 1,253 SP enter/return pairs, and
  produced 77 nonzero PCM rows; its AI shim rows were 1,024 `set-next`, zero
  `get-status`, and zero `get-length`, with the shim control firing once.
  This selects H-A16-unreached: the status/length shims are not a covered-route
  PCM explanation. No shim behavior change is authorized.

- **s4858 requalified the M5 A13 drain boundary.** The same-build default-off
  and `ROGUESQ_DRAIN_INLOOP_TICK=1` arms both reached title/hangar, completed
  SP work, and produced nonzero PCM. Default-off observed active `0x02` slots,
  drained to `nz=0`, and returned at 100,000 iterations with no timeout. The
  tick arm retained 13–16 active `0x02` slots through 700,000+ iterations and
  did not return before the watchdog kill. The retail oracle independently
  fired its whole-RDRAM control, title/hangar VI controls, and both status
  writer PCs `0x8009B7CC`/`0x8009B7EC`. This selects H-A13-default-valid and
  rules out the in-loop tick as required producer activity for this route; no
  runtime change is authorized. The recipe summary was stale, so counts were
  extracted directly from the fresh logs.

- **s4857 qualified the M5 host queue edge.** The same-build default and
  rollback arms reached title and hangar, with 78/81 phase-5 PCM source rows
  and 60/62 nonzero rows. Both had zero `[m5-audio-host-error]` rows, 546/549
  successful queue edges, and consumer joins carrying the matching source
  hash. This selects H-host-queue-valid and closes the SDL queue boundary;
  no host-error suppression or consumer-join defect is selected.

- **s4856 made the M5 host queue edge truthful.** `queue_samples` now records
  the `SDL_QueueAudio` return, reports phase-scoped host failures, and only
  emits the PCM consumer join after a successful queue. The DEBUG target builds
  successfully. No runtime route result is claimed yet; the next unit is the
  phase-gated host/source/consumer validation with this binary.

- **s4855 found the task-contract qualification route-invalid.** The existing
  image-route harness crashed at `spTaskSchedulerThread+9632` with
  `si_addr=0x400128d47` during the first 320-wide phase. Title and hangar
  transitions, task-contract/lifetime rows, and PCM controls were absent; the
  single early route-order row is not a positive control for the planned
  phase-5 measurement. This selects neither task-contract legitimacy nor a
  mismatch. Do not infer a contract defect or repeat the same route unchanged.

- **s4854 found the broader M5 port-task-load control unreached on the same
  qualified image route.** The single-source run reached title and hangar with
  1,255 phase-5 SP-complete enter/return rows, 1,255 action-dequeue rows, and
  10,970 PCM rows, with no crash or abort. Both `m5-port-load-control` and
  `m5-port-load` rows were absent. This selects H-port-load-unreached for this
  instrument, not a task-field mismatch; do not repeat this control without a
  new route discriminator.

- **s4853 found the targeted M5 descriptor control unreached on a qualified
  image route.** The single-arm descriptor run reached title and hangar, with
  1,273 phase-5 SP-complete enter/return rows, 1,273 action-dequeue rows, and
  11,027 PCM rows; it had no crash or abort. The target
  `0x800377C8` descriptor control, start, compare, and yield rows were all
  absent. This selects H-descriptor-unreached, not a descriptor-layout defect;
  do not repeat this exact target without a new route discriminator.

- **s4852 qualified the A10 guard class as legitimate on the covered route.**
  The corrected same-build default/`ROGUESQ_A10_GUARD_OFF=1` pair reached title
  and hangar in both arms. The newly enabled route-order control recorded
  phase-5 `action-dequeue`, `sp-complete-enter`, and `sp-complete-return` rows
  (512 each per arm), proving the prior SP zero was an instrumentation omission.
  Both arms had 32 named-writer rows, 262 identical A10 audit/traversal rows,
  nonzero PCM, and no crash/abort; guard-off produced no qualifying downstream
  route or traversal difference. This selects H-A10-legitimate and authorizes
  no guard relaxation. The next M5 unit may move past A10.

- **s4851 invalidated the queued A10 port A/B and its corrected retry.** The
  queued recipe failed before launch because its root calculation resolved to
  `scratch/build`; the fixed same-build retry reached title and hangar in both
  arms, with 32 named-writer rows, 262 traversal/guard rows, and nonzero PCM
  in each. However, the required SP positive control was zero in both arms, so
  neither A10-legitimate nor A10-suppression is selected. No guard relaxation
  is authorized. The next A10 unit must repair/qualify the SP control itself
  before comparing guard behavior again.

- **s4849 qualified the independent A10 writer route and queued the port A/B.**
  The same retail-oracle run reached the whole-RDRAM 10,000-hit control, title
  VI 1024, and hangar VI 512. The physical `0x801529C0` watch recorded 2,428
  writes, including 469 title-phase and 331 hangar-phase writes from retail PC
  `0x80096D88`. The shared port build passed; a concurrent default versus
  `ROGUESQ_A10_GUARD_OFF=1` soak is queued with phase-gated guard, traversal,
  PCM, SP, and route controls. No guard relaxation is authorized before its
  verdict.

- **s4848 closed the generated 32-bit multiplication class.** The complete
  census found 670 `mult`/`multu` annotations (669 unique file/guest-PC sites).
  The independent retail ELF decoded 643 rows, and every decoded row had the
  expected signed/unsigned product lowering. The first decoded row at
  `0x80000E04` was the positive control and passed. The remaining 27 rows are
  annotation/ELF mismatches: their retail words are not multiplication
  instructions and their generated bodies have no product lowering. No live
  multiplication translation defect is selected; no runtime or generated
  output change is authorized. See `docs/M3-S4848-MUL-CENSUS.md` and
  `tools/census_mul.py`.

- **s4847 closed the generated 64-bit shift class.** The complete census found
  720 annotations (678 unique file/guest-PC sites) across `dsll`/`dsrl`/`dsra`,
  32-bit variants, and variable forms. All 720 raw words independently decoded
  from the retail ELF; 529 generated lowerings matched, while the remaining 191
  were unreachable or `$zero`-destination. The per-function CFG found 162
  reachable rows, all 162 with nonzero destinations and correct lowerings. The
  positive control at `0x800074E0` independently decoded as `dsll32 $v0,$a0,0`
  and lowered correctly. No live translation defect is selected. See
  `docs/M3-S4847-DOUBLE-SHIFT-CENSUS.md` and `tools/census_double_shifts.py`.

- **s4846 closed the generated HI/LO move class.** The complete census found
  989 annotated `mfhi`/`mflo`/`mthi`/`mtlo` rows. The independent retail ELF
  decode and generated lowering agree at 916 rows; 47 remaining rows are
  zero-destination/data-like sites, and 26 annotation/ELF mismatches are in
  unreachable generated regions. The positive control at `0x80003444`
  independently decodes as `mflo $v0` and lowers to `ctx->r2 = lo`. No live
  HI/LO translation defect is selected. See
  `docs/M3-S4846-HILO-MOVES-CENSUS.md` and
  `tools/census_hilo_moves.py`.

- **s4845 closed the external retail-entry boundary as route-absent.** The
  debugger-enabled oracle ran the documented Rice video plugin and Start
  schedule in one 180-second invocation. The whole-RDRAM control reached its
  10,000-hit cap; title reached VI 1024 at `0x00790400` and hangar reached VI
  512 at `0x006AB400`. The execution watch at `0x800903F0` recorded zero hits
  on this qualified retail route. This selects H-retail-route-absent and
  rules out the prior undriven-route explanation; it does not establish why
  the port still observes the boundary input.

- **s4844 qualified the retail-oracle setup but not the external handoff.**
  The rebuilt DEBUGGER=1 core and frontend ran with a whole-RDRAM write
  control, VI polling, and the target `0x800903F0` execution watch in one
  180-second invocation. The control reached its 10,000-hit cap and VI
  polling remained live, but the undriven Rice-less route stayed at 320-wide
  pre-title (`0x006DD280`), with zero target-PC hits. This is a route/setup
  result, not a retail null for the qualified title/hangar route; the next
  attempt must add the known Rice video plugin and Start schedule.

- **s4843 closed the next generic CPU-trap class: `sync`.** The new census
  found 7 generated occurrences at 6 file/guest-PC sites whose independent
  big-endian retail-ELF words decode as valid SPECIAL funct `0x0F` encodings.
  The generated-C CFG classified all 6 unique sites as data-like/unreachable;
  raw words and annotations agree, and neither N64Recomp's operation maps nor
  `fixup_game_funcs_vendored.py` contains a `sync` lowering. This selects
  H-unhandled-data for this class, not a live translation defect; no runtime
  change is authorized. Tables: `docs/M3-S4843-UNHANDLED-CPU-CENSUS.md` and
  `docs/M3-S4843-UNHANDLED-CPU-REACHABILITY.md`.

- **s4842 traced the reachable conditional-move defect to N64Recomp itself.**
  The source ELF contains the valid word `0x0022D34B` (`movn $k0,$at,$v0`) at
  `0x800A2B64`; the pristine `RecompiledFuncs.s4204-fresh` output already emits
  `do_break` there, and the current `fixup_game_funcs.py` has no `movn`/`movz`
  rewrite. N64Recomp's `binary_ops`, `unary_ops`, and conditional-branch maps
  omit both conditional moves, so `process_instruction` reaches its generic
  unhandled-instruction trap. The duplicate `funcs_27.c` context agrees. This
  selects H-cmov-unsupported, rules out fixup-loss and regeneration drift for
  this site, and still authorizes no generated-output behavior change.

- **s4841 selected a live generated conditional-move site in static CFG.** The
  independent reachability pass covered all 149 file/guest-PC sites: 2 are on
  reachable generated guest paths, 16 are post-return/unreachable, and 131
  are data-like/unreachable. One reachable site has a nonzero destination
  (`funcs_49.c`, `0x800A2B64`, `$k0`), so the `do_break` lowering defect is not
  latent-only. This is still static generated-C evidence, not proof that the
  qualified runtime route reaches that site; audit the fixup/regeneration path
  before changing behavior. Table and classifier:
  `docs/M3-S4840-MOVZ-MOVN-REACHABILITY.md` and
  `tools/classify_movz_movn.py`.

- **s4840 found a generated conditional-move translation defect.** The complete
  census found 179 `movz`/`movn` annotations (95/84), 149 file/guest-PC sites,
  and 144 `.word` encodings whose independent raw decoder agreed 144/144 with
  the annotated opcode and operands. Every generated body is `do_break`;
  115 sites have nonzero destinations, so this is not equivalent to a harmless
  write to `$zero`. The sites cluster in data-like/obfuscated regions and
  several follow indirect-return paths; runtime reachability is unmeasured.
  Do not patch the class or call it a route cause until the next bounded
  reachability classification. Full table and reproducer:
  `docs/M3-S4840-MOVZ-MOVN-CENSUS.md` and `tools/census_movz_movn.py`.

- **s4839 closed the generated variable-shift class.** The complete source
  census found 721 textual `sllv`/`srlv`/`srav` mentions: 469 direct
  instruction comments and 252 `.word` data-as-code annotations. All 403
  live-destination sites use the expected 32-bit, masked-count, signedness
  lowering; the other 66 write `$zero`. No mismatch or intervening-write
  defect was found. Runtime reachability was not claimed. Full table:
  `docs/M3-S4839-VARIABLE-SHIFT-CENSUS.md`.

- **s4838 closed the generated HI16/LO16 construction class.** The complete
  source census found 24,276 `lui` sites and 3,015 canonical same-register
  immediate low-half pairs (2,479 `addiu`, 536 `ori`). An independent raw
  adjacency pass found no destination/source-register mismatch; 1,174 adjacent
  low-half-looking operations were independent operations with different
  registers, not pairs. No intervening-write or relocation defect was found.
  Route reachability was not claimed. Full table:
  `docs/M3-S4838-HILO-CENSUS.md`.

- **s4837 closed the generated branch-likely idiom class.** The complete
  census found 893 sites across 44 generated files: 197 `bc1fl`, 597 `bc1tl`,
  36 `bgezl`, 10 `bgtzl`, 13 `blezl`, and 40 `bltzl`, with no `beqzl`/`bnezl`.
  Every site matched the annulled-delay-slot shape: conditional delay-slot
  body, taken target, untaken skip, and fall-through duplicate. The 24 apparent
  shape exceptions were existing guest-PC breadcrumbs (23) and one viewer-fade
  observer; neither changes the predicate or control flow. This selects
  generated translation validity and authorizes no guard or behavior change.
  Full table: `docs/M3-S4837-BLIKELY-CENSUS.md`.

- **s4836 qualified the Step 11 producer/clear route with the generic writer
  table.** After replacing the table's unsafe `rogue_current_thread_id(nullptr)`
  observer with a host-thread hash, both same-build arms reached title 1024 and
  hangar 512, completed 64 SP tasks, produced nonzero PCM, and had no crash or
  abort. Both recorded repeated `0x80091680` arm writes of `1` followed by the
  exact `0x800912F8` clear writes of `0` to `0x8014974C`; the named
  `[waitmusyx-spin2-clear]` row remained absent because its fixup anchor is not
  present in the generated live helper. The prior s4834 crash was therefore
  observer-induced, while the generic table independently proves the legitimate
  clear writer and value transition. No yield-causal difference is selected.

- **s4834 clear-site discriminator was route-invalid twice.** Both same-build
  default/rollback attempts reached VI 640, title 1024, 64 SP completions, and
  the existing second-wait arm/return rows, but crashed before hangar. PCM and
  phase-scoped gate controls were absent, so no Step 11 hypothesis is selected.

- **s4833 stabilized the M5 Step 11 route but did not qualify the clear edge.**
  The corrected same-build default/rollback pair used `STUB_MISSING_FUNCS=1`
  and the phase-gated autopilot; both arms reached title 1024 and hangar 512,
  with 64 SP completions, nonzero PCM source/consumer rows, and no crash or
  abort. Both emitted 40 second-wait arm rows and three wait-return rows, but
  neither emitted a `waitmusyx-spin2-clear` row. The two arms therefore show
  no yield-dependent route difference, while the required producer-clear
  discriminator remains unevaluable. The harness's broad witness label must
  not be read as proof of a clear.

- **s4832 Step 11 remains unevaluable after correcting the wait-witness driver.** The converted same-build default/rollback driver initially reached title and hangar with SP/PCM controls but had not armed `ROGUESQ_LOG_WAITMUSYX_SPIN2`, so its zero wait count is invalid. The fixed rerun stopped before VI 640 in default and crashed in rollback (36 rows); neither emitted phase/gate/wait witnesses. No Step 11 hypothesis is selected. The oracle precheck was blocked by a missing debugger-core dylib, so no new retail null is claimed.

- **s4831 M5 Step 1 is qualified on the corrected same-build pair.** The
  corrected harness compared Factor 5 image (`ROGUESQ_AUDIO_UCODE=1`) against
  the silent control (`=0`) using the documented multi-press autopilot. Both
  arms reached title 1024 and hangar 512 with 64 SP completions and no
  crash/abort. Phase-5 PCM source samples were nonzero in the image arm
  (`nz=768`) and zero in the silent arm (`nz=0`), selecting image downstream
  activity rather than a route-only explanation. The prior s4823/s4829
  request-only pair remains invalid for Step 1; do not repeat it.

- **s4830 A9/A10 replay passed its fixup discriminator but not whole-file
  identity:** the pristine generated copy replayed with `failures=0`, A10
  reported 44/44 sites, and A9 reported 13 sites plus its writer. All four
  selected files differed from the live tree because the live files retain
  later diagnostic patches (for example s4784/s4700 and s4597/s4601); this is
  replay drift, not evidence that either A9 or A10 failed to replay.

- **s4829 M5 Step 11 A/B is route-invalid at the wait discriminator:** the
  corrected same-build default/rollback pair reached title and hangar, with
  SP completion and nonzero PCM source/consumer controls in both arms and no
  crash. Both arms showed second-spin arm and loop-return activity, but neither
  showed the required producer-clear/seed witness or a wait-contract return;
  both loop returns reported `yields=0`. The route therefore does not exercise
  the A12 second-wait difference, so no yield-safe or yield-causal conclusion
  is selected.

- **s4828 crash-path capture:** the corrected same-build default/request-only
  pair again produced the task-validity positive control: 64 matching start
  and 64 pre-conversion enqueue rows per arm, all in-range, with no rejected
  pointer or `0x400128d47`. Both arms reached phase 3 / VI-640 and stopped at
  the same gate; neither emitted a native crash marker. This retains
  intermittent route instability as the only selected explanation for the
  absent crash and rules out the validated conversion/start/enqueue path in
  this run. Do not repeat this capture without a new discriminator.

- **s4826 host-boundary audit:** a corrected same-build default/request-only
  pair qualified the task-validity positive control. Both arms showed the same
  in-range task pointers and fields at `osSpTaskStartGo` and pre-conversion
  enqueue; neither emitted a rejected pointer or `0x400128d47`. The pair still
  stopped at the VI-640 gate (64 SP completions each), so no request-only
  lifecycle conclusion is selected and the intermittent malformed-pointer
  crash remains unobserved. The conversion/start/enqueue path is not the
  source in this capture; a native crash capture is still required.

- **s4825 startup-boundary audit:** the default and request-only arms share
  the first SP task, queue/message, type-0x81 dispatch, LLE task, and one SP
  completion. Request-only crashes before any `[sp-yielded-ab]` row, so its
  `osSpTaskYielded` exchange did not run. The `0x8000834c` breadcrumb is the
  `drainMeshReleaseQueue` return delay slot and is stale attribution. This
  selects a common pre-VI-640 scheduler/host boundary, not request-only
  lifecycle causality; exact pointer writer remains open. See
  `docs/M5-S4825-STARTUP-BOUNDARY-AUDIT.md`.

- **`ROGUESQ_OVL2C_DROP` was dead code since s4773 (s4802).** The splice route preceded the drop branch, so every DROP=0/1 A/B compared the splice with itself. Now `ROGUESQ_OVL2C_MODE` 0=splice (default) 1=drop 2=none (`tools/apply_s4805_ovl2c_mode.py`, fixup synced). s4806 three-arm run (single run each, cross-run caveat): routing 0x2C cuts phase-3 RDP submissions ~3x (513k vs 1.53M unrouted), but phases 5/6 are identical in all arms (~254k / ~955k) and the splice adds no measurable texrects at the mission origin. The old "0xBD arrival <=> runaway" claim does not extend to phase 6. VI-640 phase 3 lasts ~50 s in every run (s4803); transient `stalled=1` lines there are normal.

- **VI-640 stall = presentation-side symptom (s4797, same-run `sample` control).**
  At a live `vi-fs stalled=1`, `update_screen` ordinals advance and the Gfx
  thread is active in `RT64::State::updateScreen`/`processDisplayLists`, while
  guest MAIN is parked in `submitGfxFrame -> waitForPostSwapAck`; the synth
  thread is separately in its message wait. Rejects audio-main-wait and
  producer-thread-stalled. The stall is nondeterministic (s4794: 2/5 runs stay
  at VI 640 for 200 s, 2/5 reach VI 1024 at 55/77 s, 1/5 startup crash; s4791/
  s4792 load-sensitive, single-source). No mitigation authorised.
- **Mission route is blocked by that stall (s4796) and by input (s4774).**
  Overlay-0x2C splice (resident `OVL2C_1DB0`, built and validated s4773) is
  unevaluable: no driver has reached mission origin `0x00690400` with `res=0x2C`
  rows since s4759. Old "zero res=0x2C" nulls were void: the `[ovl-route]`
  logger had no 0x2C branch until s4787.
- **Rename sweep closed (s4795).** 8 remaining placeholders are deliberate
  `fake_func_*` boundaries; table in `docs/RENAME-S4795-AUDIT.md`.

- **s4803: splice emits sprites.** Offline frame-split phase-6 diff: m1 (drop) texrects are a strict subset of m0 (splice); m0 adds up to ~119 small sprites/frame by frame 130. s4804: retail s4733 rdp.bin contains NO mission frames (its >=100-texrect frames are menu text, 0 sprites <=8x10), so splice correctness vs retail is unevaluable until a retail mission capture exists.
- **s4823: M5 Step 1 qualification remains route-invalid.** The same-build two-arm
  harness passed its VI-640/SP positive controls in both arms, but neither arm
  reached title/hangar; it returned `H-DiscriminatorIncomplete`. Default had 4
  completion-wins rows (`returned=0`, `pending_after=1`); request-only had 7
  request-only rows (`returned=1`, `pending_after=0`) and E70/E80F rows. No
  audio or request-only conclusion is selected.
- **s4824: the documented qualified tuple is also route-invalid before VI 640.**
  After adding `AUTOPILOT + real-audio + LLE / ungated / solo / spin-yield` to the
  A/B harness, default stopped at VI 320 after 10 SP completions; request-only
  hit the known `spTaskSchedulerThread+8972` startup segfault
  (`si_addr=0x400128d47`) after one completion. Neither arm reached the VI-640
  control, so Step 1 remains unevaluable and the request-only lifecycle is not
  implicated. The harness now carries the documented tuple by default.
- **s4822: M5 Step 1 qualification remains route-invalid.** The existing two-arm
  harness reached its VI-640 positive control with 64 SP completions per arm,
  but neither arm reached title/hangar; it returned `H-DiscriminatorIncomplete`.
  A rerun with the documented qualified `AUTOPILOT + real-audio + LLE /
  ungated / solo / spin-yield` tuple failed earlier: default stopped at VI 320
  after 15 SP completions, while request-only hit the known
  `spTaskSchedulerThread+9632` startup crash (36 crash rows). No audio arm or
  SP-lifecycle hypothesis is selected.

## Current state (durable)

- **M5 A9 voice-array base guards (s4805):** 0 bad of ~2.4M checks at 10/13 sites on title+hangar (forced-bad control fired in the same build); writer `0x8008F0EC` publishes in-range `rs_malloc` bases. Guards are inert here; 3 sites (`0x8009236C`, `0x800923C0`, `0x800924F4`) unreached. Tool `tools/apply_s4805_m5_a9.py`; env `ROGUESQ_LOG_M5_A9`, `ROGUESQ_A9_FORCE_BAD=N`.

- Qualified native route: attribution, N64 logo, intro cinematic, Factor 5 logo,
  title VI 1024 (`0x00790400`), hangar VI 512 (`0x006AB400`) on the real-audio /
  LLE / ungated / solo / spin-yield route. Mission origin is `0x00690400` (512).
  Retail RDP is obtainable (hangar ≈1244 tris, 205 KB RDP). Port hangar geometry
  and colour artifacts remain localised (rim band, blue holo spikes, right-edge
  garbage = benign stale RDRAM, s4643).
- **M5 audio:** no longer a zero-output stub; nonzero PCM, AI byte order fixed.
  Step 1 image-versus-silent qualification is closed on the corrected route
  (s4831). Steps 4-13 qualified or closed on the covered route (key-on early-return valid
  s4678, status-03 writer legitimate s4680, A10 song-tempo guards valid s4681,
  AI/SDL bridge valid s4682, A11 wait cap s4691, A12 countdown wait s4692, A13
  drain default-off + timeout guard s4693). Plan: `docs/M5-AUDIO-PLAN.md`.
  A14 needs `ROGUESQ_A14_YIELD` default on; B40 default flipped to pass-through
  (s4701; rollback `ROGUESQ_M5_B40_VALUE=0`; after regen verify funcs_23.c shows
  `== '0') ? 0 : ctx->r2`). Second MusyX wait gate (`0x8014974C`) yields by
  default (s4765; rollback `ROGUESQ_AUDIO_SPIN2_YIELD=0`).
- **M5 Step 11 s4833 route result:** the route-stabilizing tuple reaches the
  qualified title/hangar phases in both yield arms. The wait logger records
  arm and return activity but no clear-site row in either arm; do not repeat
  the same A/B without a new clear-site discriminator.
- **M5 Step 11 s4834 discriminator:** the fixup source now logs every
  phase-scoped byte store overlapping physical `0x14974C` with guest PC, value,
  and thread, and the named clear row records pre/post values. Two captures
  were route-invalid before hangar; no writer-origin conclusion is selected.
- **M5 Step 11 s4836 writer result:** the phase-scoped generic writer table is
  qualified on both default and `ROGUESQ_AUDIO_SPIN2_YIELD=0` arms. The exact
  producer/clear PCs are `0x80091680`/`0x800912F8`; the named clear logger is a
  stale/missing generated anchor, not evidence that the clear is absent. The
  observer crash was diagnostic-only and is fixed by host-thread identification.
- **musyxSynthFrame `+5808` crash family: closed for idle title/hangar (s4786).**
  Cause: synth ticking over the audio arena freed by the retail-legitimate
  `musyxNoopStub` teardown (s4782/s4783: retail never ticks the synth between
  free burst and re-init; the port's synth is a separate host thread and does).
  Fix: `ROGUESQ_S4562_PAUSE=4` default-on (`tools/apply_s4562_synth_pause.py`,
  rollback `=0`; hold pause until guest `initSampleStreamBlockCache` return
  `0x8008F958`); 544 s soak 0 crashes. Installed funcs_24.c once silently lost
  PAUSE=2/3 code, so PAUSE=2/3 negatives after a regen are void.
- Callback table (s4762-s4772): `musyxSynthFrame` is registered twice and
  first-match deregistration leaves a live duplicate; dispatch is all-live-slot
  (s4770); the covered route never reaches `shutdownAudioEngine` (s4771/s4772,
  single static caller `0x8008ECB8`). Do not change deregistration or dispatch.
- **Early (~3.3 s) `+9668` bus error was our own `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN`
  unsigned-literal bug (s4696)**, fixed via `S32()`; older recipes that armed it
  are suspect.
- **M3 idiom classes are ALL closed** (trap/break/syscall/cop0, unaligned/ll-sc/cache (s4820) s4818, integer div/divu/ddiv/ddivu s4813, float->int TRUNC/CVT s4814, float compare/NaN s4815, ctc1/cfc1 FCSR s4816, MEM_B/BU/H/HU/W/WU, LD, lwl/lwr,
  SDL/SDR/SWL/SWR, FPR lwc1/swc1/ldc1/sdc1, LL/SC, jalr/jr indirect calls,
  backward self-referential walks, `rs_free` idiom to s4502). Tools
  `tools/census_*.py`; tables `docs/M3-S46xx-*-CENSUS.md`. No guard without a
  named writer plus legitimacy proof.
- **M3 branch-likely delay slots are closed (s4837).** Static census and
  control-shape pass cover all 893 sites; no annulment defect was found. See
  `docs/M3-S4837-BLIKELY-CENSUS.md`. Reachability of every site on the
  qualified route was not claimed.
- **M3 variable shifts are closed (s4839).** Static source census and
  register-aware semantic pass cover all 469 direct sites; no width, count-mask,
  signedness, or intervening-write defect was found. See
  `docs/M3-S4839-VARIABLE-SHIFT-CENSUS.md`.
- **M3 conditional moves are statically mistranslated (s4840).** All 179
  generated `movz`/`movn` sites emit `do_break`, including 115 nonzero
  destinations; the raw decoder independently validates all 144 `.word`
  encodings. s4841's static CFG finds one reachable nonzero-destination site;
  runtime impact remains open and no fix is yet authorised.
- **M3 conditional-move provenance (s4842):** the reachable site is a valid
  source instruction but is unsupported by the current N64Recomp operation
  tables, not altered by the fixup pass. A recompiler-side implementation and
  route qualification remain separate future work; do not hand-edit generated
  output.
- **M3 HI/LO moves are closed (s4846).** The retail-ELF decode and generated
  lowering agree at all nonzero-destination decoded sites; zero-destination
  rows and 26 stale/unavailable annotations are confined to data-like or
  unreachable generated regions. No guard or recompiler change is authorized.
- **M3 64-bit shifts are closed (s4847).** The complete retail-ELF/raw-decode
  and generated-lowering census found no reachable nonzero-destination defect;
  no guard or recompiler change is authorized.
- **M3 32-bit multiplication is closed (s4848).** All decoded `mult`/`multu`
  rows have the expected lowering; 27 stale annotation rows are not
  multiplication words in the retail ELF. Do not repeat this census without a
  new recompiler or annotation-provenance hypothesis.
- **External retail-entry boundary (s4845):** the Rice/input oracle route is
  qualified through title and hangar, with whole-RDRAM control positive, but
  `0x800903F0` has zero execution hits. The retail handoff is absent on this
  route; do not repeat the setup without a new route or PC discriminator.
- **Runaway-DL cause (s4746-s4749):** DL op `0xBD` (TexrectGen) → overlay `0x2C`
  (real 0x240-byte VU image, ROM `0x27368`, dest `0x1DB0`) is unrouted, so the
  window entry restarts the task. Present ⇔ arrival ⇔ runaway (150/150 vs 0/550).
  Runaways: phase 3 (VI 640) and ~65% of phase 7 (mission). Splice effect on
  ship/HUD is untested (see Next steps #2). s4753: ship/HUD/radar/terrain do
  render at mission origin without the splice.
- **M4 accumulator-origin boundary: parked.** Port VMADH, VGE, store arms all
  closed on the port (s4626-s4651); retail oracle (Rice/HLE) has no RSP
  witness and no retail hangar pixels exist (s4652, s4689), so H-source is
  unevaluable.
- **Odd PI DMA:** port writes ASCII `lcre` into a cart record via FE98; the bad
  input is `0x800903F0` reading `late` from voice `+0x34` = tail of "xbkplate"
  written into a name table that voice index 30 (past the 18-slot array) lands
  in, because count 32 is published before the new base with the mixer running
  (s4577/s4580/s4708). No odd event on any canonical hangar route (s4622-s4625);
  external retail-entry handoff capture was route-absent (s4690).
- **Attached-mesh `rs_free` NULL gap** (`attachedMeshOverlayNpcHandler`
  `0x8005427C`, free at `0x80054344`): statically confirmed (s4654); retail
  handler first executes at 512-wide attract origins, not boot/title (s4656);
  mission contract unevaluated.
- **Regeneration:** full regen is unsafe since s4204 (newer N64Recomp +
  `fixup_game_funcs.py` aborts at the E088 anchor). Use `tools/apply_s*.py`.
  Safe fresh-copy fixer `tools/fixup_game_funcs_vendored.py <scratch copy>` is
  qualified in scratch only (s4649/s4653); never regenerate over
  `../N64Recomp/RecompiledFuncs` until the external fixer is repaired.
  `spTaskSchedulerThread+9632` startup crash (guest PC `0x8000834c`) is
  intermittent, not DROP-caused, not load-gated (s4790).

## Parked and closed

- M3 `jal rs_free` audit closed s4502; wild-width writeback is a named
  garbage-region SETCIMG writer — no skip without an origin proof.
- VI-640 crash families and broad M3 guard classes parked; a mitigation needs an
  `ORIGIN:` line naming the writer and whether the value is legitimate.
- External retail-entry parked (s4845): Rice/input route is qualified through
  title and hangar but has zero `0x800903F0` hits; do not repeat without a new
  route or PC discriminator.
- Hangar pillar stubs (no pixel reference; Rice retail hangar frames are wrong,
  s4645/s4731); 0x1F0D74 width-1161 premise (generic heap/DMA reuse, s4728);
  overlay-registration chunked-load H2 (s4673); right-edge col-511 noise.
- M3 patch-runtime qualification blocked on `mips64-elf-gcc`, `mips64-elf-ld`,
  `PatchesLib`.
- Generated-symbol renaming exhausted (s4646/s4795).

## Superseded conclusions to avoid repeating

## Superseded conclusions to avoid repeating

- **"M5 needs human authorization for the data_size writer trace; no de-stub step remains" (s4863).** Believable because every M5-AUDIO-PLAN step was closed and the trace looked like a new build+run. Overturned s4864: builds/runs are already permitted by ITERATION.md, and the data_size 1-vs-2 question is still an open, cheap discriminating experiment.
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

0. **M5 double synth walk (s4874-s4875):** port synth runs 2/VI because callback-table slots 1 and 2 both hold `0x8009123C`; retail holds one. NAMED (s4875, two sources: port rows + retail oracle): the dereg comes from the teardown function at 0x8008ECxx (generated name `musyxNoopStub`, jal wait at 0x8008ED14), which branches over the wait/dereg when gate byte `0x800A0F50`==0. Retail: that teardown runs at t=1.8 s with gate=1 (before any reapply) -> dereg -> reapply -> register, balanced, 1 copy. Port: the FIRST teardown (boot) sees gate=0, skips the dereg, so cycle 1's reapply register is unmatched (+1 copy); every later cycle is balanced (dereg+register) so 2 copies persist. Root = the deliberate gate-write force-zero stubs (setDisplayMode 0x8008EB40 / reapplyDisplayMode 0x8008EC88 / initMusyXEngine never called, see fixup comments ~l.8105; reversing them hung boot 4x). Next: a bounded fix that keeps gate semantics but makes the first-teardown dereg happen (e.g. one-shot dereg of 0x8009123C when reapplyAudioConfig registers and the table already holds it) - ORIGIN named, not a mitigation of unknown writer. **s4878 RESULT: tools/apply_s4878_synth_dedup.py (env ROGUESQ_S4875_DEDUP=1, default off) drops the 2nd register; A/B same recipe: synth entries per message 1.97 -> 0.99. Pending: 3-run VI1024 stability then default-on; AI-ring delta check.** Instrument: tools/apply_s4877_dereg_order.py (ROGUESQ_LOG_S4700_CB=1), oracle recipe scratch/agent/s4877_oracle_order.sh.

1. (s4869) The synth entry runs the voice-walk 0x80090E04 once per 0xC0-sample chunk (call sites 0x800914C8/0x80091588/0x8009163C, chunk loop with s2+=0xC0, s3+=1). Retail: 701 builds, 1341 walks (1.91/build), 15820 per-voice jals (11.8/walk). Port: 11264 builds, 5693 walks (0.505/build; 1.01 per REAL entry, the spurious entries do no walk and have a1=0), 66835 jals (11.74/walk). Per-voice work per walk MATCHES, so H-V (voice population) and H-W (per-voice add drops) are refuted; the split is chunks-per-synth-entry (retail ~2, port 1). Next: log the chunk-loop bound/target (s2 start, end limit near 0x800913A0-0x800914B0) in port vs retail (oracle prints only v0/s1/a0/a2; extend rs64_oracle to print s2/s3/s4 or watch the loop head). Note: oracle exec watch at a delay-slot PC (0x80091084) gives 0 hits - blind, never use.  Retail producer 0x8008EE6C = 1343 per 702 synth entries (1.91); port 5704 per 11264 (0.51) - H-A refuted. Build loop trip count a1 (loaded 0x8009132C, written by voice-array walk 0x80090E04) is ~2 retail vs ~1 port; this is the data_size 1-vs-2 residual. Next: retail vs port $v0 at 0x80091084 (=a1) histogram plus voice-array population at 0x80090E04. Older: (s4867) Loop bound 0x8014974E is 3 in retail AND port (writer 0x8008F20C, 5 writes each) - the s4866 "bound 2" was wrong. Retail = 703 synth entries : 703 builds : 702 stores, branch 0x80091390 always taken. Port: ~2 synth entries per store; the extra entry takes the FALL path (ring byte 0x801496F0 already advanced by runAiAudioStreamPlaybackLoop 0x8008EE6C), has counter 0 and stores nothing. Next: retail vs port counts of the 0x8008EE6C producer write per synth entry, and which guest thread runs each port entry (r31 is 0 in the port, no ra logging). Residual: retail TAKEN builds average 1.9 incrs, port TAKEN builds 1. Then close M5 and take the rename sweep / VI-640 route wall.

(s4836: Step 11's generic writer table qualified arm/clear and wait-return rows
on both arms after removing the observer crash; do not repeat the A/B.)
(s4837: branch-likely census matched all 893 generated sites; do not repeat
the class. Continue the next complete M3 idiom census.)
(s4846: HI/LO move census matched all decoded nonzero-destination sites; do not
repeat the class. Continue with the next complete M3 idiom census.)
(s4847: 64-bit shift census matched all 162 reachable nonzero-destination rows;
do not repeat the class. Continue with the next complete M3 idiom census.)
(s4848: 32-bit multiplication census matched all 643 decoded rows; 27 stale
annotation rows were raw-word mismatches, with the positive control passing.
Do not repeat the class.)
(s4838: HI16/LO16 census matched all 3,015 canonical pairs; do not repeat the
class. Continue with the next complete M3 idiom census only when M5 has no new
discriminator.)
(s4839: variable-shift census matched all 469 direct sites; do not repeat the
class. Continue with the next complete M3 idiom census.)
(s4840: conditional-move census found all 179 sites emitted as do_break;
s4841's CFG found one reachable nonzero-destination site; s4842 traced it to
N64Recomp's missing conditional-move operation support. Do not repeat the
fixup audit.)
(s4833: route-stabilizing Step 11 A/B reached title/hangar in both arms, but
the clear-site witness was absent in both. Do not repeat the same A/B; make the
clear-site instrumentation itself discriminating.)
(s4831: corrected image-versus-silent pair reached title/hangar in both arms;
image PCM was nonzero while silent PCM was zero. Step 1 is qualified; advance
to the next M5 plan item.)

(s4830: pristine replay had failures=0 and both A9/A10 reports, but selected generated files differed from the live tree due to later diagnostics; classify replay as behavior-valid but whole-file comparison drift.)
(s4829: Step 11 reached title/hangar but lacked the producer-clear/seed and wait-return controls in both arms; pivot to the next M5 validation rather than repeating this route.)
(s4821: M3 indirect-jump census closed the jr/jalr class; next M3 candidates: branch-likely delay slots, HI16/LO16 pairs.)
(s4812: M5 Step 11 / A12 has a mission row: loop copies not entered (producer arm 40/40, loop rows 0), blind-spin rollback stalls at VI 640; M5 plan has no unqualified covered-route step. Next unit: M3 idiom-class audit.)
(s4811: scratch regen via vendored fixer gives failures=0 and A9/A10 tag counts match live exactly 3/15/96/11; residual diffs are post-s4653 diagnostic probes s4700/s4784 + S32() spelling. Regen chain item closed.)
(s4826: task-boundary witnesses were positive at start and enqueue in both arms, with no malformed pointer; the next capture must target the intermittent native crash path.)

Single monotonic backlog (renumbered s4798). RSPRecomp allow-rule dependency is
resolved (s4755: the tool ran; the old block was false).

0. **M5 host queue validation:** s4856 changed the host bridge to reject failed
  SDL queue calls from the PCM consumer join. Run the phase-gated source,
  host-error, queue-delta, and consumer controls before interpreting the
  Step 10 boundary. **Closed s4857:** both arms had zero host errors and
  matching nonzero source/consumer PCM joins; do not repeat without a new
  host discriminator.
0. **M5 A16 AI shim caller qualification:** closed s4859 as
   H-A16-unreached. The qualified image route reached title/hangar, completed
   SP work, and produced nonzero PCM, but only `set-next` entered the AI shim
   (`1024` phase rows); `get-status` and `get-length` were both zero. Retail
   independently reached title/hangar and showed nonzero AI length plus busy
   status. Do not change the status/length shims or repeat this caller probe.
   Select the next M5 contract boundary with a fresh route discriminator.
0. **M5 task family (s4860):** the qualified route publishes one stable audio task family (0x80149470, type 2, ucode 0x80099FE0, data_ptr 0x80171CE0 title / 0x80171E70 hangar, data_size mostly 1), joined to 2104 SP completions and 79 nonzero PCM rows; s4854's "rows absent" was a control artifact. s4861 retail oracle (hangar only, control passed): same task 0x80149470 type 2, zero output, data_size 1-2 (retail 194x2/22x1, port mostly 1), data_ptr slot differs (ring slot). Class matches; ratio unexplained (single-source). s4862: retail data_size ratio reproduced (title 572x2/53x1, hangar 188x2/22x1, control passed, port now shares data_ptr slots): retail ~90% size 2, port 1-dominant — a real, unexplained difference (single-source on port side). Next: name the OSTask data_size writer on both sides (see NEXT.md). s4863: data_size = frame-batch counter 0x80149760 (stored at 0x80091784 in musyxSynthFrame, OSTask+0x34); no host-shim writer; likely cadence (single-source static). M5 plan has no step left; BLOCKED for direction. s4870: synth chunk loop bound = AI-ring index (byte 0x801496F0, writer runAiAudioStreamPlaybackLoop 0x8008EE6C) delta per synth entry: retail +2, port +1 (cap hw 0x8014974E=3 never binds). Next: who posts value-1 msgs to queue 0x80149670 and what wakes the synth (single-source retail). s4871: messages per synth entry retail 1.91 (1345/704, control passed) vs port 0.50 (steady, run-lifetime): port wakes synth ~2x per AI-done message. Next: per-entry caller/r31 of 0x8009123C on both sides (two registrations?). s4872: retail single caller 0x80019B74 (VI-retrace callback walk); port retrace walk ~117/s = ~2x VI updates, AI-done ~59/s = 1x VI updates (strict 1,0 alternation) - cadence difference, not two registrations. Next: who posts retrace-queue messages in the port (2/VI?) and the AI-done driver (1/VI vs retail ~2/retrace); join retail VI updates per retrace.
0. **M5 port-task-load contract:** s4854 found both the port-load control and
   rows absent despite positive title/hangar, SP, action, and PCM controls.
   This is a single-source route result; do not infer a task-contract defect
   or repeat the same control without a new route discriminator.
0. **M5 task-contract qualification:** s4855 was route-invalid: the image
   harness crashed at `0x400128d47` before title/hangar, so task-contract,
   lifetime, and PCM controls were absent. Revisit only with a new route
   discriminator; do not classify the absent rows as a contract mismatch.
0. **M5 descriptor target:** s4853 found the exact `0x800377C8` descriptor
   control unreached despite title/hangar, SP, action, and PCM positive
   controls. Do not repeat the same target; select the next M5 contract
   boundary with a route-specific control.
0. **M5 A10 guard-class qualification:** closed s4852 as H-A10-legitimate.
   The same-build default/guard-off pair had qualified route-order SP controls,
   32 writers, 262 identical audit/traversal rows, title/hangar, and nonzero
   PCM in both arms. No guard relaxation is authorized; do not repeat this A/B.
1. **M5 next behavior validation:** Step 1 and Step 11 are qualified by s4831
   and s4836, and the Step 8 A10 guard class is closed by s4852. Select the
   next unqualified M5 contract boundary with a fresh positive control; do not
   repeat the invalid request-only route or the A10 A/B.
1. **M3 multiplication class:** closed s4848. The 643 decoded rows all have
   expected signed/unsigned lowerings; 27 stale annotation/ELF mismatches are
   not live multiplication instructions. Do not repeat without new provenance
   evidence.
1. **External retail-entry boundary:** closed s4845. The Rice/input oracle
   route reached title and hangar with whole-RDRAM control positive, but
   `0x800903F0` had zero hits. Revisit only with a new route or PC
   discriminator.
1. **M5 A10 replay (s4830):** the pristine-copy replay ran end to end with `failures=0`; A10 reports 44/44 and A9 reports 13 sites plus the writer. The four whole-file comparisons differ because the live tree contains later diagnostic patches absent from the s4648-fresh replay input, so the replay is valid for these two fixes but not byte-identical to the accumulated live tree. Do not repeat the replay without a new comparison target. A10 guards remain dead on covered routes; no removal is authorised.
1. **VI-640 stall: not reproducible (s4801):** 0/24 stalls since s4794 on the SAME binary (mtime predates s4794); the s4793 recipe's t=20 `sample` call is not the trigger (4+4 A/B, all reach VI 1024 at ~50 s). Cause is an unrecorded external condition. Park; if it recurs in any run, immediately capture `vi-fs stalled=1` state plus `ps`/display/load context. Meanwhile advance M5 plan.
2. **Overlay-0x2C splice evaluation:** mission origin is reached unattended at ~98 s
   (s4802/s4806), no driver needed. Frame-align done (s4803/s4804): no retail mission reference exists; parked pending oracle mission capture.
3. **M5 callback teardown:** park unless a route that reaches
   `shutdownAudioEngine` appears; keep M5 plan going otherwise.
4. **Attached-mesh mission watches:** the s4724 recipe reaches a mission; could
   revisit the `rs_free` NULL contract with mission-phase watches.
5. **Parked, do not repeat without a new discriminator:** M4 accumulator
   boundary, odd-PI DMA, col-511 noise, pillar stubs, 0x1F0D74, external
   retail-entry, rename sweep (see Parked section).

Operational notes: keep soaks <=4 concurrent; every game-launching recipe must
`pkill -KILL -x RogueSquadron64Recomp` in cleanup. Under host load 7-20 the
default recipe stalls at VI 640 or startup-crashes; judge only state-gated
(`vi-fs stalled=1`) samples, never wall-clock ones.

## Evidence and operating rules

Retail oracle watches are physical-address ground truth. Whole-RDRAM, VI, target-PC, and adjacent-range controls must qualify every null. Phase-gate animated comparisons on VI transitions. Batch all counters and A/B arms in one build/run. Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX assumptions. Keep safety guards separate from explanations.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py -> CMake`; never hand-edit generated functions for behavior. If `lib/` changes, export submodule patches in the same session. Never run submodule update, checkout, clean, or hard reset. Kill runs with SIGKILL and run from `build/` with the ROM present. Any mitigation-shaped change needs an `ORIGIN:` line.

See [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) for the evidence archives and [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md) for the audio plan.
- s4817: mult/dmult lowering census closed (docs/M3-S4817-MULT-CENSUS.md)
- s4818: trap/break/syscall/cop0, unaligned/ll-sc/cache (s4820) census closed (docs/M3-S4818-TRAP-CENSUS.md); lvj_checkComplexObjectives syscall proven dead s4819 (data after an immediate return); remaining: M5 passive items

- s4873: port VI thread is the only poster of VI queue 0x80114388 (1/VI; trace 2321 enq vs 2304 update_screen) and posts AI-done 1/VI by design; synth entries still 2.0 per VI message (strict 1,0). AI_EVENT_HZ=115 doubles msgs (control) but not synth entries. Doubling is inside the guest retrace handler / recv shim. Next: log osRecvMesg returns (calls at 0x800198F4/0x80019928) per walk.
