# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable project
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is
the authority for session detail. Reviewed through s1567 (2026-08-16).

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
   and M4 threads; s1544 was that revisit). One bounded exact-name census
   per session over the next adjacent function. Synchronize only names
   independently supported by the companion project, generated definitions,
   sizes, and caller/semantic evidence. Per-session H1 syncs through s1567
   live in `PORTING-STATE.md` and are archived in
   `PROJECT-OVERVIEW.md` §33; do not re-list them here.

   Next census: `0x800B41FC..0x800B42BC`. The generated entry is already
   `advancePitchTowardTarget`; the companion mission list maps
   `advancePitchTowardTarget = 0x800B41FC` with no extra comment.
   TOML is still `func_800B41FC` (size `0xC0`, ends at generated
   `fake_func_800B42BC` / TOML `fake_func_800B42BC` at `0x800B42BC`).
   Overlay `rom_size` is `0xC0` at offset `0x0000F0CC`. Confirm the
   complete live function, matching size, and caller/semantic
   evidence before synchronizing the TOML name. Independently named
   `getWeaponChargeLevel` at `0x800B41EC` (`rom_size` `0x10`)
   ends at this address. Last live instruction pair is `0x800B42B4`
   / `0x800B42B8` (`jr $ra` / `nop`). The body starts
   `lwc1 $f2, 0xC0($a0)`, `mtc1 $zero, $f0`, `mtc1 $a1, $f4`,
   `c.le.s $f2, $f0`, and ends `swc1 $f0, 0xC0($a0)` then the
   return pair. Zero retail `jal` encodings `0x0C02D07F`.
   Menu-overlay `accumulateShipThrottleCharge` at `0x800B4168`
   (`rom_size` `0xBC`, ends `0x800B4224`) occupies overlapping
   VRAM from `.ovl.menu` through the start of this body; menu-overlay
   `computeThrottleChargeFraction` at `0x800B4224` (`rom_size`
   `0x40`) occupies overlapping VRAM through the middle of this
   body. Neither is a mission size split. This naming census does
   not reopen closed M5 audio de-stubbing.

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
| s1240–s1268 | Exact companion/generated symbol sweeps synchronized the repository map; explicit fake/address-only entries stayed unchanged. |
| s1269 | Maintenance compaction only; no experiment or code change. |
| s1270–s1567 | Generated-symbol renaming sweep: exact companion/generated names from `0x80086450` through `getWeaponChargeLevel` at `0x800B41EC`. H2/H3 parks listed under Next steps #1. Full per-session table in `PORTING-STATE.md`; compact archive in `PROJECT-OVERVIEW.md` §33. No build or runtime run in these census sessions. |
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
