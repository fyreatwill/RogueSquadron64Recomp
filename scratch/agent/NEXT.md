# Next: source-byte frequency histograms, retail and port
HYPOTHESIS-ID: entry-source-byte

Session 5223 selected H-field-diff and refuted a missed entry, a dead
`0x800903F0` site, and a caller mismatch. On both mission origins the port's
`source_byte` at `s0+0x22` was outside {0x00, 0x01, 0xFF} on about 99.9% of
entries (78377/78464 and 79175/79264). s0/s1 stayed in KSEG0 and v0 stayed in
1..8. The retail {0x00, 0x01, 0xFF} set is the 32768 retained distinct rows
from `scratch/agent/s5203_retail_entry_range/retail_fixed.log`, not a
frequency sample. 111686 later novel tuples were dropped, so retail may still
emit 0x03 or 0xBB.

Do not resume the rename sweep. Do not re-watch whether `0x800903F0` executes.
Do not add a guard. Do not rename `bzero_recomp` or `bcmp_recomp` back to
`bzero` / `bcmp`.

One port build and one retail oracle run, in this iteration. Add all bins
before either run.

Port arm, in the existing s5223 entry hook (and the matching fixup block):
256 bins per mission origin of the byte at `(s0+0x22) & 0x1FFFFFFF`, plus the
existing entry counter. Flush the histogram on the leave line for that origin.
Positive control: `[s5223-armed]` fires, and the 256 bins sum to that
origin's entry count. A bin sum that is not the entry count is unevaluable.

Retail arm, in `tools/oracle/rs64_oracle.c` at the `0x8008FAAC` field dump:
256 bins of `debug_mem_u8(s0+0x22)` for every hit while the VI origin is
`0x00690400` or `0x00620400`, including hits that would overflow the unique-row
cap. Print the bins at shutdown. Positive control: the whole-RDRAM watch
fires about 1.6M times in 8 emulated seconds, and both mission origins occur.
Do not use the 4.3 GB range-watch log.

Competing hypotheses:

- H-port-byte-diverges: retail's mission-origin histogram, counting every
  hit, is still only {0x00, 0x01, 0xFF}, and the port's modal byte is outside
  that set. The field difference is real. Next question is who writes the
  port byte, not another entry-field.
- H-retail-cap-blind: retail's modal mission-origin byte equals the port's
  modal byte (the s5223 samples were 0x03, with one 0xBB). The unique-row cap
  hid the common retail byte. This closes H-field-diff as a port defect.
- Unevaluable: either histogram's bin sum disagrees with its hit count, the
  armed or whole-RDRAM control does not fire, or a mission origin is missing
  on either side.

Do not add a further field after this table.
