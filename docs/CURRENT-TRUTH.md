# Rogue Squadron 64 Recomp — current truth

Operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable background
is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed run evidence remains
in `scratch/agent/` and the append-only ledger.

Current maintenance marker: Session 3377 (2026-08-31). This file was compacted
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
  excluded from the narrow count. The upstream zero-source boundary is now
  selected; the writer of those RDRAM spans remains open.

No output substitution or mitigation is authorized. Do not change waits, slots,
status handling, consumer dispatch, or PCM writeback while tracing the source.

## Next steps

Priority is maintenance, M5 de-stubbing, systematic M3, then generated-symbol
renaming. M5 design is in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).

1. Attribute writers of zero source spans `0x1797B0` and `0x1798B0`. Before
   building instrumentation, obtain/confirm retail writer-PC ground truth for
   those physical ranges and the existing port store hooks. Then batch one
   phase-scoped writer census and one validated run.
2. Competing hypotheses for that unit:
   - `H-PortRSPSourceZero`: the upstream producer is absent or writes zero.
   - `H-PortRSPTransformZero`: source is nonzero but the transform emits zero;
     this remains unevaluable until a nonzero source is observed.
   - `H-PortDMADestinationMismatch`: the joined DMA is not the PCM source;
     currently refuted for joined stage-2/3 rows.
3. Discriminator: join every writer of `0x1797B0/0x1798B0` to the target
   audio-task ordinal/row. No writer or only zero stores selects an absent/
   zero producer; nonzero writes followed by zero source-DMEM selects a DMA
   visibility/ordering edge; a different source range reopens source identity.
4. Keep phase, audio-task/ABI, PCM, image-stage/DMA, title, and hangar positive
   controls. Build all desired arms in one iteration if an A/B is needed. Do
   not change behavior. Evidence: `scratch/agent/s3376_m5_zero_pcm_source.md`.

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

- `scratch/agent/s3376_m5_zero_pcm_source.md`
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
