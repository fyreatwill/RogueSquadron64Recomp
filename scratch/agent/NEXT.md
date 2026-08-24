# NEXT work unit (s2274) — M5 Step 1 canonical-route validation

HYPOTHESIS-ID: m5-step1-task-output-contract

## Work unit

Run one unchanged-build, phase-gated pair with the default silent
`M_AUDTASK` arm and the opt-in `factor5_ucode_b` arm using the canonical
reduced trace that qualified s2272. Keep all runtime behavior and defaults
unchanged. The pair must qualify the silent arm at the hangar before
launching the image arm, so the image launch is not used as a route gate.
Record one phase-keyed validation row for each arm and do not promote the
image arm or change a gate, slot, guard, return, or writeback.

## Competing hypotheses and discriminating measurement

- **H-AudioDegeneracy:** both arms pass the route controls, while only the
  image arm adds the predicted downstream audio edge: nonzero DMEM/DMA,
  completed task/SP edge, service and slot/voice progress, and a nonzero
  phase-keyed PCM source/consumer join. This supports audio de-stubbing as a
  causal change, but does not by itself authorize a default flip.
- **H-ContractGap:** the image arm has dispatch, task-field identity,
  nonzero DMEM/DMA, and `Broke`/SP completion, but one later service,
  slot/voice, output, or PCM join is absent or unordered. This selects the
  first missing contract edge for a later bounded change.
- **H-MixedPipelines:** the image RSP row closes while the MORT descriptor
  class/CPU voice path remains independent of the arm, or the inverse. This
  keeps Factor 5 audio and CPU MORT work as separate investigations.
- **H-RouteInvalid:** either arm lacks the positive route controls or reaches
  no target phase. The comparison is unevaluable and selects route stability
  work rather than an audio explanation.

The single discriminating table is phase-keyed:
`arm,phase,width,origin,dispatch,task_fields/source_hash,dmem_changed,
dma_ranges,image_exit,sp_completion,service_entry/return,status_01_02_00,
status_03_reap,voice_activity,mort_class,pcm_source/consumer_join,
source_before_consumer,missing_func,b40_rows,route_state_rows,title,hangar,
crash_pc,last_guest_pc`.

The positive controls are one `[missing-func]`, 14 B40 rows, 28 route-state
rows, title `1024 @ 0x00790400`, and hangar `512 @ 0x006AB400` in both arms;
the stagger control is an explicit `silent_first_512=observed` line before
the image process is launched. Select H-AudioDegeneracy only when both arms
are route-qualified and the image-only downstream delta is complete; select
H-ContractGap when image task controls pass but a named later edge does not;
select H-MixedPipelines when the RSP/MORT rows separate; otherwise select
H-RouteInvalid.

## Ground-truth prerequisite

No new instrument is being added. The retail whole-RDRAM watch and writer
controls already recorded in the M5 plan/current truth are the independent
positive control; this run uses the existing port-side phase/task/PCM probes.

## Build

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp -j2
```

## Run

Use the pair driver from the repo root. Both arms use
`ROGUESQ_M5_C88_VALUE=0`, `ROGUESQ_SPIN_YIELD=1`,
`ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`, with
`PROBE_PHASE_WIDTH=1024` and `PROBE_KEYS_FROM_PHASE=1`. Keep only the
canonical existing audio-return, PCM-boundary, B40/route-state, image-stage,
runner, thread-resume, and OST-writeback probes; the prior attempt showed
that adding VI-caller/filter/gate/task-contract detail can make this route
miss its target window. The driver must SIGKILL both processes, capture under
`scratch/agent/`, and reject an image launch unless the silent log contains
the explicit hangar phase line.

Exact command after the build:

```sh
zsh scratch/agent/run_s2273_m5_step1_pair.sh s2274_m5_step1_canonical
```

Read only bounded summaries and phase-keyed rows from the two run logs. The
next ledger entry must retain both arm controls, the stagger gate, every
nonzero image/PCM join, and any missing service/slot/voice/MORT edge.
