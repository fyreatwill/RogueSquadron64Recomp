# NEXT: G3 retail 4:3 LEVEL DESCRIPTION overlay vs angrylion (CURRENT-TRUTH item 40)
HYPOTHESIS-ID: g3-retail-43-ldesc
Why: s7183 closed crawl, pause and the interlaced 512x448 screen (it is ELITE ROGUES, not level description). Per s6802, LEVEL DESCRIPTION
is C-up on SELECT LEVEL: an overlay on the same 512x339 menu (typed green text replaces the hologram top), matched at RDP level only
(s6802/s6803), never scored as presented pixels at retail 4:3.
Route: s7182 F1 = tools/s7146_arm.zsh RDIR=s7184 ASP=4:3 FROM=0 EVERY=5 SECS=70 DL=5 DU=60 CW=849 CH=788, "ROGUESQ_FPS60=0 ROGUESQ_DRAW_DISTANCE=1",
with AP = the s7146 default but a C-up held on SELECT LEVEL: find the SELECT LEVEL window from s7181 ph_* csvs / scratch/s7181 M1.idx
(SELECT LEVEL sits between the 27:start and 33:start presses), e.g. ...,27:start,29:cup,33:start... (the autopilot knows cup since s6802;
a 2nd cup closes it, so press once; it types text over several seconds, so let it sit >=3 s before 33:start, shifting later presses if needed).
Post: tools/s7152_post.zsh (336-row screens score on the pre-fill *r dir), rectfit 1,25,848,668 start (s7182), tools/s7183_native_edge.py
for the native edge split + shift control. Optional same iteration: crawl/pause with no ASPECT env (ASP=off, window 640x512) on the s7183 B1 route.
Hypotheses: H-equal (native frac at the ~0.01-0.02 floor, loss on glyph edges), H-type (the typed-text reveal animates: lag shows as
shift-sensitive frames only), H-rect (overlay texrects stretched; RECT_ASPECT default on keeps 4:3 at k=1; check k with s7181 kfit if residual).
Discriminator: native-res frac + edge share + shift control on the LDESC swaps vs the SELECT LEVEL swaps before it (same run control).
Disk >= 25 GB per run; delete .cap/.raw after scoring; one game run at a time; never write WORKING to STATUS; owner save rule stands.
TRAP (s7183): capture bursts (raw frame gaps 7-11 ms) mis-pair 2-swap runs; re-pair +-6 before calling a swap bad.
