# NEXT: G3 render match vs retail angrylion, front-end screens (title, level select, mission briefing)
HYPOTHESIS-ID: g3-render-match-frontend

s6778 closed the in-mission menus: the pause menu matches, and the debrief text and emblem match. The oracle now copies fb dumps on the emulator
thread (no more torn dumps). Screens not yet render-compared: the title screen (VI width 1024), the level select (512, bases
6AB000/656000), and the mission briefing fly-over (640).
Hypotheses:
- H-match: each screen's best pairs fall inside the same-run median band (flight range d 4-9).
- H-diff: a specific element differs (text, hologram, overlay, combiner) -> localise it with the worst pairs, then find the root cause.
- H-phase: high d only during animated transitions (hologram spin, fades).
Work unit (one run per screen group, all dumps emu-thread):
1. Reuse the mission-17 route (tools/g3_mission/run.sh LEVEL 16, s6771/s6778 recipe: ARM=20 DWARM=30 CAP0=<early>) with
   retail --fb-dump windows armed on width 1024 (title) and 512 (level select) from early t: set FARM to 0 and
   add dumps at those widths (run.sh currently dumps width 512 only, so add an NDUMP1024 option or pass EXTRA args).
   Port CAP0 early (~8 s) so the title and level-select captures exist.
2. g3_oracle_match.py per screen with its own --w and --bases (logged origin0 & ~0xFFF); same-run median control,
   plus a mismatched-pair positive control (title dump vs level-select capture must score well above the median).
Discriminating outcome: per-screen best-pair d vs median, plus the worst pairs eyeballed.
