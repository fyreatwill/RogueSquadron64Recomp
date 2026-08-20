# NEXT work unit (s2039)

HYPOTHESIS-ID: m5-callback-side-pcm-witness

## Work unit

Run one opt-in C88=1 arm from a freshly built binary with forced LLE, the
opt-in Factor 5 audio path, spin yield, and the post-title width-relative
schedule that reached both target anchors in s2038. Enable `ROGUESQ_LOG_ALL=1`
so the existing `[pcm-bridge]` census is live. This is a single-arm callback
witness, not a writer A/B: keep the retail-value store opt-in and unchanged.
The C88=1 assertion may terminate the run after the target table; rows before
that terminal symptom remain usable if all positive controls are live.

## Competing hypotheses and discriminator

- **H1 — valid PCM reaches the host bridge:** phase-valid `[pcm-bridge]` rows
  at `0x00790400` and/or `0x006AB400` report `nz>0`, and the independent
  `pcm-sanity` rows report `all_zero=0`. The producer/task path is producing
  nonzero samples; the next boundary is AI/device ordering, not the RSP image.
- **H2 — the bridge receives only silence:** phase-valid `[pcm-bridge]` rows
  exist with `nz=0` and the independent `pcm-sanity` rows remain all zero.
  The callback path is reached, but the task/descriptor/codec side is still
  invalid; do not change SDL or AI behavior.
- **H3 — the guest never queues a bridge buffer:** phase-valid gate-1 and
  `audtask-dispatch` controls are live, but no target `[pcm-bridge]` row
  exists. This selects the guest AI submit/queue boundary for the next M5
  unit.
- **H4 — harness or route failure:** preflight, title/hangar anchors,
  post-640 host-input edges, or the 24/24 `s2006-svc` positive control is
  missing. Reject the PCM null and repair the route in a new work unit.

The discriminator is one same-run table: `input=ok visual=ok`; width-relative
host Start edges; title/hangar VI transitions and origins; `s2006-svc`
entry/exit; phase-valid `reapplyDisplayMode` writer and raw-gate/gate-1 rows;
`audtask-dispatch`; target `[pcm-bridge]` rows with `bytes`, `fnv`, and `nz`;
and target `pcm-sanity` rows. The `s2006-svc` and phase transitions are the
positive controls; a callback count alone is not a control.

## Commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp

set +e
env REGRESS_SECS=45 REGRESS_INTERVAL=0.6 REGRESS_REQUIRE_VISUAL=1 \
REGRESS_KEYS='640@1:start 640@3:start 640@5:start 640@7:start 640@9:start 1024@1:start 1024@3:start 1024@5:start' \
REGRESS_LABEL=s2039_pcm_bridge \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2039_pcm_bridge 45 > scratch/agent/s2039_pcm_bridge_driver.log 2>&1
rc=$?
print "rc=$rc"
```

After the run, use only bounded `grep -c`, `grep -n ... | head/tail`, `tail`,
and `verdict.json` reads. A scorer FAIL caused only by a post-crash transition
heuristic does not override live preflight and phase controls.
