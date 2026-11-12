# NEXT: G3 owner recipe in FULLSCREEN vs angrylion (CURRENT-TRUTH item 42)
HYPOTHESIS-ID: g3-owner-fullscreen
Why: G5's owner recipe is `ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=16:9 ROGUESQ_FULLSCREEN=1`, but every G3 fidelity
capture (s7122-s7185) was a window (504x216 .. 849x788). Fullscreen changes the swapchain size, RT64's window-derived resolution scale
and the presenter's fit, none of which is scored. s7185 showed scores move with presented scale (edge class), so the fit is the question.
Boring first: does scratch/s6894/g5b_capture find the fullscreen window (SCK "not on screen" / Code -3815 = no)? s6930 checked fullscreen
at auto/16:9/21:9 on the built-in display by screenshots only. If SCK cannot capture it, use `screencapture -l<id>` stills on a few phases.
Run (screen unlocked: `/usr/sbin/ioreg -n Root -d1 | grep -c '"CGSSessionScreenIsLocked"=Yes'` prints 0; owner save read-only):
  env RDIR=s7186 ASP=16:9 FROM=1900 EVERY=3 SECS=120 CW=<display w> CH=<display h> zsh tools/s7146_arm.zsh F1 "ROGUESQ_FULLSCREEN=1"
  (s7146_arm defaults FPS60=1 dd4; default AP is the L6 hangar route). Window size: read cap_F1.txt "window (...)" line.
Post: tools/s7152_post.zsh scratch/s7186 F1 <rect> <split>; tools/s7163_rectfit.py for the flight and menu ranges;
tools/s7183_native_edge.py per phase (shift ctl must PASS).
Hypotheses: H-equal (native frac within ~0.005 of the windowed s7125/s7155 numbers, edge share >=85%), H-scale (fullscreen fit is
non-uniform: rectfit x/y scales differ by >1%), H-res (internal resolution does not follow the display: presented image is an upscale,
edge loss rises sharply and fine detail blurs vs a windowed same-res control).
Discriminator: rect scale ratio x/y + native frac + edge share vs windowed numbers. Delete .cap/.raw after scoring. Never write WORKING to STATUS.
