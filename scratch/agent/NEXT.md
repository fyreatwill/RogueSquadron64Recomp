# NEXT (s7266): fold s7265_ww_r_cost + s7265_ww_r_edge — is there an auto-stack R that keeps WIDEWIN's side gain at 60/s?
HYPOTHESIS-ID: widewin-169-tv
State (s7265): R=48 in the auto stack (src/main/main.cpp ~12456, s7258) skips 92-95% of the wide cells and erases the side gain; merge+E16
alone keeps the gain (21:9 R=0 -6.1/-6.4 hard80). WIDEWIN widens 16:9 too (-3.8/-5.1). Predictor: tools/s7265_ww_r_predict.py <run.log> [R..].
Results: scratch/s7265q (timing; s7230_headroom, flat30, dip runs, merged; w0d DUTY control must show clearly more <55/s s) and
scratch/s7265e/edge_{r72,r88,c219}.txt (c219 must drop >=3 on a side, capfps >=10/s).
Outcomes:
- H-keep: the largest R whose window p50 stays <~13 ms with no flat-30 run and 0 beyond-route s, AND whose edge arm drops >=3 on a side ->
  change the auto R in main.cpp from 48 to it (explicit ROGUESQ_DD_WIDEWIN_R still wins), update OWNER-OPT-INS WIDEWIN line, then check dd6
  (s7258's late dips) with a soak like s7257_dd6r_stack at the new R.
- r0 already holds 60/s on AC (s7248 ww 13.16 ms was 60/s; merge saves ~1.3 ms) -> consider R=0 auto (merge only) if r72/r88 buy nothing.
- H-clash: every R that keeps the gain costs like STACK=0 -> report the trade to the owner in OWNER-OPT-INS (WIDEWIN auto = cheap but no side
  gain; STACK=0 or R=0 = side gain at +~3 ms), keep default, close thread.
- Any crash -> backtrace first.
If the soaks have not run (owner active): do not wait; ladder 3c next open owner-look item (G5i hangar re-entry status, G5h cutscenes).
