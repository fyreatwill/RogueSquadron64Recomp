# Next work unit
HYPOTHESIS-ID: mission-512-is-demo-or-real
Question: is the 512 @0x690400 phase (3-4 s, then back to title) a real mission or the attract demo? Competing: H-demo (no player input in route reaches it; loops indefinitely), H-real-abort (route Start/inputs enter mission, then game bounces to title = failure/reset path in port, would be a real runtime defect to fix), H-timeout (mission ends via scripted timeout).
Discriminator: in ONE run, log key injections (PROBE_KEYS_FROM_PHASE) vs phase transitions; and check whether title->640 transition happens without any injected key (pure attract). If inputs absent yet 640/512 still occur => H-demo. If inputs present at 640 and 512 ends at title without game-over => H-real-abort -> then attack the boot/route path (pivot item b).
Use tools/vi_progress.py for the metric. Needs one game run (route recipe: scratch/agent/s4950 route soak script).
