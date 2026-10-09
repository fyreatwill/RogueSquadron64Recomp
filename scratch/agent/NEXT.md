# Next work unit (s4472): who writes 4 into 0x801545FD (slot-0 request byte)?

HYPOTHESIS-ID: m5-status03-service-reaping

State (s4471): port phase-5 status 03 is written at 0x8009B7CC (worker), taken because *0x801545FD == 4 (== fp). stopVoiceSlotSynced is NOT entered in phase 5. Retail executes B7CC x0 in 75 s.
Hypotheses: (A) a legitimate guest writer sets 4 in the port only because upstream state diverged; (B) a host/patched writer or DMA/stale memory leaves 4; (C) retail also writes 4 but later than 75 s.
Discriminator: retail oracle `--watch-write 0x1545FD:0x1545FE` (PHYSICAL; keep the whole-RDRAM watch as positive control, as in the s4104 recipe) for title+hangar, and in a same-shape port run a byte-write catch on 0x801545FD (log PC/thread/value). A: port writer PC is guest code and retail writes a different value or nothing. B: writer is non-guest/DMA. C: retail writes 4 after 75 s (extend --secs 150).
Tools: scratch/agent/s4471_run.sh (port run), tools/apply_s4471_stop_caller_log.py (live-tree probes; re-apply after regen), scratch/agent/soak_results/s4471/port.log.
