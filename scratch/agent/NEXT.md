# Next: fold s6290 G3c turn-shake soaks
HYPOTHESIS-ID: g3c-owner-visual
Soaks s6290_g3c_{retail,fps60,wide,both} (queued) write `[g3c]` lines. For each log in scratch/agent/soak_results/: `python3 -I tools/g3c_jerk.py <log>`.
First validity check: cam floats must be a changing matrix with unit-length rows (else 0x80138D20+0x2C is wrong: dump 0x80138D20..+0x70 in flight, re-aim). Also "turning frames" must be >=10 (the sl/sr pattern turned) else arm void.
Outcomes: H-fps60 = FPS60 arm alternation fraction >0.7 while retail ~0.5 or lower; H-pacing = frame spacing histogram uneven (mixed 1/2/3 VI) in any arm; H-aspect = wide arm alone shows it; H-retail = retail arm shows it too. Camera-minus-craft heading sd large in one arm = camera/craft cadence mismatch.
Then: (a) terrain-edge arm table (retail vs dd2/dd3 vs ASPECT; fb dumps), (b) spikes reference check. Parked: dd3 grow-site tagging.
