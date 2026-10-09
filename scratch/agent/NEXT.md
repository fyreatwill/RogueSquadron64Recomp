# Next work unit (s4456): does ROGUESQ_AI_EVENT_HZ=115 bring port mix rate to retail 114.3/s?

HYPOTHESIS-ID: m5-ai-event-cadence

s4455: port mix calls/s = 60 (unset), 86 (AI_EVENT_DRAIN=768); retail 114.3. Build 120/s both arms.
Work: rate gap CLOSED (hz115 = 114-116/s). Now: soak 4+4 hz115 vs unset, compare crash rate; then compare active-voice count at mix entry vs retail.
Outcomes: HZ=115 arm mix ~114/s => event pacing is whole gap; then also characterise crash musyxSynthFrame+5436 (hit ~32 s in all s4455 arms). mix still <<114 => another gate inside the playback loop (runAiAudioStreamPlaybackLoop 0x8008EE08).
Note: no `timeout` binary on this Mac.
