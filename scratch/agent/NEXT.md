# NEXT: G1d step 25 - OSMEM=12 lvl1 hang: main thread waits forever in waitForPostSwapAck
HYPOTHESIS-ID: g1d-widescreen
Known (s6132 sample): initMission finished; mainGameLoop->runInMissionFrame->waitForPrevFrameDone->waitForPostSwapAck->osRecvMesg blocked; idle thread running; gfx/SP threads alive.
Hypotheses: H-nosend (the post-swap ack sender never fires: gfx/swap completion path has another size-dependent assumption), H-drop (message sent but queue/pointer rejected by an 8 MB-style range check), H-order (thread priority/scheduling stall specific to the larger heap).
Discriminator: find the queue pointer waitForPostSwapAck passes to osRecvMesg (funcs_5.c:7048 area) and log every osSendMesg to it plus the receive, per VI, OSMEM=12 vs unset (same recipe: env XENV_EXTRA=\"ROGUESQ_OSMEM_MB=12 \" HOLD_S=60 LEVEL=1 TAG_SUFFIX=x zsh scratch/agent/g1_level_coverage_common.zsh). Sends>0 with no wake = H-drop; zero sends = H-nosend (then trace who should send).
