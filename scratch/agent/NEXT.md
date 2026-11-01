# NEXT: G3 -- mission 5 in-flight sim/frame match with dt pinned (s6753/s6754 method)
HYPOTHESIS-ID: g3-mission5-pinned

s6755 closed lvl4: the tick-2302 event is the song-end bit 0x100 (tickSongFadeTimer, isSongHandleActive), audio
clocked; the song is the same length in AI buffers in both arms. Fixed the duplicate-VI defect in the VI thread (events.cpp
deadline rounding; ROGUESQ_VI_TRUNC_DEADLINE=1 = old). The rest of the tick gap is retail frame drops (pacing).
Expect audio-clocked script events to keep landing at different ticks under pinned dt: time them in AI buffers
(tools/g3_ai_clock.py), not ticks.

Work:
1. Mission 5 save: `python3 tools/g3_eep_patch.py scratch/s6754/lvl4.eep scratch/s6757/lvl5.eep` with +0x31=4 (read
   the tool's usage for the arg form).
2. Arms (one run at a time): copy scratch/s6756/port.sh and retail.sh (they carry the song-state spec + dt pin), point
   SAVE_FROM/EEP at lvl5.eep, add XA="--exec-trace-also 0x8008EE08 --exec-trace-also 0x8008EE84" to retail (AI buffer
   rows; the port markers are built in).
3. Analyse: tools/g3_rand_ticks.py (sim-tick keyed rand diff), g3_tick_mem.py for 0x8010C9E0 (event mask) and
   0x8010C0E0 (song handle), g3_ai_clock.py for audio-clocked events, g3_frame_snap.py / g3_oracle_match.py for frames.
Outcomes: sim identical up to an audio-clocked event = H-match (record its AI-buffer timing); a non-audio divergence
before any event = a real port defect -> bisect with xtrace-mem as s6751-s6753.
Positive control: the s6754 pair through g3_rand_ticks.py -> identical for ticks 0-2301.
