# NEXT (s7860)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. A crash or owner report outranks this.
State: the main-mission det sweep 0x31=0..15 is COMPLETE (s7859). 0x31=16 without the bonus unlock duplicates 15. With
scratch/s7859/base_bonus.eep (+0x39=0x60) it is the self-starting race, which FORKs at t395 because det_pair's hangar Start
schedule (retail PP / port AP, tools/s7849_det_pair.sh lines 16 and 21) lands presses mid-race in the port only (H-input).
Unit: make the press schedules env-overridable in s7849_det_pair.sh (PP_OVR / AP_OVR; defaults unchanged, so 0..15 stay
byte-identical) and rerun bonus 16 with no Start after the level pick on BOTH sides. Copy the times from the s6771 recipe in the
tools/g3_mission/run.sh header (PRESS to 51 s / AP to 31 s). Keep the dt pins (8192 cap) and the seed pin:
  `env BASE_EEP=scratch/s7859/base_bonus.eep PP_OVR=... AP_OVR=... zsh tools/s7849_det_pair.sh 16 scratch/s7860/v16r`
  (delete nothing; new OUTDIR so r1 reruns with the new PP).
Outcomes: H-exact through the t395 ground crash (port also crashes at t395, retry ~t458) closes H-input, and bonus 16 = retail.
A rand/record fork before t395 with equal press ticks reopens H-new: name the writer with tools/s7858_store_seq_cmp.py.
Positive controls: p2 must fork at t0; the control flip must be caught at t100; both arms' press ticks must be printed (count
800fa730 rows before each [press]/[autopilot] fire line, as in s7859) and equal.
Then: bonus 17/18 (0x31 clamps to 16, so 17/18 need d-pad RIGHT on SELECT LEVEL, per the s6771/s6772 recipes).
