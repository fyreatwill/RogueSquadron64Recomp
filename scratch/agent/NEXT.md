# NEXT: remaining front-end screens vs retail (G3)
HYPOTHESIS-ID: g3-frontend-remaining

Done: title, SELECT GAME (fixed s6781), level/craft select, pause, debrief (s6778-s6781). Stack-send class closed s6782.
Unit: OPTIONS screen + its sub-screens (controller settings, sound/music test, records/medals) and ERASE GAME, port vs
retail oracle, same press script both arms.
1. Recipe: copy the s6779-s6781 menu runner (scratch/s6781 state.py / the s6779 press scripts; title decode
   --w 512 --h 448 --bases 790000 --win 64,1024 --winx 85,1191). Navigate SELECT GAME -> options entries by d-pad.
   Retail: oracle --fb-dump on dbg_vi (s6778 fix), same presses at retail timing.
2. Per screen: tools/g3_oracle_match.py distance vs mismatch control (a different screen) and a flip control.
3. Arm all relevant xtrace marks in BOTH arms: pollServiceMessageByte receive 0x800B4004 and the song-worker doorbell
   receive 0x800C3B4C (ROGUESQ_XTRACE_MEM / oracle --exec-trace), to see whether the SELECT GAME image worker and
   tickSongAssetLoadWorker (0x800C5834, menuSubtype02Handler 0x800C30C8) ever coexist (s6782 residual: shared queue
   0x80138920, two consumers).
Hypotheses per screen: H-match (d within median band of the s6779 controls), H-diff-sim (port state/timing differs: find
the writer like s6781), H-diff-render (same RDP stream, different pixels: RT64). Cross-consumer: H-disjoint (never both
pending: s6782 residual dead) vs H-overlap (a doorbell read at 0x800B4004 or a completion at 0x800C3B4C).
