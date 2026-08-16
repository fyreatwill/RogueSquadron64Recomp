# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable project
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is
the authority for session detail. Reviewed through s1545 (2026-08-15).

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
  `0x006dd280`. Homebrew Rice (`--video …/mupen64plus-video-rice.dylib`)
  with the eleven-Start schedule is the available later-phase recipe:
  320→640 at ~2.3s, 640→1024 at ~17.2s, 1024→512 hangar origin
  `0x006ab400`/`0x006ab800` at ~38.4s (s707 and s1496). After hangar, extra
  Start or A leaves to 640 / `0x006a2900`/`0x006a2e00` (s1528); the
  eleven-Start hold arm stays at hangar through 100s. s1544: that 640
  phase is still menu-overlay (last `loadOverlay` is menu path
  `0x80000BA8` at 16.9s; mission path `0x80000B70` and `lv0`/`lv1`
  inits stay 0) and is not a cinematic reload (`cinematicLoopBody`
  only at boot 6.9s). Watched hangar frontend PCs
  (`tickCraftSelectScreen`, `handleLevelSelectStartConfirm`,
  `printLevelSelectWeaponText`) run at 512/`0x6ab400` then stop at
  `runHangarMenuFromOverlay` (53s); they do not resume after the
  512→640 edge. Post-settle Start and B reach PIF but do not change
  width, origin, or overlay. The 640 handler is some other
  menu-overlay function; do not name it a mission or LEVEL DESCRIPTION
  without a second independent line. Do not add target watches on a
  dummy-video arm. Glide64MK2 stayed at 320 in s707.
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
  The unresolved issue is the RSP-internal vector numeric origin before
  `vmadh v6,v4,v0`; the oracle cannot watch RSP accumulators.

## Active investigation and ranked next steps

1. Continue the generated-symbol renaming sweep (~1,548 placeholder
   `func_0x...` names remained when counted at s1487; no other stated
   finish line — see `tools/agent/ITERATION.md` strategic-priority item 4
   for the mandatory every-15-sessions revisit of the retail-entry-boundary
   and M4 threads; s1544 was that revisit) with one bounded exact-name
   census over the next adjacent function, `0x800AF668..0x800AF6A8`.
   Synchronize only names independently supported by the companion project,
   generated definitions, sizes, and caller/semantic evidence. Leave
   `func_8008ED6C` address-encoded (s1309 H2), `func_800927B0`
   address-encoded (s1355 H3), `func_80092A54` address-encoded
   (s1357 H3), `func_80092CF0` address-encoded
   (s1359 H3: no independent companion name), `func_80092F10`
   address-encoded (s1360: TOML-only live-tail fragment of
   `resampleVoiceLutSamplesPacked`), `fake_func_80093E74`
   unchanged (s1369: already-fake three-instruction epilogue fragment),
   `fake_func_80094348` unchanged (s1378: already-fake two-instruction
   jump fragment before `startSongSequence`), `fake_func_8009711C`
   unchanged (s1408: already-fake one-instruction jump fragment before
   `resetSongSubsystemCounter`), `fake_func_80097D58`
   unchanged (s1420: already-fake two-instruction epilogue fragment
   before `clearStreamedVoiceFlags`), `fake_func_80099C4C`
   unchanged (s1446 H2: already-fake one-word `beq` gap before
   `transformVec3ByAffineMatrix`), `fake_func_80099FDC`
   unchanged (s1451 H2: already-fake one-word `bne` gap before
   `aspMainTextStart` at `0x80099FE0`; overlay `0xF84` is the
   misparsed RSP text lump, not a CPU function),
   `fake_func_8009C2C8` unchanged (s1471 H2: already-fake
   two-instruction COP1 multiply-accumulate fragment before
   `computeVoicePanCoefficients`), `fake_func_8009D7CC`
   unchanged (s1476 H2: already-fake one-instruction `mtc1 $zero, $f4`
   fragment before `filterVoiceSampleBlock`), `func_8009D8BC`
   unchanged (s1477: eight-byte PC-relative packed-nibble table
   `C7 D7 E3 E7 F1 F3 F5 F7`, not a function), and `func_8009D978`
   unchanged (s1478: eight-byte PC-relative Q15 delay-mix table
   `0CCD 2CCD 5333 7FFF`, not a function). s1479 synchronized
   `runVoiceLatticeFilter` at `0x8009D980`. s1480 synchronized
   `renderVoiceAudioBlock` at `0x8009DB44`. s1481 synchronized
   `audioMixStereoBlock8` at `0x8009DC98`. s1482 synchronized
   `audioMixSampleS16_1_3` at `0x8009DD3C`. s1483 synchronized
   `audioMixSampleS16_1_1` at `0x8009DD54`. s1484 synchronized
   `audioMixSampleS16_3_1` at `0x8009DD64`. s1485 synchronized
   `audioCompandS16` at `0x8009DD7C`. s1486 synchronized
   `cinematicLoopBody` at `0x800A5D80`. s1487 confirmed already-
   matching `load_cutscene` at `0x800A6620` (H1; generated, companion,
   and TOML already agree; overlay `rom_size` `0x2E4` matches the live
   body). s1488 synchronized `cinematicSlotUpdate` at `0x800A6904`.
   s1489 synchronized `setupCutsceneLevel` at `0x800A6CE4`.
   s1490 synchronized `initCinematicDispatchSlots` at `0x800A6FC0`.
   s1491 synchronized `cinematicSlotBatchDispatch` at `0x800A70E4`.
   s1492 synchronized `slotEffectHandlerDispatch` at `0x800A71B8`.
   s1493 synchronized `cutscenePopulateSlotsFromLevelLists` at
   `0x800A73E4`. s1494 synchronized `cinematicSlotDispatcher` at
   `0x800A76B8`. s1495 synchronized `spawnCutsceneObjectsFromList`
   at `0x800A7C4C`. s1497 synchronized `cutsceneDispatchSlotsByFlag`
   at `0x800A8420`. s1498 synchronized `spawnCutsceneEffectsAndCues`
   at `0x800A89B0`. s1499 synchronized `initCutsceneAudioChannels`
   at `0x800A959C`. s1500 synchronized `initCutsceneScene` at
   `0x800A98AC`. s1501 synchronized `initSceneForMission` at
   `0x800A9ABC`. s1502 synchronized `emit3DSoundsForActiveNpcs` at
   `0x800A9D70`. s1503 synchronized `updatePositionalAudioSource` at
   `0x800AA1BC`. s1504 synchronized
   `applyCutsceneSlotMaterialOverrides` at `0x800AA4F4`. s1505
   synchronized `tickCutsceneActionSlots` at `0x800AA658`. s1506
   synchronized `applyNamedEffectParameterDefaults` at `0x800AA850`.
   s1507 synchronized `spawnCutsceneDebrisField` at `0x800AAC88`.
   s1508 synchronized `npcIncomingMissileUpdate` at `0x800ABD0C`.
   s1509 synchronized `buildCutsceneGradientBuffers` at
   `0x800AC574`. s1510 synchronized `spawnNpcBurstAlongSegment` at
   `0x800AC75C`. s1511 synchronized `processCutsceneActions` at
   `0x800ACE8C`. s1513 synchronized `computeCutsceneScreenScale` at
   `0x800AD224`. s1514 synchronized `tickCutsceneCameraFromTimeline`
   at `0x800AD690`. s1515 synchronized
   `transformAndNormalizeDirectionByMatrix` at `0x800ADBF8`. s1516
   synchronized `loadBackdropAsset` at `0x800ADF74`. s1517
   synchronized `initCinematicSceneAssets` at `0x800AE518`. s1518
   synchronized `dispatchCinematicFromMainLoop` at `0x800AE878`.
   s1519 synchronized `shouldShowCutsceneForLevelStage` at
   `0x800AE928`. s1520 synchronized `getAssetNameForNpcType` at
   `0x800AE98C`. s1521 synchronized `getCutsceneRuntimeContext` at
   `0x800AEA18`. s1522 synchronized `noopHandler_800AEB30` at
   `0x800AEB30`. s1523 synchronized `freeCutsceneResources` at
   `0x800AEB38`. s1524 synchronized `resetCutsceneActionSlots` at
   `0x800AEB7C`. s1525 synchronized `scheduleCutsceneActionSlot`
   at `0x800AEBD0`. s1526 synchronized
   `composeInterpolatedNodeMatricesAlt` at `0x800AEC48`. s1527
   synchronized `tickCutsceneNpcSlots` at `0x800AEE14`. s1529
   synchronized `despawnCutsceneNpcSlot` at `0x800AEF30`. s1530
   synchronized `initCutsceneSlotTable` at `0x800AEFC8`. s1531
   synchronized `insertCutsceneSlot` at `0x800AEFF0`. s1532
   synchronized `lookupCutsceneIdMapping` at `0x800AF03C`. s1533
   synchronized `destroyAllNpcsInSlotChain` at `0x800AF08C`. s1534
   synchronized `maybeLoadYwingCutscene` at `0x800AF0EC`. s1535
   synchronized `buildBobbingObjectMatrix` at `0x800AF164`. s1536
   synchronized `cinematicShutdownAudioAndAssets` at `0x800AF260`.
   s1537 synchronized `bytesDiffer` at `0x800AF284`.
   s1538 synchronized `matchKeywordWithPriority` at
   `0x800AF2C8`. s1539 synchronized `cinematicComputeDt` at
   `0x800AF360`. s1540 synchronized `cinematicInitializer` at
   `0x800AF408`. s1541 synchronized `isCinematicActive` at
   `0x800AF540`. s1542 synchronized `cinematicStageAdvancer` at
   `0x800AF550`. s1543 synchronized `cinematicDeactivator`
   at `0x800AF60C`. s1545 synchronized
   `getCinematicStateSubObject` at `0x800AF65C`.
   The generated entry at `0x800AF668` is already
   `cinematicInterpRatio`; the companion cinematic list
   maps `cinematicInterpRatio = 0x800AF668` (comment:
   computes interpolation ratio from byte counter / float
   threshold). TOML is still `func_800AF668` (size `0x40`,
   ends at already-fake generated `fake_func_800AF6A8` /
   TOML `fake_func_800AF6A8` at `0x800AF6A8`). Overlay
   `rom_size` is `0x40` at offset `0x0000A538`. Confirm the
   complete live function, matching size, and caller/semantic
   evidence before synchronizing the TOML name. Independently
   named `getCinematicStateSubObject` at `0x800AF65C`
   (`rom_size` `0xC`) ends at this address. The generated
   body loads `MEM_W(0x800B0934)`, early-outs if that
   cinematic state pointer is null, otherwise loads the
   sub-object at `state+0xC`, reads the byte at `+0x2F`,
   converts it to float, divides by a float threshold, and
   subtracts from a second float constant. Last live
   instruction pair is `0x800AF6A0`/`0x800AF6A4` (`jr $ra` /
   `mov.s $f0, $f4`). Generated caller is independently
   named `cinematicLoopBody` at `0x800A607C`. Menu-overlay
   `tickCraftSelectScreen` / TOML `func_800AF3C0` at
   `0x800AF3C0` (`rom_size` `0x2EC`, ends `0x800AF6AC`)
   occupies overlapping VRAM from `.ovl.menu` and is not a
   cinematic size split. Mission-overlay `tickCutsceneObject`
   at `0x800AF04C` continues
   `playCutsceneObjectImpactSound` / TOML `func_800AEF58` at
   `0x800AEF58` (size `0xF4`, ends `0x800AF04C`) and likewise
   overlaps from `.ovl.mission`.
2. Future oracle work on the 640/`0x6a2900` handler, a later mission
   watch, or a new M4 RDRAM dest (a DMEM→RDRAM transfer that is not
   `0xD60`) must use the Rice `--video` recipe above, not dummy video.
   s1544 closed the "is 640 a mission / cinematic / hangar tick loop?"
   table: menu overlay stays resident, mission and cinematic paths stay
   quiet, and the hangar tick set stops at `runHangarMenuFromOverlay`.
   The remaining 640 question is which menu-overlay function runs after
   that return. Extra A or extra Start after the eleven-Start hangar
   window still selects 640/`0x6a2900`; post-settle Start and B do not
   leave it. Physical `0x130B10:0x130B58` is written at hangar and at
   leave (`runHangarMenuFromOverlay` `0x800c68d0`). Pass whole-RDRAM,
   PIF, and VI positive controls in the same run. Do not re-watch
   `0x688:0x710`, do not re-audit dummy-video 320-only schedules, and
   do not treat 640/`0x6a2900` as an outdoor mission.
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
DMEM `r9`). The unresolved issue is the RSP-internal numeric origin before
`vmadh v6,v4,v0`, not RT64 lane order and not low-RDRAM ownership.

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
| s1496 | Dummy-vs-Rice revisit: dummy stayed at 320/`0x006dd280`; Rice reached 640, 1024, and hangar 512/`0x006ab400`. |
| s1512 | Rice hangar M4 revisit: whole-RDRAM 10000/removal rc=0, 11 Start/PIF hits, 320→640→1024→512/`0x006ab400`; `0x688:0x710` and `0x04000670:0x04000720` 0 CPU writes. Rejects RDRAM ownership of DMEM `r9`. |
| s1528 | Rice post-hangar A/B: hold stays 512/`0x6ab400`; extra Start or A leaves to 640/`0x6a2900`; `0x130B10:0x130B58` live (s1086 dummy-320 zeros were unevaluable); leave write `0x800c68d0` in `runHangarMenuFromOverlay`. Not an outdoor mission. |
| s1544 | Rice 640-identity revisit: four arms, whole-RDRAM 10000/removal rc=0, 11 Start/PIF, 320→640→1024→512. Leave A reaches 640/`0x6a2900`; post-settle Start/B seen on PIF, no third width. Last overlay load is menu `0x80000BA8` at 16.9s; mission path and `lv0`/`lv1` inits 0. Hangar ticks run 40–52s then `runHangarMenuFromOverlay` at 53s; 0 watched PCs after the 512→640 edge. 640 is still menu-overlay, not mission/cinematic/hangar-tick. |
| s1240–s1268 | Exact companion/generated symbol sweeps synchronized the repository map; explicit fake/address-only entries stayed unchanged. |
| s1269 | Maintenance compaction only; no experiment or code change. |
| s1270 | Exact companion/generated voice-symbol census synchronized nine entries at `0x80086450..0x80086F44`; no build or runtime run. |
| s1271 | Exact companion/generated voice-symbol census synchronized seven entries at `0x80086FC4..0x800880D8`; no build or runtime run. |
| s1272 | Exact companion/generated MusyX voice-symbol census synchronized seven entries at `0x800881F4..0x80088A24`; no build or runtime run. |
| s1273 | Exact companion/generated MusyX voice-symbol census synchronized six entries at `0x80088A8C..0x80089244`; no build or runtime run. |
| s1274 | Exact companion/generated MusyX macro-symbol census synchronized eight entries at `0x80089414..0x800897D4`; no build or runtime run. |
| s1275 | Exact companion/generated MusyX macro-symbol census synchronized seven entries at `0x80089838..0x80089B40`; no build or runtime run. |
| s1276 | Exact companion/generated MusyX macro-symbol census synchronized 13 entries at `0x80089B50..0x8008A014`; no build or runtime run. |
| s1277 | Exact companion/generated MusyX macro-symbol census synchronized six entries at `0x8008A12C..0x8008A6FC`; no build or runtime run. |
| s1278 | Exact companion/generated MusyX macro-symbol census synchronized eight entries at `0x8008A828..0x8008ACB4`; no build or runtime run. |
| s1279 | Exact companion/generated MusyX macro-symbol census synchronized five entries at `0x8008AE50..0x8008B284`; no build or runtime run. |
| s1280 | Exact companion/generated MusyX sequencer-handler census synchronized seven entries at `0x8008B33C..0x8008B8DC`; no build or runtime run. |
| s1281 | Exact companion/generated MusyX voice-symbol census synchronized `refreshVoicePlaybackRate` at `0x8008B9CC` and `soundMacroSetPitchTarget` at `0x8008BA60`; no build or runtime run. |
| s1282 | Exact companion/generated MusyX sequencer census synchronized `tickAudioChannel` at `0x8008BC10` and `tickAllAudioChannels` at `0x8008C9AC`; no build or runtime run. |
| s1283 | Exact companion/generated MusyX sequencer census synchronized `tickAudioSequencerFrame` at `0x8008D960`; no build or runtime run. |
| s1284 | Exact companion/generated MusyX update census synchronized `tickMusyXIfActive` at `0x8008DA00`; no build or runtime run. |
| s1285 | Exact companion/generated MusyX voice census synchronized `releaseSynthVoice` at `0x8008DA4C`; no build or runtime run. |
| s1286 | Exact companion/generated MusyX voice census synchronized `stopVoicesByHandle` at `0x8008DA98`; no build or runtime run. |
| s1287 | Exact companion/generated MusyX voice census synchronized `stopAllSynthVoices` at `0x8008DBF4`; no build or runtime run. |
| s1288 | Exact companion/generated MusyX table-access census synchronized `getMusyXChannelSlotByte` at `0x8008DD20` and `setMusyXChannelSlotByte` at `0x8008DD38`; no build or runtime run. |
| s1289 | Exact companion/generated MusyX gate census synchronized `setMusyXVoiceTickGate` at `0x8008DD50`; no build or runtime run. |
| s1290 | Exact companion/generated MusyX command census synchronized `dispatchAudioCommand` at `0x8008DD60`; no build or runtime run. |
| s1291 | Exact companion/generated MusyX wrapper census synchronized `playSimpleAudioCmd` at `0x8008E0B0`; no build or runtime run. |
| s1292 | Exact companion/generated MusyX volume census synchronized `applyMusicOrSfxVolume` at `0x8008E120`; no build or runtime run. |
| s1293 | Exact companion/generated MusyX fader census synchronized `isAudioFaderRampActive` at `0x8008E1C4`; no build or runtime run. |
| s1294 | Exact companion/generated MusyX fader census synchronized `setupAudioFaderRamp` at `0x8008E218`; no build or runtime run. |
| s1295 | Exact companion/generated MusyX fader census synchronized `setAudioFaderRampLocked` at `0x8008E4E4`; no build or runtime run. |
| s1296 | Exact companion/generated MusyX fader census synchronized `setAudioFaderState` at `0x8008E54C`; no build or runtime run. |
| s1297 | Exact companion/generated audio-slot census synchronized `anyAudioSlotActive` at `0x8008E57C`; no build or runtime run. |
| s1298 | Exact companion/generated MusyX reset census synchronized `resetMusyXEngineState` at `0x8008E614`; no build or runtime run. |
| s1299 | Exact companion/generated MusyX sequencer census synchronized `clearMusyXSequencerState` at `0x8008E85C`; no build or runtime run. |
| s1300 | Exact companion/generated MusyX table-access census synchronized `getMusyXStateTableIfActive` at `0x8008E8B8`; no build or runtime run. |
| s1301 | Exact companion/generated MusyX sync census synchronized `syncMusyXIfActive` at `0x8008E8D8`; no build or runtime run. |
| s1302 | Exact companion/generated MusyX lock census synchronized `runMusyXTaskLocked` at `0x8008E904`; no build or runtime run. |
| s1303 | Exact companion/generated MusyX init census synchronized `initMusyXEngine` at `0x8008E940`; no build or runtime run. |
| s1304 | Exact companion/generated display-mode census synchronized `setDisplayMode` at `0x8008EA14`; no build or runtime run. |
| s1305 | Exact companion/generated display-mode census synchronized `reapplyDisplayMode` at `0x8008EB5C`; no build or runtime run. |
| s1306 | Exact companion/generated MusyX shutdown census synchronized `shutdownMusyXEngine` at `0x8008ECA4`; no build or runtime run. |
| s1307 | Exact companion/generated MusyX wait-teardown census synchronized `musyxNoopStub` at `0x8008ED00`; no build or runtime run. |
| s1308 | Exact companion/generated MusyX getter census synchronized `isMusyXActive` at `0x8008ED5C`; no build or runtime run. |
| s1309 | Overlapping `0x8008ED6C`/`0x8008ED70` census selected H2 for truncated `func_8008ED6C` and H1 for `runAiAudioStreamPlaybackLoop` at `0x8008ED70`; no build or runtime run. |
| s1310 | Exact companion/generated song-tempo census synchronized `buildSongTempoSchedule` at `0x8008EEC0`; no build or runtime run. |
| s1311 | Exact companion/generated song-channel census synchronized `allocateSongChannelArray` at `0x8008F0A0`; no build or runtime run. |
| s1312 | Exact companion/generated song-buffer census synchronized `setupSongRenderBuffers` at `0x8008F2FC`; no build or runtime run. |
| s1313 | Exact companion/generated volume-fade census synchronized `advanceVolumeFadeEnvelope` at `0x8008F4D8`; no build or runtime run. |
| s1314 | Exact companion/generated decode-ring census synchronized `buildSongDecodeBufferRing` at `0x8008F65C`; no build or runtime run. |
| s1315 | Exact companion/generated stream-block census synchronized `acquireSampleStreamBlock` at `0x8008F758`; no build or runtime run. |
| s1316 | Exact companion/generated stream-cache census synchronized `initSampleStreamBlockCache` at `0x8008F858`; no build or runtime run. |
| s1317 | Exact companion/generated stream-cache census synchronized `moveSampleBlockToFront` at `0x8008F95C`; no build or runtime run. |
| s1318 | Exact companion/generated stream-cache census synchronized `recycleSampleStreamBlock` at `0x8008F9C8`; no build or runtime run. |
| s1319 | Exact companion/generated stream-range census synchronized `fillSampleStreamRange` at `0x8008FAAC`; no build or runtime run. |
| s1320 | Exact companion/generated voice-mix census synchronized `musyxRenderVoiceSamples` at `0x8008FFAC`; no build or runtime run. |
| s1321 | Exact companion/generated voice key-on census synchronized `musyxKeyOnVoice` at `0x80090A3C`; no build or runtime run. |
| s1322 | Exact companion/generated voice-mix census synchronized `musyxMixActiveVoices` at `0x80090E04`; no build or runtime run. |
| s1323 | Exact companion/generated voice-cmd census synchronized `musyxBuildVoiceCommandList` at `0x80091034`; no build or runtime run. |
| s1324 | Exact companion/generated synth-frame census synchronized `musyxSynthFrame` at `0x8009123C`; no build or runtime run. |
| s1325 | Exact companion/generated mixer-init census synchronized `initN64RspMixer` at `0x8009189C`; no build or runtime run. |
| s1326 | Exact companion/generated audio-init census synchronized `initAudioSubsystem` at `0x80091B3C`; no build or runtime run. |
| s1327 | Exact companion/generated audio-reconfig census synchronized `reapplyAudioConfig` at `0x80091C88`; no build or runtime run. |
| s1328 | Exact companion/generated audio-shutdown census synchronized `shutdownAudioEngine` at `0x80091D40`; no build or runtime run. |
| s1329 | Exact companion/generated audio-wait census synchronized `waitForMusyXAudioTaskDone` at `0x80091EB0`; no build or runtime run. |
| s1330 | Exact companion/generated mutex-init census synchronized `initFactor5Mutex` at `0x80091FC4`; no build or runtime run. |
| s1331 | Exact companion/generated mutex-acquire census synchronized `factor5MutexAcquire` at `0x80092010`; no build or runtime run. |
| s1332 | Exact companion/generated mutex-release census synchronized `factor5MutexRelease` at `0x8009205C`; no build or runtime run. |
| s1333 | Exact companion/generated mutex-queue census synchronized `factor5QueueBlock` at `0x800920A4`; no build or runtime run. |
| s1334 | Exact companion/generated mutex-queue census synchronized `factor5QueueSignal` at `0x800920D0`; no build or runtime run. |
| s1335 | Exact companion/generated audio-slot census synchronized `isAudioSlotActive` at `0x800920FC`; no build or runtime run. |
| s1336 | Exact companion/generated audio-stub census synchronized `audioStubReturnZero` at `0x80092120`; no build or runtime run. |
| s1337 | Exact companion/generated voice-init census synchronized `musyxInitVoiceFromSample` at `0x80092128`; no build or runtime run. |
| s1338 | Exact companion/generated voice-release census synchronized `musyxStartVoiceRelease` at `0x80092274`; no build or runtime run. |
| s1339 | Exact companion/generated ADSR-store census synchronized `musyxStoreVoiceAdsrParams` at `0x800922C4`; no build or runtime run. |
| s1340 | Exact companion/generated voice-attack census synchronized `musyxTriggerVoiceAttack` at `0x8009231C`; no build or runtime run. |
| s1341 | Exact companion/generated voice-stop census synchronized `musyxStopVoice` at `0x80092368`; no build or runtime run. |
| s1342 | Exact companion/generated audio-noop census synchronized `noopHandler_80092388` at `0x80092388`; no build or runtime run. |
| s1343 | Exact companion/generated pitch-bend census synchronized `musyxSetVoicePitchBend` at `0x80092390`; no build or runtime run. |
| s1344 | Exact companion/generated voice-mod census synchronized `setVoiceModulationParams` at `0x800923E4`; no build or runtime run. |
| s1345 | Exact companion/generated voice-stop census synchronized `stopVoiceMarkRetrigger` at `0x8009244C`; no build or runtime run. |
| s1346 | Exact companion/generated voice-fade census synchronized `beginVoiceFadeRelease` at `0x80092490`; no build or runtime run. |
| s1347 | Exact companion/generated voice-slot census synchronized `deactivateVoice` at `0x800924F0`; no build or runtime run. |
| s1348 | Exact companion/generated audio-tick census synchronized `tickAudioBufferUpdate` at `0x80092510`; no build or runtime run. |
| s1349 | Exact companion/generated audio-scratch census synchronized `freeAudioScratchBuffer` at `0x80092530`; no build or runtime run. |
| s1350 | Exact companion/generated voice-field census synchronized `getVoiceUserField` at `0x80092564`; no build or runtime run. |
| s1351 | Exact companion/generated cache-writeback census synchronized `writebackDCacheHalfwords` at `0x80092588`; no build or runtime run. |
| s1352 | Exact companion/generated halfword-copy census synchronized `copyFourHalfwordsWriteback` at `0x800925A8`; no build or runtime run. |
| s1353 | Exact companion/generated SND-pointer census synchronized `relocateSndPointer` at `0x800925F4`; no build or runtime run. |
| s1354 | Exact companion/generated voice-resample census synchronized `resampleVoicePointTableSamples` at `0x8009264C`; no build or runtime run. |
| s1355 | Exact companion/generated census selected H3 for `func_800927B0` at `0x800927B0` (complete `0x124` inner kernel; no independent name); left address-encoded; no build or runtime run. |
| s1356 | Exact companion/generated voice-resample census synchronized `resampleVoiceLutSamples` at `0x800928D4`; no build or runtime run. |
| s1357 | Exact companion/generated census selected H3 for `func_80092A54` at `0x80092A54` (complete `0x154` inner LUT kernel; no independent name); left address-encoded; no build or runtime run. |
| s1358 | Exact companion/generated voice-resample census synchronized `resampleVoiceConstantSamples` at `0x80092BA8`; no build or runtime run. |
| s1359 | Exact companion/generated census selected H3 for `func_80092CF0` at `0x80092CF0` (complete `0x158` inner constant-s16 kernel; no independent name); left address-encoded; no build or runtime run. |
| s1360 | Exact companion/generated voice-resample census synchronized `resampleVoiceLutSamplesPacked` at `0x80092E48`; left `func_80092F10` address-encoded (TOML-only live tail); no build or runtime run. |
| s1361 | Exact companion/generated voice-resample census synchronized `packFourLutResampledSamples` at `0x80092F94`; no build or runtime run. |
| s1362 | Exact companion/generated voice-copy census synchronized `copyVoiceSamplesS16` at `0x8009314C`; no build or runtime run. |
| s1363 | Exact companion/generated voice-copy census synchronized `copyVoiceSamplesLut` at `0x800932C4`; no build or runtime run. |
| s1364 | Exact companion/generated audio-buffer census synchronized `zeroAudioBufferWords` at `0x800934A4`; no build or runtime run. |
| s1365 | Exact companion/generated ADPCM census synchronized `decodeAdpcmSampleBlock` at `0x800934D0`; no build or runtime run. |
| s1366 | Exact companion/generated PCM expand census synchronized `expandBytesToPcm16ViaTable` at `0x80093D10`; no build or runtime run. |
| s1367 | Exact companion/generated math-primitive census synchronized `truncDouble` at `0x80093E54`; no build or runtime run. |
| s1368 | Exact companion/generated math-primitive census synchronized `ceilDouble` at `0x80093E60`; no build or runtime run. |
| s1369 | Exact companion/generated math-primitive census synchronized `sqrtf_recomp` at `0x80093E6C`; left `fake_func_80093E74` unchanged; no build or runtime run. |
| s1370 | Exact companion/generated MusyX note-rate census synchronized `musyxComputeNotePlaybackRate` at `0x80093E80`; no build or runtime run. |
| s1371 | Exact companion/generated mixer-divisor census synchronized `divideByMixerBaseFrequency` at `0x80093F18`; no build or runtime run. |
| s1372 | Exact companion/generated fixed-point-scale census synchronized `scaleFixedPointByRatioA` at `0x80093F3C`; no build or runtime run. |
| s1373 | Exact companion/generated fixed-point-scale census synchronized `scaleFixedPointByRatioB` at `0x80093F60`; no build or runtime run. |
| s1374 | Exact companion/generated pitch-table census synchronized `scaleByPitchTableA` at `0x80093F84`; no build or runtime run. |
| s1375 | Exact companion/generated pitch-table census synchronized `scaleByPitchTableB` at `0x80093FB4`; no build or runtime run. |
| s1376 | Exact companion/generated note-rate census synchronized `computeNoteRatePairFromTableA` at `0x80093FE4`; no build or runtime run. |
| s1377 | Exact companion/generated note-rate census synchronized `computeNoteRatePairFromTableB` at `0x8009405C`; no build or runtime run. |
| s1378 | Exact companion/generated voice-pan census synchronized `computeVoiceVolumePanCoefficients` at `0x800940D4`; left `fake_func_80094348` unchanged; no build or runtime run. |
| s1379 | Exact companion/generated song-start census synchronized `startSongSequence` at `0x80094350`; no build or runtime run. |
| s1380 | Exact companion/generated song-track census synchronized `stepActiveSongTracks` at `0x80094958`; no build or runtime run. |
| s1381 | Exact companion/generated song-event census synchronized `tickScheduledSongEvents` at `0x80094DB4`; no build or runtime run. |
| s1382 | Exact companion/generated song-pitch-bend census synchronized `stepSongPitchBendLanes` at `0x80094EE4`; no build or runtime run. |
| s1383 | Exact companion/generated song-modulation census synchronized `stepSongModulationLanes` at `0x80095090`; no build or runtime run. |
| s1384 | Exact companion/generated song-region census synchronized `advanceSongRegion` at `0x80095244`; no build or runtime run. |
| s1385 | Exact companion/generated song-tempo census synchronized `updateSongTempoTickRate` at `0x800955B0`; no build or runtime run. |
| s1386 | Exact companion/generated song-param census synchronized `getSongParamByHandle` at `0x80095700`; no build or runtime run. |
| s1387 | Exact companion/generated song-handle census synchronized `isSongHandleActive` at `0x800957AC`; no build or runtime run. |
| s1388 | Exact companion/generated song-stop census synchronized `stopSongByHandle` at `0x8009582C`; no build or runtime run. |
| s1389 | Exact companion/generated song-stop census synchronized `stopSongByHandleLocked` at `0x80095A94`; no build or runtime run. |
| s1390 | Exact companion/generated song-tick census synchronized `tickSongSequence` at `0x80095ADC`; no build or runtime run. |
| s1391 | Exact companion/generated song-tick census synchronized `tickSongSequenceLocked` at `0x80095D58`; no build or runtime run. |
| s1392 | Exact companion/generated song-tick census synchronized `tickActiveSongs` at `0x80095DA0`; no build or runtime run. |
| s1393 | Exact companion/generated song-pause census synchronized `setSongPauseStateByHandle` at `0x80095DF4`; no build or runtime run. |
| s1394 | Exact companion/generated song-cmd census synchronized `applySongU16ParamCmd` at `0x80095EA8`; no build or runtime run. |
| s1395 | Exact companion/generated song-cmd census synchronized `applySongU16ParamCmdLocked` at `0x80095F94`; no build or runtime run. |
| s1396 | Exact companion/generated song-cmd census synchronized `quiesceSongSlotCmd` at `0x80095FEC`; no build or runtime run. |
| s1397 | Exact companion/generated song-cmd census synchronized `quiesceSongSlotCmdLocked` at `0x800960D0`; no build or runtime run. |
| s1398 | Exact companion/generated song-cmd census synchronized `setSongParamPairCmd` at `0x80096118`; no build or runtime run. |
| s1399 | Exact companion/generated song-cmd census synchronized `setSongParamPairCmdLocked` at `0x8009621C`; no build or runtime run. |
| s1400 | Exact companion/generated song-cmd census synchronized `queueAudioVoiceCmdLocked` at `0x80096284`; no build or runtime run. |
| s1401 | Exact companion/generated song-cmd census synchronized `queueAudioVoiceCmd` at `0x800964C8`; no build or runtime run. |
| s1402 | Exact companion/generated song-getter census synchronized `getSongStateByteByHandle` at `0x80096540`; no build or runtime run. |
| s1403 | Exact companion/generated song-setter census synchronized `setSongChannelParamByHandle` at `0x800965E4`; no build or runtime run. |
| s1404 | Exact companion/generated song-dispatch census synchronized `processSongByHandle` at `0x800966A4`; no build or runtime run. |
| s1405 | Exact companion/generated song-play census synchronized `playSongIfMusyXActive` at `0x80096C88`; no build or runtime run. |
| s1406 | Exact companion/generated song-predicate census synchronized `isSongHandleFree` at `0x80096CE4`; no build or runtime run. |
| s1407 | Exact companion/generated song-tick census synchronized `tickAllActiveSongs` at `0x80096D08`; no build or runtime run. |
| s1408 | Exact companion/generated song-pool census synchronized `initSongSequencerPools` at `0x80097088`; left `fake_func_8009711C` unchanged; no build or runtime run. |
| s1409 | Exact companion/generated song-counter census synchronized `resetSongSubsystemCounter` at `0x80097120`; no build or runtime run. |
| s1410 | Exact companion/generated sound-group census synchronized `bindMacroIdsToSoundGroup` at `0x80097130`; no build or runtime run. |
| s1411 | Exact companion/generated SND-table census synchronized `registerSndMacroTable` at `0x800971E8`; no build or runtime run. |
| s1412 | Exact companion/generated SND-table census synchronized `registerSndCurveTable` at `0x800972A0`; no build or runtime run. |
| s1413 | Exact companion/generated SND-table census synchronized `registerSndSampleTable` at `0x8009735C`; no build or runtime run. |
| s1414 | Exact companion/generated SND-MIDI census synchronized `applySndMidiSetupRecords` at `0x80097430`; no build or runtime run. |
| s1415 | Exact companion/generated SND-MIDI census synchronized `releaseSndMidiSetupRecords` at `0x800974B4`; no build or runtime run. |
| s1416 | Exact companion/generated SND-parse census synchronized `parseSndFiles` at `0x80097518`; no build or runtime run. |
| s1417 | Exact companion/generated SND-unload census synchronized `unloadLastSndFileGroup` at `0x800978EC`; no build or runtime run. |
| s1418 | Exact companion/generated audio-stub census synchronized `returnZeroAudioStub` at `0x80097AC8`; no build or runtime run. |
| s1419 | Exact companion/generated song-play census synchronized `playSongByIdLockCtl` at `0x80097AD0`; no build or runtime run. |
| s1420 | Exact companion/generated song-play census synchronized `playSongById` at `0x80097C2C`; left `fake_func_80097D58` unchanged; no build or runtime run. |
| s1421 | Exact companion/generated streamed-voice census synchronized `clearStreamedVoiceFlags` at `0x80097D60`; no build or runtime run. |
| s1422 | Exact companion/generated streamed-voice census synchronized `serviceStreamedVoices` at `0x80097DA8`; no build or runtime run. |
| s1423 | Exact companion/generated streamed-voice census synchronized `flushStreamedVoiceBuffers` at `0x80097F54`; no build or runtime run. |
| s1424 | Exact companion/generated streamed-voice census synchronized `startStreamedSampleVoice` at `0x80097FE8`; no build or runtime run. |
| s1425 | Exact companion/generated streamed-voice census synchronized `streamSampleCountToByteSize` at `0x800981E4`; no build or runtime run. |
| s1426 | Exact companion/generated voice-mix census synchronized `setVoiceVolumePanLocked` at `0x800981F0`; no build or runtime run. |
| s1427 | Exact companion/generated streamed-voice census synchronized `stopStreamedVoice` at `0x80098298`; no build or runtime run. |
| s1428 | Exact companion/generated 3D-mix census synchronized `compute3DSourceSpatialMix` at `0x80098310`; no build or runtime run. |
| s1429 | Exact companion/generated 3D-mix census synchronized `applyVoice3DMixParams` at `0x8009868C`; no build or runtime run. |
| s1430 | Exact companion/generated 3D-source census synchronized `updateActive3DAudioSource` at `0x800988E8`; no build or runtime run. |
| s1431 | Exact companion/generated 3D-source census synchronized `isAudioVoiceActive` at `0x800989B8`; no build or runtime run. |
| s1432 | Exact companion/generated 3D-source census synchronized `play3DSoundEvent` at `0x800989D8`; no build or runtime run. |
| s1433 | Exact companion/generated 3D-source census synchronized `play3DSoundEventVariant` at `0x80098BDC`; no build or runtime run. |
| s1434 | Exact companion/generated list-unlink census synchronized `factor5RemoveListNode` at `0x80098DE0`; no build or runtime run. |
| s1435 | Exact companion/generated MusyX-gate census synchronized `mostlyMusyxFlagGatedHelper` at `0x80098E84`; no build or runtime run. |
| s1436 | Exact companion/generated 3D-voice census synchronized `tickAndReap3DAudioVoices` at `0x80098EEC`; no build or runtime run. |
| s1437 | Exact companion/generated 3D-spatial census synchronized `setMusyX3DProperties` at `0x80098FA8`; no build or runtime run. |
| s1438 | Exact companion/generated 3D-listener census synchronized `register3DAudioListenerNode` at `0x8009912C`; no build or runtime run. |
| s1439 | Exact companion/generated list-unlink census synchronized `unlinkMusyXListNode` at `0x80099310`; no build or runtime run. |
| s1440 | Exact companion/generated priority-enqueue census synchronized `enqueueSoundInPriorityGroup` at `0x80099394`; no build or runtime run. |
| s1441 | Exact companion/generated spatial-enqueue census synchronized `enqueueSpatialSoundInPriorityGroup` at `0x8009952C`; no build or runtime run. |
| s1442 | Exact companion/generated priority-dispatch census synchronized `dispatchPrioritizedSoundQueue` at `0x80099720`; no build or runtime run. |
| s1443 | Exact companion/generated 3D-frame census synchronized `update3DAudioFrame` at `0x800998E8`; no build or runtime run. |
| s1444 | Exact companion/generated 3D-list census synchronized `reset3DAudioLists` at `0x80099C2C`; no build or runtime run. |
| s1445 | Exact companion/generated audio-noop census synchronized `noopHandler_80099C44` at `0x80099C44`; no build or runtime run. |
| s1446 | Exact companion/generated census selected H2 for already-fake `fake_func_80099C4C` at `0x80099C4C` (one-word `beq` gap); left unchanged; no build or runtime run. |
| s1447 | Exact companion/generated affine-transform census synchronized `transformVec3ByAffineMatrix` at `0x80099C50`; no build or runtime run. |
| s1448 | Exact companion/generated vec3-normalize census synchronized `normalizeVec3` at `0x80099CFC`; no build or runtime run. |
| s1449 | Exact companion/generated vec3-cross census synchronized `crossProductVec3` at `0x80099D68`; no build or runtime run. |
| s1450 | Exact companion/generated orientation-inverse census synchronized `invertOrientationMatrix` at `0x80099DCC`; no build or runtime run. |
| s1451 | Exact companion/generated census selected H2 for already-fake `fake_func_80099FDC` at `0x80099FDC` (one-word `bne` gap before `aspMain` text); left unchanged; no build or runtime run. |
| s1452 | Exact companion/generated voice-slot census synchronized `findVoiceSlotByAge` at `0x8009AF60`; no build or runtime run. |
| s1453 | Exact companion/generated voice-slot census synchronized `allocAndConfigureNewVoice` at `0x8009B048`; no build or runtime run. |
| s1454 | Exact companion/generated voice-slot census synchronized `stopVoiceSlotSynced` at `0x8009B268`; no build or runtime run. |
| s1455 | Exact companion/generated voice-slot census synchronized `stopVoiceByHandle` at `0x8009B33C`; no build or runtime run. |
| s1456 | Exact companion/generated voice-slot census synchronized `isVoiceHandleActive` at `0x8009B3CC`; no build or runtime run. |
| s1457 | Exact companion/generated voice-mix census synchronized `setVoiceMixByKey` at `0x8009B464`; no build or runtime run. |
| s1458 | Exact companion/generated voice-pool census synchronized `serviceVoicePoolFrame` at `0x8009B5A8`; no build or runtime run. |
| s1459 | Exact companion/generated voice-progress census synchronized `getVoicePlaybackProgressByKey` at `0x8009B8A8`; no build or runtime run. |
| s1460 | Exact companion/generated speech-file census confirmed already-matching `loadSpeechFile` at `0x8009BA38` (H1; TOML left unchanged); no build or runtime run. |
| s1461 | Exact companion/generated MusyX voice-table census synchronized `initMusyXVoiceTable` at `0x8009BBA0`; no build or runtime run. |
| s1462 | Exact companion/generated speech-slot census synchronized `findFreeSpeechVoiceSlot` at `0x8009BC88`; no build or runtime run. |
| s1463 | Exact companion/generated MusyX teardown census synchronized `shutdownMusyXVoices` at `0x8009BCC4`; no build or runtime run. |
| s1464 | Exact companion/generated voice-offset census synchronized `accumulateVoiceSampleOffset` at `0x8009BD7C`; no build or runtime run. |
| s1465 | Exact companion/generated voice-DMA census synchronized `dmaVoiceSampleAndSignal` at `0x8009BE08`; no build or runtime run. |
| s1466 | Exact companion/generated voice-slot census synchronized `initMusyXVoiceSlot` at `0x8009BE40`; no build or runtime run. |
| s1467 | Exact companion/generated streamed-voice census synchronized `serviceStreamingVoice` at `0x8009BF14`; no build or runtime run. |
| s1468 | Exact companion/generated voice-consume census synchronized `consumeVoiceSamples` at `0x8009C240`; no build or runtime run. |
| s1469 | Exact companion/generated voice-state census synchronized `advanceVoiceStateToPlaying` at `0x8009C2A0`; no build or runtime run. |
| s1470 | Exact companion/generated voice-state census synchronized `stopVoice` at `0x8009C2BC`; no build or runtime run. |
| s1471 | Exact companion/generated census selected H2 for already-fake `fake_func_8009C2C8` at `0x8009C2C8` (two-instruction COP1 fragment); left unchanged; no build or runtime run. |
| s1472 | Exact companion/generated voice-pan census synchronized `computeVoicePanCoefficients` at `0x8009C2D0`; no build or runtime run. |
| s1473 | Exact companion/generated voice-channel census synchronized `updateVoiceChannelParams` at `0x8009C4E8`; no build or runtime run. |
| s1474 | Exact companion/generated voice-channel census synchronized `updateVoiceChannelParamsLarge` at `0x8009C5BC`; no build or runtime run. |
| s1475 | Exact companion/generated voice-decode census synchronized `decodeAndFillVoiceBlock` at `0x8009C904`; no build or runtime run. |
| s1476 | Exact companion/generated census selected H2 for already-fake `fake_func_8009D7CC` at `0x8009D7CC` (one-instruction `mtc1` fragment); left unchanged; no build or runtime run. |
| s1477 | Exact companion/generated voice-filter census synchronized `filterVoiceSampleBlock` at `0x8009D7D0`; left `func_8009D8BC` as an eight-byte lookup-table pad; no build or runtime run. |
| s1478 | Exact companion/generated voice-delay census synchronized `applyVoiceDelayFilter` at `0x8009D8C4`; left `func_8009D978` as an eight-byte Q15 coefficient pad; no build or runtime run. |
| s1479 | Exact companion/generated voice-lattice census synchronized `runVoiceLatticeFilter` at `0x8009D980`; no build or runtime run. |
| s1480 | Exact companion/generated voice-render census synchronized `renderVoiceAudioBlock` at `0x8009DB44`; no build or runtime run. |
| s1481 | Exact companion/generated stereo-mix census synchronized `audioMixStereoBlock8` at `0x8009DC98`; no build or runtime run. |
| s1482 | Exact companion/generated s16-mix census synchronized `audioMixSampleS16_1_3` at `0x8009DD3C`; no build or runtime run. |
| s1483 | Exact companion/generated s16-mix census synchronized `audioMixSampleS16_1_1` at `0x8009DD54`; no build or runtime run. |
| s1484 | Exact companion/generated s16-mix census synchronized `audioMixSampleS16_3_1` at `0x8009DD64`; no build or runtime run. |
| s1485 | Exact companion/generated s16-compand census synchronized `audioCompandS16` at `0x8009DD7C`; no build or runtime run. |
| s1486 | Exact companion/generated cinematic-loop census synchronized `cinematicLoopBody` at `0x800A5D80`; no build or runtime run. |
| s1487 | Exact companion/generated cinematic-load census confirmed already-matching `load_cutscene` at `0x800A6620` (H1; TOML left unchanged); no build or runtime run. |
| s1488 | Exact companion/generated cinematic-slot census synchronized `cinematicSlotUpdate` at `0x800A6904`; no build or runtime run. |
| s1489 | Exact companion/generated cinematic-setup census synchronized `setupCutsceneLevel` at `0x800A6CE4`; no build or runtime run. |
| s1490 | Exact companion/generated cinematic-dispatch census synchronized `initCinematicDispatchSlots` at `0x800A6FC0`; no build or runtime run. |
| s1491 | Exact companion/generated cinematic-batch census synchronized `cinematicSlotBatchDispatch` at `0x800A70E4`; no build or runtime run. |
| s1492 | Exact companion/generated cinematic-effect census synchronized `slotEffectHandlerDispatch` at `0x800A71B8`; no build or runtime run. |
| s1493 | Exact companion/generated cinematic-slot census synchronized `cutscenePopulateSlotsFromLevelLists` at `0x800A73E4`; no build or runtime run. |
| s1494 | Exact companion/generated cinematic-dispatch census synchronized `cinematicSlotDispatcher` at `0x800A76B8`; no build or runtime run. |
| s1495 | Exact companion/generated cinematic-spawn census synchronized `spawnCutsceneObjectsFromList` at `0x800A7C4C`; no build or runtime run. |
| s1497 | Exact companion/generated cinematic-dispatch census synchronized `cutsceneDispatchSlotsByFlag` at `0x800A8420`; no build or runtime run. |
| s1498 | Exact companion/generated cinematic-spawn census synchronized `spawnCutsceneEffectsAndCues` at `0x800A89B0`; no build or runtime run. |
| s1499 | Exact companion/generated cinematic-audio census synchronized `initCutsceneAudioChannels` at `0x800A959C`; no build or runtime run. |
| s1500 | Exact companion/generated cinematic-scene census synchronized `initCutsceneScene` at `0x800A98AC`; no build or runtime run. |
| s1501 | Exact companion/generated cinematic-scene census synchronized `initSceneForMission` at `0x800A9ABC`; no build or runtime run. |
| s1502 | Exact companion/generated cinematic-audio census synchronized `emit3DSoundsForActiveNpcs` at `0x800A9D70`; no build or runtime run. |
| s1503 | Exact companion/generated cinematic-audio census synchronized `updatePositionalAudioSource` at `0x800AA1BC`; no build or runtime run. |
| s1504 | Exact companion/generated cinematic-material census synchronized `applyCutsceneSlotMaterialOverrides` at `0x800AA4F4`; no build or runtime run. |
| s1505 | Exact companion/generated cinematic-action census synchronized `tickCutsceneActionSlots` at `0x800AA658`; no build or runtime run. |
| s1506 | Exact companion/generated cinematic-effect census synchronized `applyNamedEffectParameterDefaults` at `0x800AA850`; no build or runtime run. |
| s1507 | Exact companion/generated cinematic-spawn census synchronized `spawnCutsceneDebrisField` at `0x800AAC88`; no build or runtime run. |
| s1508 | Exact companion/generated cinematic-NPC census synchronized `npcIncomingMissileUpdate` at `0x800ABD0C`; no build or runtime run. |
| s1509 | Exact companion/generated cinematic-gradient census synchronized `buildCutsceneGradientBuffers` at `0x800AC574`; no build or runtime run. |
| s1510 | Exact companion/generated cinematic-NPC census synchronized `spawnNpcBurstAlongSegment` at `0x800AC75C`; no build or runtime run. |
| s1511 | Exact companion/generated cinematic-action census synchronized `processCutsceneActions` at `0x800ACE8C`; no build or runtime run. |
| s1513 | Exact companion/generated cinematic-scale census synchronized `computeCutsceneScreenScale` at `0x800AD224`; no build or runtime run. |
| s1514 | Exact companion/generated cinematic-camera census synchronized `tickCutsceneCameraFromTimeline` at `0x800AD690`; no build or runtime run. |
| s1515 | Exact companion/generated cinematic-matrix census synchronized `transformAndNormalizeDirectionByMatrix` at `0x800ADBF8`; no build or runtime run. |
| s1516 | Exact companion/generated cinematic-backdrop census synchronized `loadBackdropAsset` at `0x800ADF74`; no build or runtime run. |
| s1517 | Exact companion/generated cinematic-asset census synchronized `initCinematicSceneAssets` at `0x800AE518`; no build or runtime run. |
| s1518 | Exact companion/generated cinematic-dispatch census synchronized `dispatchCinematicFromMainLoop` at `0x800AE878`; no build or runtime run. |
| s1519 | Exact companion/generated cinematic-predicate census synchronized `shouldShowCutsceneForLevelStage` at `0x800AE928`; no build or runtime run. |
| s1520 | Exact companion/generated cinematic-NPC census synchronized `getAssetNameForNpcType` at `0x800AE98C`; no build or runtime run. |
| s1521 | Exact companion/generated cinematic-getter census synchronized `getCutsceneRuntimeContext` at `0x800AEA18`; no build or runtime run. |
| s1522 | Exact companion/generated cinematic-noop census synchronized `noopHandler_800AEB30` at `0x800AEB30`; no build or runtime run. |
| s1523 | Exact companion/generated cinematic-teardown census synchronized `freeCutsceneResources` at `0x800AEB38`; no build or runtime run. |
| s1524 | Exact companion/generated cinematic-slot census synchronized `resetCutsceneActionSlots` at `0x800AEB7C`; no build or runtime run. |
| s1525 | Exact companion/generated cinematic-slot census synchronized `scheduleCutsceneActionSlot` at `0x800AEBD0`; no build or runtime run. |
| s1526 | Exact companion/generated cinematic-matrix census synchronized `composeInterpolatedNodeMatricesAlt` at `0x800AEC48`; no build or runtime run. |
| s1527 | Exact companion/generated cinematic-NPC census synchronized `tickCutsceneNpcSlots` at `0x800AEE14`; no build or runtime run. |
| s1529 | Exact companion/generated cinematic-NPC census synchronized `despawnCutsceneNpcSlot` at `0x800AEF30`; no build or runtime run. |
| s1530 | Exact companion/generated cinematic-slot census synchronized `initCutsceneSlotTable` at `0x800AEFC8`; no build or runtime run. |
| s1531 | Exact companion/generated cinematic-slot census synchronized `insertCutsceneSlot` at `0x800AEFF0`; no build or runtime run. |
| s1532 | Exact companion/generated cinematic-lookup census synchronized `lookupCutsceneIdMapping` at `0x800AF03C`; no build or runtime run. |
| s1533 | Exact companion/generated cinematic-NPC census synchronized `destroyAllNpcsInSlotChain` at `0x800AF08C`; no build or runtime run. |
| s1534 | Exact companion/generated cinematic-load census synchronized `maybeLoadYwingCutscene` at `0x800AF0EC`; no build or runtime run. |
| s1535 | Exact companion/generated cinematic-matrix census synchronized `buildBobbingObjectMatrix` at `0x800AF164`; no build or runtime run. |
| s1536 | Exact companion/generated cinematic-teardown census synchronized `cinematicShutdownAudioAndAssets` at `0x800AF260`; no build or runtime run. |
| s1537 | Exact companion/generated cinematic-compare census synchronized `bytesDiffer` at `0x800AF284`; no build or runtime run. |
| s1538 | Exact companion/generated cinematic-keyword census synchronized `matchKeywordWithPriority` at `0x800AF2C8`; no build or runtime run. |
| s1539 | Exact companion/generated cinematic-dt census synchronized `cinematicComputeDt` at `0x800AF360`; no build or runtime run. |
| s1540 | Exact companion/generated cinematic-init census synchronized `cinematicInitializer` at `0x800AF408`; no build or runtime run. |
| s1541 | Exact companion/generated cinematic-predicate census synchronized `isCinematicActive` at `0x800AF540`; no build or runtime run. |
| s1542 | Exact companion/generated cinematic-stage census synchronized `cinematicStageAdvancer` at `0x800AF550`; no build or runtime run. |
| s1543 | Exact companion/generated cinematic-teardown census synchronized `cinematicDeactivator` at `0x800AF60C`; no build or runtime run. |
| s1545 | Exact companion/generated cinematic-getter census synchronized `getCinematicStateSubObject` at `0x800AF65C`; no build or runtime run. |

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
