# NEXT work unit (phase-5 E9 accounting boundary audit)

HYPOTHESIS-ID: m3-postsec2-parser-chain

The s793 fixed repeat reached the post-sec2/VI-1024 phase and showed
authoritative E9 dispatch (1,531) tracking `rdp-fullsync` (1,475), refuting a
handler/accounting loss for that arm. It did not capture the aligned-walker
total, so authoritative-advance loss versus a phase/co-gate remains open.
Perform one bounded source-and-log audit; do not add a mitigation or run a new
soak.

## Competing hypotheses

- H-authoritative-advance-loss: the aligned walker sees E9 commands that never
  enter the authoritative dispatch stream. Prediction: the phase-5 counters
  have different scopes or reset points, and a reconstructed aligned-vs-
  authoritative comparison remains materially divergent.
- H-phase-co-gate: the apparent loss is caused by task/phase gating rather than
  parser control flow. Prediction: the phase-5 logs show dispatch/fullSync
  records only in a gated task subset, with no single parser boundary dropping
  commands.
- H-measurement-scope: the prior aligned and authoritative counters are not
  comparable. Prediction: source locations, phase latches, or reset semantics
  differ; the discrepancy cannot be interpreted as a loss without new
  instrumentation.

## Discriminating measurement

Read the exact implementations and bounded s793 log windows for the aligned-E9,
authoritative-dispatch, and `rdp-fullsync` counters. Record each counter's
scope, reset point, phase latch, and task identity, then compare the first and
last phase-5 records. A shared scope with aligned E9 materially above
authoritative E9 selects H-authoritative-advance-loss; task-gated but internally
consistent records select H-phase-co-gate; mismatched scope/reset semantics
select H-measurement-scope. This audit must either identify the boundary or
explicitly leave it open; no mitigation is allowed.

## Exact commands

```sh
rg -n "e9-prov|e9-dispatch|rdp-fullsync|aligned|phase=5|PROBE_PHASE" \
  src lib ../N64Recomp/RecompiledFuncs tools scratch/agent/soak_results/s790_postsec2_reachability_20260812-233436/run.log
sed -n '49040,49120p' scratch/agent/soak_results/s790_postsec2_reachability_20260812-233436/run.log
sed -n '61620,61780p' scratch/agent/soak_results/s790_postsec2_reachability_20260812-233436/run.log
```
