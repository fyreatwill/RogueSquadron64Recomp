# NEXT work unit (s2040)

HYPOTHESIS-ID: m5-callback-route-c88-control

## Work unit

Build once, then run a same-build concurrent route comparison: one
`ROGUESQ_M5_C88_VALUE=1` arm and one unset/default arm. Use forced LLE, opt-in
Factor 5 audio, spin yield, `ROGUESQ_LOG_ALL=1`, and the eleven width-640
Starts that previously reached the target route. This is route qualification
for the callback witness, not a PCM interpretation or a writer change. Keep
the retail-value store opt-in and unchanged. Do not interpret any bridge or
PCM row unless the target VI anchors and positive controls are live.

## Competing hypotheses and discriminator

- **H1 — C88=1 is the route-specific blocker:** the unset arm reaches title
  and/or hangar with live controls while the C88=1 arm remains at VI 640. The
  callback arm is not yet runnable; the next boundary is the C88 route branch.
- **H2 — C88=1 is required for the route:** the C88=1 arm reaches a target
  anchor while unset remains at VI 640, with matching preflight and service
  controls. The callback arm is phase-valid and can be rerun as the next M5
  unit.
- **H3 — common route/focus failure:** both arms remain at VI 640 despite
  `input=ok visual=ok`, post-640 host Start edges, and 24/24 `s2006-svc`
  entry/exit controls. No PCM conclusion is allowed; the next unit must fix
  the route or focus wrapper.
- **H4 — s2039 was intermittent:** both arms reach their target anchors with
  the required controls. The prior H4 result was not reproducible, and the
  callback-side PCM witness becomes the next unit.

The discriminator is one same-build table for both arms: preflight status;
width-relative host Start edges; VI transitions at `0x00790400` and
`0x006AB400`; `s2006-svc` entry/exit; `reapplyDisplayMode` writer and
raw-gate/gate-1 rows; and real `audtask-dispatch` rows. A target bridge row
is useful only after those controls pass. Concurrent GUI arbitration remains
a possible H3 confound and must be reported, not silently treated as a C88
result.

## Commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp

set +e
env REGRESS_SECS=150 REGRESS_INTERVAL=0.6 REGRESS_REQUIRE_VISUAL=1 \
REGRESS_KEYS='640@1:start 640@3:start 640@5:start 640@7:start 640@9:start 640@11:start 640@13:start 640@15:start 640@17:start 640@19:start 640@21:start' \
REGRESS_LABEL=s2040_c88_one \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2040_c88_one 150 > scratch/agent/s2040_c88_one_driver.log 2>&1 &
p_one=$!
env -u ROGUESQ_M5_C88_VALUE REGRESS_SECS=150 REGRESS_INTERVAL=0.6 REGRESS_REQUIRE_VISUAL=1 \
REGRESS_KEYS='640@1:start 640@3:start 640@5:start 640@7:start 640@9:start 640@11:start 640@13:start 640@15:start 640@17:start 640@19:start 640@21:start' \
REGRESS_LABEL=s2040_c88_unset \
ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2040_c88_unset 150 > scratch/agent/s2040_c88_unset_driver.log 2>&1 &
p_unset=$!
wait $p_one; r_one=$?
wait $p_unset; r_unset=$?
print "c88_one_rc=$r_one c88_unset_rc=$r_unset"
```

After both runs, use only bounded `grep -c`, `grep -n ... | head/tail`,
`tail`, and `verdict.json` reads. Compare target phases only; a scorer FAIL
caused by a final-key heuristic does not override live anchors and controls.
