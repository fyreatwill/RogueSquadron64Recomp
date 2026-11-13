# NEXT (s7274): G5c frozen-frame check at the owner's EXACT recipe (fullscreen 16:9, several levels)
HYPOTHESIS-ID: g5c-freeze-owner-fullscreen
State: the WIDEWIN auto stack adds no in-flight frozen frames on L4 dd4 windowed at 16:9 (s7272) or 21:9 (s7273); every hold >= 250 ms
there was a scene transition (sheets docs/owner_sheet_s7272_*, s7273_*). G5c's owner recipe is FPS60 dd4 ASPECT=16:9 FULLSCREEN=1, and
fullscreen + other levels have never been scored with the image-hold scorer.
Hypotheses: H-none-fs (0 flight holds >= 250 ms at fullscreen on L1/L4/L5/L12 -> G5c stays owner-only); H-fs (holds appear only in
fullscreen: present/swapchain size path, e.g. RETINA/fullscreen drawable resize, s7202-s7203); H-level (flight holds on some level,
not L4: name it by its phase/frames and profile with `sample` on a live run).
Discriminator: tools/s7272_g5c_hold_arm.zsh with KEEP=1 (SIGSTOP 1 s control x3, hold sheet via tools/s7273_hold_sheet.py), per level.
First check (boring): does scratch/s7009/arm.zsh pass ROGUESQ_FULLSCREEN=1 through E, and does tools/g5b_capture find the fullscreen
window (frames > 10/s)? If capture fails at fullscreen, use the window at full display size instead and say so.
Commands: check HID idle >= 120 s and `/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes'` is false, then per level L:
  edit the arm's level arg (it runs `arm.zsh 4 4 ...` = level 4, dd4), e.g. add LEVEL=${LEVEL:-4}; run
  `env KEEP=1 TAG=s7274f$L ASP=16:9 CW=480 LEVEL=$L zsh tools/s7272_g5c_hold_arm.zsh`, one run at a time; view scratch/s7272/<tag>/holds_sheet.jpg.
Expected: H-none-fs -> close G5c engineering (owner flight remains); any flight hold -> its phase + frames name the next unit.
