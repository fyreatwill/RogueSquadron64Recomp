# NEXT (s7543)
HYPOTHESIS-ID: class-gd-replacement-yield-atomicity

Fold first: SOAK-RESULTS lines for s7540_rwait_cost (fps NODRAIN=3 vs =1 vs drained, tools/g1e_level_fps.py; needs AC). If it
voids out (SOAK_MAX_VOIDS), rerun in-session with ALLOW_SLOW=1 ALLOW_BATT=1 and score in-run only.

Work unit: class GD idiom census (offline, one tool, the s7538/s7542 model). GC (s7542) showed every host write into guest RAM is
ordered vs its signal, and 58 rows run on a guest thread inside a libultra replacement. Guest threads run one at a time, so the
open question is atomicity: does any replacement YIELD (rs64_preempt_point, run_next_thread_and_wait, resume_thread_and_wait,
a blocking wait, dequeue_external_messages -> do_send) BETWEEN two dependent guest-struct stores (OSMesgQueue msg slot vs
validCount/first, OSThread queue/next/priority/state, OSTimer fields, OSIoMesg fields before do_dma, cont data buffer), so another guest
thread can observe a half-updated struct that hardware (interrupts off inside libultra) never shows?
Tool: tools/s7543_gd_census.py: per replacement function in the GC H-guest-thread rows, list guest-struct stores and yield calls in
body order (follow one level of callee); classify H-atomic (no yield between dependent stores), H-yield-safe (yield, but the struct is
consistent at that point: name the invariant), H-torn-OPEN. --controls: plant a preempt call between do_send's slot store and
validCount++ -> OPEN; rule deleted -> unclassified. Exit 0 only with 0 OPEN / 0 unclassified.
Expected outcomes: all rows atomic/yield-safe (close GD), or a named H-torn-OPEN row (next unit: same-run A/B with a planted yield
counter, then fix by moving the yield).
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
