# Next work unit: repair the pre-clear CPU-writer positive control

HYPOTHESIS-ID: m5-pre-clear-producer-provenance

Repair the port-side positive control for CPU writers overlapping
`0x178C80..0x178F18`, then rerun the same route-qualified retail/port
discriminator. The s4155 port reached both target phases, but its clear-body
rows were all zero and its intended CPU-writer markers emitted no rows.

Competing hypotheses and discriminator:

- H-port-preclear-absent: after the control fires, retail has nonzero
  pre-clear source-span writers while the port has none. This selects a
  missing port-side producer boundary.
- H-port-preclear-overwritten: after the control fires, the port has a
  nonzero source-span writer before its known zero clear. This selects the
  overwrite explanation.
- H-instrument-gap/route-invalid: the CPU-writer positive control still does
  not fire, or either arm lacks whole-RDRAM/title/hangar gates. No provenance
  conclusion is valid.

Exact work: inspect the generated hook/fixup path for the missing
`field348-writer`/`field348-candidate` positive control, enable or repair the
regeneration-safe hook for the aligned `0x178C80..0x178F18` range, and build
once. Run `zsh scratch/agent/run_s4154_m5_preclear_provenance.sh` from the
repo root for the paired capture. Require whole-RDRAM, title, and hangar
controls plus at least one port CPU-writer control row before interpreting
any zero/nonzero result. Do not change guest, audio, wait, cap, predicate,
slot, or writeback behavior.

Expected outcomes: nonzero retail writers with no port counterpart selects
H-port-preclear-absent; a nonzero port writer followed by the known clear
selects H-port-preclear-overwritten; missing writer control or route gates
selects H-instrument-gap/route-invalid.
