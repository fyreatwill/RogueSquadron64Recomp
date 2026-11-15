# NEXT (s7402)
HYPOTHESIS-ID: replaced-libultra-side-effect-contract

s7401 closed class BK (argument contract, H-none + latent flags fix ROGUESQ_S7401_FLAGFIX default on).
Fold first: soak s7401_flags_levels (L4/L7/L12, pass = alive, 0 crash, 1 [s7401-ctl] PASS(retail), 0 [s7401-odd]).

Work unit, class BL (replaced-libultra SIDE-EFFECT contract: guest-visible state retail writes that the port does not):
1. For each of the 64 live replacements (tools/s7400_replaced_contract.py rows), list the guest globals / structs retail libultra
   mutates as a side effect (e.g. __osRunningThread / __osRunQueue, __osViCurr/__osViNext, __osContPifRam, __osMaxControllers,
   __osEepromTimer, __osSiAccessQueue, osTvType, __osCurrentTime/__osBaseCounter, __osTimerList, OSThread.state/priority/queue
   fields, OSMesgQueue.validCount/first/mtqueue/fullqueue) from /tmp/s7392.dis (sw/sh/sb to %hi/%lo pairs inside the original
   libultra body), versus what the replacement writes into rdram.
2. Join with guest READERS that are live (non-replaced, s7401 live()): a global retail writes and a live game function reads
   but the port never writes = H-unwritten. A field the port writes with a different encoding = H-encoding.
3. Hypotheses: H-none, H-unwritten, H-encoding. Static first (tool tools/s7402_side_effects.py); runtime only for a flagged row,
   two-arm in ONE build with a planted control (s7400/s7401 model). Fix behind a default-on env, =0 old.
