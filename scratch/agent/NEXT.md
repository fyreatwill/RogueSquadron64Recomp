# NEXT: retail control for the ~19-VI guest AI feed gap at scene transitions
HYPOTHESIS-ID: g3-transition-ai-gap

State (s6806): port guest skips osAiSetNextBuffer (0x8008EE08/0x8008EE84) for 19 VI (~317 ms) at transitions
(lvl19 pre-mission ticks -1 VI 2016/3451; lvl3 t3803; lvl10 t5053; tools/g3_ai_gaps.py). G2b saw the same as ~315 ms
empty SDL queue at boot, hangar entry, mission load, game over in every arm. Retail oracle logs never cover a
transition: the exec trace is armed by --debug-write at DWARM=85 s (tools/g3_mission/run.sh), after mission entry.
Hypotheses: H-retail (retail's guest also stops feeding AI ~19 VI during the load: synchronous load blocks the audio
thread, then retail-faithful, close); H-port (retail gap is shorter; our PI/DMA/overlay load or thread scheduling
starves the audio thread, so root-cause it); H-length (retail gap exists but its length differs, a pacing artefact).
Discriminator: ONE retail oracle run with the AI exec-trace rows live from boot (drop --debug-write so the trace runs
from boot, or set DWARM small; check README line ~260: "from boot without one"), same save/recipe as an existing port
pair (lvl19 s6773/r19 has two port gaps pre-mission; or lvl3 s6777), through title -> level select -> mission load.
Then g3_ai_gaps.py on both arms; report the gap length at each transition in VI. Positive control: the in-mission
retail rows must show the usual ~1.91 buf/VI (gap <=1 VI), and the port arm (re-run in same iteration, same build)
must reproduce its 19-VI gaps. If H-port: instrument the audio thread's last osAiSetNextBuffer vs what the game
thread is doing during the 19 VI (lldb sample or the G1E timeline).
