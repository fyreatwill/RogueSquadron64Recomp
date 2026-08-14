# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`. Durable history is in
[`docs/PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); do not reopen closed
lineages without a new class-level lead.

Reviewed through s975 (2026-08-13). The active blocker is authoritative
FULL_SYNC/E9 accounting after the post-sec2 gate. M5 audio de-stubbing is
closed; M3 work is limited to systematic idiom-class audits.

## User directive

1. Run maintenance when this file exceeds 60,000 bytes.
2. Pursue only a genuinely new M5 audio lead; the existing campaign is closed.
3. Do M3 crash work only as complete idiom-class audits, not reactive chases.

## Current truth

- Overlay dispatch is sufficiently fixed for mission entry and post-sec2
  outdoor presentation; the original boot/menu hypothesis is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Any new mitigation requires an `ORIGIN:` naming the
  writer and assessing legitimacy.
- Phase-gated port captures reach VI width 1024 with independent
  `emit/raw/dispatch/match` controls. Pre-chain crashes are disjoint families
  and do not classify parser loss.
- s833–s840 established exact ordinary producer/consumer task and range
  identity for late E9-bearing work, including zero synthetic markers. The
  remaining bridge/parser delta is best explained by command-boundary/span
  accounting, but the residual extended condition remains unclassified.
- s842–s853 moved candidate B4/BF ownership from Factor 5 to RDP garbage-shaped
  entries; no mitigation or legitimacy conclusion followed.
- s855–s861 showed that `0x8000834c` is a stale process-wide breadcrumb from
  `drainMeshReleaseQueue`, not attribution for `getNextSlotNpcTypeId`.
- s862–s880 found invalid port coalescer entry state, but retail remains at VI
  width 320 and the oracle has no safe post-write writer/value channel. The
  coalescer line is parked.
- s881–s938 completed a long sequence of static idiom inventories. Local
  bounds, caller shapes, and termination were classified where stated, but
  dynamic writer/value legitimacy remains unproven. s935 found a pointer/index
  mismatch in `musyxTriggerVoiceAttack`; s937 found that `musyxStopVoice` has
  one direct caller that passes constant zero, but no independent proof of
  global base/count lifecycle or register-indirect callers. s938 found one
  direct `stopVoiceByKey` caller and a bounded allocator-produced index, but
  the path uses `stopVoiceMarkRetrigger` rather than `musyxStopVoice`; active
  list pointer and base/count legitimacy remain unproven. s940 found that
  `D_8013D880` is a 32-entry `0x17C`-stride record array and that count writers
  clamp to `0..0x20`; reset/release/stop paths use `-1` for the `+0x64` handle
  sentinel and note-on constructs the handle. The four
  `stopVoicesByHandle` callers agree on linked-list node `+0x8` handles, but
  node `+0xC` index provenance and runtime value legitimacy remain unproven.
- s941 found four generated sorted-list insertion/reuse writers for node
  `+0xC`; each copies the owning voice record's `+0x64`. Unlink/reuse preserves
  the list contract, but the complete `+0x64` writer set and possible indirect
  paths do not prove every copied value is an in-range `0..31` slot index.
- s942 separated the remaining generated `+0x64` stores: reset/release/stop
  paths write the `-1` sentinel, the `tickAudioChannel` path writes `$s1` after
  reachable initialization to `-1`, and neighboring channel/fade functions
  write unrelated state fields. The sorted-node copies remain structurally
  coherent, but indirect callers/writers and the complete handle-to-slot value
  lifecycle remain unproven. H-stop-voices-by-handle-index-unclassified
  remains selected.
  H-stop-voices-by-handle-index-unclassified remains selected; no mismatch or
  mitigation conclusion followed.
- s943 audited the allocator and all four sorted-node `+0xC` writers. No
  direct generated call to `allocVoiceHandleNode` was found; the only nearby
  `jalr` is a generic comparator callback and is not proven to target it. The
  allocator at `0x80086524` and duplicated insertion/reuse bodies at
  `0x80086E40`, `0x8008738C`, and `0x800877E0` each copy a voice-record
  `+0x64` into the node. List links and handle fields are coherent, but the
  complete indirect dispatch and handle-to-slot value lifecycle remain
  unproven. H-stop-voices-by-handle-index-unclassified remains selected.
- M5 audio de-stubbing is closed. Do not reopen it without a genuinely new
  lead. M4 correctness remains parked behind the active blocker.
- s944 audited `startNoteOnVoice`: there are exactly four direct callers and no
  generated-source or companion-symbol register-indirect reference. Its return
  is the sorted-list handle counter, not the voice slot; the allocated slot is
  packed into the low byte of the voice record's composite `+0x64` handle at
  `0x80087294`. The four sorted-node `+0xC` copies preserve that full-handle
  contract, and `stopVoicesByHandle` extracts the low byte as the slot before
  validating the full handle. Runtime legitimacy of all record pointers and
  the complete indirect handle lifecycle remains unproven.
- s945 traced all four node `+0xC` copy sources. The three inline bodies at
  `0x80086E40`, `0x8008738C`, and `0x800877E0` derive the source from the
  `0x8013D880 + slot*0x17C` voice table. The standalone allocator body at
  `0x80086524` receives its source through `$a0`, but has no direct generated
  caller; the only nearby `jalr` is an unrelated comparator callback. The
  three inline sites are structurally valid; standalone reachability and any
  indirect allocator edge remain unclassified.
- s946 exhaustively searched generated audio sources, overlay metadata, and
  companion symbols for `allocVoiceHandleNode` reachability. There are no
  direct references outside its definition/registration and no audio-overlay
  `jalr` candidate besides the generic comparator callback at `0x80085C70`.
  That callback receives its target from the caller stack and is documented as
  a comparator; no caller or assignment targets the allocator. This selects
  standalone-dead at the static call-graph level, but runtime function-pointer
  reachability and handle-value legitimacy remain unproven.
- s947 exhaustively classified the remaining generated `+0x64` stores in
  funcs_21–23. The seven voice-record stores are sentinel `-1` writes or the
  tick-path `$s1` copy; the three other stores are float fields in
  `advanceVolumeFadeEnvelope`, not voice handles. The only audio-overlay
  `jalr` remains the generic comparator at `0x80085C70`, and companion symbols
  add no allocator-targeted edge. This selects
  H-stop-voices-by-handle-index-unclassified: no mismatch writer was found,
  but runtime indirect reachability and handle-value legitimacy remain open.
- s948 exhaustively inventoried generated `+0x64` reads in funcs_21–23. Five
  live reads are voice-record/sorted-node contract uses, one is the unrelated
  floating-point envelope field in `advanceVolumeFadeEnvelope`, and one in
  `soundMacroOpKeyOnNote` uses its caller context after note-on to feed a
  slot-indexed table. The sound-macro context and its `+0x64` writer lifecycle
  remain unresolved, so H-stop-voices-by-handle-index-unclassified remains
  selected; no mismatch or mitigation conclusion followed. The stack
  spill/reload at `startNoteOnVoice` was excluded as non-object data.
- s949 found exactly one direct generated caller of `soundMacroOpKeyOnNote`:
  `tickAudioChannel` at `0x8008C1EC`, passing `$s0`. The callee reads that
  channel-context object's `+0x64` after `startNoteOnVoice` and writes it to
  the `0x8013D894 + index*0x17C` table; six generated `-0x276C` stores
  populate that table, but no direct read-side consumer was found through the
  audited address forms. Channel-field provenance and table consumers remain
  unresolved; no mismatch or mitigation conclusion followed.
- s950 exhaustively audited the channel `+0x64` field and the
  `0x8013D894 + index*0x17C` table across generated funcs_21–23. The table has
  eight generated stores and no reads through the audited `-0x276C` form; the
  stores are voice-list/voice-start bookkeeping except for the one
  `soundMacroOpKeyOnNote` store fed by channel `+0x64`. All generated audio
  writers of channel `+0x64` write the `-1` sentinel, including
  `tickAudioChannel`'s `$s1` initialized at `0x8008BF1C`. Companion symbols
  independently identify the channel array base/stride and the sole direct
  caller. The structure is coherent, but channel-field lifecycle and runtime
  legitimacy remain unproven; H-channel-context-field-unclassified remains
  selected.
- s951 closed the two remaining edges: `funcs_21–23` contain exactly one
  `LOOKUP_FUNC`/`jalr` site total (`funcs_21.c:2837`, a generic comparator
  callback in `binarySearchWithComparator`, unreachable from
  `tickAudioChannel`/`soundMacroOpKeyOnNote`), so no indirect dispatch can
  reach the channel object with an unaudited writer; and
  `tickAudioChannel`'s sole caller `tickAllAudioChannels` (`funcs_23.c:4061`)
  passes `$a0 = 0x8013D880 + index*0x17C` — fixed-array indexing, not a
  computed pointer. Both pre-registered discriminator conditions are met, so
  this selects **H-channel-context-field-sentinel-contract**, closing the
  `m3-audio-stop-voices-by-handle-contract` thread (active since s938).
  Residual curiosity (unverified, non-blocking): the store target
  `0x8013D894` is exactly `0x8013D880 + 0x14`, the same base/stride as the
  channel array itself, i.e. the store may write into the channel's own
  struct rather than a separate table — not confirmed this session.
- s952 resolved the recurring `slotDispatcherIter+872` symbol to
  `funcs_8.c:22810`, the generated prologue spill `MEM_W(0x1C, ctx->r29)`.
  `atos`/DWARF maps the host offset and `otool` independently shows the
  prologue store; the companion map identifies `slotDispatcherIter` as the
  NPC-list walker at `0x8003E8DC`. This is a guest-stack-pointer
  (`$sp`/`ctx->r29`) failure before any `gNpcSlotList` access, not an NPC
  record `+0x368` field. The source has 144 direct generated call sites in 19
  files, so the writer/origin class is caller stack-state, not a single slot
  writer; no caller audit or mitigation was attempted. The active hypothesis
  is H-slotdispatcheriter-stacksp-unclassified.
- s953 audited all 144 direct `slotDispatcherIter` call sites in 72 generated
  caller functions. Every caller has the normal generated frame shape: one
  entry `$sp` decrement and a reachable matching restore; the second textual
  restore is duplicated MIPS delay-slot emission. No caller assigns `ctx->r29`
  from a non-frame value. Eight callers contain unrelated `LOOKUP_FUNC`/`jalr`
  calls, so indirect target behavior remains the only unresolved caller-side
  context-corruption branch; no legitimacy or mitigation conclusion followed.
- s954 classified the statically addressed indirect targets in all eight
  callers. Every target either has no `ctx->r29` write or only the generated
  frame decrement/restore pair; no target-side non-frame `$sp` writer was
  found. `runInMissionFrame` additionally dispatches a pointer loaded from
  `0x8010B350 + i*8`, so its target set remains runtime-driven and unresolved.
  The active hypothesis remains H-slotdispatcheriter-stacksp-unclassified;
  no guard or mitigation followed.
- s955 attempted the independent retail-oracle watch of the runtime callback
  table at physical `0x0010B350..0x0010B750`, with a whole-RDRAM positive
  control. The control fired millions of times, but all runs stayed at VI 320;
  PIF tracing showed injected controller-state changes without reaching the
  required later phase. The table watch had zero hits and is phase-unevaluable,
  not evidence against any callback writer hypothesis.
- s956 repeated the documented named-`start` oracle schedule for 90 seconds
  with whole-RDRAM, VI, PIF, and callback-table watches. The positive control
  fired 15,068,831 times and 5,399 VI frames ran, but VI remained width 320;
  the callback-table watch had zero hits. All 11 `sym=40` injections were
  logged, with no PIF transition. This remains phase-unevaluable and points
  the next probe at the input/phase path, not callback-table legitimacy.
- s957 ran undriven and named-`start` retail-oracle arms concurrently for 60
  seconds with whole-RDRAM controls, VI polling, and PIF tracing. Controls
  passed (10,120,336 and 10,146,403 hits); driven delivered all 11 `sym=40`
  presses, but both arms stayed at VI width 320/origin `0x006dd280`, with no
  PIF-trace records. This selects the core/setup phase hypothesis for this
  oracle configuration; callback-table zeros remain phase-unevaluable.
- s959 audited the oracle attachment path and ran a corrected 30-second named-
  `start` arm. The input plugin attached and the press scheduler delivered
  scancode 40; the whole-RDRAM control fired 5,189,202 times. The PIF “trace”
  is only a per-VI `DebugMemRead32` poll, not a game-read attribution, so the
  run cannot distinguish absent game PIF reads from an unobserved trace path.
  VI stayed at 320/origin `0x006dd280`; callback-table reachability remains
  unevaluable. The next probe is a direct physical PIF-range read watch.
- s960 attempted the direct physical PIF-range read watch twice: once paired
  with the whole-RDRAM write control and once alone. Both runs exited `rc=139`
  during RDRAM initialization, before the first VI, with no watch hit. A
  same-configuration whole-RDRAM-only control passed with 1,082,129 write hits
  over 287 VI frames in 5 seconds. This is a tool/core read-breakpoint failure,
  not evidence about retail PIF reads; the PIF-watch hypothesis is blocked
  pending an oracle-path fix.
- s961 isolated the oracle failure by comparing read watches in one bounded
  batch. An ordinary RDRAM read watch survived with 1,105,122 whole-RDRAM
  write-control hits, one read hit, and 299 VI frames. PIF RAM and PIF ROM
  read watches both crashed `rc=139` during RDRAM initialization before VI or
  any hit. The oracle source maps `0x1FC00000` to `read_pif_mem`, unlike the
  surviving plain-RDRAM handler. This selects a PIF-region debugger-handler
  defect over a generic read-watch defect; retail PIF activity remains
  unevaluable and no runtime mitigation followed.
- s962 tested one external-core address-normalization fix: `pif_address()` now
  strips the `0x1FC00000` mapping base before indexing `pif->base`. The
  ordinary-RDRAM arm still passed its positive control (1,105,106 writes, one
  read, 299 VI), while the PIF-RAM arm still exited `rc=139` after RDRAM
  initialization, before emulator start, VI, or any PIF hit. The normalization
  defect is real as a latent handler bug but does not explain this pre-start
  crash; the remaining fault is in the PIF-specific debugger/init path. An
  attempted LLDB batch produced no backtrace and was terminated, so the exact
  failing frame remains unclassified.
- s963 added one batched diagnostic to the external oracle core. The ordinary
  arm completed with 1,105,162 whole-RDRAM write hits and 299 VI frames. The
  PIF-RAM arm reached PIF mapping, breakpoint activation, and the first wrapped
  PIF read at `0x1fc007e4`, then exited `rc=139` before completion. This rules
  out mapping/device initialization as the immediate failure and localizes the
  remaining defect to the debugger callback path after read entry; no runtime
  mitigation or retail conclusion followed.
- s964 added rate-limited PIF-only markers around breakpoint lookup, the
  `RUNNING`→`PAUSED` state assignment, and `update_debugger()` in the external
  oracle core. The ordinary arm passed its controls with 1,105,307 whole-RDRAM
  writes, one ordinary read, and 299 VI frames. The PIF arm reached the wrapped
  read at `0x1fc007e4` but emitted no pre-lookup marker and exited before an
  oracle completion line. This localizes the immediate crash before
  `check_breakpoints_on_mem_access()` enters lookup; the three instrumented
  callback stages remain unevaluable. No runtime mitigation or retail
  conclusion followed.
- s965 added before/after markers around the PIF wrapper's call to
  `check_breakpoints_on_mem_access()`. The ordinary-RDRAM arm passed its
  controls (1,102,500 whole-RDRAM writes, one ordinary read, 298 VI); the PIF
  arm reached the wrapper pre-call marker on `0x1fc007e4`, emitted no
  post-call marker, and exited `rc=139`. This rules out a pre-wrapper/device
  failure and selects the callback call/early-entry boundary, but does not
  identify the callback's failing instruction. No runtime mitigation or
  retail conclusion followed.
- s966 added a first-statement marker to `check_breakpoints_on_mem_access`.
  With the same positive control, ordinary RDRAM completed (1,102,384 writes,
  298 VI), while the PIF arm reached wrapper pre-call but not callback entry or
  wrapper return (`rc=139`). This selects the callback call/entry boundary but
  does not distinguish ABI from callee prologue; no retail conclusion followed.
- s967 audited the external oracle's current source and generated ARM64
  artifact. The source declares four callback arguments and calls it as
  `(pc,address,4,READ|ENABLED)`, but the emitted `read_with_bp_checks` call at
  `0x13d64` sets `w0=pc`, `x1=address`, `w2=3`, and does not set `w3`; the
  callback at `0x48768` has a normal 16-byte-aligned prologue and its first
  marker follows that prologue. Object and dylib timestamps are after both
  edited sources, so this is not safely attributable to a stale dylib. This
  selects an oracle ABI/compiler-artifact mismatch over callback body; the
  exact source-to-artifact cause and crash instruction remain open. No runtime
  mitigation or retail conclusion followed.
- s970 captured the successful forced oracle link. The fresh
  `_obj/device/memory/memory.o` is LLVM bitcode under `-flto`, so it has no
  machine-code relocation to compare; `nm -m` shows its callback reference as
  undefined external. The final dylib binds both wrapper and callback as
  non-external local symbols and emits a direct local call at `0x13d64`, still
  passing `w0=pc`, `x1=address`, `w2=3` with `w3` unset despite source and
  preprocessing showing four arguments `(pc,address,4,flags=3)`. Stale
  product selection is refuted; the remaining boundary is LTO bitcode-to-code
  transformation/ABI state. This is static single-source evidence only.
- s971 compiled both oracle translation units with `-fno-lto` and inspected
  fresh ARM64 assembly. `read_with_bp_checks` emits `w2=4,w3=3` at both
  callback sites, while the current LTO dylib emits `w2=3` with `w3` unset.
  This selects an LTO transformation at the object-to-dylib boundary over an
  effective source/ABI defect. No runtime or retail conclusion followed.
- s972 linked the non-LTO oracle successfully after preserving the Makefile
  linker flags and supplying the Homebrew binutils path through the
  environment. Fresh dylib assembly emits `w2=4,w3=3` at both callback
  sites. The missing-path and command-line-override failures were build setup
  artifacts; ordinary non-LTO compile/link is independently correct. This
  selects the LTO transformation boundary over source, ABI, and non-LTO link
  hypotheses. No runtime or retail conclusion followed.
- s973 built isolated all-non-LTO and mixed oracle dylibs. The mixed arm used
  fresh non-LTO `memory.o` and `dbg_breakpoints.o` with all other objects left
  as LTO bitcode; both callback sites in both fresh dylibs emit `w2=4,w3=3`.
  The mixed recipe is reproducible and correct, ruling out a generic
  LTO/non-LTO link interaction between those two callback objects. The
  remaining static boundary is the individual LTO treatment of `memory.c`,
  `dbg_breakpoints.c`, or their interaction when both are LTO; no runtime or
  retail conclusion follows.
- s974 rebuilt the two single-object mixed arms from a fresh all-LTO baseline.
  Arm A (non-LTO `memory.o`, LTO `dbg_breakpoints.o`) retained the bad
  callback shape `w2=3` with `w3` unset at both sites. Arm B (LTO
  `memory.o`, non-LTO `dbg_breakpoints.o`) emitted the correct `w2=4,w3=3`
  at both sites. This selects the LTO treatment of `dbg_breakpoints.c` as the
  sufficient build boundary; no runtime or retail conclusion followed.

## Recent evidence ledger

The detailed session records are in `PORTING-STATE.md`; durable campaign
history is in PROJECT-OVERVIEW §§27–30.

| Sessions | Result |
|---|---|
| s820–s840 | Width-1024 controls passed; ordinary producer/consumer identity matched; synthetic path absent. |
| s841–s853 | Copy/triangle candidates were RDP-owned; residual extended path remained unobserved. |
| s854–s880 | Breadcrumb, coalescer, retail-oracle, and independent-writer routes were classified or parked; no legitimacy conclusion. |
| s881–s924 | Complete M3 inventories covered model/audio/song/MusyX idioms; no behavior or mitigation changes. |
| s925–s937 | Audio filter/mixer/voice idioms were audited; see PROJECT-OVERVIEW §30. s935 rejected a shared attack-helper contract; s937 structurally passed `musyxStopVoice` but left runtime index/base legitimacy open. |
| s936 | Maintenance pass: compacted this file and migrated durable s925–s935 outcomes to PROJECT-OVERVIEW. No experiment ran. |
| s938 | `stopVoiceByKey` has one direct streamed-voice caller and coherent local index arithmetic; base/count and active-list legitimacy remain open. |
| s939 | `stopVoicesByHandle` has four direct callers in two song-list walks; handle lookup and termination are coherent, but the node `+0xC` to 8-bit voice-index contract and voice-table lifecycle remain unproven. |
| s940 | `D_8013D880`/`0x80141AD0` inventory found compatible 32-slot bounds and `-1` handle clearing across reset/release/stop paths, but did not prove node `+0xC` index provenance or runtime value legitimacy. |
| s941 | Four node `+0xC` insertion/reuse writers all copy voice `+0x64`; list links and sentinels are coherent, but complete `+0x64` provenance and indirect paths remain unclassified. |
| s942 | Classified generated `+0x64` stores by domain; voice paths are sentinel/constructed-handle or `$s1` initialized to `-1`, but indirect provenance and runtime slot legitimacy remain unproven. |
| s943 | Exhaustive source audit found the allocator plus three duplicated sorted-node insertion/reuse writers; no direct allocator call and no proven indirect edge were found, while pointer/value lifecycle remains unclassified. |
| s944 | Four direct `startNoteOnVoice` callers were found; the return is a list handle, while voice `+0x64` is a composite handle with the allocated slot in its low byte. Node `+0xC` and `stopVoicesByHandle` agree structurally; indirect pointer/lifecycle legitimacy remains open. |
| s945 | Three inline node-copy sites derive `0x8013D880 + slot*0x17C` voice records. The standalone allocator copy has no direct generated caller and receives `$a0` without a proven dispatch edge; the structural contract remains single-source and incomplete. |
| s946 | Exhaustive generated-source/overlay/companion search found no direct allocator reference and only the unrelated generic comparator `jalr`; static standalone reachability is selected dead, while runtime pointer/value legitimacy remains unproven. |
| s947 | All remaining funcs_21–23 `+0x64` stores classified as voice-handle sentinels/copy or unrelated fade floats; no mismatch writer or allocator-targeted indirect edge, but runtime legitimacy remains unproven. |
| s948 | Exhaustive `+0x64` read inventory: five voice/sorted-node reads, one unrelated fade float, and one unresolved sound-macro context read; stack spill excluded. No mismatch or mitigation conclusion. |
| s949 | One direct sound-macro caller (`tickAudioChannel`) passes `$s0`; its context `+0x64` feeds the `0x17C`-stride table. Six table writers were found, but channel-field provenance and read-side consumers remain unresolved. |
| s950 | Complete generated audio inventory found eight `-0x276C` table stores, no reads, and only the `soundMacroOpKeyOnNote` store sourced from channel `+0x64`; all generated channel-field writers are `-1` stores. Structure is coherent but lifecycle/legitimacy remains unclassified. |
| s951 | Closed the channel `+0x64` hypothesis thread: no reachable indirect-dispatch edge and fixed-array channel-object origin select H-channel-context-field-sentinel-contract. |
| s952 | Mapped `slotDispatcherIter+872` to `funcs_8.c:22810`, the prologue spill of guest `$sp`/`ctx->r29`; 144 direct callers in 19 files are the next writer/origin class. No guard or mitigation. |
| s953 | Audited all 144 direct callers in 72 generated functions: frame entry/restore is structurally balanced and no non-frame `$sp` writer exists; eight callers retain indirect-call targets as the unresolved shared-context branch. No guard or mitigation. |
| s954 | Audited all indirect targets in the eight callers: 26 statically addressed targets are frame-balanced or leaf functions; the `runInMissionFrame` callback table at `0x8010B350` remains runtime-driven and unresolved. No guard or mitigation. |
| s955 | Retail oracle positive control passed (15.1M whole-RDRAM writes), but VI stayed 320 and callback-table writes were zero; PIF/input checks did not reach the required phase. Callback writer hypotheses remain unclassified. |
| s956 | Named-`start` schedule delivered all 11 presses; positive control passed (15,068,831 whole-RDRAM writes), but 5,399 frames stayed at VI 320 and callback-table writes remained zero. No PIF transition was logged; phase remains unevaluable. |
| s957 | Concurrent undriven/driven controls both passed (10,120,336/10,146,403 whole-RDRAM writes); driven delivered 11 presses, but both stayed at VI 320/origin `0x006dd280` with no PIF trace. Core/setup phase remains selected; callback-table watch is unevaluable. |
| s958 | Config/help audit plus corrected 30-second pair passed whole-RDRAM controls (5,201,480/5,203,031); driven delivered five `sym=40` presses, but both stayed at VI 320/origin `0x006dd280` with no PIF trace. Timeline is ruled out; input-read/core setup remains phase blocker. |
| s959 | Source audit and one driven arm confirmed input-plugin attachment and scancode-40 delivery; whole-RDRAM control passed with 5,189,202 hits. The PIF trace is a VI poll rather than game-read attribution; VI stayed 320, so callback-table reachability remains unevaluable. |
| s960 | Physical PIF read watch crashed the oracle twice before VI, both paired and isolated; whole-RDRAM-only control passed with 1,082,129 hits/287 VI. PIF read activity remains unevaluable; investigate the debugger read-watch path. |
| s961 | Ordinary RDRAM read watch survived with 1,105,122 write-control hits, one read hit, and 299 VI; PIF RAM and PIF ROM read watches both crashed pre-VI. Source mapping selects a PIF-region handler defect over a generic read-watch defect; no retail PIF conclusion. |
| s962 | Core rebuild with `pif_address()` base stripping left ordinary RDRAM healthy (1,105,106 writes/one read/299 VI) but PIF read watch still crashed `rc=139` after RDRAM init and before emulator start. Latent normalization bug recorded; pre-start PIF debugger/init failure remains. |
| s963 | Batched oracle diagnostics showed ordinary RDRAM completing (1,105,162 writes/299 VI), while PIF mapping and activation succeeded and the first wrapped PIF read entered before `rc=139`; immediate failure is in the debugger callback path after read entry. |
| s964 | Callback-boundary markers showed the ordinary arm completing (1,105,307 writes/one read/299 VI), while the PIF arm reached wrapped read entry but produced no pre-lookup marker before `rc=139`; lookup/state/update remain unevaluable and the failure is earlier in the PIF read-with-breakpoint path. |
| s965 | Wrapper before/after markers showed the ordinary arm completing (1,102,500 writes/one read/298 VI), while the PIF arm reached the wrapper pre-callback marker at `0x1fc007e4`, emitted no post-callback marker, and exited `rc=139`; the failure is at callback call/early-entry, not before the wrapper. |

| s966 | First-statement callback marker paired with the wrapper markers: ordinary control completed (1,102,384 writes/298 VI), while PIF reached wrapper pre-call but no callback entry or wrapper return (`rc=139`). ABI/prologue boundary selected; retail remains unevaluable. |

| s968 | Exact source/preprocessed C, fresh LLVM IR, and current object bitcode all contain `(pc,address,4,flags=3)`; linked dylib disassembly alone emits `w2=3` with `w3` unset at `0x13d64`. Link/LTO artifact mismatch selected; stale-product versus link-stage transformation remains open. |
| s969 | Forced the exact oracle rebuild successfully with current Homebrew binutils libraries. Source/object/dylib timestamps were 19:49:20/20:07:30/20:07:33 and fresh object/dylib hashes changed; the new dylib still emits `w0=pc`, `x1=address`, `w2=3`, with no `w3` before `_check_breakpoints_on_mem_access` at `0x13d64`. Stale-product hypothesis is refuted; link-stage/object-to-dylib transformation remains selected. |
| s971 | Fresh non-LTO ARM64 assembly emits `w2=4,w3=3` at both callback sites, while the current LTO dylib emits `w2=3` with `w3` unset. This selects the LTO transformation boundary; the source/ABI hypothesis is refuted for non-LTO codegen and no runtime or retail conclusion follows. |
| s972 | Fresh non-LTO linked dylib emits `w2=4,w3=3` at both callback sites after using the environment-preserved binutils path. This independently selects LTO over source, non-LTO codegen, and non-LTO link; no runtime or retail conclusion follows. |
| s973 | Isolated all-non-LTO and mixed dylibs both emit `w2=4,w3=3` at both callback sites; the reproducible mixed arm rules out a generic link interaction between the two callback objects and selects single-object LTO treatment or their all-LTO interaction. |
| s974 | From a fresh all-LTO baseline, non-LTO `memory.o` plus LTO `dbg_breakpoints.o` remains bad, while LTO `memory.o` plus non-LTO `dbg_breakpoints.o` is correct at both callback sites. This selects the `dbg_breakpoints.c` LTO transformation boundary; no runtime or retail conclusion follows. |
| s975 | LTO `dbg_breakpoints.o` IR still defines a four-argument callback, while non-LTO object code saves `x3` and the all-LTO linked dylib omits `x3` and substitutes constant `4` in the first callback diagnostic. The non-LTO dylib preserves `w2=4,w3=3`. This selects LTO lowering of `dbg_breakpoints.c` at link time; no runtime or retail conclusion follows. |

All runtime claims in the ledger had positive controls in the relevant
capture. Static single-source results are labelled as such in the session
entries and do not authorize mitigations.

## Ranked backlog

1. The `tickAudioChannel`/`stopVoicesByHandle` M3 class (s938–s951) is
   CLOSED — see s951. The recurring `slotDispatcherIter+872` terminal SIGBUS
   is now localized to the generated prologue spill at `funcs_8.c:22810`.
   Audit all 144 direct callers for guest `$sp`/`ctx->r29` provenance and
   caller-frame balance before considering any runtime change; do not guard
   the dispatcher prologue. s953 found no non-frame `$sp` writer in the 72
   direct callers; audit the eight callers containing `LOOKUP_FUNC`/`jalr`
   targets for context mutation before closing the class.
2. Do not use the process-wide `0x8000834c` breadcrumb to select a crash site;
   require an independently phase-gated caller/state boundary.
3. Isolate the remaining oracle PIF-region crash before retrying the
   callback-table watch: s975 shows correct LTO IR but an incorrect all-LTO
   callback entry. Capture the linker's generated LTO object and inspect its
   callback prologue/call shape to identify the lowering stage; do not infer
   retail behavior or change the runtime yet.
4. M4 correctness: outdoor `baseFixed=-32768` zero shade, attribution S=0
   triangles, then I4 `sample=64x128`, each with independent controls.
5. Retain the regeneration delete-before-regen rule and audit fixup counts if
   a reproducible omission appears.

## Next work unit

HYPOTHESIS-ID: oracle-pif-breakpoints-lto

Run one bounded oracle rebuild with the all-LTO recipe, preserving the
linker-generated LTO object with `-Wl,-object_path_lto,/tmp/s976-lto.o`.
Inspect that object and the resulting dylib with `file`, `nm`, and
`otool -tvV`; compare the callback entry and both wrapper call sites against
the s975 non-LTO control. Do not edit the recomp runtime or retry retail
PIF/callback hypotheses.

Competing hypotheses:

- H-pif-breakpoints-lto-lowering: the generated LTO object already drops
  `x3`/changes the callback argument shape, selecting LTO lowering/backend
  code generation.
- H-pif-breakpoints-final-link: the generated LTO object is correct but the
  final dylib changes the shape, selecting final-link handling.
- H-pif-breakpoints-recipe: preserving the generated object is unsupported or
  unreproducible, selecting recipe/toolchain state.

Discriminating measurement: whether `/tmp/s976-lto.o` has the same callback
entry/call shape as the bad all-LTO dylib. Bad generated object selects LTO
lowering; correct generated object plus bad dylib selects final-link handling;
failure to preserve/reproduce it selects recipe/toolchain state.

Exact commands:

`cd /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-alllto/projects/unix && make clean && make LDFLAGS="-Wl,-object_path_lto,/tmp/s976-lto.o"`

`file /tmp/s976-lto.o && nm -m /tmp/s976-lto.o && otool -tvV /tmp/s976-lto.o | rg -n -A 45 "check_breakpoints_on_mem_access|read_with_bp_checks"`

`otool -tvV /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-alllto/projects/unix/libmupen64plus.dylib | rg -n -A 45 "_check_breakpoints_on_mem_access:|_read_with_bp_checks:"`

## Closed and parked

- M5 audio (legacy campaign) is CLOSED; see `docs/M5-AUDIO-PLAN.md` and
  PROJECT-OVERVIEW §§9–12.
- Hangar-exit to sec2 is CLOSED except for the active accounting/backlog work;
  see PROJECT-OVERVIEW §27–28.
- Earlier idiom campaigns, duplicate-symbol work, missing-function inventory,
  old ucode/DMA experiments, and rendering dead ends are archived in
  PROJECT-OVERVIEW §§13–26.
- Parked items include intermittent regeneration omission, isolated
  animation/frameStart SIGBUS reports, the M3 DoD gate, and M4 band-row
  coverage.

## Ground truth and method rules

- Before runtime instrumentation, consult `tools/oracle/README.md` and
  `docs/F5-UCODE-REFERENCE.md`; arm a positive whole-RDRAM control first.
- Gate animating comparisons on `PROBE_PHASE_WIDTH` and
  `PROBE_KEYS_FROM_PHASE=1`; scope counters and budgets to the phase.
- Batch instrumentation into one build/run. Require two independent evidence
  lines before promoting a conclusion.
- Launch from `build/` with the ROM present, use SIGKILL, and use capture paths
  whose final component does not begin with `.`. Queue repeat soaks.
- Generated diagnostics belong in fixup scripts. Regeneration order is
  `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then CMake.

## Build and patch cautions

Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
`git reset --hard`. If editing under `lib/`, export patches with
`./submodule-patches/export.sh`. Ignore the benign `wmain/main` warning;
prefix environment-led commands with `env`; do not hand-edit generated game
logic; use `patches/` overrides. No emojis in code or documentation.
