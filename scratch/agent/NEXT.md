# Next work unit: offline-compare retail accumulator records (scratch/agent/s5003/rsp.dump) against port

HYPOTHESIS-ID: m4-accumulator-origin-new-witness

Capture exists (record format in tools/oracle/patches/cxd4-rsp-dump.md; 4156 B records, type 1 = gfx).
Steps: (1) Phase-gate records using the VI trace in scratch/agent/s5003/cxd4.log (hangar = after 1024->512 at t=38.4s;
map via gfx task ordinal vs rdp.log rows). (2) Find which port stage rows hold the equivalent accumulator/DMEM
state (grep CURRENT-TRUTH "M4"/port stage rows), build one table of retail vs port for the first accumulator
publication. (3) Outcomes: match => port RSP emulation faithful, M4 origin elsewhere; mismatch => names the
first diverging DMEM/VACC lane. Do not guard or rewrite values; do not A/B across animating scenes.
