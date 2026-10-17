# Resume: compare the keyed retail and port M4 streams

Checkpoint status: this retry did not rerun the experiment. The prior port arm
completed and its artifact is `scratch/agent/m4-port-next/run.log`; no retail
arm or join ran. The existing same-run controls and 4,091 keyed rows refute
H3's missing-port-key prediction, but do not select H1 or H2. Resume the same
single work unit. Session 5332 reached
`vi_width=512`, origin `0x006AB400`; the port key path emitted 4,091 target
rows with task serial `961`, generated PCs `0x112C` and `0x17F0`, and
increasing per-task step values. Do not infer PC from stage ordinal or treat
the constant task serial in this one long task as a missing field.

Competing hypotheses and discriminator:

- H1: retail and port agree on first/last writer and VACC lane for repeated exact keys.
- H2: both streams join, but a repeated writer/lane mismatch remains.
- H3: the two arms fail to produce a live positive control or exact join despite the port key path.

Discriminating measurement: run the independent cxd4 arm and the rebuilt port
arm with whole-RDRAM/VI positive controls, then join repeated exact
`(origin,width,task_serial,rsp_pc,step_bucket)` keys. H1 requires matching
writer/lane summaries; H2 requires a repeated mismatch; H3 requires a failed
positive control or failed join. A hook count alone is not a field control.

Resume commands: run the retail oracle arm with its validated whole-RDRAM
control, then run the port arm with the validated phase-gated recipe below.
Require both positive controls and exact-key rows before comparing. Do not add
a mitigation or infer from stage ordinals.

Retail control:

```sh
tools/oracle/build/rs64_oracle --core \
  /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 8 --watch-write 0x0:0x800000 --hit-cap 3 --vi-trace
```

Port recipe:

```sh
env ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M4_Y8000=1 ROGUESQ_M4_Y8000_WIDTH=512 \
  ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 \
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 \
  PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  zsh tools/probe.sh scratch/agent/m4-port-compare 240 1
```

HYPOTHESIS-ID: m4-accumulator-boundary
