# What is the VI 640 stall waiting on (update_screen stops ~#250, vi-fs loop keeps spinning)?

HYPOTHESIS-ID: vi640-stall-vs-512

s4791: 0/3 default 300 s runs reached 512, no crashes, same binary that reached 512 in s4787 (2/2). Reach-rate runs are exhausted (budget rule 8): do ONE run, same recipe as scratch/agent/s4791_vi640_triplet.sh run 1, and at +60 s (still VI 640) take `sample <pid> 5` of the game process (plus the guest pc-symbol / thread list) before SIGKILL. Hypotheses: H-A main/game thread blocked on a host condvar/semaphore (audio or scheduler handoff, port-only ordering), H-B spin in a guest wait loop (waitFor... gate), H-C swap/present blocked by load. Sample outcome: blocked in semaphore wait => H-A, name the primitive; guest wait function frames => H-B; Metal/SDL present frames => H-C. Control: run to 20 s (VI 640 normal) sampling shows live frames. If the run instead reaches 512, record load and retry once.
