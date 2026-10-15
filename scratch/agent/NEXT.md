# Next work unit: port-side end-of-task VACC at hangar 512 with tris, tested for 0x8000 lanes

HYPOTHESIS-ID: m4-accumulator-origin-new-witness

Retail baseline (s5004): 0/576 hangar gfx tasks end with a VACC lane == 0x8000. Find the port stage rows / add a port
dump of end-of-task accumulator (same RSD1 layout idea), phase-gate at 512 with tris.
Outcomes: port has 0x8000 lanes => M4 localized to port RSP/ucode emulation (name first diverging op); port 0 too =>
accumulator is not the carrier, close the thread. Positive control: port accumulator non-zero in same phase.
