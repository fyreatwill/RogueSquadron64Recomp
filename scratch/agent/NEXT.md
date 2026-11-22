# NEXT (s7836)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks this unit. G6c and all G5 items wait on the owner only.
Why: G3 flight fidelity vs RETAIL (not angrylion-of-our-stream) is closed on lvl1 (s7831 exact) and lvl2 (s7832-s7835: render exact,
~0.1 deg rest pitch = retail-legal dt path, s7835 H-guest). Two levels is thin; take a third level with a different terrain/sky class.
Unit: det pair on mission 3 (0-based selected-mission byte 2) flight, same method as s7832.
- Save: derive from scratch/s6748/lvl2.eep (selected mission byte 0x31) with byte = 2, re-sign the EEPROM the way s6748/s7832 did
  (grep PORTING-STATE "Session 6748" for the signer), -> scratch/s7836/lvl.eep. Check the route reaches flight on retail first.
- Runs, one at a time: retail `env CPO=2 RSECS=175 EEP=scratch/s7836/lvl.eep PP=<s7832 PP> zsh tools/s7828_retail_cpo.sh scratch/s7836/r1`
  and a second retail schedule (R2, as s7832) as the retail-vs-retail baseline; port `env SAVE_FROM=scratch/s7836/lvl.eep SECS=150 CAP0=12
  AP=<s7832 AP> zsh tools/g3_port_capture.sh scratch/s7836/p1`.
- Score with the s7832 tools (tri dy mode, rect classes s7826_rect_path_offset.py --p-retail/--none-detail, pose fit) and its planted control.
Hypotheses / outcomes:
 - H-exact: tri dy mode 0, all sprite classes present, pose within the retail-vs-retail spread -> lvl3 CLOSED.
 - H-dtpath: render exact but a constant sub-pixel pose offset like lvl2 -> confirm with ROGUESQ_S7835_DT=1 that the onset dt differs
   (one extra port run), close as retail-legal.
 - H-defect: a missing/extra draw class or a >1 px geometry offset outside the retail spread -> name it and root-cause next.
