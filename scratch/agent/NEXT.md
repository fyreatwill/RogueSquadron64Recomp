# NEXT (s7462)
HYPOTHESIS-ID: soak-stall-measure-coverage

s7461 (class DQ): the m6 live stall poller was blind during the 130 s mission-verify sleep; it now polls through it
(scratch/agent/m6_god_common.sh vtick; M6_VERIFY_BLIND=1 = old behaviour). Queued scratch/agent/soak_queue/s7461_m6_verify_window_ctl.sh
(same recipe as the s7460 m6 arm: L4 FPS60 dd4 16:9, ROGUESQ_PLANT_HOLD=120,40).

Step 1: fold s7461_m6_verify_window_ctl from SOAK-RESULTS.md / its log.
  - CONTROL PASS (alive_at_end=1 fs_holds>=1 vi_stalls30s>=1, keys.log has a "stall t=" line in ~150-200 s) -> H-ok: close the
    stall-measure series DN/DO/DP/DQ in CURRENT-TRUTH item 1 (one line), and take the next ladder item: an M3 idiom-class audit
    (ITERATION item 3) or the top open owner G5 item in CURRENT-TRUTH.
  - vi_stalls30s=0 with plant begin present -> the mission gate moved later than 120 s (check "mission t=" in keys.log); move the
    plant to mission_t+30 and re-queue once.
  - "VOID: plant never fired" or dead arm -> grep run.log for the killer; do not re-queue blind.
Step 2: if the soak voids 5x on idle, run it by hand when HID idle allows.
