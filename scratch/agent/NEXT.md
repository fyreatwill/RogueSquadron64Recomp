# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## Single work unit

**2nd confirming run of item -422** (post-sec2 menu-return is input-gated).

s670 got ONE recovery-active, sec2-reaching, pulse-fired attempt (single-
source): a synthetic Start pulse ~8s after `[overlay] start-match: section 2`
kept thr12 (id=13, `entry=0x800495FC`) alive for >1000s post-sec2 with **zero**
`[thr-destroy] id=13`, **zero** `start-match: section 3` return, and **zero**
packTlut — vs the s669 baseline's unforced ~195–200s teardown+menu-return
under identical product defaults (headers restore ON, drop OFF) with NO
post-sec2 input. Iron rule 4 requires a 2nd independent line before this enters
CURRENT-TRUTH as CONFIRMED rather than SUPPORTED/single-source.

## Command

```bash
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
env BUDGET_S=2400 TARGET_PULSED=2 \
  zsh scratch/agent/s670_postsec2_pulse_freeroll.sh \
  > scratch/agent/s670_logs/wrapper2.stdout 2> scratch/agent/s670_logs/wrapper2.stderr
```

Run in-session with a bounded wait loop (`zsh scratch/agent/s670_wait.sh`,
grep for `VERDICT` in the wrapper stdout, repeat in ~580s chunks — plain
`bash` scripts need approval under this session's allowlist, `zsh:*` does
not). **Do NOT queue this to soak_queue/** — one successful attempt (hangar-
sel ~215s + recovery-silent rerolls ~266s each + the pulse-hold observation
itself ~1000–1400s wall time, inflated by per-iteration `screencapture` under
heavy `[thr-resume]` logging) blows past the soak queue's 600s hard cap long
before a verdict lands.

The scoring bug from s670 (score_log read `run.log` for the `[sec2-pulse]`
marker, which only appears in `launcher.stdout`; thr13c/d search wasn't
scoped to `>= sec2_ln`) is **already fixed** in
`scratch/agent/s670_postsec2_pulse_freeroll.sh` — no further repair needed
before this run.

## Outcomes

- **A)** thr12 survives >500s post-sec2 again with 0 section-3 return / 0
  packTlut → **H-menu-return-input CONFIRMED** (2/2). Next: test whether ANY
  input (not just Start) delays teardown, whether it's delay-vs-indefinite
  (extend POST_PULSE_HOLD_S further), and whether packTlut ever fires given
  enough held-alive time.
- **B)** thr12 dies at ~195–200s post-sec2 despite the pulse (baseline shape
  returns) → **H-menu-return-input REFUTED**; s670's single sample was noise
  (e.g. the pulse landed during a frame the guest wasn't polling input, or
  attempt-5-specific timing) — fall back to guest-side teardown instrumentation
  (find the `osDestroyThread` call site for thr12 and its caller condition).
- **C)** recovery-silent every attempt again (as happened 3/4 times in s670)
  and budget exhausts before a 2nd pulsed attempt → INCONCLUSIVE, re-run with
  higher `MAX_ATTEMPTS`/`BUDGET_S`; this is expected noise, not evidence
  either way (recovery-active rate is historically ~1/3, matches s670).

Do NOT re-derive Arm A (FS_PIPE_INJECT reach) — s670 already closed it via
offline reanalysis of existing s668/669 data
(`scratch/agent/s669_postsec2_offline_score.py`): synth climbs, rdpFs stays
flat, **H-inject-misses-mission REFUTED**. The rdpFs plateau itself (item
-421) is a separate open mechanism from -422's menu-return and is not what
this work unit is testing.

## Do NOT

- Productize the -422 input-pulse mechanism (single-source; needs 2nd confirm
  first).
- Productize `DROP_GARBAGE_CIMG` (s666 REJECTED).
- Re-soak thr11d multi-hold rate (-419 CLOSED).
- Re-prove outdoor present post-sec2 (s669 CLOSED) or re-run Arm A (s670 CLOSED
  via offline reanalysis).
- Chase packTlut SIGBUS (-373) until the loader actually fires (still 0).
