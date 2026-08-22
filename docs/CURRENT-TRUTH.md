# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger remains
authoritative for exact commands and probe rows. Maintained in Session 2175
(2026-08-22); behavioral and source evidence is current through s2175.

This file is intentionally compact. Archives: s2080–s2108 in
`PROJECT-OVERVIEW.md` §40; s2110–s2163 in §§41–42. s2164–s2175 live here
until the next archive pass.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu overlay explanation is closed.
- The qualified route reaches title VI `1024 @ 0x00790400` and hangar VI
  `512 @ 0x006AB400` with `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield remains
  environment-gated and default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation must name its writer, state
  whether the value is legitimate, and include an `ORIGIN:` line.
- [`docs/M5-AUDIO-PLAN.md`](M5-AUDIO-PLAN.md) controls incremental audio
  work. The default audio path is a silent `Broke` stub. The Factor 5
  image arm is opt-in through `ROGUESQ_AUDIO_UCODE=1` and is not defaulted
  on. s2162 selected `H-UnsignedMemBu`
  (`scratch/s73_post_a_scene/s2162_s32_membu_ab.txt`): replacing the
  unsigned PATCH `MEM_BU(0X1AD0, 0X80140000)` with
  `MEM_BU(0X1AD0, S32(0X8014 << 16))` lets same-build `=1` return from
  `waitForAnyAudioSlot` (`c=0x11`/`0x10`) and reach title
  `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`. Stub `=0` still
  matches that route. The s2160 `waitForAnyAudioSlot+1060` SIGSEGV is
  closed on the current binary. s2163 executed the default-on retry
  (`scratch/s73_post_a_scene/s2163_default_on_ab.txt`) and selected
  `H-CinematicRegress`: unset matched `=1` at dispatch/wait
  (`real_ucode=1`, wait return `c=0x11`) but 0/3 unset and 0/2 `=1`
  reached title (SIGBUS at `slotDispatcherIter+3092` /
  `cutsceneDispatchSlotsByFlag+8960`, or a 600s 640 stall);
  same-build `=0` retry reached title+hangar. Polarity reverted.
- The image arm performs real DMEM work and generated DMA writes, then
  returns `Broke`. The s2113 contract witness records guest PC `0x1328`,
  host exit `Broke`, task `output_buff=0`, and phase-keyed post-DMA/PCM
  joins. s2154 selected `H-CanaryComputedOnly`: host canary
  `0xF80..0xF8F` sits inside mix buffer `0xE50..0xFCF`, so `canary_ok=0`
  is that working set, not a runaway write. s2155 selected
  `H-CanaryOnlyInUcodeData`: certain/bounded write union is
  `0x220..0xA3F` plus `0xC30..0xFCF`; mix occupies `0xE50..0xFCF`
  continuously; the only unused `>=0x10` holes in `0x000..0xFBF` sit
  inside ucode-data (`0x000..0x21F`, `0xA40..0xC2F`). A relocated host
  canary has nowhere to live in DMEM. s2157 selected `H-CanaryLogOnly`:
  every `canary_ok` assignment and read in `rsp.cpp` is storage or a
  fprintf/probe field; `run_task` computes `exit_reason` before the
  post-hash and completes on `Broke` alone; DMA recording ignores the
  flag. `canary_ok=0` does not gate host completion, writeback, or DMA.
  s2158 selected `H-IsolatedOnlyByEnv`: the only control-flow isolator
  that keeps `factor5_ucode_b` opt-in is `get_rsp_microcode`'s
  `ROGUESQ_AUDIO_UCODE` branch returning `&factor5_ucode_b_probe` versus
  `&musyx_stub_probe`. `run_task` always calls that pointer and completes
  on `Broke`; its second getenv is a probe-gated log label / optional
  canary-prefill skip, not an early return, skipped writeback, or forced
  `Broke`. The env-true wrapper calls `factor5_ucode_b`, not
  `musyx_stub`. s2159 selected `H-PolicyOnly`: every named host-contract
  reason to keep the arm opt-in was already closed by a selected
  hypothesis; remaining isolation was the env default plus historical
  comments (`scratch/agent/s2159_image_arm_default_blockers.txt`).
  s2160 then executed that default-on flip and selected
  `H-RouteRegress` (`scratch/agent/s2160_default_on_ab.txt`). s2161
  selected `H-RetailLoadsCount` and named the guest ORIGIN
  (`scratch/agent/s2161_wait_slot_oracle.txt`): retail writes
  `D_80141AD0` from `setDisplayMode` `0x8008EA44` and
  `reapplyDisplayMode` `0x8008EB8C` (clamped config+0x20), then
  `waitForAnyAudioSlot` jals `anyAudioSlotActive` which loads it.
  The port SIGSEGV at `waitForAnyAudioSlot+1060` was the s2045 loop
  PATCH `MEM_BU(0X1AD0, 0X80140000)` using an unsigned KSEG0
  constant (host `rdram+4GB+0x141AD3`), not original MIPS; the
  crashing image path is `anyAudioSlotActive` `path=gate0`, which
  does not load the byte. s2162 `S32`-addressed those PATCH sites
  and the image arm now returns from wait. s2163 selected
  `H-CinematicRegress` for the post-wait 0x00696100 cinematic
  window and reverted default-on. s2164 selected `H-NoSuchSite`
  (`scratch/s73_post_a_scene/s2164_unsigned_kseg0_census.txt`):
  neither SIGBUS function contains an unsigned KSEG0 `MEM_*`
  constant. The crash sites are register-base guest loads
  (`0x8003E944` `lbu 0x1A($s1)`, `0x800A87A8` `lwc1 0x44($v0)`).
  s2165 selected `H-RetailExecsValidPtr`
  (`scratch/s73_post_a_scene/s2165_cinematic_pc_oracle.txt`):
  Rice 45s, same-log whole-RDRAM 10000, `[gpr-ctl]`, VI 640
  including origin `0x00696100`. All four PCs execute (148586
  exec hits). Logged crash-site `$s1`/`$v0` are KSEG0 RDRAM,
  not 0. s2166 selected `H-RetailWriterNamed`
  (`scratch/s73_post_a_scene/s2166_cutscene_a2_50_writer.txt`):
  watch 1 on phys `0xC7B0C` (`$a2+0x50` for first slot
  `0x800C7ABC`) took 5 writes. Writer histogram:
  `rs_memset` `0x800078EC` `sb` n=4 and
  `spawnCutsceneObjectsFromList` `0x800A8144`
  `sw $v0, 0x50($v1)` n=1 after `jal walkMeshdef0List`.
  Same-run `$a2` at `0x800A879C` stays in
  `0x800C7ABC..0x800CA5F0` including the sampled slot;
  loaded word at `0x800A87A0` is heap `0x8025A580`.
  s2167 selected `H-PortStoreMatchesRetail`
  (`scratch/agent/s2167_port_store_ab.txt`): same-build
  `=1`/`=0` both store and reload heap `0x8025A580` at
  dest `0x800C7B0C` (0 mismatches). `=1` still SIGBUS later
  (`matchKeywordWithPriority+88`, `si_addr=0x380000030`).
  s2168 selected `H-RetailValidV0`
  (`scratch/s73_post_a_scene/s2168_match_keyword_oracle.txt`):
  Rice 45s, same-log whole-RDRAM 10000, `[gpr-ctl]`, VI 640
  including origin `0x00696100`. Lifetime exec at
  `0x800AF2C8`/`CC`/`D0` n=264 each, caller always
  `spawnCutsceneEffectsAndCues` `0x800A9248`. Logged
  `0x800AF2CC` `$v0` is heap-object `0x800CDB58` (KSEG0
  RDRAM, not 0, not `0x80000000`) 21/21; `$a0` is heap
  `0x802231EC`. Retail takes a legitimate `0x30($v0)`.
  s2169 selected `H-PortMatchesRetailUntilLater`
  (`scratch/agent/s2169_match_kw_ab.txt`): same-build
  `=1`/`=0` both load retail-class `$a0=0x802231EC` /
  `$v0=0x800CDB58` at `matchKeywordWithPriority`; always-log
  of `$v0==0`/`0x80000000` never fired. Image last logged
  n=150 at t=21.3 then 640-stalled; stub continued to n=250
  and reached title+hangar. s2170 selected `H-NoHangAtN150`
  (`scratch/agent/s2170_match_kw_flow_ab.txt`): flow-ctl at
  640/`0x00696100` on both arms; image `matchEntry` n=150
  and n=151 at t=20.7 (n=150 returned) then n=264 at t=36.0;
  `effectsEntry==effectsRet` through n=820; both arms title
  `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`. The
  s2169 missing n=200 was every-50 rate-limit, not a hang
  inside the callee. s2171 selected `H-NullV0At87A8`
  (`scratch/agent/s2171_image_cinematic_flow.txt`) on the
  queued failing `=1` soak: flow-ctl n=40 at
  640/`0x00696100`; `effectsEntry==effectsRet` n=338;
  `matchEntry` n=168 returned (effectsRet n=328 same t,
  then effects n=329–338); SIGBUS t=28.2
  `cutsceneDispatchSlotsByFlag+9072` `si_addr=0x380000044`
  `x2=0` `x1=0x800a87a8` after load879c n=5393
  `+0x50=0x8025A580`. The four hang hyps are now refuted
  on a failing run, not only s2170's completing run.
  `H-CinematicRegress` remains (s2163 0/5 title, s2167
  matchKeyword SIGBUS, s2169 stall, s2171 87A8 SIGBUS vs
  s2162/s2170 title+hangar). s2172 selected
  `H-RetailHeap0NeverZero`
  (`scratch/agent/s2172_heap0_writer.txt`): Rice 45s watch
  1 on phys `0x25A580` took 5 writes. Writer histogram:
  `zmemcpy` `0x80018F5C` `sd` n=4 and
  `walkMeshdef0List` `0x80057100` `sw $v0, 0($s7)` n=1
  after `rs_malloc`, `$v0` from `hobObjectListItems`+4.
  Same-run 87A8 `$v0` 32/32 KSEG0 (first-slot word0
  `0x800CA748`); 87A0 first-slot `$v0=0x8025A580`;
  snapshot nonzero=4; 0 logged zero stores. s2173
  selected `H-PortHeap0MatchesRetail`
  (`scratch/agent/s2173_heap0_store_ab.txt`): same-build
  `=1`/`=0` both store dest `0x8025A580` value
  `0x800CA748` at `0x80057100` and `0x800A87A0` reloads
  it (933/933 and 317/317, mismatch=0, zero=0). Completing
  `=1` reached title+hangar with lwc zero_logged=0. s2174
  selected `H-StallWord0Intact`
  (`scratch/agent/s2174_heap0_fail.txt`): queued failing
  `=1` soak is a 640-stall (0 SIGBUS) with dest
  `0x8025A580` still `0x800CA748` 366/366, lwc
  zero_logged=0; guest cinematic probes stop at t=28.4
  after last first-slot 87A0 while VI continues to
  `#10752`. s2175 selected
  `H-CompletePathDispatchReturned`
  (`scratch/agent/s2175_hang_after_87a0.txt`) on a
  completing `=1` run: last first-slot 87A0 n=14305
  t=48.4 dest `0x8025A580` value `0x800CA748` is
  followed by lwc87a8 n=14305 dest `0x800CA748`,
  xformEntry/Ret n=14305, and dispatchRet n=895, then
  title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`. dispatchEntry ctl n=8 at
  640/`0x00696100`. Hang hyps remain for a failing
  soak. Do not S32-address by guess, NULL-skip,
  re-flip default-on, skip/allow `matchKeywordWithPriority`
  or the lwc or transform, add a wait/slot guard, or change
  `osAiGetStatus_recomp` / `osAiSetNextBuffer_recomp`.

### Selected hypotheses (scoped; do not widen)

| Id | Selected | Scope / two-source note | Forbidden follow-on |
|---|---|---|---|
| s2135 | `H-ExistingFactor5ConfigMatches` | companion `aspMainText` is `factor5b_rsp.toml` ROM `0x09ABE0..0x09BB60`; `speech` is uncompressed MORT `0x583D90..0x8A1174` (546 descriptors, CPU voice path) | new MORT RSP segment |
| s2136 | `H-RetailTaskMatchesFactor5b` | retail `ucode=0x80099FE0`, `ucode_data=0x800A4E00`, nonzero `data_ptr`/`data_size`, zero `output_buff` writes | task-field rewrite |
| s2137 | `H-PortTaskFieldsMatchRetail` | same-build stub/image; image `field348+0x100` dest; hangar stage-2 PCM joins `nz=621`/`639` | output-route change |
| s2140 | `H-RetailDataPtrOffset100` | independent retail writes at both exact `data_ptr+0x100` dests; writer PC `0x80090CA4` | output-route change |
| s2113/s2118 | `H-TaskExitMapping` | legitimate generated `break 0` / `Broke` at `0x1328` | treat `output_buff=0` as a failed route |
| s2105/s2118 | `H-ImageDestIsPCM` | sampled hangar stage-2 `0x6F0`/`0x300` DMA/PCM joins | task-ABI rewrite |
| s2132 | `H-RetailAIQueued` | retail `osAiSetNextBuffer` live through hangar (`8,556` in s2132) | port PCM proof |
| s2133 | `H-PortAIQueueMatches` | image PCM source/consumer joins; stub zero; `[pcm-sanity]` lifetime sampler missed transients | `osAiGetStatus` change |
| s2152 | `H-BusyIsThePoll` | named `osAiGetStatus`/`osAiGetLength` absent; only poll is `__osAiDeviceBusy` inside `osAiSetNextBuffer` (1:1) | change `osAiGetStatus_recomp` |
| s2153 | `H-BusyAlwaysClear` | reject PC `0x80029EF0` = 0; success `0x80029EF4` = set-next = busy; generated caller ignores v0 | change `osAiSetNextBuffer_recomp` |
| s2134 | `H-RetailMORTDecoderLive` | seven named decode/filter PCs plus `musyxSynthFrame` and `osAiSetNextBuffer` | default-arm change |
| s2138–s2151 | `H-MORTRemainingMatches` | all six descriptor types and both rates have complete nonempty rows; type 4 is 16000-only | host shortcut / remaining-class recensus |
| s2120 | `H-C88-ReversedOrSuppressing` | named writer `0x8008EC88`; gate 1 suppresses nonzero image/PCM | blanket gate flip |
| s2111/s2112 | `H-RecipeVariance` / `H-RecipeTiming` | B40 read/branch table identical at 0; phase-7 caller/entry/route rows matched | B40 read-site recensus |
| s2121 | `H-KeyOnRetailDead` | **single-source** retail: eight `musyxKeyOnVoice` PCs zero | port-dead claim or guard removal |
| s2122 | `H-PortKeyOnNormal` | hangar phase 10: normal tail, divisor `0xC0`, no guard fire | guard removal |
| s2123 | `H-RetailWaitContract` | countdown seed/decrement, worker/status, named waits/service/shutdown live | wait/guard change |
| s2125 | `H-PumpIrrelevant` | pump-on/off same title/hangar wait/drain sequence; stall/guard silent | pump/wait/task change |
| s2128 | `H-CoverageFailure` | A10 parked: third drain-tick pair missed both-arm target coverage | repeat the same drain recipe |
| s2154 | `H-CanaryComputedOnly` | mix `0xE50` span `0x180` writes host `0xF80`; no immediate in `0xF80..0xFBF` | canary-prefill / exit-mapping change |
| s2155 | `H-CanaryOnlyInUcodeData` | no unused `>=0x10` hole in `0x000..0xFBF` outside ucode-data | relocate the host canary |
| s2157 | `H-CanaryLogOnly` | host-source: every `canary_ok` site in `rsp.cpp` is storage or fprintf; `run_task` completes on `Broke` alone | default-arm / canary-prefill change |
| s2158 | `H-IsolatedOnlyByEnv` | host-source: live `RspUcodeFunc*` assigned only in `get_rsp_microcode` from `ROGUESQ_AUDIO_UCODE`; `run_task` calls that pointer; env-true path never reaches `musyx_stub` | default-arm / canary-prefill change |
| s2159 | `H-PolicyOnly` | host-source: every named keep-opt-in sentence in CURRENT-TRUTH, M5 A1, and the `get_rsp_microcode` hang comment is closed-by-selected-hypothesis or policy-comment; both required positive-control rows present | flip from the census table; canary / AI-status change |
| s2160 | `H-RouteRegress` | pre-S32 binary: unset/`=1` SIGSEGV at `waitForAnyAudioSlot+1060` before title; `=0` title+hangar stub contract; not `waitForMusyXAudioTaskDone` | treat pre-fix SIGSEGV as still live; canary / AI-status / wait-slot guard |
| s2161 | `H-RetailLoadsCount` | retail wait exec 1 from `0x800C5CF4`; jal `anyAudioSlotActive` loads `0x141AD0` at `0x8008E5C0`; writers `setDisplayMode`/`reapplyDisplayMode`; port +1060 is unsigned PATCH `MEM_BU` (`si_addr` = `rdram+4GB+0x141AD3`) | wait/slot guard; leave unsigned `MEM_BU(0X1AD0, 0X80140000)` |
| s2162 | `H-UnsignedMemBu` | same-build `=1` wait entry/loop/return `c=0x11`/`0x10`, title+hangar, `break_pc=0x1328`; `=0` stub title+hangar; 0 SIGSEGV | wait/slot guard; treat post-hangar `0x80001b08` SIGABRT as the wait-slot defect |
| s2163 | `H-CinematicRegress` | dispatch/wait: unset=`=1` `real_ucode=1` wait return `c=0x11`; title: unset 0/3 and `=1` 0/2 (SIGBUS `slotDispatcherIter+3092`/`cutsceneDispatchSlotsByFlag+8960` or 640 stall); stub retry title+hangar; polarity reverted | wait/slot guard; default-on flip; treat cinematic SIGBUS as the wait-slot defect |
| s2164 | `H-NoSuchSite` | both `RECOMP_FUNC` defs present; `slotDispatcherIter` 47 `MEM_*` (1 already-S32 PATCH, 46 register/stack) and `cutsceneDispatchSlotsByFlag` 146 `MEM_*` (all register/stack); unsigned-KSEG0-constant count 0; atos `+3092`/`+8960` are `MEM_BU(ctx->r17, 0X1A)` / `MEM_W(ctx->r2, 0X44)` | S32-address by guess; default-on flip; wait/slot guard |
| s2165 | `H-RetailExecsValidPtr` | Rice 45s: `[gpr-ctl]` + watch0 10000 + VI 640 `0x0066a500` then `0x00696100`; exec `0x8003E944` n=54246 `$s1` KSEG0 3/3 logged (`0x80208df4`/`0x80208db8`); `0x800A87A8` n=14256 `$v0` KSEG0 22/22 logged (`0x800ca748`..); producers `0x8003E938`/`0x800A87A0` also KSEG0 `$v0` | NULL skip; S32-address; default-on flip; wait/slot guard |
| s2166 | `H-RetailWriterNamed` | Rice 45s: watch 1 phys `0xC7B0C` 5 writes; `rs_memset` `0x800078EC` n=4; `spawnCutsceneObjectsFromList` `0x800A8144` `sw $v0, 0x50($v1)` n=1 after `walkMeshdef0List`; `$a2` at `0x800A879C` in `0x800C7ABC..0x800CA5F0` including sampled slot; load word heap `0x8025A580`; snapshot nonzero=4 | NULL skip; S32-address; default-on flip; wait/slot guard |
| s2167 | `H-PortStoreMatchesRetail` | same-build `=1`/`=0`: ctl n=2 at 640 `0x00696100`; store8144 n=16 all KSEG0; dest `0x800C7B0C` value `0x8025A580`; load of that dest all `0x8025A580` mismatch=0; store80d4 n=0; lwc `$v0` in `{0x800CA748,0x800CAE88,0x800CDB58,0x800CE028,0x800CF158}`; `=1` SIGBUS `matchKeywordWithPriority+88` never title; `=0` title+hangar | NULL skip; S32-address; default-on flip; wait/slot guard; skip/allow the +0x50 load |
| s2168 | `H-RetailValidV0` | Rice 45s: `[gpr-ctl]` + watch0 10000 + VI 640 `0x00696100`; exec `0x800AF2C8`/`CC`/`D0` n=264 each, prev `0x800A9248`; logged CC `$v0=0x800CDB58` 21/21 KSEG0 not base; `$a0=0x802231EC` 22/22; 0 wild | NULL skip; S32-address; default-on flip; wait/slot guard; skip/allow `matchKeywordWithPriority` |
| s2169 | `H-PortMatchesRetailUntilLater` | same-build `=1`/`=0`: ctl at 640 `0x00696100`; callee `$a0=0x802231EC` `$v0=0x800CDB58` dominant; wild=0; image last logged n=150 t=21.3 then 640-stall; stub n=250 title+hangar | NULL skip; S32-address; default-on flip; wait/slot guard; skip/allow `matchKeywordWithPriority`; treat last n=150 as hang-inside |
| s2170 | `H-NoHangAtN150` | same-build: `[match-kw-flow-ctl]` at 640 `0x00696100`; image `matchEntry` n=150 and n=151 at t=20.7 then n=264 t=36.0; `effectsEntry==effectsRet` n=820; both arms title+hangar; 0 SIGBUS | NULL skip; S32-address; default-on flip; wait/slot guard; skip/allow `matchKeywordWithPriority`; treat s2169 missing n=200 as hang-inside |
| s2171 | `H-NullV0At87A8` | failing `=1` soak: flow-ctl n=40 at 640 `0x00696100`; `effectsEntry==effectsRet` n=338; `matchEntry` n=168 returned then effects n=329–338; SIGBUS t=28.2 `+9072` `si_addr=0x380000044` `x2=0` `x1=0x800a87a8`; last load879c `+0x50=0x8025A580`; lwc probe is before `MEM_W` and every-50 so did not print `$v0=0` | hang-inside / caller-stops / effects-hang; NULL skip; S32-address; default-on flip; wait/slot guard; skip/allow `matchKeywordWithPriority` or the lwc; treat heap+0 as selected ORIGIN |
| s2172 | `H-RetailHeap0NeverZero` | Rice 45s: `[gpr-ctl]` + watch0 10000 + VI 640 `0x00696100`; watch 1 phys `0x25A580` 5 writes; `zmemcpy` `0x80018F5C` `sd` n=4; `walkMeshdef0List` `0x80057100` `sw $v0, 0($s7)` n=1 after `rs_malloc`; `$v0` from `hobObjectListItems`+4 (`0x80139020`); exec 87A0/87A8 n=14160; logged 87A8 `$v0` 32/32 KSEG0 `{0x800CA748,0x800CAE88,0x800CDB58,0x800CE028,0x800CF158}` zero=0; first-slot 87A0 `$v0=0x8025A580` `$a2=0x800C7ABC`; snapshot nonzero=4 | NULL skip; S32-address; default-on flip; wait/slot guard; skip/allow the lwc; treat retail word0 as 0 |
| s2173 | `H-PortHeap0MatchesRetail` | same-build `=1`/`=0`: ctl at 640 `0x00696100`; store57100 dest `0x8025A580` value `0x800CA748` n=1 both arms; load87a0 of that dest `=1` 933/933 and `=0` 317/317 value `0x800CA748` mismatch=0 zero=0; lwc zero_logged=0; `=1` title+hangar; `=0` still cinematic at 90s concurrent cap | NULL skip; S32-address; default-on flip; wait/slot guard; skip/allow the lwc; treat constructor as missing |
| s2174 | `H-StallWord0Intact` | failing `=1` soak: ctl at 640 `0x00696100`; store57100 dest `0x8025A580` value `0x800CA748`; load87a0 of that dest 366/366 `0x800CA748` zero=0 mismatch=0; lwc zero_logged=0; last 87A0 n=5825 t=28.4; 0 SIGBUS; 0 VI 1024; last `[vi]` #10752 640 `0x0062BD00`; effectsEntry==effectsRet n=365 | NULL skip; S32-address; default-on flip; wait/slot guard; skip/allow the lwc; treat 640-stall as first-slot word0=0 |
| s2175 | `H-CompletePathDispatchReturned` | completing `=1`: ctl n=23 at 640 `0x00696100` including dispatchEntry n=8; store57100 dest `0x8025A580` value `0x800CA748`; last first-slot 87A0 n=14305 t=48.4 then lwc87a8 n=14305 dest `0x800CA748`, xformEntry/Ret n=14305, dispatchRet n=895 = dispatchEntry nmax; title+hangar; lwc zero_logged=0. Hang hyps not selected (wrong run class) | NULL skip; S32-address; default-on flip; wait/slot guard; skip/allow the lwc or transform; treat hangar `0x80001b08` SIGSEGV as the cinematic hang |

Coverage-only pairs that selected no ABI hypothesis: s2114–s2117, s2124,
s2126–s2128, and the first s2120 pair. Absent target rows are coverage
failure, not evidence for a destination, writeback, or output-validity
claim.

Generated-symbol close-out: s2129–s2147 confirmed the mission-overlay
mappings at `0x800AD380`, `0x800AE3F0`, `0x800C41B0`, `0x800BF790`,
`0x800C64B0`, `0x800E71D0`, `0x800EC110`, `0x800EC6F0`, `0x800ED150`,
and `0x800FEF10`. s2148–s2149 confirmed menu mappings
`0x800B2630`/`buildFormatMessageGlyphBuffer` and
`0x800B3824`/`buildLevelSelectTextTextures` and closed the two-line
overlay-move class. s2150 selected `H-LeftoverAllHolds` for leftover
`fake_func_*` with ELF size `> 0xC` (table
`scratch/agent/s2150_leftover_table.txt`). Remaining generated `func_*`
placeholders are five parked or intentional holds: `func_8000040C`,
`func_800927B0`, `func_80092A54`, `func_80092CF0`, `func_800E9AE0`. Do
not re-census leftover `fake_func_*` or invent names for parked inner
kernels. Prior live-crash warnings remain runtime-risk records, not
static-boundary conflicts.

## Active backlog

The backlog is one monotonic sequence. Closed investigations are not
active work items.

1. **M5 A1 cinematic window (blocks default-on).** s2163 selected
   `H-CinematicRegress` and reverted the default-on flip. s2164
   selected `H-NoSuchSite`. s2165 selected `H-RetailExecsValidPtr`.
   s2166 selected `H-RetailWriterNamed`. s2167 selected
   `H-PortStoreMatchesRetail`. s2168 selected `H-RetailValidV0`.
   s2169 selected `H-PortMatchesRetailUntilLater`. s2170 selected
   `H-NoHangAtN150`. s2171 selected `H-NullV0At87A8` on a failing
   `=1` soak: SIGBUS is `cutsceneDispatchSlotsByFlag`
   `0x800A87A8` `lwc1 0x44($v0)` with `$v0=0` after a good
   first-slot `+0x50=0x8025A580`. s2172 selected
   `H-RetailHeap0NeverZero`. s2173 selected
   `H-PortHeap0MatchesRetail`
   (`scratch/agent/s2173_heap0_store_ab.txt`): port
   `0x80057100` stores `0x800CA748` at dest `0x8025A580`
   and `0x800A87A0` reloads it on both arms; completing
   `=1` reached title+hangar with lwc zero_logged=0.
   s2174 selected `H-StallWord0Intact`
   (`scratch/agent/s2174_heap0_fail.txt`): the queued
   failing `=1` soak is a 640-stall with first-slot word0
   still `0x800CA748` 366/366 and lwc zero_logged=0;
   cinematic probes stop at t=28.4 after last first-slot
   87A0. s2175 selected
   `H-CompletePathDispatchReturned`
   (`scratch/agent/s2175_hang_after_87a0.txt`) on a
   completing `=1` run: last first-slot 87A0 is followed
   by 87A8 dest `0x800CA748`, transform entry+return, and
   dispatch return, then title+hangar. Hang location on a
   failing cinematic (87A8 / transform / dispatch return)
   is still open; soak `s2175_image_hang` is queued.
   Failure modes remain intermittent (`=1` title+hangar
   in s2162/s2170/s2173/s2175; matchKeyword SIGBUS in
   s2167; 640-stall in s2169/s2174; 87A8 SIGBUS in
   s2163/s2171). Do not S32-address, NULL-skip, re-flip
   default-on, skip/allow the function, the lwc, or
   transform, or add a wait/slot guard.
2. **M5 drain in-loop tick A/B — parked.** The s2125 phase-repaired pump
   pair selected `H-PumpIrrelevant` only at route scope. s2126–s2128 all
   supplied positive controls but failed to put both drain arms in the
   target comparison; do not repeat the same recipe. Resume only with a
   genuinely new renderer-recovery or ground-truth discriminator.
3. **M3 crash work.** Only systematic idiom-class audits with a named
   discriminator. The dormant `slotDispatcherIter+872` class has 7659
   clean hangar calls in its guarded run; no mitigation is authorized.
4. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
   attestation and consumer-mode H1 by the RT64 census. H3 is unavailable
   because the oracle cannot screenshot the LLE path. Do not repeat the
   `0xD60` scan.
5. **Generated-symbol renaming sweep — leftover class closed.** s2149
   closed the two-line overlay-move class. s2150 selected
   `H-LeftoverAllHolds` for leftover `fake_func_*` with ELF size `> 0xC`.
   Remaining generated `func_*` names are the five holds above. Do not
   re-census leftover `fake_func_*` or invent names for the parked inner
   kernels.

## Durable boundaries

### Route and rendering

Factor 5 custom opcode mappings and independent-ground-truth requirements
are in [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). The runtime cannot
be its own witness for a null result.

Forced LLE is the route gate under the common wrapper. The accepted
four-arm table selected `LLE_UNGATED=1, LLE_SOLO=1`: `11` reaches title
and hangar, `01` reaches title only, and `10`/`00` reach neither. This
is recipe-level port evidence, not an explanation of the audio callback
or PCM boundary. Menu spin yield is a diagnostic route aid, not a default
behavior change.

Route history is in `PROJECT-OVERVIEW.md` §§36–42. s2093–s2096 closed
the wrapper, task-thread, SP external-delivery, and guest-receive route
at the qualified recipe scope. s2111 superseded B40 as a route-admission
cause at that recipe; s2112 selected recipe timing for the unreproduced
phase-7 origin split. Do not reopen the SP queue or B40 read-site census.

### M5 status, service, wait, and AI

The generated tree reaches both target phases. Direct service entry/exit
and the service gate/loop are live. The port observes the legitimate
slot-0 sequence through the service store at `0x8009B7EC`, guest address
`0x80154620`, including `0x03 -> 0x00`. Retail independently observes the
same status-table cycle. It does not execute the port crash labels
`0x8000B650`/`0x80095D54`; that is a PC-scope boundary, not permission
to change the port wait or guard behavior.

s2122 is a normal-path hangar key-on contract at sampled scope: the
generated function enters, performs four valid `0xC0` divides, and
reaches its normal tail with no early-return guard hit. s2123
independently establishes that the completion-wait contract is live on
the qualified retail route. s2125 closed the pump's sampled
route-admission question (`H-PumpIrrelevant`) without changing the pump,
wait, task ABI, or guards. A10 (drain in-loop tick) is parked after three
coverage-only pairs.

s2132–s2133 plus s2152–s2153 close the sampled AI-status/queue boundary:
retail queues through `osAiSetNextBuffer`; the only status poll is
in-function `__osAiDeviceBusy`; on the covered title/hangar route that
busy check never returns FIFO-full; the generated caller ignores v0.
Always-queue return-0 is observationally equivalent here. Host SDL
fullness is not the N64 AI FIFO. Do not change `osAiGetStatus_recomp` or
`osAiSetNextBuffer_recomp`.

s2135–s2140 close the sampled RSP-image/task/output edge:
`factor5b_rsp.toml` is the retail audio image, MORT speech is a separate
CPU asset, task fields match, and both retail and port write
`data_ptr+0x100`. s2138/s2139/s2151 close the MORT remaining-class
reference decode. None of those results default the image arm or rewrite
task fields.

s2154–s2155 close the host-canary *location* question: `canary_ok=0` is
the generated mix buffer. s2157 closes the host-canary *effect* question:
`canary_ok` is a probe field only and does not gate `RspExitReason`,
`run_task` completion, DMEM-to-RDRAM writeback, or DMA recording. s2158
closes the remaining isolator question: isolation is the env dispatch in
`get_rsp_microcode` only. s2159 closes the remaining named-blocker
question: `H-PolicyOnly`. s2160 then closed the *first* default-on
execute question: `H-RouteRegress` on the pre-S32 binary. s2161
closed the wait-slot count-byte ORIGIN question:
`H-RetailLoadsCount`. s2162 closed the unsigned PATCH addressing
question: `H-UnsignedMemBu`; image `=1` now reaches title and hangar.
s2163 then selected `H-CinematicRegress` at the post-wait 640
`0x00696100` cinematic and reverted default-on. s2164 selected
`H-NoSuchSite` for unsigned KSEG0 `MEM_*` constants in the two
SIGBUS functions; the sites are register-base guest loads.
s2165 selected `H-RetailExecsValidPtr`: retail takes those
loads at 640 with legitimate KSEG0 pointers. s2166 selected
`H-RetailWriterNamed`: the consumed +0x50 word is stored by
`spawnCutsceneObjectsFromList` `0x800A8144` after
`walkMeshdef0List`. s2167 selected
`H-PortStoreMatchesRetail`: the port writes and reloads
that same heap pointer. s2168 selected
`H-RetailValidV0`: retail `$v0` at `0x800AF2CC` is
`0x800CDB58`, not the port's `0x80000000`. s2169 selected
`H-PortMatchesRetailUntilLater`. s2170 selected
`H-NoHangAtN150`: image-arm `matchKeywordWithPriority` returns
and is re-entered past n=150 on a completing cinematic; the
s2169 640-stall is not a deterministic hang inside that
function. s2171 selected `H-NullV0At87A8`: a failing `=1`
cinematic is SIGBUS at `0x800A87A8` with `$v0=0` after a
good `+0x50` heap pointer, not a hang in matchKeyword or
`spawnCutsceneEffectsAndCues`. s2172 selected
`H-RetailHeap0NeverZero`: the consumed heap-object word0
is stored by `walkMeshdef0List` `0x80057100` after
`rs_malloc` from `hobObjectListItems`+4; retail 87A8
`$v0` stays KSEG0 (`0x800CA748` for the first slot).
s2173 selected `H-PortHeap0MatchesRetail`: the port
writes and reloads that same word on both arms.
s2174 selected `H-StallWord0Intact`: a failing `=1`
640-stall keeps first-slot word0 `0x800CA748` through
last 87A0 n=5825 t=28.4 (lwc zero_logged=0, 0 SIGBUS).
s2175 selected `H-CompletePathDispatchReturned`: a
completing `=1` cinematic takes 87A8 dest `0x800CA748`,
transform entry+return, and dispatch return after last
first-slot 87A0, then title+hangar. Hang location on a
failing cinematic remains open.
The A1 execute / SP-complete / MORT-ownership /
both-arm-validate / task-exit+PCM / two-source-completion
clauses remain selected at the s2118 C88=0 sampled scope
(s2118, s2132–s2140, s2157). Remaining isolation is the
env default. Do not re-flip default-on, S32-address by
guess, NULL-skip, skip/allow `matchKeywordWithPriority`
or the lwc or transform, or add a wait/slot guard.

The stock `aspMain` contract is not the game's MusyX contract. C88
testing selected reversed-or-suppressing polarity at sampled port gate
scope; no blanket gate flip is authorized.

### M3, M4, and generated symbols

The `-0x25A4` pointer-chase family, six-site PIC class, ten-site
audio-slot class, dormant slot-dispatch census, two-line overlay-move
class, and leftover `fake_func_*` size-`> 0xC` class are closed at their
stated scopes. M3 resumes only as an idiom-class audit or with a new
discriminator. M4 accumulator/beam evidence rules out the old shade-lane
theory but is not pixel ground truth. Remaining `func_*` placeholders
are semantic holds or intentional non-sync entries.

## Superseded conclusions

Detailed history is in `PROJECT-OVERVIEW.md` §§26 and 35–42 and the
ledger. Operational reversals:

- “640 is a flaky crash,” missing-input, missing-wait-return, and
  unqualified PCM-null claims were believable because the relevant rows
  were absent. Same-run controls and the accepted LLE/spin recipe later
  reached both target phases.
- The old title/hangar callback split and global zero-payload image-DMA
  claim were believable because joins lacked guest address/full-span
  identity or had not sampled a nonzero hangar task.
- The old clean-stub, canary-poison, final-E50, and uniform-gate
  explanations were believable because the first image and retail runs
  lacked a complete task/consumer or writer-specific table. Those
  controls now show real image DMEM activity, a mixed retail gate, and a
  sampled nonzero hangar join, but they do not authorize a runtime
  change. s2154 further supersedes treating `canary_ok=0` as a runaway
  write: the span is the mix buffer. s2157 supersedes treating that flag
  as a host completion, writeback, or DMA gate: every consumer is a log
  or storage field. s2158 supersedes treating `run_task` as a second
  image-arm isolator: its `ROGUESQ_AUDIO_UCODE` getenv is a probe-gated
  log label / optional canary-prefill skip, and the env-true wrapper
  never calls `musyx_stub`. s2159 supersedes “the image arm is isolated
  because it does not yet satisfy the host task contract”: that summary
  was believable while `canary_ok=0` and A1’s two-source bar were still
  being treated as open, but the named A1 clauses were already closed
  by s2118/s2132–s2140/s2157. Remaining isolation is policy (env
  default), not an unsatisfied contract clause. The
  `waitForMusyXAudioTaskDone` hang comment is a stale pointer to a
  nonexistent M5-AUDIO-PLAN §3 crash family and is refuted as a
  boot-wedge by s2118 image-arm hangar reach. s2160 supersedes
  “default-on is the next safe A1 landing”: that was believable after
  `H-PolicyOnly`, but the same-build unset/`=1` arms SIGSEGV in
  `waitForAnyAudioSlot` before title on the current recipe while `=0`
  matches the stub title/hangar contract. s2161 supersedes treating
  that SIGSEGV as a guest wait/slot defect or a missing count-byte
  write: retail writes the byte from `setDisplayMode` /
  `reapplyDisplayMode` and wait’s jal loads it; the port fault
  address matches unsigned PATCH `MEM_BU` arithmetic
  (`rdram+4GB+0x141AD3`), and the crashing image path is `gate0`
  so original wait MIPS does not perform that load.
  s2162 supersedes treating that SIGSEGV as a live image-arm blocker:
  after `S32`-addressing the PATCH, `=1` returns from wait with
  `c=0x11`/`0x10` and reaches title and hangar. `H-RouteRegress`
  remains true of the pre-fix binary. s2163 supersedes “default-on
  retry is the next safe A1 landing on this binary”: that was
  believable after `H-UnsignedMemBu` wait-return plus s2162 `=1`
  title+hangar, but the same-build unset/`=1` arms failed title at
  the 0x00696100 cinematic (SIGBUS or 640 stall) while `=0` retry
  reached title+hangar. Dispatch/wait still match (`H-DefaultMatchesOptIn`
  at that scope). Polarity reverted. s2164 supersedes treating the
  cinematic `si_addr` values as unsigned KSEG0 `MEM_*` constants in
  those two functions: that was believable from the s2161/s2162
  PATCH shape (`rdram+0x80000044` / `rdram+0x7fff0019`), but the
  bodies contain zero such constants (positive-control defs and
  `MEM_*` counts in the same output). The atos crash lines are
  register-base `MEM_BU($s1,0x1A)` / `MEM_W($v0,0x44)`.
  s2165 supersedes treating those loads as a path retail does
  not take, or as retail-null `$v0`/`$s1`: same-run `[gpr-ctl]`,
  whole-RDRAM 10000, and VI 640/`0x00696100` sit in the same
  log as 148586 exec hits, and every logged crash-site GPR is
  KSEG0 RDRAM. s2166 supersedes treating the `$a2+0x50` word as
  an unattributed overlay/data slot: same-run watch-1 histogram
  names `rs_memset` `0x800078EC` then
  `spawnCutsceneObjectsFromList` `0x800A8144`
  `sw $v0, 0x50($v1)` after `walkMeshdef0List`, and the
  consumer load at that slot reads heap `0x8025A580`.
  s2167 supersedes treating the cinematic SIGBUS as a
  missing, zero, or wild port +0x50 store, or as a load
  that fails to see that store: same-build `=1`/`=0`
  both store `0x8025A580` at dest `0x800C7B0C` and load
  it back (0 mismatches) with `[cutscene-a2-50-ctl]` at
  640 `0x00696100`. `=1` still dies later in
  `matchKeywordWithPriority`.
  s2168 supersedes treating that later SIGBUS as a
  retail-wild object header at `0x800AF2CC`: same-run
  `[gpr-ctl]`, whole-RDRAM 10000, and VI 640/`0x00696100`
  sit in the same log as 792 exec hits, and every logged
  crash-site `$v0` is KSEG0 `0x800CDB58` (not 0, not
  `0x80000000`). The caller is
  `spawnCutsceneEffectsAndCues` `0x800A9248`.
  s2169 supersedes treating that SIGBUS as a wild port
  `$a0`/`$v0` at the same PCs on every `=1` run: same-build
  both arms load retail-class heap pointers (wild=0);
  image failure that run was a 640-stall after logged n=150.
  s2170 supersedes treating that n=150 last-row as hang-inside
  `matchKeywordWithPriority` or as `spawnCutsceneEffectsAndCues`
  stopping: always-log at 640 n>=140 shows n=151 at the same
  timestamp, `effectsEntry==effectsRet` through n=820, and
  both arms reach title+hangar. `H-CinematicRegress` remains
  as intermittent `=1` cinematic failure, not as a hang at
  n=150.
  s2171 supersedes treating a failing `=1` cinematic as
  hang-inside matchKeyword, caller-stop, or effects-hang:
  same-run flow-ctl at 640/`0x00696100`, `effectsEntry==effectsRet`
  n=338, and matchEntry n=168 returned before SIGBUS at
  `0x800A87A8` with `$v0=0` (`si_addr=0x380000044`, matching
  s2164 `MEM_W(0, 0x44)` arithmetic). The `+0x50` heap
  pointer was still `0x8025A580`. The four hang hyps are
  refuted on a failing run, not only s2170's completing run.
  s2172 supersedes treating retail heap-object word0 as 0
  or as an unattributed slot: same-run `[gpr-ctl]`,
  whole-RDRAM 10000, and VI 640/`0x00696100` sit in the
  same log as 28320 exec hits; watch-1 names
  `walkMeshdef0List` `0x80057100` `sw $v0, 0($s7)` after
  `rs_malloc` (`$v0` = `hobObjectListItems`+4); logged
  87A8 `$v0` is KSEG0 `0x800CA748` for the first slot
  (0 zeros). The port 87A8 `$v0=0` is not a retail live
  zero at that word.
  s2173 supersedes treating the port 87A8 `$v0=0` as a
  missing, zero, or failed constructor store at
  `0x80057100`, or as a load of dest `0x8025A580` that
  fails to see that store: same-build `=1`/`=0` both
  store `0x800CA748` at dest `0x8025A580` and load it
  back (0 mismatches) with `[heap0-ctl]` at 640
  `0x00696100`. Completing `=1` never logs word0=0.
  `H-CinematicRegress` remains as intermittent `=1`
  cinematic failure, not as a missing word0 constructor.
  s2174 supersedes treating a failing `=1` 640-stall as
  first-slot word0 clobber or as 87A8 `$v0=0` on that
  run: same-run `[heap0-ctl]` at 640 `0x00696100`, dest
  `0x8025A580` loads 366/366 `0x800CA748` (zero=0), lwc
  zero_logged=0, 0 SIGBUS; cinematic probes stop at
  t=28.4 after last first-slot 87A0 while VI continues
  to `#10752`. `H-NullV0At87A8` remains a separate
  intermittent SIGBUS class (s2171), not this soak.
  s2175 supersedes treating a completing `=1` cinematic
  as hanging after last first-slot 87A0: same-run
  `[heap0-ctl]` at 640/`0x00696100` including
  dispatchEntry n=8; last first-slot 87A0 n=14305
  t=48.4 is followed by lwc87a8 n=14305 dest
  `0x800CA748`, xformEntry/Ret n=14305, and
  dispatchRet n=895, then title+hangar. Hang hyps remain
  for a failing soak, not this completing run.
- The old retail voice-field interpretation was believable because a
  pointer entry was treated as a physical array base.
- The old “B40 was unreached” and s2110 `H-B40-RouteRequired`
  interpretations were believable because reduced pairs lacked a control
  target-phase route. s2111's same-build pair reached title and hangar in
  both arms with identical read/branch tables. s2112 then matched
  phase-7 caller/entry/route rows, superseding the producer selection at
  that paired-recipe scope.
- The s2117 “no contract hypothesis selected” result was believable
  because its image arm stopped in the pre-target 640 phase. s2118
  supplied the missing coverage.
- `0x8000B650` is a shared last-guest-PC breadcrumb, not evidence that
  retail executes the port's fill/wait function.
- The first s2128 drain pair's apparent no-split result was believable
  because the run recipe named an environment gate absent from the
  binary.

## Evidence ledger summary

History through s1879 is in `PROJECT-OVERVIEW.md` §§33–35. The VI-1024
and spin-yield chain is in §36; the M5 archive through s2047 is in
§§37–38; the late route/fill boundary is in §39; the s2080–s2108 archive
is in §40; B40 s2110–s2112 is in §41; and the s2113–s2163 contract,
symbol, MORT, AI, canary, isolator, default-blocker, default-on,
wait-slot count-byte, unsigned PATCH, and cinematic-regress archive
is in §42. s2164 is the unsigned-KSEG0 cinematic `MEM_*` census
(`H-NoSuchSite`). s2165 is the retail GPR census at those PCs
(`H-RetailExecsValidPtr`). s2166 is the retail writer of
cutscene `$a2+0x50` (`H-RetailWriterNamed`). s2167 is the
port store/load of that word (`H-PortStoreMatchesRetail`).
s2168 is the retail `$a0`/`$v0` census at
`matchKeywordWithPriority` (`H-RetailValidV0`). s2169 is
the port `$a0`/`$v0` A/B (`H-PortMatchesRetailUntilLater`).
s2170 is the entry/return flow A/B (`H-NoHangAtN150`).
s2171 is the failing-`=1` flow classification (`H-NullV0At87A8`).
s2172 is the retail writer of heap-object word0
(`H-RetailHeap0NeverZero`). s2173 is the port
store/load of that word (`H-PortHeap0MatchesRetail`).
s2174 is the failing-`=1` 640-stall heap0 classification
(`H-StallWord0Intact`). s2175 is the completing-`=1`
hang-after-87A0 flow (`H-CompletePathDispatchReturned`).

Exact commands, counts, failed retries, and session headings remain in
`PORTING-STATE.md`. Selected hypotheses above must not be widened from
single-source or single-arm observations. No AI-status shortcut, task
ABI, canary-prefill, wait, or guard change follows from `H-PolicyOnly`,
`H-RouteRegress`, `H-RetailLoadsCount`, `H-UnsignedMemBu`,
`H-CinematicRegress`, `H-NoSuchSite`, `H-RetailExecsValidPtr`,
`H-RetailWriterNamed`, `H-PortStoreMatchesRetail`,
`H-RetailValidV0`, `H-PortMatchesRetailUntilLater`,
`H-NoHangAtN150`, `H-NullV0At87A8`,
`H-RetailHeap0NeverZero`,
`H-PortHeap0MatchesRetail`,
`H-StallWord0Intact`, or
`H-CompletePathDispatchReturned`.
Do not re-flip default-on, S32-address by guess, NULL-skip,
skip/allow `matchKeywordWithPriority` or the lwc or transform, or add a
wait/slot guard.

## Method and safety rules

- Ask the retail oracle for ground truth before adding an instrument.
  Arm its whole-RDRAM positive control first; use physical-address
  watches and phase-gated VI callbacks.
- A null is worthless without a same-run positive control. Batch all
  desired counters and every A/B arm in one build/run. Scope counters
  and log budgets to the relevant phase.
- Read `F5-UCODE-REFERENCE.md` before interpreting a Factor 5 display
  list. Regenerate in order: `make_elf.py`, N64Recomp,
  `fixup_game_funcs.py`, then CMake. Diagnostics in generated output
  belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM
  present. Capture paths must not start with `.` in the final component.
- Do not run `git submodule update`, `git checkout -- lib/...`,
  `git clean`, or `git reset --hard`. If `lib/` changes, export submodule
  patches in the same iteration.
- A mitigation is not an explanation. Name the writer, state legitimacy,
  and add an `ORIGIN:` line before landing a skip, allow, guard, or
  restore.
- Never add a diagnostic field without a whole discriminating table and
  an outcome that selects among hypotheses. A repeated join key or
  counter is not a work unit.
