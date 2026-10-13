# Next work unit

HYPOTHESIS-ID: oracle-poke-mission-entry

s4723 result: hangar state byte 0x800CC3E4 reaches state 3 (waiting) ~3.5 s after hangar entry (t=54-58 s) and the run's presses had ended; state 5 (A/Start launch) and initMission never fired. H1: more A/Start presses after 58 s advance 3 -> ... -> 5 -> initMission (block refuted). H2: state 3 needs other input first (D-pad/C, ship select). H3: presses never move it (then poke byte 0x800CC3E4=5 at hangar phase).
Unit: edit scratch/agent/s4723_run.sh: alternate `start` and `a` every 3 s from 56 s to 140 s (occasional dright), --secs 150 (~10 min wall; background it, Monitor until-loop on driver.log rc=). Same watches. Outcome: 0x800AC8B0 or 0x800FA250 hit => refutes the block; no state change => extend --debug-write to wait for width 512 origin 0x6abxxx and write byte 0x800CC3E4=5.
