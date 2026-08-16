# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable project
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is
the authority for session detail. Reviewed through s1618 (2026-08-16).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu explanation is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Any future mitigation needs an `ORIGIN:` naming the
  writer and assessing legitimacy.
- Phase-gated port captures reach VI width 1024 with independent
  emit/raw/dispatch/match controls. Late E9 producer/consumer identity is
  established; remaining deltas are boundary/span-shaped and unclassified.
- The recurring `slotDispatcherIter+872` SIGBUS is the generated prologue
  spill of guest `$sp` at `funcs_8.c:22810`. Complete static audits of callers,
  indirect targets, context ownership, stack/dynamic-copy/store/load idioms,
  and partial loads found no reachable frame-overlapping writer. Runtime
  guest memory/value corruption remains open; no mitigation is justified.
- The corrected `npcPowerGeneratorUpdate` boundary is main `.text` at
  `0x80077AF0`; regenerated ELF, N64Recomp output, fixups, and Debug target
  pass. Runtime boundary tests remain pre-1024 and unevaluable.
- The complete `do_sdl`/`do_sdr` census found five emitted calls; all are
  malformed/data-like or in a malformed oversized generated body. No reachable
  target-path writer or frame-overlapping span was established.
- M5 audio de-stubbing is closed. Audio remains stubbed. Prior retail watches
  that stayed at VI 320 used dummy video and never reached the identified
  `musyxInitVoiceFromSample` writers. Do not reopen without a new bounded plan
  that uses the Rice hangar recipe below.
- Retail oracle whole-RDRAM, scheduled PIF, and VI controls are healthy.
  Dummy video (`ProcessDList` no-op) stays at width 320 / origin
  `0x006dd280`. Homebrew Rice (`--video …/mupen64plus/mupen64plus-video-rice.dylib`)
  with the eleven-Start schedule is the available later-phase recipe:
  320→640 at ~2.3s, 640→1024 at ~17.2s, 1024→512 hangar origin
  `0x006ab400`/`0x006ab800` at ~38.4s (s707 and s1496). After hangar, extra
  Start or A leaves to 640 / `0x006a2900`/`0x006a2e00` (s1528); the
  eleven-Start hold arm stays at hangar through 100s. s1544: that 640
  phase is still menu-overlay (last `loadOverlay` is menu path
  `0x80000BA8` at 16.9s; mission path `0x80000B70` and `lv0`/`lv1`
  inits stay 0) and is not a cinematic reload (`cinematicLoopBody`
  only at boot 6.9s). s1569: the 640 handler is `menuOverlayInit`
  case 6 `runModelViewerLoop` (`0x800C9BF0`) after hangar returns
  nonzero and `getPlanetAssetForLevel` is not `0xFF`. Hold keeps
  `runHangarSelectionFrame` through 100s at 512; leave A stops that
  inner loop at 63.7s, then `gracefulMenuShutdown` / selector=6 /
  `runModelViewerLoop`+`initModelViewer`+`buildModelViewerTextPage`+
  `loadJfifAsset`. Extra Start during 640 does not exit it. This is
  the planet / text-crawl viewer (the product LEVEL DESCRIPTION
  after AVAILABLE CRAFT), not a mission. Do not add target watches
  on a dummy-video arm. Glide64MK2 stayed at 320 in s707.
- s1616's Rice pre-exit B arm is a distinct valid route: B was delivered
  (`sym=224`, pad word `0x400000`) while the hangar-frame control was live,
  then VI changed 512→1024 at `0x00790400` and later 1024→640 at
  `0x00696100`. It executed no `runModelViewerLoop` and no mission-entry
  path (`0x80000B70`), so B does not solve mission entry but does refute the
  claim that every hangar exit follows the case-6 viewer. A control and the
  two directional arms followed the known 512→640 viewer route; the
  directional arms logged `sym=0` rather than a valid mapped input and are
  unevaluable for navigation. The selector watch `0x13B40:0x13B48` stayed
  quiet in all four arms. This is retail-oracle evidence; the generated
  B-mask branch at `0x800AB0F4` is an independent static
  control at `0x800AB0F4`, not a second retail execution witness.
- The port VI 640-to-1024 lifecycle is generated state plus host VI submission.
  `applyPendingViChanges` can change selector bytes
  `0x8011A862/0x8011A864/0x8011A865`; a direct `osViSetMode` edge can submit
  `0x80128DF0` without entering the selector consumer. Host logging agrees
  with generated and committed VI state. The active boot descriptor selects
  the index-0 320 record.
- M4 shade-lane/order is not the cause. Port VMADH modeling and an independent
  control matched all 128 lanes; VGE changed 0/128 (s1135). The s1135 remainder
  that retail CPU-owns the captured record at physical `0x688..0x710` is
  rejected (s1512): Rice reached hangar 512/`0x006ab400` with the whole-RDRAM
  control passing, and both `0x688:0x710` and SP-DMEM `0x04000670:0x04000720`
  had zero CPU writes. Generated `ori $9, $zero, 0x670` plus the only
  `SP_WR_LEN` DMA from DMEM `0xD60` independently identify `r9` as DMEM.
  s1602's new phase-6 paired capture matched the local VMADH model on all 32
  target lanes and showed no VGE change. This is a single-source local
  consistency result, not an independent retail arithmetic proof; the
  unresolved issue is source state or the later DMA/consumer boundary. The
  retail watch at the port's runtime-allocated `0x4B7800` candidate was
  quiet, but port/oracle scene origins and allocation state differ, so that
  null is single-source and not a retail source-state conclusion.

## Active investigation and ranked next steps

1. Continue the generated-symbol renaming sweep (~1,548 placeholder
   `func_0x...` names remained when counted at s1487; no other stated
   finish line — see `tools/agent/ITERATION.md` strategic-priority item 4
   for the mandatory every-15-sessions revisit of the retail-entry-boundary
   and M4 threads; s1569 was that revisit). One bounded exact-name census
   per session over the next adjacent function. Synchronize only names
   independently supported by the companion project, generated definitions,
   sizes, and caller/semantic evidence. Per-session H1 syncs through s1594
   live in `PORTING-STATE.md` and are archived in
   `PROJECT-OVERVIEW.md` §33; do not re-list them here.

   s1572 synchronized `playWeaponFireSound` at `0x800B4588` (size
   `0x738`): the companion mission list, generated `funcs_31.c`, TOML
   boundary, and a generated caller agree. s1573 synchronized
   `playXwingEngineSound` at `0x800B4F54` (size `0x4E0`): the companion
   mission list, generated definition and caller, and TOML boundary agree.
   s1574 synchronized `isWeaponSlotReady` at `0x800B585C` (size `0x58`):
   the companion mission list, generated definition and callers, and TOML
   boundary agree; the intervening `fake_func_800B58B4` and
   `playerAwingInit` boundary also match. The next census is
   `func_800B63C8`, independently named `acquireLockOnTarget`.
   Synchronize only if the complete comparison remains exact. This naming
   census does not reopen closed M5 audio de-stubbing.

   s1575 synchronized `resetEngineTrailQuads` at `0x800B5B4C` (size
   `0x87C`): the companion mission list, generated definition and caller,
   exact generated boundary, and TOML size agree. The next census was
   `func_800B63C8`, independently named `acquireLockOnTarget`.

   s1576 synchronized `acquireLockOnTarget` at `0x800B63C8` (size `0x3D8`):
   the companion mission list, generated definition and two generated callers,
   exact next-function boundary, and TOML size agree. The next census is
   `func_800B67A0`, independently named `emitTexturedImpactEffect`.

   s1577 synchronized `emitTexturedImpactEffect` at `0x800B67A0` (size
   `0x1F0`): the companion mission list, generated definition and three
   generated callers, exact next-function boundary, and TOML size agree. The
   next census was `func_800B6990`, independently named
   `updateEngineThrustEffect`.

   s1578 synchronized `updateEngineThrustEffect` at `0x800B6990` (size
   `0x7D8`): the companion mission list, generated definition and caller from
   `playerAwingUpdate`, exact next-function boundary, and TOML size agree.
   s1579 synchronized `findLockOnTarget` at `0x800B7590` (size `0x34`): the
   companion mission list, generated definition and three generated callers,
   exact next-function boundary, and TOML size agree. s1580 synchronized
   `tickCraftAbilityCooldown` at `0x800B77D0` (size `0x27C`): the companion
   mission list, generated definition and caller, exact next-function
   boundary, and TOML size agree. s1581 synchronized
   `orientEffectToVelocity` at `0x800B7A4C` (size `0x3B0`): the companion
   mission list, generated definition and caller, exact next-function
   boundary, and TOML size agree. s1582 synchronized
   `spawnTexturedExplosionBurst` at `0x800B7DFC` (size `0x68C`): the
   companion mission list, generated definition, `playerYwingUpdate` caller,
   exact next-function boundary, and TOML size agree. s1583 synchronized
   `emitTexturedEffectCue` at `0x800B88C8` (size `0x12C`): the companion
   mission list, generated definition, exact `fake_func_800B89F4` boundary,
   and TOML size agree; the generated body's texture lookup/cue-dispatch
   behavior supplies semantic evidence. s1584 synchronized
   `updateVwingEngineEffect` at `0x800B8C30` (size `0x9B0`): the companion
   mission list, generated definition, `playerVwingUpdate` caller, exact
   `orientVwingSubmodelByQuat` boundary, overlay-table span, and TOML size
   agree. The next census is `func_800B95E0`, independently named
   `orientVwingSubmodelByQuat`, with size `0x370`.

   s1585's mandatory retail-entry revisit ran four Rice arms against the
   640 `runModelViewerLoop` phase: no post-gate input, A, B, and Z. Every arm
   passed whole-RDRAM and PIF/controller controls and reached the same
   320→640→1024→512→640 lifecycle. After the 640 gate, all had zero mission
   path `0x80000B70`, identical menu/cinematic PC counts, one case-6 viewer
   hit, and no candidate-specific write in `0x130B10:0x130B58`. This selects
   H3 for the tested buttons: none exits the viewer in the observed interval.
   The retail-entry question remains open for a different input or state
   condition; do not repeat these A/B/Z arms.

   s1586 synchronized `orientVwingSubmodelByQuat` at `0x800B95E0` (size
   `0x370`): the companion mission list, generated definition and three
   generated callers, exact next-function boundary, overlay-table span, and
   TOML size agree. The next census is `func_800B9950`, independently named
   `tickVwingEngineAudio`, with size `0x5FC`.

   s1587 synchronized `tickVwingEngineAudio` at `0x800B9950` (size `0x5FC`):
   the companion mission list, generated definition and caller from
   `playerVwingUpdate`, exact `playerVwingUpdate` boundary, overlay-table span,
   and TOML size agree. The next census is `func_800BA620`, independently named
   `computeFalconFlightTransform`.

   s1588 synchronized `computeFalconFlightTransform` at `0x800BA620` (size
   `0x3E0`): the companion mission list, generated definition and caller from
   `playerFalconMainUpdate`, exact `triggerFalconEngineEffect` boundary,
   overlay-table span, and TOML size agree. The next census is
   `func_800BAA00`, independently named `triggerFalconEngineEffect`, with size
   `0x170`.

   s1589 synchronized `triggerFalconEngineEffect` at `0x800BAA00` (size
   `0x170`): the companion mission list, generated definition and caller from
   `spawnFalconEngineParticles`, exact `bindFalconSubmodelMaterials` boundary,
   overlay-table span, and TOML size agree. s1590 synchronized
   `bindFalconSubmodelMaterials` at `0x800BAB70` (size `0x25C`): the companion
   mission list, generated definition and caller from
   `computeFalconFlightTransform`, exact `playerFalconMainUpdate` boundary,
   overlay-table span, and TOML size agree. The next census is
   `func_800BB608`, independently named `spawnFalconEngineParticles`, with
   size `0x228`.

   s1591 synchronized `playerFalconMainUpdate` at `0x800BADCC` (size `0x83C`):
   the companion mission list, generated definition and caller from
   `spawnFalconEngineParticles`, exact `spawnFalconEngineParticles` boundary,
   overlay-table span, and TOML size agree. s1592 synchronized
   `spawnFalconEngineParticles` at `0x800BB608` (size `0x228`): the companion
   mission list, generated definition, `playerFalconUpdate` caller at
   `0x800BBB14`, exact `playerFalconUpdate` boundary, overlay-table span, and
   TOML size agree. s1593 synchronized `integrateFalconFlightPhysics` at
   `0x800BBC58` (size `0xD8`): the companion mission list, generated
   definition and floating-point clamp/integration body, exact
   `playerTieInterceptorInit` boundary, overlay-table span, and TOML size
   agree. s1594 synchronized `computeTieInterceptorTransform` at
   `0x800BBF6C` (size `0x324`): the companion mission list, generated
   definition, generated caller at `0x800BCAE8`, exact
   `triggerTieInterceptorEffect` boundary, overlay-table span, and TOML size
   agree. s1595 synchronized `triggerTieInterceptorEffect` at `0x800BC290`
   (size `0x268`): the companion mission list, generated definition and six
   generated callers from `playerTieInterceptorUpdate`, exact
   `computeTieInterceptorOrientation` boundary, overlay-table span, and TOML
   size agree. The next census is `func_800BC4F8`, independently named
   `computeTieInterceptorOrientation`, with size `0x318`. s1596 synchronized
   `computeTieInterceptorOrientation` at `0x800BC4F8` (size `0x318`): the
   companion mission list, generated definition and caller from
   `playerTieInterceptorUpdate`, exact `playerTieInterceptorUpdate` boundary,
   overlay-table span, and TOML size agree. s1597 synchronized
   `computeT16Transform` at `0x800BCE74` (size `0x3E0`): the companion mission
   list, generated definition and `playerT16Update` caller, exact
   `playerT16MainUpdate` boundary, overlay-table span, and TOML size agree.
   s1598 synchronized `playerT16MainUpdate` at `0x800BD254` (size `0x2DC`):
   the companion mission list, generated definition and `playerT16Update`
   caller at `0x800BD814`, exact `playerT16Update` boundary, overlay-table
   span, and TOML size agree. The next census is `func_800BD958`,
   independently named `triggerT16Effect`, with size `0xF8`.

   s1599 synchronized `triggerT16Effect` at `0x800BD958` (size `0xF8`): the
   companion mission list, generated definition and effect/sound dispatch
   body, exact `playerNabooStarfighterInit` boundary, overlay-table span, and
   TOML size agree. s1600 synchronized `buildNabooSubmodelTransform` at
   `0x800BDC9C` (size `0x58C`): the companion mission list, generated
   definition and caller, exact `triggerNabooEngineEffect` boundary,
   overlay-table span, and TOML size agree. The next census is
   `func_800BE228`, independently named `triggerNabooEngineEffect`, with size
   `0x280`. s1601 synchronized `triggerNabooEngineEffect` at `0x800BE228`
   (size `0x280`): the companion mission list, generated definition, three
   generated callers, exact `tickPlayerCraftBlinkIndicator` boundary,
   overlay-table span, and TOML size agree. s1602's M4 revisit did not alter
   the sweep ordering. s1603 synchronized `tickPlayerCraftBlinkIndicator`
   at `0x800BE4A8` (size `0x328`): the companion mission list, generated
   definition and `playerNabooStarfighterUpdate` caller, exact next-function
   boundary, overlay-table span, and TOML size agree. s1604 synchronized
   `initDemoPlayState` at `0x800BEC00` (size `0xDC`): the companion mission
   list, generated definition and `loadAndStartDemo` caller, exact
   `applyDemoRecordedHudEvents` boundary, overlay-table span, and TOML size
   agree. s1605 synchronized `applyDemoRecordedHudEvents` at `0x800BECDC`
   (size `0x13C`): the companion mission list, generated definition and
   demo-HUD state-update body, exact `clearPlayerSlotHudTracking` boundary,
   overlay-table span, and TOML size agree. s1606 synchronized
   `clearPlayerSlotHudTracking` at `0x800BEE18` (size `0x94`): the companion
   mission list, generated definition and `initAllPlayersHudTracking` caller,
   exact `initAllPlayersHudTracking` boundary, overlay-table span, and TOML
   size agree. s1607 synchronized `tickPlayerHudIndicators` at `0x800BEFBC`
   (size `0x2A8`): the companion mission list, generated definition in the
   mission overlay file, generated `funcs_42.c` caller, exact
   `loadPlayerSlotHudPreset` boundary, overlay-table span, and TOML size
   agree. s1608 synchronized `loadPlayerSlotHudPreset` at `0x800BF264`
   (size `0x90`): the companion mission mapping, generated definition and
   HUD-preset copy semantics, exact `countTrailingZeros16` boundary,
   overlay-table span, and TOML size agree. s1609 synchronized
   `countTrailingZeros16` at `0x800BF2F4` (size `0x64`): the companion
   mission mapping, generated definition and 15 generated call sites across
   two generated files, exact `applyResModeFromSettings` boundary,
   overlay-table span, and TOML size agree. s1610 synchronized
   `applyResModeFromSettings` at `0x800BF358` (size `0x4C`): the companion
   mission mapping, generated flag-propagation body and caller, exact
   `restoreGameSettingsAfterDemo` boundary, overlay-table span, and TOML
   size agree. s1611 synchronized `restoreGameSettingsAfterDemo` at
   `0x800BF3A4` (size `0x64`): the companion mission mapping, generated
   restore-body semantics, generated caller, exact previous and next
   function boundaries, overlay-table span, and TOML size agree. The next
   census is `func_800BF408`, independently named `loadAndStartDemo`, with
   size `0x60`. s1612 synchronized `loadAndStartDemo` at `0x800BF408` (size
   `0x60`): the companion mission mapping, generated definition and demo
   asset/init/flag-setting body, generated caller, exact previous and next
   function boundaries, overlay-table span, and TOML size agree. The next
   census is `func_800BF468`, independently named `getDemoRecordedTimestep`,
   with size `0x30`. s1613 synchronized `getDemoRecordedTimestep` at
   `0x800BF468` (size `0x30`): the companion mission mapping, generated
   timestep-lookup body and caller, exact previous and next boundaries,
   overlay-table span, and TOML size agree. s1614 confirmed that the next
   entry, `fake_func_800BF498` (size `0x8`), is an explicitly fake fragment;
   `fake_func_800BF498` (size `0x8`), is an explicitly fake fragment. s1615
   likewise confirmed `fake_func_800BF784` (size `0xC`) as an explicit fake
   fragment; the next census is `func_800BF790` with size `0x634`. s1617
   classified `func_800BF790` at `0x800BF790` (size `0x634`) as H3: its live
   generated body calls `getPlayerHealthPercentage` and updates HUD health
   fields, and the generated/TOML/section-4 overlay span is exact from
   `fake_func_800BF784` through `func_800BFDC4`; however, the companion
   `mission_overlay.txt` deliberately leaves this mission entry address-coded
   while `main_overlay.txt` carries `updateHudHealthIndicator` at the same
   VRAM address. That is an overlay-context conflict, not an independently
   validated mission name, so no rename was made. s1618 classified
   `func_800C41B0` at `0x800C41B0` (size `0x1AC`) as H3: its live generated
   radar-blip body, exact `fake_func_800C41AC` predecessor and
   `plotRadarBlipRow` successor boundaries, TOML size, and mission overlay
   span all agree, but the only independent name at that address is
   `plotRadarBlipColumn` in `main_overlay.txt`; the mission mapping remains
   address-coded. The overlay-context conflict leaves the name unvalidated,
   so no rename was made. The next census is `func_800C435C` with size
   `0x174`.

   Leave these parked entries unchanged:
   - `func_8008ED6C` address-encoded (s1309 H2)
   - `func_800927B0` address-encoded (s1355 H3)
   - `func_80092A54` address-encoded (s1357 H3)
   - `func_80092CF0` address-encoded (s1359 H3: no independent companion name)
   - `func_80092F10` address-encoded (s1360: TOML-only live-tail fragment of
     `resampleVoiceLutSamplesPacked`)
   - `fake_func_80093E74` (s1369: already-fake three-instruction epilogue)
   - `fake_func_80094348` (s1378: already-fake two-instruction jump before
     `startSongSequence`)
   - `fake_func_8009711C` (s1408: already-fake one-instruction jump before
     `resetSongSubsystemCounter`)
   - `fake_func_80097D58` (s1420: already-fake two-instruction epilogue before
     `clearStreamedVoiceFlags`)
   - `fake_func_80099C4C` (s1446 H2: already-fake one-word `beq` gap before
     `transformVec3ByAffineMatrix`)
   - `fake_func_80099FDC` (s1451 H2: already-fake one-word `bne` gap before
     `aspMainTextStart` at `0x80099FE0`; overlay `0xF84` is the misparsed
     RSP text lump, not a CPU function)
   - `fake_func_8009C2C8` (s1471 H2: already-fake two-instruction COP1
     multiply-accumulate fragment before `computeVoicePanCoefficients`)
   - `fake_func_8009D7CC` (s1476 H2: already-fake one-instruction
     `mtc1 $zero, $f4` fragment before `filterVoiceSampleBlock`)
   - `func_8009D8BC` (s1477: eight-byte PC-relative packed-nibble table
     `C7 D7 E3 E7 F1 F3 F5 F7`, not a function)
   - `func_8009D978` (s1478: eight-byte PC-relative Q15 delay-mix table
     `0CCD 2CCD 5333 7FFF`, not a function)
   - `fake_func_800AF6A8` (s1546 H2: already-fake cinematic overlay data-tail
     gap-filler; generated `__builtin_trap()`; companion Fake Function
     Fixing; next ROM word `0x0C03A807` is a `jal`, not a prologue)
   - `fake_func_800B42BC` (s1570 H2: already-fake one-instruction
     `lw $v0, 0x2C($fp)` gap before `playerXwingInit`; companion Fake
     Function Fixing; zero jal/j/ptr; menu `destroyPlayerShipRecord`
     occupies the same VRAM from `.ovl.menu`)
   - `fake_func_800BF498` (s1614 H1: companion, generated C, TOML, and
     overlay table agree on the explicit 8-byte `lw`/`sw` frame fragment;
     `attached3DSoundEmitterNpcHandler` begins at `0x800BF4A0`)
   - `fake_func_800BF784` (s1615 H1: companion, generated C, TOML, and
     overlay table agree on the explicit 12-byte three-instruction fragment;
     `func_800BF790` begins at the exact next boundary)

2. Future oracle work on leaving the 640 crawl into a mission, or a
   new M4 RDRAM dest (a DMEM→RDRAM transfer that is not `0xD60`),
   must use the Rice `--video` recipe above, not dummy video. s1544
   closed mission/cinematic/hangar-tick identity; s1569 named the
   handler `runModelViewerLoop` (two lines: generated case-6
   dispatch plus Rice PC watches). Extra Start during 640 does not
   exit the crawl. s1616 shows that pre-exit B selects a distinct
   512→1024→640 route with no case-6 or mission PC, while A selects
   case 6; the B route is not yet identified as a mission. The remaining
   retail-entry question is which input or timeout leaves case 6 into a
   mission overlay, and what the B-selected 640 route represents. Pass
   whole-RDRAM, PIF, and VI positive controls in the same run. Do
   not re-watch `0x688:0x710`, do not re-audit dummy-video 320-only
   schedules, and do not treat 640/`0x6a2900` as an outdoor mission.
3. Keep audio closed unless a new independent lead reaches audio initialization
   or voice allocation; then write a new bounded plan before changing stubs.
4. Revisit M3 only as a complete idiom-class audit with a named discriminator;
   do not chase recurring single-crash breadcrumbs reactively.
5. For any runtime probe, read `tools/oracle/README.md` and
   `docs/F5-UCODE-REFERENCE.md`, batch all arms in one build/run, and phase-gate
   animated comparisons on VI transitions.

## Durable boundaries

### M3 dispatcher/frame origin

The s1162 census found 144 direct `slotDispatcherIter` calls in 72 generated
callers; caller entries, stack pairs, and saved-`$ra` contracts match. No
static indirect target to `0x8003E8DC` exists. Runtime context ownership has
one executable `r29` initializer in `run_thread_function` and no alternate
context handoff.

Completed writer/load classes selected H3 with no mitigation: stack-relative
stores, `r29` assignments, dynamic copy/DMA/controller/flash, `SD`,
`do_swl`/`do_swr`, narrow stores, `MEM_W`/`MEM_WU`, `MEM_D`/`LD`,
`do_ldl`/`do_ldr`, `do_lwl`/`do_lwr`, and `do_sdl`/`do_sdr`. The 418-call
`do_lwl`/`do_lwr` census found no saved-frame overlap; malformed tails are
data-like. The next M3 class is not justified without a new discriminator.

### VI descriptor boundary

`osTvType=1` feeds `rsViModeType=0`; boot selector bytes are `A/B/C=1/0/0`.
`initVideoSubsystem` copies records to `0x00/0x50/0xA0/0xF0`, and the active
selector chooses `base+0xF0` (`0x80128E40`), the 320 descriptor.
`osViSetMode_recomp` forwards `ctx->r4` unchanged; the host does not rewrite
width. This boundary is independently established.

### M4 accumulator boundary

Factor 5 reference data and paired combiner evidence refute an RT64 shade
ordering explanation. VTXCOLOR is nonzero while decoded shade is the fixed
`0xFFFF8000`/`0x00008000` sentinel. Port VMADH matched all 128 captured
lanes; VGE mutated none. Physical `0x688..0x710` is not a retail CPU-written
shade record (s1512 Rice hangar, two-line: quiet CPU watches plus generated
DMEM `r9`). s1602 captured four phase-6 target rows (32 lanes): every
post-VMADH lane matched the exact `rsp_vu_impl.hpp` accumulator model, and
post-VGE values were unchanged. This is a single-source local consistency
result: no VMADH/VGE mismatch was observed in that capture. The unresolved
boundary is source state or later DMA/consumer identity, not RT64 lane order
or low-RDRAM ownership. The port's live DMA control identified
`0x4B7800..0x4B7808` as a runtime destination for one phase-6 transfer, but
the retail oracle's whole-RDRAM-positive run reached the 512 hangar with zero
writes there; differing allocator/scene origins make that targeted null
single-source and unevaluable as a retail ownership result.

## Superseded conclusions

- The old stale/unseen-writer result was superseded by physical-byte samples
  observing nonzero `0x8011A8A0` at SP send boundaries. It was believable
  because static census found no writer, but it did not measure runtime stores.
- `setViModeType` does not map `osResetType`; generated loads show `osTvType`.
- Fixed-selector, bad-mode-table, and host-logger explanations for width 320
  are closed by the descriptor chain and independent retail controls.
- The old boot/menu overlay-dispatch explanation is closed by mission and
  post-sec2 behavior.
- The nonblank-EEPROM explanation was refuted by paired existing-versus-zero
  EEPROM runs with positive controls intact.
- The broad retail-only GPR mismatch was refuted by the complete generated-path
  census: saved `s3..s7`/`t3` values are dead or overwritten before use;
  `sp`/`ra` differ only in bookkeeping.
- The claim that no frontend, launcher, or savestate artifact existed was
  refuted by the adjacent Mupen64Plus source, installed `--savestate` support,
  and existing state files. Their audited lifecycle still has no new retail
  state source.
- The s1194–s1239 claim that the external retail-entry boundary "lacks a
  new state-changing route" and that the available recipe remains at width
  320 / `0x006dd280` is superseded. It was believable because those sessions
  used dummy video, whose `ProcessDList` is empty, so the boot cinematic
  never advances. s707 and the s1496 dummy-vs-Rice batch show Rice is the
  later-phase route.
- The s1135 remainder that physical `0x688..0x710` is the retail shade
  record (parked as unevaluable under dummy video in s1136–s1239) is
  rejected. It was believable because the port probe treated `r9` as RDRAM
  (`r9 & 0x7FFFFF`) and the dummy-video nulls never reached hangar. s1512
  Rice hangar plus generated DMEM `ori $9, $zero, 0x670` close it.
- The s1086 claim that retail never accesses `0x130B10:0x130B58` on the
  eleven-Start schedule is superseded. It was believable because that run
  stayed at dummy-video 320/`0x006dd280`. s1528 Rice hangar writes the
  block, and leave-hangar arms add `0x800c68d0` → `0x130b40`.

## Evidence ledger summary

| Sessions | Durable result |
|---|---|
| s820–s951 | Post-sec2 accounting and M3 crash/idiom families were classified or parked. |
| s952–s983 | Dispatcher stack-spill family localized; no static frame writer found. |
| s984–s1038 | M4 shade audits moved the issue to accumulator numeric origin. |
| s1039–s1167 | Retail/port controls, VI lifecycle, and generated boundaries were resolved; late runtime paths remain phase-sensitive. |
| s1168–s1193 | Audio and complete M3 store/load idiom audits closed without a mitigation; `do_sdl`/`do_sdr` selected H3. |
| s1194–s1239 | Dummy-video M4 and retail-entry experiments passed controls but stayed at VI 320; that parking is superseded by the Rice recipe. |
| s1240–s1268 | Exact companion/generated symbol sweeps synchronized the repository map; explicit fake/address-only entries stayed unchanged. |
| s1269 | Maintenance compaction only; no experiment or code change. |
| s1270–s1599 | Generated-symbol renaming sweep: exact companion/generated names from `0x80086450` through `triggerT16Effect` at `0x800BD958`, with the s1585 retail-entry revisit interleaved. H2/H3 parks listed under Next steps #1, including s1570 `fake_func_800B42BC`. Full per-session table in `PORTING-STATE.md`; compact archive in `PROJECT-OVERVIEW.md` §33. No build or runtime run in the census sessions. |
| s1496 | Dummy-vs-Rice revisit: dummy stayed at 320/`0x006dd280`; Rice reached 640, 1024, and hangar 512/`0x006ab400`. |
| s1512 | Rice hangar M4 revisit: whole-RDRAM 10000/removal rc=0, 11 Start/PIF hits, 320→640→1024→512/`0x006ab400`; `0x688:0x710` and `0x04000670:0x04000720` 0 CPU writes. Rejects RDRAM ownership of DMEM `r9`. |
| s1528 | Rice post-hangar A/B: hold stays 512/`0x6ab400`; extra Start or A leaves to 640/`0x6a2900`; `0x130B10:0x130B58` live (s1086 dummy-320 zeros were unevaluable); leave write `0x800c68d0` in `runHangarMenuFromOverlay`. Not an outdoor mission. |
| s1544 | Rice 640-identity revisit: four arms, whole-RDRAM 10000/removal rc=0, 11 Start/PIF, 320→640→1024→512. Leave A reaches 640/`0x6a2900`; post-settle Start/B seen on PIF, no third width. Last overlay load is menu `0x80000BA8` at 16.9s; mission path and `lv0`/`lv1` inits 0. Hangar ticks run 40–52s then `runHangarMenuFromOverlay` at 53s; 0 watched PCs after the 512→640 edge. 640 is still menu-overlay, not mission/cinematic/hangar-tick. |
| s1553 | Maintenance compaction only; no experiment or code change. |
| s1554 | H1: synchronized `tickCinematicObjectStateMachine` at `0x800B13E0` (size `0x808`). |
| s1555 | H1: synchronized `updatePlayerCraftPhysics` at `0x800B1BE8` (size `0x1B14`). |
| s1556 | H1: synchronized `applyCraftCapabilityFlags` at `0x800B36FC` (size `0xC4`). |
| s1557 | H1: synchronized `initPlayerCraftMovementMode` at `0x800B37C0` (size `0x250`). |
| s1558 | H1: synchronized `tryPlaySpatialSoundWithGates` at `0x800B3A10` (size `0x43C`). |
| s1559 | H1: synchronized `scheduleSceneFormatMessageTimed` at `0x800B3E4C` (size `0xC0`). |
| s1560 | H1: synchronized `cancelSceneQueueHandle` at `0x800B3F0C` (size `0x44`). |
| s1561 | H1: synchronized `playSpeechClipOncePerChange` at `0x800B3F50` (size `0x64`). |
| s1562 | H1: synchronized `playSpeechClipOncePerLevel` at `0x800B3FB4` (size `0xEC`). |
| s1563 | H1: synchronized `resetSpeechOncePerLevelFlag` at `0x800B40A0` (size `0x50`). |
| s1564 | H1: synchronized `setPlayerSlotPositionVec3` at `0x800B40F0` (size `0x44`). |
| s1565 | H1: synchronized `destroySceneNpcsAndUnlink` at `0x800B4134` (size `0x88`). |
| s1566 | H1: synchronized `decayWeaponCooldownTimer` at `0x800B41BC` (size `0x30`). |
| s1567 | H1: synchronized `getWeaponChargeLevel` at `0x800B41EC` (size `0x10`). |
| s1568 | H1: synchronized `advancePitchTowardTarget` at `0x800B41FC` (size `0xC0`). |
| s1569 | Rice 640-handler revisit: hold stays 512 with `runHangarSelectionFrame` through 100s; leave A stops that inner loop at 63.7s and enters `runModelViewerLoop` (case 6) at 64.3s with `initModelViewer` / `buildModelViewerTextPage` / `loadJfifAsset`. Selector write `0x800C5AC8` is the generated set-6 path. Extra Start during 640 does not exit. Not a mission. |
| s1584 | H1: synchronized `updateVwingEngineEffect` at `0x800B8C30` (size `0x9B0`); companion mapping, generated definition, `playerVwingUpdate` caller, exact `orientVwingSubmodelByQuat` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1585 | Rice model-viewer-input revisit: four arms (hold, A, B, Z) passed whole-RDRAM/PIF/VI controls and reached 640; all stayed in case-6 viewer with zero mission-path PC `0x80000B70`, identical watched PCs and target writes. Selects H3 for the tested buttons; no mitigation. |
| s1586 | H1: synchronized `orientVwingSubmodelByQuat` at `0x800B95E0` (size `0x370`); companion mapping, generated definition and three callers, exact next-function boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1587 | H1: synchronized `tickVwingEngineAudio` at `0x800B9950` (size `0x5FC`); companion mapping, generated definition and `playerVwingUpdate` caller, exact next-function boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1588 | H1: synchronized `computeFalconFlightTransform` at `0x800BA620` (size `0x3E0`); companion mission list, generated definition and `playerFalconMainUpdate` caller, exact `triggerFalconEngineEffect` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1589 | H1: synchronized `triggerFalconEngineEffect` at `0x800BAA00` (size `0x170`); companion mission list, generated definition and `spawnFalconEngineParticles` caller, exact next-function boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1590 | H1: synchronized `bindFalconSubmodelMaterials` at `0x800BAB70` (size `0x25C`); companion mission list, generated definition and `computeFalconFlightTransform` caller, exact `playerFalconMainUpdate` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1570 | H2: parked already-fake `fake_func_800B42BC` at `0x800B42BC` (size `0x4`). |
| s1571 | H1: confirmed `playerXwingInit` at `0x800B42C0` is already synchronized: exact `0x2C8` TOML/overlay/generated boundary, companion name, and two generated `playerXwingUpdate` calls agree; no file rename was needed. |
| s1572 | H1: synchronized `playWeaponFireSound` at `0x800B4588` (size `0x738`); companion mapping, generated definition, TOML boundary, and a generated caller agree. No build or runtime run was needed. |
| s1573 | H1: synchronized `playXwingEngineSound` at `0x800B4F54` (size `0x4E0`); companion mapping, generated definition/caller, and TOML boundary agree. No build or runtime run was needed. |
| s1574 | H1: synchronized `isWeaponSlotReady` at `0x800B585C` (size `0x58`); companion mapping, generated definition/callers, TOML boundary, and the adjacent fake/`playerAwingInit` boundaries agree. No build or runtime run was needed. |
| s1575 | H1: synchronized `resetEngineTrailQuads` at `0x800B5B4C` (size `0x87C`); companion mapping, generated definition/caller, exact next-function boundary, and TOML size agree. No build or runtime run was needed. |
| s1576 | H1: synchronized `acquireLockOnTarget` at `0x800B63C8` (size `0x3D8`); companion mapping, generated definition/two callers, exact next-function boundary, and TOML size agree. No build or runtime run was needed. |
| s1577 | H1: synchronized `emitTexturedImpactEffect` at `0x800B67A0` (size `0x1F0`); companion mapping, generated definition/three callers, exact next-function boundary, and TOML size agree. No build or runtime run was needed. |
| s1578 | H1: synchronized `updateEngineThrustEffect` at `0x800B6990` (size `0x7D8`); companion mapping, generated definition/caller, exact next-function boundary, and TOML size agree. No build or runtime run was needed. |
| s1579 | H1: synchronized `findLockOnTarget` at `0x800B7590` (size `0x34`); companion mapping, generated definition/three callers, exact next-function boundary, and TOML size agree. No build or runtime run was needed. |
| s1580 | H1: synchronized `tickCraftAbilityCooldown` at `0x800B77D0` (size `0x27C`); companion mapping, generated definition/caller, exact next-function boundary, and TOML size agree. No build or runtime run was needed. |
| s1581 | H1: synchronized `orientEffectToVelocity` at `0x800B7A4C` (size `0x3B0`); companion mapping, generated definition/caller, exact next-function boundary, and TOML size agree. No build or runtime run was needed. |
| s1582 | H1: synchronized `spawnTexturedExplosionBurst` at `0x800B7DFC` (size `0x68C`); companion mapping, generated definition, `playerYwingUpdate` caller, exact next-function boundary, and TOML size agree. No build or runtime run was needed. |
| s1583 | H1: synchronized `emitTexturedEffectCue` at `0x800B88C8` (size `0x12C`); companion mapping, generated definition, exact `fake_func_800B89F4` boundary, and TOML size agree, with matching texture/cue-dispatch semantics. No build or runtime run was needed. |

| s1591 | H1: synchronized `playerFalconMainUpdate` at `0x800BADCC` (size `0x83C`); companion mission list, generated definition and caller from `spawnFalconEngineParticles`, exact next-function boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1592 | H1: synchronized `spawnFalconEngineParticles` at `0x800BB608` (size `0x228`); companion mission list, generated definition, `playerFalconUpdate` caller, exact next-function boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1593 | H1: synchronized `integrateFalconFlightPhysics` at `0x800BBC58` (size `0xD8`); companion mission list, generated definition and floating-point clamp/integration body, exact `playerTieInterceptorInit` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1594 | H1: synchronized `computeTieInterceptorTransform` at `0x800BBF6C` (size `0x324`); companion mission list, generated definition, generated caller at `0x800BCAE8`, exact `triggerTieInterceptorEffect` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1595 | H1: synchronized `triggerTieInterceptorEffect` at `0x800BC290` (size `0x268`); companion mission list, generated definition and six generated callers from `playerTieInterceptorUpdate`, exact next-function boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1596 | H1: synchronized `computeTieInterceptorOrientation` at `0x800BC4F8` (size `0x318`); companion mission list, generated definition and `playerTieInterceptorUpdate` caller, exact next-function boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1597 | H1: synchronized `computeT16Transform` at `0x800BCE74` (size `0x3E0`); companion mission list, generated definition and `playerT16Update` caller, exact `playerT16MainUpdate` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1598 | H1: synchronized `playerT16MainUpdate` at `0x800BD254` (size `0x2DC`); companion mission list, generated definition and `playerT16Update` caller at `0x800BD814`, exact `playerT16Update` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1599 | H1: synchronized `triggerT16Effect` at `0x800BD958` (size `0xF8`); companion mission list, generated definition and effect/sound dispatch body, exact `playerNabooStarfighterInit` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1600 | H1: synchronized `buildNabooSubmodelTransform` at `0x800BDC9C` (size `0x58C`); companion mission list, generated definition and caller, exact `triggerNabooEngineEffect` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1601 | H1: synchronized `triggerNabooEngineEffect` at `0x800BE228` (size `0x280`); companion mission list, generated definition and three callers, exact `tickPlayerCraftBlinkIndicator` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1602 | M4 paired revisit: the existing LLE probe passed its independent arithmetic control, captured four phase-6 target tuples, and matched the local VMADH model on all 32 target lanes with no post-VGE change. This is a single-source local consistency result. Live DMA logging identified the port destination as runtime `0x4B7800..0x4B7808`; the retail oracle passed whole-RDRAM and VI controls through 320→640→1024→512 but wrote that candidate zero times. The targeted retail null is unevaluable across differing allocation/scene origins; no mitigation. |
| s1603 | H1: synchronized `tickPlayerCraftBlinkIndicator` at `0x800BE4A8` (size `0x328`); companion mission mapping, generated definition and `playerNabooStarfighterUpdate` caller, exact next-function boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1604 | H1: synchronized `initDemoPlayState` at `0x800BEC00` (size `0xDC`); companion mission mapping, generated definition and `loadAndStartDemo` caller, exact `applyDemoRecordedHudEvents` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1605 | H1: synchronized `applyDemoRecordedHudEvents` at `0x800BECDC` (size `0x13C`); companion mission mapping, generated definition and demo-HUD state-update body, exact `clearPlayerSlotHudTracking` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1606 | H1: synchronized `clearPlayerSlotHudTracking` at `0x800BEE18` (size `0x94`); companion mission mapping, generated definition and `initAllPlayersHudTracking` caller, exact next-function boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1607 | H1: synchronized `tickPlayerHudIndicators` at `0x800BEFBC` (size `0x2A8`); companion mission mapping, generated definition in `funcs_33.c`, generated caller in `funcs_42.c`, four-player/16-indicator HUD update semantics, exact `loadPlayerSlotHudPreset` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1608 | H1: synchronized `loadPlayerSlotHudPreset` at `0x800BF264` (size `0x90`); companion mapping, generated definition and HUD-preset copy semantics, exact `countTrailingZeros16` boundary, overlay-table span, and TOML size agree. No build or runtime run was needed. |
| s1609 | H1: synchronized `countTrailingZeros16` at `0x800BF2F4` (size `0x64`); companion mapping, generated definition and 15 generated call sites across two generated files, exact `applyResModeFromSettings` boundary, overlay-table span, and TOML size agree. H2/H3 were ruled out by the exact independent name, live body, and span. No build or runtime run was needed. |
| s1610 | H1: synchronized `applyResModeFromSettings` at `0x800BF358` (size `0x4C`); companion mapping, generated flag-propagation body and caller, exact `restoreGameSettingsAfterDemo` boundary, overlay-table span, and TOML size agree. H2/H3 were ruled out by the exact independent name, live body, caller, and span. No build or runtime run was needed. |
| s1611 | H1: synchronized `restoreGameSettingsAfterDemo` at `0x800BF3A4` (size `0x64`); companion mapping, generated restore-body semantics and caller, exact adjacent boundaries, overlay-table span, and TOML size agree. H2/H3 were ruled out by the exact independent name, live body, caller, and span. No build or runtime run was needed. |
| s1612 | H1: synchronized `loadAndStartDemo` at `0x800BF408` (size `0x60`); companion mapping, generated definition and demo asset/init/flag-setting body, generated caller, exact adjacent boundaries, overlay-table span, and TOML size agree. H2/H3 were ruled out by the exact independent name, live body, caller, and span. No build or runtime run was needed. |
| s1613 | H1: synchronized `getDemoRecordedTimestep` at `0x800BF468` (size `0x30`); companion mapping, generated timestep-lookup body and caller, exact adjacent boundaries, overlay-table span, and TOML size agree. H2/H3 were ruled out by the exact independent name, live body, caller, and span. No build or runtime run was needed. |

| s1615 | H1: confirmed `fake_func_800BF784` at `0x800BF784` (size `0xC`) is an explicit three-instruction fake fragment; companion mapping, generated body, TOML size, exact `func_800BF790` boundary, and overlay-table span agree. No rename, build, or runtime run was needed. |
| s1616 | Retail Rice input revisit: four arms passed whole-RDRAM controls and reached hangar 512. Pre-exit B was delivered and selected a distinct 512→1024→640 route (`0x00790400`→`0x00696100`) with zero model-viewer and mission-entry PCs; A followed the known case-6 512→640 viewer route. Up/Down were invalid `sym=0` injections and remain unevaluable. Selector watch `0x13B40:0x13B48` stayed quiet. Single-source retail execution, with generated B-mask branch as an independent static control. |
| s1617 | H3: bounded census of `func_800BF790` at `0x800BF790` (size `0x634`) found a live generated HUD-health body and exact mission section/TOML boundaries, but the companion name `updateHudHealthIndicator` exists only in the separate/ambiguous main-overlay list while the mission mapping remains address-coded. The overlay-context conflict leaves the mission name unvalidated; no rename, build, or runtime run was needed. |
| s1618 | H3: bounded census of `func_800C41B0` at `0x800C41B0` (size `0x1AC`) found a live generated radar-blip body, exact `fake_func_800C41AC`/`plotRadarBlipRow` boundaries, matching TOML size, and matching mission overlay span, but the only independent name at the address is `plotRadarBlipColumn` in `main_overlay.txt`; the mission mapping remains address-coded. The overlay-context conflict leaves the name unvalidated; no rename, build, or runtime run was needed. |

## Method and safety rules

- A null result is worthless without a positive control in the same run.
- Batch instrumentation, scope budgets to the VI phase, use SIGKILL, launch
  from `build/`, and queue repeat soaks instead of babysitting.
- Regeneration order is `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated code belong in fixup scripts.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. Changes under `lib/` require patch export.
- Before any mitigation, identify the writer and legitimacy with an `ORIGIN:`
  line.
