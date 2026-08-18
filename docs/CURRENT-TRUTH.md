# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is in
[`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is the authority for session
detail. Reviewed through s1948 (2026-08-18). s1948 is maintenance: this file
was compacted from 60,464 bytes / 1,700 lines.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu explanation is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Future mitigations need an `ORIGIN:` naming the writer
  and assessing legitimacy.
- Phase-gated port captures reached VI 1024 through s844 (2026-08-13). Late E9
  identity is established; remaining deltas are boundary/span-shaped. Post-s844
  recipes then stalled at 640 `0x00696100` (s1888–s1918). H1-flake, H3a-lowpower,
  and the `rs64_is_hangar_vi` toggle are refuted; no source change in the
  s844→HEAD window explains it. Ask (b) (clone + `git submodule update` bisect
  at `ef7a0fb9`) is still human-only. s1918 selected H3 true-stall: 2/8 `s790`
  logs live 180s with zero `osViSetMode width=1024` (s844 control: `#10` at
  79.6s `#4715`). Crash families kill some runs but are not why 1024 is missing.
- **1024 miss, closed through title-like 1024.** The `#10` issuer is
  `advanceVideoFrame` `0x80018378` → `initVideoSubsystem` (s1919). The swap
  loop dies after two `runVideoFrameTick` calls (s1920–s1922). Tick 1 is
  `menuOverlayInit`; tick 2 is `initSceneForMission`; `menu-entry` siten=2 then
  sits in `L_800C5930` `anyAudioSlotActive` (s1923–s1924). The 16-voice table
  at `0x8018D4A0` is a sane `allocateSongChannelArray` retarget; slot+0 `0x02`
  is `musyxRenderVoiceSamples` after key-on (s1926–s1927). Mix and VI-retrace
  both freeze at `.ovl.menu` + entry 2 (s1930–s1931). The walk after `#8`
  completes; the next `osRecvMesg(0x80114388)` blocks (s1935–s1938). Host VI
  keeps enqueueing that mq and never dequeues (s1939–s1941) because the spin
  is runnable (`beq v0==0`) so idle-wait never runs. `ROGUESQ_SPIN_YIELD=1`
  (env-gated `yield_self_1ms` every 100000 `L_800C5930` iters) unblocks recv1,
  resumes synth, and publishes `#9`/`#10` width-1024 origin `0x00790400`
  (s1942; H-spin-starves-idle). Default-off. ORIGIN: host VI retrace
  (legitimate) sits in `external_messages`; hardware would preempt the spin.
  Session-by-session table: `PROJECT-OVERVIEW.md` §36.
- **After title 1024 the same idiom re-starves SI.** Eleven-Start from boot
  stays on title 1024 (s1943; not hangar). Only 4/11 Starts reach
  `get_n64_input`; 2 of those are a live title pad word the screen ignores
  (s1944). SDL poll and host pad die together after Start #4 (s1945).
  `siServiceThread` completes iter 1419 then blocks on the next loop Recv
  (s1946). After 1024 the only live `jal 0x8008E57C` is `menuControllerInput`
  `L_800B8050` (n=773e6, `v0=0` walk); `menuOverlayInit` /
  `waitForAnyAudioSlot` / the other seven are dead (s1947; H-menu-input).
  The s1942 yield does not cover this site.
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

1. **H-menu-input SELECTED (s1947).** After title 1024, the only live
   `jal 0x8008E57C` site is `menuControllerInput` `0x800B8050` (n=773e6,
   `v0=0` walk). Same `beq v0==0` audio-slot spin as the s1924
   `menuOverlayInit` stall; s1942 `ROGUESQ_SPIN_YIELD` only covers
   `L_800C5930`, so this second spin re-starves idle-wait (SI send 1418
   then recv1 n=1419 `blocked=1`). Next split: extend that same env-gated
   yield to `L_800B8050` and see whether SI/poll resume and whether hangar
   appears. Do not default the yield on. Do not repeat eleven-Start as a
   hangar recipe without that yield. Ask (b) remains human-only.
2. Generated-symbol sweep leftover `func_800F7130` (`0x800F7130`,
   TOML size `0xB44` matches generated `renderNpcAnchoredProceduralEffect`
   `rom_size 0xB44`). Four-step already complete (s1906–s1917). Next sweep
   iteration can rename directly (TOML metadata-only). After that:
   `func_800F7C74` → `spawnAndUpdateEffectActors`;
   `func_800F8398` → `executeActorType4Effect`;
   `func_800F9474` → `clearObjectField112`. Generated tree lives
   at `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/`.
   Archive: `PROJECT-OVERVIEW.md` §33–§36. About 1,548 placeholder
   `func_0x...` names remained at s1487; TOML leftover `func_800*`
   count is 982 after s1917. s1903–s1917 were all sweep-titled;
   s1918 was the mandatory 15-title REVISIT (do not treat a later
   session as another REVISIT just because the window once contained
   only sweep titles).
3. Hangar/512 live `0x8000` Y is parked UNEVALUABLE (s1872, s1888,
   s1943, s1944). The 640 stall is no longer the blocker (s1942 yield
   publishes 1024; s1944 still publishes it at 14.1s). The classified
   hangar schedule still never produces origin `0x006AB400`/`800`. Gate
   stays (`ROGUESQ_M4_Y8000_WIDTH=512` plus `rs64_is_hangar_vi`). Success
   is still `[phase] vi_width=512 origin=0x006AB400` (or `0x006AB800`).
   Do not treat 640, attract 512, or title `0x00790400` as hangar. Do
   not re-walk VMADH/VGE, `0xD60` shape, or the ovl20 consumer table.
4. Keep audio closed unless a new independent lead reaches audio
   initialization or voice allocation. Write a bounded plan first.
5. Revisit M3 only as a complete idiom-class audit with a named discriminator.
6. Runtime probes: `tools/oracle/README.md` + `docs/F5-UCODE-REFERENCE.md`;
   batch arms; phase-gate; SIGKILL; queue soaks.

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

Older overturned claims live in `PROJECT-OVERVIEW.md` §26, §35, and §36.
Most recent, still load-bearing for the next unit:

- s1888–s1917 "stall at 640 then crash" is superseded by s1918 — 2/8 logs
  live 180s with no crash and no `osViSetMode width=1024`.
- H-slots-stay-live is superseded by s1942 — two `yield_self_1ms` calls
  unblocked recv1 and the guest issued `#9/#10`.
- Eleven-Start-from-boot as a hangar recipe once 1024 is reachable is
  superseded by s1943 — it reaches title-like 1024 at 14.2s and stays.
- s1943 "all 11 Starts printed" as host pad consumption is superseded by
  s1944 — those were probe `[keys]` sends; only 4 rising Start edges
  reached `get_n64_input`.
- Missing 7 Starts as SDL/focus drop, `poll_input`-only drain, or a
  56s live window is superseded by s1945 — poll and host die together
  after Start #4.
- SI stop as a stuck post-`StartReadData` Recv, a thread exit, or a skip
  of `StartReadData` is superseded by s1946 — last site is `send` n=1419
  with no `loop` n=1420.
- Continuing post-1024 spin as `waitForAnyAudioSlot` / `menuOverlayInit`
  / another of the ten `jal 0x8008E57C` sites is superseded by s1947 —
  only `menuControllerInput` is live after 1024.

s1919–s1941 caller / slot / mix / VI-recv supersessions are archived in
§36 rather than restated here.

## Evidence ledger summary

Per-session rows through s1879 live in `PROJECT-OVERVIEW.md` §33–§35.
s1880–s1917 leftover remaps and the s1888–s1947 VI-1024 / spin-yield /
title-SI chain live in §36. s820–s1239 closed post-sec2 / M3 / audio / VI
(dummy-video retail-entry later superseded by Rice). s1728 and s1948 are
maintenance only.

## Method and safety rules

- A null result is worthless without a same-run positive control. Batch all A/B
  arms in one build/run; scope budgets to the VI phase; never compare animating
  scenes by stopwatch. Read the Factor 5 reference before interpreting a DL or
  RDP anomaly. Regen: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, CMake.
  Never `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. `lib/` edits require patch export. Before any mitigation,
  name the writer and legitimacy with `ORIGIN:`.
