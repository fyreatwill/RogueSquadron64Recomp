# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is in
[`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is the authority for session
detail. Reviewed through s1795 (2026-08-16).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu explanation is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Future mitigations need an `ORIGIN:` naming the writer
  and assessing legitimacy.
- Phase-gated port captures reach VI 1024 with independent emit/raw/dispatch/match
  controls. Late E9 identity is established; remaining deltas are
  boundary/span-shaped and unclassified.
- Recurring `slotDispatcherIter+872` SIGBUS is the generated prologue spill of
  guest `$sp` at `funcs_8.c:22810`. Complete static audits found no reachable
  frame-overlapping writer. Runtime guest corruption remains open; no mitigation.
- Corrected `npcPowerGeneratorUpdate` is main `.text` at `0x80077AF0`;
  regenerated ELF, N64Recomp, fixups, and Debug target pass. Runtime boundary
  tests remain pre-1024 and unevaluable.
- M5 audio de-stubbing is closed. Audio remains stubbed. Dummy-video retail
  watches never reached `musyxInitVoiceFromSample`. Do not reopen without a new
  bounded plan using the Rice hangar recipe.
- Retail oracle whole-RDRAM, scheduled PIF, and VI controls are healthy. Dummy
  video stays 320 / `0x006dd280`. Homebrew Rice with the eleven-Start schedule
  is the hangar-entry recipe (s707, s1496). Classified frontend routes live in
  `PROJECT-OVERVIEW.md` §35 — do not repeat them.
- Attract A/Start/C-up/L/Z title-like 1024 (`0x00790400`/`800` at 126.3–126.4 s)
  is not a new `cinematicLoopBody`, `runMenuContentStateMachine`,
  `runInMissionFrame` (s1744), or `menuOverlayInit` jump-table case (s1760).
  Extra `loadOverlay` +2 is menu dest +1 plus a skip. Leave stops the
  high-frequency overlay-aliased ticks hold's attract continues. Case 9
  `0x800C28F0` stays 1. Leave also adds `submitGfxFrame` +104/+102 vs hold
  (s1776 H1; s1792 reproduced). Unwatched callers stay flat or drop (s1792
  H3): `runIdleFramesAndLoadSaveData` stays 1; `tickCraftSelectScreen` stays
  ~1028; `menuControllerInput`/`runResultsTextScreenLoop` drop with
  ship-select; `runMenuRandomBackdropScreen`/`menuSubtype02Handler`/
  `runModelViewerLoop` stay 0. `mainGameLoop` and
  `applyLevelScreenAndCameraSettings` stay 1 (H2 closed); `emitFrameRdpInitDl`
  drops −180 with the ship-select ticks (H4 closed).
  `runVideoFrameTick`/`swapBufferWithViMode` +1 is the extra WIDTH change.
  Rice still dies ~135 s. Next revisit needs jal-site / `$ra` watches, not
  another entry-PC set.
- Port VI 640-to-1024 is generated state plus host VI submission.
  `applyPendingViChanges` can change `0x8011A862/64/65`; a direct `osViSetMode`
  edge can submit `0x80128DF0` without the selector consumer. Active boot
  descriptor is the index-0 320 record.
- M4 shade-lane/order is not the cause. Port VMADH matched 128/128 lanes; VGE
  changed 0/128 (s1135). Rice hangar watches: zero CPU writes to `0x688..0x710`
  and zero writes to SP-DMEM `0x04000670:0x04000720` (s1512). Generated
  `ori $9, $zero, 0x670` plus the only `SP_WR_LEN` DMA from DMEM `0xD60`
  identify `r9` as DMEM. s1602's 32-lane capture is single-source local
  consistency. Unresolved boundary: source state or later DMA/consumer identity.

## Active investigation and ranked next steps

1. Resume the generated-symbol sweep at leftover `func_800E8828` /
   companion `playAttachmentCueNoTexture` (`0x800E8828`, size `0x120`).
   Neighbor peek: TOML still carries `func_800E8828`; generated
   headers/body, overlay INL, and `mission_overlay.txt` already use the
   human name (likely H2 TOML-only). Next leftover after it is
   `func_800E8948` / companion `applyCraftAnimDetailParamsB`. Archive:
   `PROJECT-OVERVIEW.md` §33 (s1240–s1589), §34 (s1590–s1647), §35
   (s1648–s1795). About 1,548 placeholder `func_0x...` names remained
   at s1487.
2. Next mandatory REVISIT (when last-15 titles are all sweep): watch
   `submitGfxFrame` jal-sites / `$ra`, not another function-entry PC set.
   The extra +104/+102 is still real (s1776 H1, s1792 reproduced) and is
   not an entry of the 12 classified/unwatched callers. Do not repeat
   the s1744 six-entry, s1760 jump-table, s1776 main-text, or s1792
   unwatched-caller recipes or extend `--secs 133`. Every oracle run
   needs whole-RDRAM, PIF, and VI/PC controls. Do not repeat §35
   classified routes.
3. Keep audio closed unless a new independent lead reaches audio initialization
   or voice allocation. Write a bounded plan first.
4. Revisit M3 only as a complete idiom-class audit with a named discriminator.
5. Runtime probes: `tools/oracle/README.md` + `docs/F5-UCODE-REFERENCE.md`; batch
   arms; phase-gate; SIGKILL; queue soaks.

## Durable boundaries
**M3 dispatcher/frame origin.** s1162: 144 direct `slotDispatcherIter` calls in
72 generated callers; caller entries, stack pairs, and saved-`$ra` contracts
match. No static indirect target to `0x8003E8DC`. One executable `r29`
initializer in `run_thread_function`. Writer/load classes selected H3; no next
class without a new discriminator.

**VI descriptor.** `osTvType=1` → `rsViModeType=0`; boot selector `A/B/C=1/0/0`.
Active record is base `+0xF0` (`0x80128E40`), the 320 descriptor.
`osViSetMode_recomp` forwards `ctx->r4` unchanged. Independently established.

**M4 accumulator.** Factor 5 reference data and paired combiner evidence refute
RT64 shade-ordering. VTXCOLOR is nonzero; decoded shade is the `0xFFFF8000`/
`0x00008000` sentinel. Port VMADH matched 128 lanes; VGE mutated none. Rice
watches plus generated DMEM source reject `0x688..0x710` as the retail
CPU-written shade record. Unresolved: source state or later DMA/consumer identity.

## Superseded conclusions
Older overturned claims (stale-writer, `osResetType`, boot overlay, EEPROM, GPR
mismatch, savestate, dummy-video 320-only, `0x688` shade record, `0x130B10`
never-access) live in `PROJECT-OVERVIEW.md` §26 and §35. Most recent: s1698
"Z on attract 512 stays 512 through 125.8 s" is superseded by s1714 — Z leaves
`512→1024` at 126.3 s; the stay was a flush cutoff.

## Evidence ledger summary
Per-session rows through s1789 live in `PROJECT-OVERVIEW.md` §33–§35.
s820–s1239 closed post-sec2 / M3 / audio / VI (dummy-video retail-entry later
superseded by Rice). s1240–s1589 sweep through `triggerFalconEngineEffect` (§33).
s1590–s1647 through `dispatchObjectiveSlot1` plus M4 s1602 and Rice revisits (§34).
s1648–s1795 through leftover `func_800E7390` synchronized to
`tickFighterSquadronWithSplinePaths` after `transformCraftAnchorsApplySubFx3`,
leftover `fake_func_800E71C8`, `npcWaterCraftUpdate`, and confirmed
`npcGroundTroopUpdate`, plus the s1744 overlay-PC, s1760 jump-table,
s1776 main-text-handler, and s1792 unwatched-caller revisits that
selected H3-stop-tick for overlay ticks, H1-submitGfx for the attract
1024, and H3-no-unwatched-rise for the extra presenter's function entry
(§35). s1728 is maintenance only.

## Method and safety rules
- A null result is worthless without a same-run positive control. Batch all A/B
  arms in one build/run; scope budgets to the VI phase; never compare animating
  scenes by stopwatch. Read the Factor 5 reference before interpreting a DL or
  RDP anomaly. Regen: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, CMake.
  Never `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. `lib/` edits require patch export. Before any mitigation,
  name the writer and legitimacy with `ORIGIN:`.
