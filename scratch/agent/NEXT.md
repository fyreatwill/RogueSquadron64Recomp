# NEXT work unit

HYPOTHESIS-ID: m3-dod-craft-stick-hold

## s577 recap (read this first)

**Item -7 breakthrough: REAL hangar exit + mission overlay load without force.**

Natural path: leave Start → state 3→5 → auto 5→6 (~195 case5 frames) → 2nd Start at
case-6 ACE94 → hangar-sel + state 6→8 → graceful-menu → VI 640@0x6A2900 →
`[overlay] start-match section 2 rom=0xA5D30` (`.ovl.mission`).

| Hyp | s577 |
|-----|------|
| H-edge1 host never sees 2nd RETURN | **REFUTED** (7 host START edge pairs) |
| H-edge2 prev sticks / new=0 | **REFUTED** (7 newbtn start_new=1 port 0) |
| Natural exit needs AC8C0 | **REFUTED** (case 6 ACE94 is the confirm) |
| H-edge4 port at AC8C0 | **partial** (logs port=98 = craft-bits byte; case6 same load saw Start) |

Instruments already in tree: `[host-start]`, `[newbtn]`, AC8C0 `port=`, prior hangar-exit tags.

## This iteration's work unit

**Item -7 body — characterize post-state-8 / mission entry after real hangar exit.**

### Hypotheses
- H-m1: mission overlay start-match is enough for in-mission rendering within ~30s of state 8.
- H-m2: post-exit enters cutscene/cinematic (section 4) before mission gameplay (VI/content).
- H-m3: post-exit hits the s178 graphics-task-submission stall (`stalled=1 pairs=0`).
- H-m4: hangar-sel val=0 means no craft / wrong selection and mission never fully arms.

### Discriminating measurements (prefer one longer run; instruments already on)
1. After hangar-sel / state 8: overlay section sequence, VI phases, fs counter still advancing.
2. PNG content after p2 (already size-changing in s577) — classify scene offline if needed.
3. Optional stick marks in hold after exit; `[missing-func]` / UnhandledJump / CRASH tags.
4. Positive control: hangarbay n≥900 + hangar-sel + graceful-menu + mission start-match all fire.

### Exact commands
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# Longer hold after double_start so post-mission window is visible
env PROBE_MODE=double_start HOLD_S=45 ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s578_item7_post_exit 5 12 \
  > scratch/s73_post_a_scene/s578_item7_post_exit_driver.log 2>&1

grep -E 'hangar-sel|state-write|graceful-menu|sentinel=0|\[overlay\]|\[phase\]|\[CRASH\]|UnhandledJump|missing-func|host-start.*edge|ACE94.*a_start=1' \
  scratch/s73_post_a_scene/s578_item7_post_exit/run.log | tail -80
```

### Expected outcomes
- H-m1: sustained non-black mission-like frames + fs advancing past exit → next = stick response.
- H-m2: section 4 / crawl-like VI before section 2 gameplay → map cutscene then mission.
- H-m3: fs freezes + stalled=1 → reopen s178 stall with exit as trigger (not reactive crash chase).
- H-m4: hangar-sel val always 0 and mission never arms → craft-selection write site.

### Do NOT
- Chase 0x8000afa0 / -338.
- Treat ROGUESQ_FORCE_CASE5_START as product fix (optional regression only).
- Reopen freelist residual / M5.
- Spend a session only on port=98 unless mission path is blocked by it.
