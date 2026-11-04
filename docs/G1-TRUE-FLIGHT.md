# G1 true flight seconds

Session 6867, 2026-11-03. Tools: `tools/audit_hold_flight.py`, `tools/audit_hold_segments.py`. New runs print `inits=` and
`flight_s=` in their summary (`scratch/agent/m6_god_common.sh`). All runs below: alive at end, 0 VI stalls, 0 crash lines.

Terms. `hold` is what the harness reported and counts from its gate. `flight` is seconds after the first `[initMission]`.
`inits` counts `[initMission]` lines; above 1 the mission restarted, so the time is not one continuous mission. `longest` is the
longest stretch between two inits. Keys stop at about 520 s, so a final segment can include time idle on a screen, and any init
after that reads the last key time. Treat the final segment of a multi-init run as an upper bound (flagged `*`).

## Owner path, 4:3, FPS60 + dd4

| Level | Before (reported hold -> flight) | Now | Run |
| --- | --- | --- | --- |
| 1 | 302 -> 229 s (s6832) | 305 s, inits 1 | `g1_lvl1s6867truehold` |
| 5 | 300 -> 231 s (s6788) | 306 s, inits 1 | `g1_lvl5s6865regen` |
| 10 | 304 -> 124 s (s6832) | 302 s, inits 1 | `g1_lvl10s6865truehold` |

One run each. Longest same-hash run after `[initMission]`: none above 60 frames on lvl1 and lvl10, while the same runs flag 366 and
1127 frames before it, so the frozen-frame check was live. dd4 was on (`[ddbundle]`). FPS60 was on: 40.5 and 59.9 frames/s against
30.0 for the lvl1 dd1 control. Those rates are under recipe logging, which costs frames on lvl1 dd4 (s6788 entry in CURRENT-TRUTH);
they are a witness that FPS60 was live, not a frame-rate result.

Not held to 300 s of flight: FPS60+dd3 (lvl5 231 s, no lvl1 or lvl10 run found), FPS60+dd2 on lvl10 (no run found; lvl1 307 s and
lvl5 305 s). dd4 is the heavier setting, so these are expected to hold, but that is inference.

## Wide bundles, FPS60 + dd4

| Bundle | Level | Reported hold | Flight | Longest | Session |
| --- | --- | --- | --- | --- | --- |
| 21:9 | 9 | 305 s | 261 s | 264 s | s6859 |
| 21:9 | 17 | 305 s | 275 s, inits 5 | 117 s | s6859 |
| 16:9 | 1 | 302 s | 253 s | 256 s | s6858 |

The s6860 load pass on levels 0-8, 10-16 and 18 flew 52-129 s, not about 140 s. Level 5 flew 148 s (s6860b).

## Retail settings, 660 s holds (s5985-s6005, runs of 2026-10-23)

The gate fired 2-11 s after `[initMission]` on every level, so these holds are real time in mission. The gap found in s6865 does
not apply to them. What they did not show is one continuous mission: `mission_cycles` read 0 on levels where the mission restarted
(lvl11 inits 3, lvl14 inits 2), and it read 0 on lvl0 (inits 3) and lvl1 (inits 2) too.

| Level | Inits | Longest | Segments (s) |
| --- | --- | --- | --- |
| 0 | 3 | 302* | 191 176 302 |
| 1 | 2 | 345* | 321 345 |
| 2 | 2 | 357 | 357 315 |
| 3 | 1 | 672 | 672 |
| 4 | 2 | 376* | 297 376 |
| 5 | 1 | 669 | 669 |
| 6 | 6 | 267* | 169 52 60 52 72 267 |
| 7 | 4 | 299* | 161 96 112 299 |
| 8 | 2 | 425* | 249 425 |
| 9 | 2 | 459* | 213 459 |
| 10 | 1 | 672 | 672 |
| 11 | 3 | 289* | 189 188 289 |
| 12 | 1 | 669 | 669 |
| 13 | 1 | 664 | 664 |
| 14 | 2 | 461* | 205 461 |
| 15 | 1 | 669 | 669 |
| 16 | 8 | 374* | 59 36 52 36 32 52 28 374 |
| 17 | 8 | 324* | 75 46 34 46 68 22 54 324 |
| 18 | 1 | 669 | 669 |

Single-init levels 3, 5, 10, 12, 13, 15, 18 are the only ones shown to stay in one mission for 300 s, and those also stop receiving
keys at about 520 s. On the rest, the blind autopilot's mission ended before 300 s and the harness restarted it. Why each one ended
(death, failure or completion) was not checked here. Those runs still show 0 crashes and 0 stalls across the restarts. Mission
outcomes are owner playtest, and crash and repeat-hold hunting is parked (G4), so no further holds were queued for these.
