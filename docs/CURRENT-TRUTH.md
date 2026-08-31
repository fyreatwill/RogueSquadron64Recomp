# Rogue Squadron 64 Recomp — current truth

Operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable background
is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed run evidence remains
in `scratch/agent/` and the append-only ledger.

Current maintenance marker: Session 3377 (2026-08-31); active state refreshed
through Session 3391 (2026-08-31). This file was compacted
from 991 lines / 60,639 bytes to a concise active-state record; sessions
s3201–s3376 remain in the ledger and archived overview.

## Current state

The native port builds and boots through attribution, the N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024
(`0x00790400`), and hangar VI 512 (`0x006AB400`) on the validated
spin-yield/F5-LLE route. Hangar visuals still have geometry/color artifacts.
Audio is not production-complete: the Factor 5 image task is the qualified
real-audio arm and `musyx_stub`/Broke is the silent control.

The default port now returns from the attract viewer and reaches the
cinematic loop, but its stage advancer sees null `0x800B0934`; the
initializer call at `0x800A62B4` is skipped because port skip-allow remains
zero. Retail independently sets that byte to one at about 48.1 seconds,
enters the initializer, and reaches title 1024. This is a known cinematic
parity boundary, not a license to force the flag or bypass state.

M5 is the active engineering thread. Sessions 3369 and 3372 established the
status-03 worker/clear contract on retail and port. Sessions 3373–3376 then
narrowed the remaining gap to zero PCM data at the observed port RSP-DMA
source boundary:

- Retail independently writes all three primary PCM spans 768 times with
  nonzero payloads; the observed guest writer is `0x800078EC`.
- The qualified port reaches title and hangar with phase, audio-task/ABI,
  image-stage/DMA-join, and PCM controls live and no crash/abort.
- Joined stage-2/3 rows have zero source-DMEM, zero post-transform DMEM,
  and zero destination payload (`F59C39C5` / `762B22A5`, `nz=0)).
  Stage-2 destination was nonzero before the observed DMA, so this is not
  merely an empty destination read.
- This selects `H-PortRSPSourceZero` at the observed boundary and refutes
  `H-PortDMADestinationMismatch` for those joined rows. Transform behavior
  on nonzero input is unevaluable.
- Session 3378's source-DMA census passed its hook control and found 12 narrow
  target-phase DMAs: 7 from `0x1797B0` into DMEM `0x6F0` and 5 from
  `0x1798B0` into `0xCB0`; all payloads were zero. Broad task-data DMAs were
  excluded from the narrow count. Session 3379 attributed 512 target-phase
  port stores into `0x1797B0:0x1798B0` to `0x800078EC`; every observed byte was
  zero. Retail independently attributes that PC to nonzero writes in both
  spans. This selects `H-PortSourceWriterZero`, refutes writer absence for the
  observed port span, and moves the gap upstream to the writer's input/caller
  contract. Transform behavior on nonzero input remains unevaluable.
- Session 3385 rebuilt the stale executable and re-qualified the paired route:
  no-log and established-logging arms both reached title VI 1024 and hangar
  VI 512, with zero crash/abort markers. The logging arm's phase and audio/task
  controls fired. The prior s3384 pre-title crash was not reproduced; no
  direct-writer row occurred in this qualification window, so writer-edge
  hypotheses remain open.
- Session 3380's fixed caller census passed whole-RDRAM, title, hangar,
  audio-ABI, image-join, PCM-join, and PCM-boundary controls. The port target
  span was issued by `rs_memset` callsite `0x8008F2CC` with
  `dst=0x801797B0`, `val=0`, `len=0x298`; retail's target-phase writer
  predecessor was independently `0x8002BEEC` (399 rows), with the same
  sampled zero-fill tuple. This selects `H-PortSourceCallerMismatch` at the
  observed boundary. It does not establish that the zero fill is illegitimate
  or select a nonzero-input path.
- Session 3386 phase-qualified the direct-writer edge. The port reached title
  and hangar with all controls live; its only target-overlap row was the
  zero-fill `0x8008F2CC -> rs_memset` path, with no `0x8002BEEC` caller edge or
  callback-writer row. The independent retail control fired, and its
  undriven route executed `0x800078EC` 9,667 times but not `0x8002BEEC`.
  This selects `H-EarlierProducerGap` for the driven port route and refutes a
  port-side dispatch alias at the observed boundary. It does not establish
  whether the zero fill is legitimate.
- Session 3387 asked the independent retail oracle for the selected producer
  edge, with a whole-RDRAM positive control, then ran the existing port census
  in the same phase-qualified route. Retail reached title and hangar, and its
  two target spans each had 449 writes: 256 phase writes from `0x800078EC`,
  116 from `0x80007670`, and small initialization bursts. The port reached
  both phases and exposed only the zero-fill `0x8008F2CC -> rs_memset` row at
  the target span; it exposed no matching `0x800078EC`, `0x80007670`, or
  `0x8002BEEC` edge. This selects `H-RetailDrivenProducer` and refutes a
  matching port producer edge at the observed boundary. It does not establish
  that the port zero fill is illegitimate or identify the missing producer's
  input/dispatch contract. Detailed evidence is in
  [M5-S3387-PRODUCER-EDGE.md](M5-S3387-PRODUCER-EDGE.md).

- Session 3388 repeated the qualified pair with both producer execution
  watches. Retail's whole-RDRAM control and both phase gates fired; target
  writer histograms included `0x80007670` (116/184) and `0x800078EC`
  (512/816), and `0x8002BEEC` preceded `0x800078EC` in 387 execution rows.
  The port reached title and hangar but exposed only the zero-fill
  `0x8008F2CC -> rs_memset` at `0x801797B0`, with no matching producer edge;
  PCM remained zero. This reinforces `H-RetailDrivenProducer` at the observed
  boundary and points the next census at the predecessor/call chain. Evidence
   is in [M5-S3388-PRODUCER-PREDECESSOR.md](M5-S3388-PRODUCER-PREDECESSOR.md).

- Session 3389 watched the selected predecessor PCs on retail with a
  whole-RDRAM control. Retail reached title and both `0x8002BEEC` and
  `0x800078E8` fired there; their immediate predecessors were `0x8002BEE8`
  and `0x800078E0`. Retail target spans had 502/500 writes, but the explicit
  hangar 512 bucket had no rows. The port reached title and hangar with
  controls live and again exposed only `0x8008F2CC -> rs_memset` zero-fill at
  the target span, with no matching producer or callback row and zero PCM.
  This reinforces an earlier producer gap at the observed boundaries, but is
  not a like-for-like hangar discriminator; the next probe moves to
  `0x800078E0`/`0x8002BEE8`.

- Session 3390 repeated the retail arm with the selected predecessor PCs and
  target-span payload control. Whole-RDRAM and target controls fired (11,830
  and 1,830 writes); retail reached hangar and had 664 target-writer samples,
  189 nonzero. The port reached title and hangar with controls live but again
  exposed only `0x8008F2CC -> rs_memset` zero-fill, with no matching producer
  edge and zero PCM. This selects `H-EarlierRetailProducer` and refutes a
  matching port predecessor edge and a legitimate zero boundary at this
  scope. The port later hit the existing unaligned-ROM DMA assertion after
  leaving hangar, outside the discriminator. Evidence is in
  [M5-S3390-PREDECESSOR-EDGE.md](M5-S3390-PREDECESSOR-EDGE.md).

- Session 3391 enumerated the current generated `jal 0x800078E0` set (88
  callsites) and ran the selected earlier-producer census. Retail's
  whole-RDRAM control fired 223,338 times over 7,169 VI frames; its
  `0x8002BEE8` predecessor execution watch fired 37,635 times and its
  `0x800078E0`/`0x800078E8` controls were live. The target-span oracle watch
  produced no visible hit rows, so payload attribution for this arm is
  partial. The port reached title and hangar with phase, static-call, and PCM
  controls live; its only hangar target row remained the zero-fill
  `0x8008F2CC -> rs_memset` path (`dst=0x801797B0`, `len=0x298`), with no
  callback or earlier-producer row and zero PCM. This selects
  `H-EarlierPortContract` at the observed boundary, but does not establish
  that the zero fill is illegitimate or provide a retail payload comparison.
  Evidence is in [M5-S3391-EARLIER-PRODUCER.md](M5-S3391-EARLIER-PRODUCER.md).

No output substitution or mitigation is authorized. Do not change waits, slots,
status handling, consumer dispatch, or PCM writeback while tracing the source.

## Next steps

Priority is maintenance, M5 de-stubbing, systematic M3, then generated-symbol
renaming. M5 design is in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).

1. Refine the selected earlier producer/call contract with a bounded oracle
   run retaining only `0x8002BEE8`, `0x800078E8`, and `0x800078EC` execution
   rows plus the exact target-span watch, avoiding the noisy `0x800078E0`
   field table. Keep whole-RDRAM control and the canonical driven Rice route.
   Batch one equivalent port census with the existing controls; do not change
   output or audio behavior.
2. Discriminator: a phase-gated retail target write with a valid predecessor
   and no port counterpart keeps `H-EarlierPortContract`; a matching port
   predecessor and target write moves the boundary downstream; matching zero
   writes on both routes make the boundary legitimate. If either target watch
   is absent while its whole-RDRAM control fires, record that arm as partial
   and do not select a payload hypothesis.

M5 Step 3 remains gated until a like-for-like target row names one missing image
task/output contract edge. Configured-host PatchesLib validation is an open
dependency only; this Unix checkout lacks the MIPS toolchain and generated
patch input, so do not repeat the local missing-target check.

Closed or parked work:

- The task-start guest-pointer guard is landed and runtime-validated on the
  title/hangar route; the task-pointer class is closed.
- The callback-table source/target qualification is closed: port matches the
  retail guest chain `0x800919D4 -> 0x800919EC -> 0x80007910`; unresolved
  indirect consumer/output behavior is subsumed by the active PCM boundary.
- The B1C source census, generated free-list-walk class, and generated-symbol
  renaming campaign are closed at their measured scopes.
- Keep external retail-entry, hangar `0x8000` Y/accumulator arithmetic, and
  M5 SP-yield/MORT publication threads parked pending a new discriminator.
- The corrected MORT descriptor edge is `+0x190` to
  `dmaVoiceSampleAndSignal`.

## Durable boundaries and operating rules

Factor 5 uses [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter limits,
null-GBI guards, and related defenses are safety mechanisms, not explanations.
Overlay dispatch is fixed enough for the validated route.

Ask the independent retail oracle for ground truth before adding port
instrumentation. Every instrument needs a same-run positive control, a
phase-scoped budget, and two independent lines of evidence before promotion.
Phase-gate animated comparisons on VI transitions. Batch all A/B arms in one
build and run. A null without a positive control is worthless.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py -> CMake`.
Never hand-edit generated functions for behavior changes. If `lib/` changes,
run `./submodule-patches/export.sh` and commit refreshed patches in the same
iteration. Never run submodule update, checkout, clean, or hard reset commands.
Kill runs with SIGKILL and run from `build/`. A mitigation-shaped change needs
an `ORIGIN:` line naming the writer and stating whether its value is legitimate.

CMake's `RECOMP_FUNCS_DIR` is `../N64Recomp/RecompiledFuncs`. The strong
SP-task override and completion-aware `osSpTaskYielded` contract are the
current defaults; request-only behavior is an explicitly superseded diagnostic
arm. Static boundary-only symbol classifications remain non-renames without
defensible semantic evidence.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The request-only SP-yield interpretation and viewer-stall chain from sessions
3288–3302 describe only the old diagnostic arm. Session 3304's
completion-aware default returns the viewer, so those findings are not the
current default explanation.

The old interpretation of the 1,578-entry cinematic dispatcher pool as an
audio-slot pool was superseded by the actual MusyX voice-table measurement:
title/hangar reachability is valid and the voice mask is zero/max=1.

The old `H-PtrZeroSkip`/cinematic loop findings remain descriptive of the
port/retail parity boundary, but do not justify forcing state; the skip-allow
writer and initializer ordering are the measured explanation.

## Evidence index

Latest M5 evidence:

- `scratch/agent/s3386_m5_direct_writer_census.md`
- `docs/M5-S3389-PREDECESSOR-EDGE.md`
- `scratch/agent/s3376_m5_zero_pcm_source.md`
- `scratch/agent/s3379_m5_source_writer.md`
- `scratch/agent/s3375_m5_port_pcm_writer.md`
- `scratch/agent/s3374_m5_retail_pcm_writer.md`
- `scratch/agent/s3373_m5_consumer_output_contract.md`
- `scratch/agent/s3372_m5_status03_port_contract.md`
- `scratch/agent/s3369_m5_status03_worker_contract.md`
- `scratch/agent/s3364_m5_port_callback_edge.md`

Baseline and independent boundary evidence remains indexed in the ledger and
PROJECT-OVERVIEW section 54. Use bounded `grep`/ `sed` windows for
PORTING-STATE.md; never read it wholesale. The soak queue is consumed by
automation; fold only new tail lines into the next audit.
