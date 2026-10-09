# Next work unit (s4445): chain drain accounting for the s4441 B1 crash

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4444): B1 = head 0x801FAB68 len=1 -> head=0 -> null deref; chain len 256 is walker cap. Drain writer unnamed.
Hypotheses: (a) returns stop because a retire path needs audio-task completion the port lacks; (b) retail drains too but survives by cadence/size; (c) leak in a guest path we mis-execute.
Discriminator: offline, from [s4234-ENTRY]/[s4254-CHAIN] rows in /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4441/port_*.log, count head advances vs tail inserts per 1000 ENTRYs; flatlined inserts -> (a)/(c); then oracle (tools/oracle/README.md) for retail rate.
