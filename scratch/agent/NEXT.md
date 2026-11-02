# NEXT: what ends the lvl9 death camera (retail ~t2210, port t2250)
HYPOTHESIS-ID: g3-deathcam-end

State (s6804): post-death screen sequence matches retail frame-for-frame except the HUD-off death camera: retail 33
frames / t2130-2210 at a flat 4 VI/tick, port 117 frames / t2133-2250 at 2 VI/tick. Its end is the lvl9 sim split
t2217 (s6763: rand caller retail 8007132c vs port 80054174). Data: scratch/s6804/pair (retail.bin, port.bin, oracle.log,
port.rand.txt, segcmp.txt); rerun with tools/g3_mission/death_pair.sh OUTDIR.
Hypotheses: H-audio (camera waits for a death sound/voice/stream to finish: audio clock, the known song-end split class,
then retail-faithful pacing, close); H-vi (an osGetCount/VI-count timer: port VI 234 vs retail ~320 says no unless the
start differs); H-frames (counter bumped per rendered frame / gfx task done: retail renders fewer frames per tick in
the camera, so a frame-counted wait ends LATER in ticks on retail - opposite sign, unless retail skips frames);
H-sim (tick-counted; would give equal ticks - refuted unless the start tick differs).
Discriminator, offline first: disassemble around 8007132c and 80054174 (the first callers that differ at t2217) and the
HUD-hide flag writer for the death camera (find via the port census HUD-off edge + ROGUESQ_DEBUG_WRITE on the flag);
name the counter the end test reads. Then ONE pair run (death_pair.sh) adding that word to both xtrace specs
(RS64_XTRACE_MEM / ROGUESQ_XTRACE_MEM at 800FA730) plus the AI/audio-voice state words: whichever word reaches its end
value on the same tick-relative schedule in both arms names the clock. If H-audio: document as retail-faithful pacing
(close). If port-only: root-cause.
