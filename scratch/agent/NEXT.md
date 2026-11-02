# NEXT: G3 render match vs retail angrylion, in-mission menus (pause menu, MISSION FAILED / debrief)
HYPOTHESIS-ID: g3-render-match-menus

Mission 3 closed in s6777: the pinned sim is identical up to t1775, and the split at t1776 is where song 1 ends on the audio clock. Pre-split render matches (d 3.9-6.4 against same-run medians of 44-64).
The per-mission sim+render sweep for missions 1-19 is complete. Screens not yet compared against retail: the pause menu and MISSION FAILED / debrief at
4:3 retail settings.
Hypotheses:
- H-match: menu frames match retail (d within the same-run median band, colour fit ~1-3% gain as in flight).
- H-menu-diff: specific glyphs/panels/backdrop differ (missing overlay, wrong combiner/alpha, text offset) -> localise
  with the worst pairs, then root-cause.
- H-phase: high d only from menu animation phase (blinking cursor/fades): same layout, differs at transition VIs only.
Work unit:
1. Route: mission 17 race (unsteered craft crashes ~12 s in -> MISSION FAILED in both arms, s6771 recipe in
   PORTING-STATE; grep '## Session 6771'). Add a Start press during flight for the pause menu in both arms
   (port key script / retail mupen input at the same tick).
2. `zsh tools/g3_mission/run.sh scratch/s6778 <level>` with the matching eep (tools/g3_eep_patch.py --set 0x31=16).
3. `tools/g3_oracle_match.py --dec shift` with the menu screen's own width and bases; same-run median control;
   positive control = one deliberately mismatched pair (flight dump vs menu capture) must score above the median.
Discriminating outcome: per-frame d of menu pairs vs same-run median + eyeballed worst pairs.
