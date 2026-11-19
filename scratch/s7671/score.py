#!/usr/bin/env python3
# s7671 scorer: for every forced effect ([s7671-fx] arm, one per autopilot key) report the first game osMotorStart after it
# (did the game's own SI service play it = positive control), the [rumble] run that contains it, and for each hangar entry /
# initMission the motor state and the most recent fx arm (ms before). Verdict: stuck if motor ON at a hangar entry or any
# game LONG run (plant excluded); control FAIL if no fx arm reached osMotorStart or the plant LONG is missing.
import sys, re
L = open(sys.argv[1], errors='replace').read().splitlines()
state = 0; last_fx = None; fx = []; ev = []; runs = []; starts = []; inject_end = False; plant = 0; longs = []; abort_fx = []; inits = []
for ln in L:
    m = re.search(r'\[s7671-fx\] arm key=(\d+) btn=(\S+) .*susp=(\d) wall_ms=(\d+)', ln)
    if m: last_fx = (int(m.group(1)), m.group(2), int(m.group(4)), int(m.group(3))); fx.append(last_fx)
    m = re.search(r'\[s7669-pak\] fn=(\S+) .*wall_ms=(\d+)', ln)
    if m:
        fn, t = m.group(1), int(m.group(2))
        if fn == 'osMotorStart': state = 1; starts.append(t)
        elif fn == 'osMotorStop': state = 0
        elif fn == 'osMotorInit': inits.append((t, state))
    if 'hangarmenu-a0-entry' in ln or 'initMission] call' in ln:
        ev.append(('hangar' if 'hangar' in ln else 'initMission', state, last_fx))
    if 'beginMissionEndTransition' in ln and last_fx: abort_fx.append((state, last_fx))
    if 'inject end' in ln: inject_end = True
    m = re.search(r'\[rumble\] run n=(\d+) ms=(\d+) max_s=(\S+)( LONG)?\s+long_total=\d+ wall_ms=(\d+)', ln)
    if m:
        n, ms, t = int(m.group(1)), int(m.group(2)), int(m.group(5)); runs.append((t - ms, t, ms))
        if m.group(4):
            if not inject_end or n <= 2: plant += 1
            else: longs.append(ln)  # with a train, forced runs are LONG by design; the verdict uses the tail metric
hit = 0; lat = []
for k, b, t, s in fx:
    nxt = [x for x in starts if t <= x <= t + 1500]
    if nxt: hit += 1; lat.append(nxt[0] - t)
inrun = sum(1 for k, b, t, s in fx if any(a - 50 <= t <= e + 50 for a, e, _ in runs))
print(f'fx_arms={len(fx)} fx_susp={sum(1 for f in fx if f[3])} fx_to_start={hit} lat_ms(min/max)={min(lat) if lat else "na"}/{max(lat) if lat else "na"} fx_in_rumble_run={inrun}')
print(f'motor_starts={len(starts)} rumble_runs={len(runs)} max_run_ms={max((r[2] for r in runs), default=0)} plant_long={plant} game_long={len(longs)}')
print('events (kind, motor_state, last fx key/btn, ms since fx):')
for k, s, f in ev: print('  ', k, s, (f[0], f[1]) if f else None, None)
print('osMotorInit rows (game Init+Stop = serviceRumblePakMotors / pak re-probe): t, motor_was, last_fx_key, ms_after_fx, run_live')
for t, st in inits:
    pf = [f for f in fx if f[2] <= t]; f = pf[-1] if pf else None
    live = any(a <= t <= e for a, e, _ in runs)
    if f and t - f[2] < 1500: print('  ', t, st, f[0], t - f[2], live)
for l in longs: print('  LONG', l)
# tail metric: ms from the last forced arm (any, incl. train re-arms) to the end of each rumble run. A game-ended effect
# ends <~400 ms after its arm; the planted stuck run (no arm) has tail >= 3000. Stuck = tail > 800 ms with an arm before it.
import bisect
at = sorted(f[2] for f in fx); tails = []
for a, e, ms in runs:
    i = bisect.bisect_right(at, e) - 1
    tails.append((e - at[i]) if i >= 0 and at[i] >= a - 50 else None)
tv = [t for t in tails if t is not None]
stuck_tail = [t for t in tv if t > 800]
trains = sum(1 for ln in L if '[s7671-fx] train end' in ln)
print(f'train_ends={trains} runs_with_arm={len(tv)} tail_ms max={max(tv) if tv else "na"} stuck_tail={stuck_tail} runs_ms_top={sorted((r[2] for r in runs), reverse=True)[:6]}')
bad = [e for e in ev if e[0] == 'hangar' and e[1] == 1]
if plant < 1 or hit < 1: print('VERDICT control FAIL'); sys.exit(3)
if stuck_tail or bad: print('VERDICT stuck', bad); sys.exit(1)
print('VERDICT clean'); sys.exit(0)
