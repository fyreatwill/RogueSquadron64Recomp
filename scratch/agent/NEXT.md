# NEXT (s5918): confirm what [s5901] pp is

HYPOTHESIS-ID: g1-mission-progression

s5917: bearing of class-1 sphere centres relative to pp travel is flat (tools/s5917_bearing.py). If pp is a bolt/segment position (not the ship), this does not test ship-aim.
Work unit: grep tools/apply_s5835_sphere_probe.py (and the s5901 emitter) for what pp is. If ship: H-aim closed, move to G1 next unmet item. If bolt: redo bearing using [plpos] ship position joined by log order (s5916_tally.py has the join), same hist; flat again => H-aim closed.
Control: c1f=0 hist shape must be reproduced.
