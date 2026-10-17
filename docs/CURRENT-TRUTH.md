# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Maintained
at Session 5108; detailed historical evidence is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md)
and the per-session `docs/M5-S*.md` notes. Git history preserves prior wording.

## Headline

- **s5107:** The bounded generated-symbol sweep renamed the companion
  `bzero` entry at `0x8002A080`: generated `bzero_recomp` had the exact `0xA0`
  span and three live callers. The rename was applied to the generated
  snapshot, overlay table, and rename tooling; audit recorded in
  `docs/RENAME-S5107-AUDIT.md`. This rules out stale-address, split-span, and
  no-caller explanations for `bzero`; no runtime behavior changed.

- **s5108:** The next companion entry, `osEepromLongRead = 0x8002A120`, is a
  host-wrapper entry rather than generated code: the snapshot has three live
  callers and a zero-span overlay record, but no generated prologue/body. The
  bounded rename helper selected no change. The `_recomp` name is preserved as
  an ABI boundary; audit recorded in `docs/RENAME-S5108-AUDIT.md`.

- **s5106:** The bounded generated-symbol sweep renamed the companion
  `bcmp` entry at `0x80029F60`: generated `bcmp_recomp` had the exact `0x120`
  span and one live caller. The rename was applied to the generated snapshot,
  overlay table, and rename tooling; audit recorded in
  `docs/RENAME-S5106-AUDIT.md`. This rules out stale-address, split-span, and
  no-caller explanations for `bcmp`; no runtime behavior changed.

- **s5105:** Restored the missing time/interrupt host-wrapper census tool.
  Its positive-control self-test passed 4/4, and the live census classified
  `osGetCount`, `osSetCount`, `osGetTime`, and `osSetTime` as scalar/time host
  handling with no guest dereference; `osSetIntMask` is an intentional no-op.
  Independent symbol/edge grep agrees. This is source-audit evidence only; no
  runtime guard or soak was warranted. The audited M3 host-wrapper census is
  now complete; generated-symbol renaming is the next eligible bounded work.

- **s5103:** Thread/queue host-wrapper census completed after restoring the
  missing audit tool. The positive-control self-test passed (4/4), and the live
  census covered 16 wrapper/runtime definitions including `do_send`/`do_recv`:
  all pointer-bearing paths were translated/range-checked or forwarded, with
  no raw guest dereference. Direct symbol/edge grep independently agrees. This
  is source-audit evidence only; no runtime guard or soak was warranted.

- **s5104:** Restored the missing timer/virtual/cache wrapper census tool.
  Its four synthetic translated/raw/no-op controls passed. The live census
  classified timer setup and stop through `TO_PTR`/runtime handling,
  `osVirtualToPhysical` as integer-only translation, cache wrappers as
  intentional no-ops, and `osPiGetCmdQueue` as absent from the audited source
  set; no raw guest dereference was found. Independent symbol/edge grep agrees.
  This is source-audit evidence only; no runtime guard or soak was warranted.

- **s5102:** DMA/event host-wrapper census completed after restoring the missing
  audit tool. The positive-control self-test passed (4/4), and the live census
  found 7 translated/forwarded or address-storing paths plus 1 intentional
  `osDpSetNextBuffer` assert/no-op; no raw guest dereference was reported.
  Direct symbol grep independently confirms the wrapper/callee edges. This is
  source-audit evidence only; no runtime guard or soak was warranted.

- **s5101:** M3 host-wrapper guest-pointer census CLOSED for VI/EEPROM/controller/PFS/pak: positive-control audit passed; 15 translated, 5 range-checked+translated, 8 explicit no-op/error returns, and no reachable raw guest dereference. Direct `_arg`/`TO_PTR` and `save_read`/`save_write` inspection independently confirms the classification. Next: remaining DMA/event wrappers (`osPiStartDma`, `osDpSetNextBuffer`, `osSetEventMesg`).
- **s5096:** audit shape 2 (`(uint32_t)X`, `U32(X)`, `0x...u` bases) CLOSED: 0 hits in generated code, 3 in tools/*.py all stale-form detector strings; positive control 3/4 in same run (`scratch/agent/audit_unsigned_base.sh`). Remaining unsigned-base work: s5095 soak verdict fold-in (absent from SOAK-RESULTS at s5096 start), pristine-regen check of the AC8C0 repair branch (blocked s5091). Nothing superseded.
- **s5095:** unsigned-base class CLOSED for the audited shape: s5094 hangar fix confirmed (3/3 arrivals, 0 CRASH); 11 stale env-gated sites repaired via tools/repair_unsigned_base_live.py; soak with all gates ON 3/3 crash=0 (diagnostic lines fired). Open: pristine-regen check of the repair branch.
- **s5094:** hangar flake updateHangarBayScene+76424 ROOT-CAUSED: `[buttons-hangar] port=` diagnostic read `MEM_BU(-0X2930, 0x800D0000u)` (zero-extended base, host addr +2^32). Fixed in funcs_28.c + fixup repair branch; soak s5094_hangar_unsigned_base_fix queued (verify >=2 hangar arrivals, 0 CRASH). Single-source until soak.
- **s5092:** BLOCKED for owner target; M5 plan/steps, M3 classes, sweep, retail-entry, M4, mission stall all closed. See scratch/agent/BLOCKED.md.
- **s5090:** fixup_game_funcs_vendored.py post-condition: regen now fails if funcs_26.c lacks the s4296 A14 yield marker, and warns on RS64_SKIP_REPLAY=1 (control: marker present live/absent when stripped; not yet run through a full regen).
- **s5093 (unblock):** hangar flake updateHangarBayScene+76424 recurs (>=6 hits across sessions), so it is an auditable class, not a single crash; NEXT = hangar-flake-fault-class. Open dependency: mips64-elf-gcc (s5023, human install).
- **s5089 (m6-mission-stall):** WIN=420 mission soak: 426 s past onset, no stall, crash=0 (n=3 with s5086/87); mission never ended (origins alternate 0x620400/0x690400). 1 of 2 runs flaked in hangar (updateHangarBayScene+76424). Stall thread closed; next = M5-AUDIO-PLAN step.
- **s5087 (m6-mission-stall):** apply_s4296 re-applies cleanly in a replay-style sandbox (anchor hypothesis refuted; scratch/agent/s5087_replay_probe.py). Why the 2026-10-16 23:37 regen dropped it is still unknown (likely RS64_SKIP_REPLAY=1 or unlogged). In-arm mission soak n=2 with patch: no stall at 175 s after onset, crash=0.
- **s5086 (m6-mission-stall):** The s5085 mission 'stall' (main thread spinning in shutdownMusyXVoices A14) was a missing patch: built funcs_26.c lacked the s4296 yield (0 tags, 0 `[a14-yield]` rows). Re-applied + rebuilt: same `in` soak ran 186 s after onset with no stall, crash=0, control = 8 `[a14-yield]` rows with b0=0x03 then exit (n=1). Guard: `tools/check_a14_yield_patch.py`. Open: why the last regen dropped the patch (unverified). Supersedes s5085 'open: why A14 never exits'.
- **s5085 (m6-mission-stall):** the s5084 'stall' = MAIN thread spinning in shutdownMusyXVoices (A14 status-03 wait) under endMissionCleanup->finalizeCurrentSpeechBuffer (`sample` stack, arm `in`, 111 s after onset). Idle arm: no stall in 175 s (n=1 each; one idle try crashed in updateHangarBayScene). Open: what ends the mission, why A14 never exits. Supersedes s5084's 'game thread blocked/dead'.
- **s5084 (m6-mission-soak):** mission survives ~75 s then the game thread silently stops (no pad polls, [watch] frozen) while VI keeps ticking with stalled=1; no crash line. Single run. Next: no-input control + `sample` of the hung pid (NEXT.md).
- **s5083 (unblock):** s5082 block re-scoped, not escalated: next unit m6-mission-soak (sustained-input mission soak, NEXT.md). Open non-gating deps: mips64-elf-gcc, rename symbol source, screen capture (TCC).
- **s5072:** Pad input can be injected without display/focus: `ROGUESQ_PAD_OVERRIDE_FILE=path` (file "btn sx sy"; librecomp cont.cpp). Verified by padlog edge (padovr_test.sh). winctl no longer required for key tests.
- **s5068:** In-mission input reaches the game (single-source, N=1): `ROGUESQ_PAD_LOG=1` pad log shows 0 transitions in no-key mission windows and exactly press+release with correct values (W/D stick 127, Z=0x8000, Return=0x1000) in the key window; crash=0, VI advancing. Unmeasured: visible mission reaction. Next: frame capture / game-state read of ship response (NEXT.md).
- **s5067 (unblock):** s5066 "owner must pick a target" re-scoped, not escalated: in-mission input response (never tested) is runnable via the s4958 keyed route. Next unit m6-mission-input (NEXT.md). Open non-gating human deps: mips64-elf-gcc install, symbol-mapping source for renames.
- **s5076:** Mission flight state reacts to the stick (single run, n=1): gate byte 0x130B56=0 throughout; float triple at 0x9DEAC static in both no-key windows, 57/247 distinct values in the W/D hold windows (`ROGUESQ_WATCH_LOG=1`, `scratch/agent/s5076_watch.sh`). Open: name the object/writer; ctlB movement after release unattributed. Answers the s5075 open question.
- **s5075:** Game stick-state struct located: `0x80130B88` (port*6: btn u16, stickX s8 @+2, stickY s8 @+3, valid @+4), filled by pollControllerInputs 0x80002FF4 from raw OSContPad `0x8010FF30`; readers 0x80079D54/0x8007A068/0x8007A0A8. s5069 keyW snapshot shows y=0x7f at both addresses, ctl1-3 zero (n=1). Input reaches the game struct in mission; open question is whether flight code reacts. Replaces snapshot-diff designs (s5069-s5074).
- **s5066:** Priority list exhausted (M5, M3 classes, rename sweep, retail-entry, M4 all closed); loop BLOCKED awaiting an owner-chosen target. See scratch/agent/BLOCKED.md.

- **s4933-s5033 headline entries** (retail/port boundary joins, heap-guard census, rename audits, assembly-patch toolchain notes) migrated to PROJECT-OVERVIEW.md ("Archive: CURRENT-TRUTH headline entries"). Survivors: retail-entry boundary closed for title/hangar/mission (s5029); keyed mission route works (s4958); stale-base s4540 bad rows not closed by ordering/atomic/lock variants (s4982-s4987); mips64-elf-gcc absent (non-gating).


## Durable state

### M5 audio

- Audio is active, not a zero-output stub: nonzero PCM and corrected AI byte
  order are qualified on the current route. M5 plan: `docs/M5-AUDIO-PLAN.md`.
- The qualified route reaches attribution, N64 logo, intro, Factor 5 logo,
  title (`0x00790400`, VI 1024), hangar (`0x006AB400`, VI 512), and mission
  (`0x00690400`, VI 512; later `0x00620400`). Retail mission qualification
  passed whole-RDRAM/VI controls and reached both mission origins (s4932).
- The s4927–s4930 mission joins show fresh audio route ordinals and row-0
  resets across the `0x00690400 -> 0x00620400` handoff, with PCM activity.
  This is legitimate port-side route reinitialization, not a basis for a
  guard or skip; retail ordinal parity is unclaimed.
- Retail/port task-family class matches (`0x80149470`, type 2), while retail
  publishes mostly `data_size=2` and port mostly `1`; s4887 closed this as a
  cadence difference. The s4933–s4937 writer/auxiliary captures supersede the
  old assumption that `0x80091784` is the task publication site.
- The voice-render range fires in retail title and hangar, but exact consumer
  `0x800903F0` remains absent (s4897). Treat this as an internal boundary, not
  as route absence and not as authorization for filtering.
- First-teardown synth deregistration is named and fixed (s4890). The covered
  route does not reach `shutdownAudioEngine` (s4894); callback registration
  rows do not prove shutdown execution. Synth `+5808` idle title/hangar crash
  family is closed by the default pause fix (s4786).
- Current default stability: title/hangar longevity is qualified; mission
  route captures have advanced counters and zero crash/abort markers in the
  cited runs. Judge future runs by phase controls, never wall-clock alone.
- The s4939 auxiliary-store witness is regeneration-preserved in the fixup
  template and records the four store sites with phase, order, value, and
  `s0/s1`; its title controls passed, while the requested hangar phase was not
  reached by the driven port capture.
- The s4941 retail watch-boundary run confirms that the odd byte is written by
  the retail store at `0x800917C4`; exact one-byte watch nulls are therefore a
  watch-boundary artifact, not evidence that the field is unwritten.
- s4984's atomic pair variant is regeneration-preserved by
  `tools/apply_s4984_atomic_voice_pair.py` and the vendored replay list. It
  uses host acquire loads and release stores for guest `0x80149700`/
  `0x801496F8`; the mission route remained qualified, but stale rows increased
  from 4 to 8 in this one run.

### M3 and rendering

- M3 idiom audits are closed for trap/break/syscall/cop0, unaligned and
  LL/SC/cache, integer division, float conversion/compare/FCSR, memory-width
  operations, indirect calls, self walks, branch-likely, variable shifts,
  HI/LO moves, 64-bit shifts, 32-bit multiplication, and 64-bit mul/div
  (s4975: 66 sites, 2 real, zero-divisor benign on arm64). Do not repeat a
  class without new recompiler or provenance evidence.
- Conditional moves (`movz`/`movn`) were a recompiler defect but are DONE since s4970
  (N64Recomp patch + `tools/fixup_movz_movn.py`; census 179/179 `do_break` -> 0/179).
- Factor5 runaway-DL cause is known: op `0xBD` loads overlay `0x2C` (ROM
  `0x27368`, destination `0x1DB0`) without a route, restarting the task.
  Runaways occur in VI-640 and much of mission; splice effect remains parked.
- Native port hangar artifacts (rim band, holo spikes, right-edge stale data)
  remain localized. M4 accumulator origin, pillar references, `0x1F0D74`, odd
  PI DMA, and external retail-entry are parked pending a genuinely new
  discriminator.

### Operational constraints

- Retail oracle watches physical addresses and require whole-RDRAM, VI, and
  phase controls before any null is interpreted. Use `docs/F5-UCODE-REFERENCE.md`
  for Factor5 command semantics.
- Batch all counters and A/B arms in one build/run; phase-gate animated
  comparisons. A mitigation-shaped change requires an `ORIGIN:` naming the
  writer and stating whether its value is legitimate.
- Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
  CMake`; generated functions are not hand-edited for behavior. If `lib/`
  changes, export submodule patches in the same iteration. Never use
  submodule update, checkout, clean, or hard reset. Kill runs with SIGKILL.

## Parked and closed

- VI-640 crash families and broad guard classes: no reproducible current
  failure; any recurrence needs phase state plus process/display/load context.
- External retail-entry: Rice route is qualified through title/hangar but the
  old exact PC is absent; do not repeat without a new route or PC discriminator.
- M4 accumulator boundary (closed s5006: hangar 0/1955 = retail 0/576; the 8 port 640-phase 0x8000 rows are ordinary values, no clamp shape), attached-mesh mission contract, hangar pillars,
  col-511 noise, `0x1F0D74`, and overlay-registration chunking are parked.
- Generated-symbol renaming is active again because the companion now supplies
  additional semantic mappings. s5025 qualified and preserved
  `func_800B3824 -> buildLevelSelectTextTextures`; continue one candidate at a
  time with the semantic-name, exact-span, and live-caller gates. The older
  s4999 no-safe-map result still applies to `0x8000040C` and `0x800E9AE0`.
- M3 patch-runtime qualification remains blocked on the MIPS GCC toolchain.
  s5023 independently confirmed that CMake omits `PatchesLib` when GCC is
  absent; the available assembler/linker are sufficient only for the
  assembly-only artifact.

## Superseded conclusions

- **s5007/s5009: "loop needs an owner decision; no runnable experiment"** — believable because every audited thread was closed and the s4993 per-origin budget had been run. Wrong because the mission-qualified s4994 sample was runnable via the soak queue; it had just never been enqueued (s5010).

- **s5001 “M4 accumulator witness needs a human-installed LLE RSP plugin”** -
  believable because the oracle README names `mupen64plus-rsp-hle` and s4689
  measured no accumulator/DMEM rows, and the s4514 cxd4 build was not carried
  forward. Refuted s5002: a built cxd4 dylib already exists in the maintained
  oracle tree and reached the hangar in s4514; exposing `VACC` is a local patch.
- **s4985 “a narrower publication/observation lock will close the stale-base
  calls”** - believable because it preserves exclusion only over the writer's
  base/count stores and the mixer's paired count/base loads, avoiding the
  route-blocking span of the whole-function mutex. Overturned by the
  same-run armed soak: title, hangar, mission, allocator, PCM, and no-crash
  controls all passed, but kind=bad=8 remained. This is single-source
  evidence against this lock placement; it does not prove which reader or
  writer produces the rows. No guard or value rewrite was added.

- **s4982 “a reader acquire fence will close the stale-base calls”** - believable because the writer now has a release fence after both base stores and before the legitimate count publication. Overturned by the clean same-route soak: allocator and mission controls passed, but the four `s4540` bad rows remained. The ordinary `MEM_HU` load plus fence is not an effective pair handoff; no guard or value rewrite was added.
- **s4983 “explicit atomic guest-memory observation will close the stale-base calls”** - believable because both publication sites and both mixer reads were changed to host acquire/release atomics at the exact guest locations. Overturned by the same-route armed soak: controls passed, but 8 stale rows remained. This leaves a lock-compatible handoff as the next discriminator; no guard or value rewrite was added.

- **s4985 “a host mutex around both complete functions will close the stale-base calls”** - believable because it provides exclusion across allocator publication and mixer observation. Not selected: the same armed recipe did not reach the title positive control, despite one allocator entry, so the whole-function lock is route-blocking/unevaluable. This does not refute a narrower publication/observation lock; no value guard or rewrite was added.

- **s4981 expected "writer reorder closes the race"** - believable because the
  source fix moved the legitimate count publication after allocation and added
  a release fence. Overturned by the same-run armed validation: allocator
  control and 9 array-control rows fired, yet 4 stale-base calls remained.
  This selects a reader-side ordering defect; no guard or value rewrite was
  added.

- **s4959 "BLOCKED: multi-minute recipes cannot be waited on inside an iteration"** - believable because foreground sleep/polling is blocked and the Stop hook fired six times mid-run. Overturned by the unblock iteration: the soak queue (ITERATION.md, 600 s cap per recipe, verdicts in SOAK-RESULTS.md) is the intended mechanism; the x3 script was just too long for it. Split into soak_queue/s4959_mission_run{1,2,3}.sh. Mission stability is still unmeasured.

- **s4950 "5/5 reached mission" (0x690400, VI-512)** - believable because the phase appeared after scripted keys and had a distinct width/origin. Overturned s4954 (script ordering + deterministic timing) and s4955 (3/3 solo run, hangar control absent): it is the attract demo, not player-mission evidence.

- s4950's "5/5 reached mission" (and its `stalled=1` stall grep) was refined by s4953: `stalled=1` appears at every phase, and the 512 phase is only ~3-4 s before return to title, so it is not established as a player mission. Believable because the origin 0x690400 matched the retail mission origin.

- s4934's “writer attribution” was refined by s4935–s4937: `0x80091784` is
  real mission-phase auxiliary activity, not yet an OSTask publisher.
- s4940's phase-route-mismatch selection was overturned by s4941: the same
  aligned watch with the qualified Rice route reached title and hangar and
  captured the target store. The earlier null remained valid only for its
  pre-route run.
- s4893's claim that the route reached `shutdownAudioEngine` was overturned by
  s4894's kind-0 entry and kind-2 return markers; only kind-1 registration rows
  occurred.
- The apparent port retrace burstiness was overturned by s4901: two
  `update_screen` calls represented one true origin change; port pacing is
  steady at two retraces per origin versus retail one.
- The early `+9668` bus error was our own unsigned diagnostic address bug,
  fixed with `S32()` (s4696); older recipes arming that probe are suspect.
- “M5 is fully closed” was too broad: nonzero PCM proves route activity, not
  task-contract, ownership, wait-gate, safety-exit, or MORT correctness.

## RESOLVED (s5050) - s5049 clobber of N64Recomp/RecompiledFuncs
The s5049 in-place regen (tools/agent/regen_n64recomp.sh, still disabled) destroyed the live tree, but it is RESTORED and verified: N64Recomp/scratch_s4970_live (Oct-13 copy) + replay of post-s4970 scripts (scratch/agent/s5050_replay.sh, s5050_s5037.sh) compiles to byte-identical __text for 51/51 funcs_*.c vs the surviving build/libRecompiledFuncs.a (scratch/agent/s5050_compare.py). funcs.h/lookup.cpp/recomp_overlays.inl identical to the clobbered copies. The clobbered tree is kept at N64Recomp/RecompiledFuncs.s5049-clobbered. cmake --build is safe again (it recompiles ~5 files whose mtimes the replay touched; code identical). Never regen in place; "live tree is unreproducible" was wrong: backup + ordered apply_s* replay reproduces it.

## Next steps (single monotonic backlog)
- s5108: `osEepromLongRead = 0x8002A120` is a host-wrapper entry, not a
  generated placeholder. Its three callers and zero-span overlay record are
  documented in `docs/RENAME-S5108-AUDIT.md`; preserve the `_recomp` ABI name.
  Next: audit the following companion-mapped entry only, `osEepromLongWrite =
  0x8002A1B0`, with the same generated-body/overlay/caller gates.
- s5106: `bcmp_recomp -> bcmp` passed companion semantic-name, exact-span, and
  live-caller gates and was applied to the generated snapshot and overlay
  table. Next: continue the bounded companion-symbol sweep at the next
  semantically mapped candidate; do not build or soak naming-only changes.
- s5105: Time/interrupt host-wrapper class closed. `tools/audit_time_interrupt_wrappers.py`
  passed its 4/4 positive-control self-test; the live census found eight
  scalar/time implementations without guest dereference and one intentional
  `osSetIntMask` no-op. Independent symbol/edge grep agrees. No runtime build,
  guard, or soak was authorized. Next: resume the generated-symbol renaming
  sweep, using the companion semantic-name, exact-span, and live-caller gates.
- s5104: Timer/virtual/cache host-wrapper class closed. The restored
  `tools/audit_timer_virtual_cache_wrappers.py` passed its positive-control
  self-test and live census; direct symbol/edge grep independently confirmed
  the classifications and showed no `osPiGetCmdQueue` definition in the
  audited runtime sources. No raw guest dereference was found and no runtime
  build or soak was authorized. Next: audit the remaining time/interrupt
  wrappers (`osGetCount`, `osGetTime`, `osSetTime`, `osSetCount`, and
  `osSetIntMask`) with the same translated/raw/no-op census.
- s5103: Thread/queue host-wrapper class closed for the audited set. `tools/audit_thread_queue_wrappers.py` passed its synthetic raw/translated/no-op controls; live census covered the seven requested wrappers plus `do_send`/`do_recv` runtime callees and found no raw guest dereference. Direct symbol/forwarding grep independently confirmed the wrapper/callee edges. No guard or runtime build was authorized. Next: remaining timer/virtual/cache host wrappers.
- s5102: DMA/event host-wrapper class closed for the audited set. `tools/audit_dma_event_wrappers.py` passed its synthetic raw/translated/no-op controls; live census classified `do_dma`, `osPiStartDma_recomp`, and `osEPiStartDma_recomp` as translated/range-checked callee paths, event wrappers as forwarded/address-storing, and `osDpSetNextBuffer_recomp` as intentional assert/no-op. Direct symbol grep independently confirmed all wrapper/callee edges. No raw guest dereference was found; no guard or runtime build was authorized. Next: remaining thread/queue host wrappers.
- s5100: shape 4 (bare narrow-int local/param as MEM_x base) closed: census 26 gpr, 10 gpr params, 1 benign int loop index; tools/audit_narrow_base.py (control 2/0, live 0) gated in fixup post-condition. s5099 soak folded: rc=0, hangar_arrivals=3 crash=0. Unsigned-base class closed. Next M3 class: host wrappers (osViSwapBuffer, EEPROM/pak buffer args).
- s5099: shape-3 now gated too: tools/audit_uint32_s32_base.py (selftest control 1/0, live tree 0 hits) is called from the fixup post-condition after s5097's; not run through a real regen. Soak s5099_shape3_fix_soak queued (hangar route, scene-node-cache guard log on) - fold its SOAK-RESULTS line next iteration. Next M3 class: bare int/unsigned locals as MEM_x base after regen; then remaining host wrappers (osViSwapBuffer, EEPROM/pak buffer args).
- s5098: unsigned-base shape 3 (bare uint32_t var as MEM_x base): 2 live wild-address sites (scene-node-cache zero_hi guard, heap-dequeue diagnostic) fixed in fixup + generated tree; audits scratch/agent/audit_base_shapes.py + audit_bare_base_types.py. Needs a build+soak confirmation (NEXT.md).
- s5097: unsigned-base class closed (shapes 1+2) and now gated: fixup_game_funcs_vendored.py aborts on regression after replay (regex control + live=0; not run through a real regen). No open item in this class.
- s5063: SP StartGo + AI SetNextBuffer guard landed (ROGUESQ_SPAI_GUARD[_FORCE]); FORCE pg=16, default pg=0 => class clean on keyed route (two-source). Next M3 class: remaining host wrappers (osViSwapBuffer, EEPROM/pak buffer args).
- s5062: do_rom_pio guard landed (ROGUESQ_PIO_GUARD[_FORCE]); FORCE arm fired 0 => PIO never invoked on keyed route (unexercised, not clean; single-source). Next M3 class: SP/AI DMA host wrappers.

> s5058: baseline hangar recipe reaches hangar 3/3 on the current binary at load 4-6 (4/4 with s5057); host load is not the discriminator. Next: census-on recipe x3 (NEXT.md).

> s5047: queued soak s5047_route_flake_hostload (2 back-to-back runs, per-key rc + host load). Read SOAK-RESULTS first: both pass = host-load flake (H1); both fail = rebuild with s5038 census / s5039 lib hook compiled out (H2) else H3 build staleness. Host load avg was 7.2 (Chrome/REAPER) at s5047.

- **s5044 note:** s5043 refuted 'GUARD2 dropped' as the cause of the poison-arm route stall; the only remaining recipe delta vs s5037 is ROGUESQ_FREE_CENSUS=1 (4/4 census runs stalled, 3/3 non-census reached mission; single-source). Do not combine census with keyed-route soaks. Poison arms re-queued as s5044_*_nocensus.

**s5041 (top):** double-free census (rs_free/rs_malloc shadow set) clean on the mission route: 0 doubles in >=16K frees, force control 16384/16384. Next: poison-on-free read-after-free probe (NEXT.md).
**s5040:** mq census class closed on keyed route (jam never called under force; setevent control fired). Next: use-after-free readers after audited frees (scratch/agent/NEXT.md).

**s5030 (top, supersedes the s5027 rename item):** The generated-symbol renaming
sweep is CLOSED. Measured on the current N64Recomp/RecompiledFuncs tree: 2 of the
~1,548 s1487 placeholders remain (`func_8000040C`, `func_800E9AE0`) and both already
have `tools/rename_generated_symbols.py` entries (the tree just predates the mapping);
all 14 remaining menu-overlay companion candidates 0x800B32F4..0x800B4048 are already
generated under their companion names (N64Recomp reads the symbol files). Adding more
helper entries is a no-op. The next unit must be M5 / M3 / retail-entry work, or a
human decision on the missing MIPS GCC toolchain (s5023). Gate script:
`scratch/agent/s5030_rename_gate.py LO HI`.

**s5027 (top):** The next bounded rename candidate is the next newly mapped
menu-overlay symbol. Apply the same independent companion-address, exact-span,
and live-caller gates before adding it to
`tools/rename_generated_symbols.py`; reject stale, split, or callerless
records. Keep runtime and patch qualification unchanged.

**s5025 (completed):** `func_800B2630 -> buildFormatMessageGlyphBuffer` passed
all gates and is now explicit in the regeneration helper. The snapshot was
already synchronized, so no generated code or runtime behavior changed.

**s5023 (top):** The normal `PatchesLib` target is not present after a clean
reconfigure because `mips64-elf-gcc` is unavailable on this host; only
`mips-linux-gnu-as/ld` are installed. The patch-runtime qualification is
blocked until a MIPS GCC toolchain is supplied. Do not substitute the
assembly-only artifact for this test or enable the override. Once GCC is
available, rerun `cmake -S . -B build -DMIPS_TOOLCHAIN_DIR=<toolchain>`, then
`cmake --build build --target PatchesLib -j2`; successful generation and
compilation selects the normal-path hypothesis, while a generated relocation
failure selects the residual-artifact hypothesis.

**s5022:** The exact-span assembly now passes N64Recomp after the ELF
reader integration fix for absolute linker aliases that match game reference
symbols. The next bounded unit is to build the normal patch pipeline with the
C implementation excluded only for this validation, confirm the generated
host artifact is accepted by the CMake target, and keep the runtime override
disabled until that artifact-level integration is qualified.

**s5021 (completed):** The recovered generated snapshot and reconstructed assembly
now agree on the complete `0x80007D74..0x80007E58` window and exact `0xE8`
span. The remaining bounded unit is an N64Recomp integration fix for the
faithful direct call to `findAndUnlinkSmallestEntry` at `0x8002221C`; the
current tool reports no function for that external `jal` and clears output.
Keep the override disabled until the exact assembly is consumable, and do not
replace the direct call with an indirect sequence merely to satisfy the tool.

**s5020 (superseded):** The missing source artifact was not yet located; this
is superseded by s5021's preserved generated snapshot and exact reconstruction.

**s5019:** The assembly-only patch pipeline and corrected symbol identity
are qualified, but the first bounded slice is structurally incomplete (0x44
bytes emitted versus the original 0xE8-byte entry). The next bounded unit is
to hand-port the remaining original `allocateDisplayListBuffer` control flow
and queue stores in assembly, then compare its disassembly and generated host
function to the known 0x80007D74–0x80007E58 path. Keep it disabled until the
full path matches; the missing MIPS C compiler still blocks compiling
`patches/heap_guards.c` directly.

**s5020 (top):** Obtain or reconstruct the missing recovered instruction window
for `allocateDisplayListBuffer` (`0x80007D74..0x80007E58`) before extending the
assembly probe again. Compare its branch targets and every memory store with
`patches/heap_guard_asm.S`; a source-backed exact `0xE8` span selects faithful
assembly coverage, while absent or ambiguous source leaves this M3 route
blocked. Do not enable the override or pad the function to match size.

**s5012 (top):** The mission-qualified s4994 sample ran validly (mission_onset_t=173, arm=1, crash=0): 32 of 32 mission-origin s4540 caller rows were current-base `0x8018C720`, 0 stale `0x801714D0`; with s4993 (0 bad rows at mission origins) this closes the mission-phase `kind=bad` thread. No runnable M5 unit remains; next eligible work is a genuinely new M3 idiom class or a new witness for the parked retail/M4 boundaries. Declaring M5 done stays an owner call, non-gating.

**s5010 (top):** The s5007/s5009 "BLOCKED on owner decision" was refuted: running the queued mission-sample soak needs no human decision (the s4994-instrumented binary is already built). Enqueued `soak_queue/s5010_s4540_mission_sample.sh`; next unit is consuming its verdict (NEXT.md). Declaring M5 done stays an owner question but is non-gating.

**s5007 (top):** All priority threads are closed or parked; loop is BLOCKED on an owner decision (scratch/agent/BLOCKED.md). Only live defect: mission-phase `kind=bad` voice-index reads (H-lock-required); s4985 lock attempt was route-unevaluable.

**s5000 (top):** The external-retail retry is route-mismatched: retail reached
the qualified phases and remained absent at `0x800903F0`, but the port did not
reach qualified hangar. Keep this question parked until a new port route
reaches `0x006AB400`; no mitigation was added.

**s4999 (prior):** The residual generated-symbol audit found no safe rename. The
`0x8000040C` entry has a live caller and exact span but no semantic companion
name; `0x800E9AE0` has an exact span but no semantic companion name or
generated live caller. The local inferred/mechanical rename entries do not
meet the gates. No generated file, mapping, or behavior was changed. Detailed
evidence: `docs/RENAME-S4999-AUDIT.md`. The symbol sweep is closed pending a
new mapping source; next eligible work is a genuinely new M3 class or the
parked external-retail/M4 boundary only if a new witness exists.

**s4998 (prior):** The complete register-target indirect-call audit closed the
remaining non-`$ra` M3 dispatch class: 113 `LOOKUP_FUNC(ctx->rN)` sites split
into 42 memory-derived, 3 arithmetic-derived, 11 other, and 57 locally
unresolved callback/data-as-code sites; the independent census found 177/177
jump-table `switch_error` defaults and 114 `$zero` sites in known data regions.
No silent lowering or reachable malformed dispatch was found, and the runtime
log search found no CPU missing-function marker. No guard or recompiler change
is authorized. M3 is parked pending a new class or witness; the next eligible
unit is the generated-symbol-renaming sweep after its required last-15-session
preflight.

**s4995 (prior):** The new ordinary s4540 caller sample is live and regeneration-preserved, but the s4984 retry reached hangar and pre-mission origins only (`mission_onset_t=-1`), with no mission-origin rows. The s4540 arm and s4987 observations fired, proving the instrument, but their pre-mission phase cannot discriminate the hypotheses. This thread is parked after the mandatory pivot; its mission-origin zero remains unevaluable. ORIGIN: legitimate writer is `allocateSongChannelArray`; this remains an observation/propagation boundary, not a value-rewrite target.

**s4984 (prior):** The explicit atomic count/base loads and release stores reached mission (onset 176 s) with `ctl_arm=1`, `s4579A=9`, `bad=8`, `pidma=0`, crash=0, abort=0, and PCM positive control 147. H-atomic-observation is refuted for this implementation; H-lock-required remains.

**s4981 (prior):** Armed soak s4980 showed the count-before-base race LIVE (`[s4540-call] kind=bad` s0=30 count=32 against the old 18-voice base; ctl_arm=1). Root cause: the s147 reorder never reached the live funcs_23.c. Fixed by `tools/apply_s4981_count_after_base.py` (applied, replay-registered, built). Verification showed the route and allocator were live, but the reader still logged 4 bad calls; see s4982.

**s4980 (prior):** Default soaks since s4959 never armed the env-gated S45xx instruments (0 `[s4539-entry] kind=arm` lines), so their zero `kind=bad`/`pi.cpp` hits are uninterpretable; 6 uninstrumented mission runs had 0 CRASH. Armed recipe queued (`soak_queue/s4980_armed_mission_a.sh`), verdict decides close vs source fix (NEXT.md).

**s4979 (top):** Retail-entry boundary CLOSED as design-dead. Two-source offline check (`tools/voice_kind_crosscheck.py`, no new run): (a) port `[init-desc]` rows are retail-consistent — 11,444 rows, only descs `0x8013ACA0` (d04 top nibble 0xB -> flag set, kind 3) and `0x8011C820` (d04 `0x801B2C60`, nibble 8 -> flag clear, kind 0); init (`0x80092234-0x80092268`) sets flag bit0 only when `(d04&0xF0000000)!=0x80000000`; (b) retail also inits kind-0 voices from `0x8011C820` (ra `0x800980f4`) and their next renders show flag v0=0 at `0x800901C0`, so they never reach `0x800901CC/0x800903F0`. H1 (init skipped) and H2 (stray ASCII store) refuted; the port reaches 0x800903F0 only via s4577/s4578's mixer index past the 18-voice array (count stored before `rs_malloc`, base after) into name-string memory. Not a retail boundary; no guard added.
**s4978:** Retail branch census: 0x800903F0 is design-dead in retail. Flagged voices always have `+0x6D==3` (241,308 hits); the `+0x6D==0` branch at 0x80090358 has 0 hits. The port reaches it, so port voice records carry kind 0 with the flag set, a state retail never makes. Next: port-side histogram of `+0x6D` and its writers (NEXT.md).

**s4977 (prior):** M3 idiom census EXHAUSTED: mfc1/dmfc1 width (4 dmfc1/dmtc1 sites, all $zero), sltiu sign (2 negative-imm sites, data-as-code, semantics correct), jr non-ra (176 $v0 jump tables; 12 $zero data-as-code; ~14 LOOKUP_FUNC uninspected) all benign. Next: REVISIT external retail-entry with a new angle (see NEXT.md).

**s4976 (top):** ldc1/sdc1 alignment class closed: 12/2644 misaligned-offset sites, all data-as-code; LD/SD are 32-bit pairs so arm64 cannot fault. Remaining M3 candidates: mfc1/dmfc1 width, sltiu, jr non-ra.

**s4975 (prior):** 64-bit mul/div class closed (see M3 list). Remaining unexamined M3 candidates: ldc1/sdc1 alignment, cvt rounding modes, mfc1/dmfc1 width, sltiu, jr non-ra. Then resume backlog item 3/4.

**s4974 (top):** s4972r soak consumed: 5/5 runs seen640=1 (positive control) and exit640@48s, bad=0. With s4971 (4/4) that is 0/9 VI-640 stalls vs s4794's 2/5; Fisher p~0.1, so not proven gone but not reproducible. VI-640 route wall CLOSED as non-observable (re-open only on a stay640 line in any future soak, since all recipes now arm seen640). Next: M3 census of idiom classes NOT in the closed list (see NEXT.md).

**s4973 (prior):** s4972 soaks never ran (zsh ${0:A:h...} bug, rc=2 in 0 s). Requeued as soak_queue/s4972r_vi640_idle_a.sh (5 idle runs; verdict in soak_results/s4972r_a/summary.txt, seen640=1 is the positive control). 0/5 stall => close the VI-640 wall; any stay640 => reproduced stall, investigate phase-gated.

**s4971 (prior):** VI-640 boot stall NOT reproduced (4/4 idle/loaded arms exit at 48-50 s, loadavg up to 39; no positive control, so not proof it is gone). H-load unsupported. Route wall is not currently observable; next: N>=10 repeat in soak queue to bound the rate, else treat as closed.

**s4970 (prior):** movz/movn DONE: N64Recomp now emits them (submodule-patches/n64recomp-movz-movn.patch), live tree patched by tools/fixup_movz_movn.py (census 179/179 do_break -> 0/179), build 0 errors, title+hangar smoke crash=0 (scratch/agent/s4970_smoke.sh). Live RecompiledFuncs is not reproducible from fixup_game_funcs.py alone (many apply_s*.py layers). Remaining pivot target: VI-640 route wall.

**s4969 (top):** the s4968 block was not an owner decision; re-scoped. Next unit is movz/movn support in N64Recomp via scratch regen (engineering-only, dormant defect, no runtime change expected); see NEXT.md.

**s4968 (prior):** long hold CLEAN (alive to 586 s, crash=0, PCM nz>0); M5 closed. Mandatory pivot has no remaining target; BLOCKED, see scratch/agent/BLOCKED.md.

**s4967 (prior):** Step 10 was already qualified at s4857, so the only open M5 item is a long mission hold. `soak_queue/s4967_mission_image_long.sh` is enqueued (image arm, ~310 s hold, cap 600 s); no verdict yet. Clean => long-hold qualified, then pick an M3 idiom-class audit; crash/stall => name the writer (rule 11). See NEXT.md.

**s4966 result (prior):** mission image-vs-silent A/B (s4964_mission_{image,silent}) both crash=0 abort=0 over ~320 s, onset t=183 vs 186 s; image pcm_nz_rows=131, silent 0 (controls valid, n=1/arm). H-stable-both: the audio image is not the mission-stability factor on the keyed route. Next: take the next unqualified row of M5-AUDIO-PLAN's execution sequence (Step 10 host PCM consumer / longer mission hold); see NEXT.md.

**s4965 (superseded by s4966):** recipes enqueued; now consumed.

**s4963 result (superseded by s4964):** s4959 run1/run2 VALID: mission (0x690400) at t=186/185 s held to 314 s, crash=0 abort=0, pcm_nz_rows 151/153 of 168 (n=2, keyed route). Run3 still queued: consume its SOAK-RESULTS line, then take the next unfinished step of M5-AUDIO-PLAN's execution sequence.

**s4962 note:** s4959 run1/run2 verdicts (rc=1) are INVALID — recipes ran under /bin/bash with zsh-only `${0:A:h}`, empty ROOT; fixed by zsh self-re-exec, all three re-queued.
**s4960 next (top; still unrun at s4961):** consume the verdicts of the three queued soaks scratch/agent/soak_queue/s4959_mission_run{1,2,3}.sh (SOAK-RESULTS.md, soak_results/s4959_mission_run*/keys*.log); do not babysit or rerun. rc=137 = timeout, not a result. Then add the mission-phase row to docs/M5-AUDIO-PLAN.md.

**s4958 next (superseded by s4960 above; recipe unchanged):** repeat the keyed route N=3 with mission-phase audio/PCM counters (see NEXT.md). Older, resolved by s4958: **s4957:** hangar keycode sweep (15 keys: A/B/Start/D-pad) never reaches a mission (0x690400/0x620400 = 0); the 5th A leaves to the 0x6A2900 model viewer. Input delivery works. Next: find the mission-launch state/flag (see scratch/agent/NEXT.md), try keys inside the viewer.

**s4955 next (top):** s4955 solo N=3 run confirmed the 512/0x690400 phase is the attract demo (bounces to title 3-5 s after onset; hangar 0x6AB400 never reached, keys sent only after 512 appeared). Next: rerun with keys sent at the TITLE phase (~50 s, origin 0x790400), hangar 0x6AB400 as control, then judge mission stability; see NEXT.md.

**s4954 next (superseded by s4955 above):** resolved as demo. Next: M5 plan row for the keyed route (title->hangar->mission) with the s4943 recipe; see NEXT.md.

**s4952: unblocked** - s4951 scope question re-scoped to NEXT.md (VI-progress metric from s4950 logs, then mission-phase M5 row). stalled=1 is not a VI640 indicator. Declaring the milestone done remains an owner decision.

0. **s4945 note:** s4944's "~11x more synth frames per VI" is a witness artifact (aux-store row cap resets per origin flip; rows/flip 32.8 image vs 30.8 silent; flips 49 vs 512). The arms are equivalent per flip; the image arm just presents fewer flips (cause undiscriminated, single-source offline).

1. **Completed — s4939:** perform the phase-gated retail/port join for
   `0x800A1778`, `0x80149702`, and `0x80149988/8A`, using whole-RDRAM and VI
   controls plus port `musyxSynthFrame`/`aspTask=0x80149470` controls. Match
   store order, values, and cadence in one table. The title-phase arm is
   unresolved because retail `0x80149702` was absent and the port did not reach
   hangar. No rewrite or filter was added.
2. **Completed — s4941:** repeat the aligned retail watch with the qualified
   Rice route and verified Start presses. The aligned watch and field-aware
   rows identified the legitimate `0x800917C4` store in title and hangar;
   exact odd-byte watch nulls are closed as a boundary artifact. Do not add a
   rewrite, filter, or port instrument for this field.
3. **Completed — s4944/s4964:** run the A1 image/silent auxiliary-store A/B concurrently with
   title + mission origins as controls (route qualified by s4943); relaunch any
   arm that stalls at VI-640 rather than reading it as a null.
4. **Partly done — s5003 (capture only):** patch the already-built cxd4 LLE RSP
   (`rs64-oracle/src/mupen64plus-rsp-cxd4`, global `VACC[3][N]`) to dump
   accumulator + DMEM, run with `tools/oracle/rdplog` and positive controls
   (title VI 1024 non-empty, hangar `0x006AB400` reached, dump non-zero on a
   known F5 task), then compare the first accumulator publication against the
   port. Do not rewrite or guard any value. Keep the patch diff under `tools/oracle/`.
   s5003 landed the patch (`tools/oracle/patches/cxd4-rsp-dump.md`) and the
   recipe `scratch/agent/s5003_cxd4_dump.sh`; capture `scratch/agent/s5003/rsp.dump`
   passed all controls (6536 records = 2089 gfx + 4447 audio; gfx count equals
   2089 rdp rows; VACC non-zero in 5603; VI 1024 and 512@0x6ab800 reached).
   s5004 retail baseline: 0/576 hangar gfx tasks end with any VACC lane == 0x8000 (also 0 in every other phase); refutes retail-also-saturates, single-source until the port side is compared.
   **s5005 CLOSED (two-source):** the port's task-end accumulator (`ROGUESQ_LOG_M4_END`,
   fixup 10b, `tools/m4_end_table.py`) at hangar 512 (phase ord 5) is 0/1955 tasks with
   any 0x8000 lane, nz>0 in 1955/1955 (positive control) - same as retail 0/576. The
   end-of-task accumulator is NOT the carrier of the hangar Y=0x8000; M4 accumulator
   thread closed at task-end granularity (mid-task not examined). Residual lead: port
   640 phase (ord 3) has 8/1281 tasks with an accl 0x8000 lane vs retail 640 0/425
   (likely a legitimate 48-bit value; unclassified). Capture: scratch/agent/s5005_port_end_acc.sh.
5. Revisit M3 only as a complete idiom-class audit with a new discriminator;
   conditional-move recompiler support is a separate engineering task.
6. Revisit external retail-entry only with a recipe that reaches the qualified
   port hangar phase; otherwise keep it parked.
7. Resume symbol renaming only after the required last-15-session preflight
   shows it is not a REVISIT and a new mapping source exists.
8. **Next:** when a MIPS GCC compiler is supplied, configure with explicit
   `-DMIPS_GCC=... -DMIPS_LD=...` paths and build `PatchesLib`; classify
   generation/compile success, target omission, or relocation/symbol failure.
   Until then, do not repeat the blocked qualification command.

## Evidence index

The detailed s4822–s4937 headline history and older backlog are archived in
`docs/PROJECT-OVERVIEW.md`; per-run evidence is in the session-specific M5/M3
notes and `PORTING-STATE.md`. The next iteration must read `scratch/agent/NEXT.md`
and the tail of `scratch/agent/SOAK-RESULTS.md` before acting.

- s4947: aux-store A/B thread closed; arms identical on [phase] transitions (6 each), pacing, rows/flip. Not a lead.
- s4948: all tiers closed or unevaluable; BLOCKED for owner decision (see scratch/agent/BLOCKED.md).

### s4950 update
Mission-route soak (solo, N=5): 5/5 reached origin 0x690400, 0 do_break hits, 0 crashes (single-source, small N). VI640-stall rate still undetermined: vi-fs-decision lines carry stalled=1 late in every run, needs a phase-gated count, not a raw grep.

- Open owner-level options (not blockers, s5008): (a) declare M5 done, set new target; (c) supply symbol-mapping source for rename sweep. Mission-phase kind=bad voice reads: per-origin budget ALREADY RUN (s4993): 0 bad rows at mission origins vs 2,602 pre-mission, same-run control passed; only open arm is the s4994 mission-origin caller sample, which needs a mission-qualified recipe (s4995 never reached mission).

- s5011: s5010 mission-sample soak route-unevaluable (mission_onset_t=-1; updateHangarBayScene crash). Retry queued as s5012; no conclusion on stale32/cur20.

## s5034 addendum — heap-guard census
s5033 soak: guard2/3/4, r1, coalesce guards fired 0 times on title->hangar->mission (onset 170s), no crash. Single-source (no fire control yet). MIPS toolchain no longer gates heap-guard work. Fire-control env ROGUESQ_FORCE_ALLOC_TAIL_GUARD2 is in fixup_game_funcs_vendored.py but unbuilt.

s5035: guard2 force-control fired (93 lines, 1 site 0x800079AC) on the same route -> s5033 guard2 zero is a valid two-source null (guard is not load-bearing on title->hangar->mission). guard3/4/coalesce/r1 still single-source nulls. Metal toolchain absent: rebuild via scratch/agent/s5034_build.sh (touches shader artifacts, then cmake). Live guard2 patch: tools/apply_s5034_guard2_force.py.

s5036: guard3/guard4 log-only force controls (ROGUESQ_FORCE_ALLOC_TAIL_GUARD3/4) built into 190 live blocks (tools/apply_s5036_guard34_force.py, in RS64_REPLAY); soak `s5036_guard34_force_control` enqueued. r1 guard env has NO generated site (null by construction); coalesce site's `[coalesce-next]` log is its control. Verdict pending -> NEXT.md.
s5036 result: heap-guard census CLOSED. Mission route (onset 174 s, crash=0): guard3 force fired 7752x at 4 drain-mesh sites, coalesce site reached 256x; no guard ever tripped => guards are live-but-silent, not load-bearing there. guard4: 0 passes under force (unreached; shares guard3's generator, no own control = single-source on wiring). r1: no generated site.

## s5037 addendum — copy-primitive guard
memcpy_recomp/bcopy_recomp now carry a host range/length guard (tools/apply_s5037_copy_guard.py; FORCE control env ROGUESQ_COPY_GUARD_FORCE). Census soaks s5037_copy_guard_{default,force} enqueued; verdict pending. Next: consume them (NEXT.md).

## s5038 addendum — copy-guard class closed; message-queue census built
s5037 soaks (mission_onset 170/174s, crash=0, 1.1M lines each): force arm cg=16 (positive control fired), default arm cg=0 => no memcpy/bcopy with wild length or non-RDRAM span on the keyed title->hangar->mission route (two-source, same recipe). Class closed there; other routes unexercised. Next: s5038 log-only message-queue structure census in osSendMesg_recomp/osRecvMesg_recomp (ROGUESQ_MQ_CENSUS, control ROGUESQ_MQ_CENSUS_FORCE); soaks s5038_mq_census_{default,force} enqueued; expect force mq=16, default mq=0 closes the class (osJamMesg has no host wrapper, uncovered).
s5038 result: force mq=16 (control), default mq=0, crash=0 on the keyed route => message-queue structure class closed there (osJamMesg uncovered). Next: use-after-free reads after audited frees.

- s5042: read-after-free poison probe (ROGUESQ_FREE_POISON, tools/apply_s5042_free_poison.py) built; on/off soaks queued, verdicts pending (see NEXT.md).
- s5043: s5042 arms stalled before hangar because the recipe dropped GUARD2 (vs s5037); corrected arms s5043_poison_{off,on}_g2 queued.
- (s5045) s5044 no-census arms stalled nohangar too: FREE_CENSUS refuted; s5045 control rerun of s5037 queued to separate route flake from binary regression (NEXT.md).

- (s5048) s5047 both runs nohangar (keys rc=0, load 4-7); pre-s5038 upstream_compat.cpp rebuild also stalls => mq census/lib hook refuted. Left: host load vs generated-code staleness; next = clean s5037 worktree rebuild (NEXT.md).

## s5046 addendum — keyed route regression (open)
Since s5042, the keyed title->hangar recipe (s5037 default) stalls: after title (phase 4, 1024/0x790400) the game goes to 640/0x696100 screens, never hangar 512/0x6AB400 (working s5037 reached hangar t=91, mission t=174). 6 straight failures (s5042-s5046). Refuted as cause: s5041/s5042 hooks (hook-free rebuild s5046 stalls identically; script tools/revert_s5041_s5042_hooks.py, dropped from RS64_REPLAY), save file (unchanged), poison/census/GUARD2 arms. Open: host load / stopwatch-driven keys vs s5038-s5040 mq census + lib weak hook. All free-poison / census-derived conclusions in s5041-s5045 entries remain valid only for phases up to title. Next: see scratch/agent/NEXT.md.

- s5051: restored-tree rebuild still stalls nohangar under host load 5-7 (Chrome 108% CPU). H1 vs H3 undecided; needs a quiet-host rerun (see scratch/agent/NEXT.md).
- s5057: the 'needs load <2' dependency (s5053) is REFUTED: O0 control and the current binary both reached hangar at load 3.8-4.7 (Chrome 110% CPU). Earlier 0/8 stalls (s5042-s5051) unexplained; treat the recipe as intermittent and measure the flake rate (NEXT.md).
- (s5059) FREE_CENSUS=1 hangar recipe 3/3 pass (t=63-75, load ~4): census does not cause the nohangar stall; 7/7 passes on current binary. Earlier stalls (s5042-s5051) unattributed/transient; resume poison-on-free probe (see NEXT.md).

- s5060: poison-on-free A/B on mission route clean (0 crash, 0 guard, control poisoned>=16384); read-after-free thread closed (single route, 1 run per arm).

## s5061 addendum — PI DMA guard
s5061: do_dma PI range guard CLOSED on keyed route: default pg=0, force pg=16, crash=0 (two-source). Next: do_rom_pio + SP DMA wrappers.
s5064: EEPROM x4 + osContGetReadData guarded via shared rs64_spai_guard_bad; default pg=0 crash=0, FORCE pg=16 (all AI, so per-site reachability of EEPROM/cont is unmeasured; single-source). Next: per-wrapper calls/bad counters.
s5065: per-wrapper census on keyed route (default+FORCE): AI/cont >=16384 calls bad=0, EepromLongRead/LongWrite 2-3 calls bad=0; short EEPROM + StartGo never reached. Host-wrapper pointer guard class closed on this route (single route, 1 run/arm). Next: M5 de-stub step.

- s5069: whole-frame FNV hash (ROGUESQ_FB_HASH=1) is saturated in the mission — 100% distinct frames in ctl and key windows alike; unusable for the reaction question. Next: RDRAM state-witness diff (stable-in-ctl words that move under held W).

- s5074: phase-gated snapshot (ctlA/B/keyW only; 600 s cap hit): 205k witnesses in whole pages, gate does not phase-lock (post-snap origin 0x690400). Snapshot-diff design abandoned; next = in-VI-handler snapshot or read the pad consumer directly.
- s5073: mission snapshot run done (W stick edge confirmed; 175k nominal witnesses but origin-phase confounded; keyD/keyZ not taken). Next: phase-gated re-run, see scratch/agent/NEXT.md.

- s5077: mission flight floats at 0x9DEAC react to stick and coast to static ~3.5 s after release (momentum); static writers 0x800448B0/0x80045540/0x8004562C/0x80045658/0x8004567C; position-vs-scroll unverified. Next: runtime writer attribution (NEXT.md).

- **s5078 (m6-mission-input):** 0x9DEAC is a per-frame lerp/copy of floats 0x80130C54/0x80130C58 written by one function at 0x8004562C/0x80045658 (single-run census, positive control passed; single-source). Hpos refuted. **s5079:** 0x130C54/58 get NO stores in any flight window (setup-time writers only); the lerp parameter is a per-swap accumulator 0x130C40 (writer 0x80019444); stick only picks the arm (single-source, positive control passed). **s5080:** arm selector (0x80045618) reads x=`*(*0x80138D1C+0x50)` (mission object 0x80138458; thresholds 2.0/-8.0, outputs 16.0/24.0); x moves with stick (250 distinct values in W hold, static otherwise). 0x130C40 is NOT its parameter (supersedes s5079 wording). Single-source. **s5081:** 0x80138458 is the player-vehicle effect object; +0x50 is Y of its position vec3, written per frame by updatePlayerVehicleByControlMode/buildEffectObjectWorldTransform and stick-gated by updateEffectObjectOrientationQuat (single run, census positive control passed). m6-mission-input thread CLOSED: stick moves the ship normally; no hidden input path. Link failure after tree restore = stale register_overlays.cpp.o; touch it.


## s5091 note
Pristine-regen discriminator for the s5085 s4296 drop was UNEVALUABLE: s4204-fresh input fails vendored fixup at s4938 (before replay) in both arms. s5090 post-condition remains the guard. Next: M5 audio plan (NEXT.md).
