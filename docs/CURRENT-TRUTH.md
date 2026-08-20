# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is in
[`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is the authority for session
detail. Reviewed through s1976 (2026-08-19).

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
- **Hangar is reachable (s1949).** Extending the same env-gated
  `ROGUESQ_SPIN_YIELD` to `menuControllerInput` `L_800B8050`
  (`site=menuInput`, every 100000, default-off) unblocks post-1024 SI
  and publishes `[phase] 512 origin=0x006AB400` at 26.1s `#1496`.
  Captured frame is the hangar SELECT LEVEL / AMBUSH AT MOS EISLEY
  screen. Recipe: `ROGUESQ_SPIN_YIELD=1` + eleven-Start from boot.
  Do not default the yield on. ORIGIN: host VI/SI retrace (legitimate)
  sits in `external_messages`; this second `beq v0==0` spin is runnable
  so idle-wait never drains. Hardware would preempt.
- **bltzal $zero PIC-idiom link-register class fixed (s1971); hangar stable
  60s+ (17 frames, no crash).** N64Recomp's direct-call lowering generates
  `if (SIGNED(0) < 0) { ... }` for `bltzal $zero` (dead code) but omits
  writing `ctx->r31 = PC+8`. Six sites in `funcs_27.c` use `$ra` as a
  PC-relative data-pointer base immediately after: two in
  `filterVoiceSampleBlock` (0x8009D7E0, 0x8009D8EC), one in
  `applyVoiceDelayFilter` (0x8009D8EC), and four in `renderVoiceAudioBlock`
  (0x8009DBA4, 0x8009DBC8, 0x8009DBEC, 0x8009DC10). The `fixup_game_funcs.py`
  s1971 patch inserts `ctx->r31 = 0x[PC+8]u` before each consumer. Callees of
  `bgezal $zero` (`audioMixStereoBlock8`, `runVoiceLatticeFilter`) confirmed
  to use ctx->r31 zero times — safe. Runtime: hangar ran 60s with 17 frames
  vs 1 frame / 4s before. H-link-lost selected class-wide; filterVoiceSampleBlock
  SIGBUS family CLOSED. ORIGIN: N64Recomp direct-call lowering omits the link
  write; fix is the legitimate PC+8 value.
- **anyAudioSlotActive spin class fully enumerated and gated (s1974).** All 10
  `anyAudioSlotActive` callers catalogued: 3 yield-gated (menuInit/L_800C5930,
  menuInput/L_800B8050, audioDrain/L_800B24D4), 1 bounded (waitForAnyAudioSlot/
  L_800668C0), 6 newly yield-gated (runMenuRandomBackdropScreen/L_800BFF60,
  runMenuShipSelectScreen/L_800C1750, runMenuModelViewerScreen/L_800C2DB0,
  menuSubtype02Handler/L_800C3F64, runModelViewerLoop/L_800CA580,
  initCinematicSceneAssets/L_800AE75C) — patches in funcs_33/36/28.c and
  fixup_game_funcs.py. Census probe: none of the 6 new sites fired in 120s
  hangar run. The frame freeze at update_screen #2176 is NOT an anyAudioSlotActive
  spin. Class closed.
- **`drainAudioAndFinalizeSpeechBuffer` spin-yield class CLOSED (s1972); idle
  wait is NOT.** Same `beq v0==0 / anyAudioSlotActive` pattern as menuInit and
  menuInput. Yield at `L_800B24D4` (s1972) lets idle-wait run; it does not
  make the drain return. s1976 ground truth: `anyAudioSlotActive` returns 1
  when idle (`sltiu s1<1` after OR of slot byte+0); the spin waits for idle,
  not for a key-on. In-loop `tickMusyXIfActive` (gate=0x01, 10M iters, same-run
  `[drain-tick]` control) never idled call=1; logged 10M timeout forced
  `v0=1` and the function returned; `fs` stayed 1215 with zero further
  `[lle task]`. H-reap-in-loop and H-tick-skips REFUTED; H-stuck-slot
  SELECTED; force-idle is not sufficient. ORIGIN: leftover nonzero
  slot-status bytes (legitimate `isAudioSlotActive` byte+0). Writer is the
  game's own voice key-on. `tickAndReap3DAudioVoices` + `stopAllSynthVoices`
  do not clear them on this host path. Timeout is a diagnostic escape hatch,
  not a product mitigation. Default-off yield unchanged.
- **M4 hangar/512 Y=0x8000 is not live (s1949).** On the first hangar
  capture: 2187 `L_17F0` entries, 3904 flushes, `y8000_entry=0`
  `y8000_any=0`, plus a recognizable 3D hangar frame. Do not re-walk
  VMADH/VGE / `0xD60` / the ovl20 table. Late-hangar Y is unsampled
  (crash cut the window).
- **Hangar hologram-beam artifact: H2 (malformed triangle command)
  REFUTED (s1967).** Extended the M4 `0xD60`-restage walker to check
  every flushed Fill-Triangle command's `YH<=YM<=YL` ordering, not just
  the Y=`0x8000` subset; zero degenerate (zero-height) triangles, but a
  recurring `order_bad` hit at offset `0xE80-0xEA8` with implausible
  Y/X values. A first pass couldn't tell a genuine bad write from a
  stale buffer read, so s1967 added a writer-attestation hook at the
  actual `L_1930` store site (`tools/fixup_factor5_ucode.py` Fixup 21)
  and re-ran: **all 14 sampled `order_bad` hits had `stored=0`** (never
  written this cycle) while every ordinary triangle showed `stored=1`
  (positive control confirmed live). The offending bytes are stale
  DMEM left over from the buffer's prior use, not a corrupted command
  reaching the RDP queue — `r16`'s write-pointer legitimately extends
  past what was freshly written that cycle. ORIGIN named: unwritten
  scratch memory, ruled not a writer bug, no mitigation applies. The
  oracle cannot help with the remaining hypotheses: no screenshot
  capability and RSP-HLE never executes guest `L_17F0`, so there is no
  oracle-side equivalent of the `0xD60` capture (confirmed, not
  assumed). H1 (blend/z — needs a `SETOTHERMODE` census, untested) and
  H3 (needs pixel ground truth neither side can supply) remain open.
  Full detail: `PORTING-STATE.md` s1967.
- **H1 mode-state census is out-of-scope in the `0xD60` restage buffer
  (s1968).** The corrected hangar-gated walker recognized 1,134 live
  `0xC8`-class triangles, with ordinary triangles `stored=1` as the same-run
  writer-attestation positive control, but found zero valid standard RDP
  `SETOTHERMODE_L/H` commands (`0xB9`/`0xBA`). Six header matches were
  rejected because their standard operands were impossible (`shift=81..242`,
  `size=90..211`); the first pass counted these false candidates and was
  fixed/re-run in the same iteration. Static generated-code evidence shows
  generic `L_10F4` source-word copies can populate the output buffer while
  `L_1930` emits its triangle headers, and there are no explicit `0xB9/0xBA`
  constants in the generated Factor 5 files. Therefore the null does not
  refute H1: this buffer has no valid mode command to associate with a
  triangle. ORIGIN: invalid candidates are stale/non-command bytes or copied
  source words with malformed operands; they are not legitimate mode state,
  and no mitigation applies. Next scope is the RT64 whole-RDP stream/draw
  state, not another `0xD60` opcode scan. Full detail: `PORTING-STATE.md`
  s1968.
- **Hangar hologram-beam artifact: H1 consumer-state explanation REFUTED
  (s1969, single-source).** The same-run DPC positive control saw 1,128 live
  restaged triangles and the new RT64 consumer census reached its 500-row cap
  at hangar VI 512/origin `0x006AB400`. Of 153 sampled consumer triangles whose
  bounds overlapped the captured beam-cone box, all had the same coherent
  coverage/blender state (`CVG_X_ALPHA=0`, `ALPHA_CVG_SEL=1`, `ZMODE=0`,
  `Z_UPD=1`, `blend=0x0055`); 95 had `Z_CMP=1` and 58 had `Z_CMP=0`. The
  consumer path is therefore reached and no incompatible draw mode was
  isolated. The frame visibly retains the blue beam artifact, but the oracle
  has no pixel witness for this LLE path, so H3 (the remaining pixel/coverage
  explanation) is unavailable rather than selected. No mitigation applies.
- **`slotDispatcherIter+872` SIGBUS is DORMANT (s1973).** 7659 calls in 90s
  hangar run (ROGUESQ_LOG_SLOT_SP_GUARD=1): zero INVALID sp events. H-uninit-stack
  and H-stack-collision REFUTED in hangar context. Two-source with s1972_hangar_300s
  (rc=0, 80 frames, 330s). H-corruption-from-caller cannot be ruled out in a
  mission context. Re-evaluate with mission-entry recipe only.
- Corrected `npcPowerGeneratorUpdate` is main `.text` at `0x80077AF0`;
  regenerated ELF, N64Recomp, fixups, and Debug target pass. Runtime boundary
  tests remain pre-1024 and unevaluable.
- M5 audio de-stubbing is closed. Audio remains stubbed. Dummy-video retail
  watches never reached `musyxInitVoiceFromSample`. Do not reopen without a new
  bounded plan using the Rice hangar recipe.
- **Generated-symbol sweep is effectively closed (s1966).** A full-file
  census found s1962–s1965 had only swept a small tail of the TOML;
  845 leftovers resolved in one batch (902 → 57 `func_8[01]*`). The
  remaining 57 all need genuine RE or are deliberate holds (live
  `patches/heap_guards.c` declarations, `build_redefs.py` reverts, one
  `PROJECT-OVERVIEW.md`-parked entry, overlay-VRAM collisions, and
  entries with no generated-tree match at all) — not a metadata-sync
  target anymore. Full detail: `PORTING-STATE.md` s1966.
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
  `+0x1A` / YL/YM/YH `== 0x8000`. s1872 hangar/512 was UNEVALUABLE
  (no hangar origin); s1949 published hangar and selected
  H-never-live there (see Durable).

## Active investigation and ranked next steps

Re-ranked s1976: in-loop MusyX tick does not idle the drain; force-idle
does not restore `fs`. Next discriminator is which slot bytes stay
nonzero (idx / byte / chCount / flicker after tick).

1. **Hangar frame-freeze: leftover slot bytes never idle (s1976).** Drain
   call=1 at origin `0x00656400` (craft-select, after hangar `0x006AB400`)
   spun 10M iters with `tickMusyXIfActive` in the loop, gate `0x800A0F50=1`.
   Timeout forced idle; function returned; `fs` stayed 1215 and `[lle task]`
   stopped. Dump `isAudioSlotActive` idx+byte and `chCount` (`0x80141AD0`)
   on the existing `[drain-tick]` samples. Discriminators: one zombie idx,
   all slots stuck, wild chCount, or bytes that clear then re-key.
2. **slotDispatcherIter+872 SIGBUS: DORMANT (s1973).** 7659 calls in 90s hangar
   run with ROGUESQ_LOG_SLOT_SP_GUARD=1; zero INVALID fires. H-uninit-stack and
   H-stack-collision REFUTED for hangar context (two-source with s1972_hangar_300s
   300s clean). H-corruption-from-caller cannot be ruled out in mission context.
   Do not add mitigation. Re-evaluate only with a mission-entry recipe or a new
   crash with this signature.
3. Hangar visual artifacts (geometry cracks, blue tris, hologram layering).
   H2 (malformed triangle) REFUTED s1967; H1 (consumer draw state) REFUTED
   s1969 (single-source). H3 (pixel/coverage) unavailable — oracle has no
   screenshot for LLE path. Hologram-beam artifact remains open. Do not add
   mode-state mitigation or repeat the `0xD60` scan. Captured s1976 hangar
   frame is AVAILABLE CRAFT / AMBUSH AT MOS EISLEY with the blue beam.
4. 600s hangar soak (s1974_hangar_600s): done. rc=137 SIGKILL at cap, hangar
   at 26.9s, audioDrain yields n=1,2,3, last slot-ret drain n=16, `fs=1248`
   through update_screen #35904, 0 crashes. Freeze is a hang.
5. Mission-entry: SDL key delivery fails after Start #6 (31s from boot) due to
   likely macOS focus drop. Do not run more mission-entry probes until the
   frame freeze is diagnosed.
6. Keep audio closed unless a new bounded lead reaches initialization.
7. M3: only as complete idiom-class audits with a named discriminator.
8. Runtime probes: `tools/oracle/README.md` + `docs/F5-UCODE-REFERENCE.md`;
   batch arms; phase-gate; SIGKILL; queue soaks. Hangar recipe is
   `ROGUESQ_SPIN_YIELD=1` + eleven-Start from boot. Ask (b) remains
   human-only.

## Durable boundaries

**M3 dispatcher/frame origin. DORMANT (s1973).** s1162: 144 direct
`slotDispatcherIter` calls in 72 generated callers; caller entries, stack pairs,
and saved-`$ra` contracts match. No static indirect target to `0x8003E8DC`. One
executable `r29` initializer in `run_thread_function`. s1973: 7659 calls in 90s
hangar run with sp guard active; zero INVALID sp events; H-uninit-stack and
H-stack-collision REFUTED (hangar context). Two-source with s1972_hangar_300s clean soak.

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
single-source). s1872 hangar/512 was UNEVALUABLE (no hangar origin).
s1949 published hangar `0x006AB400` and selected H-never-live there:
2187 hangar `L_17F0` entries / 3904 flushes with `y8000_any=0`, plus a
recognizable 3D hangar frame. Late-hangar Y unsampled (4s crash).

**Attract 1024 presenter.** Leave adds `submitGfxFrame` +104/+102 without a new
screen-handler entry. Callee-side `prev_pc` attributes every present: eight
ROM jals, of which `menuControllerInput` `0x800B8014` rises and
`runInMissionFrame` `0x800FAD90` drops, net matching the extra (s1808 H2).
VRAM jal/entry watches at overlay addresses are not a second source.

**Hangar RDP consumer state.** s1969: with the DPC writer-attestation control
live, `decodeTriangles` reached the actual `drawTris` consumer for 500 rows in
the hangar origin `0x006AB400` window. The 153 rows overlapping the captured
beam-cone box had `blend=0x0055`, `ZMODE=0`, `Z_UPD=1`, `CVG_X_ALPHA=0`, and
`ALPHA_CVG_SEL=1`; the sample split was 95 `Z_CMP=1` / 58 `Z_CMP=0`. This is
single-source evidence against an incompatible consumer mode, not pixel
ground truth.

**bltzal $zero link-register class. CLOSED (s1971).** s1970 found ctx->r31=0
at the `filterVoiceSampleBlock` site; s1971 completed the class census: six
`bltzal $zero` PIC-idiom sites in `funcs_27.c` (across three functions)
never received their `ctx->r31 = PC+8` write. The `fixup_game_funcs.py` s1971
patch applies all six. Hangar ran 60s / 17 frames with no SIGBUS after the fix,
vs 1 frame / 4s before. Class is fully enumerated and patched; no remaining
sites elsewhere in the generated codebase. Do not reopen without a new site
identified by grep + static analysis.

## Superseded conclusions

Older overturned claims live in `PROJECT-OVERVIEW.md` §26, §35, and §36.
Most recent, still load-bearing for the next unit:

- s1888–s1917 "stall at 640 then crash" is superseded by s1918 — 2/8 logs
  live 180s with no crash and no `osViSetMode width=1024`.
- H-slots-stay-live is superseded by s1942 — two `yield_self_1ms` calls
  unblocked recv1 and the guest issued `#9/#10`.
- Eleven-Start-from-boot as a hangar recipe *without* yielding
  `L_800B8050` is still wrong (s1943–s1947 stay at title 1024).
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
- s1943–s1947 "eleven-Start stays at title 1024" is superseded by s1949
  — those runs did not yield `L_800B8050`. With that yield, hangar
  `0x006AB400` publishes at 26.1s.
- Hangar/512 live `0x8000` Y parked UNEVALUABLE (s1872, s1888, s1943,
  s1944) is superseded by s1949 — hangar origin published and
  `y8000_any=0` on that window.
- s1968's first H1 census pass, which treated any `0xB9/0xBA` header as a
  mode command, is superseded by the fixed rerun: all six matches had
  impossible standard operands and were false candidates, while valid mode
  count remained zero.
- s1970's first audit attempt without the proven LLE-solo hangar environment
  stalled at VI 640 and produced no audit rows; it is recipe failure, not a
  null result. The corrected run reached VI 512 and supplied the positive
  control before selecting H-filter-local-range.
- "First hangar window is short (~4s / 1 frame / SIGBUS filterVoiceSampleBlock)"
  is superseded by s1971 — bltzal $zero link-register fix eliminated the crash;
  hangar now stable 60s+ / 17 frames with no SIGBUS.
- "Needs investigation before calling the hangar fully stable" (s1971 audioDrain
  observation) is superseded by s1972 — audioDrain spin-yield gate closes the
  class; 180s hangar stable / 48 frames / zero crashes. The later #2176 freeze
  is a different drain-idle failure, not a missing yield.
- s1975 "anyAudioSlotActive returns 0 because no slot keyed on" and "add
  tickMusyXIfActive inside the spin to match menuControllerInput" are
  superseded by s1976 — the return is inverted (1=idle); menuInput is the
  same one-tick-then-poll shape; 10M in-loop ticks with gate=0x01 never
  idled; force-idle did not restore `fs`. s1975's "drains 1–16 completed"
  was slot-ret-caller n (per-site anyAudioSlotActive polls, no v0), not
  drain function returns.

s1919–s1941 caller / slot / mix / VI-recv supersessions are archived in
§36 rather than restated here.

## Evidence ledger summary

Per-session rows through s1879 live in `PROJECT-OVERVIEW.md` §33–§35.
s1880–s1917 leftover remaps, the s1888–s1949 VI-1024 / spin-yield /
title-SI / hangar chain, and the s1950–s1959 leftover remaps live in §36.
s1961–s1965 leftover remaps are in `PORTING-STATE.md` directly (not yet
archived to §36). s1968's H1 scope result, s1970's filter audit, and s1971's bltzal class fix
are in `PORTING-STATE.md` directly.
s820–s1239 closed post-sec2 / M3 / audio / VI (dummy-video retail-entry
later superseded by Rice). s1728 and s1948 are maintenance only; s1960 is
loop-infra only (unblock: grok runner balance exhausted, refuted as a
loop-stopper since the loop already runs under `RUNNER=claude` — no
porting conclusion touched, see `PORTING-STATE.md` s1960).

## Method and safety rules

- A null result is worthless without a same-run positive control. Batch all A/B
  arms in one build/run; scope budgets to the VI phase; never compare animating
  scenes by stopwatch. Read the Factor 5 reference before interpreting a DL or
  RDP anomaly. Regen: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, CMake.
  Never `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. `lib/` edits require patch export. Before any mitigation,
  name the writer and legitimacy with `ORIGIN:`.
