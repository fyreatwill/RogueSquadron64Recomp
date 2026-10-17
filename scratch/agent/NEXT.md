# Next: retail M4 run at the mapped PCs (stride 1, filtered)

Mapping is exact (s5353): retail_pc = port_pc & 0xFFF. Unit: one cxd4 retail run (S5335 recipe incl. whole-RDRAM + VI
positive controls, autopilot route 3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a) with RSM1 stride 1 filtered
to PC {0x012C,0x07F0}; join with port rows (task ~959-961, 512-wide hangar) by VI phase ordinal + overlay/task type.
Outcomes: retail samples there show -32768 lanes -> port transient legitimate; retail never samples them -> close M4
unevaluable; lanes absent there -> H2 candidate, still no mitigation without a named writer.

HYPOTHESIS-ID: m4-generated-pc-imem-mapping
