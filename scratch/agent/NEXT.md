# NEXT (s7839)
HYPOTHESIS-ID: g3-flight-fork-carrier
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks this unit. G6c and the G5 items wait on the owner only.
Why: s7838 showed the lvl4 camera fork (rest pitch 0.1917 port vs 0.2084 retail, reticle 5.75 px low) is NOT carried by the sim dt
word 0x8011A904: ROGUESQ_VI_STAMP_ONSET2 raised the onset dt to 2 VI right before the forking row and that row stayed bit-identical.
Hypotheses:
  H-snapshot: timeSnapshotFiller 0x8000BE1C ((stamp - prev) / k, called mid-frame from 0x800AF36C / 0x800C666C / 0x800FA728) returns
    VIs elapsed during guest work: ~0 in the port, >0 in retail. Predicts: port v0 at 0x8000BE28 = 0 at the fork frame, retail > 0.
  H-other: some other host-timed input (osGetCount / osGetTime direct callers, audio/RSP completion order) differs at that frame.
    Predicts: timeSnapshotFiller values equal in both at the fork frame.
Unit (one port build, one retail run, ONE table):
  1. Port: add an opt-in log (new tools/apply_s7839_snaplog.py, registered in fixup_game_funcs_vendored.py like s7838) at 0x8000BE28 in
     timeSnapshotFiller: `[snap7839] ra=<ctx->r31> el=<v0>` plus the [dt7835] fr lines already there. Run the s7838 p1 recipe
     (SAVE_FROM scratch/s7838/lvl.eep, VI_STAMP=1, RAMDUMP, S7835_DT) + ROGUESQ_S7839_SNAP=1.
  2. Retail: the s7838 R1 recipe with XO="--watch-pc 0x80043918,0x8000BE28 --pc-ram-dump 0x80043918:0x80137DB0:0x801384E0"
     (--watch-pc prints $v0 = elapsed ticks). Positive control: retail must print watch rows at 0x8000BE28 (non-empty) during flight.
  3. Table per flight frame rows 0..10: caller, elapsed ticks port vs retail. If H-snapshot holds, a lever ROGUESQ_SNAP_VI=<n> that
     pins el to retail's value at the fork frame must make row 3 match retail (same-run comparison against s7838 p1).
Do NOT spend more than this unit on it if the table is flat (H-other): then write the hypothesis table and move to mission 5 (0x31=4,
Liberation of Gerrard V) in the det sweep.
