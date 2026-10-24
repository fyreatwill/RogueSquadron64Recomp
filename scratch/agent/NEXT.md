# NEXT: G1d step 12 - verify on-screen window at FB_WIDTH=683, then widen FOV/HUD
HYPOTHESIS-ID: g1d-widescreen
Known (s6119): 683 flip readback is a correct frame after RT64 width-allowlist fix; VI regs consistent.
Do: one run, ROGUESQ_FB_WIDTH=683 + VPW/ASPECT_SCALE 1.3333, window screenshot with the game window activated (osascript activate the process before screencapture; s6116 did this) in ctl and w683 arms. Positive control: ctl screenshot shows the game, not another app. Expected: w683 window shows the 16:9-ish frame.
Then: check what the 3D view is at 683 (FOV scalar 0x130C50 from s6024 is the lead; is the extra width real scenery or a stretch?), HUD anchoring, menus/hangar at 683, and bundle behind ROGUESQ_ASPECT=auto|4:3|16:9|21:9.
