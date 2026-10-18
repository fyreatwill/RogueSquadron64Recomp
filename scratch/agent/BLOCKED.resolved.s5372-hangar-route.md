# BLOCKED (s5372)
Need: owner decision on direction, or a fix to the key-driven hangar route.
The title->hangar route in soak recipes (s5371, run_a5370.sh, s5369) fails with `nohangar` (title reached at origin 0x790400; 0x6AB400 never appears after 12 key attempts, 200 s). That makes the mission-phase census unmeasurable, and every thread parked on it (free-list head/walk guards, A9 unreached sites) cannot progress. M5 plan is closed (s4968); M3 is parked pending a discriminator.
Tried: s5369 (300 s runs), s5370 (title census), s5371 (queued soak) - all nohangar or title-only.
Question: (a) debug the winctl key driver / hangar route (did a macOS focus or key-timing change break it? s5094/s5099 soaks reached hangar earlier on 2026-10-17), or (b) pivot to the renaming sweep / retail-entry revisit?
