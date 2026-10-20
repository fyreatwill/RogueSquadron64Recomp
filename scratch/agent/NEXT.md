Single next work unit (s5617): identify the writer of b14=2 / the natural mission-end trigger seen in nopoke_b (g4 -> g4s1b2 -> g6s1b2 -> g0b2).
Hypotheses: H4a mission timer/objective completes naturally (a real win condition met by god-mode flight); H4b a game-side event (enemy count, wave) sets it; H4c an artifact of our runtime (stale flag, audio gate).
Discriminator: lldb break (or write-watch) on the b14 byte and 800FB190 with a0 logged + backtrace, in a nopoke run with ROGUESQ_MISSION_WIN_NOPOKE=1; positive control: same watch must fire in a poked p100 run. Run as lldb-armed variant of m6_god_common.sh, 2 runs concurrently.
HYPOTHESIS-ID: m6-mission-endurance
