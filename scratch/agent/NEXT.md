# NEXT: G3 large fireball / destroyed-vehicle explosion vs retail angrylion (uncovered by s6747/s6748)
HYPOTHESIS-ID: g3-fireball-match

State (s6810): G3 flight render + sim matched for missions 1-19 (s6744-s6777); menus/pause/debrief matched (s6778);
impacts matched by population on lvl1 only as small puffs (s6747). NOT covered: a large fireball from a destroyed vehicle
(s6747 note), and lvl2 impacts (s6748: no positive). G1e dd4 clean fps = 59.3 (s6810, tools/g1e_clean_fps.zsh).
Hypotheses: H-match (fireball frames within the same-run match band); H-blend (RT64 blend/combiner differs on the
fireball sprite: colour/alpha mismatch localized to the fireball); H-anim (fireball sprite frame sequence/timing differs).
Method: need a deterministic kill. lvl1 (Mos Eisley) with the dt pin + rngSeed recipe (tools/g3_mission/run.sh, s6770)
and the s5841 TELE-style forced-hit lever if one destroys a vehicle in view; else fire arms (B/Z alternating, s6748
fire recipe) on lvl1 where targets are in front at flight start. Retail arm: oracle with matching press schedule, dumps
every 0.25 s around the kill. Port: g3_port_capture.sh window captures. Compare: g3_oracle_match.py on the pair, plus
g3_effect_count.py orange/yellow population inside the fireball bbox.
Control: same-run median d over non-matching pairs; the orange instrument must count >0 on a retail fireball dump.
Aim/steer work is OUT OF SCOPE (ITERATION 3c G1): if no kill happens in view without aiming, use the forced-hit lever.
