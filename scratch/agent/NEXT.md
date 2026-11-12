# NEXT: M6 boot freeze, fold s7190 hunts b-d (CURRENT-TRUTH item 1)
HYPOTHESIS-ID: m6-boot-freeze-loop
State: s7190 proved the capture path in the s6993 freeze env (HUNT_CONTROL dump=PASS frozen=PASS); 13 owner-recipe boots clean.
Queued: scratch/agent/soak_queue/s7190_bootloop_{b,c,d}.sh (14 boots each). Read their SOAK-RESULTS lines first.
Hypotheses: H-consumer (the video-queue 0x80128CF0 receiver is blocked elsewhere: audio/MusyX, DMA completion),
H-race (duplicate VI/retrace posts overflow the queue under a scheduling burst), H-host (host lock in present/RT64 init).
If any recipe exited 1 with FROZEN: python3 tools/sample_game_threads.py on scratch/s7190/hunt_X/rs64_stall_*.sample.txt and
boot*_freeze_{a,b}.threads.txt; game [Game] thread stack in a recv/send of another queue -> H-consumer (name it); stacks idle
and [stall-dump] queue CF0 count==valid with duplicate VI msgs -> H-race; a host mutex/condvar under RT64/present -> H-host.
If all clean (~55 boots, control passing): the rate is <1/65 in this env; do not queue more identical hunts. Pivot to the
static route: audit every osSendMesg to 0x80128CF0 and every path that sets/clears vflag 0x80037808 in the recompiled
advanceVideoFrame / viRetraceHandlerThread (0x80019868) for a post-with-flag-set-then-leave window (s6993 refined
H-lost-post), and to host-side VI event delivery ordering in librecomp (H-race), offline.
