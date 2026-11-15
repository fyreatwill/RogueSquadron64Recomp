# NEXT (s7399)
HYPOTHESIS-ID: event-msg-payload

s7398 closed class BH (PI/SI I/O-message lifecycle): H-none; upstream osPiStartDma OSIoMesg fill + completion msg fixed
(ROGUESQ_S7398_IOFIX default on). Fold soak s7398_io_levels (SOAK-RESULTS) first: pass = alive + 0 crash + readback PASS rows,
0 FAIL/skip on L4/L7/L12.

Work unit, class BI (event-message payloads, last of the message-queue lifecycle family):
1. Static: for every guest osRecvMesg site whose mq is bound to an ultramodern-delivered event (VI osViSetEvent, SP/DP/AI
   osSetEventMesg, SI cont, PI ring — census rows in tools/s7395_event_census.py + tools/s7392_mesg_census.py), record whether
   the received msg slot is loaded and compared/dispatched on (template: next_recv in tools/s7398_iomesg_census.py, extend it to
   follow the slot load into beq/bne/jalr). Read the msg each ultramodern sender passes (events.cpp vi/ai/sp/dp, cont.cpp,
   pi.cpp) and check it equals the bound msg (or libultra's value).
2. Hypotheses: H-none (every sender passes the bound msg / every consumer discards it), H-payload (a consumer dispatches on a
   msg value librecomp sends differently from libultra -> wrong branch), H-jam (a sender jams where libultra sends, reordering
   a dispatch queue). Discriminator if static does not settle: per-mq log of (msg sent, msg received) on route
   tools/s7392_mq_run.zsh owner + RETAIL=1 with a planted control (send one known bad msg to a test mq, must be reported).
