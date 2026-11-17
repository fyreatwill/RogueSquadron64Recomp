# NEXT (s7547)
HYPOTHESIS-ID: class-gg-host-retained-guest-ptrs

Class GF CLOSED s7546 (tools/s7546_gf_census.py rc 0, controls 5/5). Successor idiom class GG: guest pointers the HOST keeps
past the guest call that handed them over (OSMesgQueue* for osSetEventMesg / osViSetEvent / osSetTimer / PI-SI-EEPROM requests, OSTimer*,
OSIoMesg*, VI framebuffer/mode pointers, audio buffers). The guest frees and reuses heap objects (s7545: thread nodes within 2 s), so
a host-retained pointer to a freed object delivers messages / writes into whatever now lives there.

Work unit: static census tools/s7547_gg_census.py (--controls), offline.
- Enumerate host stores of a guest PTR into host-lifetime state (statics, events_context members, timer maps, rsp/pi queues):
  grep `PTR(OSMesgQueue)|PTR(OSTimer)|PTR(OSIoMesg)|PTR(void)` members/globals in ultramodern/src/{events,timer,mesgqueue,misc_ultra}.cpp,
  librecomp/src/{pi,eep,cont,sp}.cpp, src/main.
- For each: who registers it in the guest (generated code caller), is the object static (.bss/.data, never freed), or heap
  (rs_malloc), and is there a guest unregister (osSetEventMesg(ev, NULL), osStopTimer) before the free?
- Classify H-static (object in .data/.bss), H-unreg (heap but unregistered before free), H-stale (heap, freed while still registered -> fix:
  drop registration on free or validate at delivery, =0 knob), H-dead.
- Controls: a planted registration of a heap pointer with no unregister -> OPEN; deleted rule -> UNCLASSIFIED.
Hypotheses: H-static (all retained pointers are static objects), H-unreg (heap ones are unregistered first), H-stale (some are not).
Runtime witness only if a row is H-stale: reuse s7545's thread-watch pattern on the object address.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
