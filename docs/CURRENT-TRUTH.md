# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable project
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is
the authority for session detail. Reviewed through s1356 (2026-08-15).

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
- M5 audio de-stubbing is closed. Audio remains stubbed. Retail watches passed
  whole-RDRAM controls but stayed at VI 320 and never reached the identified
  `musyxInitVoiceFromSample` writers. Do not reopen without a new independent
  lead reaching audio initialization or voice allocation.
- Retail oracle whole-RDRAM, scheduled PIF, and VI controls are healthy, but
  the available recipe remains at width 320/origin `0x006dd280`. The external
  retail-entry boundary is unresolved and currently lacks a new state-changing
  route. Do not add target watches before that boundary is reached.
- The port VI 640-to-1024 lifecycle is generated state plus host VI submission.
  `applyPendingViChanges` can change selector bytes
  `0x8011A862/0x8011A864/0x8011A865`; a direct `osViSetMode` edge can submit
  `0x80128DF0` without entering the selector consumer. Host logging agrees
  with generated and committed VI state. The active boot descriptor selects
  the index-0 320 record.
- M4 shade-lane/order is not the cause. Port VMADH modeling and an independent
  control matched all 128 lanes; the leading static explanation is a legitimate
  clipping/saturation sentinel. Exact numeric origin and retail reachability
  remain open.

## Active investigation and ranked next steps

1. Continue the generated-symbol renaming sweep with one bounded exact-name
   census over the next adjacent function, `0x80092A54..0x80092BA8`.
   Synchronize only names independently supported by the companion project,
   generated definitions, sizes, and caller/semantic evidence. Leave
   `func_8008ED6C` address-encoded (s1309 H2) and `func_800927B0`
   address-encoded (s1355 H3: no independent companion name).
2. Keep the external retail-entry boundary parked until a new independent
   artifact or state-changing handoff is available. Any future oracle work
   must pass whole-RDRAM, PIF, and VI positive controls in the same run.
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
`0xFFFF8000`/`0x00008000` sentinel. The unresolved issue is the vector numeric
origin before `vmadh v6,v4,v0`, not RT64 lane order.

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

## Evidence ledger summary

| Sessions | Durable result |
|---|---|
| s820–s951 | Post-sec2 accounting and M3 crash/idiom families were classified or parked. |
| s952–s983 | Dispatcher stack-spill family localized; no static frame writer found. |
| s984–s1038 | M4 shade audits moved the issue to accumulator numeric origin. |
| s1039–s1167 | Retail/port controls, VI lifecycle, and generated boundaries were resolved; late runtime paths remain phase-sensitive. |
| s1168–s1193 | Audio and complete M3 store/load idiom audits closed without a mitigation; `do_sdl`/`do_sdr` selected H3. |
| s1194–s1239 | M4 and retail-entry experiments passed controls but remained phase-incomplete; external handoff remains open. |
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
