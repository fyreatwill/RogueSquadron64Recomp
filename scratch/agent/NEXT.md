# Next work unit: map fillSampleStreamRange host offsets +932 and +8292 to guest loads (garbage vs NULL pointer)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4232: 0x80001b08 was our ai-output probe (fixed). Real faults: fillSampleStreamRange+8292 (guest addr 0, NULL) and +932 (guest 0x10CF300D). Re-run scratch/agent/s4230_listwatch.sh with the fix (ROGUESQ_LOG_ALL on) for 6 runs; tally host pc-symbols not last-guest-pc.
Hypotheses: (a) NULL and garbage derive from the same list node with a stale/overwritten link; (b) separate sites; (c) save-state-dependent. Discriminator: disassemble the host offsets (otool -tv) to the generated C line, name the base register's source field.
