Single next work unit (s5613): qualify the win route. Run twice more: env TAG=s5613_real_a HOLD=420 STOP=500 LATE=95 LATE_NOSTART=1 LKEY=a XENV="ROGUESQ_LOG_LEVEL=1 ROGUESQ_MISSION_WIN=300 ROGUESQ_MISSION_WIN_REAL=1" zsh scratch/agent/m6_god_common.sh (queue as soaks). Then decide from the log whether the post-win 0x690400 is mission 2 or a replay of mission 1 (compare level-id word / objective counters get(1..10) at 0x80138060+ before and after; log mission id).
Hypotheses: H1 return to 0x690400 is mission 2 (level id changes); H2 replay of mission 1 (level id same, counters reset); H3 hangar route with different mission loaded.
Discriminator: level-id / counters at second 0x690400 vs first.
HYPOTHESIS-ID: m6-mission-endurance
