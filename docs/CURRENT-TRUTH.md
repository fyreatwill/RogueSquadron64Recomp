# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable project
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is
the authority for session detail. Reviewed through s1657 (2026-08-16).

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
  B intermediate 1024 phase begins, A or Start cancels back to hangar 512
  (elevated hangar-frame PC counts, no mission entry); Z is ignored and the
  B-route completes to 640 at `0x00696100` (s1650). Valid D-pad, post-viewer
  control, and post-B A/Start/Z arms passed controls but have not reached
  mission PC `0x80000B70`; do not repeat the already-tested inputs.
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

1. Continue the generated-symbol renaming sweep. The next exact census is
   companion `despawnEffectOnNamedDatItem` / generated
   `despawnEffectOnNamedDatItem` / TOML `func_800C7C88` at `0x800C7C88`
   (size `0x64`). Compare companion mapping/callers and semantics, generated
   body, previous and next boundaries, TOML size, and overlay span.
   Synchronize only on complete independent agreement (likely a stale-TOML
   correction if the generated body already carries the human name). The
   s1639 census confirmed `checkComplexObjectives` was already
   synchronized; s1640 synchronized `getAndSetByteAtLevelStateTable`;
   s1641 synchronized `getGlobalFloatGameState`; s1642 synchronized
   `getObjectiveGlobalFloat`; s1643 synchronized `setHudEnableBit4`;
   s1644 synchronized `setHudEnableBit8`; s1645 synchronized
   `isLevelStateByteZero`; s1646 synchronized `randMod`; s1647 confirmed
   `addBooleanCountHandleWrapper` was already synchronized; s1648 confirmed
   `addTimerHandleWrapper` was already synchronized; s1649 synchronized
   `setHudFlagBit40AndStoreArg` after correcting its stale TOML name;
   s1651 confirmed `calculateDatItemDistanceToPlayer` was already
   synchronized; s1652 synchronized `getScaledPlayerCraftSpeed` after
   correcting its stale TOML name; s1653 synchronized
   `spawnEffectOnNamedDatItem` after correcting its stale TOML name;
   s1654 synchronized `initActorTowardNamedDatItem` after correcting its
   stale TOML name; s1655 synchronized
   `initAnchoredActorTowardNamedDatItem` after correcting its stale TOML
   name; s1656 confirmed `getDatItemHealth` was already synchronized;
   s1657 confirmed `getDatItemHealthPercentage` was already synchronized.
   s1650 was the mandatory retail-entry revisit (post-B A/Start/Z). The
   full s1590–s1649 archive is in `PROJECT-OVERVIEW.md` §34; the earlier
   sweep is in §33. About 1,548 placeholder `func_0x...` names remained when
   counted at s1487.
2. Use the Rice `--video` oracle recipe for one genuinely new route that may
   leave a 640 frontend into a mission, or for a new M4 RDRAM destination
   from a DMEM→RDRAM transfer other than `0xD60`. Known hold/A/B/Z,
   valid-D-pad, post-viewer `C-up/C-down/C-left/C-right/L/R`, and post-B
   A/Start/Z arms are already classified or parked; do not repeat them. The
   640 B-frontend identity and any later input on that frontend remain open.
   Every oracle run needs whole-RDRAM, PIF, and VI/PC positive controls.
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
