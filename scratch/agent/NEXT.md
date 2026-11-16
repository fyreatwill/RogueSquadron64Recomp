# NEXT (s7473)
HYPOTHESIS-ID: guest-heap-integrity

Class EB (guest-heap chain integrity) OPEN since s7472: walker ROGUESQ_S7472_HEAPCHK=1 landed (src/main/upstream_compat.cpp
s7472_check), run 2 L4/L7/L12 dd4 16:9 + L15 dd8 21:9 HOLD=220 = 0 bad headers, plant PASS but in the front-end phase.

1. Fold scratch/agent/SOAK-RESULTS.md line for s7472_heapchk_inflight (PLANT_S=150 => plant in flight on L4). Read
   scratch/s7472_heapchk_inflight/out.txt: expect `arm=l4 ... plant_detected=1` and grep log_l4.txt that `plant SET` comes AFTER
   `[initMission] call#1`. If the soak has not run yet, run it in-session: `zsh scratch/agent/soak_queue/s7472_heapchk_inflight.sh`
   (needs HID idle >= 180 s, ~22 min) and move it to soak_queue/done/.
2. If in-flight control PASS and 0 non-plant bad headers: widen to the remaining levels in one recipe pair (make the arm list an
   env in tools/s7472_heapchk_recipe.zsh: L0-L3,L5,L6,L8-L11,L13,L14,L16-L18 alternating dd4 16:9 / dd8 21:9) and queue them;
   then close EB H-heap-clean once all 19 levels are walked with a same-recipe in-flight plant.
3. If a non-plant heap-bad appears: arm a write watch on that header word (tools/oracle or ROGUESQ_DEBUG_WRITE recipe) to name
   the writer; fix root cause with an ORIGIN line.
Hypotheses: H-heap-clean / H-heap-hit / H-walker-wrong (flags {1,2,6} valid; any new flag value on every arm at load = layout
gap, check rs_malloc a1 bits before scoring).
