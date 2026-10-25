# Does the 0x25000 extra drop make the wide HUD (ammo readout) render correctly?
HYPOTHESIS-ID: g1d-widescreen
s6217: extra=0x25000 moves wb/memset off the TLUT gap (end 0xAC1E00). Remaining: framebuffer capture of the flight HUD in both arms (scratch/agent/s6217_run.sh arms ctl/test; add the framebuffer-dump env used by g1_level_coverage_common.zsh, level 1). Outcome A: test HUD correct, ctl corrupt -> bake total drop (t0-0x70000) as wide default in apply_s6031_far.py, regen fully. Outcome B: both corrupt -> something else in gap; check heap/pool use.
