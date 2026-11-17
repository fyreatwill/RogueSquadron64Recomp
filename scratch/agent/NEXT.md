# NEXT (s7554)
HYPOTHESIS-ID: class-gn-async-writeback-clobber

GM CLOSED s7553 (sync RDP: every out-of-rect writeback change is RT64 re-emitting its own previous writeback; tools/s7553_gm_score.py).
GK (s7551) and GM (s7553) covered the SYNC RDP only. GN: the same two checks under the owner opt-in ROGUESQ_RDP_ASYNC=1
ROGUESQ_RDP_NODRAIN=3 (OWNER-OPT-INS recommends =3), where fullSync and its colour/depth writebacks run on the RT64 worker AFTER the
guest is told reads are done, so the guest can legitimately write the fb/zbuffer span before RT64's full-row writeback lands.

Hypotheses:
- H-clean: gch/clob 0 as in sync (the guest never writes a pending writeback span before it lands) and GM verdicts unchanged.
- H-clobber: clob > 0 (RT64's async full-row writeback reverts guest/host bytes written after dp_complete) -> name the writer (s7551-ev
  first= address -> store watch) and fix (e.g. wait-for-writeback before the guest's next touch of that span, or write only drawn rows/cols).
- H-blind: the s7551 hooks do not fire on the worker path (wb=0 or plants not seen) -> fix the hook first, then rerun in the same session.
Discriminating run, ONE launch (same build as s7553, no rebuild):
  mkdir -p scratch/s7554_gn; E="ROGUESQ_S7551_GK=1+ROGUESQ_S7551_GK_PLANT=1+ROGUESQ_RDP_ASYNC=1+ROGUESQ_RDP_NODRAIN=3"
  env R=$PWD/scratch/s7554_gn HOLD=120 ARMS="4:l12:ROGUESQ_FORCE_SAVE_MISSION=12+$E 4:l4:ROGUESQ_FORCE_SAVE_MISSION=4+$E 1:l1:ROGUESQ_FORCE_SAVE_MISSION=1+$E" zsh tools/g1e_owner_quiet_arms.zsh
Score: python3 tools/s7551_gk_score.py scratch/s7554_gn/log_*.txt ; python3 tools/s7553_gm_score.py scratch/s7554_gn/log_*.txt
(and --from 72 for mission-only). Positive control: plants seen/clobbered >= 97% per arm (both scorers check it).
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
