# NEXT: attribute the runtime writer of voice 0x801724C0 +0x34
HYPOTHESIS-ID: m5-audio-destub

s4596 completed the static census; see docs/M5-S4596-VOICE34-CENSUS.md.
The only relevant voice-field writers are 0x800921E8 (sample descriptor +4)
and 0x80090C80 (source voice +0x38). At 0x800903F0, a3 is a direct load of
voice +0x34 and a1 is only that value plus an aligned offset. This selects
H-writer/input over H-builder. Retail independently showed B0xxxxxx pointer
stores, so the port's ASCII value remains illegitimate.

Next work unit: before any new instrument, run the retail oracle's positive
control and target watch for physical 0x1724F4, then build one phase-scoped
port store watch that attributes every write to guest 0x801724F4, including
both named writers and any other PC. Competing outcomes: (H-init/keyon) the
bad value is written by 0x800921E8 or 0x80090C80; (H-foreign) another guest
PC writes it; (H-no-store) no port write reaches the target and the value
enters through a host/translation boundary. Discriminator: first-writer PC,
value, and phase for the target address, with the retail watch as the
independent control. Do not add a mitigation.
