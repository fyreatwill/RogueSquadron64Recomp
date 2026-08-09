# NEXT work unit

HYPOTHESIS-ID: m3-dod-craft-stick-hold

## s572 recap (read this first)

**Item -7 soak fold — leave survives; hangar-menu stickiness; -338 2nd occ.**

- Loop ran `s571_item7_craft_stick_hold_retry` →
  `scratch/s73_post_a_scene/s571_item7_retry_20260809-145351/`.
- Menu clean through SELECT YOUR CRAFT. Leave Start applied; **hold-iter 12** death (not
  hold-iter 1). Stick sr at hold_10; 11 hold_*.png.
- Crash: `last-guest-pc=0x8000afa0` / `beginFrameDLChunk+46800` — **item -338 2nd occ**
  (moderate confidence; do not chase until 3rd).
- Stack at death: still `runHangarSelectionFrame` ← `runHangarMenuFromOverlay` ←
  `menuOverlayInit`. hangarbay-entry n=1000. **0 mission* log tags entire run.**
- `fs` plateau 4355; thr-resume-skip=0. hold_04..11 frozen identical MD5 (stick no pixels).
- Item -7 partial PROBED: leave can survive + stick marks fire, but path is **not in-mission**.

## This iteration's work unit

**Item -7 gate pivot — leave→mission transition: does craft-leave Start ever enter mission code?**

s572 shows stick hold is blocked by hangar-menu stickiness + graphics stall, not by missing
stick marks. Discriminate whether mission entry is (a) never attempted, (b) attempted but
fails silently, or (c) reaches a frame function we do not log.

### Hypotheses
- H1: Post-leave control never leaves hangar menu (`runHangarSelectionFrame` / hangar overlay
  only) — mission overlay never DMA'd, no mission frame function runs → need state-machine /
  confirm-key / overlay-dispatch fix before DoD stick hold is meaningful.
- H2: Mission entry is attempted (overlay load / mission init / cutscene frame) but aborts or
  returns to hangar within seconds — log will show a brief mission tag then hangar resume.
- H3: Mission runs under a name we do not log; hangar symbols on crash stack are callers only —
  need positive control that a known mission symbol fires during a real mission path (or
  decomp-named mission frame JAL targets instrumented).

### Discriminating measurements (batch in ONE build/run)
1. Offline first (no build): from s572 `run.log`, enumerate every `[overlay]` line and any
   function-entry tags after the leave Start wall time; confirm 0 mission-side hits (already
   true for mission* strings — extend to overlay section idx / known mission ROM ranges).
2. If offline is inconclusive for H3: one instrumented run with entry counters on
   `runHangarSelectionFrame` (rate-unlimited after leave) + best-known mission frame/init
   symbols from decomp/`syms` (batch all; positive control: hangar counter must keep firing
   pre-leave).
3. Crash/stall outcome secondary — do not chase -338.

### Exact commands
```bash
# Offline overlay + post-leave function tags (prefer before any build):
RUNLOG=scratch/s73_post_a_scene/s571_item7_retry_20260809-145351/run.log
grep -n '\[overlay\]' "$RUNLOG"
# Find leave wall-time from console / first after_p1; count hangarbay-entry after that.

# Mission symbol candidates (decomp / syms — pick real names, do not invent):
#   grep -E 'mission|Mission|Chapter|levelLoad|startLevel' syms/ docs/ companion decomp

# If instrumenting: put counters in fixup or existing ROGUESQ_LOG_* only; one cmake + one
# run_mission_keys leave+HOLD_S=20 is enough (full 60s not required for entry proof).
```

### Expected outcomes
- H1: document leave→hangar-only as CURRENT-TRUTH; reframe item -7 next step as mission-entry
  state-machine audit (systematic, not crash chase).
- H2: name the aborting function / missing overlay; that becomes the next fix work unit.
- H3: expand log coverage with positive control; re-run once.

### Do NOT
- Chase 0x8000afa0 / beginFrameDLChunk from this leave path (wait 3rd occ of -338).
- Chase 0x80010b7c (s571 noise).
- Blind HOLD_S=60 stick retries without mission-entry evidence (stick marks already proven).
- Reopen M5 (due s573+ only).
- Resume freelist/sibling residual scans (exhausted s569).
