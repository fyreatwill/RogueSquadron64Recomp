# Next work unit (s4443): name the writer of 0x801FB3F0[0]=0x801FB408 (m5-ai-event-cadence)

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4442, offline): the s4441 crash splits into A1 = s4279 wipe, B1 = pool overrun (last pool node 0x801FB3F0 has next 0x801FB408, but init writes 0 there).
Hypotheses: (a) guest LRU/pool code writes it (off-by-one, retail too); (b) host/RT64 or a probe writes it; (c) init ran with a different n.
Discriminator: one build with a store watch/poller on words 0x801FB3F0 and 0x801FB408 from heap init to first change, logging guest PC + value + ENTRY n; positive control: the same watch on 0x801F9CE0 must fire at init (0x8008F8DC). Run arms A (unset) and B (ROGUESQ_AI_EVENT_HZ=115) concurrently via scratch/agent/s4441/run.sh. Then oracle watch phys 0x1FB3F0 in retail for the same word. Note: lldb/otool need approval in headless mode; read the generated C instead.
