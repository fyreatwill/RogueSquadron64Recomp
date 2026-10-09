# Next work unit (s4446): name the retire path that advances head

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4445): port chain only fills; head advances 91x in first 1000 ENTRYs then ~0/1000 (A1/A2), tail ~1/ENTRY.
Hypotheses: (a) retire needs audio-task completion the port lacks; (b) retail also drains little (cadence); (c) mis-executed guest path.
Discriminator: oracle retail run (tools/oracle/README.md, positive control first): watch head word of the chain (phys of 0x801F9CE0-region head var) over title; count head advances/1000 inserts. Retail ~0 -> (b); retail >>0 -> (a)/(c), then PC-attribute the writers from the oracle.
Also: PC of the 91 early head advances in the port (store watch on head var) gives the retire function name.
