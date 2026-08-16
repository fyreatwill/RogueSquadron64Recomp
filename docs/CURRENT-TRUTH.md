# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable project
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is
the authority for session detail. Reviewed through s1703 (2026-08-16).

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
  partial loads, and `do_sdl`/`do_sdr` found no reachable frame-overlapping
  writer. Runtime guest memory/value corruption remains open; no mitigation is
  justified.
- The corrected `npcPowerGeneratorUpdate` boundary is main `.text` at
  `0x80077AF0`; regenerated ELF, N64Recomp output, fixups, and Debug target
  pass. Runtime boundary tests remain pre-1024 and unevaluable.
- M5 audio de-stubbing is closed. Audio remains stubbed. Prior retail watches
  that stayed at VI 320 used dummy video and never reached the identified
  `musyxInitVoiceFromSample` writers. Do not reopen without a new bounded plan
  using the Rice hangar recipe below.
- The retail oracle's whole-RDRAM, scheduled PIF, and VI controls are healthy.
  Dummy video stays at width 320 / origin `0x006dd280`. Homebrew Rice with
  `--video …/mupen64plus/mupen64plus-video-rice.dylib` and the eleven-Start
  schedule reaches `320→640` at about 2.3s, `640→1024` at about 17.2s, and
  `1024→512` hangar at about 38.4s, with hangar origins
  `0x006ab400`/`0x006ab800` (s707, s1496).
- After hangar, extra Start or A reaches a 640 planet/text-crawl viewer at
  `0x006a2900`/`0x006a2e00`; it is menu-overlay case 6
  `runModelViewerLoop` (`0x800C9BF0`), not a mission or cinematic reload.
  Hold remains in `runHangarSelectionFrame` at 512. Pre-exit B is a distinct
  valid route (`sym=224`, pad word `0x400000`) through `512→1024→640` with no
  viewer or mission-entry PC, so not every hangar exit is case 6. After that
  B intermediate 1024 phase begins, A or Start cancels back to hangar 512;
  Z is ignored and the B-route completes to 640 at `0x00696100` (s1650).
  That arrived 640 B-frontend is neither hangar nor viewer: hangar-frame
  PCs stay at the earlier hangar-visit count, viewer `0x800C9BF0` is zero,
  and the origin pair is `0x00696100`/`0x00696600`. It lasts about 21 s
  then times out to attract 512 (`0x00690400`). A or Start pressed on it
  cancel `640→1024→512` hangar; Z on it is ignored (s1666). C, L, R, and
  valid D-pad on it are ignored (s1682): same 117.7 s attract timeout as
  hold, viewer PC zero, hangar-frame 59–62, and `0x80000B70` = 1 matching
  hold so the interior hit is the post-timeout attract path, not the
  105/115 press. On the attract 512 that timeout reaches, A, Start,
  C-up, and L at 119/123 leave `512→1024` at 126.4 s origin
  `0x00790400`/`0x00790800` (title-like; same pair as the B-route
  intermediate). The 125 s flush cuts off at that WIDTH change, so the
  1024 destination is unevaluable; hangar-frame PCs did not increment
  and viewer stayed 0. Z, C-down, C-left, C-right, R, and valid D-pad
  stay on attract 512 matching hold through 125.8 s (s1698). Z-on-attract
  `512→1024` at 128.3 s (s1666, after a 126.4 s Z press) is still
  single-source: this window ended at 125.8 s. `0x80000B70` = 1 on hold
  and every candidate. The watched "mission PC" `0x80000B70` is
  `loadOverlay+0x50` (same function, `0x80000B20` size `0x124`), not a
  separate entry. Valid D-pad on hangar, post-viewer C/L/R, post-B
  intermediate A/Start/Z, post-arrival A/Start/Z/C/L/R/D-pad on the
  640 B-frontend, and attract-512 A/Start/Z/C/L/R/D-pad in the
  119–125 s window are classified or parked; do not repeat them.
- The port VI 640-to-1024 lifecycle is generated state plus host VI
  submission. `applyPendingViChanges` can change selector bytes
  `0x8011A862/0x8011A864/0x8011A865`; a direct `osViSetMode` edge can submit
  `0x80128DF0` without entering the selector consumer. Host logging agrees
  with generated and committed VI state. The active boot descriptor selects
  the index-0 320 record.
- M4 shade-lane/order is not the cause. Port VMADH modeling and an independent
  control matched all 128 lanes; VGE changed 0/128 (s1135). Rice hangar
  watches found zero CPU writes to physical `0x688..0x710` and zero writes to
  SP-DMEM `0x04000670:0x04000720` (s1512). Generated `ori $9, $zero, 0x670`
  and the only `SP_WR_LEN` DMA from DMEM `0xD60` identify `r9` as DMEM.
  s1602's phase-6 paired capture matched the local VMADH model on all 32
  target lanes with no VGE change. This is single-source local consistency,
  not an independent retail arithmetic proof; the unresolved boundary is
  source state or later DMA/consumer identity. The port runtime destination
  `0x4B7800..0x4B7808` was quiet in the retail oracle, but differing allocator
  and scene origins make that targeted null unevaluable.

## Active investigation and ranked next steps

1. Resume the generated-symbol sweep at `fake_func_800D2C98`
   (`0x800D2C98`, size `0x8`). After s1703 the last-15 titles
   include the s1698 retail-entry revisit, so the 15-title gate does
   not fire. s1651–s1665, s1667–s1681, s1683–s1697, and s1699–s1703
   synchronized or confirmed DAT-item through
   `spawnScaledBootVec4Effect`; s1650, s1666, s1682, and s1698 were
   the mandatory retail-entry revisits. The full s1590–s1649 archive
   is in `PROJECT-OVERVIEW.md` §34; the earlier sweep is in §33.
   About 1,548 placeholder `func_0x...` names remained when counted
   at s1487.
2. Remaining external retail-entry / M4 revisit leads, for the next
   15-title gate only: destination of the attract-512 A/Start/C-up/L
   `512→1024` at 126.4 s (origin `0x00790400`/`800`; 125 s flush cut
   off at the WIDTH change); Z-on-attract `512→1024` at 128.3 s is
   still single-source (s1666; s1698's 125 s window ended at 125.8 s
   still on 512). Do not repeat hangar hold/A/B/Z, valid D-pad on
   hangar, post-viewer C/L/R, post-B intermediate A/Start/Z,
   post-arrival A/Start/Z/C/L/R/D-pad on the 640 B-frontend, or
   attract-512 A/Start/Z/C/L/R/D-pad in the 119–125 s window. Every
   oracle run needs whole-RDRAM, PIF, and VI/PC positive controls.
   Alternative: a new M4 RDRAM destination from a DMEM→RDRAM transfer
   other than `0xD60`.
3. Keep audio closed unless a new independent lead reaches audio
   initialization or voice allocation. If that happens, write a bounded plan
   before changing any stub or trap.
4. Revisit M3 only as a complete idiom-class audit with a named discriminator.
   Do not chase recurring single-crash breadcrumbs reactively.
5. For any runtime probe, read `tools/oracle/README.md` and
   `docs/F5-UCODE-REFERENCE.md`, batch all arms in one build/run, phase-gate
   animated comparisons on VI transitions, use SIGKILL, and queue repeat
   soaks instead of babysitting them.

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
data-like. No next class is justified without a new discriminator.

### VI descriptor boundary

`osTvType=1` feeds `rsViModeType=0`; boot selector bytes are `A/B/C=1/0/0`.
`initVideoSubsystem` copies records to `0x00/0x50/0xA0/0xF0`, and the active
selector chooses base `+0xF0` (`0x80128E40`), the 320 descriptor.
`osViSetMode_recomp` forwards `ctx->r4` unchanged; the host does not rewrite
width. This boundary is independently established.

### M4 accumulator boundary

Factor 5 reference data and paired combiner evidence refute an RT64 shade
ordering explanation. VTXCOLOR is nonzero while decoded shade is the fixed
`0xFFFF8000`/`0x00008000` sentinel. Port VMADH matched all 128 captured
lanes; VGE mutated none. The Rice physical watches and generated DMEM source
proof reject `0x688..0x710` as the retail CPU-written shade record. The s1602
32-lane capture is a single-source local consistency result, not an
independent retail arithmetic witness. The unresolved boundary is source
state or later DMA/consumer identity, not RT64 lane order or low-RDRAM
ownership.

## Superseded conclusions

- The old stale/unseen-writer result was superseded by physical-byte samples
  observing nonzero `0x8011A8A0` at SP send boundaries. Static census had found
  no writer, but it had not measured runtime stores.
- `setViModeType` does not map `osResetType`; generated loads show `osTvType`.
  Fixed-selector, bad-mode-table, and host-logger explanations for width 320
  are closed by the descriptor chain and independent retail controls.
- The old boot/menu overlay-dispatch explanation is closed by mission and
  post-sec2 behavior.
- The nonblank-EEPROM explanation was refuted by paired existing-versus-zero
  EEPROM runs with positive controls intact.
- The broad retail-only GPR mismatch was refuted by the complete
  generated-path census: saved `s3..s7`/`t3` values are dead or overwritten;
  `sp`/`ra` differ only in bookkeeping.
- The claim that no frontend, launcher, or savestate artifact existed was
  refuted by adjacent Mupen64Plus source, installed `--savestate` support, and
  existing state files. Their audited lifecycle still has no new retail state
  source.
- The s1194–s1239 claim that the external retail-entry boundary lacked a new
  state-changing route and the available recipe stayed at width 320 is
  superseded. Those sessions used dummy video, whose empty `ProcessDList`
  prevented the boot cinematic from advancing; Rice supplies the later phase.
- The s1135 remainder that physical `0x688..0x710` was the retail shade record
  is rejected by s1512's Rice hangar watches and generated DMEM proof.
- The s1086 claim that retail never accesses `0x130B10:0x130B58` on the
  eleven-Start schedule is superseded by s1528 Rice hangar/leave-hangar runs.

## Evidence ledger summary

| Sessions | Durable result |
|---|---|
| s820–s951 | Post-sec2 accounting and M3 crash/idiom families were classified or parked. |
| s952–s1167 | Dispatcher spill, M4 shade, VI lifecycle, retail controls, and generated boundaries were narrowed; unresolved runtime paths remain phase-sensitive. |
| s1168–s1239 | Audio and complete M3 store/load audits closed without mitigation; dummy-video retail-entry/M4 results were later superseded by Rice. |
| s1240–s1589 | Exact companion/generated symbol sweep through `triggerFalconEngineEffect`; s1585 was the required retail-entry revisit. Full archive: `PROJECT-OVERVIEW.md` §33. |
| s1590–s1637 | Continued exact sweep through `dispatchObjectiveSlot1`, with M4 revisit s1602 and Rice route/input revisits s1616, s1620, and s1636. Full archive: `PROJECT-OVERVIEW.md` §34. |
| s1638 | Maintenance compaction only; no experiment or code change. |
| s1639 | Confirmed `checkComplexObjectives` (`0x800C7358`, size `0x38`) already agrees across companion mapping, generated body, TOML, and section-4 overlay span; next candidate is `func_800C7648`. |
| s1640 | Synchronized `getAndSetByteAtLevelStateTable` (`0x800C7648`, size `0x18`) after companion callers/semantics, generated byte-swap body, TOML size, and section-4 span agreed; next candidate is `func_800C7718`. |
| s1641 | Synchronized `getGlobalFloatGameState` (`0x800C7718`, size `0x10`) after companion mapping, live generated float-load body, TOML size, and section-4 span agreed; next candidate is `func_800C7728`. |
| s1642 | Synchronized `getObjectiveGlobalFloat` (`0x800C7728`, size `0x10`) after companion mapping, live generated objective-float getter, exact adjacent boundaries, TOML size, and section-4 span agreed; next candidate is `func_800C7738`. |
| s1643 | Synchronized `setHudEnableBit4` (`0x800C7738`, size `0x34`) after companion caller/semantic mapping, live generated body, exact adjacent boundaries, TOML size, and section-4 span agreed; next candidate is `func_800C776C`. |
| s1644 | Synchronized `setHudEnableBit8` (`0x800C776C`, size `0x34`) after companion caller/semantic mapping, live generated body, exact adjacent boundaries, TOML size, and section-4 span agreed; next candidate is `func_800C77A0`. |
| s1645 | Synchronized `isLevelStateByteZero` (`0x800C77A0`, size `0x10`) after companion mapping, live generated byte-zero test, exact adjacent boundaries, TOML size, and section-4 span agreed; next candidate is `func_800C77D0`. |
| s1646 | Synchronized `randMod` (`0x800C77D0`, size `0x60`) after the companion mission mapping, live generated signed-16-bit random-remainder body, exact adjacent boundaries, TOML size, and section-4 span agreed; next candidate is `func_800C7830`. |
| s1647 | Confirmed `addBooleanCountHandleWrapper` (`0x800C7830`, size `0x34`) was already synchronized: companion mapping, live generated wrapper body, exact adjacent boundaries, TOML size, and section-4 span agreed; next candidate is `func_800C7864`. |
| s1648 | Confirmed `addTimerHandleWrapper` (`0x800C7864`, size `0x20`) was already synchronized: companion mission mapping, live generated wrapper body, exact adjacent boundaries, TOML size, and section-4 span agreed; next candidate is `func_800C7884`. |
| s1649 | Synchronized `setHudFlagBit40AndStoreArg` (`0x800C7884`, size `0x1C`) after the companion mapping, live generated body, exact `0x800C7864`/`0x800C78A0` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder; next candidate is `func_800C78A0`. |
| s1650 | Rice post-B A/Start/Z revisit: all arms passed whole-RDRAM and hangar controls; zero mission/viewer PC. Hold and Z completed B-route 640 at `0x00696100`; A and Start cancelled the post-B 1024 intermediate back to hangar 512. H3 selected for A/Start; Z ignored. Mission entry still open only for a genuinely new route. |
| s1651 | Confirmed `calculateDatItemDistanceToPlayer` (`0x800C78A0`, size `0xAC`) was already synchronized: companion mission mapping, live generated 3D DAT-item-to-player distance body, exact `0x800C7884`/`0x800C794C` boundaries, TOML size, and section-4 span agreed; next candidate is `func_800C794C`. |
| s1652 | Synchronized `getScaledPlayerCraftSpeed` (`0x800C794C`, size `0x2C`) after companion mission mapping, live generated craft-speed scale body, exact `0x800C78A0`/`0x800C7978` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder; next candidate is `func_800C7978`. |
| s1653 | Synchronized `spawnEffectOnNamedDatItem` (`0x800C7978`, size `0x78`) after companion mission mapping, live generated DAT-item effect-spawn body, exact `0x800C794C`/`0x800C79F0` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder; next candidate is `func_800C79F0`. |
| s1654 | Synchronized `initActorTowardNamedDatItem` (`0x800C79F0`, size `0xC0`) after companion mission mapping, live generated DAT-item actor-init body, exact `0x800C7978`/`0x800C7AB0` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder; next candidate is `func_800C7AB0`. |
| s1655 | Synchronized `initAnchoredActorTowardNamedDatItem` (`0x800C7AB0`, size `0xB0`) after companion mission mapping, live generated DAT-item anchored-actor-init body, exact `0x800C79F0`/`0x800C7B60` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder; next candidate is `getDatItemHealth`. |
| s1656 | Confirmed `getDatItemHealth` (`0x800C7B60`, size `0xC8`) was already synchronized: companion mission mapping, live generated DAT-item health-lookup body, exact `0x800C7AB0`/`0x800C7C28` boundaries, TOML size, and section-4 span agreed; next candidate is `getDatItemHealthPercentage`. |
| s1657 | Confirmed `getDatItemHealthPercentage` (`0x800C7C28`, size `0x60`) was already synchronized: companion mission mapping, live generated DAT-item health-percentage body, exact `0x800C7B60`/`0x800C7C88` boundaries, TOML size, and section-4 span agreed; next candidate is `func_800C7C88` / `despawnEffectOnNamedDatItem`. |
| s1658 | Synchronized `despawnEffectOnNamedDatItem` (`0x800C7C88`, size `0x64`) after companion mission mapping, live generated DAT-item effect-despawn body, exact `0x800C7C28`/`0x800C7CEC` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder; next candidate is `func_800C7CEC` / `setLevelObjectTrackingScalar`. |
| s1659 | Synchronized `setLevelObjectTrackingScalar` (`0x800C7CEC`, size `0xC`) after companion mission mapping (12 `lvN_initializeObjectTracking` callers; `MEM_W[0x8013973C]=f12`), live generated one-instruction float store, exact `0x800C7C88`/`0x800C7CF8` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder; next candidate is `func_800C7D44` / `dispatchHudEffectUpdate`. |
| s1660 | Synchronized `dispatchHudEffectUpdate` (`0x800C7D44`, size `0x1C`) after companion mission mapping, live generated thin wrapper (`jal initSpeechPlaybackState` / `0x80067938`), exact `0x800C7D1C`/`0x800C7D60` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder; next candidate is `func_800C7D60` / `delegateToLevelStageTick`. |
| s1661 | Synchronized `delegateToLevelStageTick` (`0x800C7D60`, size `0x1C`) after companion mission mapping, live generated thin wrapper (`jal 0x800EF770` → `triggerStageMusicForNamedDatItem`), exact `0x800C7D44`/`0x800C7D7C` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder; next candidate is `func_800C7D7C` / `triggerNamedAssetCue`. |
| s1662 | Synchronized `triggerNamedAssetCue` (`0x800C7D7C`, size `0x1C`) after companion mission mapping, live generated thin wrapper (`jal 0x800EF95C` → `triggerStageAmbientForNamedDatItem`), exact `0x800C7D60`/`0x800C7D98` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder; next candidate is `func_800C7D98` / `triggerSoundCueByType`. |
| s1663 | Synchronized `triggerSoundCueByType` (`0x800C7D98`, size `0x1C`) after companion mission mapping, live generated thin wrapper (`jal 0x800EFCD4` → `initSoundCueRequest`), exact `0x800C7D7C`/`0x800C7DB4` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder; next candidate is `func_800C7DC0` / `initNpcActorFromSpawnMessage`. |
| s1664 | Synchronized `initNpcActorFromSpawnMessage` (`0x800C7DC0`, size `0x238`) after companion mission mapping, live generated NPC-actor-from-spawn-message body (ends `initObjectAnimSubstruct`), exact `0x800C7DB4`/`0x800C7FF8` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder; next candidate is `func_800C7FF8` / `playNpcStateChangeEffect`. |
| s1665 | Synchronized `playNpcStateChangeEffect` (`0x800C7FF8`, size `0x180`) after companion mission mapping, live generated NPC state-change effect body (`lookupHmtTextureByName` ×2, emit-direction jitter, progress-channel ticks, `triggerCueWithSlotEffect`, `play3DSoundEvent`), exact `0x800C7DC0`/`0x800C8178` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `computeCellGridIndices` at `0x800C804C` is a different overlay, not a name collision. Next candidate is `func_800C8178` / `spawnNpcDestructionEffect`. Last-15 titles were then all sweep-scoped, so s1666 was the mandatory retail-entry revisit. |
| s1666 | Rice post-arrival A/Start/Z on the 640 B-frontend (`1024→640` ~96 s, origin `0x00696100`/`0x00696600`). All arms passed whole-RDRAM and B-pad controls and reached that frontend before the 105 s presses. The 640 screen is neither hangar nor viewer; it times out at ~117.7 s to attract 512 (`0x00690400`). A/Start at 106.3 s cancel `640→1024→512` hangar (H3). Z on 640 is ignored (H2). `0x80000B70` is `loadOverlay+0x50`; A/Start hit it 0 times, Z once only after the later attract continuation. Hold died rc=139 at 135 s still on attract 512. Next sweep candidate is `func_800C8178` / `spawnNpcDestructionEffect`. |
| s1667 | Synchronized `spawnNpcDestructionEffect` (`0x800C8178`, size `0x38C`) after companion mission mapping, live generated NPC destruction-effect body (`getObjectMeshTransformOrLocal`, `getObjectNpcTypeId`, `lookupHmtTextureByName` ×2, `triggerCueWithSlotEffect` ×4, `spawnByteAnimDebrisWithParam` ×2, `slotDispatcherIter` ×2, `play3DSoundEvent`), exact `0x800C7FF8`/`0x800C8504` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `buildDebrisCellBitfield` at `0x800C821C` is a different overlay, not a name collision. Next candidate is `func_800C8504` / `spawnNpcImpactEffectVariant`. |
| s1668 | Synchronized `spawnNpcImpactEffectVariant` (`0x800C8504`, size `0x474`) after companion mission mapping, live generated NPC impact-effect body (`lookupHmtTextureByName` ×4, `generatePerpEmitDirectionWithJitter` ×4, `tickProgressChannel` ×6, `triggerCueWithSlotEffect` ×5, `getObjectMeshTransformOrLocal`, `getObjectNpcTypeId`, `slotDispatcherIter` ×2, `play3DSoundEvent`), exact `0x800C8178`/`0x800C8978` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `allocDebrisCellTable` at `0x800C8520` is a different overlay, not a name collision. Next candidate is `func_800C8978` / `updateNpcOrientationFromMotion`. |
| s1669 | Synchronized `updateNpcOrientationFromMotion` (`0x800C8978`, size `0x518`) after companion mission mapping, live generated orientation-from-motion body (`buildRotationMatrixSlot0`/`composeRotationMatrixSlot1`, `transformVec3ByMat34`, `isPendingChildNpcActive`, `computeActorAnchorDeltaAfterLOS`, `getObjectMeshTransformOrLocal`, `computeAnchorRelativePositionByDistanceRatio`, `vec3Length` ×4, `vec3Dot` ×3, `vec3Cross` ×2, `quatFromAxisAngle`, `rotateVec3ByQuat`, `play3DSoundEventVariant`), exact `0x800C8504`/`0x800C8E90` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `allocCellGeometryBuffer` at `0x800C8A64` is a different overlay, not a name collision. Next candidate is `func_800C8E90` / `setupNpcModelForState`. |
| s1670 | Synchronized `setupNpcModelForState` (`0x800C8E90`, size `0x100`) after companion mission mapping, live generated state-to-mesh body (`releaseMeshAsset`, state halfword `+0x70` picks `0x800A6A0C`/`0x6A18`/`0x6A24`/`0x6A30`, `walkMeshdef0List`, `initVec4TripletFromArgs`, `composeRotationMatrixSlot0`/`Slot1`/`Slot2`, `addVec3At0x24`), exact `0x800C8978`/`0x800C8F90` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `buildDebrisMeshFromCells` at `0x800C8C1C` is a different overlay, not a name collision. Next candidate is `npcTurretUpdate`. |
| s1671 | Confirmed `npcTurretUpdate` (`0x800C8F90`, size `0x11FC`) was already synchronized: companion mission mapping, live generated 11-way turret-update body (`setupNpcModelForState`, `updateNpcOrientationFromMotion`, `safeLookup3DSoundEntry`, `play3DSoundEvent`, `unregisterAndFreeNpcSlot`), exact `0x800C8E90`/`0x800CA18C` boundaries, TOML name and size, and section-4 span agreed. Menu-overlay `cloneCellBufferWithAlloc` / `allocZeroedCellRecord` / `runModelViewerLoop` at `0x800C9A88`/`0x800C9B8C`/`0x800C9BF0` are a different overlay, not a name collision. Next candidate is `func_800CA18C` / `playNpcAmbientEffect`. |
| s1672 | Synchronized `playNpcAmbientEffect` (`0x800CA18C`, size `0xE0`) after companion mission mapping, live generated ambient-effect body (`lookupHmtTextureByName`, `generatePerpEmitDirectionWithJitter`, `tickProgressChannel`, `triggerCueWithSlotEffect`, `play3DSoundEvent`), exact `0x800C8F90`/`0x800CA26C` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `runModelViewerLoop` at `0x800C9BF0` (size `0xA48`) is a different overlay, not a name collision. Next candidate is `func_800CA270` / `initNpcActorVariant`. |
| s1673 | Synchronized `initNpcActorVariant` (`0x800CA270`, size `0x134`) after companion mission mapping, live generated NPC-actor-init body (`setNpcHealth`, `initActorMotionParams`, `setObjectDetailLevel`, `initObjectAnimSubstruct`, `setEffectIntensity`), exact `0x800CA26C`/`0x800CA3A4` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `runModelViewerLoop` at `0x800C9BF0` (size `0xA48`) is a different overlay, not a name collision. Next candidate is `func_800CA3A4` / `spawnProbeDroidGroundImpactEffect`. |
| s1674 | Synchronized `spawnProbeDroidGroundImpactEffect` (`0x800CA3A4`, size `0x1BC`) after companion mission mapping, live generated ground-impact-effect body (`getObjectMeshTransformOrLocal`, `vec3Cross` ×2, `normalize_vector` ×3, `generatePerpEmitDirectionWithJitter`, `tickProgressChannel`, `triggerCueWithSlotEffect`, `play3DSoundEvent`), exact `0x800CA270`/`0x800CA560` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `runModelViewerLoop` at `0x800C9BF0` (size `0xA48`) is a different overlay, not a name collision. Next candidate is `func_800CA560` / `initProbeDroidScatterLaunch`. |
| s1675 | Synchronized `initProbeDroidScatterLaunch` (`0x800CA560`, size `0x1C0`) after companion mission mapping, live generated scatter-launch-init body (`rand` ×4, `vec3Length`, `normalize_vector`; writes target `+0x6C/+0x70/+0x74`, speed `+0x78`, state halfword `+0xE2=1`), exact `0x800CA3A4`/`0x800CA720` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `initModelViewer` / `buildModelViewerTextPage` at `0x800CA638`/`0x800CA714` are a different overlay, not a name collision. Next candidate is `func_800CA720` / `updateProbeDroidHopState`. |
| s1676 | Synchronized `updateProbeDroidHopState` (`0x800CA720`, size `0x4B4`) after companion mission mapping, live generated hop-state body (reads/writes state halfword `+0xE2`; state 1 walks toward scatter target `+0x6C/+0x70/+0x74` via `vec3NormalizeInto`/`vec3Length`/`normalize_vector`/`vec3Dot`/`sinfApprox`/`quatFromAxisAngle`/`rotateVec3ByQuat`/`orthonormalizeFrame`; later states `spawnNpcAnchoredEffectSlot`, `wrapAngleToCyclicRange`, `isTerrainCellBlockedAtWorldXz`, `rs_free`), exact `0x800CA560`/`0x800CABD4` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `initModelViewer` / `buildModelViewerTextPage` / `runModelViewerSoundDemo` at `0x800CA638`/`0x800CA714`/`0x800CADB8` are a different overlay, not a name collision. Next candidate is `npcProbeDriod`. |
| s1677 | Confirmed `npcProbeDriod` (`0x800CABD4`, size `0x11CC`) was already synchronized: companion mission mapping (keep the `Driod` typo), live generated 6-way probe-droid update (`updateProbeDroidHopState` ×3, `initProbeDroidScatterLaunch`, `createAndInitObject`, `dealDamageToNpc`, `spawnDestructionEffectBurst`), exact `0x800CA720`/`0x800CBDA0` boundaries, TOML name and size, and section-4 span agreed. Menu-overlay `runModelViewerSoundDemo` / `loadModelViewerModels` / `shutdownModelViewer` at `0x800CADB8`/`0x800CB604`/`0x800CBB30` are a different overlay, not a name collision. Next candidate is `func_800CBDA0` / `findNearestNpcWithinRange`. |
| s1678 | Synchronized `findNearestNpcWithinRange` (`0x800CBDA0`, size `0x29C`) after companion mission mapping, live generated nearest-NPC-in-range body (`getPlayerField2`, `getNpcContextField8`, `findActiveNpcInSlotChain`, `vec3Length` ×2, `c.lt.s` range reject, `getNpcContextByIndex`, `lookupHmtTextureByName`, `revalidateNpcSlotIterator`; two `tickCinematicEffectObject` callers), exact `0x800CABD4`/`0x800CC03C` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `appendNodeToListHead` / `tickMultiPartVoiceLine` / `mallocVoiceLineStruct` / `setVoiceLineLoopFlag` at `0x800CBDC4`/`0x800CBE00`/`0x800CBF60`/`0x800CC02C` are a different overlay, not a name collision. Next candidate is `func_800CC03C` / `initActorFromSpawnTemplate`. |
| s1679 | Synchronized `initActorFromSpawnTemplate` (`0x800CC03C`, size `0x11C`) after companion mission mapping, live generated spawn-template actor-init body (`setNpcHealth`, `setObjectDetailLevel`, `initActorMotionParams`, `initObjectAnimSubstruct`, `setEffectIntensity`; state byte `+0xE6` = 4/3 on fail), exact `0x800CBDA0`/`0x800CC158` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `setVoiceLineLoopFlag` / `fake_func_800CC038` / `loadMedalInfo` / `getMissionMedal` at `0x800CC02C`/`0x800CC038`/`0x800CC040`/`0x800CC070` are a different overlay, not a name collision. Next candidate is `func_800CC158` / `tickActorTexturedSoundEffect`. |
| s1680 | Synchronized `tickActorTexturedSoundEffect` (`0x800CC158`, size `0x154`) after companion mission mapping, live generated textured-sound-effect tick body (`lookupHmtTextureByName` on `0x800A6D60`/`0x800A6D64`, `setObjectSubstructF10IfReady`, `tickProgressChannel`, `getObjectNpcTypeId`, `triggerCueWithSlotEffect`, `slotDispatcherIter`, `play3DSoundEvent`), exact `0x800CC03C`/`0x800CC2AC` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `calculatePlayerRank` / `getMedalInfo` at `0x800CC1A8`/`0x800CC200` are a different overlay, not a name collision. Next candidate is `func_800CC2AC` / `tickAtAtBodyTransform`. |
| s1681 | Synchronized `tickAtAtBodyTransform` (`0x800CC2AC`, size `0x70C`) after companion mission mapping, live generated AT-AT body-transform tick (`isPendingChildNpcActive`, `computeActorAnchorDeltaAfterLOS`, `getObjectMeshTransformOrLocal`, `computeAnchorRelativePositionByDistanceRatio`, `mat34CrossRowsAndCopyPos`, `mat3x3InverseInto`, `transformVec3ByMat34`, `buildRotationMatrixSlot0`/`Slot1`, `composeRotationMatrixSlot1`, `quatFromAxisAngle`, `rotateVec3ByQuat`, `play3DSoundEventVariant`), exact `0x800CC158`/`0x800CC9B8` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `compareStatstoMedalInfo` / `calculateShotAccuracy` / `fake_func_800CC3D4` at `0x800CC2B0`/`0x800CC374`/`0x800CC3D4` are a different overlay, not a name collision. After this session the last-15 titles were all sweep-scoped, so s1682 was the mandatory retail-entry revisit. |
| s1682 | Rice C/L/R and D-pad on the arrived 640 B-frontend (`1024→640` ~96 s, origin `0x00696100`/`0x00696600`). All 11 arms passed whole-RDRAM, B-pad, hangar, and 640-arrival controls. Presses at 105/115 delivered the expected pad words. Every candidate matched hold: `640→512` attract at 117.7 s (`0x00690400`/`800`), viewer PC 0, hangar-frame 59–62. `0x80000B70` = 1 on hold and every candidate (post-timeout attract path, not the 105/115 press). H2 selected; H1/H3/H4 rejected. First 160 s batch died at the known ~135 s Rice crash before PC flush; `--secs 125` flush exited rc=0. Remaining retail-entry lead is attract-512 input. Next sweep candidate is `func_800CC9B8` / `tickAtAtAudioAndWeaponState`. |
| s1683 | Synchronized `tickAtAtAudioAndWeaponState` (`0x800CC9B8`, size `0x164`) after companion mission mapping, live generated AT-AT audio/weapon-state tick (`clearModelAnimChannelEntry`, `releaseModelAnimSlot`, `play3DSoundEvent`, `initActorRenderDescriptorWithNpcVelocity`, `flattenAnimTreeAndAllocateSlot`, `markModelAnimChannelEntryActive`, `setModelAnimSlotCycleDuration`), exact `0x800CC2AC`/`0x800CCB1C` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `fake_func_800CC3D4` at `0x800CC3D4` is a different overlay, not a name collision. Next candidate is `func_800CCB1C` / `processAtAtSubFeatureSlot`. |
| s1684 | Synchronized `processAtAtSubFeatureSlot` (`0x800CCB1C`, size `0x17C`) after companion mission mapping, live generated AT-AT sub-feature slot tick (`lookupHmtTextureByName` on stack name `sf`+(`'1'`+byte `+0x6E`), `findActiveNpcInSlotChain`, `getNpcContextField8`, range test vs scaled `+0x54`, `slotDispatcherIter` type 9, `revalidateNpcSlotIterator`, `+0x6E` modulo-4), exact `0x800CC9B8`/`0x800CCC98` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay `fake_func_800CC3D4` at `0x800CC3D4` is a different overlay, not a name collision. Next candidate is `func_800CCC98` / `npcAtAtHandleDestruction`. |
| s1685 | Synchronized `npcAtAtHandleDestruction` (`0x800CCC98`, size `0x6F4`) after companion mission mapping, live generated AT-AT destruction body (`spawnNpcType0xAFromTemplate` ×2, `spawnByteAnimDebrisDefault` ×2, `spawnDebris1Npc` ×2, `spawnOrientedNpc` ×4, `composeRandomRotationMatrix` ×2, `scaleVec3ByRandomRange` ×2, `rand_recomp` ×6, `play3DSoundEvent` ×2, `spawnDestructionEffectBurst`), exact `0x800CCB1C`/`0x800CD38C` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu-overlay data `D_800CCCB0`/`D_800CCD10`/`D_800CD184` at the same VRAM window is a different overlay, not a name collision. Next candidate is `func_800CD38C` / `spawnAtAtFootstepDustBurst`. |
| s1686 | Synchronized `spawnAtAtFootstepDustBurst` (`0x800CD38C`, size `0x1CC`) after companion mission mapping, live generated footstep-dust-burst body (`isTerrainCellBlockedAtWorldXz`, `spawnRandomBurstNpcVariantWrapper`), exact `0x800CCC98`/`0x800CD558` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Exclusive callers are two `updateAtAtLegArticulation` sites. Menu-overlay data at the same VRAM window is a different overlay, not a name collision. Next candidate is `func_800CD558` / `updateAtAtLegArticulation`. |
| s1687 | Synchronized `updateAtAtLegArticulation` (`0x800CD558`, size `0x1C4`) after companion mission mapping, live generated AT-AT leg-stride body (`lookupHmtTextureByName` on `0x800A6DCC`, `computeWalkerLimbStrideTargets`, scale by `*(0x800A6EC8)`, loop-3 of `wrapAngleToCyclicRange` + `spawnAtAtFootstepDustBurst` ×2), exact `0x800CD38C`/`0x800CD71C` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Exclusive caller is `npcAtAtUpdate` at `0x800CE378`. Menu-overlay hangar data at the same VRAM window is a different overlay, not a name collision. Next candidate is `npcAtAtUpdate`. |
| s1688 | Confirmed `npcAtAtUpdate` (`0x800CD71C`, size `0x1800`) was already synchronized: companion mission mapping, live generated 9-way AT-AT update (`tickAtAtAudioAndWeaponState`, `tickAtAtBodyTransform`, `processAtAtSubFeatureSlot`, `updateAtAtLegArticulation`, `npcAtAtHandleDestruction`), exact `0x800CD558`/`0x800CEF1C` boundaries, TOML name and size, and section-4 span agreed. Menu-overlay hangar/bridge data at the same VRAM window is a different overlay, not a name collision. Next candidate is `fake_func_800CEF1C` / `func_800CEF20` / `advanceAtStEffectPhaseSound`. |
| s1689 | Confirmed `fake_func_800CEF1C` (`0x800CEF1C`, size `0x4`) was already classified as the explicit 4-byte leftover store (`sw $s1, 0x44($sp)`) between `npcAtAtUpdate` and `advanceAtStEffectPhaseSound`: companion mapping, live generated fragment, exact `0x800CD71C`/`0x800CEF20` boundaries, TOML name and size, and section-4 span agreed. No menu function occupies the address. Next candidate is `func_800CEF20` / `advanceAtStEffectPhaseSound`. |
| s1690 | Synchronized `advanceAtStEffectPhaseSound` (`0x800CEF20`, size `0x17C`) after companion mission mapping, live generated AT-ST effect-phase sound body (`+0x7E` phase 0/1/2 tables, progress wrap, `play3DSoundEvent` type 5/6; callers `advanceAtStDeathAnimPhase`/`npcAtStUpdate`), exact `0x800CEF1C`/`0x800CF09C` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. No menu function occupies the address. Next candidate is `func_800CF09C` / `tickAtStCannonFireEffect`. |
| s1691 | Synchronized `tickAtStCannonFireEffect` (`0x800CF09C`, size `0x170`) after companion mission mapping, live generated AT-ST cannon-fire effect tick (`lookupHmtTextureByName` on `0x800A700C`/`0x800A7010`, `setObjectSubstructF10IfReady`, `resolveNpcAttachmentPos`, `generatePerpEmitDirectionWithJitter`, `tickProgressChannel`, `triggerCueWithSlotEffect` type 3, `play3DSoundEvent` type `0xD`), exact `0x800CEF20`/`0x800CF20C` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. No menu function occupies the address. Next candidate is `func_800CF20C` / `updateAtStBodyKinematics`. |
| s1692 | Synchronized `updateAtStBodyKinematics` (`0x800CF20C`, size `0x68C`) after companion mission mapping, live generated AT-ST body-kinematics tick (`isPendingChildNpcActive`, `computeActorAnchorDeltaAfterLOS`, `getObjectMeshTransformOrLocal`, `mat34CrossRowsAndCopyPos`, `mat3x3InverseInto`, `transformVec3ByMat34`, `vec3NormalizeInto`, `buildRotationMatrixSlot0`/`Slot1`, `composeRotationMatrixSlot1`, `vec3Dot` ×6, `vec3Length` ×8, `vec3Cross` ×4, `constMinusSinfApprox` ×6, `quatFromAxisAngle` ×2, `rotateVec3ByQuat` ×2, `play3DSoundEventVariant` ×2, `factor5RemoveListNode`; exclusive caller `npcAtStUpdate` at `0x800D0820`), exact `0x800CF09C`/`0x800CF898` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu m2c `func_800CF20C` in hangar/save files is data on a different overlay, not a name collision. Next candidate is `func_800CF898` / `npcAtStHandleDestruction`. |
| s1693 | Synchronized `npcAtStHandleDestruction` (`0x800CF898`, size `0x474`) after companion mission mapping, live generated AT-ST walker-destruction body (`clearModelAnimChannelEntry`, `releaseModelAnimSlot`, `spawnNpcType0xAFromTemplate`, `spawnByteAnimDebrisDefault`, `spawnOrientedNpc` ×2, `spawnDestructionEffectBurst`, `rand_recomp` ×4, `composeRandomRotationMatrix`, `scaleVec3ByRandomRange`, `spawnDebris1Npc`, `spawnSplineWalkerCraft`; exclusive caller `npcAtStUpdate` at `0x800D0DAC` after `dealDamageToNpc` `<= 0`), exact `0x800CF20C`/`0x800CFD0C` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu m2c `func_800CF898` in `func_800B47C4` is hangar/controller data on a different overlay, not a name collision. Next candidate is `func_800CFD0C` / `advanceAtStDeathAnimPhase`. |
| s1694 | Synchronized `advanceAtStDeathAnimPhase` (`0x800CFD0C`, size `0x170`) after companion mission mapping, live generated AT-ST death-anim phase-advance body (`clearModelAnimChannelEntry`, `releaseModelAnimSlot`, `+0xAB` 1/2/3 → `+0x7E` 2/1/0 tables, `flattenAnimTreeAndAllocateSlot`, `markModelAnimChannelEntryActive`, `setModelAnimSlotCycleDuration`, `advanceAtStEffectPhaseSound`; exclusive caller `npcAtStUpdate` at `0x800D0678`/`0x800D06E4`/`0x800D07CC`), exact `0x800CF898`/`0x800CFE7C` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Menu concert-hall bytes at `0x800CFE3D`/`0x800CFE3E` are a different overlay, not a name collision. Next candidate is `npcAtStUpdate`. |
| s1695 | Confirmed `npcAtStUpdate` (`0x800CFE7C`, size `0x120C`) was already synchronized: companion mission mapping, live generated 9-way AT-ST update (`advanceAtStDeathAnimPhase` ×3, `advanceAtStEffectPhaseSound`, `updateAtStBodyKinematics`, `npcAtStHandleDestruction`), exact `0x800CFD0C`/`0x800D1088` boundaries, TOML name and size, and section-4 span agreed. Menu concert-hall/medal data at the same VRAM window is a different overlay, not a name collision. Next candidate is `playerAtStInit`. |
| s1696 | Confirmed `playerAtStInit` (`0x800D1088`, size `0x1C0`) was already synchronized: companion mission mapping, live generated player-AT-ST-init body (`initPlayerCraftMovementMode`, `refreshPlayerSecondaryWeaponHud`, craft record `0x80137DBC`), exact `0x800CFE7C`/`0x800D1248` boundaries, TOML name and size, and section-4 span agreed. Menu concert-hall/medal data at the same VRAM window is a different overlay, not a name collision. Next candidate is `func_800D1248` / `spawnPlayerAtStCannonFire`. |
| s1697 | Synchronized `spawnPlayerAtStCannonFire` (`0x800D1248`, size `0x330`) after companion mission mapping, live generated player-AT-ST cannon-fire body (`lookupHmtTextureByName` on `0x800A700C`/`0x800A7010`, `acquireNpcTargetsInAimCone`, `dispatchCueByCategory`, `play3DSoundEvent` type `0xD`), exact `0x800D1088`/`0x800D1578` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. Exclusive caller is `updatePlayerAtStBehavior` at `0x800D213C`. No menu function occupies the address. After this session the last-15 titles are all sweep-scoped, so s1698 is the mandatory retail-entry revisit. |
| s1698 | Rice A/Start/Z/C/L/R/D-pad on attract 512 (`640→512` ~117.7 s, origin `0x00690400`/`800`). All 14 arms passed whole-RDRAM, B-pad, hangar, 640-arrival, and attract-arrival controls; `--secs 125` flush rc=0. Presses at 119/123 delivered the expected pad words. H3 A/Start/C-up/L: `512→1024` at 126.4 s origin `0x00790400`/`800`; viewer 0; B70=1 matching hold; 1024 destination unevaluable. H2 Z/C-down/C-left/C-right/R/D-pad: still attract 512 through 125.8 s. H1 rejected (no mission VI; B70 not elevated). Z-on-attract 128.3 s remains single-source. Next sweep candidate is `func_800D1578` / `advancePlayerAtStLocomotion`. |
| s1699 | Synchronized `advancePlayerAtStLocomotion` (`0x800D1578`, size `0x1B8`) after companion mission mapping, live generated player-AT-ST locomotion-probe body (`wrapAngleToCyclicRange`, `findActiveNpcInSlotChain`, `getNpcContextByIndex`, `findSegmentObjectSphereHit`, `revalidateNpcSlotIterator`; exclusive callers `updatePlayerAtStBehavior` at `0x800D189C`/`0x800D1A44`), exact `0x800D1248`/`0x800D1730` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. No menu function occupies the address. Next candidate is `func_800D1730` / `updatePlayerAtStBehavior`. |
| s1700 | Synchronized `updatePlayerAtStBehavior` (`0x800D1730`, size `0xAD8`) after companion mission mapping, live generated player-AT-ST behavior-tick body (`advancePlayerAtStLocomotion` ×2, `quatFromAxisAngle`, `rotateVec3ByQuat` ×2, `orthonormalizeFrameAndSnapToZero`, `play3DSoundEvent` ×2, `setModelAnimSlotCycleDuration` ×2, `seekAllModelAnimChannelsInSlotToTime`, `wrapAngleToCyclicRange`, `spawnPlayerAtStCannonFire`; exclusive caller `playerAtStUpdate` at `0x800D2630`), exact `0x800D1578`/`0x800D2208` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. No menu function occupies the address. Next candidate is `playerAtStUpdate`. |
| s1701 | Confirmed `playerAtStUpdate` (`0x800D2208`, size `0x954`) was already synchronized: companion mission mapping, live generated 15-way player-AT-ST update (`playerAtStInit` ×2, `updatePlayerAtStBehavior`, `flattenAnimTreeAndAllocateSlot`, `spawnHeavyMechSubEffect`, `slotDispatcherIter`, `updatePlayerHudFrame`; craft record `0x80137DBC`), exact `0x800D1730`/`0x800D2B5C` boundaries, TOML name and size, and section-4 span agreed. Menu concert-hall/medal data at the same VRAM window is a different overlay, not a name collision. Next candidate is `func_800D2B5C` / `npcInitFromTemplate`. |
| s1702 | Synchronized `npcInitFromTemplate` (`0x800D2B5C`, size `0xFC`) after companion mission mapping, live generated NPC-from-template init (`setNpcHealth`, `initActorMotionParams`, `initObjectAnimSubstruct`, `setObjectDetailLevel`; state byte `+0xFA` = 0/2), exact `0x800D2208`/`0x800D2C58` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. No menu function occupies the address. Next candidate is `func_800D2C58` / `spawnScaledBootVec4Effect`. |
| s1703 | Synchronized `spawnScaledBootVec4Effect` (`0x800D2C58`, size `0x40`) after companion mission mapping, live generated wrapper (`a0=0`, `a1=a2=0x3D400000`, dest `a3=0x8013800C`, stack floats from incoming `a1` and `D_800A73B8`, `jal computeBootConfigScaledVec4`), exact `0x800D2B5C`/`0x800D2C98` boundaries, TOML size, and section-4 span agreed; corrected the stale TOML placeholder. No menu function occupies the address. Next candidate is `fake_func_800D2C98`. |

## Method and safety rules

- A null result is worthless without a positive control in the same run.
- Batch instrumentation and all A/B arms in one build/run; scope budgets to
  the VI phase, and never compare animating scenes by stopwatch.
- Read the Factor 5 reference before interpreting a DL or RDP anomaly.
- Regeneration order is `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated code belong in fixup scripts.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. Changes under `lib/` require patch export.
- Before any mitigation, identify the writer and legitimacy with an
  `ORIGIN:` line.
