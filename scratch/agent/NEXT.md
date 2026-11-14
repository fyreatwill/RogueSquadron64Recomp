# NEXT (s7307): G5e - fold the queued 21:9 fog hold, then (if clean) close G5e pending the owner's look
HYPOTHESIS-ID: g5e-far-fog
State (s7306): 21:9 L1 toggle sheet: FOG_ALT=1,3,1 is null in every band (lever ctl 8/27/17% PASS), 0 crash -> safe, weak melt.
Unit: if SOAK-RESULTS has an s7307_219_dd8_fog_hold line, fold it (arms l1f/l1n/l5f/ctl; pass = all alive, 0 crash, 60/s beyond route,
[s7302] line in l1f/l5f and absent in l1n, ctl dips to flat-30). If it is absent (gated on idle), run it yourself:
`zsh scratch/agent/soak_queue/s7307_219_dd8_fog_hold.sh` (~30 min, needs idle >=180 s and an unlocked screen).
Outcomes:
  - H-hold: clean -> FOG_ALT qualified at both owner screens. Mark G5e awaiting the owner's look and move to the next G-ladder rung.
  - H-crash/dip at 21:9 only -> root-cause it (backtrace) before anything else.
Optional, only if the owner asks for more haze at 21:9: sweep ke 2 / 2.5 at 21:9 with tools/s7306_fog_219.zsh l1k2:1:1,2,1.
