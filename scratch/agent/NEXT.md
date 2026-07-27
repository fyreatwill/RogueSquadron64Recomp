# NEXT work unit — M3: 60s hangar-flight hold + craft stick input

s75 closed leave-key isolation: **single Start** from stable SELECT YOUR CRAFT enters
hangar-flight by +2–4s (`PROBE_MODE=start_only`). Next: M3 definition-of-done — 60s of
in-mission/hangar-flight rendering with craft response to synthetic input.

## Competing hypotheses (for the hold)

| ID | Claim | If true, we will see… |
|----|--------|------------------------|
| H1 | Hangar-flight can hold 60s with content if we just wait longer | start_only + grace≥60: content frames through t+60 post-leave; fs keeps advancing |
| H2 | `fs` freezes ~6–10s post-leave (present starvation / fullSync stall) | content ~6–9s then black; fs plateaus (s75: 3360); process may stay alive |
| H3 | Process dies (MetalFramebuffer SIGSEGV / transition SIGBUS) before 60s | CRASH/SIGSEGV in log; wall time of death <60s post-leave |
| H4 | Craft responds to stick once in hangar-flight | stick pulses change camera/craft pose across snaps at fixed post-leave marks |

## Discriminating measurement (one soak)

Extend `run_mission_keys.sh` (or a thin wrapper) so that after start_only leave:

1. Confirm leave (title-yellow → 0 + visual hangar-flight) within first 5s post-Start.
2. Fire stick keys at +10s, +25s, +40s post-leave (winctl keycodes for left/right or up/down).
3. Snap every 1s for ≥60s post-leave with unique tags `hold_NN`.
4. Same env as s75 (LLE four knobs + LOG_RUNNER_ALL + thr-resume + ost-wb).

```bash
# Preferred: edit script once to add HOLD_S=60 + stick schedule after start_only leave,
# then one run. Or wrapper that reuses the existing path and only extends grace + sticks.
env PROBE_MODE=start_only HOLD_S=60 zsh scratch/s73_post_a_scene/run_mission_keys.sh hold60 65 12
```

Offline:
- title-yellow on pre-leave vs hold_01..05 (positive control leave happened)
- content vs black file-size / visual on hold_10,20,30,40,50,60
- fs max + whether it advances after leave
- thr-resume bad=0; CRASH stack if death
- visual craft pose change across stick marks (H4)

### Outcomes

- **H1 + H4:** M3 nearly done — document phase timeline; note texture garbage; close hold.
- **H2 without death:** next unit = present/`fs` freeze diagnosis (scoped counters post-leave).
- **H3:** next unit = that crash class (MetalFramebuffer or SIGBUS) with same-run control.
- **H4 false (no craft motion):** input path / menu-vs-flight control ownership — separate unit.

## Do not

- Re-isolate Start path (S1 closed s75).
- Re-open s72 writeback unless thr-resume bad=1.
- Cross-run A/B on animating hangar-flight for visual knobs.
- Start M4 outdoor missing-func until M3 hold is attempted once.
