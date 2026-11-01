# NEXT: G3 render fidelity -- lvl1 explosions (hit effects) vs retail, population method
HYPOTHESIS-ID: g3-flight-effects-oracle-diff

s6746: bolts H-match (rate 34.7% retail vs 33.3% port, hue equal; tools/g3_effect_count.py). `a` = throttle, B/Z fire.
Explosions were seen in only one retail dump (vi 7774, orange fireball + debris), never in a matched port capture.
Hypotheses: H-match (explosion rate and colour equal); H-rt64-fx (additive/alpha blend of the fireball differs: hue or
brightness of explosion pixels differs while the rate matches); H-geom (no explosions in port: rate 0 vs >0); H-sim (port
hits fewer targets: rate differs but colour matches -- check with the bolt rate as the input control).
Steps (one game run at a time):
1. Reuse scratch/s6746/retail_flight.sh and port.sh (B/Z every 0.5 s). Extend: retail dumps every 0.25 s (160 dumps,
   flight +2..+41.75 s, check rs64_oracle accepts 160 --fb-dump args), port unchanged (~4 captures/s).
2. Add an orange/explosion class to tools/g3_effect_count.py (e.g. --class orange: R>200, 90<G<190, B<90, box = whole
   picture below the horizon excluding the craft/engine glow area and HUD) and report rate + mean colour per arm,
   bolt class alongside as the input control. Eyeball the top-K explosion frames from each arm side by side.
3. If explosions stay too rare to measure (<3 frames per arm), move on to a second biome (hangar level select in both:
   retail --press dright before the hangar Start, port autopilot "right" at the same point) and repeat the whole-frame match.
