# NEXT: G3 retail 4:3 remaining screens vs angrylion (CURRENT-TRUTH item 39)
HYPOTHESIS-ID: g3-retail-43-remaining
Why: s7181 matched 18 screen classes; three were not reached: the interlaced 512x448 level-description screen (button on SELECT
LEVEL), the chapter text crawl (owner save's progress skips it on the default route; tools/s7146_arm.zsh was built for the crawl route,
see its header and the s7146 PORTING-STATE entry), and the pause menu in flight (start during flight; s7150_pause_sheet.py exists).
Method (s7182 lessons): capture the window at FULL size (CW=849 CH=788 for ASPECT=4:3), fit the rect with tools/s7163_rectfit.py
after a first s7122_fidelity score, and score thin features at native fb size (tools/s7182_ringfull.py pattern). Check the rect
against the raw height. Interlaced fbs: s7180 notes FID_MAINRUN crops an interlaced field to 512x1; score with FID_MAINRUN=0.
One run per route, arms ASPECT=4:3 and no ASPECT env (ASP=off). Painted-square control as in s7181.
Hypotheses per screen: H-equal (frac at the ~0.02 floor), H-interlace (RT64 weaves/bobs the two fields differently from the VI:
predicts a row-parity pattern in the diff), H-tool (crop/rect), H-rect (2D rect scaling under ASPECT=4:3; RECT_ASPECT default on).
Disk >= 20 GB per run (a 60 s full-res capture is ~6 GB raw + ~9 GB cap; delete after scoring); one game run at a time; never write
WORKING to STATUS; owner save rule stands.
