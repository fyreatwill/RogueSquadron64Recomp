# Next work unit: pair the object-init return at the caller continuation

HYPOTHESIS-ID: m5-step4-object-entry-body

s4190: caller continuation 0x8008F8A8 matched retail in the hangar; the oracle
cannot observe the `jr` delay slot 0x8008F958 (0 hits, port fired). The caller
of initSampleStreamBlockCache does `jal 0x8008F858` at 0x8008F4B8; the
continuation is 0x8008F4C0.

Hypotheses:
- H-return-parity: retail and port agree on v0/s-regs/sp at 0x8008F4C0.
- H-return-mismatch: restored regs/sp differ, selecting the divergent register.
- H-route-invalid: controls/phases fail.

Discriminator: add a port witness at 0x8008F4C0 (new apply script modelled on
tools/apply_s4190_m5_object_return.py; marker `    // 0x8008F4C0: lw          $ra, 0x18($sp)`),
add `--watch-pc 0x8008f4c0` with pc-field-dump to a copy of the s4190 recipe
(run_s4191_*.sh), and gate retail rows by phase so the title row is not lost to
the 10000 hit cap. Keep 0x8008F8A8 as the positive control.
