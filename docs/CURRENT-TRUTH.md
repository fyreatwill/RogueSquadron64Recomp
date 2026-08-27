# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable project
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is
authoritative for exact commands and probe rows.

Current maintenance marker: Session 2604 (2026-08-26).

- **s2604 — the next generated-symbol span is a boundary-only fragment.**
  `0x800E71C8–0x800E71CF` contains only `lhu v0, 0x14(v1)` and
  `lw a0, 0x58(fp)` immediately before the complete
  `transformCraftAnchorsApplySubFx3` body at `0x800E71D0`. The companion
  retains `fake_func_800E71C8`; exact-address source, m2c, caller, and
  alternate-name searches found no defensible candidate. The rename generator
  completed with no mapping, so the placeholder remains unchanged. Artifact:
  `scratch/agent/s2604_symbol_census_audit.md`.

- **s2603 — the next generated-symbol span is a duplicate-symbol boundary
  fragment.** `0x800E447C` is the two-instruction fragment `lhu v0, 0x14(v1)`
  / `lw a0, 0x58(fp)` between the complete `handleRayShieldedNpcDestroy` and
  `resetCraftInstanceMotionState` bodies. The companion retains only
  `fake_func_800E447C` and documents deletion of the following duplicate
  symbol; exact-address source, m2c, caller, and alternate-name searches found
  no defensible candidate. The rename generator emitted no mapping, so the
  placeholder remains unchanged. Artifact:
  `scratch/agent/s2603_symbol_census_audit.md`.

- **s2602 — the next generated-symbol span is an unnamed boundary fragment.**
  `0x800E406C` is a single `sw $a0, 0x20($sp)` instruction between the
  complete `playDualTextureAttachmentCueMode1` and `handleRayShieldedNpcDestroy`
  bodies. The companion retains only `fake_func_800E406C`; exact-address
  source/m2c/caller searches found no semantic candidate. The rename generator
  completed with no mapping, so the placeholder remains unchanged. Artifact:
  `scratch/agent/s2602_symbol_census_audit.md`.

- **s2601 — the next generated-symbol span has a companion-defined duplicate
  prefix name.** `0x800DFB8C` is a four-byte prologue (`addiu sp, sp,
  -0x18`) immediately before the complete `applyCraftAnimAndDetailParams`
  body at `0x800DFB90`. The companion assigns the exact address
  `duplicateSymbolPrefixForApplyCraftAnimAndDetailParams` and documents the
  following duplicate-symbol deletion. Exact-address source/m2c/caller and
  alternate-name searches found no competing candidate. Added the
  regeneration-safe mapping to `tools/rename/build_redefs.py`; the generator
  emitted the target redefinition lines. Artifact:
  `scratch/agent/s2601_symbol_census_audit.md`.

- **s2600 — the next generated-symbol span has a companion-defined duplicate
  prefix name.** `0x800DD2C4–0x800DD2CF` is a 12-byte fragment (`nop`,
  `lw v0, 0x74(fp)`, `sw zero, 0x34(v0)`) immediately before the complete
  `npcInitFullModel` body at `0x800DD2D0`. The companion assigns the exact
  address `duplicateSymbolPrefixForNpcInitFullModel` and documents the
  following duplicate-symbol deletion. Added the regeneration-safe mapping
  to `tools/rename/build_redefs.py`; the generator emitted the target
  redefinition lines. Artifact:
  `scratch/agent/s2600_symbol_census_audit.md`.

- **s2599 — the next generated-symbol span has a companion-defined duplicate
  prefix name.** `0x800D4EC4–0x800D4ECF` is a three-instruction fragment
  immediately before the complete `npcInitChildLinkedToParent` body at
  `0x800D4ED0`. The companion assigns the exact address
  `duplicateSymbolPrefixForNpcInitChildLinkedToParent` and documents the
  following duplicate-symbol deletion. Exact-address source/m2c/caller and
  alternate-name searches found no competing candidate. Added the
  regeneration-safe mapping to `tools/rename/build_redefs.py`; the generator
  emitted the target redefinition lines. Artifact:
  `scratch/agent/s2599_symbol_census_audit.md`.

- **s2598 — the next generated-symbol span has a companion-defined duplicate
  prefix name.** `0x800D2C98–0x800D2C9F` is an 8-byte jump veneer into the
  complete `npcInitWithMotionParams` body at `0x800D2CA0`. The companion
  assigns the exact address `duplicateSymbolPrefixForNpcInitWithMotionParams`
  and documents the following duplicate-symbol deletion. Exact-address
  source/m2c/caller searches found no competing name. Added the
  regeneration-safe mapping to `tools/rename/build_redefs.py`; the generator
  emitted all three expected redefinition lines. Artifact:
  `scratch/agent/s2598_symbol_census_audit.md`.

- **s2597 — the next generated-symbol span is a duplicate-symbol boundary
  fragment.** `0x800CEF1C` is the single instruction `sw $s1, 0x44($sp)`
  immediately before the complete `advanceAtStEffectPhaseSound` body at
  `0x800CEF20`. The companion retains `fake_func_800CEF1C` and documents the
  following body as a deleted duplicate-symbol entry. Exact-address source,
  m2c, caller, and alternate-name searches found no defensible candidate; the
  rename generator emitted no mapping. The placeholder remains unchanged.
  Artifact: `scratch/agent/s2597_symbol_census_audit.md`.

- **s2596 — the final menu-overlay placeholder is a boundary-only gap.**
  `0x800CC3D4` follows the complete generated `calculateShotAccuracy` body
  ending at `0x800CC3D0`; the current generated body is trap-only, and the
  next named body starts at `0x800CC9B8`. The companion retains
  `fake_func_800CC3D4` without a semantic name. Exact source/m2c/caller and
  alternate-symbol searches found no candidate; `build_redefs.py` completed
  with no mapping. The placeholder remains unchanged and the sweep moves on
  from the menu-overlay list. Artifact:
  `scratch/agent/s2596_symbol_census_audit.md`.

- **s2595 — the next generated-symbol span is a duplicate-symbol boundary
  fragment.** `0x800CC038` is a one-instruction `swc1 $f0, 0x40($fp)` entry
  immediately before `initActorFromSpawnTemplate` at `0x800CC03C`; the
  following instruction overlaps that next function's entry. The companion
  retains `fake_func_800CC038` and documents no semantic name. Exact-address
  source, m2c, caller, and alternate-symbol searches found no defensible
  candidate. The rename generator emitted no mapping, so the placeholder
  remains unchanged. Artifact:
  `scratch/agent/s2595_symbol_census_audit.md`.

- **s2594 — the next generated-symbol span is a duplicate-symbol boundary
  fragment.** `0x800CA26C` is a one-instruction `lbu v1, 0x11(fp)` stub
  immediately before `initNpcActorVariant` at `0x800CA270`. The companion
  retains `fake_func_800CA26C` and documents deletion of the following
  duplicate `func_800CA270`; exact-address source, m2c, caller, and alternate
  symbol searches found no defensible candidate. The rename generator has no
  mapping, so the placeholder remains unchanged. Artifact:
  `scratch/agent/s2594_symbol_census_audit.md`.

- **s2593 — the next generated-symbol span is a duplicate-symbol boundary
  fragment.** `0x800C7DB4–0x800C7DBF` is the complete three-instruction
  `addiu/addu/sll` fragment immediately before the complete
  `initNpcActorFromSpawnMessage` body at `0x800C7DC0`. The companion retains
  only `fake_func_800C7DB4` and documents the following duplicate-symbol
  deletion; exact-address source, m2c, caller, and alternate-name searches
  found no defensible candidate. The rename generator emitted no mapping, so
  the placeholder remains unchanged. Artifact:
  `scratch/agent/s2593_symbol_census_audit.md`.

- **s2592 — removed an unsupported generated-symbol boundary override.** The
  complete `0x800C64A4–0x800C64AF` span is an epilogue (`lw ra`, `lw fp`,
  stack restore) immediately before `initHangarDisplayItemTimers` at
  `0x800C64B0`. The companion retains `fake_func_800C64A4` and supplies no
  exact-address source or m2c name. An existing explicit generator override
  called it `initHangarDisplayItemTimersPreamble`; that input/generated
  disagreement was removed rather than treating adjacency as proof. The
  placeholder remains unchanged. Artifact:
  `scratch/agent/s2592_symbol_census_audit.md`.

- **s2591 — the next generated-symbol span is an unnamed entry/delay-slot
  boundary fragment.** `0x800C5898–0x800C589F` is the two-instruction
  `lui/addu` fragment immediately before `menuOverlayInit` at `0x800C58A0`;
  the preceding body also renders `0x800C5898` as the delay-slot overlap of
  its `jal`. The companion retains only `fake_func_800C5898`, while m2c has an
  unimplemented three-argument declaration with no body or semantic name.
  Exact-address source, caller, and alias searches found no defensible
  candidate. The rename generator completed with no mapping for the
  placeholder, so it remains unchanged. Artifact:
  `scratch/agent/s2591_symbol_census_audit.md`.

- **s2590 — the next generated-symbol span is an unnamed two-instruction
  boundary fragment.** `0x800B2628–0x800B262F` is the complete pair
  `lwc1 $f0,-0x5D04($at)` / `swc1 $f0,0x168($v0)` between the complete
  `playExitSoundAndToggleScreenMeshes` and `buildFormatMessageGlyphBuffer`
  bodies. The companion explicitly retains `fake_func_800B2628`; exact
  address, source, m2c, caller, and alternate-symbol searches found no
  defensible semantic candidate. The rename generator emitted no mapping for
  it, so the placeholder remains unchanged. Artifact:
  `scratch/agent/s2590_symbol_census_audit.md`.

- **s2589 — the next generated-symbol span is a trap-only data boundary.**
  The complete `0x800AEC54–0x800AEC5F` span is 12 bytes before the real
  `initCraftSelectScreen` at `0x800AEC60`. The generated placeholder contains
  only the fixup `__builtin_trap()`, while the companion explicitly retains
  `fake_func_800AEC54`; exact-address, source, m2c, and caller searches found
  no defensible human candidate. The generator was run successfully with no
  mapping added. This selects `H-BoundaryOnly`; the placeholder remains
  unchanged. Artifact: `scratch/agent/s2589_symbol_census_audit.md`.

- **s2588 — maintenance compaction and a bounded symbol-rename batch.** The
  redundant pre-s2580 evidence archive was collapsed into a ledger pointer,
  reducing this file from 60,145 to 35,509 bytes and from 929 to 558 lines.
  Four companion-defined fragment preambles were added to the regeneration-
  safe rename generator: `npcPredictedRangeCheckPreamble`,
  `initDemoPlayStatePreamble`, `updateHudHealthIndicatorPreamble`, and
  `initHangarDisplayItemTimersPreamble`. The generator emitted all four
  mappings; no runtime experiment or behavior change was run.

- **s2587 — disabling the writer-entry logger did not clear the 640 boundary.**
  The same-build image-arm run reached neither title nor hangar and produced
  zero `[m5-pretgt]`, writer, gate, PCM, or target-phase rows. It aborted in
  the known scene-graph `get_function` path through
  `convertMat3x4ToN64Mtx`/`traverseSceneGraphRecursive`, with last guest PC
  `0x80001F88`. This reproduces s2586's boundary with the new writer-entry
  helper disabled, so that helper is not shown to cause the abort; it remains
  a boundary result, not writer-absence evidence. No M5 behavior or
  mitigation change is authorized. Artifact:
  `scratch/agent/s2587_m5_writer_boundary.log`.

- **s2586 — the new M5 writer call-path census was unevaluable at the target
  boundary.** Regeneration, fixup, and Debug build succeeded, and the helper
  was present for `setDisplayMode`, `reapplyDisplayMode`,
  `shutdownMusyXEngine`, `musyxNoopStub`, and `startSongSequence`. Two
  same-build qualified image-arm attempts reached only boot/640 phases and
  produced 40 audio-task dispatch controls but no title/hangar, writer, gate,
  PCM, or image rows; both aborted at the known scene-graph `get_function`
  path with last guest PC `0x80001F88`. This is not writer evidence and does
  not select any hypothesis or authorize a store/task/gate change. Artifacts:
  `scratch/agent/s2586_m5_writer_callpath.log` and
  `scratch/agent/s2586_m5_writer_callpath_retry.log`.

- **s2585 — the complete port-side M5 writer census leaves the retail-named
  writers absent at runtime.** Static enumeration found seven direct gate
  stores (`0x8008E9F8`, `0x8008EA34`, `0x8008EB40`, `0x8008EB7C`,
  `0x8008EC88`, `0x8008ECEC`, `0x8008ED48`), six fixed channel-byte stores,
  and the indexed `0x80094648` store. The qualified image run passed title and
  hangar plus audio-dispatch and PCM source/consumer controls. Only
  `0x8008EC88` ran in both target phases; neither retail-attributed
  `0x8008ED48` nor `0x80094648` ran, and no PCM guest-writer rows appeared.
  This selects `H-PortWriterUninstrumented`/missing at the current boundary,
  rejecting a reachable matching port writer, but does not identify the
  missing call path or authorize a store/task/output/gate change. Artifact:
  `scratch/agent/s2585_m5_port_writer_census/audit.md`.

- **s2584 — the port-side M5 writer/value correspondence selects
  `H-PortWriterMissing` at the current observable boundary.** The qualified
  image-arm run passed title (`0x00790400 @ 1024`) and hangar
  (`0x006AB400 @ 512`) controls, with 48 audio-task dispatches and 64 image
  runner rows as positive controls. It produced 70 PCM source and 70 consumer
  rows; all sampled 384-sample buffers were zero and every join row had
  `writer_pc=0`, `writer_phys=0`, `writer_writes=0`, and value `0`. No port
  writer row appeared in either phase, so none matched retail's s2583 writers
  (`0x8008ED48` for `0xA0F50`; `0x80094648` for `0x141AD0`). This is two-line
  evidence from the port capture and retail oracle. It identifies an absent
  port-side writer event before the PCM join, but not the responsible store or
  task contract; no mitigation or data rewrite is authorized. Artifact:
  `scratch/agent/s2584_m5_port_writer_value/audit.md`.

- **s2583 — retail writer/value evidence selects `H-RetailWriterMissing` at
  the M5 contract boundary.** The required whole-RDRAM control reached 10,000
  callbacks, and the oracle reached title (`0x00790400 @ 1024`) and hangar
  (`0x006AB400 @ 512`). Retail wrote nonzero values in the candidate ranges:
  `0xA0F50` had writer PC `0x8008ED48` in title and hangar phases with
  post-store `0x01000000`; `0x141AD0` had hangar writer PC `0x80094648` with
  24 phase hits and nonzero values including `0x7F7F7F7F`. `0x1498A` had no
  writes. This rejects `H-RetailLegitZero` and selects
  `H-RetailWriterMissing` at the current observable boundary. It is
  single-source oracle evidence: no task/output/gate/store promotion or
  mitigation is authorized until a port-side comparison maps the writers and
  values. Artifact: `scratch/agent/s2583_m5_retail_writer_value/audit.md`.

- **s2582 — the same-build M5 contract pair selects `H-ContractGap` at the
  current observable boundary.** The retail oracle first passed the required
  whole-RDRAM 10,000-callback control and reached title and hangar. Silent and
  image port arms both reached those phases. The image arm positively produced
  2,922 title and 1,798 hangar image-stage rows plus generated DMA rows; silent
  produced none. Both arms still had zero task output/yield fields and matching
  zero-valued PCM source/consumer samples (title 45/45 each; hangar 47/47
  silent and 43/43 image). No slot/voice/reap rows appeared. This proves the
  image path is live, but not that its output or PCM contract is complete; no
  task/output/gate promotion or mitigation is authorized. The silent arm also
  reproduced the known wild-ROM `do_rom_read` crash; image did not. Artifact:
  `scratch/agent/s2582_m5_step1_contract_pair/audit.md`.

- **s2581 — the first-task boundary is live; the prior s2580 null was an
  observability miss, not an image/host stall.** The required retail oracle
  control produced 10,000 whole-RDRAM callbacks and 461 VI. In the fresh
  image run, all 16 bounded first tasks reached `run-task-enter`, staging,
  image entry, image return (`break_pc=0x1328`, `exit=1`), and SP-task return
  (`ok=1`); the run reached hangar `512 @ 0x006AB400`. The exact task shape
  was type 2, ucode `0x80099FE0`, ucode data `0x800A4E00/0x800`, data size
  1–3, and zero output/yield fields. Existing ABI/return diagnostics added
  1,163 task rows and target-phase returns, supplying an independent second
  line from the new boundary table. `H-ImageLoop` and `H-HostWait` are
  rejected at this boundary; `H-TaskShape` is not a blocker for these tasks.
  This does not authorize any task/output/gate promotion: stage/PCM rows
  remain contract evidence, not proof of correct audio. Artifact:
  `scratch/agent/s2581_m5_image_first_task_stall/audit.md`.

- **s2580 — the M5 Step 1 image/control checkpoint was unevaluable at the
  intended contract boundary.** The retail oracle whole-RDRAM control reached
  10,000 writes plus title and hangar phases, and the silent control reached
  hangar. In the same build, the image arm dispatched the real Factor 5 image
  40 times but produced zero task-ABI, DMEM/DMA, image-stage, audio-return,
  PCM, title, or hangar rows and remained on the boot 320/640 path. A fresh
  90-second image-only retry with in-process autopilot reproduced exactly
  40 dispatches and zero contract rows, with no crash/abort; this rules out
  simultaneous-arm or window-focus orchestration as the blocker. The prior
  H-AudioDegeneracy/H-ContractGap/H-RouteOnly target discriminator therefore
  did not run. Do not promote or mitigate task fields, output pointers, or
  gates from this result. Artifacts:
  `scratch/agent/s2580_m5_step1_contract_pair/driver.log`,
  `scratch/agent/s2580_m5_image_isolated/status`.

- **s2579 — refreshed the M5 design gate against the current dispatcher.**
  `docs/M5-AUDIO-PLAN.md` now inventories the active RSP stubs, Factor 5
  image arm, guest gate/trap classes, wait and drain hatches, scheduler/DMEM
  invariants, AI/SDL bridge, and CPU MORT boundary. It corrects the stale
  policy text: `factor5_ucode_b` is the default `M_AUDTASK` arm and
  `ROGUESQ_AUDIO_UCODE=0` is the silent control. No runtime behavior changed
  and no soak ran. The next unit is the same-build, phase-gated image/control
  contract checkpoint described in `scratch/agent/NEXT.md`.

- **s2578 — the M4 dynamic join is live in the qualified route.** The fixed
  90-second capture had an independent `[ovl-route]` positive control with
  25,164 rows. In phase 6, task 208 entered overlay 0x20 target `0x13D8`;
  256 `r3 >> 6` evaluations included two `r4 == 2` branches. The same
  phase produced 128 producer rows at slot `0x00` and 128 consumer rows at
  index `0x00`, so the observed producer/consumer join is real. This corrects
  s2560's phase-filtered null; it does not prove every slot or scene, and no
  mitigation or data rewrite is authorized. Artifact:
  `scratch/agent/s2578_m4_route_branch/audit.md`.

- **s2577 — the next generated-symbol region is an object-tracking boundary
  with no defensible mapping.** The complete `0x80109618–0x8010961F` span is
  two loads (`lw v0,0x128(fp)` and `lw v1,0xE8(fp)`) immediately before the
  complete `lvj_initializeObjectTracking` function. The companion explicitly
  retains `fake_func_80109618` and identifies the following real function;
  exact-address, source, m2c, caller, and rename-tool searches found no human
  candidate. This is a static, single-source boundary classification, so the
  placeholder remains unchanged. The next unresolved placeholder is
  `0x800AEC54`. Artifact: `scratch/agent/s2577_symbol_census/audit.md`.

- **s2576 — the next generated-symbol region is an objective boundary with no
  defensible mapping.** The complete `0x80109428–0x8010942F` entry is only
  `c.lt.s $f0,$f2` plus its `nop` delay slot, immediately before the complete
  `lvk_checkComplexObjectives` function. The companion explicitly retains
  `fake_func_80109428` and identifies that following function; exact-address,
  source, m2c, caller, and rename-tool searches found no independent human
  candidate. This is a static, single-source boundary classification, so the
  placeholder remains unchanged. Artifact:
  `scratch/agent/s2576_symbol_census/audit.md`.

## Current state

- **s2575 — the next generated-symbol region is an object-tracking boundary
  with no defensible mapping.** The complete `0x80108B8C–0x80108B8F` span is
  one `lwc1 $f0,0x100($v0)` between the complete `lvg_calculateFriendliesSaved`
  and `lvh_initializeObjectTracking` functions. The companion explicitly
  retains `fake_func_80108B8C`; exact-address, source, m2c, caller, and rename-
  tool searches found no human candidate. This is a static, single-source
  boundary classification, so the placeholder remains unchanged. The next
  unresolved placeholder is `0x80109618`. Artifact:
  `scratch/agent/s2575_symbol_census/audit.md`.

- **s2574 — landed six regeneration-safe generated-symbol fragment renames.**
  Companion annotations identify `fake_func_800AAADC`, `fake_func_800B42BC`,
  `fake_func_800B58B4`, `fake_func_800B75C4`, `fake_func_800B89F4`, and
  `fake_func_800BCC38` as fragments immediately preceding the named craft
  initializers `playerSnowSpeederInit`, `playerXwingInit`, `playerAwingInit`,
  `playerYwingInit`, `playerVwingInit`, and `playerT16Init`. Added stable
  `Preamble` mappings to `tools/rename/build_redefs.py` and verified the
  generator emits all six. The unresolved `0x80108B8C` fragment remains
  unchanged because its companion supplies no exact human candidate.

- **s2573 — the next generated-symbol region is an object-tracking boundary
  with no defensible mapping.** The complete `0x80107EA4–0x80107EAF` span is
  a 12-byte sign-extension/float-transfer fragment (`sll`, `sra`, `mtc1`)
  immediately before the complete `lvf_initializeObjectTracking` function.
  The companion explicitly retains `fake_func_80107EA4`; exact-address,
  source, m2c, and caller searches found no human candidate. This is a static,
  single-source boundary classification, so the placeholder remains
  unchanged. Artifact: `scratch/agent/s2573_symbol_census/audit.md`.

- **s2572 — the next generated-symbol region is an object-tracking boundary
  with no defensible mapping.** The complete `0x8010721C–0x8010721F` span is a
  lone `addiu $sp,-0x58` immediately before the complete
  `lvd_initializeObjectTracking` function. The companion explicitly retains
  `fake_func_8010721C`; exact-address, source, m2c, and caller searches found
  no human candidate. This is a static, single-source boundary classification,
  so the placeholder remains unchanged. Artifact:
  `scratch/agent/s2572_symbol_census/audit.md`.

- **s2571 — the next generated-symbol region is a two-instruction
  object-tracking boundary.** The complete `0x80106BE8–0x80106BEF` span is
  `sw $fp,0x10($sp)` / `addu $fp,$sp,$zero`, immediately before the complete
  `lvc_initializeObjectTracking` function. The companion explicitly retains
  `fake_func_80106BE8`; exact-address, source, m2c, and caller searches found
  no independent human candidate. This is a static, single-source boundary
  classification, so the placeholder remains unchanged. Artifact:
  `scratch/agent/s2571_symbol_census/audit.md`.

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The old boot/menu-overlay explanation is closed.
- Qualified route: `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is gated and
  default-off.
- **Reliable in-game input: `ROGUESQ_AUTOPILOT` (2026-08-26).** Synthetic keys
  posted to the window (winctl / PROBE_KEYS) drop when window focus is lost, so
  a "driven" run idles at width 640 with 0 presses seen and the phase gate times
  out — wasted runs, forcing retries (s2506 took 3 attempts). `ROGUESQ_AUTOPILOT=
  "<sec>:<key>,..."` (bare `<sec>`=start; keys start/a/b/z/up/down/left/right;
  times from boot) injects the schedule from INSIDE the input poll
  (`get_n64_input`, main.cpp) — no OS focus, deterministic, every press seen.
  `ROGUESQ_AUTOPILOT_HOLD_MS` (default 150) sets the hold; `ROGUESQ_AUTOPILOT_
  STOP_WIDTH=512` stops all presses once the hangar is reached. VALIDATED 2/2:
  `ROGUESQ_AUTOPILOT="3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a"
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512` drives boot→hangar (origin 0x6AB400) with
  ZERO external input and survives 90s. Prefer this over PROBE_KEYS for any
  hangar/mission run; it also removes the winctl/raise_game focus dependency.
- **Crash pc=0x80001b08 = `recomp::do_rom_read` (pi.cpp:65), a PI-DMA with a
  wild ROM `physical_addr`.** Stack: do_rom_read←do_dma←osPiStartDma←piDmaWorker;
  `rom_addr = rom.data()+physical_addr-rom_base` has no bounds check, so a garbage
  addr walks off the ROM buffer (host SIGSEGV, far≈21GB). TRIGGER: pressing
  Start/A AT the hangar (width 512) starts a mission/asset load into still-stubbed
  code — input-overshoot, so `STOP_WIDTH=512` avoids it (test survived 90s vs
  crash at ~50s). GUARDABLE at do_rom_read: reject `physical_addr-rom_base+
  num_bytes > rom.size()`, drop+log with `ctx->r31` caller. s85/s90 note: one
  specific caller passes a bad `raw_r7`; that caller (root cause) is still open.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation needs a named writer, a
  legitimacy judgment, and an `ORIGIN:` line.
- M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
  silent `M_AUDTASK` `Broke` stub. The image arm performs DMEM work, returns
  `Broke`, emits generated DMA, and can publish PCM. Stock `aspMain` is not
  this game's contract; MORT is a separate CPU speech asset.
- The retail oracle is the independent witness for game-side memory claims.
  Whole-RDRAM, phase, task/status, and named-PC controls must pass before a
  retail null is interpreted. It reaches attract, title, and hangar, not a
  mission.

- **s2570 — the next generated-symbol region is an object-tracking boundary
  with no defensible mapping.** The complete `0x8010619C–0x8010619F` span is a
  lone `lui v1,0x801A` between the complete `lva_checkComplexObjectives` body
  and `lvb_initializeObjectTracking`. The companion explicitly retains
  `fake_func_8010619C`; exact source/m2c/caller searches found no human
  candidate. This is a static, single-source boundary classification, so the
  placeholder remains unchanged. Artifact:
  `scratch/agent/s2570_symbol_census/audit.md`.

- **s2559 — the M5 Step 1 stub/image checkpoint did not authorize promotion.**
  The retail whole-RDRAM control reached its 10,000-write threshold and title
  and hangar VI phases. Staged silent and image arms both reached title and
  hangar without crash or abort markers. The image arm positively executed
  `factor5_ucode_b` (`changed=1597`, `break_pc=0x1328`, and 3 generated DMA
  ranges), while the silent arm had no DMEM change or generated DMA. Both arms
  nevertheless reported PCM source/consumer boundary activity, so this run did
  not isolate a new downstream audio edge attributable to the image arm. This
  selects `H-contract-gap` at the current observable boundary (with
  `H-route-only` still not fully separable from existing shared controls), and
  leaves image dispatch opt-in. No task field, output pointer, gate, or guard
  was changed. Artifact: `scratch/agent/s2559_m5_step1_contract_pair/driver.log`.

- **s2560 — superseded by s2578.** Its target-phase null was caused by the
  probe's title/hangar VI filter; s2578's all-phase bucket observed the route,
  branch, producer, and consumer in phase 6. The original result remains
  useful only as evidence that the old filter was too narrow.

- **s2561 — the next generated-symbol region had no defensible mapping.** The
  complete `0x8009C2C8–0x8009C2CF` span is an eight-byte floating-point
  accumulation fragment (`mul.s` / `add.s`) between the complete named
  functions `stopVoice` and `computeVoicePanCoefficients`. The active
  generated declaration, implementation, overlay table, and project symbol
  input retain `fake_func_8009C2C8`; the companion symbol file and exact
  source/m2c/caller searches provide no human candidate. This is a static,
  single-source boundary classification, not a reachability proof. No
  generated code changed. Artifact:
  `scratch/agent/s2561_symbol_census/audit.md`.

- **s2562 — the next generated-symbol region had no defensible mapping.** The
  complete `0x80101CCC–0x80101CCF` span is a lone `lw a0,0x3C(v0)` between the
  complete `lv1_checkComplexObjectives` epilogue and the real
  `lv2_initializeObjectTracking` prologue. The companion explicitly retains
  `fake_func_80101CCC` and identifies the following real function; exact
  symbol/source/m2c/caller searches found no human candidate. This is a
  static, single-source boundary classification. No generated code changed.

- **s2563 — the next generated-symbol region is an objective boundary with no
  defensible mapping.** The complete `0x80102A98–0x80102A9F` span is an
  8-byte trap-only gap filler between `lv2_calculateFriendliesSaved` and
  `lv3_initializeObjectTracking`. The companion explicitly retains
  `fake_func_80102A98` and identifies the following real function; exact
  address, source, m2c, and caller searches found no human candidate. This is
  a static, single-source boundary classification, so the placeholder remains
  unchanged. Artifact: `scratch/agent/s2563_symbol_census/audit.md`.
  Artifact: `scratch/agent/s2562_symbol_census/audit.md`.

- **s2564 — the next generated-symbol region is an objective boundary with no
  defensible mapping.** The complete `0x8010357C–0x8010357F` span is a lone
  `lwc1 $f2,-0x6C94($at)` between the complete
  `lv3_calculateFriendliesSaved` epilogue and the real
  `lv4_initializeObjectTracking` prologue. The companion explicitly retains
  `fake_func_8010357C`; exact address, source, m2c, and caller searches found
  no human candidate. This is a static, single-source boundary
  classification, so the placeholder remains unchanged. Artifact:
  `scratch/agent/s2564_symbol_census/audit.md`.

- **s2565 — the next generated-symbol region is an objective boundary with no
  defensible mapping.** The complete `0x80103D08–0x80103D0F` span is only a
  two-instruction constant-load fragment (`lui/addiu`) between
  `lv4_calculateFriendliesSaved` and `lv5_initializeObjectTracking`. The
  companion explicitly retains `fake_func_80103D08`; exact-address, source,
  m2c, and caller searches found no human candidate. This is a static,
  single-source boundary classification, so the placeholder remains unchanged.
  Artifact: `scratch/agent/s2565_symbol_census/audit.md`.

- **s2566 — the next generated-symbol region is an objective boundary with no
  defensible mapping.** The complete `0x80104208–0x8010420F` span is two
  instructions (`c.eq.s f0,f2`; `lw v0,0x7CE4(v0)`) between
  `lv5_checkComplexObjectives` and `lv6_checkComplexObjectives`. The companion
  explicitly retains `fake_func_80104208` and identifies
  `lv6_checkComplexObjectives` as the real following function; exact-address,
  source, m2c, and caller searches found no independent human candidate. This
  is a static, single-source boundary classification, so the placeholder
  remains unchanged. Artifact:
  `scratch/agent/s2566_symbol_census/audit.md`.

- **s2567 — landed a regeneration-safe batch of five generated fragment
  renames.** Companion annotations identify `fake_func_8005C61C`,
  `fake_func_8005EE64`, `fake_func_800613B8`, `fake_func_80069AEC`, and
  `fake_func_8006ACA4` as setup fragments immediately preceding named
  functions. Added explicit `build_redefs.py` mappings to stable `Preamble`
  names and verified the generator emits all five mappings. The unresolved
  `0x801044D8` target remains unchanged because its companion entry provides
  no human candidate. This was a source-of-truth tool change; no runtime build
  was needed.

- **s2568 — the next generated-symbol region is an objective boundary with no
  defensible mapping.** The complete `0x801044D8–0x801044DF` span contains
  `sh v1,0x10C(v0)` followed by its delay-slot `addu a0,zero,zero`, between
  `lv6_dispatchStageTick` and `lv7_checkComplexObjectives`. The companion
  explicitly retains `fake_func_801044D8` and identifies the following real
  function; active project/generated tables retain the placeholder, and exact
  address, source, m2c, and caller searches found no human candidate. This is
  a static, single-source boundary classification, so the placeholder remains
  unchanged. Artifact: `scratch/agent/s2568_symbol_census/audit.md`.

- **s2569 — the next generated-symbol region is an object-tracking boundary
  with no defensible mapping.** The complete `0x80105B54–0x80105B5F` span
  contains `addu v1,v1,a0` and two `lwc1` field loads between the complete
  `lv9_calculateFriendliesSaved` and `lva_initializeObjectTracking` bodies.
  The companion explicitly retains `fake_func_80105B54`; exact-address,
  source, m2c, and caller searches found no human candidate. This is a static,
  single-source boundary classification, so the placeholder remains
  unchanged. Artifact: `scratch/agent/s2569_symbol_census/audit.md`.

## Latest evidence

The detailed pre-maintenance evidence remains in `PORTING-STATE.md`; the
current, decision-relevant results are summarized in the session bullets above.
The compact archive below preserves only the conclusions needed to interpret
the active backlog:

- s2513–s2517 established the image/PCM and retail task boundaries but did
  not authorize a task/output remap or mitigation.
- s2518–s2577 advanced the generated-symbol sweep; unresolved boundary
  fragments remain placeholders, while defensible preamble fragments are
  renamed through `tools/rename/build_redefs.py`.
- s2578 established one live M4 producer/consumer join; broader coverage is
  optional and remains lower priority than M5.
- s2579–s2587 left M5 contract-writer qualification blocked by the current
  pre-title scene-graph boundary; no audio gate, store, task field, output
  pointer, or mitigation was promoted.

For exact commands, artifacts, and failed experiments, use the corresponding
session entry in `PORTING-STATE.md`.
## Active backlog

This is one monotonic sequence; #1 is the next campaign priority.

1. **M5 named retail writer/value boundary — blocked at the current qualified
   route boundary.** s2587 reproduced s2586's pre-title/640 scene-graph
   `get_function` abort with writer-entry logging disabled, so the writer
   census cannot be evaluated from this route. Do not treat the absent rows as
   writer evidence or change task/output fields, stores, or gates. The next
   M5 unit must use a genuinely new boundary-qualification angle or execute a
   documented incremental de-stub step; retain `ROGUESQ_AUDIO_UCODE=0` as the
   silent control and rollback.
2. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator; passive recurrence breadcrumbs belong in the
   soak queue.
3. **Hangar visual artifact — parked.** H2 and consumer-mode H1 are refuted;
   H3 is unavailable because the oracle cannot screenshot the LLE path.
4. **Generated-symbol renaming — active bounded sweep.** M5 has no newly named
  contract writer and M3 is parked pending a complete idiom audit, so s2561
  resumed the sweep. s2588 added four regeneration-safe preamble mappings for
  the next companion-defined fragment boundaries. s2593 classified
  `0x800C7DB4–0x800C7DBF` as an unchanged duplicate-symbol boundary fragment;
  the next census is `0x800E8A34`. The `0x8009C2C8–0x8009C2CF` fragment is unchanged because
  its two floating-point instructions form no callable body and no
  companion/source/m2c mapping was found. Continue only with a complete
  bounded span and leave unresolved placeholders unchanged. s2558 revalidated
  `0x800E71C8–0x800E71CF` as an unchanged orphan two-instruction boundary
  fragment. Earlier sweep results remain recorded below. Resume with
  one bounded address-region census and only names supported by the companion
  decomp or clear local semantics; leave unresolved placeholders unchanged.
  s2527 and s2528 left `0x8007A0E8` and `0x8007A86C` unresolved; next is
  `0x8007C298`; s2529 left it unresolved. s2530's `0x80082268` and the
  adjacent `0x800825C8` were renamed in s2531 after their boundaries were
  established. s2532 revalidated `0x80093E74` as an unchanged epilogue
  fragment, and s2533 left `0x80094348` unchanged as a jump fragment; s2534
  left `0x8009711C` unchanged as a jump into `bindMacroIdsToSoundGroup`, and
  s2535 left `0x80097D58` unchanged as an epilogue fragment; s2536's M4
  revisit found the indirect B00/B02/B04 table path is a static 0x670-derived
  consumer candidate; the dynamic table-index join remains open. The sweep
  census at `0x80099C4C` found only a 4-byte `sw s2,0x38(sp)` fragment and no
  defensible human mapping; the placeholder remains. s2538 classified
  `0x80099FDC–0x80099FDF` as the four-byte boundary before `aspMainTextStart`
  and left it unchanged. s2539's retail boundary revisit found active writer
  ranges but no M4 source/consumer join, so no port-side change is authorized.
  s2540 found `0x8009D7CC–0x8009D7CF` is a four-byte `mtc1 $zero,$f4`
  fragment immediately before `filterVoiceSampleBlock`; companion/source/
  caller searches supplied no defensible mapping, so it remains unchanged.
  s2541 found `0x800AA6CC–0x800AA6CF` is a four-byte `lw v0,0x24(fp)` fragment
  immediately before `npcPredictedRangeCheck`; companion/source/m2c/caller
  searches supplied no defensible mapping, and the fragment has no complete
  callable body. It remains unchanged as a data/boundary artifact candidate.
  s2542 left `0x800AAADC` unchanged as a four-byte store/boundary fragment
  before `playerSnowSpeederInit`; s2543 renamed the complete two-store span
  at `0x800AD378` to `storeTrackedObjectAuxiliaryFields`; s2544 left
  `0x800AE3E4–0x800AE3EF` unchanged as an overlay/boundary fragment; s2545
  left `0x800AEC54–0x800AEC5F` unchanged as a trap-only data boundary; s2589
  revalidated that boundary with a complete generated/companion/source audit
  and advanced to `0x800B2628`; s2546
  left `0x800B2628–0x800B262F` unchanged as an eight-byte data-boundary
  fragment; s2547 renamed the `0x800B47C4` three-instruction setup fragment
  to `menuControllerInputPreamble`; s2548 left `0x800C5898–0x800C589F`
  unchanged as an 8-byte boundary fragment. s2550 left `0x800CC038–0x800CC03F`
  unchanged as an overlay-shared boundary fragment, and s2551 classified
  `0x800CC3D4–0x800CC9B7` as a menu data boundary with no rename candidate;
  s2552 left `0x800CEF1C–0x800CEF1F` unchanged as an incomplete mission
  boundary fragment. s2553 left `0x800D2C98–0x800D2C9F` unchanged as a
  tail-call boundary. s2598 restored the regeneration-safe mapping for the
  companion-defined duplicate-symbol prefix at `0x800D2C98`, and s2599 restored
  the matching mapping at `0x800D4EC4`, s2600 restored `0x800DD2C4`, and
  s2601 restored `0x800DFB8C`; the next census is `0x800E406C`.
  s2554 had previously recorded this same family as renamed,
  but the current generated table still carried the placeholder and the
  mapping was absent from the generator, so the current source was repaired.
  s2554 renamed the four duplicate-symbol prefix
  fragments at `0x800D2C98`, `0x800D4EC4`, `0x800DD2C4`, and `0x800DFB8C`
  through the symbol inputs and generated declarations/implementations/
  overlay table. Their names encode the companion-map duplicate-collision
  relationship, not independent game functions. s2555 left
  `0x800E406C–0x800E406F` unchanged as a four-byte boundary fragment; the
  s2563 left `0x80102A98–0x80102A9F` unchanged as an objective boundary;
  s2564 left `0x8010357C–0x8010357F` unchanged as a one-instruction objective
  boundary; s2565 left `0x80103D08–0x80103D0F` unchanged as a two-instruction
  objective boundary; s2566 left `0x80104208–0x8010420F` unchanged as a two-
  instruction objective boundary; s2568 left `0x801044D8–0x801044DF`
  unchanged as a two-instruction objective boundary; s2569 left
  `0x80105B54–0x80105B5F` unchanged as a three-instruction object-tracking
  boundary; s2570 left `0x8010619C–0x8010619F` unchanged as a one-instruction
  object-tracking boundary and advanced to `0x80106BE8`. s2571 left
  `0x80106BE8–0x80106BEF` unchanged as a two-instruction object-tracking
  boundary and advanced to `0x8010721C`. s2572 left
  `0x8010721C–0x8010721F` unchanged as a one-instruction object-tracking
  boundary and advanced to `0x80107EA4`. s2573 left
  `0x80107EA4–0x80107EAF` unchanged as a 12-byte sign-extension/float-transfer
  fragment and advanced to `0x80108B8C`; s2575 left `0x80108B8C–0x80108B8F`
  unchanged as a one-instruction object-tracking boundary and advanced to
  `0x80109428`. s2576 left
  `0x800E447C–0x800E447F` unchanged as a one-instruction boundary fragment
  and advanced to `0x800E71C8`; s2558 revalidated that span as an unchanged
  orphan two-instruction boundary fragment and pivots the next unit to the
  dynamic M4 producer-slot/consumer-index join. s2556 revisited M4 with a
  complete generated producer/consumer index table and found the consumer's
  low-seven-bit index is sourced from runtime state, so the alias remains
  static-only; no runtime or mitigation change was authorized.
5. **M4 accumulator-origin work — observed join established; broader coverage
   remains open.** s2536
   found overlay 0x1c table writers derived from `0x670`; s2556 exhaustively
   identified the overlay-0x20 indirect consumer and its runtime index source,
   but could not bound that index to a producer slot. s2578's phase-6 capture
   observed the route, two `r4 == 2` branches, producer slot `0x00`, and
   consumer index `0x00`, establishing one live dynamic join. Do not add a
   mitigation or data rewrite; broader slot/scene coverage is optional and M5
   now has strategic priority.

## Durable boundaries

### Route, rendering, and Factor 5

The accepted route is `LLE_UNGATED=1, LLE_SOLO=1`; it reaches title and
hangar. Menu spin yield is a diagnostic route aid, not a default behavior
change. Factor 5 mappings and independent controls are in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md).

### M5 audio and image output

Direct service entry/exit, service gate/loop, task/AI boundary, image DMEM
work, generated DMA, reporter association, target-route SP queue consumption,
and PCM consumption are live on the port. The image arm's downstream identity
is not yet a complete legitimate slot, voice, PCM, or output mapping. Retail
proves related ranges and task-field writers, including the second-range
helper/caller relation, but does not prove a port equivalent. Zero-valued rows
are diagnostically ambiguous; no output remap or mitigation is permitted
without a named legitimate writer and an `ORIGIN:` line.

The M4 indirect alias audit adds a static cross-overlay path: overlay 0x1c
writes B00/B02/B04 pointer entries from `0x670`-derived records, and overlay
0x20 can feed those pointers into `L_17F0`. A live table-index join in a
qualified scene remains open.

### VI, M3, and generated symbols

Retail/port VI selector and current-line publication remain unresolved outside
the qualified route. M3 is parked pending a complete idiom audit. Generated
symbol renaming remains parked at the useful boundary.

## Superseded conclusions

These conclusions were believable before qualified routes or independent
controls, but are superseded at their measured scopes:

- The old overlay/menu explanation, intrinsic 640 flakiness, missing input or
  wait-return claims, and unqualified PCM-null claims.
- Clean-stub, canary-poison, final-E50, uniform-gate, host-isolator, and
  global-zero image-DMA explanations.
- The s2190–s2197 and s2283/s2284 second-origin/A1 matrices, s2228,
  s2242–s2259 image/pair crash splits, and s2288 stub-first route conclusion.
- s2304's route-wide PCM gap, s2307's fixed addresses, s2308's zero-fill
  interpretation, s2325's destination-role split, and s2335–s2342's
  inactive-parent/gate labels.
- s2346's output-metadata-writer-absent label and the successive s2347–s2360
  candidate, overflow, value, task-field, and source/payload labels.
- s2376's input-dependent A1 label, s2379's unresolved flag split, s2383's
  missing-completion label, and s2399's identity-cleared label.
- s2445's `H-PortAlternatePath` label and s2446's assumption that
  `0x800078EC` was a callable function target; later boundary inspection and
  live indirect controls superseded them.
- s2493's descriptor-to-load mismatch, s2495's temporal image/load join,
  s2497's image-handoff-absent shorthand, and s2505's static destination
  non-join; later direct port-load and runtime table joins superseded those
  labels at their inspected boundaries.
- s2580's “image arm never reached the contract boundary” label is superseded
  at the first-task boundary. It was believable because every existing
  contract row was target-phase gated and the capture remained in boot/640;
  s2581's all-phase entry/stage/return/SP rows show that the image did run and
  return. The downstream contract gap remains open.

## Evidence and safety rules

- Ask the retail oracle for ground truth before adding an instrument; arm its
  whole-RDRAM positive control first.
- A null requires a same-run positive control. Batch counters and A/B arms in
  one build/run, scope budgets to the phase, and use VI gates rather than
  time. A diagnostic field must be part of a complete discriminating table.
- Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM present.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export submodule patches in the same
  iteration.
- A mitigation is not an explanation: name the writer, state legitimacy, and
  add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Keep the active hypothesis slug while pursuing one thread. After three
  stalled iterations, pivot or block; after six advanced iterations with no
  engineering change, pivot to bounded work.
