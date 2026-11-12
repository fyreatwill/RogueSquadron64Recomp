# NEXT: G3 true-retail arm (no ROGUESQ_ASPECT env) on crawl, pause and LEVEL DESCRIPTION (CURRENT-TRUTH item 41)
HYPOTHESIS-ID: g3-retail-43-noaspect
Why: s7181 scored menus/cutscenes with ASP=off (RECT_ASPECT inert there), but crawl (s7183), pause (s7183) and the LDESC overlay (s7184)
were scored only under ROGUESQ_ASPECT=4:3. With no env the window opens 640x480-class (check cap_*.txt window size; set CW/CH to it).
Runs (one at a time, screen unlocked: `/usr/sbin/ioreg -n Root -d1 | grep -c '"CGSSessionScreenIsLocked"=Yes'` must print 0):
 A (LDESC): env RDIR=s7185 ASP=off FROM=0 EVERY=5 SECS=56 DL=5 DU=60 CW=<w> CH=<h> AP=6:start,11:start,16:start,21:start,25:left,27:start,31:cup,43:cup,47:start
    zsh tools/s7146_arm.zsh A1 "ROGUESQ_FPS60=0 ROGUESQ_DRAW_DISTANCE=1"   (phases s7184: SELLVL ~1150-1262, AVAIL 1270-1365, LDESC 1440-1770)
 B (crawl + pause): the s7183 B1 route with ASP=off (PORTING-STATE s7183 "B =" line; FROM=2300 EVERY=12 SECS=300).
Post: tools/s7152_post.zsh <dir> <name> <rect> <split>, then tools/s7163_rectfit.py to fit the rect (window size differs from 849x788),
tools/s7183_native_edge.py per phase, tools/s7184_ldesc_region.py raw aldir frames.csv rect ldesc_lo ldesc_hi <craft-info swap> 12.
Hypotheses: H-equal (same native fractions as s7183/s7184 within ~0.005), H-scale (a non-4:3 window applies a different presentation
scale: rectfit lands off-aspect, kfit != 1), H-rect (RECT_ASPECT path differs without ASPECT env; s7181 says inert).
Discriminator: native frac + edge share + kfit vs the s7184/s7183 numbers; same-run control = the craft-info / flight phases.
Delete .cap/.raw after scoring. Owner save rule stands; never write WORKING to STATUS.
If this closes H-equal the G3 retail 4:3 matrix is complete; take the next 3c ladder rung not closed (owner-look items need no runs).
