# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); detailed session records stay
in the ledger. Reviewed through s1240 (2026-08-15).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu explanation is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Any new mitigation requires an `ORIGIN:` naming the
  writer and assessing whether the value is legitimate.
- Phase-gated port captures can reach VI width 1024 with independent
  emit/raw/dispatch/match controls. Pre-chain crashes are disjoint families;
  they do not classify parser loss. Ordinary late E9 producer/consumer
  identity is established; synthetic FULL_SYNC was absent in the decisive
  capture. Remaining deltas are boundary/span-shaped and unclassified.
- The recurring `slotDispatcherIter+872` SIGBUS is the generated prologue
  spill of guest `$sp` at `funcs_8.c:22810`. The complete generated audits
  found balanced direct callers, no static indirect target, no runtime `$sp`
  replacement, and no reachable frame-overlapping writer in the audited
  stack, dynamic-copy, wide/narrow/word/partial-store, and load idioms.
  Runtime-side guest memory/value corruption remains open; no mitigation is
  justified.
- The corrected `npcPowerGeneratorUpdate` boundary is sourced as main `.text`
  at `0x80077AF0`; regenerated ELF, N64Recomp output, fixups, and Debug target
  pass. Runtime boundary tests stayed pre-1024 and are unevaluable.
- The complete generated `do_sdl`/`do_sdr` census found five emitted calls.
  The `0x8003A3AC` call lies in the `pows`/`D_8003A4C4` data interval, and the
  four `audioCompandS16` calls lie in a malformed oversized generated body
  with 214 trapped cross-function gotos. No reachable target-path writer or
  frame-overlapping span was established. The helper's aligned-dword merge and
  two-word write are exact by static inspection (single-source evidence).
- M5 audio de-stubbing is closed. Audio remains stubbed. Retail execution
  watches passed whole-RDRAM controls but stayed at VI 320 and never executed
  the four identified `musyxInitVoiceFromSample` writers. Do not reopen without
  a new independent lead reaching audio initialization or voice allocation.
- Retail oracle controls are healthy: whole-RDRAM, scheduled PIF input, and VI
  callback/poll controls pass. The current oracle recipe stalls at width 320 /
  origin `0x006dd280`; its target watches are therefore unevaluable.
- The port VI 640-to-1024 lifecycle is understood as generated state plus host
  VI submission. `applyPendingViChanges` can change selector bytes
  `0x8011A862/0x8011A864/0x8011A865`; a direct `osViSetMode` edge at
  `0x8001B8DC` can submit `0x80128DF0` without entering the selector consumer.
  Host logging independently agrees with the generated pointer and committed
  VI state. The active boot descriptor chain selects the index-0 320 record.
- M4 shade-lane/order is not the cause. Port-side VMADH modeling and an
  independent control matched all 128 lanes. The s1194 producer-chain audit
  accounted for the final operands: `v0` is loaded from the state block and
  `v4` is produced by the documented accumulator chain. H1 (missing operand
  initialization/preservation) is not supported statically; H2 is already
  refuted. H3, a legitimate clipping/saturation sentinel, is the leading
  static explanation, but the exact numeric origin and retail target
  reachability remain open.
- The s1195 paired M4 capture was controlled but phase-unreached. The port
  reached only transient 320/640 widths with zero M4 rows; retail passed its
  whole-RDRAM control but stayed at width 320 and produced zero writes to the
  candidate `0x688:0x710` range. Neither arm selects an M4 hypothesis.
- The s1196 retail execution-mode check passed its debugger-on whole-RDRAM
  control and produced 10,799 VI frames at width 320. The debugger-off
  `--vi-poll` arm also stayed at width 320, but debugger-disabled mode cannot
  produce VI/PIF callbacks and reported zero emulated VI in its summary. The
  two arms therefore do not select H1, H2, or H3: the eleven injected Start
  events were logged, but only the debugger-on arm can verify PIF reads.
- The s1197 debugger-enabled retail control passed whole-RDRAM and PIF/VI
  controls in both arms. The eleven driven Start events changed the observed
  PIF words, but driven and undriven execution both remained at VI width 320
  with origin `0x006dd280`. Input delivery is validated; the fixed schedule
  does not reach the intended later state path. M4 target watches remain
   unevaluable.
- The s1212 source audit found that `tools/oracle/rs64_oracle.c` exposes only
  timed SDL keydown/keyup injection (`--press`), debugger watches/traces, and
  VI polling. It has no savestate, reset-state, direct pad-state setter, or
  other callable alternate entry route. The current retail-entry blocker is
  therefore an external/front-end capability gap, not an untried CLI option.
- The s1213 installed Mupen64Plus 2.6.0 audit found a callable alternate route:
  the front-end accepts `--savestate <filepath>`, and the installed core API
  declares `M64CMD_STATE_LOAD`, `M64CMD_STATE_SAVE`, `M64CMD_STATE_SET_SLOT`,
  and `M64CMD_RESET` for `CoreDoCommand`. This selects the route-exists
  hypothesis; the remaining work is to add state-file lifecycle calls to the
  debugger-enabled oracle and verify that its whole-RDRAM/PIF/VI controls stay
  positive.
- The s1214 oracle state smoke created and loaded a state with return code 0.
  The whole-RDRAM positive control reached 10,000 callbacks before the save
  and remained active through 1,506 VI frames. The lifecycle is therefore
  validated, but the run stayed at width 320 and did not test later phases.
- The s1215 paired debugger-enabled reachability comparison passed the
  whole-RDRAM positive control in both arms (10,000 callbacks each), and both
  arms observed the scheduled Start press/release words in PIF RAM. The state
  arm saved and loaded at the 320-boot boundary with `save_rc=0`, `load_rc=0`,
  and a valid state file, but both arms remained at VI width 320 with origin
  `0x006dd280` for the full run. Savestate lifecycle is usable; this state
  route does not provide the missing later retail entry (H2 selected).
- The s1216 paired debugger-enabled comparison passed the whole-RDRAM control
  at 10,000 callbacks in both arms. A continuous Start hold from 6s produced
  the expected PIF word, while the pulse control produced all eleven expected
  Start words; both arms nevertheless remained at VI width 320/origin
  `0x006dd280` for about 70s. Continuous Start is therefore another refuted
  retail-entry variation (H2); M4 watches remain unevaluable.
- The s1217 debugger capability audit found that the Homebrew core is not
  debugger-enabled, but the project's DEBUGGER=1 core and console frontend
  expose a working pause/write/read/resume path. A harmless virtual-RDRAM
  write at `0x80007FFC` read back as `0xDEADBEEF` before and after resume.
  Paired 12-second oracle arms both passed the whole-RDRAM control (10,000
  callbacks), PIF input, and VI controls; the write arm logged its phase-gated
  write at VI 1 / width 320. This REFUTES H3 (control-disruption/absent
  control) and CLOSES the "does a state-changing debugger route exist"
  question. No later phase was reached, so it does not yet select H1 or H2 for
  the retail-entry-capability hypothesis; the next step is a justified
  state-changing target, not another control-surface check.
- The s1219–s1221 debugger writes to `0x130B60` were misidentified as three
  `gGameSettings` state bytes. The s1222 census reconciled the addresses:
  `gGameSettings` is `0x80130B40`, so `0x80130B60..62` are volume bytes, while
  `mainGameLoop` reads `D_80130B10+0x20..22` at `0x80130B30..32`. Those three
  oracle writes therefore tested volume fields, not menu/cinematic/mission
  state, and cannot select H2.
- The s1223 generated/companion census selected H2 for the corrected state
  bytes. `resetGameSettingsAndMissionStats` clears all 0x28 bytes at
  `0x80130B10`; the only direct non-reset writes to offsets `0x20..21` are
  `runIdleFramesAndLoadSaveData` at `0x8006DAB8/BC` (`B30=1`, `B31=0`) before
  the main loop begins. `B32` has no direct writer in the generated census.
  `applySaveSlotToMissionState` writes the save-state prefix and status, while
  `initPlayerMissionStateFromSettings` writes only offsets 2, 3, and 5..7.
  No later producer supplies a justified debugger target for retail entry.
- The s1224 bounded consumer/caller audit confirms H2. `mainGameLoop` reads
  `D_80130B10+0x20` at `0x8003E07C`, `+0x21` at `0x8003E0DC` and
  `0x8003E128`, and `+0x22` at `0x8003E114`; the reads only select overlay,
  unlock, cinematic, and mission-frame work. The idle initializer writes
  `B30=1/B31=0`, while `applySaveSlotToMissionState` writes all three from a
  save record during `loadSaveDataIfNotLoaded`; reset/default paths clear or
  fill the same structure. No input-controlled writer reaches this triplet,
  so no debugger target or oracle run is justified from it. This is static
  source evidence; the independent retail entry path remains unresolved.
- The s1225 post-idle chain audit confirms H2. `loadSaveDataIfNotLoaded`
  has only EEPROM-read/copy logic, `classifySaveStateFromInput` has no
  generated caller, and the post-load loop only polls controller status,
  renders eight frames, and applies account unlocks. No input-controlled
  writer or concrete retail-entry transition occurs before `mainGameLoop`'s
  state-byte consumers; no debugger target is justified from this chain.
- The s1226 caller/boot-config audit confirms H2 for the remaining generated
  handoff. `mainGameLoop` has no direct generated caller: `main` starts the
  idle thread, that starts `thread3_video_handle`, and the latter registers
  `mainBootstrapWorker` as a service worker. The worker invokes the callback at
  the boot-config pointer's `+0x04` through `jalr`; the companion map identifies
  that callback as `mainGameLoop`. No input-dependent transition precedes it.
  The unresolved boundary is provenance/initialization of the
  `gBootConfig+0x04` data value or an external front-end handoff, not a missing
  generated caller. Static source evidence only.
- The s1227 bounded provenance audit closes the config-data side of that
  handoff. `gBootConfig` is the 0x50-byte ROM-backed object at `0x80037560` in
  the main `.text` image (`ROM 0x38160`); the retail ROM bytes at `+0x04` are
  `80 03 DF A0`, exactly `0x8003DFA0`. No generated store targets
  `0x80037564`. `thread3_video_handle` passes `0x80000C68` to
  `registerServiceWorker`; `mainBootstrapWorker` later loads `gBootConfig+4`
  and calls it. H2 is selected: the callback is a static ROM initializer and
  the missing retail-entry event is outside this generated handoff. The next
  boundary is the external/front-end retail-entry route, not config
  initialization. Two independent lines are the ROM bytes/section mapping and
  the generated caller/registration chain.
- The s1228 bounded source audit found no hidden oracle startup/reset or later-entry command. `rs64_oracle.c` performs `ROM_OPEN`, attaches input only when a press schedule exists, then calls `M64CMD_EXECUTE`; its optional state save/load happens after five seconds inside the same run. The port starts directly at `recomp_entrypoint`, whose generated path creates the idle and video threads; `thread3_video_handle` registers `mainBootstrapWorker`, which invokes static `gBootConfig+4`. The first explicit oracle state-changing event is therefore scheduled SDL input, while the port has no matching external handoff. H2 is selected; the remaining boundary is outside the in-tree oracle CLI and generated boot path. Source evidence only.
- The s1229 installed Mupen64Plus 2.6.0 front-end/core audit found the same contract outside the oracle: the console UI calls `CoreStartup`, `M64CMD_ROM_OPEN`, plugin attach, optional `M64CMD_STATE_LOAD` only for `--savestate`, then `M64CMD_EXECUTE`; it has no reset, EEPROM injection, or alternate entry command. The core does load EEPROM/SRAM through ROM database/config during ROM open, so save-media provenance remains a separate data question, not a launcher handoff. H2 is selected for the external-command hypothesis; the next boundary is whether the existing retail EEPROM file carries meaningful state. Source/config evidence only.
- The s1232 generated/companion provenance census found no new retail-entry producer or address disagreement. `mainGameLoop` reads `D_80130B10+0x20/+0x21/+0x22` at `0x8003E07C`, `0x8003E0DC`, `0x8003E128`, and `0x8003E114`; the targeted writers remain reset/default initialization, `runIdleFramesAndLoadSaveData` (`B30=1/B31=0`), and save-state application. The companion map agrees on `mainGameLoop=0x8003DFA0`, `mainBootstrapWorker=0x80000C68`, `thread3_video_handle=0x80001088`, and `gBootConfig=0x80037560`. The bootstrap path registers `mainBootstrapWorker`, which loads `gBootConfig+4` and indirect-calls the static `mainGameLoop` pointer. H2 is selected: the missing retail transition remains outside this generated handoff. No build or run.
- The s1233 startup-event census found no hidden state-changing route between `ROM_OPEN` and `EXECUTE`. The installed core's `ROM_OPEN` validates/copies the ROM and selects database/config settings; plugin attachment starts plugins; the oracle attaches SDL input only for a press schedule, then calls `M64CMD_EXECUTE`. `STATE_LOAD` is explicit and the wrapper's optional save/load occurs after five seconds; reset, state-slot, frame-advance, media-loader, and netplay commands are not invoked. The ROM database selects `Eeprom 4KB`, with no media/config disagreement. H2 is selected: the missing retail transition is outside the available startup/front-end contract. No build or run.
- The s1235 complete generated/retail register census narrows the s1234 entry-state result to H3. Retail's PIF IPL3 values in `s3..s7` and `t3` have no pre-overwrite consumer on the generated bootstrap path: `thread3_video_handle` loads its saved-register values from the video descriptor before using them, and `mainGameLoop` overwrites `s3/s4/s5/s7` before game-visible reads and writes `s6` before its first use. `t3` is absent from the path. `sp` and `ra` differ and are used for stack/return bookkeeping only. The port's `run_thread_function` zero-initializes contexts, supplies each thread stack, and `recomp_entrypoint` sets its own `$sp`; no build or run.
- The s1236 non-GPR reset-context census selects H2 for the active VI-320 boundary. Retail's PIF reset record supplies `rom_type`, `s7`, `reset_type`, and CIC seed to IPL3, and the retail boot path sets CP0 Status/Config; the port initializes the corresponding OS globals but has no CP0 Config model. The generated bootstrap has no CP0 read/write and no caller of `getOsResetType`; the first generated CP0 Context/Status sites are later TLB/FPU support paths, not the bootstrap handoff. No reset-context value is consumed before overwrite on the generated entry path. This is supported independently by the Mupen64Plus PIF/CP0 source, the generated instruction census, and the port runtime initialization.
- The s1237 complete ROM_OPEN-to-EXECUTE census selects H2 for the external-entry hypothesis. The oracle calls ROM_OPEN, attaches optional plugins, installs debugger callbacks, starts its director/poller, and calls EXECUTE; the core's ROM_OPEN path only opens/configures the ROM, while EXECUTE enters `main_run`. State load/save, reset, and input are explicit commands with separate timing/state requirements, and no hidden state-changing handoff was found. The available oracle checkout has no console-frontend source directory, so the UI portion relies on the prior s1229 audit rather than a new local recheck. No build or run.
- The s1238 artifact check found no new frontend/launcher source, binary invocation, savestate, or other retail-entry artifact in the workspace beyond the already-audited oracle and prior logs. The prescribed discriminator cannot run without external ground truth; H3 is selected and the external retail-entry boundary is blocked on a human-supplied artifact. No build or run.
- The s1239 unblock audit corrected the literal artifact census: the adjacent `rs64-oracle/src/mupen64plus-core` checkout contains the Mupen64Plus console frontend source, the installed `mupen64plus` binary exposes `--savestate`, and two existing `.st` files are present. Their source and help contracts still reduce to the already-audited `ROM_OPEN` → plugin attach → optional `STATE_LOAD` → `EXECUTE` lifecycle; no unmatched retail-entry handoff was found. The artifact-absence claim is refuted, but the external dependency is real and remains open because the available artifacts are equivalent. No build or game run.
- The s1240 save/account naming sweep found an exact companion/generated mapping for 19 symbols spanning EEPROM, service-worker, high-score, and account helpers. The repository symbol map now uses those human names, including the corrected `loadDefaultHighScores` spelling; no ambiguous or invented name was applied. This is source maintenance only and does not alter the external retail-entry boundary.
- The s1198 debugger-enabled comparison passed whole-RDRAM and PIF/VI
  controls in both arms. The revised 150 ms Start presses produced the
  expected `0x10000000` PIF word and returned to zero, but both arms remained
  at VI width 320 with origin `0x006dd280`. The timing/state-path hypothesis
  remains selected; no M4 target watch was armed.
- The s1199 debugger-enabled comparison passed whole-RDRAM controls in both
  arms. The earlier first-Start schedule produced verified `0x10000000` PIF
  words that returned to zero, but both arms still remained at VI width 320
  with origin `0x006dd280`. The schedule remains phase-incomplete; M4 target
  watches are still unevaluable.
- The s1200 debugger-enabled comparison passed whole-RDRAM controls in both
  arms. The earlier-first-Start arm produced eleven verified `0x10000000` PIF
  words that returned to zero, but both arms still remained at VI width 320
  with origin `0x006dd280` for about 3,600 VI frames. The schedule remains
  phase-incomplete; M4 target watches are still unevaluable.

- The s1201 debugger-enabled comparison passed whole-RDRAM controls in both
  arms. Moving the first Start to `0.2s` still produced eleven verified
  `0x10000000` PIF words that returned to zero, but both arms remained at VI
  width 320 with origin `0x006dd280` for about 3,600 VI frames. The tested
  schedule remains phase-incomplete; M4 target watches are still unevaluable.
- The s1202 debugger-enabled comparison passed whole-RDRAM controls in both
  arms. Moving the first Start to `0.1s` still produced eleven verified
  `0x10000000` PIF words that returned to zero, but both arms remained at VI
  width 320 with origin `0x006dd280` for about 3,600 VI frames. The tested
  schedule remains phase-incomplete; M4 target watches are still unevaluable.
- The s1203 debugger-enabled comparison passed whole-RDRAM controls in both
  arms. The `0.0s`-first driven arm produced verified `0x10000000` PIF words
  for the later presses, but both arms remained at VI width 320 with origin
  `0x006dd280` for about 3,600 VI frames. This schedule remains
  phase-incomplete; M4 target watches are unevaluable. The oracle's documented
  6s-first hangar schedule is now the next independent reachability route.
- The s1204 debugger-enabled comparison passed whole-RDRAM and PIF/VI controls
  in both arms. The documented 6s-first hangar schedule delivered all eleven
  Start presses as verified `0x10000000` PIF words, but both arms remained at VI
  width 320 with origin `0x006dd280` for about 3,600 VI frames. The documented
  route is not reproducible in this oracle configuration; M4 target watches
  remain unevaluable. Seek a new independent retail execution path.
- The s1205 debugger-enabled comparison passed whole-RDRAM controls in both
  arms under alternate R4300 emulator mode 1. The driven arm verified all
  eleven Start presses, but undriven and driven runs remained at VI width 320
  with origin `0x006dd280` for 3,600 and 3,597 VI frames respectively. The
  emulator-mode hypothesis is refuted; M4 target watches remain unevaluable.
- The s1206 debugger-enabled comparison passed whole-RDRAM controls in both
  arms. An early A press followed by the documented Start cadence did not
  change the driven path: undriven and driven runs remained at VI width 320
  with origin `0x006dd280` for 3,600 and 3,601 VI frames. The available
  `--press` path variation is therefore insufficient; seek a different retail
  entry strategy before arming M4 watches.
- The s1207 debugger-enabled comparison passed whole-RDRAM controls in both
  arms. A at 6 seconds followed by the documented Start cadence produced the
  scheduled input events, but undriven and driven runs remained at VI width
  320 with origin `0x006dd280` for 3,600 and 3,599 VI frames. This title-time
  A variation is phase-incomplete and does not select a later retail path;
  seek a different entry strategy before arming M4 watches.
- The s1208 debugger-enabled comparison passed whole-RDRAM controls in both
  arms. A at 18 seconds followed by the revised Start cadence produced the
  scheduled PIF-confirmed input events, but undriven and driven runs remained
  at VI width 320 with origin `0x006dd280` for 3,600 and 3,597 VI frames.
  This later title-time A variation is phase-incomplete; seek a different
  input-entry mechanism before arming M4 watches.

- The s1209 debugger-enabled comparison passed whole-RDRAM controls in both
  arms. Repeated A pulses at 17–20 seconds produced four verified
  `0x80000000` PIF press/release pairs, and the seven later Start presses were
  also verified, but both arms remained at VI width 320 with origin
  `0x006dd280` for 3,599 VI frames. Repeated A confirmation edges do not
  provide the missing retail entry mechanism; M4 target watches remain
  unevaluable.

- The s1211 controller-chord comparison passed whole-RDRAM controls in both
  arms. The driven arm's A/B/Z/L/R/directional chord and later Start presses
  were visible in PIF reads, but driven and undriven runs remained at VI width
  320 with origin `0x006dd280` (3,609 and 3,599 VI frames). This new input
  path does not provide a later retail entry; M4 target watches remain
  unevaluable.

## Active investigation and ranked next steps

1. Continue the in-tree generated-symbol renaming campaign with one bounded
   adjacent save/account helper sweep (the remaining `0x8006E8CC..0x8006F1A8`
   region); it needs no external retail-entry artifact. Keep the external
   retail-entry dependency open and do not add runtime probes without a
   genuinely unmatched state-changing handoff and positive control.
2. Keep audio closed unless a new independent ground-truth lead reaches a
   later audio phase and first passes whole-RDRAM controls.
3. Revisit runtime instrumentation only after a concrete candidate exists.
   Before any probe, read `tools/oracle/README.md` and
   `docs/F5-UCODE-REFERENCE.md`, define positive controls, and phase-gate all
   animated comparisons.

## Durable boundaries

### M3 dispatcher/frame origin

The s1162 census found 144 direct `slotDispatcherIter` calls in 72 generated
callers: all caller entries match companion symbols, stack decrement/increment
pairs balance, and saved `$ra` contracts are present. No static indirect target
to `0x8003E8DC` exists. The former `0x80078894` anomaly is inside the corrected
standalone `npcPowerGeneratorUpdate` boundary. Runtime context ownership has
one executable `r29` initializer in `run_thread_function`; generated and
runtime context audits found no alternate context handoff.

Completed writer/load classes, all with H3 selected and no mitigation, are:

- stack-relative stores, `r29` assignments, dynamic copy/DMA/controller/flash;
- `SD`, `do_swl`/`do_swr`, narrow stores, `MEM_W`, and `MEM_WU`;
- `MEM_D`/`LD`, `do_ldl`/`do_ldr`, and `do_lwl`/`do_lwr`;
- `do_sdl`/`do_sdr` (five emitted sites; all malformed or data-like).

The latest `do_lwl`/`do_lwr` census classified all 418 calls: ordinary pairs
feed bounded structure or stack-local partial stores; unpaired and large or
negative-offset sites are malformed/data-like tails. Their `MEM_W` contract is
exact and no span overlaps the saved frame. The next class is `do_sdl`/`do_sdr`.

### VI descriptor boundary

`osTvType=1` feeds `rsViModeType=0`; the NTSC index window contains mixed
descriptors, while boot selector bytes are `A/B/C=1/0/0`. `initVideoSubsystem`
preserves index 0, copies records to offsets `0x00/0x50/0xA0/0xF0`, and the
generated selector chooses `base+0xF0` (`0x80128E40`), the 320 descriptor.
`osViSetMode_recomp` forwards `ctx->r4` unchanged; the host performs no width
rewrite. This boundary is independently established.

### M4 accumulator boundary

Factor 5 reference data and paired combiner evidence refute an RT64 shade
ordering explanation. The VTXCOLOR payload is nonzero, while decoded shade is
the fixed `0xFFFF8000`/`0x00008000` sentinel. The unresolved issue is the
missing-lighting/vector numeric origin before `vmadh v6,v4,v0`, not RT64 lane
order.

## Superseded conclusions

- The old `H-gate-stale-or-unseen-writer` result was superseded by corrected
  physical-byte samples observing nonzero `0x8011A8A0` at SP send boundaries.
  It was believable because the static census found no generated writer, but
  it did not measure runtime stores.
- The claim that `setViModeType` maps `osResetType` was superseded by generated
  loads and symbols showing `osTvType` at `0x80000300`.
- Fixed-selector, bad-mode-table, and host-logger explanations for width 320
  are closed by the generated descriptor chain and independent retail controls.
- The old boot/menu overlay-dispatch explanation is closed by the current
  mission/post-sec2 behavior and is no longer the active blocker.
- The s1230 claim that the selected nonblank EEPROM was the leading cause of
  the missing retail transition was superseded by s1231. It was believable
  because the file was selected by the ROM database and contained structured
  nonblank data, but replacing it with an isolated zero-filled 512-byte file
  produced the same phase-gated VI result with positive controls intact.
- The s1234 claim that the broad retail-only GPR mismatch selected H1 was
  superseded by s1235. It was believable because retail initializes `s3..s7`,
  `t3`, `sp`, and `ra` before IPL3 transfers control while the port enters
  directly, but the complete generated-path census found the saved `s3..s7`/`t3`
  values dead or overwritten before game-visible use; only `sp`/`ra`
  bookkeeping remains different.
- The s1238 claim that no frontend, launcher, or savestate artifact was locally
  available was superseded by s1239. It was believable because the workspace
  root search omitted the adjacent oracle source checkout, but the frontend
  source, installed `--savestate` invocation, and existing state files are
  present. They do not resolve the blocker because their handoff contract was
  already audited and contains no new retail state source.

## Evidence ledger summary

| Sessions | Durable result |
|---|---|
| s820–s880 | Post-sec2 accounting, breadcrumb, coalescer, and oracle routes classified or parked. |
| s881–s951 | M3 idiom inventories closed the audio-channel-field thread. |
| s952–s983 | Dispatcher stack-spill family localized; oracle callback work repaired later. |
| s984–s1038 | M4 shade source/emission audits and controls moved the issue to accumulator numeric origin. |
| s1039–s1111 | Retail input/cadence and port submit/gate work passed controls; width-320 and pre-1024 paths remained state-shaped. |
| s1112–s1133 | VI lifecycle, descriptor chain, consumer ordering, and regeneration boundary were resolved. |
| s1134–s1140 | M4 paired capture was valid but pre-1024; M3 indirect-call census isolated the old coalesced boundary. |
| s1141–s1161 | VI writer/consumer probes established the direct `applyPendingViChanges` edge and independent host request path. |
| s1162–s1167 | Complete dispatcher-origin runtime attempts were pre-1024 or alternate-failure; no frame writer or RT64 allocation origin selected. |
| s1168–s1171 | MusyX callback/callsite audits found balanced generated contracts and moved the open question to voice sample fields. |
| s1172–s1177 | Retail oracle calibration and execution watches passed controls but stayed at VI 320; audio destination origin remains unevaluable. |
| s1178–s1189 | Complete `$sp`, dynamic writer, store, and load idiom audits selected H3; no frame-overlapping writer or helper broadening found. |
| s1190–s1191 | Partial-load consumer/site rechecks classified all `do_lwl`/`do_lwr` calls and kept H3 selected. |
| s1192 | Maintenance compaction only; no experiment or code change. |
| s1193 | Complete `do_sdl`/`do_sdr` static census selected H3; no reachable frame writer or mitigation. |
| s1236 | Complete CP0/PIF/reset-context census selected H2; no bootstrap consumer before overwrite. External retail-entry boundary remains open. No build or run. |
| s1237 | Complete ROM_OPEN-to-EXECUTE census found only ROM open/configuration, plugin/callback setup, explicit input/state commands, and EXECUTE→main_run; no hidden state-changing handoff. H2 selected. No build or run. |
| s1238 | Workspace artifact check found no new frontend/launcher artifact beyond the audited oracle/core and prior logs. The planned artifact-backed event table was unevaluable; H3 selected and the external retail-entry boundary is blocked on human-supplied ground truth. No build or run. |
| s1240 | Exact companion/generated save-account mapping covered 19 symbols; synchronized the repository symbol map with those names and corrected `loadDefaultHighScores`. No build or run. |
| s1194 | Complete M4 final-operand producer-chain audit found initialized `v0` and a contiguous `v4` accumulator chain; H1 unsupported, H2 already refuted, H3 leading but numeric origin remains open. |
| s1195 | Paired M4 port/oracle capture passed independent controls but both arms were phase-unreached; target null unevaluable. |
| s1196 | Debugger-on/off oracle check stayed at width 320; off-mode callbacks are unavailable, so input reachability remained unevaluable. |
| s1197 | Debugger-enabled driven/undriven oracle arms passed controls; driven PIF words changed but both stayed at width 320, selecting schedule/path redesign. |
| s1198 | Revised 150 ms Start schedule passed controls and changed PIF words, but both arms stayed at width 320/origin `0x006dd280`; H1 timing/state-path remains selected. |
| s1199 | Earlier first-Start schedule passed controls and changed PIF words, but both arms still stayed at width 320/origin `0x006dd280`; schedule remains phase-incomplete. |
| s1200 | Earlier-first-Start schedule passed controls and changed PIF words, but both arms still stayed at width 320/origin `0x006dd280`; schedule remains phase-incomplete. |
| s1201 | First Start moved to 0.2s; both arms passed controls, the driven arm changed PIF words, but both remained at VI 320/origin `0x006dd280`; schedule remains phase-incomplete. |
| s1202 | First Start moved to 0.1s; both arms passed controls, the driven arm changed PIF words, but both remained at VI 320/origin `0x006dd280`; schedule remains phase-incomplete. |
| s1203 | First Start moved to 0.0s; both arms passed controls, the driven arm changed PIF words, but both remained at VI 320/origin `0x006dd280`; schedule remains phase-incomplete. |
| s1204 | Documented 6s-first hangar schedule passed controls and delivered all eleven Start presses, but both arms remained at VI 320/origin `0x006dd280`; route is not reproducible in this oracle configuration. |
| s1205 | Alternate R4300 emulator mode 1 passed whole-RDRAM controls; driven input delivered all eleven verified Start presses, but both arms remained at VI 320/origin `0x006dd280`; mode change does not explain the retail reachability failure. |
| s1206 | Early A plus the documented Start cadence passed whole-RDRAM and PIF/VI controls, but both arms remained at VI 320/origin `0x006dd280`; this input variation does not provide a later retail path. |
| s1207 | A at 6 seconds plus the documented Start cadence passed whole-RDRAM and PIF/VI controls, but both arms remained at VI 320/origin `0x006dd280`; this title-time A variation does not provide a later retail path. |
| s1208 | A at 18 seconds plus a revised Start cadence passed whole-RDRAM and PIF/VI controls, but both arms remained at VI 320/origin `0x006dd280`; this later title-time A variation does not provide a later retail path. |
| s1209 | Repeated A at 17–20 seconds plus seven Start presses passed whole-RDRAM and PIF/VI controls, but both arms remained at VI 320/origin `0x006dd280`; repeated confirmation edges do not provide a later retail path. |
| s1210 | R4300 emulator mode 2 passed whole-RDRAM controls in both arms; the driven arm delivered all eleven verified Start presses, but both arms remained at VI 320/origin `0x006dd280` for about 3,600 VI frames. Mode 2 does not explain the retail reachability failure; seek a different entry strategy. |
| s1211 | Controller chord plus eleven Start presses passed whole-RDRAM and PIF/VI controls; both arms remained at VI 320/origin `0x006dd280` for about 3,600 VI frames. The new input path does not provide a later retail entry. |
| s1213 | Installed Mupen64Plus front-end/core audit found startup savestate loading and CoreDoCommand save/load/reset commands; route-exists hypothesis selected. |
| s1212 | Oracle source audit found only scheduled SDL key injection; no savestate, reset-state, direct pad setter, or alternate callable entry route exists in the in-tree CLI. |
| s1214 | Oracle state smoke created and loaded a state with rc=0 while whole-RDRAM and VI controls stayed positive; route validated, later phase unreached. |
| s1215 | Startup savestate save/load passed with whole-RDRAM and PIF/VI controls, but both arms remained at VI 320/origin `0x006dd280`; the state route does not provide later retail entry. |
| s1216 | Continuous Start from 6s and the eleven-pulse control both passed whole-RDRAM/PIF/VI controls but remained at VI 320/origin `0x006dd280`; this hold variation does not provide later retail entry. |
| s1217 | DEBUGGER=1 core write/read/resume path validated with a harmless RDRAM word; paired oracle arms passed whole-RDRAM/PIF/VI controls. Refutes H3 (control-disruption/absent control) and closes the control-surface question; H1/H2 remain open pending a state-changing target. |
| s1218 | Checkpoint-recovery only: restated s1217 in gate-recognized terms, no new experiment. |
| s1220 | `gGameSettings+0x21` target write passed whole-RDRAM and VI controls but both arms stayed at width 320/origin `0x006dd280`; cinematic sub-state target did not change retail entry. |
| s1221 | `gGameSettings+0x22` target write fired and both arms passed whole-RDRAM/VI controls, but both stayed at width 320/origin `0x006dd280`; mission sub-state target did not change retail entry. No-input oracle recipe produced no PIF events in either arm. |

| s1222 | Corrected the state-byte identity: `mainGameLoop` reads `D_80130B10+0x20..22` (`0x80130B30..32`), not `gGameSettings+0x20..22` (`0x80130B60..62`). The prior writes were volume-field tests; generated/companion census found `runIdleFramesAndLoadSaveData` writes `B30=1,B31=0`, while demo save/restore writes only `B60..62`. No generated-boundary defect was found. |
| s1225 | Post-idle generated/companion audit found `loadSaveDataIfNotLoaded` is EEPROM-only, `classifySaveStateFromInput` is uncalled, and the remaining post-load loop has polling/render/account-unlock work but no input-controlled retail-entry writer. H2 selected; no oracle target justified. |
| s1227 | Bounded provenance audit found `gBootConfig` at `0x80037560` is ROM-backed in the main image (ROM `0x38160`), with bytes `80 03 DF A0` at `+0x04` (`mainGameLoop`). No generated writer exists; `thread3_video_handle` registers `mainBootstrapWorker`, whose `jalr` consumes that static callback. H2 selected; the missing retail-entry event is outside this generated handoff. No build or run. |
| s1228 | Bounded source audit found the oracle performs `ROM_OPEN` then `M64CMD_EXECUTE`, attaches input only for scheduled presses, and performs optional save/load only after five seconds. The port enters directly through `recomp_entrypoint` and the same static boot-config callback chain. No source-visible external event bridges the oracle's 320 phase to later retail entry; H2 selected. No build or run. |
| s1229 | Installed Mupen64Plus 2.6.0 UI source confirms `CoreStartup` → `ROM_OPEN` → plugin attach → optional `STATE_LOAD` only for `--savestate` → `EXECUTE`; no reset, EEPROM injection, or alternate entry command exists. Core ROM-open code does load save media via its ROM database/config, leaving actual EEPROM contents as the next boundary. H2 selected for the external-command hypothesis. No build or run. |
| s1230 | The actual save directory contains one 512-byte EEPROM file with 164 nonzero bytes and no `0xff` bytes. Its `-47CAC4E2` suffix matches the ROM's MD5 key; the ROM database selects USA v1.0 with `Eeprom 4KB`, and the core's old-goodname path loads an existing `.eep` before the fallback path, then truncates non-16K EEPROM to 0x200. H1 is selected for nonblank, selected persistent state; whether these bytes cause retail entry remains open. No build or run. |
| s1231 | Paired phase-gated retail oracle arms used the existing selected EEPROM versus an isolated same-named 512-byte zero-filled EEPROM. Both passed the whole-RDRAM control (10,000 capped writes), 11 PIF-confirmed Start press/release pairs, and VI polling; both had the same 0→320/origin `0x280` then 320/origin `0x006dd280` transitions and completed about 7,200 VI frames. H2 selected: EEPROM contents do not cause the missing retail transition. |
| s1232 | Complete targeted generated/companion census found the expected triplet reads, only known reset/idle/save writers, and matching callback/config addresses and handoff. H2 selected: no generated producer or symbol mismatch explains the missing retail transition. No build or run. |
| s1233 | Installed-core startup-event census found only ROM-open/config selection, plugin attach, optional scheduled SDL input, and explicit state commands before/after `EXECUTE`; ROM database selects Eeprom 4KB with no media/config disagreement. H2 selected: no available front-end command explains the missing retail transition. No build or run. |
| s1234 | Static retail-reset versus port-entry audit found PIF IPL3 setup at `0xA4000040`, CP0/boot register initialization, and `s3..s7`, `t3`, `sp`, `ra` boot context before game entry; the port starts directly at `0x80000400` with only `$sp` initialized. H1 selected: entry-state contracts are not equivalent. No build or run. |
| s1235 | Complete generated/retail register census found no pre-overwrite consumer for retail `s3..s7` or `t3`; `sp`/`ra` differ only in stack/return bookkeeping. H3 selected for the GPR hypothesis; the stable VI-320 divergence remains open at CP0/reset-context state. No build or run. |

## Method and safety rules

- A null result is worthless without a positive control in the same run.
- Batch instrumentation; scope counters and budgets to the VI phase; use
  SIGKILL, launch from `build/`, and queue repeat soaks instead of babysitting.
- Regeneration order is `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated code belong in fixup scripts.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. Changes under `lib/` require `./submodule-patches/export.sh`.
- Before mitigation, identify the writer and legitimacy with an `ORIGIN:` line.
