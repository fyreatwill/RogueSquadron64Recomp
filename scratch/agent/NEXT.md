# Next work unit (s4456): does ROGUESQ_AI_EVENT_HZ=115 bring port mix rate to retail 114.3/s?

HYPOTHESIS-ID: m5-ai-event-cadence

s4455: port mix calls/s = 60 (unset), 86 (AI_EVENT_DRAIN=768); retail 114.3. Build 120/s both arms.
Work: copy scratch/agent/s4455_run.sh; arms = ROGUESQ_AI_EVENT_HZ=115, ROGUESQ_AI_EVENT_HZ unset (control), 2 each, concurrent, ROGUESQ_LOG_M5_RATE=1.
Outcomes: HZ=115 arm mix ~114/s => event pacing is whole gap; then also characterise crash musyxSynthFrame+5436 (hit ~32 s in all s4455 arms). mix still <<114 => another gate inside the playback loop (runAiAudioStreamPlaybackLoop 0x8008EE08).
Note: no `timeout` binary on this Mac.
