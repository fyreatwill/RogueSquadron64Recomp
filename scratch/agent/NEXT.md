# NEXT: G3 options menu + mission abort/debrief screens at 21:9 vs angrylion (CURRENT-TRUTH item 33)
HYPOTHESIS-ID: g3-options-debrief-219
State (s7152): title + SELECT GAME closed H-equal. Score menu/title captures with tools/s7152_post.zsh (pre-fill + NOPREFILL combined),
FID_P3 unset (captures are sRGB at source). Fit with tools/s7143_affine.py (AFF_SX=0,1,2,3 AFF_SY=-4,-2,0,2 AFF_E=1.0,0.996,0.992,0.988,0.984).
Unscored 2D screens: OPTIONS (title: down, start at ~t 12 s instead of the 11:start press), and the mission abort -> debrief/results
screen (s6995 route has an abort: see scratch/s6995/route_long.txt).
Hypotheses: H-equal (<= ~0.005 after the s7144 fit); H-rect (options/debrief texrects use a scissor that matches the fb ratio so
RT64's rect scale fires; RECT_ASPECT=0 arm then differs); H-blend (memory-blended backdrop: NOPREFILL replay needed, check painted).
Step 1: env RDIR=s7153 ASP=21:9 SECS=40 FROM=600 EVERY=3 DL=8 DU=32 AP=<options route> zsh tools/s7146_arm.zsh O1 ""
  and the same with "ROGUESQ_RECT_ASPECT=0" (O2), one at a time. Phase by angrylion contact sheet (see s7152 inline sheet method).
Step 2: debrief route (abort): same, AP from route_long.txt, FROM near the abort.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. Delete .cap after scoring (12 GB each; disk ~50 GB free).
