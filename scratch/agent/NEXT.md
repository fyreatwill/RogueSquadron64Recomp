# NEXT: G3 title / main menu / profile screens at 21:9 vs angrylion (CURRENT-TRUTH item 40)
HYPOTHESIS-ID: g3-title-menu-219
State (s7151): g5b_capture is sRGB at source (rebuilt into scratch/s6894/g5b_capture; .cs sidecar). Score with FID_P3 UNSET.
Not yet compared: the title screen ("press start"), main menu and profile/load screens between the logo recede (s7145) and level
select (s7144). Hypotheses: H-equal (RT64 == angrylion after one fit, <= ~0.005 like s7144/s7145); H-rect (texrect text width/offset
differs at 21:9, RECT_ASPECT path, s7142); H-colour (residual colour bias now that capture is sRGB: glyph-core blue lift should be
~0, s7150 saw +11 after FID_P3).
Step 1: find the swap range of these screens: env RDIR=s7152 ASP=21:9 SECS=45 FROM=200 EVERY=3 DL=8 DU=32 zsh tools/s7146_arm.zsh M1 ""
  (AP default = boot route; check scratch/s7152/M1.g5g.txt / op census tools/s7146_opcensus.py for menu texrect counts).
Step 2: post + score as s7144/s7146 (tools/s7141_post.zsh, tools/s7148_pfsearch.py per-swap join), arm RECT_ASPECT=0 in the same
  iteration (rule 13). Glyph cores per s7150 glyphcore.py with FID_P3 off: expect blue lift ~0 (H-colour refuted) or not.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. Keep CURRENT-TRUTH under 60000 B (59.9 KB now: prune closed items 31-35 to
one line each first).
