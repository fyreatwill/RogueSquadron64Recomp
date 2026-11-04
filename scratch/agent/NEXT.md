# NEXT: read the s6865 post-removal arms, close s4563 removal, fold the true lvl10 hold
HYPOTHESIS-ID: s4563-dead-code-removal

Why: s6865 removed s4563 and the static compare held (2708/75, same names), but the runtime arms were unreported at stop.
First: tools/audit_hold_flight.py scratch/agent/m6/g1_lvl5s6865regen scratch/agent/m6/g1_lvl1s6865live, and read each summary + keys.log. If a summary is missing, the arm died with the session: rerun `zsh scratch/s6865/runs.sh` as a background job (needs scratch/s6865/rb; rebuild with scratch/s6865/link.sh if /tmp/s6865 survives, else tools/regen_replay.sh + regen_verify.sh first).
Hypotheses: H-dead (both clean: 0 stalls, 0 crash lines, alive, flight about 300 s / 120 s) / H-live (a failure on regen or live that the old binary lacks: restore s4563 from git and record the reader) / H-gate (nomission: the new [initMission] gate is wrong, fix it before reading anything else).
Also fold s6865_truehold_lvl10_dd4 from SOAK-RESULTS. 124 s was the most lvl10 dd4 had flown.
Waiting on a run: do not end the turn, the Stop gate counts it. Do offline work, or fold the result next iteration.
Ask owner when a human is next on: add tools/regen_replay.sh + regen_verify.sh to the CLAUDE.md regen order (owner file, not edited); Stop gate block count vs in-flight runs (BLOCKED.md).
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png.
