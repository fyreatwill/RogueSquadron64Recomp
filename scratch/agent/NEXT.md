# NEXT: G3 STAR WARS logo recede + opening text crawl at 16:9 vs angrylion (CURRENT-TRUTH item 32)
HYPOTHESIS-ID: g3-logo-crawl-169
State (s7155): every menu screen is H-equal at 21:9 and 16:9 (title, SELECT GAME, level select, craft, OPTIONS, PASSCODES, debrief,
pause, hangar). Logo recede (s7145) and text crawl (s7146, 640x300 fb triangles) were scored at 21:9 only. 16:9 = owner TV
(fb 796 wide, crop 0,9,369,216, 4:3 band x 66..303).
Hypotheses: H-equal (fit <= ~0.005 on band boxes, crawl x-scale ~1.0025 as 21:9 = presentation noise); H-crawl-wide (the 640 fb is
scaled/positioned differently at 16:9: fitted x-scale or offset beyond the 21:9 term); H-strip (non-black pillars beside the 640 fb).
Commands (one game at a time; ~24 GB disk free at s7155, delete .cap after post):
 C1: env RDIR=s7156 ASP=16:9 SECS=112 FROM=4150 EVERY=5 DL=69 DU=38 CW=384 CH=216 AP=<s7146 route: s6995 presses ending 64:a, i.e.
     6:start,11:start,16:start,21:start,25:left,27:start,33:start,40:right,46:left,52:right,58:left,64:a> zsh tools/s7146_arm.zsh C1 ""
 C2: same + "ROGUESQ_RECT_ASPECT=0" (rule 13).
Post: zsh tools/s7152_post.zsh scratch/s7156 C1 0,9,369,216 46,322; check which dir is valid with a phase sheet (s7155 inline sheet:
 thumbnails every 4th swap) - crawl fb is 640x300, try *r first, *n if magenta. Join tools/s7148_pfsearch.py, split logo / chapter title /
 crawl by swap, fit tools/s7143_affine.py box 66:4:303:200 (AFF_SX 0..3 AFF_SY -8..2 AFF_E 1..0.96 for the logo, as s7145), width term
 tools/s7154_kmd.py + 1.333x control tools/s7154_kgrid.py (env CROP=0,9,369,216 ALSUF=r|n, run from scratch/s7156). Pillars: s7155
 scratch/s7155/pill.py pattern (PIL only, no numpy on this host).
Discriminating outcomes: band boxes at floor + k 1.000 + pillars 0 -> H-equal (closes the 16:9 menu/cutscene matrix; then next open
 G-ladder rung); fitted x-scale/offset off by >1% vs 21:9 -> H-crawl-wide; RT64-only pillar pixels -> H-strip.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. CURRENT-TRUTH 58.0 KB (<60000).
