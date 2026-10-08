# Next work unit (s4307): port-side post-free synth-read join

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4306): a valid seeded port VI-512 run passed both controls and captured
256 ordered post-store rows with 0 requested-vs-post mismatches. Compared with
the independent s4305 retail table, the port has a different reused-block
layout/order and writer mix. This selects H-retail-layout-different; no
port-only damaging value was observed. The exact synth consumer boundary is
still open.

Competing hypotheses:

- H-layout-equivalent: the apparent tuple difference is only route/ordinal
  sampling, and the first synth read still sees equivalent nodes.
- H-retail-layout-different: the port's different writer/address sequence is
  present at the first synth read and explains the invalid traversal.
- H-port-only-damaging-write: a port-only damaging value appears in the joined
  read, despite the captured scalar stores being internally consistent.

Discriminator: one build/run with the existing positive controls plus a
phase-gated port read watch over 0x17D000:0x17E200. For each first read after a
post-free writer, log read PC, address, value, phase, and the immediately
preceding writer ordinal. Compare the first read tuple and its predecessor to
the retail read watch and s4305 ordered rows. A matching read selects
H-layout-equivalent; a different legitimate layout at the read selects
H-retail-layout-different; a port-only damaging value selects
H-port-only-damaging-write. Missing controls or VI 512 are invalid.

Exact command:

Before changing code, inspect the existing read-side MusyX/stream hooks and
phase plumbing; add the entire read/write join in one build, then run the
seeded-save phase-1024/key driver with PROBE_LEAVE_OK=1 from build/ and all
passive breadcrumbs enabled. Do not add a guard or skip.

Expected outcomes: matching read/predecessor tuples select H-layout-equivalent;
a different legitimate read layout selects H-retail-layout-different; a
damaging port-only value selects H-port-only-damaging-write. No control or no
VI-512 phase is invalid. Do not add a guard or skip from this probe.
