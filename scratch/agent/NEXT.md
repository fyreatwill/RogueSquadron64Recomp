# NEXT: 21:9 / 16:9 sky-side corner holes, class (a) (CURRENT-TRUTH item 29). Unit (b) closed in s7135 (ROGUESQ_HORIZON_GATEFIX).
HYPOTHESIS-ID: g3-owner-recipe-219
State: the clear-class burst is the last hole class. Bottom-left at banked roll, pitch -38..-46. The sky-band mesh ends there
(H-skyband, s7134); culling is refuted. Captures: 21:9 fix-off scratch/s7134/Z1.cap (burst 7527-7537, max 24.8k), 16:9 fix-on
scratch/s7135/W1.cap (burst 7536-7544, max 13.9k). Both have RAM every swap, replays Z1r/ and W1r/, rects files.
Hypotheses for what should fill it:
- H-fill-rect: the builder's two rects cover only the ground side of the split, and the sky side relies on the sky band. Under
  ASPECT the sky band's authored extent (made for 4:3) cannot reach the wide corner. Fix: under k > 1, add a 3rd FillRect (sky
  side, from the split line to the far edge) in the colour emitFrameRdpInitDl uses, painted BEFORE the sky band so the band still
  draws over it.
- H-band-scale: the sky band is placed in screen space with a 4:3 x scale (like s7133's split). If so, its x span is k times too
  narrow and scaling its vertices by k would close it (check: band vertex x range in Z1 7533 vs the s7133-corrected split x).
Discriminator, offline first: tools/s7134_band.py on Z1 7533 and W1 7542. Compare the band's leftmost x with the screen edge, and
the band's x span with k * (its span at the same pose in a 4:3 frame; use scratch/s7133 R1 4:3 if a comparable pose exists, otherwise
compute it from the band HOB vertices projected with the RAM camera). Span ratio ~k -> H-band-scale; ratio ~1 -> H-fill-rect.
Then patch (opt-in first, =tog for the same-run A/B), rerun tools/s7135_arm.zsh 6 Y1 "ROGUESQ_ASPECT=21:9 ROGUESQ_G5B_FRAME_EVERY=1
ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000", index/rects/replay (s7135 pattern: split -l 119), and score with
tools/s7134_score.py. Pass: clear-class >3000 swaps -> 0 at 21:9 and at 16:9, no new holes, sheet with tools/s7135_sheet.py.
Owner save rule applies. CURRENT-TRUTH is 58.8 KB: keep edits net-zero.
