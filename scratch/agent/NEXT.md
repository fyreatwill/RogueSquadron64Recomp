# NEXT work unit — M3: gate the thr-resume `bad=1` UAF resume (SIGBUS)

s83: root-caused and guarded the `evalCubicSplineAtTime` NaN abort (0/0
division on a zero-width spline interval — see `N64Recomp/fixup_game_funcs.py`).
Guard never fired in 2 soaks (0/2) — unvalidated, not confirmed, but a real
fix by code inspection. With that deterministic assert no longer winning the
race, 2 soaks (`scratch/s73_post_a_scene/spline1/`, `spline2/`) died from two
**different** crashes instead:

- **spline1** (hold+3s): SIGSEGV inside Apple's `Metal.framework` shader
  compiler (`MTLCompilerFSCache` hash-table rehash). No source on our side.
- **spline2** (hold+12s): SIGBUS in `resume_thread_tagged` →
  `LightweightSemaphore::signal`, on a `[thr-resume] live=0 ... bad=1`
  context — same UAF-shaped class as s70–s72.

This work unit targets the SIGBUS, because it has a known, already-
instrumented site: `lib/N64ModernRuntime/ultramodern/src/threads.cpp:198-238`
computes `bad = (t==nullptr)||(ctx==nullptr)||!live` and logs it every call,
but **never gates on it** — line 237 (`t->context->running.signal();`) runs
unconditionally right after the `bad=1` log line. The detector exists; the
skip does not.

## Competing hypotheses

| ID | Claim | If true, we will see… |
|----|--------|------------------------|
| U1 | Skipping resume on `bad=1` is safe and stops the SIGBUS | `[thr-resume-skip]` fires ≥1; `bad_total` stays nonzero (condition still occurs); no SIGBUS this run |
| U2 | Skipping corrupts scheduler state (thread never resumes, queue wedges) | process hangs / stalls instead of crashing; `[lle task]` count stops advancing after a skip |
| U3 | This SIGBUS is too rare/nondeterministic to validate in 1-2 runs | 0 `bad=1` occurrences this run (no positive control) — inconclusive, not refuted |
| U4 | The Metal SIGSEGV (unrelated, spline1) recurs and masks this test | process dies via Metal SIGSEGV signature (see s83) before reaching a `bad=1` case |

## Discriminating measurement (ONE build)

Edit `lib/N64ModernRuntime/ultramodern/src/threads.cpp` — in
`resume_thread_tagged` (~line 209-237), after the existing `bad`
computation and log line, add: if `bad` and `ctx != nullptr` (the null-ctx
case already has its own FATAL log path), skip the `t->context->running.signal()`
call and log `[thr-resume-skip] n=%u tag=%s id=%d` instead. **This is `lib/`
— run `./submodule-patches/export.sh` and commit the refreshed patch in the
SAME iteration, or it is lost at the next reset.**

```bash
# after edit + export.sh:
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
cmake --build build -j8
env PROBE_MODE=start_only HOLD_S=30 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh thrgate1 0 12
# offline:
grep -c 'thr-resume-skip' run.log   # positive control: >=1 with bad_total>0
grep -c 'CRASH' run.log             # 0 desired; if 1, check signature — SIGBUS gone? new class?
grep -a '\[lle task\]' run.log | tail -5   # still advancing post-skip (rules out U2 hang)
```

Run twice if the first run shows 0 `bad=1` occurrences (U3) — do not
conclude from a run with no positive control.

### Outcomes
- **U1:** SIGBUS gone, tasks keep advancing → re-check spline guard (item 3
  below) and/or retry the Metal SIGSEGV (item 2) before HOLD_S=60.
- **U2:** narrower gate — only skip the `running.signal()`, not the whole
  resume bookkeeping; or investigate why `bad` contexts still get scheduled
  at all (upstream fix instead of a resume-time patch).
- **U3:** 3rd consecutive inconclusive run on this hypothesis → stop, go
  BLOCKED or pick the Metal SIGSEGV instead per budget rule.
- **U4:** unrelated to this fix; check Metal SIGSEGV reproducibility
  separately (next-steps item 2 in CURRENT-TRUTH), don't conflate the two.

## Do not
- Re-litigate G1–G4 (last-drawn gate) or the s83 spline guard — both stand.
- Treat 0 `bad=1` this run as "fixed" — it means untested, per U3.
- Spend more than 3 consecutive iterations chasing this one hypothesis
  without a discriminating result (ITERATION.md rule 8).
