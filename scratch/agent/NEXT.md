# NEXT: G3 render fidelity -- lvl1 flight with scripted fire (laser bolts, explosions) vs retail
HYPOTHESIS-ID: g3-flight-effects-oracle-diff

s6745: no-input flight +20..60 s = H-match, no desync, but no effects ever appear (player never fires).
Hypotheses: H-match (bolts/explosions identical); H-desync (fire presses land at different phases in retail
(emulated-time --press) vs port (wall-time autopilot) -> bolt frames match only per-element, compare bolt shape/colour,
not whole frames); H-rt64-fx (bolt/explosion alpha, blend or additive colour differs: heat concentrated on effects while
terrain matches); H-geom (missing effect geometry).
Steps (one game run at a time):
0. Which N64 button fires lasers? Check docs/PROJECT-OVERVIEW/PORTING-STATE (grep -n 'fire\|laser' | head) and the
   autopilot key names in src/main/main.cpp (grep ROGUESQ_AUTOPILOT). Use the same button in both runs.
1. Retail: copy scratch/s6745/retail_flight.sh, add fire presses e.g. a held/repeated "a" every 0.5 s from 115..170 s
   (rs64_oracle --press names: start a b z dup ddown dleft dright cup cdown cleft cright l r), dumps d=2+0.5*i (i 0..79).
2. Port: g3_port_capture.sh with the oracle EEPROM, AP as s6745 plus fire presses at the same flight-relative times
   (port flight start ~69.5 s wall; retail first flight dump arms ~112.6 s).
3. g3_oracle_match.py ... --dec shift --worst 12; eyeball pairs that contain bolts/explosions.
