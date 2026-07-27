# NEXT work unit — M3: sane-width gate on last-drawn / mode-3 (B2 causal)

s81 offline: intermittent black = `ROGUESQ_VI_FOLLOW_DRAW=3` presenting wild
`g_rs64_last_drawn_fb` (w=1..257). Detail:
`scratch/s73_post_a_scene/BLACK1_ANALYSIS.md`.

## Competing hypotheses (after gate)

| ID | Claim | If true, we will see… |
|----|--------|------------------------|
| G1 | Wild last-drawn is causal for black | `[last-drawn-skip]` fires; black snaps rare/gone; 0x656/0x6AB flips dominate hold |
| G2 | Gate correct but too late / present still broken | skip fires; black duty-cycle unchanged; vi-follow still wrong |
| G3 | Sane width set too strict | skip fires on legitimate content; craft/hangar go black or pad-only |
| G4 | Black is game clear independent of last-drawn | skip fires; last-drawn stays 0x656/0x6AB; snaps still black |

## Discriminating measurement (ONE build)

Gate in **both** places (batch):
1. `rt64_framebuffer_renderer.cpp` last-drawn atomic update — reject
   `addr==0` or width ∉ {320,512,640,1024} (keep previous last-drawn).
2. `rt64_present_queue.cpp` mode-3 override — same reject; do not REGISTER
   wild keys.

Log always-on rate-limited:
```
[last-drawn-skip] #N addr=0x.. w=.. (why)
[vi-follow-skip]  #N addr=0x.. w=..
```
Positive control: early 640 attribution + title must still show content;
skip must fire ≥1 during post-leave if G1/G2 path is real.

```bash
# after edit under lib/rt64:
./submodule-patches/export.sh
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
cmake --build build -j8
env PROBE_MODE=start_only HOLD_S=30 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh ldgate1 0 12
# offline: black% of hold_*.png; grep -c last-drawn-skip run.log;
# vi-follow last drawn w= distribution
```

### Outcomes
- **G1:** keep gate; HOLD_S=60 craft stick (M3 DoD).
- **G2:** instrument present path / matcher next.
- **G3:** widen allowlist carefully (measure which skipped w had content).
- **G4:** present-luma / RDRAM clear probe.

## Do not
- Re-analyze vifs1 offline for B1–B4 (done s81).
- Treat empty=0 as continuous present health.
- Re-open synthetic FIRE / RDP-fs plateau as present root.
