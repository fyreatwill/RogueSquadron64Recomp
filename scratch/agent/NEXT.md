# RESUME — run the hangar-gated menu walk on a quiet machine

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4775: scratch/agent/s4776_gated_menu_walk.sh (hangar-gated, one key/4 s, screenshot each) died 3/3 at
musyxSynthFrame_s4562_impl+5808 at VI 640 0x696100 (~77 s) before hangar; title arrived at ~50 s vs 15 s in
fast runs; load average was ~8. Hypothesis Hload: the crash/slowness is load-sensitive.

Next: check `uptime` (want load < 3; if not, run anyway and record load). Run `zsh scratch/agent/s4776_gated_menu_walk.sh`,
read h0..h8 screenshots to learn the hangar menu, then script the true sequence. If still 3 more crashes at
quiet load, Hload is refuted -> pivot to the +5808 wild pointer (si_addr 0x38000950e) writer as an M5 item.
