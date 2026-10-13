# Catch the VI 640 freeze with a STATE-gated sample (not wall-clock)

HYPOTHESIS-ID: vi640-stall-vs-512

s4792: wall-clock sample at +65 s missed the freeze (run left 640 for 1024 at 62.7 s, update_screen kept advancing to #3558). Rewrite scratch/agent/s4792_sample.sh to poll game.log every 2 s (the `[phase]`/update_screen counter lines) and run `sample <pid> 5` only when the update_screen count has not advanced for 10 s while still VI 640; also sample once at 20 s as control. Loop up to 3 runs until one freezes (stop at first freeze; a run that exits 640 normally is a "pass", record time). Outcome: cvwait/semaphore frames on Gfx/SP Task/main => H-A (name primitive from caller frames); guest wait function frames => H-B; Metal/SDL present frames => H-C.
