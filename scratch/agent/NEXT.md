# Next: M3 guard-class audit of host wrappers (osViSwapBuffer, EEPROM/pak buffer args)
HYPOTHESIS-ID: m3-idiom-class-audits

1. Enumerate every host wrapper taking a guest pointer (grep lib/ + src/ for osViSwapBuffer, osEepromLongRead/Write, osPfs*, osContStartReadData buffers); classify each: translated via rdram+phys, range-checked, or raw.
2. Guard or prove dead each; add a regen-gate audit with a positive control like tools/audit_narrow_base.py.
3. Discriminator: any wrapper dereferencing an unvalidated guest pointer is a live class member.
