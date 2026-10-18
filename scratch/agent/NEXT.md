# Next work unit: restore key delivery, then re-run the keyed hold
HYPOTHESIS-ID: m6-mission-endurance
s5393: 0x696100/0x690400 in unkeyed runs are the ATTRACT loop (identical timings in 7 launches). Keys never reached the game in s5377/s5392/s5393 although winctl trusted=yes, rc=0. A macOS "RS64_patch_c quit unexpectedly" modal was on screen and no game window was visible in the screenshot.
Hypotheses: (H1) the crash modal / window not on the active Space blocks key delivery; (H2) the game's SDL window is not key window because Claude stays frontmost (activate ineffective); (H3) SDL reads keyboard via a path CGEventPostToPid no longer reaches after a recent main.cpp input change.
Discriminator: (1) human dismisses the dialog (click Ignore) or `killall UserNotificationCenter`/dismiss, rerun `zsh scratch/agent/m6_keyctl.sh` - H1 => origin leaves 0x790400 within 10 s of Return; (2) if not, also screenshot after activate to see if the game window is visible; (3) if still not, diff main.cpp poll_input against the s5099 commit (git log -S).
Then: fix m6_keyed_hold.sh to treat 0x690400 as a mission only if it persists >120 s (attract demo ends at ~167 s), and run >=3 holds of >=10 min.
