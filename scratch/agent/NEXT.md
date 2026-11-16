# NEXT (s7474)
HYPOTHESIS-ID: guest-heap-integrity

Class EB (guest-heap chain integrity): clean with an in-flight plant on L0-L4, L7, L12, L15 (s7472/s7473).
1. Fold SOAK-RESULTS lines for s7473_heapchk_lv_b / _c / _d. For each, read scratch/s7473_heapchk_lv_<k>/out.txt: want
   `score=0`, first arm `plant_detected=1 plant_inflight=1`, every arm heap_bad_nonplant=0 and initMission>=1.
   If any has not run, run it in-session: `zsh scratch/agent/soak_queue/s7473_heapchk_lv_<k>.sh` (HID idle >= 180 s,
   ~15 min each) and move it to soak_queue/done/.
2. All three score=0 with in-flight plant -> close EB H-heap-clean (all 19 levels, header level) in CURRENT-TRUTH item 1, and
   open the next class: either (a) in-block data integrity (guard words / canaries at block tails, rs_malloc padding) or
   (b) the passive `[s4279-BAD]` breadcrumb that prints its 40-row budget at the same front-end point in every arm
   (head=80192C40 len=0 poollen=0): classify whether it is a walker false positive on an empty/rebuilding list or a real
   LRU inconsistency (read apply_s4279_nodeinvariant.py's invariant vs the list op at 0x8008F780..0x8008FF00).
3. Any non-plant heap-bad: arm a write watch on that header word to name the writer; fix root cause with an ORIGIN line.
Hypotheses: H-heap-clean / H-heap-hit / H-walker-wrong (flag histogram other=0 must hold on every arm).
