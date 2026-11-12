# NEXT: G3 ROGUESQ_ASPECT=auto + FULLSCREEN vs angrylion (CURRENT-TRUTH item 1)
HYPOTHESIS-ID: g3-owner-auto-fullscreen
NOTE: s7187 maintenance done (CURRENT-TRUTH 20212 B); this unit is CURRENT-TRUTH Next steps item 1.
Why: on the owner's TV/ultrawide the natural setting is ASPECT=auto + FULLSCREEN, which derives the fb width from the display
(main.cpp rs64_g1d_apply_aspect_policy; built-in panel 3024x1898 below the notch -> ~1.593:1 -> fb ~714 wide). s7186 scored only
ASPECT=16:9 (796). A non-standard width exercises the s6121 projection/viewport scaling, RECT_ASPECT (s7142) and the HUD shift at a width no G3 run has seen.
Run (screen unlocked, owner save read-only, one game at a time), same as s7186 with ASP=auto:
  env RDIR=s7187 ASP=auto FROM=200 EVERY=4 SECS=45 DL=8 DU=32 CW=1512 CH=949 zsh tools/s7146_arm.zsh M1 "ROGUESQ_FULLSCREEN=1"
  env RDIR=s7187 CW=1008 CH=633 zsh tools/s7131_arm.zsh 6 L6A "ROGUESQ_FULLSCREEN=1 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  (s7131_arm hardcodes ROGUESQ_ASPECT=16:9 in XENV_EXTRA: add ROGUESQ_ASPECT=auto to EX, later env wins? CHECK - else add an ASP knob to s7131_arm.)
  Read run.log "[g1f] ROGUESQ_ASPECT=auto ... ->" for the derived ratio and the fb width from al size in the post output.
Post: tools/s7152_post.zsh <dir> <name> <rect> <split>; rect from the picture bbox; tools/s7163_rectfit.py (s7186 TRAP: nominal rect was
wrong by 7 rows, always fit); tools/s7183_native_edge.py per phase (title 760-1000 / SELECT GAME 1050-1300 on the *n replay rescored with
s7122_fidelity score; SELLVL 1380-1590, craft 1620-1950, hangar 2000-2380 on *c). Flight: presented frames.csv + shift-2 ctl.
Hypotheses: H-equal (within s7186 numbers), H-rect (RECT_ASPECT/ texrect k != 1.000 at 714: run tools/s7154_kmd.py on craft/SELLVL),
H-hud (HUD radar/ring misplaced at the odd width: HUD-area diff px vs s7186), H-wide (fb width rounding gives a 1-px seam/edge column).
Delete .cap/.raw after scoring (do not delete *n/*r replay dirs before the owner sheet is made: *c are symlinks into them).
