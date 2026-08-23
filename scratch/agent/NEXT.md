# NEXT work unit (s2194) — isolate individual logging categories

HYPOTHESIS-ID: m5-a1-retail-writer-census

## Work unit

Run the self-contained four-arm, phase-gated category-isolation test from the
repo root. All arms use the same qualified image/LLE recipe and writer
control. `quiet` leaves optional logs unset; `slot` enables only
`ROGUESQ_LOG_SLOT_DISPATCH`; `event` enables only
`ROGUESQ_LOG_EVENT_WIRING`; and `audio` enables only
`ROGUESQ_LOG_AUDIO_RETURN`. The watchdog kills an arm with SIGKILL after the
second-origin phase plus 15 seconds, on a 180-second deadline, and exits
nonzero if an arm logs a crash marker.

Exact command:

```sh
zsh scratch/agent/run_s2194_m5_log_category_ab.sh
```

Parse the complete table after the run:

```sh
for arm in quiet slot event audio; do
  echo "=== $arm ==="
  grep -a '\[m5-writer-parity-control\]' "scratch/agent/s2194_m5_log_category_ab/$arm.log" | wc -l
  grep -a '\[phase\] vi_width=640' "scratch/agent/s2194_m5_log_category_ab/$arm.log"
  grep -a '\[m5-writer-parity\]' "scratch/agent/s2194_m5_log_category_ab/$arm.log"
  grep -a -E '\[(CRASH|ABORT)\]|\[last-guest-pc\]|\[pc-symbol\]' "scratch/agent/s2194_m5_log_category_ab/$arm.log" | tail -12
done
```

## Competing hypotheses and discriminator

- H-SlotCategoryBoundary: `slot` reaches `0x00696600`, remains alive while
  `quiet` crashes, or otherwise changes the post-first-origin boundary while
  its controls pass.
- H-EventCategoryBoundary: the same discriminator selects `event`.
- H-AudioCategoryBoundary: the same discriminator selects `audio`.
- H-NoIndividualCategoryBoundary: all four arms pass controls and the first
  640 phase but miss `0x00696600`; no individual category explains the
  grouped route result, so the grouped interaction or another source remains
  open.
- H-CoverageFailure: any arm lacks its writer control or first 640 phase;
  reject the comparison rather than treating missing rows as nulls.

The discriminator is one same-iteration table per arm containing positive
control count, both 640 origins, termination/last-guest-PC outcome, optional
log-positive counts, and all six target writer-PC sets at each observed
origin. Do not add a port guard, mitigation, task rewrite, or audio-default
flip.
