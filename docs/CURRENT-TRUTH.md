# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger remains
authoritative for exact commands and probe rows. Maintained in Session 2160
(2026-08-21); behavioral and source evidence is current through s2160.

This file is intentionally compact. Archives: s2080–s2108 in
`PROJECT-OVERVIEW.md` §40; s2110–s2160 in §§41–42.

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
  on. s2160 selected `H-RouteRegress` for the A1 default-on flip: unset
  and `=1` both SIGSEGV in `waitForAnyAudioSlot+1060` from
  `menuOverlayInit` at 640 `0x0066A500` (`si_addr=0x400141ad3`, host
  XOR-3 of guest `D_80141AD0`). Same-build `=0` reached title
  `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` with
  `real_ucode=0`, `dma_count=0`, `break_pc=0`. Default polarity was
  reverted. Do not retry default-on until that image-arm wait-slot
  SIGSEGV is explained.
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
  `H-RouteRegress` (`scratch/agent/s2160_default_on_ab.txt`). The
  image arm is still isolated by the env default, now because the
  current recipe SIGSEGVs at `waitForAnyAudioSlot` before title, not
  because a host-task contract clause remains unnamed. Do not move
  the canary, change canary prefill, or change
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
| s2160 | `H-RouteRegress` | same-build unset/`=1` SIGSEGV at `waitForAnyAudioSlot+1060` before title; `=0` title+hangar stub contract; not `waitForMusyXAudioTaskDone` | retry default-on; canary / AI-status / wait-slot guard |

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

1. **M5 image-arm `waitForAnyAudioSlot` SIGSEGV.** s2160 selected
   `H-RouteRegress` and reverted default-on. Next unit is the boot
   crash at `waitForAnyAudioSlot+1060` (`si_addr=0x400141ad3`, guest
   `D_80141AD0`) on `ROGUESQ_AUDIO_UCODE=1`, which stub returns from.
   Do not add a wait/slot guard and do not retry default-on. ORIGIN
   required before any skip/allow/restore.
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
question: `H-PolicyOnly`. s2160 then closed the default-on execute
question: `H-RouteRegress`. The A1 execute / SP-complete /
MORT-ownership / both-arm-validate / task-exit+PCM /
two-source-completion clauses remain selected at the s2118 C88=0
sampled scope (s2118, s2132–s2140, s2157). Remaining isolation is the
env default because the current image recipe SIGSEGVs in
`waitForAnyAudioSlot` before title. Do not treat s2118 hangar reach as
a license to default the arm.

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
  matches the stub title/hangar contract.
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
is in §40; B40 s2110–s2112 is in §41; and the s2113–s2160 contract,
symbol, MORT, AI, canary, isolator, default-blocker, and default-on
archive is in §42.

Exact commands, counts, failed retries, and session headings remain in
`PORTING-STATE.md`. Selected hypotheses above must not be widened from
single-source or single-arm observations. No AI-status shortcut, task
ABI, canary-prefill, wait, or guard change follows from `H-PolicyOnly`
or `H-RouteRegress`. Do not retry the default-on polarity until the
image-arm wait-slot SIGSEGV is explained.

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
