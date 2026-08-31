# NEXT work unit — qualify the port status-03 worker contract

HYPOTHESIS-ID: m5-status03-port-worker-contract

Retail ground truth now independently shows the named service worker entering
the status-03 path and clearing a slot. The next unit compares that contract
with the already qualified port image-arm hangar route; it is diagnostic only.

Competing hypotheses:

- `H-PortStatus03Reaped`: port enters `serviceVoicePoolFrame`, reaches the
  status-zero worker store, and returns through the normal contract.
- `H-PortStatus03Gate`: port enters the worker but its slot/status gate keeps
  the status-zero store from executing.
- `H-PortStatus03OtherPath`: port completion uses an un-watched worker or a
  different status table.

Discriminating measurement: one Debug port run with host/task/PCM controls,
title `1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, status-table activity,
worker entry/previous-PC rows, all status-table zero stores, and shutdown or
drain return markers. Worker entry → zero store → return selects reaping;
entry without a zero store selects the gate only when the gate row fires; a
zero store with no named worker selects another path. Missing target controls
make the run invalid.

Preparation and run surface (inspect existing regeneration-surviving markers
before changing source):

```sh
rg -n 'status-03|status03|0x80154620|serviceVoicePoolFrame|slot-byte|zero' src RecompiledFuncs scratch/agent tools docs/M5-AUDIO-PLAN.md
sed -n '1,220p' scratch/agent/run_s3327_m5_slot_status_port.sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_ALL=1 zsh <validated-port-driver>
```

Before building, write the exact phase-gated worker/zero/return markers into
this file and batch every arm in one build. Do not change behavior or add a
mitigation until the port writer/value contract is captured.
