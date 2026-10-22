# NEXT (s5915): per-window class-1 crossing tally under stick steering

HYPOTHESIS-ID: g1-mission-progression

s5914: stick+A combos work (sua moved y -6.5 -> -0.4); plpos budget ended at el~253 so sra/sda/sla windows are unlogged, s5901 rows capped.
Work unit: find the plpos budget (src/main/main.cpp ~9967) and the s5901 row budget (tools/apply_s5835_sphere_probe.py / live RecompiledFuncs fixup), raise or gate them per stick window, rebuild, re-run `zsh scratch/agent/g1_steer.sh s5915_steer 270`.
Control: A-only phase (130-227 s) of the same run vs each stick window; gate on el. Positive control: sy/sx nonzero samples present per window.
Outcomes: crossings (c1f=1, best_ratio<=1) per window rise vs A-only -> aim confirmed, build closed-loop steering; flat -> steer direction is wrong/not toward NPCs, compute bearing from the player dump.
