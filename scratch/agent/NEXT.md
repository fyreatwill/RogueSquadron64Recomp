# NEXT work unit

HYPOTHESIS-ID: m5-lead-recheck

## s569 recap (read this first)

**Item -348 FULLY CLOSED 2/2.** SIBLING_PTR DIRECT residual same-base gap class (218 sites).

- s568 queued confirm: WEAK item-306 (`setByteAcrossEntryList+176`/`0x800aafa8`, hangarbay n=0).
- s569 manual retry: hangarbay **n=3000**, full ~300s rc=0, 0 CRASH, 0 sibling-ptr-write fires.
- DIRECT residual campaign exhausted (freelist R/ATTR EMPTY dual-scan + SIBLING residual CLOSED).
- Breadcrumb re-tally: -332 still 2 occs (watch); no single-occ escalation.

## This iteration's work unit

**M5 audio lead recheck** (strategic priority #2; last checked s520, due s523+, now s569+).

M5 is DONE/CLOSED (s297-376). Goal is NOT to reopen closed steps — survey whether any
**genuinely new** audio lead exists that would justify reopening de-stubbing work.

### Hypotheses
- H1: New audio-related crash family or stub/trap still in force that M5 plan never closed →
  file a new item and plan one de-stubbing step.
- H2: No new lead (stubs only where intentionally left; no new audio crash signatures in
  SOAK-RESULTS/recent logs) → document "rechecked s569, zero new leads, due again s572+",
  pivot to M3 DoD body item -7.
- H3: An existing closed M5 step regressed (e.g. waitForMusyX / voice-array / slot reaping
  reappearing in hangarbay soaks) → re-open only that step with a same-run positive control.

### Discriminating measurements (batch offline — no game run required unless H3)
1. Grep CURRENT-TRUTH + PORTING-STATE tail + SOAK-RESULTS for audio/MusyX/voice/slot/MORT
   crash signatures newer than s520.
2. Survey active stubs: `src/main/main.cpp` M_AUDTASK route, fixup audio-engine gates,
   any `ROGUESQ_*AUDIO*` envs, `aspMain` stub, waitForMusyX traps — compare to
   `docs/M5-AUDIO-PLAN.md` closed-state claim.
3. If (1)+(2) empty → H2. If a live stub contradicts the plan's "intentionally left" list → H1.

### Exact commands
```bash
# 1) new audio crash signatures since s520
grep -nE 'MusyX|musyx|waitForMusyX|voice-array|audio.?slot|M_AUDTASK|MORT|aspMain' \
  scratch/agent/SOAK-RESULTS.md | tail -40
grep -nE 'MusyX|waitForMusyX|voice|audio.?slot|M_AUDTASK' PORTING-STATE.md | tail -30

# 2) stubs still in force
grep -nE 'M_AUDTASK|audio|MusyX|aspMain|waitForMusyX' src/main/main.cpp | head -40
grep -nE 'audio|MusyX|0x800A0F50|initMusyX' \
  ~/Documents/Tools/N64Recomp/fixup_game_funcs.py | head -40
ls docs/M5-AUDIO-PLAN.md docs/PROJECT-OVERVIEW.md
```

### Expected outcomes
- H2 (most likely): update CURRENT-TRUTH "last checked s569, due s572+"; NEXT → item -7
  M3 DoD body (`PROBE_MODE=start_only HOLD_S=60`).
- H1: open item -349 with one concrete de-stubbing step + soak recipe.
- H3: same as H1 but scoped to the regressed closed step.

### Do NOT
- Re-run closed M5 de-stubbing steps without a new signature.
- Chase item -347 / single-occ breadcrumbs.
- Re-open packing DEFERRED float sites without same-run bad_ptr evidence.
- Start item -7 in the same iteration as the M5 survey (one work unit).
