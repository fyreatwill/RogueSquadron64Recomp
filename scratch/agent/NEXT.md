# NEXT work unit

HYPOTHESIS-ID: m3-dod-craft-stick-hold

## s571 recap (read this first)

**Item -7 M3 DoD body — leave dies before stick marks.**

- Recipe: `PROBE_MODE=start_only HOLD_S=60 STICK_SCHEDULE="10:sr 25:sl 40:su"` via
  `scratch/s73_post_a_scene/run_mission_keys.sh s571_item7 5 12`.
- Menu path clean through SELECT YOUR CRAFT (12 stable snaps, non-black craft_stable).
- Leave Start applied; process gone at **hold-iter 1** (0s into hold). Stick marks **never
  applied**. hold_*.png = 0.
- Crash: `last-guest-pc=0x80010b7c` / `findOrCreateMaterial+1704` — **known background-noise
  guest PC** (s553 etc.; pc-symbol unstable). Do **not** open a reactive chase.
- `fs` plateau 4346 pre-death; thr-resume-skip=0. Phase table in PORTING-STATE s571 /
  CURRENT-TRUTH item -7.
- Retry enqueued: `scratch/agent/soak_queue/s571_item7_craft_stick_hold_retry.sh`.

## This iteration's work unit

**Item -7 retry — land one clean HOLD_S=60 with stick marks (or confirm leave-path noise rate).**

### Hypotheses
- H1: Intermittent 0x80010b7c does not fire; process survives full 60s hold; sticks land at
  10/25/40; phase/content timeline documentable → item -7 body data lands.
- H2: Same early leave-path death on 0x80010b7c (or same family) again → leave-path survival
  is the real M3 gate; file recurrence count, still no reactive single-crash chase unless a
  *new* last-guest-pc appears ≥2 times.
- H3: Survives hold but fs freeze / no craft response in PNGs → DoD body partial (timeline
  yes, "in-mission craft responds" still no).

### Discriminating measurements
1. Console: `[keys] stick` count (expect 3) + hold_*.png count (~60).
2. Process exit: SIGKILL-at-timeout vs CRASH; if CRASH, last-guest-pc.
3. Phase + fs plateau during hold (grep `[phase]` / last fs values).
4. Offline: hold_10 vs hold_09 / hold_25 vs neighbors for pose change (only if H1).

### Exact commands
```bash
# Prefer consuming a loop-run soak first:
tail -5 scratch/agent/SOAK-RESULTS.md
# If s571_item7_craft_stick_hold_retry is already in SOAK-RESULTS, fold it and stop
# (or re-enqueue if WEAK/early death without reaching craft).

# Manual / same-recipe if queue empty:
mkdir -p scratch/agent/soak_results/s572_item7_craft_stick_hold
cd scratch/s73_post_a_scene
env PROBE_MODE=start_only HOLD_S=60 STICK_SCHEDULE="10:sr 25:sl 40:su" HOLD_TICK_S=1 \
  CAPTURE_TICK_S=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_RUNNER=1 \
  zsh run_mission_keys.sh s572_item7 5 12 \
  2>&1 | tee ../../agent/soak_results/s572_item7_craft_stick_hold/console.txt

# Analyze (do not cat full log):
#   grep -E '\[phase\]|stick|CRASH|last-guest-pc|hold done|game process gone' \
#     console.txt s572_item7/run.log | head -80
#   ls s572_item7/hold_*.png | wc -l
```

### Expected outcomes
- H1: document full hold phase table + stick PNG notes; mark item -7 body PROBED
  (full M3 DoD still needs in-mission craft response).
- H2: bump leave-path 0x80010b7c co-occurrence; keep item -7 OPEN; enqueue another retry
  or pivot after 3 consecutive leave-deaths on the *same* noise PC without new signal.
- H3: timeline yes, animation/response no — file fs freeze standing note, no thr-resume reopen.

### Do NOT
- Open a findOrCreateMaterial / 0x80010b7c guard chase from a single (or second same-PC) hit.
- Reopen M5 (due s573+ only, or on a new audio signature).
- Resume freelist/sibling residual scans (campaign exhausted s569).
- Cross-run A/B on animating scenes.
