# NEXT work unit

HYPOTHESIS-ID: m3-dod-craft-stick-hold

## s570 recap (read this first)

**M5 lead recheck → H2 (zero new leads).** Offline survey only.

- SOAK-RESULTS: no post-s520 audio crash signatures (only historical s348 noise).
- Hangarbay soaks s565–s569: `real_ucode=0` as designed; only known
  `[audio-wait-pump-stall]` ceiling diagnostic (s327, not a lead).
- Stubs still intentionally in force: C88 `reapplyDisplayMode` force-zero;
  `ROGUESQ_AUDIO_UCODE` default off; aspMain Broke unused.
- Cadence: last checked s570, due s573+.
- DIRECT residual freelist/sibling campaign remains exhausted (item -348 CLOSED 2/2).

## This iteration's work unit

**Item -7 — M3 DoD body: craft-stick HOLD_S=60 from SELECT YOUR CRAFT.**

Goal: leave the menu into the post-craft-select window, hold 60s with stick pulses at
10/25/40, capture phase timeline (VI width / origin / content / fs plateau / crash).
This is the documented M3 definition-of-done *body* probe, not a crash chase.

### Hypotheses
- H1: Process reaches SELECT YOUR CRAFT and survives full HOLD_S=60 with stick marks;
  phase timeline is documentable (VI + content frames). M3 DoD body data lands even if
  not yet "in-mission."
- H2: Residual S1 `fs` freeze (~3769–3872 plateau from prior notes) still stalls graphics
  task submission during the hold — process alive but `stalled=1 pairs=0` / frozen `fs`.
- H3: Crash or early death before or during hold on a catalogued family (file breadcrumb;
  do not open a reactive chase unless a *new* last-guest-pc appears ≥2 times).

### Discriminating measurements (one recipe, one run)
1. Process alive through hold end? (exit code / SIGKILL-at-timeout vs CRASH)
2. VI width/origin transitions during hold (grep `[phase]` / `vi_width` / origin)
3. Stick marks applied? (driver `[keys]` / stick lines in launcher log, not only run.log)
4. Graphics stall? (`[vi-fs-decision] stalled=1` continuous; RDP `fs` frozen)
5. Crash signature if any: `last-guest-pc` + `pc-symbol` vs catalogued families

### Exact commands
```bash
# Prefer the established mission-keys driver with start_only + stick schedule.
# Run from repo root; ROM must be in build/.
mkdir -p scratch/agent/soak_results/s571_item7_craft_stick_hold
cd scratch/s73_post_a_scene

# Full passive breadcrumb set is free; keep audio logs off unless needed.
export PROBE_MODE=start_only
export HOLD_S=60
export STICK_SCHEDULE="10:sr 25:sl 40:su"
export HOLD_TICK_S=1
export CAPTURE_TICK_S=1
# Optional: arm hangarbay/phase logs if not already in the driver defaults
export ROGUESQ_LOG_HANGARBAY_ENTRY=1
export ROGUESQ_LOG_RUNNER=1

# Grace/stable args match run_mission_keys.sh convention
zsh run_mission_keys.sh s571_item7 5 12

# Post-run (do not cat full log):
#   grep -E '\[phase\]|vi_width|stalled|\[keys\]|stick|CRASH|last-guest-pc' \
#     scratch/s73_post_a_scene/s571_item7/run.log | head -80
#   ls scratch/s73_post_a_scene/s571_item7/hold_*.png | head
```

Alternative if `run_mission_keys.sh` path is stale: clone
`scratch/agent/s569_sibling_residual_gap_confirm_retry.sh` schedule but switch to
`PROBE_MODE=start_only HOLD_S=60` and stick schedule via `tools/probe.sh` if it
supports sticks — verify with `grep STICK tools/probe.sh` first; if not, use
`run_mission_keys.sh`.

### Expected outcomes
- H1: document phase table in CURRENT-TRUTH item -7 / PORTING-STATE; M3 DoD body
  advanced (still not full DoD until 60s *in-mission* craft response).
- H2: confirm fs freeze still present; file as standing M3 stall (s176–s183 family),
  do not re-open thr-resume-skip.
- H3: catalog crash; if new PC and 2nd occ later, open -349; else breadcrumb only.

### Do NOT
- Reopen M5 (due s573+ only, or on a new audio signature).
- Chase item -347 / single-occ breadcrumbs.
- Spend the session on another freelist residual scan (campaign exhausted).
- Cross-run A/B on animating scenes; one hold window is the measurement.
