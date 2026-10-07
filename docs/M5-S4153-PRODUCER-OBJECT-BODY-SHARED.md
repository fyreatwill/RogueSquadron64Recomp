# M5 Session 4153 — producer object/body shared

The rebuilt port and independent retail oracle both passed the whole-RDRAM
positive control and title/hangar phase gates. The retail oracle watched both
`0x800078E0` and `0x800078EC` in the same phase-gated run.

At title, the entry and first body rows shared `s0=0x801BB9B0` and
`s1=0x88`; the pointed source word was `0xE51EE75C` before the body cleared
the destination. At hangar, the entry used `s0=0x8065E0A0`, `s1=0x1C`, and
the first body execution preserved the same object and length. The port's
existing setup/store rows also showed the same phase-specific object/state
tuples at the body boundary, while its stored values remained zero.

H-entry-body-shared is selected at this boundary. The result rules out a
producer-entry-to-body state transition as the explanation for the port's
zero payload, but does not identify the earlier nonzero producer that retail
feeds into the clear. ORIGIN: the legitimate retail `rs_memset` entry/body
state and the port's source-construction store loop; no guest value,
wait, cap, predicate, slot, or writeback behavior changed.

Evidence: `scratch/agent/s4152_m5_caller_state_join/retail.log`,
`port.log`, and `verdict.txt`.
