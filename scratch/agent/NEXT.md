# NEXT: cross-level audio-clocked split audit (offline)
HYPOTHESIS-ID: g3-audio-split-audit

State (s6805): every dt-pinned retail/port pair split so far (lvl3,4,7,8,9,10,12,14,15,16 and the lvl9 death camera) lands
on a song end (handle 0x8010C0E0 -> 0), and song windows were VI/AI-buffer equal where measured (lvl10 332/634 vs 334/640,
lvl9 death jingle 332/634 vs 334/640). Never tabulated across all levels/songs at once.
Hypotheses: H-parity (every song window is VI- and buffer-equal within ~1%: the split class is purely mupen's slower game
rate, close the class); H-rate (some song/level has a port length != retail: an AI rate / sample-rate / tempo defect like
G2b's 32006 Hz crawl, root-cause it); H-gameend (some song ends on a game event, not audio: equal ticks, unequal VI).
Discriminator, offline only, no game run: for every scratch/s67xx pair dir holding a retail oracle.log and a port rand.txt
with the 8010C0E0 block, run tools/g3_song_windows.py RETAIL PORT; build one table (level, song id, retail ticks/VI/bufs,
port ticks/VI/bufs, VI ratio, buffer ratio). Positive control: lvl10 (scratch/s6763) must reproduce 332/634 vs 334/640.
Find pairs: `ls scratch/s67*/ | ...; grep -l 'm=8010c0e0' scratch/s67*/**/oracle.log`. Write the table into the session
entry; land the batch script as tools/g3_song_audit.py. If H-rate: next unit is the AI rate for that song.
