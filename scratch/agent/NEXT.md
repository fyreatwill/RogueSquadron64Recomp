# Next work unit

HYPOTHESIS-ID: m5-b40-gate-default

s4700 result: port default zeroes the MusyX gate 0x800A0F50 (B40), so runVideoFrameTick's musyxNoopStub skips shutdown+dereg and the guest's reapplyAudioConfig double-registers the synth (retail alternates). B40=1: crash 0/3 vs B40=0 1/1 (scratch/agent/s4700_b40/).

Unit: qualify B40=1 as the default on the canonical route, then flip it.
Hypotheses:
- H-b40-safe: with B40=1 title VI 1024 and hangar VI 512 (0x006AB400) are reached, real-image tasks and nonzero PCM persist, no crash/abort, A13/A14 waits still return.
- H-b40-regress: gate=1 re-enables a stub path (waitForMusyXAudioTaskDone spin / drain timeout / MORT must-not-reach-aspMain) and the route breaks.
Discriminator (one build not needed; env only): run the s4677 corrected Start-mash route (see scratch/agent/soak_results/s4264_gate/ recipe) with arms B40=0 (control) and B40=1 x2, concurrently, ROGUESQ_LOG_S4700_CB=1 + the A11/A12/A13/A14 wait probes armed; phase-gate on VI transitions. Cleanup MUST pkill -KILL -x RogueSquadron64Recomp.
Outcomes: B40=1 reaches 1024 and 512 with alternation and no timeouts => edit fixup_game_funcs_vendored.py lines ~8282/8294 (and the live funcs_23.c) to pass r2 through by default, keep ROGUESQ_M5_B40_VALUE=0 as the rollback; any wait timeout/MORT trap => record which and treat as the next de-stub step.
Also consider: findAndZeroTableSlotMatching first-match-only is retail behaviour (do not change).
