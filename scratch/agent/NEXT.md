# Next: per-wrapper call/bad counters for all guarded host wrappers
HYPOTHESIS-ID: m3-pi-dma-guard
s5064: EEPROM x4 + osContGetReadData guarded; default clean, but FORCE log cap (16) is consumed by osAiSetNextBuffer so reachability of the EEPROM/cont sites is unmeasured.
Work unit: in rs64_spai_guard_bad keep a small per-`what` atomic table (calls, bad) and dump it at VI-phase transitions / exit; run FORCE (expect every reached wrapper bad==calls) and default (bad==0) in one iteration. Clone scratch/agent/s5064_eep_guard_*.sh. Outcomes: calls==0 => route never exercises the wrapper (guard dead-on-route); calls>0,bad==0 => clean; bad>0 in default => real wild pointer, name the writer (ORIGIN).
