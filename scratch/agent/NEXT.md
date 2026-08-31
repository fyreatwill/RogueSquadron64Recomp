# NEXT work unit — add exact status-03 clear witness and re-run port contract

HYPOTHESIS-ID: m5-status03-port-worker-contract

The qualified port route reaches the named worker with status `03`, but the
current regeneration-surviving probe does not witness the exact clear at
`0x8009B7EC`. Add that one missing writer witness, then repeat the same fixed
route so the gate/no-clear result can be separated from an instrumentation
gap.

Competing hypotheses:

- `H-PortStatus03Reaped`: the exact clear witness fires after a status-03
  worker entry and before its return.
- `H-PortStatus03Gate`: status-03 worker entry/return remains live but the
  exact clear witness stays absent while the worker gate rows are live.
- `H-PortStatus03OtherPath`: a status-zero write appears without the named
  worker, or a different status table is the active one.

Discriminating measurement: one Debug port run with host/task/PCM controls,
title `1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, status-table activity,
worker entry/previous-PC rows, the exact `0x8009B7EC` store, and worker return.
Worker entry → exact zero store → return selects reaping; entry without a
zero store selects the gate only when its gate row fires; a zero store with no
named worker selects another path. Missing target controls make the run
invalid.

Exact phase-gated rows for this build/run: `[phase] width=1024` and
`[phase] width=512` are the target controls; positive controls are
`[host-boundary]`, `[audio-task]`, `[pcm-boundary]`, and
`[slot-byte]`/`[slot-sb]`. The discriminator rows are
`[m5-service-entry]` (worker entry with status/index),
`[m5-status-zero]` (the store at `0x8009B7EC`, including previous PC and
slot/status), and `[m5-service-return]` (worker return/retirement). Count
only rows after the 512 phase transition. A target-valid run with all three
worker rows in order selects reaping; entry plus gate/slot evidence but no
zero store selects the gate; zero stores without the named worker selects
the alternate-path hypothesis.

Preparation and run surface (inspect existing regeneration-surviving markers
before changing source):

```sh
rg -n 'status-03|status03|0x80154620|serviceVoicePoolFrame|slot-byte|zero' src RecompiledFuncs scratch/agent tools docs/M5-AUDIO-PLAN.md
sed -n '1,220p' scratch/agent/run_s3327_m5_slot_status_port.sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_ALL=1 zsh <validated-port-driver>
```

Before building, locate the existing `s2020-svc` and `m5-audio-event` fixup
sites, add one phase-gated regeneration-surviving marker at the store PC
`0x8009B7EC` (including previous PC, slot base, prior status, and stored zero),
and preserve the existing entry/exit and slot controls. Build once, then run
the fixed `tools/probe.sh` route for 90 seconds after the 1024 phase gate with
`ROGUESQ_AUDIO_UCODE=1` and the s3364 key schedule. Do not change behavior or
add a mitigation.
