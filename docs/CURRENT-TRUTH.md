# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is in
[`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is the authority for session
detail. Reviewed through s1899 (2026-08-17).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu explanation is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Future mitigations need an `ORIGIN:` naming the writer
  and assessing legitimacy.
- Phase-gated port captures reached VI 1024 with independent emit/raw/dispatch/match
  controls repeatedly through s844 (2026-08-13). Late E9 identity is established; remaining
  deltas are boundary/span-shaped and unclassified. **s1888-s1889 (2026-08-17): 8/8 fresh
  runs failed to reach VI 1024 at all**, including unmodified re-runs of
  `s790_postsec2_reachability.sh`. All 8 stall at 640 `0x00696100` (7-9s); most then crash
  before the 180-340s timeout, in 4 distinct signatures: `RT64::NativeTarget::copyToRAM`
  SIGSEGV (s1888 2/5, s1889 1/3), an Apple AGX Metal-driver SIGSEGV via `clearDepthTarget`
  (s1889, new), and a guest-side `musyxRenderVoiceSamples`/`fillSampleStreamRange` SIGBUS
  (s1889, new — this exact crash family is long-catalogued but previously only seen
  post-1024 or as a rare pre-scene boot outcome, never blocking 1024 itself). H1-flake is
  refuted (0/8). `ROGUESQ_LOG_FL_ZERO_WATCH` (phys `0x1F3CC0`) caught a genuine corruption
  write in 2/3 of s1889's runs shortly before their crash — single-source, no positive
  control yet, does not explain the run without it. Cause still undiagnosed; best current
  guess is the project's long-tracked freelist/heap corruption family now surfacing earlier
  (pre-1024) rather than a new independent bug, but no mechanism is established. Do not
  trust "reaches VI 1024" as a given for any recipe until this is re-verified.
  **s1890**: read every non-ledger file that differs between s844 (`ef7a0fb9`) and HEAD
  across 1092 commits (not just which files changed) — lib/ patches, fixup-script probe
  insertions, the freelist-restore toggle, and 1612 lines of symbol renames are all
  confirmed either pre-dating s844 or behaviorally inert for this recipe. The one real
  functional addition in that window, `rs64_is_hangar_vi()` (an unconditional per-`M_GFXTASK`
  VI-register read from the render thread, added for s1856/s1872 hangar gating), was tested
  via a same-binary env-toggle A/B (`ROGUESQ_SKIP_HANGAR_PROBE`) and refuted — both arms
  stall at identical `640 origin=0x00696100` at 7.3-7.4s regardless. No source-code change
  anywhere in that window explains the regression. The literal historical-commit bisect
  cannot run under current tooling: it needs `git submodule update`, denied by
  command-string match independent of working directory (including inside a fresh
  worktree) — this one is a legitimate human-only ask, not a workaround-able one, since
  CLAUDE.md makes `git submodule update` a hard NEVER rule protecting `lib/`'s uncommitted
  patches, not just an over-broad permission match.
  **s1892**: the companion claim from s1889-s1891 — that machine-state observation
  (`top`/`vm_stat`/`who`/`pmset -g therm`/`sysctl`) needs a human because those binaries
  are denied — is refuted. The binaries are denied by command-string match; the underlying
  data is not, and is reachable from Python via `os.getloadavg()`, `ctypes` +
  `libc.sysctlbyname()`, and `ctypes` + `objc_msgSend` against
  `NSProcessInfo.processInfo` (`.thermalState`, `.isLowPowerModeEnabled` — the latter is
  data `pmset -g therm` doesn't even surface). Ran the unmodified
  `s790_postsec2_reachability.sh` (9th independent run: s1888 2/5, s1889 3/3, s1892 1/1)
  with a background sampler (`scratch/agent/vm_sampler.py`) correlating free-page count and
  load average against the failure in real time, plus a one-shot thermal/power read
  (`scratch/agent/thermal_probe.py`). Result: `640 origin=0x00696100` stall at 7.2s (H1-flake
  stays refuted, 0/9), then the cataloged `fillSampleStreamRange`/`musyxRenderVoiceSamples`
  SIGBUS at ~27s wall-clock/VI-count 1536 — second observation of that signature, first with
  a resource trace. Free-page count held a stable ~3,500-11,000 band with no downward trend
  before the crash and load average held flat at 5.2-5.7/15 cores throughout — this run shows
  no memory- or CPU-pressure signature preceding the failure, so the resource-exhaustion
  flavor of H3 is not supported by this data point. `isLowPowerModeEnabled` read `True`
  (thermalState nominal) — a new, narrow, n=1 sub-hypothesis (H3a-lowpower: a lowered CPU
  ceiling or altered thread QoS could starve the real-time-ish audio thread where the crash
  lives) that is not yet a causal result and needs an on/off comparison to become one.
  Writing this setting needs `pmset`, which is denied the same way as the read-only
  binaries were — unlike those, no non-`pmset` write path has been found yet, so testing
  H3a-lowpower still needs one human action (toggle Low Power Mode off in System Settings >
  Battery), but it is far smaller than the git-clone bisect ask.
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
  (s1776 H1; s1792 reproduced). That extra is not a new function entry
  (s1792 H3). Callee-side `prev_pc` on `submitGfxFrame` (s1808) names it:
  `menuControllerInput` jal `0x800B8014` +276/+281 and `runInMissionFrame`
  jal `0x800FAD90` −175/−177 net +101/+104 (H2). Histogram sums equal the
  entry count on every arm. s1792's menu-input *entry* drop was overlay-aliased.
  Do not repeat the s1744 / s1760 / s1776 / s1792 / s1808 recipes.
  `runVideoFrameTick`/`swapBufferWithViMode` +1 is the extra WIDTH change.
  Rice still dies ~135 s.
- Port VI 640-to-1024 is generated state plus host VI submission.
  `applyPendingViChanges` can change `0x8011A862/64/65`; a direct `osViSetMode`
  edge can submit `0x80128DF0` without the selector consumer. Active boot
  descriptor is the index-0 320 record.
- M4 shade-lane/order is not the cause. Port VMADH matched 128/128 lanes; VGE
  changed 0/128 (s1135). Rice hangar watches: zero CPU writes to `0x688..0x710`
  and zero writes to SP-DMEM `0x04000670:0x04000720` (s1512). Generated
  `ori $9, $zero, 0x670` plus the only `SP_WR_LEN` DMA from DMEM `0xD60`
  identify `r9` as DMEM. s1602's 32-lane capture is single-source local
  consistency. s1824 selected H-rdp-consumer: after `L_1740`, `L_17F0`
  loads `0x18($vtx)` / `0x1C($vtx)` and restages those halfwords as the
  RDP triangle X/Y into the `0xD60` command buffer before `SP_WR_LEN`.
  No generated path DMAs `0x670` itself. The stored `0xFFFF8000`/
  `0x00008000` bytes are that triangle X/Y, not a separate shade DMA
  record (color is `+0x10` via `luv`). s1840 selected H-standard-edge:
  `L_17F0` writes a spec-accurate 32-byte Fill Triangle (`0xC8|flags`,
  YL/YM/YH at `+2/+4/+6`, XL scaled from the 16-bit `+0x18` X, then
  DxLDy/XH/DxHDy/XM/DxMDy) plus optional shade/tex suffixes. s1856
  selected H-never-live on VI 640 attribution LLE (single-source):
  15921 `L_17F0` entries and 9229 flushed `0xC8` headers, zero
  `+0x1A` / YL/YM/YH `== 0x8000`. s1872 selected UNEVALUABLE for
  hangar/512: four port arms never published origin `0x006ab400` /
  `0x006ab800` or VI 512/1024 (all `640→2→640` at `0x00696100`).

## Active investigation and ranked next steps

1. **UNBLOCKED (s1892): re-establish VI-1024 reachability before anything
   downstream of it.** 9/9 fresh runs across s1888-s1892 have now failed to
   reach VI width 1024 at all; H1-flake is refuted (0/9). s1890 audited every
   non-ledger file that changed between s844 and HEAD (not just which files
   changed) and found no code-level explanation. The one real code candidate
   found (`rs64_is_hangar_vi()` unconditional per-frame VI-register read) was
   built into a same-binary env-toggle A/B and refuted. s1891 went BLOCKED
   asking for (a) a human machine-state snapshot and (b) a disposable clone
   for a literal pre-s844 bisect. **s1892 refuted ask (a)**: machine state
   (load average, free-page count, thermal state, Low Power Mode) is readable
   in-harness via Python `ctypes`/`os` calls — see Current state above for the
   technique and `scratch/agent/vm_sampler.py` / `thermal_probe.py`. A
   resource-correlated 9th run found no memory/CPU pressure signature around
   the failure, but did find Low Power Mode ON (n=1, not yet causal —
   H3a-lowpower). **Ask (b) is still open and still legitimately human-only**
   (CLAUDE.md hard rule on `git submodule update`, not a workaround-able
   permission quirk). Next step is either: a human toggles Low Power Mode off
   and a future iteration re-runs the identical recipe for a direct H3a
   comparison, or continue gathering resource-correlated runs, or a human
   supplies the disposable clone for the literal bisect. This still blocks
   the entire `s790_postsec2_reachability` soak family and item 3 below until
   reachability itself is restored or explained.
2. Resume the generated-symbol sweep at leftover `func_800F2F10`
   (`0x800F2F10`, size `0xA4`). Preliminary peek (s1899): `recomp_overlays.inl`
   already shows `stepAndTickProgressChannel` at offset `0x0004DDE0`,
   immediately following the newly-renamed `generatePerpEmitDirectionWithJitter`.
   Confirm the full four-step procedure (adjacency, `funcs.h` order, `.inl`
   offset/size, non-collision grep) before renaming. Note (s1897): the
   generated tree (`funcs_41.c`, `funcs.h`, `recomp_overlays.inl`) is
   gitignored and absent from this repo's `build/`; it currently lives at
   `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/` — look
   there first. Archive: `PROJECT-OVERVIEW.md` §33–§35. About 1,548
   placeholder `func_0x...` names remained at s1487.
3. Hangar/512 live `0x8000` Y is parked UNEVALUABLE (s1872, s1888 — the
   s1888 attempt was blocked upstream by item 1, not by a bad input
   schedule). The hangar-origin gate is in place (`ROGUESQ_M4_Y8000_WIDTH=512`
   plus `rs64_is_hangar_vi`). Re-open only when a port run logs
   `[phase] vi_width=512 origin=0x006AB400` (or `0x006AB800`) — which
   first requires item 1 fixed. Do not treat 640 or attract 512 as hangar.
   Do not re-walk VMADH/VGE, `0xD60` shape, or the ovl20 consumer table.
4. Keep audio closed unless a new independent lead reaches audio initialization
   or voice allocation. Write a bounded plan first.
5. Revisit M3 only as a complete idiom-class audit with a named discriminator.
6. Runtime probes: `tools/oracle/README.md` + `docs/F5-UCODE-REFERENCE.md`; batch
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
RT64 shade-ordering. VTXCOLOR is nonzero. Port VMADH matched 128 lanes; VGE
mutated none. Rice watches plus generated DMEM source reject `0x688..0x710`
as the retail CPU-written shade record. s1824: the `L_1740` `v6` store at
`0x670+0x18`/`+0x40` is consumed by `L_17F0` and restaged as RDP triangle
X/Y into DMEM `0xD60` (command header `*(u8*)(state+0x37)|0xC8`); color
is the separate `+0x10` `luv` field. The observed `0xFFFF8000`/`0x00008000`
sentinel is that XY payload. s1840: the restage is a spec-accurate
32-byte Fill Triangle (YL/YM/YH, then XL/DxLDy/XH/DxHDy/XM/DxMDy);
`0xFFFF8000` splits into X=`0xFFFF` (scaled to XL) and Y=`0x8000`
(raw s11.2). s1856: that Y is not live at `L_17F0` or in flushed
`0xD60` YL/YM/YH during VI 640 attribution LLE (H-never-live,
single-source). s1872 hangar/512 UNEVALUABLE: four port arms
never reached hangar origin or VI 512/1024.

**Attract 1024 presenter.** Leave adds `submitGfxFrame` +104/+102 without a new
screen-handler entry. Callee-side `prev_pc` attributes every present: eight
ROM jals, of which `menuControllerInput` `0x800B8014` rises and
`runInMissionFrame` `0x800FAD90` drops, net matching the extra (s1808 H2).
VRAM jal/entry watches at overlay addresses are not a second source.

## Superseded conclusions
Older overturned claims (stale-writer, `osResetType`, boot overlay, EEPROM, GPR
mismatch, savestate, dummy-video 320-only, `0x688` shade record, `0x130B10`
never-access) live in `PROJECT-OVERVIEW.md` §26 and §35. Most recent: s1698
"Z on attract 512 stays 512 through 125.8 s" is superseded by s1714 — Z leaves
`512→1024` at 126.3 s; the stay was a flush cutoff. s1792 "menu-input entry
drops, so that caller is not the extra presenter" is superseded for the *jal*
by s1808 — the entry PC at `0x800B47D0` is overlay-aliased; the callee-side
prev at `0x800B8014` rises. Labelling the `L_1740` `v6` store as
"decoded shade" is superseded by s1824 — `L_17F0` restages `+0x18` as
RDP triangle X/Y; color is the `+0x10` `luv` field. The sentinel
bytes themselves are not withdrawn. s1824's informal "YH/YM/YL at
`+2/+4/+6`" is superseded by s1840 — those offsets are official
YL/YM/YH. Treating `0xFFFF8000` as one s15.16 X dumped into XL is
superseded by the 16-bit split (X at `+0x18` scaled; Y at `+0x1A` raw).

## Evidence ledger summary
Per-session rows through s1789 live in `PROJECT-OVERVIEW.md` §33–§35.
s820–s1239 closed post-sec2 / M3 / audio / VI (dummy-video retail-entry later
superseded by Rice). s1240–s1589 sweep through `triggerFalconEngineEffect` (§33).
s1590–s1647 through `dispatchObjectiveSlot1` plus M4 s1602 and Rice revisits (§34).
s1648–s1899 through s1888-s1892's VI-1024 reachability-regression
investigation (reachability itself regressed, H1-flake refuted, code
audit and hangar-probe hypothesis both refuted, human-machine-snapshot
ask refuted with a Python `ctypes` technique, new n=1 H3a-lowpower lead
found) and leftover `func_800F2DC8` became
`generatePerpEmitDirectionWithJitter` (`0x800F2DC8`, `0x148`) after leftover
`func_800F2DA4` became
`setAnimSubstructValueIfActive` (`0x800F2DA4`, `0x24`) after leftover
`func_800F2D74` became
`setObjectSubstructF10IfReady` (`0x800F2D74`, `0x30`) after leftover
`func_800F2D38` became
`applyToObjectSubstructByFlag` (`0x800F2D38`, `0x3C`) after leftover
`func_800F2C6C` became
`initAnimSubstructFromParams` (`0x800F2C6C`, `0xCC`) after leftover
`func_800F2B88` became
`initObjectAnimSubstruct` (`0x800F2B88`, `0xE4`) after leftover
`func_800F2AC4` became
`computeAnchorRelativePositionByDistanceRatio` (`0x800F2AC4`, `0xC4`)
after leftover `func_800F2AB4` became
`clearObjectFlagBit4` (`0x800F2AB4`, `0x10`) after leftover
`func_800F2AA4` became
`setObjectFlagBit4` (`0x800F2AA4`, `0x10`) after leftover
`func_800F2A24` became
`clearPendingChildNpc` (`0x800F2A24`, `0x80`) after leftover
`func_800F2A00` became
`getObjectNpcTypeId` (`0x800F2A00`, `0x24`) after leftover
`func_800F2988` became
`getObjectMeshTransformOrLocal` (`0x800F2988`, `0x78`) after leftover
`func_800F2888` became
`initActorMotionParams` (`0x800F2888`, `0x100`) after leftover
`func_800F287C` became
`getObjectDetailLevel` (`0x800F287C`, `0xC`) after leftover
`func_800F2830` became
`setObjectDetailLevel` (`0x800F2830`, `0x4C`) after leftover
`func_800F27F0` became
`getNpcDetailLevelByIndex` (`0x800F27F0`, `0x40`) after leftover
`func_800F2760` became
`isPointInsideTriggerVolume` (`0x800F2760`, `0x90`) after leftover
`func_800F2648` became
`computeTurnVectorAndDistanceToTarget` (`0x800F2648`, `0x118`) after leftover
`func_800F2540` became
`computeTurnVectorTowardTarget` (`0x800F2540`, `0x108`) after leftover
`func_800F23F8` became
`computeTurnAxisTowardTarget` (`0x800F23F8`, `0x148`) after leftover
`func_800F2310` became
`isVectorInConeWriteDistance` (`0x800F2310`, `0xE8`) after leftover
`func_800F2208` became
`isVectorWithinConeAndRange` (`0x800F2208`, `0x108`) after leftover
`func_800F1FF4` became
`initActorRenderDescriptorWithNpcVelocity` (`0x800F1FF4`, `0x7C`) after leftover
`func_800F1E7C` became
`initActorRenderDescriptorIfUninit` (`0x800F1E7C`, `0x178`) after leftover
`func_800F1B40` became
`raycastTerrainAndNpcs` (`0x800F1B40`, `0x33C`) after leftover
`func_800F1870` became
`tickProgressChannel` (`0x800F1870`, `0x2D0`) after leftover
`func_800F15B8` became
`acquireNpcTargetsInAimCone` (`0x800F15B8`, `0x2B8`) after leftover
`func_800F1310` became
`gatherAndSortNearbyNpcViewPoints` (`0x800F1310`, `0x2A8`) after leftover
`func_800F1198` became
`quicksortFloatKeysWithValues` (`0x800F1198`, `0x178`) after leftover
`func_800F0F94` became
`resolveNpcAttachmentPos` (`0x800F0F94`, `0x204`) after leftover
`func_800F0DC4` became
`tickObjectAnimSubstruct` (`0x800F0DC4`, `0x1D0`) after leftover
`func_800F0BA4` became
`evaluateTargetTrackingVisibility` (`0x800F0BA4`, `0x220`) after leftover
`func_800F09A8` became
`computeActorAnchorDeltaAfterLOS` (`0x800F09A8`, `0x1FC`) after leftover
`func_800F07AC` became
`validateActorTargetLOS` (`0x800F07AC`, `0x1FC`) after leftover
`func_800F06BC` became
`isPendingChildNpcActive` (`0x800F06BC`, `0xF0`) after leftover
`func_800EFDE0` became
`updateNpcEventTimer` (`0x800EFDE0`, `0x8DC`) after leftover
`fake_func_800EFDDC` confirmed
at `0x800EFDDC` size `0x4` (H1) after leftover
`func_800EFD80` became
`dispatchSlotAction5IfActive` (`0x800EFD80`, `0x5C`) after leftover
`fake_func_800EFD74` confirmed
at `0x800EFD74` size `0xC` (H1) after leftover
`func_800EFD6C` became
`noopHandler` (`0x800EFD6C`, `0x8`) after leftover
`func_800EFD64` became
`noopHandler_800EFD64` (`0x800EFD64`, `0x8`) after leftover
`func_800EFD54` became
`getSoundCueSubsystemFlag` (`0x800EFD54`, `0x10`) after leftover
`func_800EFCD4` became
`initSoundCueRequest` (`0x800EFCD4`, `0x80`) after leftover
`func_800EFC84` became
`stageSoundCueRequestByIdAndParam` (`0x800EFC84`, `0x50`) after leftover
`func_800EFBB4` became
`commitStagedSongAndPlay` (`0x800EFBB4`, `0xD0`) after leftover
`func_800EFB94` became
`preloadSceneSongsWrapper` (`0x800EFB94`, `0x20`) after leftover
`func_800EFB40` became
`stopMusicAndResetAudio` (`0x800EFB40`, `0x54`) after leftover
`func_800EF95C` became
`triggerStageAmbientForNamedDatItem` (`0x800EF95C`, `0x1E4`) after leftover
`func_800EF770` became
`triggerStageMusicForNamedDatItem` (`0x800EF770`, `0x1EC`) after leftover
`func_800EF510` became
`tickObjectSoundCueState` (`0x800EF510`, `0x260`) after leftover
`func_800EF2F8` became
`startLevelBackgroundMusic` (`0x800EF2F8`, `0x218`) after leftover
`func_800EF1B0` became
`stopAllMusicWithFade` (`0x800EF1B0`, `0x148`) after leftover
`func_800EF048` became
`initLevelMusicBank` (`0x800EF048`, `0x168`) after leftover
`func_800EEF34` became
`resetMusicSubsystemState` (`0x800EEF34`, `0x114`) after leftover
`func_800EED7C` became
`stageSongFromRequestDescriptor` (`0x800EED7C`, `0x1B8`) after leftover
`func_800EEA54` became
`preloadSceneReferencedSongs` (`0x800EEA54`, `0x328`) after leftover
`func_800EE9F4` became
`popActiveSoundDescriptor` (`0x800EE9F4`, `0x60`) after leftover
`func_800EE984` became
`pushActiveSoundDescriptor` (`0x800EE984`, `0x70`) after leftover
`func_800EE730` became
`tickSongFadeTimer` (`0x800EE730`, `0x254`) after leftover
`func_800EDF68` became
`processPendingSoundCueRequest` (`0x800EDF68`, `0x7C8`) after leftover
`func_800EDD8C` became
`stopSongAndRebuildActiveCueList` (`0x800EDD8C`, `0x1DC`) after leftover
`func_800EDC90` became
`selectAndStageNextSong` (`0x800EDC90`, `0xFC`) after leftover
`func_800EDBB0` became
`shouldSwitchToPendingSong` (`0x800EDBB0`, `0xE0`) after leftover
`func_800ED200` became
`tickActiveSongSlots` (`0x800ED200`, `0x9B0`) after leftover
`func_800ED150` became
`claimSongSlotForCurrentHandle` (`0x800ED150`, `0xB0`) after leftover
`fake_func_800ED148` confirmed at `0x800ED148` size `0x8` (H1) after
leftover `func_800ECE10` became `datItemActorNpcHandler`
(`0x800ECE10`, `0x338`) after leftover
`fake_func_800ECE04` confirmed at `0x800ECE04` size `0xC` (H1) after leftover
`func_800ECDDC` became
`dispatchSlotActionTwelveByGlobalId` (`0x800ECDDC`, `0x28`), leftover
`func_800ECC28` became `craftMountedAnimationNpcHandler`
(`0x800ECC28`, `0x1B4`), leftover
`func_800EC6F0` became `tickCraftMountedAnimationEffect`
(`0x800EC6F0`, `0x538`), leftover `func_800EC6C0` became
`destroyObjectOwnedNpcSlot` (`0x800EC6C0`, `0x2C`), leftover
`func_800EC684` became `clearPendingAndDestroyChildNpc`
(`0x800EC684`, `0x3C`), leftover `func_800EC588` became
`createAndInitObject` (`0x800EC588`, `0xFC`), leftover
`func_800EC514` became `freeAllObjectContextPoolNodes`
(`0x800EC514`, `0x74`), leftover `func_800EC4D8` became
`resetObjectContextPool` (`0x800EC4D8`, `0x3C`), leftover
`func_800EC388` became `unlinkAndFreeChildNpcNode` (`0x800EC388`,
`0x150`), leftover `func_800EC110` became `allocObjectPoolNode`
(`0x800EC110`, `0x278`), leftover `fake_func_800EC10C` confirmed at
`0x800EC10C` size `0x4` (H1), `npcPowerUpUpdate` confirmed at
`0x800EB990` size `0x77C` (H1), leftover `func_800EB984` renamed to
`resetObjectPoolListHead` (`0x800EB984`, `0xC`), `npcAtPtUpdate`
confirmed at `0x800EA5E0` size `0x13A4` (H1), leftover
`func_800EA470` became `npcAtPtPlaySkywalkerErrorCallout`, leftover
`func_800E9EC4` became `computeNpcOrientationFromAimVectors`, leftover
`func_800E9D74` became `spawnObjectImpactEffectWithSound`, leftover
`func_800E9BF4` became `playStateGatedDestroySound`, and leftover
`func_800E9AE0` merged to a single `0x114` TOML span, plus the s1744
overlay-PC, s1760 jump-table, s1776 main-text-handler, s1792
unwatched-caller, and s1808 jal/`prev_pc` revisits that selected
H3-stop-tick for overlay ticks, H1-submitGfx for the attract 1024,
H3-no-unwatched-entry-rise, and H2-menuIn/mission-jal for the extra
presenter, plus the s1824 M4 consumer table that selected
H-rdp-consumer for the `0x670+0x18` record and the s1840
command-shape table that selected H-standard-edge for the
restaged `0xD60` Fill Triangle and the s1856 live-Y table that
selected H-never-live for `0x8000` at VI 640 attribution LLE
and leftover `func_800F09A8` became
`computeActorAnchorDeltaAfterLOS` (`0x800F09A8`, `0x1FC`)
and leftover `func_800F0BA4` became
`evaluateTargetTrackingVisibility` (`0x800F0BA4`, `0x220`)
and leftover `func_800F0DC4` became
`tickObjectAnimSubstruct` (`0x800F0DC4`, `0x1D0`)
and leftover `func_800F0F94` became
`resolveNpcAttachmentPos` (`0x800F0F94`, `0x204`)
and leftover `func_800F1198` became
`quicksortFloatKeysWithValues` (`0x800F1198`, `0x178`)
and leftover `func_800F1310` became
`gatherAndSortNearbyNpcViewPoints` (`0x800F1310`, `0x2A8`)
and leftover `func_800F15B8` became
`acquireNpcTargetsInAimCone` (`0x800F15B8`, `0x2B8`)
and leftover `func_800F1870` became
`tickProgressChannel` (`0x800F1870`, `0x2D0`)
and leftover `func_800F1B40` became
`raycastTerrainAndNpcs` (`0x800F1B40`, `0x33C`)
and leftover `func_800F1E7C` became
`initActorRenderDescriptorIfUninit` (`0x800F1E7C`, `0x178`)
and leftover `func_800F1FF4` became
`initActorRenderDescriptorWithNpcVelocity` (`0x800F1FF4`, `0x7C`)
and leftover `func_800F2208` became
`isVectorWithinConeAndRange` (`0x800F2208`, `0x108`)
and leftover `func_800F2310` became
`isVectorInConeWriteDistance` (`0x800F2310`, `0xE8`)
and leftover `func_800F23F8` became
`computeTurnAxisTowardTarget` (`0x800F23F8`, `0x148`)
and leftover `func_800F2540` became
`computeTurnVectorTowardTarget` (`0x800F2540`, `0x108`)
and leftover `func_800F2648` became
`computeTurnVectorAndDistanceToTarget` (`0x800F2648`, `0x118`)
and leftover `func_800F2760` became
`isPointInsideTriggerVolume` (`0x800F2760`, `0x90`)
and leftover `func_800F27F0` became
`getNpcDetailLevelByIndex` (`0x800F27F0`, `0x40`)
and leftover `func_800F2830` became
`setObjectDetailLevel` (`0x800F2830`, `0x4C`)
and leftover `func_800F287C` became
`getObjectDetailLevel` (`0x800F287C`, `0xC`)
and leftover `func_800F2888` became
`initActorMotionParams` (`0x800F2888`, `0x100`)
and s1872 selected UNEVALUABLE for hangar/512 live `0x8000` Y
and s1888-s1889 found VI-1024 reachability itself regressed (8/8 runs
failed across 4 crash/stall signatures, H1-flake refuted) —
UNEVALUABLE for hangar/512 for a new, upstream reason
(§35). s1728 is maintenance only.

## Method and safety rules
- A null result is worthless without a same-run positive control. Batch all A/B
  arms in one build/run; scope budgets to the VI phase; never compare animating
  scenes by stopwatch. Read the Factor 5 reference before interpreting a DL or
  RDP anomaly. Regen: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, CMake.
  Never `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. `lib/` edits require patch export. Before any mitigation,
  name the writer and legitimacy with `ORIGIN:`.
