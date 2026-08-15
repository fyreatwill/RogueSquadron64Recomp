# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); detailed session records stay
in the ledger. Reviewed through s1187 (2026-08-14).

## Current state

- Overlay dispatch is sufficiently fixed for mission entry and post-sec2
  outdoor presentation. The original boot/menu explanation is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Any new mitigation requires an `ORIGIN:` naming the
  writer and assessing whether the value is legitimate.
- Phase-gated port captures can reach VI width 1024 with independent
  emit/raw/dispatch/match controls. Pre-chain crashes are disjoint families;
  they do not classify parser loss.
- Ordinary late E9 producer/consumer identity is established. Synthetic
  FULL_SYNC was absent in the decisive capture. Remaining deltas are
  boundary/span-shaped and the residual extended condition is unclassified.
- The recurring `slotDispatcherIter+872` SIGBUS is the generated prologue
  spill of guest `$sp` at `funcs_8.c:22810`. Direct callers and statically
  addressed indirect targets are balanced; `0x8010B350` is compiled data with
  no generated writer. General runtime caller-frame corruption remains open.
- The s1162 complete frame-idiom census found 144 direct
  `slotDispatcherIter` calls in 72 generated callers. All 72 caller entries
  match their companion symbol boundaries, and every site has a balanced
  stack decrement/increment plus a saved `$ra`; no static indirect target to
  `0x8003E8DC` exists. The former `0x80078894` boundary family is now a
  separate `npcPowerGeneratorUpdate` function, so this audit selects H1 and
  moves the fault-origin question to runtime-side frame/value writes.
- The NPC function-boundary input correction is landed in the companion symbol
  files: `npcPowerGeneratorUpdate` is now sourced as main `.text` at
  `0x80077AF0`. Regenerated ELF, N64Recomp output, fixups, and the Debug target
  all pass; no runtime effect is established yet.
  The register-dump probe is landed and binary-verified; phase-positive
  no-event soaks did not classify the site.
- The s1178 runtime/generated-context `$sp` ownership census found one
  executable runtime assignment to `r29`, in `run_thread_function`, sourced
  from the scheduler-provided thread stack pointer. The only other context
  effects are whole-context save/restore in mod event/hook dispatch; the
  Rogue Squadron `GameEntry` has no thread-create callback, and no runtime
  helper assigns `ctx->r29`. Combined with s1162's independent 72/72 balanced
  generated caller census, this selects H3 for the context-writer branch:
  the remaining `slotDispatcherIter+872` origin is guest stack-memory/value
  corruption, not a direct `$sp` replacement. No mitigation was added.
- The s1179 complete stack-memory writer census found 18,773 generated
  stack-relative stores across 1,719 functions (17,457 word, 682 halfword,
  634 byte). `slotDispatcherIter`'s exact prologue stores are the only
  concrete writes to its saved-register frame; runtime writers are generic
  dynamically addressed PI/RSP DMA, zmemcpy, controller/flash, and diagnostic
  paths with no statically named edge into the failing frame. This selects H3:
  no writer-to-frame edge is established, so the next audit moves to the
  earlier guest `$sp` value origin. No mitigation was added.
- The s1181 complete generated `$sp`-value audit found 4,919 `ctx->r29`
  assignments total. The 144 `slotDispatcherIter` callsites remain ordinary
  balanced frame arithmetic. The broader tree has 67 assignments outside the
  normal `ADD32(ctx->r29, ...)` idiom: five `ADD32(ctx->r30, 0)` frame setups,
  three `recomp_entrypoint` bootstrap writes, and 59 data/audio/OS/helper
  assignments in `fake_func_80024A0C`, `fake_func_80099FDC`,
  `audioCompandS16`, the `static_3_800A21xx` through `static_3_800A2FE4`
  blocks, and `__OSGlobalIntMask`. None has a generated call edge into the
  target family, and no generated context object or alternate context pointer
  is constructed. This selects H3: no reachable invalid direct producer or
  context-preserving handoff was found; the next audit is broader guest
  memory/value corruption, with no mitigation added.
- The s1182 complete dynamic-writer census found 72 generated `zmemcpy`
  callsites, 20 `memcpy_recomp` callsites, four `osPiStartDma_recomp` callsites,
  13 controller calls, and the flash helper definitions. Copy/DMA destinations
  are runtime-computed, but no enumerated mission/cinematic edge also proves a
  span capable of covering the `slotDispatcherIter` saved frame; controller
  and flash writes are bounded to their device/state structures. This selects
  H3 for the writer-class audit: no named writer-to-frame edge or legitimate/
  corrupt value origin was established, and no mitigation was added.
- The s1183 complete generated wide-store audit found 1,356 non-`r29`
  `SD` sites, but the target-path callers contain only ordinary `r29` frame
  stores plus 13 `zmemcpy` calls with fixed lengths. Their destinations are
  caller locals or bounded game structures; none has both a reachable
  mission/cinematic edge and a span capable of covering the
  `slotDispatcherIter` saved frame. The `SD` macro and host RDRAM accessor
  both preserve the computed destination and add no hidden broadening. This
  selects H3 and rules out the wide-store/accessor class as the current
  origin; no mitigation was added.
- The s1184 complete generated partial-store audit found 414 `do_swl`/`do_swr`
  calls across 66 functions. Only five functions both contain a partial store
  and call `slotDispatcherIter`; their stores target caller locals or bounded
  object/global data, and none has a destination/span covering the callee's
  saved-register frame. `do_swl` and `do_swr` align to one guest word and
  write only that word through `MEM_W`, so the host accessor does not broaden
  the operation. This selects H3 and rules out the partial-store/accessor
  class; no mitigation was added.
- The s1185 complete generated narrow-store audit found 23,128 `MEM_H`/
  `MEM_HU`/`MEM_B`/`MEM_BU` references, including 351 stores in the 72
  `slotDispatcherIter` callers (83 based on caller `r29`). Those stores target
  caller locals or bounded object/global data; none has a destination/span
  capable of covering the callee's saved-register frame. `slotDispatcherIter`
  itself has only ordinary prologue `MEM_W` stores plus bounded byte stores.
  The four host macros preserve the computed guest address and exact 1/2-byte
  access span. This selects H3 and rules out the narrow-store/accessor class;
  no mitigation was added.
- The s1186 complete generated word-store audit found 3,633 `MEM_W` stores
  across the 72 direct `slotDispatcherIter` callers. Every caller-frame
  `r29` store uses a nonnegative offset, while the callee's saved-register
  frame is `incoming_sp-0x1C..incoming_sp-0x4`; the 1,442 non-`r29` stores
  are bounded object/global writes or unrelated paths, with no stack-derived
  negative alias. The host `MEM_W` macro writes exactly four bytes at the
  computed guest address. This selects H3 and rules out the word-store/
  accessor class; no mitigation was added.
- The s1187 complete `MEM_WU` load audit found five loads. Two are the
  bounded texture-row 64-bit assembly loop in `swizzleTextureRowsToTmem`, one
  is an unrelated `__OSGlobalIntMask` block, and the two `audioCompandS16`
  hits are outside the target path (the first follows an explicit return and
  the second is in its malformed generated tail). `MEM_WU` mirrors `MEM_W`
  and performs an exact unsigned four-byte load at the computed guest
  address. This selects H3 and rules out the unsigned-load/accessor class;
  no mitigation was added.
- M5 audio de-stubbing is closed. Audio remains stubbed; do not reopen without
  a genuinely new lead. The s1177 retail execution watch found no execution of
  any of the four statically identified `musyxInitVoiceFromSample`
  sample/stream stores during the driven attract path. Whole-RDRAM read and
  write controls passed, but the run stayed at VI 320; no destination watch is
  authorized. The s1176 static correlation found that the s1175
  writer PCs are not sample/stream-field writers: `runAiAudioStreamPlaybackLoop`
  writes a dynamic 16-entry AI buffer-pointer table, `allocateSongChannelArray`
  writes audio-global count/allocation/voice-base fields, and
  `initAudioSubsystem` writes its audio scratch pointer. The first generated
  sample/stream-field writer is instead `musyxInitVoiceFromSample` at
  `0x800921E8`, `0x80092220`, `0x80092228`, and `0x80092230`, storing descriptor
  fields into the computed voice slot at `+0x34/+0x38/+0x3C/+0x40`. No voice
  range is inferred from `0x001496F8`.
- The port-side VI 640-to-1024 transition is lifecycle-driven. The host logger
  observes committed VI state correctly; the active mode bytes, copied records,
  and pending masks are ordinary runtime state, not an unobserved host write.
- Retail oracle controls remain healthy in completed runs: whole-RDRAM,
  scheduled PIF input, and VI callback/poll controls pass. The latest targeted
  M4 arm passed the whole-RDRAM control (10,000 callbacks, removed cleanly)
  and delivered all scheduled presses through 56 seconds, but stalled before
  any later VI transition at width 320/origin `0x006dd280`; its targeted
  `0x688:0x710` watch had zero hits and is unevaluable for the shaded phase.
  No hangar watch conclusion is valid.
- The no-target retail audit reproduced the post-56-second stall with the same
  whole-RDRAM control and all eleven presses. A process sample found the main
  emulation thread in `gen_interrupt → vi_vertical_interrupt_event → nanosleep`
  for 763/777 samples. This rules out the M4 target watch as the launch cause,
  but is single-run evidence for a core/emulator progress stall and does not
  make the retail M4 ownership watch evaluable.
- The independent `--oracle-emulator 1` audit also stopped at the initial VI
  width 320/origin `0x006dd280` after delivering all eleven presses. Its
  whole-RDRAM control reached 10,000 callbacks and was removed successfully;
  no later VI transition occurred through 180 seconds. This reproduces the
  stall across execution modes, but does not distinguish core scheduling from
  debugger/watch overhead and does not evaluate the M4 target range.
- The debugger-off, `--oracle-emulator 1`, VI-poll audit stayed at width 320 /
  origin `0x006dd280` for the full 180-second bound. All eleven presses were
  delivered and VI polling remained active, so debugger/watch overhead is
  ruled out as the launch cause. The core scheduling/state-path boundary is
  still open; the shaded M4 range remains unevaluable.
- The first runtime test of the corrected NPC function boundary was
  unevaluable: the regenerated macOS build reached VI width 640 but not the
  1024 target in the 180-second phase-gate wait. The run had no `[CRASH]`,
  `[e9-prov]`, `[e9-unified]`, or `[slot-dispatch]` records because those
  categories were not explicitly enabled, so it supplies neither a
  boundary-sensitive result nor a positive-control result.
- The second runtime boundary test explicitly enabled all three categories,
  and slot-dispatch logging was live (6,438 records), but the process again
  stopped at VI width 640 for 180 seconds. It produced zero VI-1024,
  task-control E9, unified-E9, and crash markers. This remains unevaluable;
  the missing E9 rows are a pre-phase reachability problem, not evidence that
  the corrected boundary is or is not runtime-relevant.
- The s1146 trace classifies that pre-phase result as a stable active loop,
  not an early execution halt: VI transitions ended at width 640 around 7.3s,
  visible slot-dispatch records continued through `n=2341`, and the same log
  continued through host input `n=10000` and audio dispatch `n=10752`. No
  crash, SIGBUS, or E9 marker occurred. This is single-run evidence about
  the regenerated-target trace and does not explain why the 1024 transition
  is absent.
- The s1147 phase-scoped VI producer capture is evaluable: after the final
  640 record, `osViSetMode` made the transient call sequence through committed
  width 2 and requested width 640, then made no further producer calls. Slot
  dispatch (6,424 rows), host input (10,000), and audio dispatch (10,752)
  continued without a crash. This selects a producer-absent stable loop after
  the last 640 transition; no E9 or 1024 phase was reached, so the corrected
  NPC boundary remains unevaluable at runtime.
- The controlled s1148 selector capture passed an independent host-path
  positive control (`[vi-selector-positive]`) and recorded all six host VI
  calls, but the generated selector callsite/control/selection markers were
  zero. Slot dispatch and task-control E9 activity continued until the known
  `fillSampleStreamRange+336` SIGBUS at guest PC `0x8000B650`, with no VI-1024
  phase. This selects a selector-caller-absent post-640 loop (H2); it does not
  evaluate the corrected NPC boundary.
- The s1149 predecessor audit retained the independent selector positive
  control and sustained 8,192 slot-dispatch records, but reached only the
  640→2→640 VI sequence before a pre-1024 SIGBUS in
  `allocateDisplayListBuffer+3648` (guest PC `0x8000E29C`). The new entry and
  exact-edge predecessor markers, plus all selector markers, were zero. This
  selects H2 again: the post-640 loop continues without entering the unique
  generated selector predecessor. The corrected NPC boundary remains
  unevaluable.
- The s1150 static owner census found 144 direct `slotDispatcherIter` sites in
  72 generated caller functions, including `runInMissionFrame`,
  `cinematicLoopBody`, and `cinematicSlotBatchDispatch`. The VI transition is
  isolated to `freeRenderSubsystemResources` → `selectAndApplyViMode`; the E9
  producer is host-side in `submit_rsp_task`/RSP task handling, not a generated
  game-call predecessor. Generated and companion-symbol inventories agree on
  the phase-loop families, selecting H2 path separation and ruling out a
  missing generated owner edge in this census.

- The s1151 shared `submitGfxFrame` entry probe is live: selector positive,
  task-control E9, and slot-dispatch controls all fired, and the entry ran in
  phases 2/4/6. The run stalled before VI-1024 and hit the known
  `fillSampleStreamRange+336` SIGBUS family. Generated direct calls do not
  populate `ctx->r31` for this shared C call, so every logged guest return
  address was zero; caller ownership is unevaluable, and the next probe must
  tag callsites rather than infer the owner from the shared entry.
- The s1152 callsite probe is live at all 13 generated `submitGfxFrame` sites
  and the Debug target links. Both controlled captures reached only the
  640→2→640 sequence for the 180-second phase gate, with selector positive
  control (1), slot dispatch (6,438), no crash, and 168 callsite rows. The
  rows include phase-6 `0x800A64AC`, but no VI-1024 phase was reached;
  H1/H2/H3 therefore remains unevaluable. The corrected retry used
  `ROGUESQ_LOG_E9_UNIFIED=1` but still had zero unified-E9 rows, so no E9
  positive-control claim is made.
- The s1153 repeat used the documented phase-relative input schedule and all
  controls. The selector positive control fired (1), slot dispatch remained
  live (6,424), and the callsite table recorded 168 rows, including phase-6
  `0x800A64AC`; the run stayed crash-free at 640→2→640 for 180 seconds. It
  still produced no VI-1024, E9 provenance, or unified-E9 row. The
  `vi-submitgfx-owner` thread is therefore closed as unevaluable after three
  consecutive attempts; the callsite data does not select H1/H2/H3.
- The s1154 post-640 producer census timed out at width 640 after the stable
  640→2→640 sequence. The independent selector positive control fired once,
  slot dispatch logged 6,438 rows, and there were no crash or SIGBUS markers;
  generated selector, predecessor, and `osViSetMode` producer markers were all
  zero. This selects the producer-absent active-loop path (H2) and moves the
  next audit to the state writer; the corrected NPC boundary remains
  unevaluable at runtime.
- The s1155 complete generated/companion state-writer census found reachable
  post-640-capable selector writers. `buildAndRegisterDefaultMaterial`
  (`0x80017B88`) writes selector bytes at `0x8011A862`, `0x8011A864`, and
  `0x8011A865`; its companion inventory identifies both boot and per-frame
  `advanceVideoFrame` callers. `applyPendingViChanges` (`0x8001B7F0`) also
  writes `0x8011A862` and `0x8011A865`. `selectAndApplyViMode` reads source
  records at `0x80128D50`, `0x80128DA0`, `0x80128DF0`, or `0x80128E40` and
  copies four 16-byte chunks into `0x80128C90`; the census found no generated
  writer to those source records. This selects H1: a generated post-640-capable
  selector writer exists, so the next audit is its actual phase ordering and
  value change, not a non-generated-owner pivot. The `NEXT.md` shorthand
  `0x8011A865..67` was imprecise; the three selector bytes used by the code are
  the non-contiguous `0x8011A862`, `0x8011A864`, and `0x8011A865`.
- The s1156 phase-gated writer capture passed the independent selector positive
  control and slot-dispatch control. All three tagged generated callsites ran;
  after committed width 640, `applyPendingViChanges` at callsite `0x80019914`
  changed selector bytes `01/00/00` to `01/00/01`. Host phase transitions
  independently recorded the same `640→2→640` lifecycle. This selects H1,
  a post-640 selector writer as the causal candidate. The writer log's 512-row
  budget saturated later `0x80019914` rows, so downstream consumer ordering is
  the next bounded check.
- The s1157 consumer capture passed the independent selector positive control,
  slot-dispatch control (6,424 rows), and the 640 phase gate, but did not
  reproduce s1156's selector transition: live `0x80019914` rows were
  `00/00/00→00/00/00` at committed width 640. There were zero selector-control,
  selected-record, predecessor, or selector-callsite rows, while six host
  `osViSetMode` requests independently recorded `320→2→640→640→2→640`.
  This is an unevaluable non-reproduction, not evidence for H1/H2/H3; the
  next unit must establish why the writer transition is absent before tracing
  consumer ordering.
- The s1158 retry passed the selector-positive and slot-dispatch controls and
  reproduced the transition. At post-640 `applyPendingViChanges` entries, the
  pending masks were initially `0/0`; a request-mask row then set pending B to
  `0x11`, and the next apply consumed it, storing selector A and changing
  `01/00/00→01/00/01`. The tagged callsite and host VI request independently
  agree on the transition. This selects H2 for s1157's non-reproduction: its
  pending input/state path was different, not an address or store defect.
- The s1159 consumer capture and fixed retry both passed the selector-positive
  and slot-dispatch controls. The post-640 writer transition
  `01/00/00→01/00/01` occurred, and host `osViSetMode` then requested
  `0x80128DF0` (width 640), but generated `selectAndApplyViMode` entry,
  selection, and callsite markers remained zero. This selects H3: the host VI
  request is on an independent path and the generated selector consumer is
  not reached after the transition. No crash occurred; the next audit is the
  complete generated VI call-path census.
- The s1160 static census found five generated `osViSetMode_recomp` edges:
  `preNmiResetThread` at `0x80001764`, `initVideoSubsystem` at `0x8001B720`,
  `applyPendingViChanges` at `0x8001B8DC`, `swapBufferWithViMode` at
  `0x8001BB54`, and `selectAndApplyViMode` at `0x8001BC28`. The direct
  `0x8001B8DC` edge is the only one on the `0x80019914` writer path and can
  submit `0x80128DF0` without entering `selectAndApplyViMode`; the other
  edges are boot/reset, frame-swap, or selector-owned paths. This identifies
  H3's independent generated owner and closes the duplicate-edge ambiguity.
- The s1161 runtime reconciliation passed independent controls: selector-positive
  fired once and slot dispatch logged 6,864 rows. At stable VI width 640,
  `applyPendingViChanges` logged a live direct edge at `0x8001B8DC` with mode
  pointer `0x80128DF0`, and the host independently logged the same request;
  generated selector-consumer markers remained zero. This selects H3 at runtime
  and rules out a stale or misplaced direct-call marker for this lifecycle. The
  run reached no 1024 phase and had no crash.
- The s1163 runtime-origin capture rebuilt successfully and passed its
  independent slot-dispatch control (8,192 bounded entry rows through phase 6).
  It remained in the known `640→2→640` lifecycle for 209 seconds, never reached
  VI 1024, and produced zero stack-guard or crash rows. The `slotDispatcherIter+872`
  writer-origin discriminator is unevaluable in this capture; the positive
  control does not make the eventual fault path observable.
- The s1164 runtime-origin retry passed slot-dispatch (8,192 bounded entries)
  and crash controls, but again stayed pre-1024 and terminated in an unrelated
  RT64 `copyToRAM` fault at guest PC `0x8000B650` (`si_addr=0x11ffbc000`),
  after wild-width writeback skips. It produced no slot-SP guard row. This is
  a second unevaluable pre-1024 capture, not evidence for H1/H2/H3; the next
  probe must classify the pre-1024 writeback/crash reachability path.
- The s1165 pre-1024 writeback capture passed independent controls: 8,192
  bounded slot-dispatch entries and 25 writeback control rows. It recorded 32
  wild-width skips, zero overlap rows, and zero crash rows while remaining in
  the 640→2→640 lifecycle beyond the 600-second hard cap. Compared with the
  s1164 crash capture, this supports H3, nondeterministic pre-1024 reachability,
  and shows wild-width skips alone do not discriminate the crash cause. H1/H2
  remains unevaluable; no mitigation was added.
- The s1166 resource-marker capture passed slot-dispatch (8,192), writeback
  control (57), and crash controls. It recorded no `[rt64-alloc]` marker and
  no `copyToRAM` fault; instead it hit an Apple Metal compiler-cache SIGSEGV
  at guest PC `0x8000B650` before VI 1024, after 30 wild-width and 4 OOB
  writeback skips. Together with s1165's controlled stable arm, this advances
  H3: no RT64 resource marker precedes the pre-1024 failure family, and
  writeback skips alone do not select H2. No mitigation was added.
- The s1168 complete generated-call audit found exactly two direct
  `musyxSynthFrame` callers: the inline wait pumps in `shutdownAudioEngine`
  and `waitForMusyXAudioTaskDone`. Their frames are `-0x20/+0x20` and
  `-0x18/+0x18`, respectively, with saved `$ra` slots at `+0x18` and
  `+0x10`; both callers match the companion overlay registration. The
  generated tree also contains the function definition and no other direct
  or statically addressed wrapper call. The periodic active path is the
  separately documented indirect VI callback lookup, so this selects H2 for
  the generated idiom and rejects H1/H3 as literal callsite explanations.
- The s1169 phase-gated callback capture passed both independent controls:
  callback-table slot reads and indirect `get_function(0x8009123C)` resolution
  were live in phases 4 and 6. Sampled `musyxSynthFrame` entries consistently
  received `entry_sp=0x8011C8C0`, `prologue_sp=0x8011C880`, and `entry_ra=0`;
  the latter is expected for the runtime's indirect `(rdram, ctx)` ABI. This
  selects H2, a valid callback handoff with the fault downstream, and rules
  out a corrupted callback `$sp`/`$ra` handoff in this capture. The run stayed
  in `640→2→640`, reached no VI-1024, and had no crash, so downstream origin
  remains open.
- The s1170 complete callback-idiom census found 7 in-scope generated
  indirect invocation sites: 1 periodic worker site, 1 four-slot VI callback
  site, 2 `musyxSynthFrame` sites, 1 mixer-init site, and 1 site in each audio
  wait helper. Every site has a balanced stack adjustment and saved/restored
  `$ra`, and all seven owning function boundaries match companion symbols.
  The current poll's observed target `0x8009123C` also matches
  `musyxSynthFrame`; no malformed site or unresolved in-scope row was found.
  This selects H2 and moves the audit into the downstream `musyxSynthFrame`
  operation class.
- The s1171 downstream operation census covered the complete generated audio
  chain: `musyxSynthFrame` has 26 direct calls and two indirect calls;
  `musyxBuildVoiceCommandList` iterates the bounded voice count and writes the
  command ring; `musyxMixActiveVoices` iterates the same voice array with
  stride `0x88`; and `musyxRenderVoiceSamples` forms sample/stream pointers
  from voice fields `+0x34/+0x38/+0x3C/+0x40` before its stream helpers. The
  first possible wild pointer is therefore the per-voice sample/stream path,
  but static source does not reveal its runtime writer or legitimacy, and no
  operation directly identifies the later `0x8000B650` host fault. This is
  H3 for the port-only census; no mitigation was added.
- The s1172 retail-oracle arm passed the whole-RDRAM positive control (10,000
  callbacks, removed cleanly) and delivered the eleven-Start schedule through
  the known width-320/origin `0x006dd280` stall at about 56 seconds. The
  watched retail global `0x001496F8` had one pre-store write attributed to
  guest PC `0x8008F0EC`; the debugger callback reports the old value
  `0xFFFFFFFF`, so this does not reveal the allocated voice-array address.
  No later audio phase was reached, and the target was the global pointer
  field rather than a voice sample field; the intended origin discriminator is
  therefore H3/unevaluable. The oracle gained a small diagnostic that prints
  the watched field value at a detailed access.
- The s1173 corrected oracle accounting passed the whole-RDRAM positive control
  (10,000 writes, removed cleanly) and separated callback access flags from
  watch configuration. The target field had one write at `0x8008F0EC`; the
  write watch counted `1/0/1` (hits/reads/writes), the read watch counted
  `0/0/0`, and no post-store read occurred before the width-320/origin
  `0x006dd280` stall. This selects H2 for the calibration discriminator: the
  current retail path reaches the field write but not a later readable access;
  it does not expose the allocated voice-array base. The first s1173 arm was
  invalid because the frontend attributed one callback to both overlapping
  watches; the fixed rerun is the evidence used here.
- The s1174 post-step retail-oracle calibration passed the whole-RDRAM control
  (10,000 writes, removed cleanly), retained one write at `0x8008F0EC`, and
  produced a post-step callback. The field still read `0xFFFFFFFF` after the
  stepped instruction; the read watch remained `0/0/0`. This selects H2: the
  field is not a valid voice-array base in this path, and no voice range may
  be inferred from it. The post-step callback reported `pc=0x80000000` and
  `prev_pc=0x8008F0EC`, so its PC is not an independent instruction
  attribution.
- The s1175 retail neighborhood watch passed the whole-RDRAM positive control
  (10,000 writes, removed cleanly) and ran through 593 VI frames. The bounded
  `0x001496D0:0x00149730` range was active: 1,142 writes and 2,828 reads.
  PC attribution grouped writes at `0x8008EDB8` (the `D0:EC` block),
  `0x8008EE04/0x8008EE6C` (`0xF0` polling state), `0x8008F0CC` (`0xF4`),
  `0x8008F0E4` (`0xFC`), and `0x8008F0EC` (`0xF8` sentinel write), with
  `0x80091BC0` also writing `0xF4`. The companion symbols identify
  `0x80149700` as the mixer voice-count field, not a pointer. No adjacent
  KSEG0 pointer value was exposed by this watch, so the neighborhood does not
  yet provide a voice-array origin; the next lead must identify the actual
  sample-field writer rather than infer a range from `0x801496F8`.

## Retail VI descriptor boundary

The active static chain is now:

`osTvType=1` → `rsViModeType=0` → NTSC descriptor index bytes →
`gameConfig+0x44=0x1800` → selector `A/B/C=1/0/0` → copied-record offset
`0xF0` → index-0 descriptor → width 320.

Evidence and boundaries:

- `librecomp::init` writes `osTvType=1`; `setViModeType` reads that address,
  not `osResetType`.
- The NTSC index window is ROM-backed and contains mixed 320/640/1280
  descriptors. The active selector must choose one of the 320 records.
- `gameConfig+0x44` has no audited writer and is `0x00001800` in the retail
  image. Its relevant bits produce selector bytes `A/B/C=1/0/0`.
- `initVideoSubsystem` initially loads the NTSC index-0 record into `sp+0x108`.
  The alternate overwrite families require `s7==0`; boot's stack-derived
  `s7` is nonzero, so index 0 is preserved.
- The four-record copy writes table offsets `0x00/0x50/0xA0/0xF0`, then
  reaches `osViSetMode_recomp` without an intervening selector or record store.
- At `0x8001B720`, generated code selects among `0x80128D50`, `0x80128DA0`,
  `0x80128DF0`, and `0x80128E40` using only stack bytes `0x15F` and `0x17F`.
  Boot's established `0x15F=0`/`0x17F=0` state selects `0x80128E40`, exactly
  `base+0xF0`.
- The host `osViSetMode_recomp` forwards `ctx->r4` unchanged to `osViSetMode`;
  the runtime stores the pointer and control, while the VI commit reads
  `common_regs->width` from that mode. No host-side width rewrite exists. This
  closes the active-descriptor pointer/consumer boundary with independent
  generated-code and host-runtime evidence.

## M4 zero-shade boundary

Independent Factor 5 command-reference and same-combiner evidence refute RT64
shade lane/order as the cause. The VTXCOLOR payload is nonzero, while decoded
shade is the fixed `0xFFFF8000` RGB / `0x00008000` alpha sentinel. Retail ROM
and generated code show the shaded emitter reads geometry/vector data rather
than the nearby color field. The missing-lighting/vector numeric origin before
`vmadh v6,v4,v0` remains unresolved. The prior controlled-null recipe is
superseded by the paired capture below; no mitigation is authorized.

The paired accumulator capture now has a valid port-side result. The independent
VMADH control fired 8 rows, and phase-6 target task 201 produced 16 complete
pre/post/VGE tuples and completed records. A local model matched the VMADH
result on all 128 lanes; VGE changed 0/128 lanes. The target records used
`r9` values in `0x00000670..0x000006C0`, with the captured output range at
`r9+0x18..0x4F`. The run did not reach VI-1024 (it remained at 640), so this
does not yet establish retail reachability or ownership of that range.

## M3 indirect-call frame audit

The s1140 whole-class source census found 144 static `jal 0x8003E8DC`
sites in 72 generated caller functions. 143 sites have an ordinary balanced
caller contract: each caller saves/restores `$ra`, has matching negative and
positive `$sp` adjustments, and calls the generated `slotDispatcherIter`
entry directly. `slotDispatcherIter` itself uses `sp -= 0x38`, saves `$ra` at
`0x34($sp)`, restores it, and returns with `sp += 0x38`. Its update callback
and `destroyNpcSlotByIndex`'s destructor callback are the only relevant
`LOOKUP_FUNC` sites; both expand to the standard `get_function(int32_t)` ABI
and invoke the returned `(rdram, ctx)` function pointer.

One site, guest `0x80078894`, is a generated-source anomaly rather than a
balanced reachable caller: it occurs in the `forwardToNpcGeneratorSpawn`
block after an unconditional emitted C `return` at `0x80077AEC`, before a
second `sp -= 0x118` prologue. Independent decomp symbols identify
`npcPowerGeneratorUpdate` at `0x80077AF0`; the generated symbol table gives it
size `0x134C`, ending at `0x80078E3C`, where `spawnDebrisBurstFromTemplate`
begins. The generated host body nevertheless places the `0x80077AF0` prologue
and live `0x80078894` call after the earlier function's emitted `return`. This
selects H-coalesced-real: preserve the `0x80077AF0` function boundary in the
regeneration/input function table so a separate host function is emitted. It
is a generated-boundary defect, not evidence by itself of runtime stack
corruption.

## Superseded conclusions

- s1105's `H-gate-stale-or-unseen-writer` was superseded by s1106's corrected
  physical-byte sample, which repeatedly observed nonzero `0x8011A8A0` at SP
  send boundaries. The old result was believable because the static census
  found no generated nonzero writer, but it did not measure non-generated
  runtime stores.
- s1119's claim that `setViModeType` maps `osResetType` was superseded by the
  generated load and symbol evidence showing `osTvType` at `0x80000300`.
- Earlier width-320 explanations based on a fixed selector, bad mode table,
  or a host logger mismatch are closed by the static chain and independent
  retail controls above.

## Evidence ledger summary

| Sessions | Durable result |
|---|---|
| s820–s880 | Post-sec2 accounting, breadcrumb, coalescer, and oracle routes classified or parked. |
| s881–s951 | M3 idiom inventories closed the audio-channel-field thread. |
| s952–s983 | Dispatcher stack-spill family localized; oracle callback work repaired later. |
| s984–s1013 | Shade decode/source/emission audits moved M4 to accumulator numeric origin. |
| s1014–s1038 | M4 controls repaired; controlled captures remained null and the recipe closed. |
| s1039–s1056 | Retail input/cadence controls passed; width-320 caller and selector dispatch were state-shaped. |
| s1057–s1079 | Hangar/selector/demo/controller boundaries were traced to the pre-main-loop state gate. |
| s1080–s1099 | Generated and retail-oracle audits localized the pre-main-loop path and closed callback delay-slot ambiguity. |
| s1100–s1111 | Port submit/gate probes passed controls but repeated captures lacked the VI-1024 phase; writer attribution stayed open. |
| s1112–s1117 | VI lifecycle and retail-oracle setup were corrected; retail remained width 320 with positive controls. |
| s1118–s1124 | Mode table, TV-type input, selector state, and mixed descriptor widths were reconciled. |
| s1125–s1129 | Boot config `0x1800`, selector `1/0/0`, preserved index 0, and boot-first ordering were resolved. |
| s1130–s1131 | First consumer ordering was resolved; this maintenance pass compacted the live file and migrated durable detail. |
| s1132 | Traced the active VI pointer to copied-table `base+0xF0` and closed host width-rewrite as a cause. |
| s1133 | Static census found `frameStartReset` fully regenerated with 14 call sites and overlay registration; no active fixup restoration exists, closing regeneration omission. |
| s1134–s1135 | Defined and executed the paired M4 port capture; VMADH model and VGE/store path matched on 128 lanes with an independent control. |
| s1137 | Reproduced the retail post-press stall with no M4 target watch; whole-RDRAM control and input passed, but the run never left VI width 320 and sampled in the core's VI-event sleep path. |
| s1138 | Reproduced the width-320 stall with `--oracle-emulator 1`; whole-RDRAM control and all eleven presses passed, so the stall is not specific to the prior execution mode. |
| s1140 | Audited all 144 static calls to `slotDispatcherIter`: 143 caller contracts balance; one `0x80078894` site is after an emitted return in a coalesced generated block and needs boundary resolution. |
| s1141 | Independent decomp and generated symbol boundaries identify `0x80077AF0` as a distinct `npcPowerGeneratorUpdate` entry ending at `0x80078E3C`; the generated host coalesces it after `forwardToNpcGeneratorSpawn`'s return. This selects a regeneration/input boundary defect and closes the static ambiguity. |
| s1142 | Bounded regeneration audit found the split is lost in `make_elf.py`: `npcPowerGeneratorUpdate` is only in `mission_overlay.txt`, but `vram_to_shndx` rejects that source at `0x80077AF0` because it lies in the `.text` VRAM range. The ELF contains `forwardToNpcGeneratorSpawn` at `0x80077AC0` with size `0x137C` and no `0x80077AF0` symbol; N64Recomp then faithfully emits one body. The smallest durable correction is to put the function boundary in the main-overlay symbol input before ELF generation, not to change fixup or N64Recomp. |
| s1143 | Moved `npcPowerGeneratorUpdate` to `main_overlay.txt`, regenerated the ELF and host output, and ran fixup plus CMake. The ELF now has `forwardToNpcGeneratorSpawn` size `0x30` and `npcPowerGeneratorUpdate` at `0x80077AF0` size `0x134C`; generated C has separate functions and the Debug target links. This validates H1/input-boundary and rules out H2 for this defect; runtime causality remains untested. |
| s1144 | Ran the regenerated macOS target under the 1024 VI phase gate. It reached width 640, then timed out at 180 seconds with no crash, no 1024 phase, and no explicitly enabled E9/slot-dispatch controls. The result is unevaluable; the corrected boundary's runtime effect remains open. |
| s1145 | Repeated the regenerated-target phase gate with E9 provenance, unified-E9, and slot-dispatch logging explicitly enabled. Slot dispatch was live, but VI stayed at 640 for 180 seconds; there were zero VI-1024, E9-control, unified-E9, and crash markers. The result remained unevaluable. |
| s1146 | Analyzed the s1145 trace: VI stopped changing at width 640 around 7.3s, while slot dispatch and host/audio activity continued to the end of the captured log. This selects a stable active pre-phase loop over an early halt, but leaves the missing 1024 transition unexplained. |
| s1147 | Added a latched phase-scoped `osViSetMode` producer marker and corrected its transient-width gating after the first capture exposed a 640→2→640 sequence. The fixed capture saw producer calls through the requested 640 call, then none; slot/host/audio controls continued, with no E9 or VI-1024. This selects the producer-absent stable loop and leaves NPC-boundary runtime causality unevaluable. |
| s1148 | Rebuilt the regenerated selector probe after the first capture exposed stale instrumentation, then ran a controlled capture with an independent host positive control. The selector caller/control/selection remained absent while six host VI calls, slot dispatch, and task-control E9 activity were live; the run crashed in `fillSampleStreamRange+336` before VI-1024. This selects the post-640 selector-caller-absent loop and leaves NPC-boundary causality unevaluable. |
| s1149 | Added phase-aware entry and exact-edge markers for the sole generated selector predecessor, made the probe script idempotent, rebuilt, and ran the 1024 phase-gated capture. The independent selector positive control fired, slot dispatch reached 8,192 rows, and the run reached only the 640→2→640 sequence before SIGBUS in `allocateDisplayListBuffer+3648` at guest PC `0x8000E29C`; all predecessor and selector markers were zero. This selects H2 again and rules out a reachable post-640 invocation of the unique selector predecessor in this run; NPC-boundary runtime causality remains unevaluable. |
| s1150 | Static owner census found 144 direct `slotDispatcherIter` sites in 72 generated callers, including the mission and cinematic frame-loop families. `freeRenderSubsystemResources` is the sole generated caller of `selectAndApplyViMode`, while E9 production is host-side through `submit_rsp_task` and RSP task handling. Companion symbols agree on the named phase-loop owners and contain no omitted owner edge; this selects H2 path separation and rules out H3 for the censused graph. |
| s1151 | The shared `submitGfxFrame` entry marker fired in phases 2/4/6 with selector, E9, and slot controls live, but the run stalled before VI-1024 in `fillSampleStreamRange+336`. All guest return addresses were zero because generated direct C calls do not populate `ctx->r31`; the shared-entry owner discriminator is invalid, so callsites must be tagged directly. |
| s1152 | Added durable phase-scoped markers at all 13 generated `submitGfxFrame` callsites and rebuilt. The corrected retry passed selector and slot controls, logged 168 callsite rows including phase-6 `0x800A64AC`, and ran crash-free through 640→2→640, but never reached VI-1024 and logged zero unified-E9 rows. Owner hypotheses remain unevaluable. |
| s1153 | Repeated the callsite capture with the documented phase-relative input schedule and all controls. Selector positive control fired, slot dispatch logged 6,424 rows, and callsites logged 168 rows including phase-6 `0x800A64AC`; the run stayed crash-free through 640→2→640 but produced no VI-1024, E9 provenance, or unified-E9 rows. After three consecutive unevaluable owner attempts, this thread is closed without selecting H1/H2/H3. |
| s1154 | Ran the phase-scoped producer census with the independent selector positive control and slot-dispatch control. The run timed out at width 640 after 640→2→640; selector positive fired once, slot dispatch logged 6,438 rows, generated selector/predecessor/producer markers were zero, and no crash/SIGBUS occurred. This selects H2, the stable loop without a generated VI producer, and sends the investigation to the state writer. |
| s1155 | Static-censused the live generated tree and companion symbols. `buildAndRegisterDefaultMaterial` writes selector bytes at `0x8011A862/0x8011A864/0x8011A865` from boot and per-frame callers; `applyPendingViChanges` writes `0x8011A862/0x8011A865`. `selectAndApplyViMode` reads the four source records at `0x80128D50/0x80128DA0/0x80128DF0/0x80128E40` and copies them to `0x80128C90`; no generated source-record writer was found. This selects H1, a post-640-capable generated selector writer, and moves the next probe to writer phase/value attribution. |
| s1156 | Added durable callsite probes and a host committed-width accessor, rebuilt successfully, and ran one phase-gated capture. The selector positive control fired once, slot dispatch logged 6,424 rows, all three tagged writer callsites ran, and `0x80019914` changed selector `01/00/00→01/00/01` at committed width 640 after the `640→2→640` lifecycle. This selects H1, while the saturated apply-site budget leaves downstream consumer ordering open. |
| s1157 | Rebuilt and ran the phase-gated consumer capture. Selector positive and slot-dispatch controls passed, but the live `0x80019914` writer rows stayed `00/00/00→00/00/00`; no generated selector-consumer rows appeared. Host VI requests still recorded `320→2→640→640→2→640`. The planned H1/H2/H3 discriminator was unevaluable and the next unit moves to the missing-transition cause. |
| s1158 | Re-ran the phase-gated writer capture with pending-mask and store-path attribution included. Selector-positive and slot-dispatch controls passed. The post-640 sequence showed pending `0/0`, then request-mask `pending B=0x11`, then `applyPendingViChanges` storing selector A and changing `01/00/00→01/00/01`; host VI logging independently recorded the matching 640 request. This selects H2 for s1157's non-reproduction and rules out an address/store defect in this capture. |
| s1159 | Ran the consumer-order capture and a fixed retry. Both passed selector-positive and slot-dispatch controls; both observed the selector transition and host request, but zero generated selector-consumer entry/selection/callsite rows. This selects H3, an independent host VI path, and moves the next unit to a complete static call-path census. |
| s1160 | Static-censused all five generated `osViSetMode_recomp` edges and the sole selector consumer. The direct `applyPendingViChanges` edge at `0x8001B8DC` is the only edge on the `0x80019914` writer path and can submit `0x80128DF0` without entering `selectAndApplyViMode`; the other edges are boot/reset, frame-swap, or selector-owned paths. This identifies H3's generated owner and closes the duplicate-edge ambiguity without a build or run. |
| s1161 | Rebuilt and ran the phase-gated runtime reconciliation with selector-positive and slot-dispatch controls. The controls fired (1 and 6,864); at stable VI width 640, the direct `0x8001B8DC` marker carried `0x80128DF0` and the host independently logged the same request, while selector-consumer markers stayed zero. This selects H3 and rules out a stale/misplaced direct-call marker for this lifecycle. The run timed out before VI-1024, with no crash. |
| s1162 | Completed the whole generated `slotDispatcherIter` caller census: 144 direct sites across 72 callers, zero static indirect targets to `0x8003E8DC`, 72/72 companion-entry matches, and no unbalanced stack/return idiom. The `0x80078894` site is inside the corrected standalone `npcPowerGeneratorUpdate` boundary. This selects H1 and rules out a generated caller-frame idiom or the old coalesced-boundary explanation; runtime-side frame/value origin remains open. |
| s1163 | Rebuilt and ran the phase-gated runtime-origin capture with slot-dispatch and stack-guard controls. Slot dispatch produced 8,192 bounded entries through phase 6, but the run stayed in `640→2→640` for 209 seconds and was SIGKILLed after no VI-1024 transition; stack-guard and crash rows were zero. The planned writer-origin discriminator was unevaluable, so no H1/H2/H3 conclusion or mitigation is justified. |
| s1164 | Rebuilt and reran the runtime-origin capture. Slot-dispatch and crash controls were live (8,192 dispatch entries and 36 crash rows), but VI 1024 was not reached; the process terminated in RT64 `copyToRAM` at guest PC `0x8000B650` with `si_addr=0x11ffbc000`, after wild-width writeback skips, and no slot-SP guard row. The writer-origin discriminator remains unevaluable; no H1/H2/H3 conclusion or mitigation is justified. |
| s1165 | Rebuilt and ran the pre-1024 writeback reachability capture. Slot dispatch logged 8,192 entries; writeback control logged 25 rows including 32 wild-width skips, with zero overlaps and zero crashes. The process stayed in 640→2→640 beyond the 600-second cap and was SIGKILLed. Compared with s1164, this supports nondeterministic reachability (H3) and shows wild skips alone do not classify the crash; no mitigation was added. |
| s1166 | Rebuilt and ran the resource-marker capture with slot, writeback, crash, and RT64-allocation controls. All controls passed; there were no RT64-allocation markers and no `copyToRAM` fault. The run instead hit an Apple Metal compiler-cache SIGSEGV at guest PC `0x8000B650` before VI-1024, after 30 wild-width and 4 OOB skips. Together with s1165, this advances H3 and closes the resource-marker audit; no mitigation was added. |
| s1167 | Rebuilt and ran the operation-boundary capture with slot, writeback, crash, DPC, and RT64-allocation categories. Controls passed; the run stayed pre-1024 and hit a Bus error at guest PC `0x8000B650` in `musyxSynthFrame+2796`. No DPC/RT64 operation or allocation marker followed the final writeback row before the fault, so this selects the valid different-failure H3 arm and adds no mitigation. |
| s1168 | Completed the generated `musyxSynthFrame` callsite audit. The only two direct callers are the inline pumps in `shutdownAudioEngine` and `waitForMusyXAudioTaskDone`; their `-0x20/+0x20` and `-0x18/+0x18` frames, saved-return slots, and companion overlay registration agree. The ordinary periodic path is the separately documented indirect VI callback lookup. This selects H2 for the generated idiom, rejects H1/H3 as literal callsite explanations, and adds no build, runtime probe, or mitigation. |
| s1169 | Rebuilt and ran one phase-gated indirect-callback capture. Callback-table slot reads and `get_function(0x8009123C)` resolution were both live; phase-4/6 entry rows consistently showed `entry_sp=0x8011C8C0`, `prologue_sp=0x8011C880`, and `entry_ra=0`. The valid `(rdram,ctx)` handoff selects H2 and rules out callback stack/return corruption for this run; no VI-1024 or crash occurred, so downstream origin remains open. |
| s1170 | Completed the bounded static callback census without building or running. There were 7 in-scope generated indirect invocation sites: periodic worker (1), VI callback loop (1 site over 4 table slots), `musyxSynthFrame` (2), mixer init (1), shutdown wait (1), and audio-task wait (1). All 7 had balanced `$sp`/`$ra` contracts and companion-symbol-matched owning boundaries; the current poll's observed `0x8009123C` target matched `musyxSynthFrame`, with no malformed or unresolved in-scope row. This selects H2 and moves the audit to downstream `musyxSynthFrame` operations. |
| s1171 | Completed the bounded static downstream operation census without building or running. The generated chain contains 26 direct and 2 indirect calls in `musyxSynthFrame`, bounded voice-array iteration in `musyxMixActiveVoices`, command-ring construction in `musyxBuildVoiceCommandList`, and sample/stream pointer formation from voice fields `+0x34/+0x38/+0x3C/+0x40` in `musyxRenderVoiceSamples`. The first possible wild pointer is the per-voice sample/stream path, but its runtime writer and legitimacy remain unresolved and no static operation ties it to the later `0x8000B650` host fault. This selects H3 for the port-only census; no mitigation was added. |
| s1172 | Ran the retail oracle with a whole-RDRAM control and the eleven-Start schedule. The control reached 10,000 callbacks and was removed; the run stalled at width 320/origin `0x006dd280` after all presses. A write to the global voice-base field `0x001496F8` was attributed to PC `0x8008F0EC`, but the callback is pre-store and exposed only `0xFFFFFFFF`; no audio phase or sample-field write was reached. This is H3/unevaluable for the intended discriminator; no mitigation was added. |
| s1173 | Fixed the oracle's overlapping-watch accounting so each callback is counted only when its actual READ/WRITE flags match the watch. The whole-RDRAM write control reached 10,000 and was removed; the voice-base write watch recorded one write at `0x8008F0EC`, the read watch recorded zero, and no post-store read occurred before the width-320 stall. The corrected result selects H2 for the calibration: this path has no readable post-store pointer value, so no voice-array range was inferred and no mitigation was added. |
| s1174 | Added a one-instruction debugger step after the attributed retail write and captured the field in the following callback. The whole-RDRAM control still reached 10,000 and was removed, the write watch remained `1/0/1`, and the read watch remained `0/0/0`; the post-step field was still `0xFFFFFFFF`. This selects H2: the watched field is not a usable voice-array base in this path. The post-step callback's `pc=0x80000000`/`prev_pc=0x8008F0EC` pair is not a second instruction attribution. No mitigation was added. |
| s1176 | Correlated all s1175 writer PCs to generated instructions. `0x8008EDB8` is a dynamic 16-entry AI buffer-pointer table store; `0x8008EE04/0x8008EE6C` update the audio-buffer index byte; `0x8008F0CC` stores the channel count; `0x8008F0E4/0x8008F0EC` store allocation and voice-base globals; and `0x80091BC0` stores the audio scratch pointer. None is a sample/stream-field writer. The first such generated stores are `musyxInitVoiceFromSample` at `0x800921E8/0x80092220/0x80092228/0x80092230`, targeting computed voice-slot offsets `+0x34/+0x38/+0x3C/+0x40`. This selects H1 for the next ground-truth execution watch, with the target range still unmeasured. |
| s1177 | Ran the retail oracle execution watch for all four `musyxInitVoiceFromSample` PCs with separate whole-RDRAM controls. The write control reached 10,000 callbacks and the read control reached 64,047,786 callbacks; all eleven scheduled presses were delivered. The run remained at VI 320 and all four writer PCs had zero hits. This selects H2 for the driven attract path and rules out authorizing a destination-range watch from this capture; no mitigation was added. |

| s1180 | Completed the static earlier-`$sp` value-origin audit without building or running. The 144 direct `slotDispatcherIter` sites across 72 callers contain only balanced frame arithmetic; no caller has a non-prologue `r29` load or assignment. Runtime code has one executable `r29` initializer, `run_thread_function` from the scheduler's thread `sp`; hook/event paths preserve whole contexts but do not replace it. This selects H3 and rules out a direct caller-side or named runtime context handoff as the invalid-value source. The next unit is an earlier guest value-producer audit; no mitigation was added. |
| s1181 | Completed the whole generated `r29` assignment and context-edge audit without building or running. There are 4,919 `ctx->r29` assignments; 67 are outside ordinary frame arithmetic, with five valid `r30` frame setups, three entrypoint bootstrap writes, and 59 assignments in unrelated/data-like audio, OS, and helper blocks. The 144 target callsites remain balanced, no generated alternate context is constructed, and none of the enumerated producer blocks has a call edge into the target family. This selects H3 and moves the investigation to broader guest memory/value writers; no mitigation was added. |
| s1182 | Completed the broader generated dynamic-writer census without building or running. It enumerated 72 `zmemcpy`, 20 `memcpy_recomp`, four `osPiStartDma_recomp`, 13 controller, and flash helper sites. Dynamic copy/DMA destinations have no proven mission/cinematic edge plus frame-overlap span; controller and flash writes are bounded to their own structures. This selects H3 and rules out a named reachable writer-to-frame edge; no mitigation was added. |
| s1183 | Completed the generated `SD`/wide-copy audit without building or running. It classified 1,356 non-`r29` `SD` sites and 13 target-path `zmemcpy` calls; target callers use ordinary frame-local stores and fixed bounded copy lengths, with no reachable destination/span covering the `slotDispatcherIter` saved frame. The `SD` macro and host accessor add no hidden broadening. H3 selected; no mitigation added. |
| s1184 | Completed the generated `do_swl`/`do_swr` partial-store audit without building or running. There are 414 calls across 66 functions; only five functions also call `slotDispatcherIter`, and their partial stores are caller-local or bounded object/global writes with no span covering the callee's saved frame. The helpers align to and write one guest word through `MEM_W`, with no host-side span broadening. H3 selected; no mitigation added. |
| s1185 | Completed the generated narrow-store audit without building or running. There are 23,128 `MEM_H`/`MEM_HU`/`MEM_B`/`MEM_BU` references and 351 stores in the 72 target callers, including 83 caller-`r29` stores; all are caller-local or bounded object/global writes with no span covering the callee's saved frame. The four host macros preserve the computed address and exact byte/halfword span. H3 selected; no mitigation added. |
| s1186 | Completed the generated `MEM_W` audit without building or running. There are 3,633 word stores in the 72 target callers; all caller-`r29` stores use nonnegative offsets outside the callee's saved frame, and the non-`r29` stores are bounded object/global or unrelated paths with no stack-derived negative alias. The host macro is an exact four-byte write. H3 selected; no mitigation added. |
| s1187 | Completed the generated `MEM_WU` load audit without building or running. Five loads were classified: two bounded texture-row assembly loads, one unrelated OS/global-mask load, and two unrelated audio-generated loads (one after an explicit return, one in a malformed tail). The `MEM_WU` macro is an exact unsigned four-byte access matching the computed guest address. H3 selected; no mitigation added. |
| s1188 | Completed the generated `MEM_D`/`LD` audit without building or running. There are 1,404 references: 1,247 `r29` frame restores and 157 non-`r29` loads. Only 11 load directly into GPRs; the rest feed floating-point state. The non-frame GPR loads are bounded decode/audio or malformed/data-like blocks with no reachable edge to a frame-overlapping store. `LD` reconstructs exactly two guest words at the computed address, with no host-side span broadening. H3 selected; no mitigation added. |

## Ranked next steps

1. Keep audio closed. Do not add a destination watch or mitigation from the
   zero-hit writer capture. Reopen only with a new independent lead that
   reaches an audio-initialization or voice-allocation phase beyond the driven
   VI-320 attract path and can first pass the whole-RDRAM controls.

2. Continue the M3 systematic static audit with the next complete generated
   partial-load idiom: enumerate `do_ldl`/`do_ldr` and their consumers.
   Classify every site for a target-path pointer or frame-overlapping writer;
   do not add a guard unless a reachable writer edge is established.

The s1162 generated frame-idiom census is closed: 144 direct calls across 72
callers all have balanced stack and return contracts, all companion entry
addresses agree, and no static indirect call targets `slotDispatcherIter`.
The corrected `npcPowerGeneratorUpdate` boundary contains the old
`0x80078894` call, so the remaining +872 fault-origin question is runtime-side.

The bounded frameStart/regeneration census is closed: `frameStartReset` is
present in generated output with its 0x8000A6CC body, 14 generated call sites,
the `funcs.h` declaration, and the overlay registration at offset 0xA28C with
size 0x190. The active fixup script contains no executable frameStart/reset
or site-restoration rule; its mentions are historical comments. This selects
H-regenerated and rules out regeneration omission as the explanation for the
isolated SIGBUS. The remaining fault-origin question is runtime-side and does
not justify a mitigation from this census.

## Method and safety rules

- Before runtime instrumentation, consult `tools/oracle/README.md` and
  `docs/F5-UCODE-REFERENCE.md`; arm a whole-RDRAM positive control.
- Gate animated comparisons on VI transitions; scope counters and log budgets
  to the phase; batch all instrumentation into one build/run.
- Use SIGKILL, launch from `build/`, and use capture paths whose final
  component does not begin with `.`. Queue repeat soaks rather than babysit.
- Diagnostics in generated code belong in fixup scripts. Regeneration order is
  `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then CMake.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. Changes under `lib/` require patch export.
- A null result is worthless without a positive control in the same run.
  Before any mitigation, name the writer and assess legitimacy with an
  `ORIGIN:` line.
