# NEXT: G3 hangar / menus RT64 vs angrylion at 21:9 owner recipe (CURRENT-TRUTH item 31)
HYPOTHESIS-ID: g3-fidelity-hangar-219
State (s7141): flight fidelity at the owner recipe is H-equal on L1/L4 (16:9), L6 (16:9 + 21:9), L15 (21:9). Non-flight views
(SELECT YOUR CRAFT hangar with the G5g/G5i camera fix, level select, mission briefing) have no RT64-vs-angrylion score at 21:9.
Hypotheses:
- H-equal: the hangar/menu swaps score within the flight floors (frac>40 med <= 0.02, 0 frames > 0.05).
- H-wide-menu: wide 2D menu art (texrects, fills) or the ASPECT HUD/menu anchor walkers differ in RT64 at x outside the 4:3 band.
- H-hangar-cam: the G5g/G5i camera change exposes geometry RT64 draws differently (guard band, near clip) during the ship scroll.
Run: needs a hangar driver, not the forced-level route. Find the G5i (s6995) or G5g (s6907) hangar-scroll recipe in PORTING-STATE (grep
'Session 6995', 'Session 6907') and copy its key script into a tools/s7142_arm.zsh that also sets ROGUESQ_G5B_FRAME=<cap>
ROGUESQ_G5B_FRAME_EVERY=1 FROM=<first hangar swap> MAX_MB=12000 and runs scratch/s6894/g5b_capture at 504x216. Replay and score with
  zsh tools/s7141_post.zsh scratch/s7142 <name> 0,11,469,216 117,352     (check the rect with tools/s7123_present_rect.py first)
  python3 tools/s7141_summ.py ...; python3 tools/s7141_mask.py ... (HUD boxes differ in menus: mask none first)
Positive control: the --shift 2 score from the same capture must put >=100 frames over 0.05 (on slow menus use --shift 10) and the
painted-square control must PASS, or a pass is not a result. Owner save rule: hangar route reads the real save, NO_SAVE_WRITE stays on.
CURRENT-TRUTH ~59.7 KB: keep edits net-zero (Step 0 triggers at 60000).
