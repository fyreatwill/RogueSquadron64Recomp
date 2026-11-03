# NEXT: fold the s6834 boot-freeze hunt
HYPOTHESIS-ID: boot-freeze-capture

Context: s6814 a30_s2 froze at title boot (fs=39, VI origin held, audio flowing, no crash; 1 in 11 boots). s6834 landed
tools/boot_freeze_hunt.sh + tools/sample_game_threads.py (controls pass) and queued s6834_bootfreeze_hunt_a/b (22 boots).
Step 1: SOAK-RESULTS tail; then `cat scratch/s6834/hunt_{a,b}/*freeze*.threads.txt` (if any) and the soak result logs.
Outcomes:
- FROZEN captured: compare a vs b. H-lost-event = [Game] MAIN parked in osRecvMesg (name the guest caller: e.g.
  waitForPostSwapAck/waitForPrevFrameDone) while SP Task / Gfx threads idle in semaphore waits -> the event that should post
  that queue was dropped; read the runtime path that posts it (ultramodern events.cpp / rsp task completion / VI) and fix.
  H-spin = a guest thread on CPU in both captures in the same guest function -> name its loop exit condition.
  H-host = a runtime thread blocked on a mutex/cond held by another -> name the lock pair.
- 22/22 clean: the freeze rate is below ~1/22; record it, re-queue the two hunts once more (cheap, loop-run), and take the
  next engineering rung meanwhile (owner items still pending: FPS60 feel, G1d/G3c sheets).
- EXITED / crash lines: a datum; read boot*_crash.txt.
