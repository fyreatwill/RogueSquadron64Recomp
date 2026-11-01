# NEXT: G3 render fidelity -- lvl1 flight 20-60 s (laser fire, explosions, smoke, transparency) vs retail
HYPOTHESIS-ID: g3-flight-effects-oracle-diff

s6744: first ~15 s of lvl1 flight with HUD = H-match (d 4.4-5.8 vs median 17-21, monotonic). Brightness gain = decode
convention, use g3_oracle_match.py --dec shift for shaded 3D.
Hypotheses: H-match (deterministic with no input, effects identical); H-desync (no-input flight diverges once AI fires:
matched port times stop being monotonic / best d rises toward the median -- then compare only per-element, not frames);
H-rt64-fx (alpha/blend/fog effects differ: tile heat concentrated on explosions/smoke/bolts while terrain matches);
H-geom (missing/extra objects).
Steps (retail runs first, one game run at a time):
1. Retail: scratch/s6744/retail_flight.sh with RD=retail2, a dump series from ARM so dumps start 20 s after flight
   start: edit the dump loop to d=20+0.5*i, i 0..79 (MAX_FB_DUMPS 96), SECS=185.
2. Port: env SAVE_FROM="$HOME/Library/Application Support/Mupen64Plus/save/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep"
   AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,50:start SECS=140 CAP0=85
   zsh tools/g3_port_capture.sh scratch/s6745/port1   (flight starts ~69.5 s)
3. python3 tools/g3_oracle_match.py scratch/s6744/retail2/oracle.log scratch/s6745/port1 scratch/s6745/m --w 512
   --bases 690000,620000 --h 446 --win 60,1024 --winx 85,1191 --dec shift
   Control: same-run median; monotonicity of matched port times; visual sheet of best and worst pairs.
