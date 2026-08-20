# NEXT work unit (s2042)

HYPOTHESIS-ID: m5-callback-side-pcm-witness

## Work unit

Build once, then run one fresh `ROGUESQ_M5_C88_VALUE=1` arm using forced LLE,
opt-in Factor 5 audio, spin yield, `ROGUESQ_LOG_ALL=1`, the existing M5
writer/gate/service controls, and the known title-to-hangar phase-relative
schedule. This is a corrected callback-side PCM witness after s2041 reached
title only. Keep the retail-value writer unchanged and treat C88=1 as an
opt-in route arm. Do not interpret bridge or PCM rows unless both the title
and hangar VI anchors, the 24/24 `s2006-svc` control, and live gate/task
controls are present.

## Competing hypotheses and discriminator

- **H1 — upstream-valid PCM:** target-phase `[pcm-bridge]` rows carry nonzero
  bytes and paired `pcm-sanity` rows include `all_zero=0`. Usable samples
  reach the callback; the next boundary is AI/device ordering.
- **H2 — zero payload at the callback:** target-phase bridge rows fire with
  `nz=0` and paired sanity rows remain `all_zero=1`. The callback is reached,
  but task/image ABI or upstream sample production is wrong.
- **H3 — device-side boundary:** target-phase bridge rows carry nonzero data,
  but all paired sanity rows remain zero. The remaining boundary is after the
  callback, in AI submission or device ordering.
- **H4 — guest submit/queue boundary:** both anchors, the 24/24 service
  control, gate-one rows, and real audio-task rows are live, but no target-
  phase bridge row appears. The guest AI-submit/queue path is next.
- **H5 — route failure:** either target anchor or required positive control is
  absent. This is a route result and cannot select a PCM hypothesis.

The one-run table is: preflight and phase anchors; `s2006-svc` entry/exit;
phase-valid `reapplyDisplayMode` writer and gate-one rows; real
`audtask-dispatch`; then paired target-phase `[pcm-bridge]` and
`[pcm-sanity]` rows. Expected outcomes are H1 (`nz>0` with `all_zero=0`), H2
(`nz=0` with `all_zero=1`), H3 (`nz>0` with `all_zero=1`), H4 (live controls
but no bridge), or H5 (missing anchor/control). Counts must be phase-scoped.

## Commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp

set +e
env REGRESS_SECS=150 REGRESS_INTERVAL=0.6 REGRESS_REQUIRE_VISUAL=1 \
REGRESS_KEYS='640@1:start 640@3:start 640@5:start 640@7:start 640@9:start 1024@2:a 1024@3:start 1024@4:a 1024@6:start' \
REGRESS_LABEL=s2042_pcm \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 \
ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2042_pcm 150 > scratch/agent/s2042_pcm_driver.log 2>&1
rc=$?
print "probe_rc=$rc"
```

After the run, read `scratch/agent/s2042_pcm/verdict.json` and use only
bounded `grep -c`, `grep -n ... | head/tail`, and `tail` on `run.log`. Record
the selected row table before interpreting any PCM result.
