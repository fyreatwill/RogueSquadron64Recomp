# Next: m6-mission-a14 — why does shutdownMusyXVoices (A14) never exit after endMissionCleanup, and what ended the mission?
HYPOTHESIS-ID: m6-mission-stall
Fact (s5085, n=1): arm `in` stalled 111 s after onset with MAIN thread spinning in shutdownMusyXVoices (funcs_26.c:14529-14557) under endMissionCleanup; idle arm ran 175 s without it.
Hypotheses: (A) slot-0 status stays 03 because the zeroing writer (serviceVoicePoolFrame, see docs/M5-AUDIO-PLAN.md A14) never runs/loses (audio-stub artifact); (B) loop exits on a different flag (D_80154620) never set; (C) mission end was triggered by the scripted input (e.g. Z/A fires/ejects/crashes ship) and A14 is simply the first post-mission teardown.
Discriminator, ONE build/ONE run: reuse tools/apply_s4694_a14_boundary.py / s4694b status census to log slot-0 status, D_80154620 and serviceVoicePoolFrame call count per 1 s while in the spin; also log the reason endMissionCleanup is entered (caller flag). Route: scratch/agent/s5085_stall.sh in (+ the env vars the census needs).
Outcomes: A -> status 03 constant, writer count 0; B -> status 0, flag unchanged; C -> endMissionCleanup entry reason names player-death/objective.
