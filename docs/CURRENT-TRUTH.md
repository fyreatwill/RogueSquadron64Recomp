# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is in
[`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is the authority for session
detail. Reviewed through s1998 (2026-08-19).

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
  not for a key-on. In-loop `tickMusyXIfActive` never idled call=1;
  force-idle did not restore `fs`. s1978: `0x801714D0` is a live
  `allocateSongChannelArray` table, last alloc count=18 matching `ch=18`
  (tickn=4; boot 16-voice `0x8018D4A0` is tickn=2). `musyxRenderVoiceSamples`
  writes `0x02` here (16967 slot-sb) and `isAudioSlotActive` reads `0x02`
  (135/184 slot-byte samples at this base). H-ascii-heap / H-count-desync /
  H-never-keyed REFUTED; H-voice-records SELECTED. s1977's ASCII leftover
  dump used `MEM_BU` with a 32-bit unsigned KSEG0 address, which
  zero-extends against `0xFFFFFFFF80000000` and reads host memory at
  rdram+4GiB — not RDRAM. Always pass `S32(guest_addr)` into `MEM_*`.
  ORIGIN: `musyxRenderVoiceSamples` (legitimate `0x02` key-on). Drain is
  correctly waiting. s1979 selected H-subset-live: of 18 slots at
  `0x801714D0`, 12 stay `0x02` with `cross_n=0` through the 10M timeout
  (idx 0–4, 6, 7, 13–17); only a 4-voice subset cursor-crosses and
  lands `slot-sb new=0x00`. H-end-zero-lost / H-rekey-after-end /
  H-zero-unlogged REFUTED. s1980 selected H-not-at-cursor: those 12
  have `vis=0` at `L_80090150` through 108 drain-tick samples while
  still taking 155 `slot-sb new=0x02` each. s1981 selected
  H-slot40-skip: the 12 have `slot+0x40 != 0`, `skip084=155`
  matching those 155 writes, `to_cur=0`; the four ended (this run
  5/10/11/12) have `w40==0`, `skip084=0`, `to_cur==vis>0`, last
  `pos+step >= cur`. After skipping 084 they split `L_80090188` vs
  `0x800900B8` on `$a2 < $a0+$s4` -- that split is not why they miss
  the cursor. H-loop-wrap / H-a2-gate / H-idx-unmapped REFUTED
  (`unmap=0`, `vis==to_cur` on every idx). s1982 selected
  H-later-overwrite: the writer is `musyxInitVoiceFromSample`
  `sw 0x40($a0)` at `0x80092230` from `desc+0x14`. `last_init==w40`
  on all 18 idxs (`ninit` 1..22, all `armed=0`); `nsw=nsh=0` on
  idxs 0–17. `musyxKeyOnVoice` `0x80090B68`/`0x80090C28` write a
  different structure (stride ~0x50, `keyon_unmap` 18366→20372).
  H-keyon-sw / H-keyon-sh / H-stale-word REFUTED. s1983 selected
  H-start-end-triplet: 256/256 `[init-desc]` inits are oneshot
  (`d14==0` and `d10==0x11`, n=125), whole-sample loop
  (`d10==0` and `d14==d0c`, n=3), or loop length
  (`d14==d0c-d10`, n=128). `d00` low-16 is the sample rate
  (22050/16000/24000/…). `d14` is not a pointer, 0/1 flag, or
  rate. H-loop-flag / H-rate-as-flag REFUTED. Live drain voices
  are the looping ones; `bnez slot+0x40` is the legitimate
  loop-length skip. `ninitd=0`: that length is never cleared.
  s1984 dest-mapped the four named stop sites: `stopVoiceMarkRetrigger`
  165/165 mapped (81 boot `0x8018D4A0`, 84 hangar `0x801714D0`);
  8 hangar dests fire after tickn=4 alloc and before drain, each
  immediately followed by `musyxInitVoiceFromSample` of the same
  idx then render `slot-sb old=0x01 new=0x02`. `musyxStopVoice` 0,
  `deactivateVoice` 0; `stopVoice` n=1 after the 10M timeout
  (dest `0x80153420` unmapped, `armed=1`). Slot+0 is still `0x02`
  at drain because MarkRetrigger is the retrigger path (zero
  status, `+0x85=1`, re-init), not a key-off. s1983's "zero on
  hangar" was the s1927 first-32 `slot-sb` rate-limit.
  ORIGIN: sample-header loop length (legitimate); MarkRetrigger
  retrigger (legitimate). Drain waits on looping hangar BGM that
  was just retriggered. Timeout remains a diagnostic hatch.
  Default-off yield unchanged.
  s1985 dest-mapped the remaining stop/release family. tickn=4→drain
  window: `musyxStartVoiceRelease` 2 hangar (idx 2, 5), `stopVoiceByKey`
  1 dest=`0xFF`, MarkRetrigger 8 retrigger, fade/handle/slot-synced
  /`stopVoiceByHandle`/`Locked` 0. At drain start (after
  `[drain-stop-sum]`, first `tickMusyXIfActive`): `stopVoicesByHandle`
  8 song handles (`0x17`..`0x11`) each followed by
  `beginVoiceFadeRelease` on hangar idxs 4,3,17,16,14,15,13,2; static
  caller is `stopSongByHandle` `0x8009582C`. Fade then sweeps all 18.
  Slot+0 stays `0x02` on looping voices through 10M. `ra=0` on every
  dump: N64Recomp jal omits `ctx->r31`; static MarkRetrigger caller is
  `tickAudioChannel` (note engine). H-missing-song-stop REFUTED.
  H-song-stop-unmapped SELECTED for the handle. H-drain-expects-bgm-end
  SELECTED: song-stop starts fade, looping BGM never idles.
  s1986: slot+0x30 stays `0x14` and slot+0x6C stays 3 on every
  hangar idx through 108 `[drain-path]` samples (iters 1–10M);
  dump is after in-loop `tickMusyXIfActive`. Loopers 0–4, 6, 7,
  13–17 keep `b=0x02`; oneshots 9–12 go idle and stay idle.
  H-fade-timer-stuck SELECTED; H-fade-counts-no-zero /
  H-fade-zeros-rekey REFUTED. `beginVoiceFadeRelease` n
  155→181333 during the spin (rewrite of `0x14` every tick).
  s1987 dest-mapped every hangar `sh` to slot+0x30: during drain
  the only hangar writer is `beginVoiceFadeRelease` val=`0x14`
  (narmed=135611, nlt14=0, nother=0). Render `0x80090570` n=0;
  render `0x80090688` n=575 nhangar=0 (dests `0x80175F30`/
  `0x80177D90`); ADSR hangar n=115 narmed=0 val=`0xDBDA` (all
  pre-drain). Release hangar n=21 narmed=0 val=`0x14`. Unique
  hangar (site,val) during drain is one row: fade `0x14`.
  H-no-decrement SELECTED; H-dec-then-rewrite REFUTED.
  Fade then `lhu +0x30` and `sh` that value to slot+0x58
  (`0x800924E4`) after `+0x6C=3`. s1988: that copy is the
  duration, not elapsed. On every looper through 10M (108
  samples) `h58=0x0014` `w64=0` `w68=0x3F800000`; `h58` never
  counts down. `w60` is 0 on 103/108 samples and `0x0008B000`
  on 5 (all 12 loopers, same iters). Static:
  `advanceVolumeFadeEnvelope` (`0x8008F4D8`) adds `$a1` into
  +0x60 (`0x8008F64C`) and treats +0x58 as duration; fade
  zeros +0x60 every call (`0x800924DC`). H-working-timer-is-0x58
  REFUTED; H-envelope-fields-stuck SELECTED for +0x58/64/68.
  s1989 dest-mapped those +0x60 stores. Envelope hangar-armed
  n=2690 n0=0 n8b=2678 lastval=`0x8B000`; fade-zero narmed=
  131404 n0=131404 matching `[h30-sum]` fade narmed. Unique
  envelope vals are `0x8B000*N` (uniq overflow 137614). Dump
  loopers stay 0 (1391) with 40 mid-tick `0x8B000` races.
  H-envelope-never-called / H-step-is-zero REFUTED;
  H-fade-rearms-zeros-elapsed SELECTED. Fade has two static
  callers: `stopVoicesByHandle` n=30 and `stopAllSynthVoices`
  (`0x8008DBF4`) from every `tickMusyXIfActive` (`$a0=0`);
  the sweep is `blez`-gated on `lbu 0x80141AD0`.
  s1990 selected H-stop-all-gate-stuck: `[stop-all-sum]
  n=10073 narmed=10064 n_skip=0 n_work=10073 lastgate=18
  nchg=5`. Gate changes 20→17→16→15→18 are all pre-drain;
  then stuck at 18 through 10M (same byte as drain-slots
  `ch=` / `allocateSongChannelArray` count=18). In-loop
  ticks 64+10000=10064 match narmed. StopAll-fade narmed=
  181152 = 10064×18; handle-fade narmed=0 (n=31, all
  pre-drain). Fade-zero narmed=134878 is the live-slot
  subset. `0x80141AD0` is the allocated voice count
  (`sb` in `setDisplayMode`/`reapplyDisplayMode`, clamp
  0x20), not a pending-stop flag, so it never drops.
  Every drain tick therefore re-fades every live voice.
  H-stop-all-skips / H-stop-all-once REFUTED.
  s1991 selected H-empty-then-fade: `[stop-all-path-sum]
  n=181301 narmed=181152 n_empty_armed=181152
  n_free_armed=0 lastv0armed=0`. Every drain-armed
  `lw 0($s2)` at `L_8008DC50` is 0; the 13 FREEs are
  pre-drain (n_free=13). Empty-slot fade jal narmed
  matches 10064×18. Synth objects at `0x8013D880`
  stride `0x17C` stay empty; `beginVoiceFadeRelease(idx)`
  still hits live `0x88` voices. H-free-every-tick /
  H-free-once REFUTED.
  s1992 selected H-drain-inloop-only:
  `[tick-site-sum]` drain-inloop n=10064
  narmed=10064 matching `[stop-all-sum]` narmed;
  drain-entry n=1 narmed=0 (ROM jal `0x800B24CC`
  before armed); waitForAnyAudioSlot n=3,
  menuOverlayInit n=3, menuControllerInput n=1,
  runMenuModelViewerScreen n=1, all narmed=0;
  the other five ROM jals 0. H-drain-entry-plus-inloop
  / H-other-tick-sites REFUTED. ORIGIN: s1976 host
  injection inside the drain spin, not a ROM jal.
  The ROM drain is one entry tick then spin; each
  injected tick re-fades all 18 live voices.
  s1993 selected H-injection-prevents-idle for
  drain (not for fs): `ROGUESQ_DRAIN_INLOOP_TICK=0`
  skipped the injection (`[drain-inloop-gate] en=0`,
  drain-inloop n=0 narmed=0). No `[drain-timeout]`.
  `[drain-exit] call=1 iters=300000 v0=1`. All 18
  hangar slots `b=0x00` at that dump (16 were `0x02`
  at iters=1/8/100000/200000). Envelope hangar-armed
  n=48 stepped `0x8B000`/`0x116000`/`0x1A1000`;
  stopAll narmed=0; fade narmed=0. H-need-envelope-
  without-stopall / H-other-keep-alive REFUTED.
  Default stays ON. ORIGIN: s1976 host injection
  (not a ROM jal); skipping it restores the ROM
  one-entry-tick then spin, and yield-unblocked
  synth lets the ROM fade finish. Residual: fs
  still frozen from `#2112` after drain-exit (same
  freeze as s1976 force-idle). Drain is the
  craft-select exit path (`tickCraftSelectScreen`
  loop at `0x800C5EA4`, overlay func currently
  named `drawRadarIcon`).
  s1994 selected H-later-drain-jal site=
  `finalizeCurrentSpeechBuffer`: with the same
  in-loop-off recipe, arbiter/destroy/shutdown
  all nenter=1 nexit=1; finalize nenter=1
  nexit=0; 0 `[craft-select-s0]`. H-arbiter-wait
  / H-caller-returned / H-drain-exit-never-
  reached-again REFUTED. First jal inside
  finalize is always `shutdownMusyXVoices`
  (`0x8009BCC4`).
  s1995 selected H-shutdown-musyx: three
  finalize entries in the run; calls 1–2
  (pre-title, pre-hangar) both-edge shutdown
  then teardown (`[fin-a0] a0=0 beqz=1`);
  call 3 (post `[drain-exit]`) is shutdown
  nenter=3 nexit=2, no `[fin-a0] n=3`,
  teardown stays 2, 0 `site=free` entire run.
  Wrap both-edged on the two earlier shutdown
  calls (function can return). `[fin-slot]`
  dumped only nenter==1 (pre-title zeros) —
  not the hanging call. H-rs-free /
  H-teardown-dma / H-finalize-body REFUTED.
  s1996 selected H-slot-spin: inner wraps
  show call-3 `stopVoiceSlotSynced`
  nenter=3 nexit=3 (H-stop-synced REFUTED);
  find-zero / free-opt / free-tail stay at
  nenter=2 (H-find-zero / H-tail-free
  REFUTED). `[shut-enter] n=3 b0=0x02`;
  then `[shut-spin]` n=3..1.63e10 with
  `v0=b0=0x03` `a0=0 != a1=1`. Calls 1–2
  both-edged every inner site and exited
  the spin in one iter (`n=1,2 v0=b0=0x00
  a0==a1`, same-run control). Writer of
  `0x03` is `stopVoiceSlotSynced`
  `sb 0x8009B30C` after the status==2
  recv/stop/send (legitimate stop-in-
  progress). Spin waits for slot-0 idle.
  Named zeroers of `D_80154620`:
  `serviceVoicePoolFrame` `0x8009B7A8` /
  `0x8009B7EC` (and init / status==1).
  No store changed. Default-off in-loop
  tick unchanged.
- **s1997 serviceVoicePoolFrame schedule census.** The retail oracle passed
  its whole-RDRAM positive control (10,015 callbacks) and independently saw
  legitimate writes to physical `0x154620` from `0x8009B7EC` (plus init/stop
  paths). In the port, the same-run worker control reached `n=1000` with
  `gate=1` before shutdown call 3; after `[shut-enter] n=3`, no armed
  `serviceVoicePoolFrame` entry appeared in the fixed every-armed-entry
  census, while `[shut-spin]` held `b0=0x03` through the 60-second hangar
  window. `[shut-enter]` call 3 had `gate=1`, and calls 1–2 exited their
  spins. H-service-starved is selected; H-service-skips and H-service-
  rewritten have no armed worker entry to execute. The port store-site
  probes were null and are not used as independent evidence. ORIGIN:
  serviceVoicePoolFrame's status-zero stores are legitimate retail worker
  writes; no store or game state was changed by this iteration's probes.
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
- **M5 audio plan written (s1998).** `docs/M5-AUDIO-PLAN.md` now inventories
  the live task stub, stock `aspMain` stub, generated guest gates, voice and
  table guards, waits, drain timeout/tick, status-3 shutdown spin, scheduler
  yield, AI status shortcut, SDL fallback, and DMEM lock. It separates the
  MusyX task/engine question from the still-unproven MORT codec boundary and
  gives every proposed step a control, VI phase, soak, and rollback. No audio
  runtime behavior changed in s1998.
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

Re-ranked s1998: the M5 inventory is complete; its ground-truth and generated
source reconciliation is next. The hangar status-3 result remains parked with
a precise scheduler lead.

1. **M5 ground truth and generated-gate reconciliation (s1999).** Run the
   retail oracle with a whole-RDRAM positive control and inspect the target
   physical writes around the audio gates, then reconcile those results with
   `fixup_game_funcs.py`, generated `funcs_23.c`, and the host M_AUDTASK
   dispatch. Do not de-stub or repair a gate until the writer and legitimacy
   are identified. Use the exact measurement in `scratch/agent/NEXT.md`.
2. **Hangar frame-freeze: status-3 worker starvation (s1997).** The fixed
   census reached hangar `[phase] 512 origin=0x006AB400` in 24.6s and captured
   17 frames. `[svc-pool]` reached `n=1000 armed=0 gate=1`; after
   `[shut-enter] n=3 b0=0x02 gate=1`, zero armed worker entries appeared,
   while `[shut-spin]` held `b0=0x03` and stop-synced returned. The retail
   oracle independently saw the worker-side `0x8009B7EC` write. After M5's
   plan, identify the callback/thread dispatch path that should run
   `serviceVoicePoolFrame` and test whether the cooperative status-3 spin
   prevents it. Do not yield the spin or default the in-loop tick off.
3. **slotDispatcherIter+872 SIGBUS: DORMANT (s1973).** 7659 calls in 90s hangar
   run with ROGUESQ_LOG_SLOT_SP_GUARD=1; zero INVALID fires. H-uninit-stack and
   H-stack-collision REFUTED for hangar context (two-source with s1972_hangar_300s
   300s clean). H-corruption-from-caller cannot be ruled out in mission context.
   Do not add mitigation. Re-evaluate only with a mission-entry recipe or a new
   crash with this signature.
4. Hangar visual artifacts (geometry cracks, blue tris, hologram layering).
   H2 (malformed triangle) REFUTED s1967; H1 (consumer draw state) REFUTED
   s1969 (single-source). H3 (pixel/coverage) unavailable — oracle has no
   screenshot for LLE path. Hologram-beam artifact remains open. Do not add
   mode-state mitigation or repeat the `0xD60` scan. Captured s1976 hangar
   frame is AVAILABLE CRAFT / AMBUSH AT MOS EISLEY with the blue beam.
5. 600s hangar soak (s1974_hangar_600s): done. rc=137 SIGKILL at cap, hangar
   at 26.9s, audioDrain yields n=1,2,3, last slot-ret drain n=16, `fs=1248`
   through update_screen #35904, 0 crashes. Freeze is a hang.
6. Mission-entry: SDL key delivery fails after Start #6 (31s from boot) due to
   likely macOS focus drop. Do not run more mission-entry probes until the
   frame freeze is diagnosed.
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

- The historical s298–s373 M5 plan is superseded as the current work plan by
  s1998: its dummy-video closure and old audio-bridge assumptions did not
  inventory the current task stub, generated gates, waits, or MORT/MusyX
  uncertainty. The new plan is design-only until oracle and generation
  ground truth are reconciled.
- s1998 found a generated-source discrepancy: the fixup force-zero regex for
  `0x8008EC88` misses the current output because a probe call sits between the
  instruction comment and the store; the generated reapply-display tail
  therefore writes `1`. This is not yet a mitigation or a runtime conclusion.
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
- s1976 "Writer is the game's own voice key-on" / leftover bytes as
  legitimate `0x02` key-on status is superseded by s1977 — 13 frozen
  nonzero bytes at `0x801714D0` are ASCII-shaped and none are `0x02`;
  the table is not the boot `0x8018D4A0 count=16` array.
- s1977 "ASCII leftover / not `0x02`" is superseded by s1978 — the
  `[drain-slots]` dump used `MEM_BU(0, unsigned_kseg0)`, which
  zero-extends and reads host memory at rdram+4GiB. Same-run
  `slot-sb`/`slot-byte` (gpr addresses) see live `0x02` at that table;
  last `slot-alloc` is count=18 matching `ch=18`. Believable because
  the dump printed a stable hex/ASCII line 108 times.
- s1978 "whether render-end's `sb $zero, 0x28($sp)` lands on slot+0"
  is superseded by s1979 — the four post-drain ends (idx 9–12) each
  have a matching `musyxRenderVoiceSamples` `slot-sb new=0x00`;
  H-end-zero-lost / H-rekey-after-end / H-zero-unlogged REFUTED.
  Believable because the s1927 rate-limit dropped `new==0` after the
  first 32 events.
- s1979 "they almost certainly pass `L_80090150` because `slot-sb` is
  after that compare in the same function" is superseded by s1980 —
  `vis=0` on the 12 live idxs through the whole drain while
  `slot-sb new=0x02` keeps firing. Believable because the write is
  later in the same function; the `0x80090084` fallthrough skips the
  compare and still reaches the `0x28($sp)` tail.
- s1980 "nonzero `slot+0x40` skips straight toward `L_80090188`" is
  superseded by s1981 — they skip 084, then split 188 vs 0B8 on
  `$a2 < $a0+$s4`. Believable because 084 is the only skip before
  those two labels.
- s1981 "static candidate writer of slot+0x40 is `musyxKeyOnVoice`"
  is superseded by s1982 — those stores write a ~0x50-stride
  structure, not the 0x88 voice table; `musyxInitVoiceFromSample`
  copies `desc+0x14` and `last_init==w40`. Believable because both
  functions use `$s1`/`$a0` as "the voice" in different layouts.
- s1982 "whether a nonzero `desc+0x14` is a legitimate skip-end
  flag" is superseded by s1983 — it is loop length, with
  `d14==d0c-d10` (or `d14==d0c` when `d10==0`; or `d14==0` with
  `d10==0x11` for oneshots) on 256/256 inits. Sample rate is
  `d00` low-16. Believable because the live values sat in a
  16-bit scalar band that could have been either a rate or a
  length.
- s1983 "`stopVoiceMarkRetrigger` 32/32 dests on boot `0x8018D4A0`,
  zero on hangar `0x801714D0`" and "voices were never stopped" are
  superseded by s1984 — 84 hangar dests (n=82–165) were hidden by
  the s1927 `slot-sb` rate-limit (`n<=32 || n%1000==0 || newb==2`;
  MarkRetrigger writes `newb=0`). The 8 post-tickn=4 hangar dests
  each re-init the same idx before drain. Believable because the
  first 32 dumps were all boot-table.
- s1984 "drain waits because looping BGM was just retriggered /
  no song-stop in the four named sites" is superseded by s1985 —
  `stopSongByHandle` → `stopVoicesByHandle` (8 handles at drain
  start) → `beginVoiceFadeRelease` on hangar idxs; MarkRetrigger
  `$ra` is 0 because jal omits `ctx->r31`, static caller is
  `tickAudioChannel`. Believable because the pre-drain window had
  no handle-stop (those fire as drain's first tick).
- s1985 "whether fade counts down, skips the end-zero, or zeros
  then re-keys" is superseded by s1986 — `h30=0x0014` and
  `b6c=0x03` on every looper through 10M (108 samples, dump after
  tick). Believable because fade n=155 at entry already proved the
  envelope started; the missing field was the timer itself.
- s1986 "either nothing decrements +0x30 or a decrement is
  overwritten before the dump" is superseded by s1987 — unique
  hangar (site,val) during drain is only fade `0x14` (narmed=
  135611); render/ADSR hangar-armed stores are 0. Believable
  because fade n-growth already showed a rewrite every tick, which
  can hide a mid-tick decrement from a dump-after-tick.
- s1987 "the working counter may be +0x58" is superseded by
  s1988 — `h58` is frozen at the fade copy `0x14` through 10M
  (duration). Elapsed is the word at +0x60. Believable because
  fade's next instruction after `+0x6C=3` is `sh +0x30 → +0x58`.
- s1988 "whether fade zeros +0x60 after the add in the same
  tick, vs envelope never running / step 0" is superseded by
  s1989 — envelope hangar-armed n=2690 stores `0x8B000`-class;
  fade-zero narmed=131404 all val=0, matching the +0x30
  rewrite. Believable because dump-after-tick saw 5× `0x8B000`
  which could have been another writer.
- s1989 "whether `stopAllSynthVoices` blez-skips, runs once,
  or stays gated on" is superseded by s1990 — n_skip=0,
  n_work=10073, lastgate=18 through 10M, stopAll-fade
  narmed=181152=10064×18. Believable because `0x80141AD0`
  could have been a pending-stop flag that should drop; it
  is the allocated voice count.
- s1990 "whether each loop iter FREEs an occupied 0x17C
  synth or only empty-slot fades" is superseded by s1991 —
  n_free_armed=0, n_empty_armed=181152. Believable because
  a0=0 takes FREE whenever 0($s2) is nonzero; the synth
  table is already empty when drain starts.
- s1991 "which of tickMusyXIfActive's call sites produces
  the 10064 armed stopAll" is superseded by s1992 — all
  10064 are the s1976 in-loop injection; the 10 ROM jals
  narmed=0. Believable because the ROM drain jal at
  `0x800B24CC` is a real tick, but it runs before armed.
- s1992 "whether the s1976 in-loop tick is why drain
  never idles" is superseded by s1993 — with it gated
  off, drain returns at 300k with all 18 slots idle.
  Believable because every armed stopAll was that
  injection re-fading duration 0x14.
- "Hangar freeze is the drain-idle spin" (s1974–s1992)
  is superseded by s1993 — drain returns and fs stays
  1245 from `#2112` (two-source with s1976 force-idle).
  Believable because drain never returned while the
  injection was on, so the spin and the freeze were
  simultaneous.
- s1993 "next ROM jal after drain-exit is
  `bufferArbiterProducerScanWait`" as the hang
  site is superseded by s1994 — arbiter, destroy,
  and shutdown all return; finalize does not.
  Believable because arbiter is the next
  instruction and contains blocking `osRecvMesg`.
- s1994 "next is finalize's three jals /
  which of rs_free vs teardown vs shutdown"
  is superseded by s1995 — shutdown call 3
  nenter=3 nexit=2; free never entered;
  teardown stayed at 2. Believable because
  finalize is 84 bytes with three jals and
  the first is unconditional.
- s1995 "which inner site of
  shutdownMusyXVoices hangs on call 3"
  is superseded by s1996 — stop-synced
  returns; the `L_8009BD10` spin runs
  with `D_80154620==0x03` and never
  reaches find-zero. Believable because
  finalize's first jal is unconditional
  and the function has several later
  blocking-looking sites.

s1919–s1941 caller / slot / mix / VI-recv supersessions are archived in
§36 rather than restated here.

## Evidence ledger summary

Per-session rows through s1879 live in `PROJECT-OVERVIEW.md` §33–§35.
s1880–s1917 leftover remaps, the s1888–s1949 VI-1024 / spin-yield /
title-SI / hangar chain, and the s1950–s1959 leftover remaps live in §36.
s1961–s1965 leftover remaps are in `PORTING-STATE.md` directly (not yet
archived to §36). s1968's H1 scope result, s1970's filter audit, s1971's bltzal class fix,
and s1978–s1992 drain-slot identity / subset-live / skip-cursor /
slot+0x40-skip / init-writer / loop-length / stop-dest-retrigger /
stop-family song-handle-fade / fade-timer-stuck / +0x30
store-census (H-no-decrement) / +0x58-duration (H-envelope-fields-stuck)
/ +0x60 dest-map (H-fade-rearms-zeros-elapsed) / stopAll gate
(H-stop-all-gate-stuck) / stopAll L_8008DC50 path
(H-empty-then-fade) / tickMusyXIfActive caller census
(H-drain-inloop-only) / s1976 in-loop tick gate
(H-injection-prevents-idle for drain; fs residual)
/ s1994 post-drain jal census (H-later-drain-jal
site=finalizeCurrentSpeechBuffer)
/ s1995 finalize inner-jal census
(H-shutdown-musyx; call 3 never returns)
/ s1996 shutdown inner-site census
(H-slot-spin; call 3 D_80154620 stays 0x03)
/ s1997 serviceVoicePoolFrame census
 (H-service-starved; no armed worker entry)
/ s1998 M5 audio inventory and reversible de-stubbing plan
 (H-MORT-path / H-degenerate-host-path / H-MusyX-mismatch / H-scheduler-independent;
  design complete, ground truth next)
results are in `PORTING-STATE.md` directly.
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
