# NEXT: who wakes hud service worker (0x80954F60, key 0xC) with an empty slot at px3+spill (s6570)
HYPOTHESIS-ID: g1c-dd-phase2
Fact (s6570, 3/3): crash at guest 0x80049644 lw v0,0x14(s0) after recvServiceMessage returned 0; `[svcnull] R a=80954F60 b=0000000C`, zero `S` lines (no NULL was posted).
Hypotheses: H-stop (signalServiceWorkerStop 0x8000703C flag 0x40 + wake at 0x8002C3B0, worker loop at 0x80049634 never checks it); H-reaped (service record/queue freed or overwritten, slot 0x1E8 reads 0); H-sendfail (a send failed under pressure so no reply filled the slot).
Discriminator, ONE build: extend rs64_s6570_svcnull to log (a) every signalServiceWorkerStop (a0, ra), (b) at the R-null: service[+4] flag byte, [+8] thread, whether rs64 free census saw 0x80954F60 freed (s5041 set), (c) the last 5 sendServiceMessage(queue key 0xC) with msg/ra/result. Positive control: (a) must fire on a normal level exit.
Repro: zsh scratch/agent/s6553_run.sh 6 3 "ROGUESQ_RAMTOP_MB=16 ROGUESQ_DLPOOLX=1 ROGUESQ_DLPOOLX_MB=4 ROGUESQ_DLPOOLX_AT=3000 ROGUESQ_MALLOC_SPILL=1 ROGUESQ_SVCNULL=1" N   (logs: scratch/agent/m6/g1_lvl1s6553_dd6_px3_N/fail_att*.log)
