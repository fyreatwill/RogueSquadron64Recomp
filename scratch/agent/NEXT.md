# NEXT work unit (s2041)

HYPOTHESIS-ID: m5-callback-side-pcm-witness

## Work unit

Build once, then run one fresh `ROGUESQ_M5_C88_VALUE=1` arm using forced LLE,
opt-in Factor 5 audio, spin yield, `ROGUESQ_LOG_ALL=1`, and the eleven
width-640 Start schedule. This is the callback-side PCM witness. Keep the
retail-value writer unchanged and treat the C88 value as an opt-in route arm.
Do not interpret bridge or PCM rows unless the run has the title and hangar VI
anchors plus the `s2006-svc` positive control and live gate/task controls.

## Competing hypotheses and discriminator

- **H1 — upstream-valid PCM:** phase-valid `[pcm-bridge]` rows carry nonzero
  bytes and the paired `pcm-sanity` rows include `all_zero=0`. The task/image
  path is producing usable samples; the next boundary is AI/device ordering.
- **H2 — zero payload at the callback:** phase-valid bridge rows fire but have
  `nz=0`/all-zero payloads, with `pcm-sanity all_zero=1`. The callback is
  reached, but the task/image ABI or upstream sample production is wrong.
- **H3 — device-side boundary:** phase-valid bridge rows carry nonzero data,
  but all paired `pcm-sanity` rows remain zero. The remaining boundary is
  after the callback, in AI submission or device ordering.
- **H4 — guest submit/queue boundary:** title and hangar anchors, the 24/24
  service control, gate-one rows, and real audio-task rows are live, but no
  phase-valid bridge row appears. The guest AI-submit/queue path is the next
  boundary.
- **H5 — route failure:** the target anchors or positive controls are absent.
  This is a route result; it cannot select any PCM hypothesis.

The discriminating table is one run: verdict phase anchors and preflight;
`s2006-svc` entry/exit; phase-valid `reapplyDisplayMode` writer and raw/gate-1
rows; real `audtask-dispatch`; then paired `[pcm-bridge]` and `[pcm-sanity]`
rows. Counts and fields must be phase-scoped. A run-lifetime PCM null is not
evidence for H2-H4.

## Commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp

set +e
env REGRESS_SECS=180 REGRESS_INTERVAL=0.6 REGRESS_REQUIRE_VISUAL=1 \
REGRESS_KEYS='640@1:start 640@3:start 640@5:start 640@7:start 640@9:start 640@11:start 640@13:start 640@15:start 640@17:start 640@19:start 640@21:start' \
REGRESS_LABEL=s2041_pcm \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 \
ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2041_pcm 180 > scratch/agent/s2041_pcm_driver.log 2>&1
rc=$?
print "probe_rc=$rc"
```

After the run, read `scratch/agent/s2041_pcm/verdict.json` and use only
bounded `grep -c`, `grep -n ... | head/tail`, and `tail` on `run.log`. Record
the selected row table before interpreting any PCM result.
