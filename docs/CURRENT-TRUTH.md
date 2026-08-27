# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable project
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is
authoritative for exact commands and probe rows.

Current maintenance marker: Session 2569 (2026-08-26).

## Current state

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

- **s2560 — the M4 dynamic join endpoints were absent in the qualified route.**
  The corrected regeneration-safe probe reached the title and hangar phases,
  while the independent F5 fetch control fired 514 times. The retail oracle's
  whole-RDRAM control reached 10,000 writes and the same title/hangar phases.
  Neither the overlay-0x1c B00/B02/B04 producer nor the overlay-0x20 0x13D8
  consumer emitted a target-phase row. This does not distinguish producer-dead
  from consumer-dead, and does not select index-alias or index-no-join. The
  next discriminator is route/branch reachability. Artifact:
  `scratch/agent/s2560_m4_index_join/audit.md`.

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

- **s2514 — stage-2/DMA attribution is an observer-contract limitation.**
  Static audit shows `rs64_audio_image_stage` runs before the shared `L_13B0`
  `DO_DMA_WRITE`; the generic DMA observer later reconstructs identity from
  the current route and destination without retaining the stage marker. In
  s2513 ordinal 606, the nonzero pre-write stage row at `0x168B50` had no
  matching DMA event; the only joined event was stage 3 at `0x178D80` with
  zero payload. This does not distinguish missing stage-2 observation from a
  later overwrite. Image-stage and PCM controls were positive; no writer or
  mitigation claim is authorized. Artifact:
  `scratch/agent/s2514_m5_dma_attribution/audit.md`.
- **s2513 — the qualified image capture selects the RSP/image payload writer
  at the observable consumer boundary.** Image ordinal 606 produced stage-2
  output at `0x168B50` with 621 nonzero bytes and FNV `2B9E9631`; an
  independent PCM source/consumer pair used the same address and fingerprint.
  Image, DMA, AI-table, task-join, and PCM controls were positive, with no
  guest CPU writer rows. Exact DMA-event attribution remains open because of
  the observer limitation above. Artifact:
  `scratch/agent/s2513_m5_payload_writer/audit.md`.
- **s2511 — staggered startup separated paired-route failure from the later
  image-arm crash.** Both staggered image arms passed 1024 and reached hangar;
  the paired image arm later crashed in `updateHangarBayScene+76424`, the
  baseline in `do_rom_read+572`, and the silent peer reached its target and
  was killed without a crash marker. This supports startup-order as the
  explanation for the earlier pre-target symptom and refutes concurrent
  resource pressure as sufficient. The later crash writer and exact payload
  writer remain open. Artifact:
  `scratch/agent/s2511_m5_staggered_image_concurrency/audit.md`.
- **s2516 — no Step 3 edge was proven in the title-phase A/B.** The retail
  whole-RDRAM positive control reached 10,000 callbacks. Stub and image arms
  both reached `1024 @ 0x790400`; the image had 1,597-byte DMEM changes,
  `break_pc=0x1328`, and generated DMA, but all observed stage/PCM payloads
  were zero and no output consumer join or legitimate writer was selected.
  This selects no-edge at this route scope; route-only variation remains
  possible against s2513. No behavior change is authorized. Artifact:
  `scratch/agent/s2516_m5_contract_edge/audit.md`.
- **s2517 — a new independent retail task/data boundary still did not name a
  Step 3 edge.** The oracle whole-RDRAM control recorded 359,402 writes and
  reached title and hangar. It retained 1,227 phase-gated type-2 task rows:
  title used `data_ptr=0x80171CE0` / `+0x100=0x171DE0`, hangar used
  `data_ptr=0x80171E70` / `+0x100=0x171F70`, and every row had zero
  output/yield fields. The watched task-data, `+0x100`, and image spans had
  positive writer tables and nonzero snapshots, but no writer was shown to be
  the missing image payload or output consumer. Together with s2516 this
  selects `H-no-edge` at the current route scope; no behavior change is
  authorized. Artifact:
  `scratch/agent/s2517_m5_contract_boundary/audit.md`.
- **s2518 — the first bounded generated-symbol region had no defensible
  mappings.** The complete main-overlay interval `0x8000737C–0x80007908`
  contained four placeholders; the companion symbol file also retains all
  four `fake_func_*` names and no source search produced a human mapping.
  Their bodies are isolated one- or two-instruction fragments. No generated
  code was changed. Artifact:
  `scratch/agent/s2518_symbol_census/audit.md`.
- **s2519 — the second bounded generated-symbol region also had no defensible
  mappings.** The complete main-overlay interval `0x80003424–0x80005568`
  contained `fake_func_80003424`, `fake_func_8000537C`, and
  `fake_func_80005568`. The companion symbol file retains all three fake
  names; source search found no human definition at those exact addresses.
  Nearby DMA functions have distinct named entries, so no alias was inferred.
  This is a single-source/static result and no generated code changed.
  Artifact: `scratch/agent/s2519_symbol_census/audit.md`.
- **s2520 — the third bounded generated-symbol region had no defensible
  mapping.** The complete main-overlay interval `0x80005570–0x8000595C`
  contains one placeholder, `fake_func_8000595C`; its generated body is a
  single `addu v0, zero, zero` fragment between the named DMA cluster and
  `initMemoryPack`. The companion symbol file retains the fake name and a
  source-wide search found no human symbol or m2c definition. No generated
  code changed. Artifact: `scratch/agent/s2520_symbol_census/audit.md`.

- **s2522 — the fifth bounded generated-symbol region had no defensible
  mapping.** The complete interval `0x8006D8FC–0x8006D8FC` contains one
  4-byte placeholder whose body is only `sll v0,v1,2`. The companion symbol
  file retains `fake_func_8006D8FC`, and an exact-address repository search
  found no named definition, caller, or m2c source. This is a static,
  single-source result; no generated code changed. Artifact:
  `scratch/agent/s2522_symbol_census/audit.md`.
- **s2523 — the sixth bounded generated-symbol region had no defensible
  mapping.** The complete interval `0x8006F4AC–0x8006F4AC` contains one
  four-byte placeholder whose generated body is only `addiu sp,sp,0x30`,
  immediately between `getSecondaryWeaponCount` and
  `spawnDestructionDebris`. The companion symbol file retains
  `fake_func_8006F4AC`; an exact-address search found no named definition,
  caller, or m2c source. This is a static, single-source result; no generated
  code changed. Artifact: `scratch/agent/s2523_symbol_census/audit.md`.
- **s2524 — the seventh bounded generated-symbol region had no defensible
  mapping.** The complete interval `0x80072CE8–0x80072CE8` contains one
  8-byte placeholder whose body is only `addiu v1,v1,-0x4160; addu v0,v1,v0`,
  between `walkDatTreeAndScaleLeafByFloat` and `initWaterSprayParticles`.
  The companion symbol file retains `fake_func_80072CE8`, and an exact-address
  repository search found no named definition, caller, or m2c source. This is
  a static, single-source result; no generated code changed. Artifact:
  `scratch/agent/s2524_symbol_census/audit.md`.
- **s2525 — the eighth bounded generated-symbol region had no defensible
  mapping.** The complete interval `0x80079278–0x80079278` contains one
  8-byte placeholder consisting only of a `nop` and `lw a0,0x1C(fp)` before
  the named `heavyMechSubEffectNpcHandler` at `0x80079280`. The companion
  symbol file retains `fake_func_80079278`; exact-address and semantic
  searches found no human definition, m2c implementation, caller attribution,
  or rename candidate. This is a static, single-source result; no generated
  code changed. Artifact: `scratch/agent/s2525_symbol_census/audit.md`.
- **s2526 — the ninth bounded generated-symbol region had no defensible
  mapping.** The complete interval `0x80079CD8–0x80079CD8` contains one
  8-byte placeholder with `lw v1,0x1C(fp); addu v0,v1,v0`, immediately before
  the independently named `setNewAndPreviousButtonsPressed` at `0x80079CE0`.
  The companion symbol file retains the fake name and does not map the
  fragment to the neighboring function; exact-address/source searches found
  no human or m2c candidate. This is a static, single-source result; no
  generated code changed. Artifact:
  `scratch/agent/s2526_symbol_census/audit.md`.
- **s2527 — the tenth bounded generated-symbol region had no defensible
  mapping.** The complete main-overlay interval `0x8007A0E8–0x8007A0E8`
  contains one 8-byte placeholder with `lw v1,0x7C(fp); sh v0,0(v1)`, between
  the delay-slot tail of `getControllerStickYPercentage` and
  `sampleRgbBoxFilter2x2AtSubpixel`. The companion symbol file retains the
  fake name; exact-address search found no human source, m2c definition, or
  caller attribution. This is a static, single-source result and does not
  prove the fragment is dead or permanently unnameable. Artifact:
  `scratch/agent/s2527_symbol_census/audit.md`.
- **s2528 — the eleventh bounded generated-symbol region had no defensible
  mapping.** The complete interval `0x8007A86C–0x8007A86C` contains one
  4-byte placeholder whose body is only `lw a2,0x2B94(a2)`, immediately before
  the independently named `allocateNpcMeshVertexBuffer`. The companion symbol
  file retains `fake_func_8007A86C`; exact-address, source, m2c, and caller
  searches found no human candidate. This is a static, single-source result;
  no generated code changed. Artifact:
  `scratch/agent/s2528_symbol_census/audit.md`.
- **s2529 — the twelfth bounded generated-symbol region had no defensible
  mapping.** The complete 8-byte interval `0x8007C298–0x8007C29C` contains
  `fake_func_8007C298`, whose body is only `sll a1,a2,1; addu a1,a1,a0`.
  The companion symbol table and generated overlay table agree on the fake
  name and span; exact-address, source, m2c, caller, and semantic searches
  found no rename candidate. This is a static, single-source result and does
  not prove whether the fragment is callable or a boundary artifact. Artifact:
  `scratch/agent/s2529_symbol_census/audit.md`.

- **s2530 — the thirteenth bounded generated-symbol region had no
  defensible mapping.** The complete 8-byte interval
  `0x80082268–0x8008226F` contains `fake_func_80082268`, whose body is only
  `lui at,0x8005` followed by `lwc1 f2,-0x2E48(at)`, immediately before the
  independently named `applyCheatCodeFromInput` at `0x80082270`. The
  generated overlay table and companion symbol file agree on the fake name
  and span; exact-address, source, m2c, caller, and semantic searches found
  no rename candidate. This is a static, single-source result and does not
  prove whether the fragment is callable or a boundary artifact. Artifact:
  `scratch/agent/s2530_symbol_census/audit.md`.

- **s2532 — the stale next pointer was revalidated.** The complete 12-byte
  `0x80093E74` epilogue fragment remains `fake_func_80093E74`; companion
  symbols and exact-address/source searches provide no defensible rename.
  An older ledger census had already recorded the same result, so this run
  selects no-match and advances the sweep to `0x80094348`. Artifact:
  `scratch/agent/s2532_symbol_revalidation/audit.md`.

- **s2533 — the next bounded generated-symbol region had no defensible
  mapping.** The complete `0x80094348–0x8009434F` span is an 8-byte `j
  0x80094370`/`nop` fragment immediately before the independently named
  `startSongSequence` at `0x80094350`. The active generated implementation,
  declaration, overlay table, project TOML, companion symbol file, and
  exact-address/source/caller searches provide no human or m2c name. Calling
  it a thunk or alternate entry would be speculative. This selects
  `H-no-match`; no generated code changed. Artifact:
  `scratch/agent/s2533_symbol_census/audit.md`.

- **s2534 — the next bounded generated-symbol region had no defensible
  mapping.** The complete `0x8009711C–0x8009711F` span is a 4-byte jump to
  `0x8009713C`, inside `bindMacroIdsToSoundGroup` at `0x80097130`. The
  companion symbol file retains `fake_func_8009711C`; exact-address, source,
  m2c, and caller searches found no human candidate. Renaming it to either
  neighboring function would alter a boundary representation speculatively.
  This selects `H-no-match`; no generated code changed. Artifact:
  `scratch/agent/s2534_symbol_census/audit.md`.

- **s2535 — the next bounded generated-symbol region had no defensible
  mapping.** The complete `0x80097D58–0x80097D5F` span is an 8-byte epilogue
  fragment (`lw $fp,0x88($sp)` / `addiu $sp,$sp,0x90`) immediately before the
  independently named `clearStreamedVoiceFlags` at `0x80097D60`. The project
  symbol input, generated declaration/implementation/overlay table, and
  companion symbol file retain `fake_func_80097D58`; exact-address/source/m2c/
  caller searches found no human candidate. This selects `H-no-match`; no
  generated code changed. This is a static, single-source result. Artifact:
  `scratch/agent/s2535_symbol_census/audit.md`.

- **s2536 — the M4 indirect vertex-base path is a live static consumer
  candidate.** Overlay 0x1c writes DMEM `B00/B02/B04` entries from pointers
  derived from `0x670`; overlay 0x20's `L_13D8` loads those entries and feeds
  them to `L_17F0`, whose `+0x18/+0x1C` loads consume the producer record
  fields. This closes the prior literal-offset audit's missing alias path at
  static provenance scope, but does not prove a particular table index was
  live in the qualified scene. No runtime or mitigation changed. Artifact:
  [`M4-INDIRECT-ALIAS-AUDIT.md`](M4-INDIRECT-ALIAS-AUDIT.md).

- **s2538 — the next generated-symbol region is a conversion boundary, not a
  rename candidate.** `0x80099FDC–0x80099FDF` is the complete four-byte fake
  span in both symbol inputs. The companion maps place `aspMainTextStart` at
  `0x80099FE0`; the independent ROM check shows the preceding branch at
  `0x09ABDC` and the RSP image beginning at `0x09ABE0`, whose first word
  matches the generated `mfc0` at `0x80099FE0`. The generated fake body has
  therefore absorbed the RSP image stream. No human function mapping exists
  and no generated code changed. Artifact:
  `scratch/agent/s2538_symbol_census/audit.md`.

- **s2531 — two adjacent generated fragments were renamed through the
  regeneration input and generated tables.** `0x80082268` is now
  `cheatCodeConstantPreamble`, an 8-byte constant-load fragment immediately
  before `applyCheatCodeFromInput`; `0x800825C8` is now
  `rspbootTextPreamble`, the 8-byte fragment immediately before the known
  `rspbootTextStart` data. The project symbol TOML, companion symbol source,
  generated declarations, generated implementations, and overlay dispatch
  entries agree. Neither rename asserts that the fragments are independently
  callable game functions.

- **s2539 — retail boundary ranges were active but did not join to M4.** The
  oracle whole-RDRAM positive control reached 10,000 callbacks and the run
  reached title 1024 and hangar 512. Retail writer histograms showed activity
  in `0x166000:0x16A000`, `0x167000:0x169B00`, and `0x179800:0x179B00`, with
  distinct phase-gated writer PCs. The oracle cannot observe RSP DMEM,
  `ACCH:ACCM:ACCL`, or consumer reads, so this selects active-but-unjoined at
  the observed RDRAM boundary and does not close the M4 index/provenance
  question. No mitigation or port instrument was added. Artifact:
  `scratch/agent/s2539_m4_retail_boundary/audit.md`.

- **s2542 — the next generated-symbol region is a boundary fragment, not a
  rename candidate.** `0x800AAADC–0x800AAADF` is the complete four-byte fake
  span containing only `sh $a0,0x1A($v1)`, immediately before the independently
  named `playerSnowSpeederInit` at `0x800AAAE0`. The active generated
  declaration, implementation, overlay table, companion symbol input, and
  exact-address/source/m2c/caller searches provide no defensible human name.
  Renaming it to the neighboring function would absorb a real function
  boundary, so it remains unchanged. This is a static, single-source result.
  Artifact: `scratch/agent/s2542_symbol_census/audit.md`.

- **s2543 — the next generated-symbol region received a bounded semantic
  rename.** The complete `0x800AD378–0x800AD37F` span contains two stores,
  `t1` to `v0+4` and `t2` to `v0+8`, immediately before the independently
  named `computeTrackedObjectWorldAnchor`. No exact companion decomp name,
  m2c definition, or caller attribution exists, so the generated boundary
  was renamed to `storeTrackedObjectAuxiliaryFields` from its complete local
  semantics. The rename is encoded in `tools/rename/build_redefs.py` and
  synchronized into the active symbol input and generated outputs. Artifact:
  `scratch/agent/s2543_symbol_rename/audit.md`.

- **s2544 — the next generated-symbol region is an overlay/boundary fragment,
  not a rename candidate.** `0x800AE3E4–0x800AE3EF` is a complete 12-byte
  generated/project span containing only three floating-point instructions
  (`lwc1`, `lwc1`, `mul.s`) with no callable prologue or return. The mission
  companion input retains `fake_func_800AE3E4`, `initPlayerCraftTrailBuffers`
  follows at `0x800AE3F0`, and the menu overlay independently registers
  `tickEasedCameraKeyframeBlend` at the overlapping `0x800AE3EC`. Exact
  source/m2c/caller searches found no human mapping. This selects
  `H-data-boundary` / `H-no-match`; no generated code changed. Artifact:
  `scratch/agent/s2544_symbol_census/audit.md`.

- **s2545 — the next generated-symbol region is a trap-only data boundary, not
  a rename candidate.** The complete menu-overlay span
  `0x800AEC54–0x800AEC5F` is 12 bytes between
  `hangarUpdateSecWeaponIfChanged` and `initCraftSelectScreen`. The active
  generated body is an explicit trap-only gap filler, while the companion
  symbol input retains `fake_func_800AEC54`; exact source, m2c, and caller
  searches found no human mapping. Renaming it to either neighbor would
  absorb an established function boundary, so it remains unchanged. Artifact:
  `scratch/agent/s2545_symbol_census/audit.md`.

- **s2546 — the next generated-symbol region has no defensible mapping.** The
  complete menu-overlay span `0x800B2628–0x800B262F` is an eight-byte fragment
  containing only `lwc1 f0,-0x5D04(at)` and `swc1 f0,0x168(v0)`, between
  `playExitSoundAndToggleScreenMeshes` and `buildFormatMessageGlyphBuffer`.
  The active generated body/declaration/overlay table and companion symbol
  input retain `fake_func_800B2628`; exact-address, source, m2c, and caller
  searches found no human candidate. It has no complete callable boundary, so
  renaming it is speculative. This static, single-source result selects
  `H-data-boundary` / `H-no-match`; it remains unchanged. Artifact:
  `scratch/agent/s2546_symbol_census/audit.md`.

- **s2547 — the next generated-symbol region received a regeneration-safe
  local rename.** The complete menu-overlay span `0x800B47C4–0x800B47CF` is
  the three-instruction setup immediately before the independently registered
  `menuControllerInput` body at `0x800B47D0`. The companion controller
  decomp's large `func_800B47C4` name therefore cannot be applied directly
  without absorbing the established body boundary. The fragment was named
  `menuControllerInputPreamble` in `tools/rename/build_redefs.py`; the redef
  generator emitted the expected mapping. No generated C or runtime behavior
  changed. Artifact: `scratch/agent/s2547_symbol_rename/audit.md`.

- **s2548 — the next bounded generated-symbol region had no defensible
  mapping.** The complete `0x800C5898–0x800C589F` span is an 8-byte fragment
  containing only `lui at,0x801A` and `addu at,at,a0`, between
  `tickSongAssetLoadWorker` and `menuOverlayInit`. The active generated and
  overlay tables, companion symbol file, prototype-only m2c context, and
  exact-address/source/caller searches provide no human candidate. It remains
  unchanged as a data/boundary artifact candidate. Artifact:
  `scratch/agent/s2548_symbol_census/audit.md`.

- **s2549 — the next bounded generated-symbol region had no defensible
  mapping.** The complete `0x800C6968–0x800C696F` span is an 8-byte fragment
  containing `addu sp,fp,zero` and `lw ra,0x24(sp)`, with no return or complete
  callable body, immediately before `loadJfifAsset`. The active generated and
  overlay tables and companion symbol input retain `fake_func_800C6968`; exact
  address, source, and caller searches found no human candidate. It remains
  unchanged as a data/boundary artifact candidate. Artifact:
  `scratch/agent/s2549_symbol_census/audit.md`.

- **s2550 — the next bounded generated-symbol region is an overlay-shared
  boundary fragment, not a rename candidate.** The complete menu-overlay span
  `0x800CC038–0x800CC03F` contains only `swc1 $f0,0x40($fp)` and
  `addiu $v0,$fp,0x20`. The menu symbol input and generated overlay table retain
  `fake_func_800CC038`, followed by `loadMedalInfo` at `0x800CC040`; the same
  VRAM window is occupied by the mission overlay's independently named
  `initActorFromSpawnTemplate` beginning at `0x800CC03C`. Exact-address,
  companion-source, m2c, and caller searches found no human mapping. Because
  the fragment has no callable boundary and overlaps another overlay's real
  function window, renaming it to either neighbor would be speculative. It
  remains unchanged. Artifact:
  `scratch/agent/s2550_symbol_census/audit.md`.

- **s2551 — the next bounded generated-symbol region is a menu data boundary,
  not a rename candidate.** The complete `0x800CC3D4–0x800CC9B7` span is the
  `0x114C`-byte generated placeholder entry ending exactly before
  `tickAtAtAudioAndWeaponState` at `0x800CC9B8`. Its active generated body is
  only a trap-marked gap filler. The companion menu symbol file retains the
  fake name but declares menu data immediately after it, including hangar
  state/maps, bridge tables/colors, and menu colors; exact-address, source,
  m2c, and caller searches found no human function mapping. This selects
  `H-data-boundary` / `H-no-match`; no generated code changed. Artifact:
  `scratch/agent/s2551_symbol_census/audit.md`.

- **s2552 — the next bounded generated-symbol region is an incomplete mission
  boundary with no defensible mapping.** The complete `0x800CEF1C–0x800CEF1F`
  span is a lone `sw $s1,0x44($sp)` fragment immediately before the complete
  `advanceAtStEffectPhaseSound` at `0x800CEF20`. The active generated
  declaration/body/overlay table and companion symbol input retain
  `fake_func_800CEF1C`; exact-address, source, m2c, and caller searches found
  no human candidate. Borrowing the neighboring function name would be
  speculative, so the placeholder remains unchanged. Artifact:
  `scratch/agent/s2552_symbol_census/audit.md`.

- **s2553 — the next bounded generated-symbol region is an 8-byte mission
  tail-call boundary with no rename candidate.** The complete
  `0x800D2C98–0x800D2C9F` span is `j 0x800D2CA0`/`nop`, immediately before
  the independently named `npcInitWithMotionParams` at `0x800D2CA0`. The
  companion explicitly retains `fake_func_800D2C98` and deletes the duplicate
  `func_800D2CA0` label in favor of `npcInitWithMotionParams`; the active TOML,
  generated overlay table, and exact caller search agree on the 8-byte span.
  This selects `H-data-boundary` / `H-no-match`; no generated code changed.
  Artifact: `scratch/agent/s2553_symbol_census/audit.md`.

- **s2555 — the next bounded generated-symbol region is a 4-byte mission
  boundary fragment with no rename candidate.** The complete
  `0x800E406C–0x800E406F` span contains only `sw $a0,0x20($sp)`, between the
  epilogue of `playDualTextureAttachmentCueMode1` and the prologue of the
  independently named `handleRayShieldedNpcDestroy` at `0x800E4070`. The
  companion symbol input, active TOML, generated declaration/body, and overlay
  registration retain `fake_func_800E406C`; exact-address, source, m2c, and
  caller searches found no human mapping or independent call site. Renaming it
  to either neighbor would absorb an established function boundary. This
  selects `H-data-boundary` / `H-no-match`; no generated code changed. Artifact:
  `scratch/agent/s2555_symbol_census/audit.md`.

- **s2556 — the M4 producer/consumer index remains static-only.** The complete
  generated producer path writes `DMEM[0xB00/B02/B04 + r7]` at
  `0x8002642C–0x80026434`, advances `r7` by six, and supplies 0x670-derived
  pointers. The indirect consumer at `0x80026640–0x8002664C` uses a runtime
  byte loaded through the `0xC70/0xB74` path, masks it with `0x7F`, and loads
  those three table fields. The consumer is real, but generated source does
  not bound its runtime index to a producer slot. This is a static,
  single-source result; no writer or legitimacy claim follows. Artifact:
  [`M4-INDEX-PROVENANCE-REVISIT.md`](M4-INDEX-PROVENANCE-REVISIT.md).

- **s2557 — the next generated-symbol region is a one-instruction boundary
  fragment with no defensible mapping.** The complete
  `0x800E447C–0x800E447F` span is only `lw v1,0x14(v1)`, between the prior
  function epilogue and `resetCraftInstanceMotionState` at `0x800E4480`.
  The active generated declaration/body/overlay table and companion symbol
  input retain `fake_func_800E447C`; the companion explicitly deletes the
  following `func_800E4480` duplicate label, and exact-address/source/caller
  searches found no human candidate. A ROM check was unavailable because the
  expected local ROM file was absent. This selects `H-data-boundary` /
  `H-no-match`; no generated code changed. Artifact:
  `scratch/agent/s2557_symbol_census/audit.md`.

- **s2558 — the next generated-symbol region is an orphan boundary fragment
  with no defensible mapping.** The complete `0x800E71C8–0x800E71CF` span is
  only `lhu v0,0x14(v1)` followed by `lw a0,0x58(fp)`, between the complete
  `npcWaterCraftUpdate` epilogue and `transformCraftAnchorsApplySubFx3`
  prologue. The active generated tables and companion mission symbols retain
  `fake_func_800E71C8`; exact-address, source, m2c, and caller searches found
  no human candidate. This reproduces the earlier boundary classification,
  so renaming it to either neighbor would be speculative. No generated code
  changed. Artifact: `scratch/agent/s2558_symbol_census/audit.md`.

## Active backlog

This is one monotonic sequence; #1 is the next campaign priority.

1. **M5 Step 1 contract checkpoint — image execution is proven, promotion is not.** The direct load boundary,
   SP completion/consumption, image DMEM work, generated DMA, and PCM
   consumer are live under qualified controls. Runtime joins show image
   stage-2 destinations equal generated AI-table entries, but the legitimate
   nonzero payload writer is only selected at the observable consumer
  boundary and exact DMA attribution is still open. Do not map through
  `gspTask`, infer identity from timing or hashes, or change task/output
  fields without a named writer and independent retail evidence. s2516 and
  s2517 found no new legitimate edge; do not add a writeback/remap or repeat
  the unresolved observer. M5 image execution remains opt-in, and later M5
  steps remain conditional on a new named retail writer/value boundary.
  s2559's staged pair adds a positive image execution control but no distinct
  downstream audio edge. Do not promote the image arm or alter task/output
  fields without a newly named contract writer and independent retail
  evidence. The next work unit is the bounded generated-symbol sweep described
  in `scratch/agent/NEXT.md`; M4 remains parked until the sweep is inapplicable.
2. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator; passive recurrence breadcrumbs belong in the
   soak queue.
3. **Hangar visual artifact — parked.** H2 and consumer-mode H1 are refuted;
   H3 is unavailable because the oracle cannot screenshot the LLE path.
4. **Generated-symbol renaming — active bounded sweep.** M5 has no newly named
  contract writer and M3 is parked pending a complete idiom audit, so s2561
  resumed the sweep. The `0x8009C2C8–0x8009C2CF` fragment is unchanged because
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
  left `0x800AEC54–0x800AEC5F` unchanged as a trap-only data boundary; s2546
  left `0x800B2628–0x800B262F` unchanged as an eight-byte data-boundary
  fragment; s2547 renamed the `0x800B47C4` three-instruction setup fragment
  to `menuControllerInputPreamble`; s2548 left `0x800C5898–0x800C589F`
  unchanged as an 8-byte boundary fragment. s2550 left `0x800CC038–0x800CC03F`
  unchanged as an overlay-shared boundary fragment, and s2551 classified
  `0x800CC3D4–0x800CC9B7` as a menu data boundary with no rename candidate;
  s2552 left `0x800CEF1C–0x800CEF1F` unchanged as an incomplete mission
  boundary fragment. s2553 left `0x800D2C98–0x800D2C9F` unchanged as a
  tail-call boundary. s2554 renamed the four duplicate-symbol prefix
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
  boundary; the next unresolved placeholder is `0x8010619C`. s2557 left
  `0x800E447C–0x800E447F` unchanged as a one-instruction boundary fragment
  and advanced to `0x800E71C8`; s2558 revalidated that span as an unchanged
  orphan two-instruction boundary fragment and pivots the next unit to the
  dynamic M4 producer-slot/consumer-index join. s2556 revisited M4 with a
  complete generated producer/consumer index table and found the consumer's
  low-seven-bit index is sourced from runtime state, so the alias remains
  static-only; no runtime or mitigation change was authorized.
5. **M4 accumulator-origin work — dynamic index join remains open.** s2536
   found overlay 0x1c table writers derived from `0x670`; s2556 exhaustively
   identified the overlay-0x20 indirect consumer and its runtime index source,
   but could not bound that index to a producer slot. Do not add a mitigation
   or repeat static literal audits; only a phase-gated producer-slot/consumer-
   index capture can close the remaining dynamic question. s2560's corrected
   capture had positive port and retail controls but zero producer and 0x13D8
   consumer rows, so the next unit must instrument route entry and the
   `r4 == 2` branch as one reachability table; do not infer a dead producer or
   consumer from the current null.

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
