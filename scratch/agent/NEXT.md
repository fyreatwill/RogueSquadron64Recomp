# NEXT: stop the death latch, not refill after it
s5730 showed health=0 precedes every mission exit; post-hoc revive (refill after dead=1) cuts cycles 3->1 but cannot prevent the game-over latch.
H-LATE: latch is set on the frame health<=0 before our refill -> a per-frame clamp health>=1 at damage-resolve (or hooking the game's death check) drives cycles to 0 and flight outlives 541 s.
H-OTHER: cycles stay >0 under clamp -> a second fail condition exists; log the writer of the results-state change (PC attribution) at the dead=1 transition.
Control: [god-dead] lines still fire (near-death) and clamp counter > 0.
Build both arms in one iteration (rule 13), run concurrently.
HYPOTHESIS-ID: g1-gameover-cause
