# NEXT work unit (s2043)

HYPOTHESIS-ID: m5-callback-route-isolation

## Work unit

Build once, then run one fresh `ROGUESQ_M5_C88_VALUE=1` arm with forced LLE,
opt-in Factor 5 audio, spin yield, and all passive M5 controls through the
phase-gated `tools/probe.sh` wrapper. Wait for VI 1024, start the dense title
A/Start schedule only after that phase, and keep capturing after the phase
changes. This removes the regress scorer's invalid “undriven” classification
from the route measurement. Do not interpret bridge or PCM rows unless both
title VI 1024 and hangar VI 512 anchors, the 24/24 `s2006-svc` control, and
live gate/task controls are present.

## Competing hypotheses and discriminator

- **R1 — wrapper/schedule boundary:** the phase-gated wrapper and dense title
  schedule produce a VI-512 transition. The earlier route failures were
  launch/schedule artifacts; the callback PCM witness becomes admissible.
- **R2 — guest title-to-hangar boundary:** phase-valid `pad-host` A/Start
  edges, service, writer, gate, and task controls are live, but no VI-512
  transition occurs. The next probe is inside the guest menu/title route.
- **R3 — focus/event boundary:** the phase-gated wrapper posts keys but no
  phase-valid `pad-host` A/Start edge appears. The remaining boundary is the
  host focus/event path, not PCM production.

The one-run discriminator is the phase table joined to post-1024
`pad-host` rows: VI 512 selects R1; live post-1024 host edges without VI 512
select R2; no post-1024 host edges selects R3. PCM rows are admissible only
under R1 and the required positive controls.

## Commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp

set +e
env PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
PROBE_KEYS='1:a 2:start 3:a 4:start 6:start 8:start 10:start 12:start 14:start 16:start 18:start' \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 \
ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/probe.sh scratch/agent/s2043_route 120 0.6 > scratch/agent/s2043_route_driver.log 2>&1
rc=$?
print "probe_rc=$rc"
```

After the run, inspect only bounded `grep -c`, `grep -n ... | head/tail`,
and `tail` slices of `scratch/agent/s2043_route/run.log`. Record the phase,
post-1024 `pad-host`, service, gate, task, and hangar rows before interpreting
any PCM result.
