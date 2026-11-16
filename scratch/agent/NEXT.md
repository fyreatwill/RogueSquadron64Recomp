# NEXT (s7461)
HYPOTHESIS-ID: soak-stall-measure-coverage

s7460 landed ROGUESQ_PLANT_HOLD=<s>[,<dur>] (main.cpp rs64_diag_plant_hold_tick: guest thread sleeps <dur> s once inside
osViSwapBuffer_recomp, host VI keeps ticking) and queued scratch/agent/soak_queue/s7460_plant_hold_ctl.sh.

Step 1: fold s7460_plant_hold_ctl from SOAK-RESULTS.md / its log.
  - CONTROL PASS (m6 fs_holds>=1 vi_stalls30s>=1; g1e vi_stalls30s>=1 max_vihold_ms>=35000) -> H-ok: close the stall-measure series
    (class DN/DO/DP) in CURRENT-TRUTH item 1 and take the next ladder item (prefer an M3 idiom-class audit, ITERATION item 3).
  - "VOID: plant never fired" -> rs64_store_diag_tick is not reached on this route; move the call to the top of osViSwapBuffer_recomp.
  - m6 fs_holds=0 with begin line present -> H-m6-blind: fs (cumulative RDP fullsyncs) advances while the swapping thread sleeps, so a
    second guest thread submits gfx; add a swap-count field to the [vi] row and score holds on it.
  - g1e vi_stalls30s=0 with begin line present -> H-ring-blind: inspect ring_ph.txt origins over the 40 s window.
  - Dead arm (alive_at_end=0) -> the 40 s block tripped a watchdog/timeout somewhere: grep the log for the killer and shorten dur to 35.
Step 2: if the soak voids 5x on idle, run it by hand when HID idle allows; do not re-queue blind.
