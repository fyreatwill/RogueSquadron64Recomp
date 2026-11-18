# NEXT (s7609)
HYPOTHESIS-ID: guest-address-keyed-host-state

Class TK closed s7608 (tools/s7608_tk_census.py --controls --witness: 119 lines, 0 open, controls 4/4, witness PASS;
s7394fix::holder re-keyed from OSId to a host-thread incarnation token, ROGUESQ_S7608_TK=0 = old).
Next idiom class MK: host state keyed by a GUEST STRUCT ADDRESS (OSMesgQueue*, OSThread*, OSTimer*, OSIoMesg*, heap block)
that survives the guest re-creating, freeing or re-using that struct. s7393 showed the game re-creates live queues
(8010FEE0 heap mutex 10x per route, queueDeferredClearRequest); TK showed OSThread structs are re-used by new incarnations.
Any host table keyed by the address (recv_stat_for(mq), ultramodern external-message / event-queue registrations
(osSetEventMesg, osViSetEvent, VI/SI/PI/SP/DP mq globals), timer lists, s4264 maps, s7394 MQ, osCreateMesgQueue_recomp hooks)
that is not refreshed on re-create keeps the old queue's state (counts, blocked lists, pending flags) for the new one.
Enumerate: grep host containers/arrays/globals whose key or value is a PTR(OSMesgQueue)/(uint32_t)mq/ctx->r4 address, plus
every ultramodern global holding a guest queue pointer. Classify: refreshed-on-create (osCreateMesgQueue path resets it),
value-only (re-read each use), diag-gated, BAD (default-path decision reads the stale entry).
Contract: a default-path read of address-keyed host state either sees the current incarnation of the struct or the stale
entry is retail-equivalent (named reason).
Hypotheses: H-clean, H-bad-gated, H-bad-live.
Tool tools/s7609_mk_census.py --controls: (1) plant an mq-keyed std::map counter read on a default path -> OPEN; (2) drop a
row -> OPEN; (3) remove a rowed refresh-on-create reset -> OPEN; (4) plant a cached mq pointer compared after re-create -> OPEN.
Second source: runtime witness from an existing log (osCreateMesgQueue re-create of a live queue: [s7393] rows, or a
compiled witness through the real ultramodern queue functions) showing every rowed entry refreshes between incarnations.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
