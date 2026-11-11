# NEXT: capture colour space at source (CURRENT-TRUTH item 39)
HYPOTHESIS-ID: g3-capture-colourspace
State (s7150): tools/g5b_capture.swift captures 32BGRA with no colorSpaceName, so values are Display-P3 (untagged); angrylion replays are
sRGB. tools/s7122_fidelity.py FID_P3=1 converts offline (flat-area error -30..55%, 4:3 text blue lift +51 -> +11). Fix it at source.
Step 1: in g5b_capture.swift set cfg.colorSpaceName = CGColorSpace.sRGB (and log it), rebuild scratch/s6894/g5b_capture (check how it was
  built: grep swiftc in PORTING-STATE s6894/s6914).
Step 2 (one run, same-run control impossible across captures, so run TWO capture processes on the same game window at once: old binary and
  new binary, same CW/CH): env RDIR=s7151 ASP=21:9 SECS=300 FROM=15300 EVERY=5 DL=150 DU=115 AP=<s7150 AP> zsh tools/s7146_arm.zsh P1 ""
  plus a second g5b_capture (old binary) started alongside (edit a copy of the arm script, tools/s7151_arm.zsh).
Outcomes: H-src: new raw ~= FID_P3(old raw) within ~3/channel on flat areas, and the new raw vs angrylion matches FID_P3 scores ->
  make the capture sRGB, keep FID_P3 only for old raws. H-partial: new raw still differs (ScreenCaptureKit ignores colorSpaceName for
  window filters) -> keep FID_P3=1 as the documented default for new work and say so in CURRENT-TRUTH run recipes.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. Keep CURRENT-TRUTH under 60000 B.
